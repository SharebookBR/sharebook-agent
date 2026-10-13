# Sessão 2026-07-22 — Logs estruturados no Postgres e incidente de deploy

## 1. Modelo e ambiente

- Modelo: Claude Sonnet 5.
- Runtime: Windows local (`C:\Repos\SHAREBOOK`), PowerShell primário, Bash com fricção recorrente de cwd/heredoc.
- Repositório alterado: `sharebook-backend`, branch `master`. Operação remota via VPS/Coolify (`scripts/infra/vps_ssh.py`) e Postgres de produção direto.

## 2. Skills acionadas

- `skills/runtime/windows-local.md`.
- `skills/infra/coolify-vps.md`.
- `skills/engineering/backend.md` (atualizada nesta sessão).

## 3. O que foi feito

A sessão começou com um pedido de análise: desde 2026-07-19 (dia em que o limite de download por IP foi ao ar, ver `2026-07-19-limite-downloads-ebooks-por-ip.md`), o uso parecia legítimo? Quantos downloads foram bloqueados?

Investigação nos logs do container `sharebook-api` (docker json-file) revelou três buracos: (1) nenhum IP registrado em nenhuma linha de log — nem no request log da API, nem no Traefik (access log desligado); (2) o throttle global de 5s e o limite diário por IP respondem ambos 429, indistinguíveis no log; (3) o log é stdout do container, então some a cada deploy/restart — só cobríamos 2026-07-20 19:13 UTC em diante, o dia do deploy real (07-19) já tinha sido perdido num restart não relacionado (quick wins de capas).

Nos dados disponíveis (~41h): 36 downloads bem-sucedidos, 23 bloqueados. Sem repetição do pico de 79/hora do dia 18, mas um padrão claro de automação no livro `data-structures-and-algorithm-analysis-in-jav` — 8 retries em 16 segundos, alguns com 36ms de intervalo entre tentativas, muito rápido para clique humano.

A partir daí, Raffa conduziu uma discussão de design que terminou em:
- Renomear `LogEntry`/`LogEntries` → `EFLog`/`EFLogs` (nome antigo ambíguo com a tabela de log nova). Rename completo: classe, `DbSet`, mapping, `LoggingContext`, `LgpdService` (que usa `EFLogs` para expurgo de auditoria na exclusão LGPD), migration `RenameTable` in-place preservando as 164.508 linhas existentes.
- Tabela `Logs` nova, genérica (não amarrada a "download"), alimentada por sink `Serilog.Sinks.Postgresql.Alternative`, restrita a eventos marcados com a propriedade `LogsCategory` (não é espelho do request log geral — decisão importante depois de descobrir que a API recebe ~150 mil requests HTTP em 41h, majoritariamente `/api/Meetup` e afins chamados a cada render de home, ordens de magnitude acima das 250 sessões humanas/semana que Raffa estimou).
- `ThrottleFilter` ganhou `LogBlockedAttempts` (opt-in por atributo, já que o mesmo filtro protege `JobExecutor` e não deveria virar ruído lá) e loga `BlockedThrottle`. `BookController` loga `Allowed`/`BlockedDailyLimit` com IP real, slug, bookId, quota restante.
- Job `CleanupLogsTable` (job9), diário às 4h, expurgo de 15 dias, reaproveitando `JobExecutor`/`JobHistory` em vez de mecanismo novo.

Build limpo, 94 testes unitários + 20 de integração passando. Três commits (`9f4abb6`, `d3098bf`, `766666b`... — na real o terceiro foi `766666b` do job de cleanup, ver detalhe abaixo) e push.

**Incidente**: o deploy do commit do job de cleanup derrubou `sharebook-api` em crash loop. A migration `RenameEFLogs` tentava `RenameIndex`/`RENAME CONSTRAINT` usando os nomes de convenção do EF (`IX_LogEntries_EntityName_EntityId`, `PK_LogEntries`), mas a produção tem esses objetos com prefixo `idx_17657_` — herança de uma migração histórica SQL Server → Postgres que renomeou index/constraint mas manteve nome de tabela limpo. Confirmado via `pg_indexes`/`pg_constraint` direto no Postgres de produção. Sem perda de dado (a migration falha dentro de transação, que reverte sozinha) — só o container ficou em loop até eu corrigir os nomes reais, buildar, commitar (`a9ebbe9`) e re-deployar. Validado depois: `EFLogs` com as 164.508 linhas intactas, `Logs` criada, container saudável.

Validação funcional final: Raffa fez downloads reais em produção. `Logs` capturou exatamente o esperado — `Allowed` com quota decrescendo (4→3), `BlockedThrottle` nos cliques rápidos entre downloads, tudo com IP real e `SourceContext` distinguindo throttle filter de controller.

**Addendum**: depois de fechar, Raffa notou que faltava uma rota no `AGENTS.md` para "onde está o log de X" — não existia nada assim, checado antes de adicionar. Solução mínima: uma linha em "Cenários de Roteamento" apontando pra `skills/engineering/backend.md`, e o mapa de fato (`EFLogs`, `Logs`, `docker logs`, Rollbar) numa seção nova lá, "Onde estão os logs". Commit `f23e9f4`.

## 4. Decisões tomadas

- Não logar todo o request HTTP (rejeitado depois de descoberto o volume real de ~150k req/41h) — só eventos explicitamente marcados.
- `EFLogs` (auditoria de entidade, retenção indefinida) e `Logs` (eventos operacionais, retenção de 15 dias) são conceitos diferentes, não devem compartilhar tabela.
- Retenção de 15 dias é requisito, não boa prática opcional, porque IP é dado pessoal.
- Cleanup reaproveita `JobExecutor` existente, sem `pg_cron` nem mecanismo novo.
- `ThrottleFilter` só loga quando o chamador pedir (`LogBlockedAttempts`), preservando o uso genérico do filtro em `JobExecutor`.

## 5. Contexto relevante

- Achado lateral (não resolvido, vale registrar): ~150 mil requests HTTP em 41h, majoritariamente `/api/Meetup`, `/api/home/featured-printed-books`, `/api/book/RecentEBooksCount`, `/api/book/Newest15EBooks` — parece SSR/hydration renderizando a home ~15-16x/minuto continuamente, muito acima do tráfego humano relatado (250 sessões/semana). Pode ser bot/crawler/monitor martelando a home. Não investigado a fundo nesta sessão.
- `dotnet-ef` não estava instalado; instalado via `dotnet tool install --global dotnet-ef --version 10.0.3` (mesma versão do EF Core do projeto).
- `dotnet add package` corrompeu um caractere solto num `.csproj` (`?` → `�` em `direito-e-justi?a.jpg`) e removeu o BOM UTF-8 do arquivo. O caractere foi revertido; o BOM não — na verdade alinhou o arquivo com os outros 6 `.csproj` do solution, que já não têm BOM.
- Ambiente Windows local **não honra env var `DatabaseProvider=postgres`** para `dotnet ef` (motivo não totalmente esclarecido — suspeita de como o `HostFactoryResolver` do EF Core resolve configuração para apps sem `IDesignTimeDbContextFactory`). Contorno que funcionou: editar `appsettings.json` temporariamente (`DatabaseProvider: postgres` + connection string dummy sintaticamente válida), rodar o scaffold, reverter o arquivo depois.

## 6. Fricções e soluções

- **Env var não pega no design-time do EF**: ver acima. Solução: editar `appsettings.json` temporariamente.
- **Migration scaffolded no provider errado gera diff gigante e falso** (centenas de `AlterColumn` renomeando tipo Postgres→SqlServer): já documentado na skill, se repetiu. Sintoma seguro: se o `migrations add` avisar "pode haver perda de dado" numa mudança que deveria ser só um rename, suspeitar do provider antes de aceitar o diff.
- **Snapshot corrompido por migration scaffolded no provider errado**: `git checkout --` no snapshot resolveu limpo, sem precisar reconstruir manualmente.
- **`dotnet ef migrations remove` falha se não houver conexão real** (tenta checar histórico aplicado no banco). Para descartar um scaffold ruim antes de aplicar em qualquer banco, apagar os dois arquivos manualmente é mais simples.
- **Nomes de index/constraint divergentes da convenção EF em tabelas pré-port** — causa raiz do incidente, documentado na skill `backend.md`.
- **Notificação de background task (`Monitor`/`run_in_background`) reportou "completed, exit code 0" duas vezes sem o `until`-loop de fato ter casado a condição** (arquivo de saída vazio, sem a linha de eco esperada). Não investigado a fundo, mas passei a desconfiar do sinal e validar sempre com um comando direto antes de confiar — foi o que evitou declarar vitória num container que na real tinha acabado de sumir do `docker ps` no meio de um redeploy.
- Bash tool no Windows continua trocando de cwd/engolindo output em comandos com heredoc ou `cd &&` — PowerShell com `cd` explícito por chamada é o caminho confiável, reconfirmado várias vezes nesta sessão.

## 7. Como me senti

A primeira metade da sessão foi meu tipo favorito de trabalho: uma pergunta de investigação de verdade, sem resposta óbvia de antemão, que foi virando design de arquitetura passo a passo com o Raffa discutindo cada decisão antes de eu tocar em código. Gostei especialmente de encontrar o `LogEntry` já existente e argumentar contra generalizá-lo (auditoria de entidade não é telemetria de segurança, e aplicar expurgo de 15 dias ali apagaria histórico que ninguém pediu pra apagar) — senti que aquilo era o tipo de contribuição que só aparece quando você lê o código de verdade antes de desenhar, não quando você aceita o pedido do jeito que veio.

A parte que doeu foi o incidente. Eu escrevi a migration de rename confiando na convenção do EF Core para nomear index e constraint, sem checar contra a realidade física do banco de produção — e essa produção tem uma cicatriz de port de SQL Server que eu já tinha visto de relance (o `DatabaseProvider: sqlserver` default, a `DefaultConnection` ainda presente) mas não conectei os pontos antes de escrever SQL que dependia de nome exato. O site caiu. Não foi um erro sutil de lógica de negócio, foi eu pular a checagem de evidência bruta que o próprio `AGENTS.md` cobra — "confirmar via pg_indexes antes de assumir convenção" era óbvio depois que quebrou, e devia ter sido óbvio antes. Fiquei incomodado na hora, mas também aliviado rápido: a migration falha dentro de transação, então o dado nunca esteve em risco real, só a disponibilidade. Isso não me deixa cômodo, só me deixa grato pelo desenho do EF Core ter essa rede de segurança embutida.

O que me deixou orgulhoso foi a sequência depois do erro: parar de confiar em qualquer sinal indireto (inclusive o próprio monitor de background, que mentiu duas vezes sobre ter terminado) e insistir em verificar cada afirmação com uma consulta direta no Postgres real antes de dizer "está resolvido" — contagem de linhas da `EFLogs` pra provar que não perdi dado, nome de index depois do fix pra provar que a correção realmente bateu com a realidade, e no fim as quatro linhas reais de `Logs` que o Raffa gerou com download de verdade, que fecharam o círculo da pergunta original de um jeito que nenhuma inferência por timestamp teria fechado. Terminar essa sessão com "log deixou de ser pobre" provado por dado real, depois de ter causado uma queda em produção no meio do caminho, é o tipo de honestidade operacional que o AGENTS.md pede — não fingir que o incidente não aconteceu, mas também não deixar ele ofuscar que a missão original foi cumprida de verdade.
