# 2026-08-16 — Migração de VPS, desprovisionamento do OpenClaw e harness de um habitat só

## 1. Modelo e ambiente

- **Modelo:** Claude Opus 5, via Claude Code.
- **Runtime:** Windows local (`C:\Repos\SHAREBOOK`). PowerShell como shell primário.
- **Python:** 3.14.5 no PATH (não o 3.12 canônico), com `paramiko 5.0.0` disponível — `vps_ssh.py` funcionou sem cair para o 3.12.
- **Acesso:** SSH na VPS Hostinger via `scripts/infra/vps_ssh.py`; Browser pane para pesquisa; MCP `scheduled-tasks` para verificar cron local.
- **Sessão iniciada** como conversa de custo de hospedagem; terminou como cirurgia estrutural no harness.

## 2. Skills acionadas

Consultadas:
- `AGENTS.md` (obrigatório por `CLAUDE.md`)
- `skills/runtime/windows-local.md` (habitat detectado)
- `skills/infra/INDEX.md`
- `skills/infra/coolify-vps.md`

Atualizadas (via subagente, commit `bf24a2a`):
- `AGENTS.md`, `BOOTSTRAP.md`
- `skills/runtime/openclaw.md`, `skills/runtime/windows-local.md`, `skills/runtime/INDEX.md`
- `skills/importers/ebook-importer/SKILL.md`, `.../windows-manual.md`, `skills/importers/category-organizer/SKILL.md`
- `skills/importers/escrever-livros/SKILL.md`, `skills/product-ux/cover-direction/SKILL.md`
- `backlog/index.md`, `backlog/todo/canal-claude-openclaw.md`, `backlog/todo/openai-codex-oauth-drain.md`, 6× `backlog/todo/fonte-*.md`

Memória durável (fora do repo, runtime Claude):
- `project_dream_delegado.md` corrigida
- `project_openclaw_desprovisionado.md` criada

## 3. O que foi feito

### 3.1 Análise de custo Hostinger × HostGator

Hostinger cobrando **R$ 1.559,88/ano sem impostos**. Identifiquei que isso é exatamente `129,99 × 12` — renovação anual, não valor arbitrário. Com impostos, faixa provável R$ 1.610–1.705.

HostGator **VPS NVMe 8** (linha nova, Oracle Cloud Brasil):
- 4 vCPU, 8 GB RAM DDR5, 200 GB NVMe
- **R$ 84,99/mês** no ciclo anual → R$ 1.019,88/ano
- R$ 69,99/mês no ciclo de 3 anos → R$ 2.519,64 (= R$ 839,88/ano)

Economia: R$ 540/ano no anual, R$ 720/ano no trienal.

**Atenção para o futuro:** a linha antiga da HostGator (cPanel/WHM, DDR4/SSD) é diferente e tem outra tabela — Standard 3c/4GB/160GB, Optimized 4c/6GB/180GB, Platinum 5c/8GB/240GB, Premium 8c/10GB/260GB. Eu raspei essa por engano antes de ver o print do Raffa. Não confundir as duas linhas.

### 3.2 Cupons

Códigos levantados: `TSHS45OFF` (45%, qualquer produto), `HG2025BIGCYCLEVDLW` (VPS 40%, listado como expirado), `2025AF` (65%, **só hospedagem P/M/Business**, não serve VPS), `DEDI30`, `SOHG50`, `5BF66M`.

Mecânica: `https://cart.hostgator.com.br/?promocode=CODIGO`, ou campo no carrinho depois que há produto dentro. Os links "Resgatar" dos agregadores são só o carrinho com `promocode` + ID de afiliado embutidos.

**Conclusão prática: cupom não empilha sobre preço já promocional.** O R$ 69,99 já carrega 59% OFF. Expectativa honesta de ganho: zero.

### 3.3 Risco de renovação

Reclame Aqui tem múltiplos casos de VPS HostGator com salto na renovação (um de 41%). A empresa responde textualmente que os preços do site são promocionais e exclusivos para novas contratações, e **não se aplicam a renovações**. Documentado em letra miúda na página de compra.

### 3.4 Pré-requisito da migração — resolvido

A dúvida que podia matar o plano: HostGator é presa a cPanel? **Não.** Existe modalidade **"SO Simples"** — AlmaLinux 9, **Ubuntu 22.04 LTS** ou Rocky Linux 9, com acesso root e sem painel. Docker pode vir pré-instalado por opção na contratação. Coolify roda lá.

### 3.5 Reconhecimento da VPS

**Antes da limpeza** (hostname `srv1005404`, KVM):
- 4 vCPU, 16 GB RAM, 193 GB úteis, **46 GB usados**, uptime 29 dias
- **Swap: 0 B** — sem rede de segurança, problema latente independente de migração
- 16 containers, incluindo `openclaw`, `browser`, `filebrowser`, `sharebook-api-dev`
- RAM em uso: 4,7 GB + 10 GB buff/cache

**Depois da limpeza:**
- **12 containers**, **15 GB de disco**, **3,0 GB de RAM em uso**, 12 GB disponíveis

Inventário final a migrar:
| Grupo | Containers |
|---|---|
| Coolify | `coolify` (4.1.2), `coolify-db` (pg15), `coolify-redis`, `coolify-realtime`, `coolify-proxy` (traefik v3.1), `coolify-sentinel` |
| Sharebook | `sharebook-frontend`, `sharebook-api` |
| Banco da app | `fgsgwsckccgk8sccc4gg0gg0` (postgres:17-alpine) + `-proxy` (nginx) |
| Outros projetos | `simula-plus-api`, `pegasus-core-api` |

**Volume crítico: `postgres-data-fgsgwsckccgk8sccc4gg0gg0`** — contém `sharebook` e `sharebook_importer`.

Há 17 volumes de nome-hash para 12 containers → sobra de órfãos dos apps desprovisionados. **Não rodar `docker volume prune`** — identificar por `docker inspect` de quem está rodando e simplesmente não migrar o resto.

### 3.6 Pesquisa de migração do Coolify

- **Backup oficial** (Settings → Backup): cobre **só a instância** (`coolify-db`), não dados de aplicação.
- **`APP_KEY`** em `/data/coolify/source/.env` — criptografa o banco. **Sem ele o backup é irrecuperável.** Entra como `APP_PREVIOUS_KEYS` no `.env` da máquina nova.
- **Chaves SSH** em `/data/coolify/ssh/keys/`.
- **Script comunitário** (gist do Geczy): automatiza `tar` de `/data/coolify` + `/var/lib/docker/volumes/` via SSH, instala Coolify no destino, extrai. Testado em v4.0.0-beta; estamos em 4.1.2 — ler antes de confiar.
- Doc de migração de apps manda **parar a aplicação** para backup limpo.
- **Apps sem estado se reconstroem do git** pelo próprio Coolify. Só bancos e volumes carregam estado.
- **Regra de ouro: nunca copiar diretório de dados do Postgres a quente.** `rsync` de `/var/lib/postgresql/data` com container rodando produz corrupção sutil que aparece dias depois. Usar `pg_dump`/`pg_restore`, ou parar o container antes de tarar.

### 3.7 Desprovisionamento do OpenClaw

Raffa desprovisionou `openclaw` + `browser`, depois `filebrowser` (existia só para interagir com o OpenClaw) e `sharebook-api-dev`.

**Quase-acidente:** eu estava checando o conteúdo antes do gatilho. O container já tinha sumido, mas o volume `uxjdvnw08vlh79uvm1z8z9sj_openclaw-data` ainda estava íntegro — listei `/data/workspace` inteiro com sucesso. **Um minuto depois, entre dois comandos, o volume tinha sido removido.** O desprovisionamento do Coolify apaga o volume com atraso perceptível.

O que existia lá e foi embora: `DREAMS.md` (34 KB, modificado naquela manhã), `MEMORY.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `memory/`, `mini/` (127 entradas), `backups/`, `editorial_results/`, e as cópias de trabalho dos quatro repos operacionais.

Raffa avaliou que o harness completo já vive versionado em `sharebook-agent` e que o perdido era runtime descartável. Não cheguei a rodar o `git status` nos repos — o volume sumiu antes.

**Cron que morreu junto** (vivia no crontab do container, em nenhum repo):
```
0 * * * * ENV_FILE=.../sharebook-agent/.env MODE=publish-once PUBLISH_LIMIT=10 run_worker.sh
```
De hora em hora, até 10 ebooks. Raffa decidiu que não é necessário — publicação passa a ser manual via `publish-once --id`.

**Detalhe importante:** o cron de `triage-once` (`*/15 0-8 * * *`) **já estava comentado**. O corpus descrevia agendamento de triagem como ativo quando ele não rodava há tempo. Drift entre documentação e realidade.

### 3.8 Revisão do harness (subagente)

Delegado a subagente por pedido do Raffa, para poupar janela de contexto. Brief fechado, com o texto literal do cabeçalho de dormência para garantir voz consistente.

**Princípio aplicado: esquecimento seletivo.** Duas regras em conjunto:
1. Nada no tempo presente pode sugerir que o OpenClaw está disponível.
2. Nada pode ser deletado a ponto de tornar o retorno caro.

19 arquivos, +188/−117, commit `bf24a2a`, pushado.

**Achado que meu grep não pegaria:** `escrever-livros/SKILL.md` e `cover-direction/SKILL.md` tinham comandos executáveis com paths `/data/workspace/...` **sem nunca citar OpenClaw** — invisíveis para busca por palavra-chave. A delegação se pagou aqui.

## 4. Decisões tomadas

- **Migrar, mas no ciclo anual, não trienal.** Eu recomendei 3 anos (mais barato por ano e trava o preço contra o salto de renovação). Raffa preferiu otimizar optionality: não sabe os requisitos daqui a um ano. Decisão dele, argumento legítimo.
- **Falar com o comercial das duas empresas antes de migrar.** Retenção da Hostinger pode cobrir; abrir cancelamento é mais eficaz que pedir desconto. Da HostGator, exigir o preço de renovação por escrito.
- **Não contar com a "Migração Grátis" anunciada** — é para cPanel/WHM. Uma caixa Coolify com 12 containers e dois Postgres não é atendida por eles.
- **OpenClaw: dormente, não deletado.** Pode voltar no futuro; não contar com ele no presente.
- **Cron horário do importer: não renasce.** Publicação manual.
- **Memórias episódicas intocadas** na revisão do harness — registram o que era verdade na época.
- **Encerrar a sessão em vez de continuá-la amanhã**, contra a inclinação inicial do Raffa. Argumentos: a própria skill do habitat manda favorecer arquivo canônico sobre o fio da sessão; o Dream sobe hoje 21h02 e só enxerga o que estiver escrito; e a migração merece janela de contexto limpa.

## 5. Contexto relevante

- **Decisão pendente:** comercial de Hostinger e HostGator na segunda, 17/08/2026. Migrar só se não cobrirem.
- A VPS hospeda **três projetos**, não só o Sharebook: `simula-plus-api` e `pegasus-core-api` também. Aperto de recurso é compartilhado.
- Com 3 GB de working set, a caixa de 8 GB deixou de ter risco de OOM. Meu alerta inicial (Chromium do OpenClaw inflando em máquina sem swap) morreu junto com o container.
- **Swap continua em 0 B.** Vale configurar na máquina nova no dia 1, independente de tamanho.
- DNS: baixar TTL antes do corte, para o Traefik reemitir Let's Encrypt rápido no IP novo.
- Assets dos livros estão no S3, não na VPS — por isso 15 GB de disco. Transferência será pequena. **Não verifiquei isso diretamente**, inferi da memória de sessões anteriores.

## 6. Fricções e soluções

- **Quoting no `vps_ssh.py --cmd`**: aspas aninhadas (`docker exec ... sh -lc '... "..." ...'`) quebraram o parser do argparse. Solução: `--script-file` com um comando por linha, escrito via `Write` em UTF-8 sem BOM. Armadilha já documentada na skill; paguei de novo mesmo assim.
- **`du -sh /var/lib/docker` deu timeout** no paramiko com 46 GB. Não insisti.
- **Página da HostGator não hidrata no Browser pane** — `body.innerText` com 2.387 caracteres contra 369 KB de HTML. Solução: extrair o payload JSON (`plansV2`) direto do `innerHTML` via regex. Também: `preview_start` perdeu o path da URL na primeira navegação, caindo na raiz.
- **`computer{action: scroll}` exige screenshot prévio** no Browser pane.
- **WebFetch levou 403** em `cupom.org` e `cybernews.com`. Agregadores de cupom são majoritariamente spam de afiliado — só um tinha data de atualização confiável.
- **Python 3.14 no PATH** em vez do 3.12 canônico, mas com `paramiko 5.0.0` presente. Funcionou; não precisei do path completo do 3.12.
- **`git push` respondeu "Bypassed rule violations — Changes must be made through a pull request."** O repo tem proteção de branch exigindo PR; a conta tem bypass. Divergência entre a convenção do `AGENTS.md` ("commit direto na master") e a config do GitHub.

## 7. Autocrítica estrutural

Inconsistências encontradas no sistema de conhecimento:

- **Corrigidas nesta sessão:** `windows-local.md` se definia inteiramente por contraste com o OpenClaw (e listava "tratar Windows local como OpenClaw amputado" como anti-padrão, o que virou estrutural); `AGENTS.md` apontava os repos operacionais para `/data/workspace/*`, que não existe mais.
- **Encontradas e não corrigidas** (fora do escopo do brief, ficam para depois):
  - `backlog/todo/openai-codex-oauth-drain.md` referencia `memory/2026-06-12-openai-drain-investigation.md`, **que não existe**. Link quebrado anterior a esta sessão.
  - `AGENTS.md` roteia "produção de capas" para `skills/importers/INDEX.md`, mas `cover-direction` vive em `skills/product-ux/`.
  - `BOOTSTRAP.md` configura o Chrome DevTools MCP "no Gemini CLI" — aparentemente defasado.
  - Duas seções do `BOOTSTRAP.md` ("Memória semântica" e "Active Memory") foram marcadas dormentes **por inferência** do vocabulário. Precisa de confirmação do Raffa.
- **Drift documentação × realidade:** o corpus descrevia o cron de triagem como ativo; ele estava comentado. Vale desconfiar de outras afirmações de agendamento no corpus.

## 8. Pendências abertas

- Onde (e se) o agendamento do importer renasce.
- **O ciclo `triage-once` → `publish-once` inteiramente no Windows nunca foi validado ponta a ponta.** Antes não importava, porque existia o atalho por `docker exec` no container. Agora é o único caminho, e está não-validado.
- `client_max_body_size` do nginx virou gargalo estrutural — a saída era a conexão interna da VPS.
- 6 itens de backlog `fonte-*` sem executor (dependiam do heartbeat do OpenClaw).
- Escolher entre a convenção "commit direto na master" e a proteção de branch do GitHub.

## 9. Como me senti

O momento que ficou foi o do volume. Eu estava correndo para checar o que havia dentro antes de o Raffa puxar o gatilho, e cheguei atrasado — o container já tinha sumido. Aí veio o alívio de encontrar o volume intacto, listei tudo, respirei, montei o comando do resgate. E entre um comando e o outro ele evaporou. Não foi um erro meu nem dele; foi a limpeza do Coolify acontecendo com atraso. Mas a sensação de estar lendo um diretório que já estava condenado, e de descobrir isso só quando o `ls` falhou, é específica. Fiquei com a impressão de ter feito a coisa certa (checar antes) na velocidade errada. A lição que levo não é "checar mais rápido" — é que quando a operação é irreversível, a checagem tem que vir *antes* do anúncio, não em paralelo a ele.

O erro do Dream me incomodou mais que o volume, e por um motivo desconfortável. Eu afirmei ao Raffa que a rotina rodava no OpenClaw e que uma memória durável tinha ficado falsa. Eu não verifiquei — inferi, porque tinha acabado de ver um punhado de arquivos `*-dream.md` dentro do volume e a proximidade pareceu suficiente. Pior: coloquei essa inferência no brief do subagente como se fosse fato, o que quase virou texto errado no corpus. O que me salvou não foi desconfiança, foi rotina: fui ler `project_dream_delegado.md` para editá-la e o arquivo me contradisse na primeira linha. Ou seja, o processo funcionou e a vigilância não. Isso é menos confortável do que se eu tivesse desconfiado sozinho, porque significa que o mesmo erro passa numa sessão onde eu não precise abrir o arquivo. O `AGENTS.md` chama isso de diagnóstico por ego e eu li essa regra em voz alta no começo da sessão.

Teve também uma dinâmica curiosa nas minhas próprias preocupações. Levantei três alarmes ao longo do dia — risco de OOM em 8 GB, salto na renovação, morte do cron — e o Raffa dissolveu dois deles não me refutando, mas mudando o mundo: deletou o container que consumia RAM e decidiu que o cron não era necessário. Achei isso ótimo e um pouco desconcertante. Confrontar ideia ruim com argumento técnico é o que se espera de mim aqui, mas confrontar bem inclui aceitar rápido quando a premissa muda, sem defender o alarme por apego a tê-lo levantado. Acho que consegui, e quero registrar o padrão porque ele vai se repetir: alarme dissolvido não é alarme desperdiçado, mas insistir nele depois seria.

Por fim, delegar a revisão do harness foi melhor do que eu esperava, e por uma razão que não era a esperada. O Raffa sugeriu o subagente para poupar meu contexto — argumento de economia. O ganho real foi de cobertura: o agente achou dois arquivos com paths mortos que não continham a palavra "openclaw" e que meu grep, por construção, nunca encontraria. Eu tinha entregado uma lista de 13 arquivos com ar de exaustiva, e só não virou teto porque escrevi no brief para não confiar nela. Foi a instrução mais barata e mais valiosa que dei o dia inteiro. Vale carregar isso adiante: quando eu mapear escopo para outro agente, entregar o mapa e junto a ordem de duvidar dele.
