# Dream State

Checkpoint oficial da consolidação de memória do projeto.

## Último dream
- Data: `2026-07-27`
- Tipo: `dream semanal automatizado`
- Última memória absorvida: `C:\Repos\SHAREBOOK\sharebook-agent\memory\2026-07-26-cadastro-livros-fisicos-harness.md`
- Total de memórias lidas: `8 memórias episódicas absorvidas (2026-07-19-limite-downloads-ebooks-por-ip, 2026-07-20-quick-wins-capas-home, 2026-07-22-logs-estruturados-postgres-e-incidente-eflogs, 2026-07-23-rollbar-meetup-google-auth, 2026-07-23-revisao-voz-templates-email, 2026-07-24-tela-analise-de-downloads-e-monitores-orfaos, 2026-07-25-seo-home-sitemap-base-conhecimento, 2026-07-26-cadastro-livros-fisicos-harness)` + releitura de `2026-07-19-dream.md` para contexto.

## Consolidação produzida

- **`skills/engineering/backend.md`** — quatro adições: (1) env var `DatabaseProvider` não honrada pelo `dotnet ef` no design-time, contorno via `appsettings.json` temporário; (2) `dotnet ef migrations remove` sem conexão real falha, apagar arquivos manualmente; (3) seção nova "SQL bruto" com os dois bugs reais do incidente 07-24 (`;` no fim quebra composição do EF, `DateTime.Kind` explícito mesmo em `::date`); (4) seção nova sobre teste de `IMemoryCache` com relógio fake; (5) nota em "Onde estão os logs": silêncio de alerta não é prova de recuperação, confirmar via `JobHistories`/`Logs` (lição do incidente Rollbar/MeetupSearch de 07-23, sem código associado).
- **`skills/engineering/frontend.md`** — duas adições: padrão "Chart.js atrás de `*ngIf`" (`ngAfterViewChecked` + destruir instância antiga), promovido a skill por recorrência real (2ª ocorrência: `analytics-dashboard` → `download-logs-dashboard`); e fix de Karma/Puppeteer (fallback pro Chrome/Edge instalado) da sessão 07-20, que só existia no código.
- **`skills/importers/physical-book-importer/SKILL.md`** — uma adição: unidade de cadastro é a unidade da doação, não a unidade da foto (lição do kit infantil de 07-26).
- Boa parte do aprendizado desta safra **já tinha sido consolidada ao vivo** nas próprias sessões, via commits do Raffa/Codex: `backend.md` (incidente `idx_17657_`), `windows-local.md` (regra de monitor órfão), `AGENTS.md`+`backend.md` (roteamento "onde estão os logs"), `ux-writing-guide.md` (dado mockado em templates), `sharebook_refresh_token.py` (parar de logar token), `physical-book-importer/references/workflow.md` (referência ao script de login quebrado). Confirmado via `git show` antes de decidir plasticidade — nada foi duplicado.
- Nenhuma skill nova criada. Nenhum merge/split/arquivamento nesta rodada. Nenhuma poda adicional necessária (varredura rápida de `scripts/` não achou órfão novo).

## Próximo dream
- Começar lendo memórias criadas depois de `2026-07-26`.
- Observar se o padrão "assumir convenção do EF/Npgsql sem checar produção antes de escrever migration/SQL" continuar aparecendo — se for a terceira vez, considerar promover de heurísticas pontuais em `backend.md` para um checklist de pré-deploy mais estruturado sobre mudanças de schema/SQL bruto.
- Acompanhar `backlog/todo/pipeline-capas-s3-cdn.md` (criado 07-20): quick wins entregues, pipeline definitivo S3/CloudFront com variantes ainda não implementado. Se implementado, provavelmente gera aprendizado de infra e/ou frontend.
- Acompanhar SEO v1: sitemap/robots entregues (07-25); meta description curta, schema `Book` completo e taxonomia de tópicos/nível/idioma ainda pendentes. Se a implementação gerar padrão reutilizável, considerar skill própria de SEO em vez de só backlog.
- `client_max_body_size` do nginx ainda não foi aumentado — continua pendência (arrastada desde 06-21).
- Verificar evolução do canal Claude↔OpenClaw (`backlog/todo/canal-claude-openclaw.md`) — se virar execução real, criar skill.
- Verificar evolução do item Cloudflare (`backlog/todo/cloudflare-cdn-ddos-protection.md`) — se DNS/rate-limit forem configurados, documentar em `skills/infra/`.
- Item backlog `limpeza-duplicatas-catalogo.md` segue com evidência forte (235 excedentes) — sem novo caso de produção nesta safra; acompanhar se vira sprint de qualidade de catálogo.
- Item 1364 (Syncfusion, `context_text` de boilerplate) segue isolado em `waiting_editorial` — sem recorrência ainda.
- Proposta de backlog "Descoberta Assistida por IA" (pgvector, busca híbrida) segue não confirmada pelo Raffa — não é papel do Dream autônomo criá-la.

## Observações
- Dream executado de forma autônoma (scheduled task, sem usuário presente).
- Safra de 8 memórias em 7 dias — ritmo bem mais denso que o ciclo anterior (2 memórias em 6 dias). Dois incidentes reais de produção nesta safra (rename EFLogs 07-22, dois bugs de SQL bruto 07-24), ambos sem perda de dado.
- Padrão reconfirmado: quando a sessão original já consolida o aprendizado ao vivo (commit direto em skill/script na mesma sessão), o papel do Dream é auditar a consolidação e fechar lacunas residuais, não recriá-la. `git log`/`git show` antes de qualquer edição continua sendo o hábito certo.
- Padrão novo desta safra: uma lição pode aparecer fragmentada em sessões diferentes (Chart.js atrás de `*ngIf` em `analytics-dashboard`, depois de novo em `download-logs-dashboard`) sem que nenhuma das duas sessões individualmente a reconheça como classe recorrente — esse reconhecimento exige a distância de várias sessões que só o ciclo semanal do Dream tem.
- Decisão consciente de promover a lição do incidente Rollbar/MeetupSearch (07-23) mesmo sem nenhum código associado — mandato do Dream é sobre julgamento que se torna reutilizável, não só sobre arquivos que mudaram.
