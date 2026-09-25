# Dream State

Checkpoint oficial da consolidação de memória do projeto.

## Último dream
- Data: `2026-09-25`
- Tipo: `dream semanal automatizado via scheduled task (weekly-dream), sem Raffa presente`
- Última memória absorvida: `memory/2026-09-22-incidente-conexoes-cache-ssr.md`
- Total de memórias lidas: `1 memória episódica nova desde o checkpoint real (2026-09-22), mais reinspeção de 11 memórias já absorvidas pelo dream de 2026-09-20 (ver nota abaixo)`.

## Consolidação produzida em 2026-09-25

### Nota de processo: checkpoint inicial errado, corrigido antes do push
Esta sessão começou operando sobre um clone local desatualizado do `sharebook-agent` (sem `git fetch`/`pull` no início, contrariando o ritual obrigatório de sync do `AGENTS.md`). Isso fez a sessão tratar `memory/2026-09-13-dream.md` como o último checkpoint e reprocessar 11 memórias (`2026-09-13` a `2026-09-19`) que **já tinham sido absorvidas pelo dream real de 2026-09-20** (`memory/2026-09-20-dream.md`, ver Histórico abaixo). O erro só apareceu no fim, quando o `git push` foi rejeitado por divergência de ~90 commits. Corrigido com `git fetch` + merge antes de qualquer publicação — nada foi perdido, mas o trabalho de triagem da safra 13→19 foi refeito sem necessidade. Esta é uma instância direta do padrão "memória e relato de sessão anterior não são prova", promovido a regra nomeada no `AGENTS.md` nesta mesma sessão — ironicamente, cometido pela própria sessão que escreveu a regra.

Os achados abaixo permanecem válidos porque foram verificados contra o estado real do corpus (não contra a suposição de checkpoint errada), mas a atribuição de "safra" no frontmatter desta memória reflete apenas a memória genuinamente nova (`2026-09-22-incidente-conexoes-cache-ssr.md`) — o restante foi auditoria direta de skills, não absorção de safra.

### Doctor: falso positivo corrigido
- O Harness Doctor abriu com 26 achados, todos `broken_markdown_link` dentro de `.venv-ga4/` (venv Python local, gitignored, nunca versionado).
- Causa: `IGNORED_DIRECTORIES` do `harness_doctor.py` só cobria `.venv` por igualdade exata; `.venv-ga4` escapava.
- Reparo: generalizado para `IGNORED_DIRECTORY_PREFIXES` (prefixo `.venv`), com teste de regressão novo (`test_venv_directories_with_suffixed_names_are_ignored`). Suite foi de 29 para 30 testes.
- Doctor fechou limpo.

### Skills atualizadas
- `skills/engineering/frontend.md`: fato desatualizado corrigido (SSR descrito como Angular 13/`ngExpressEngine`, real é Angular 22/`@angular/ssr`/`CommonEngine` desde 17-18/09) — gap que sobreviveu ao dream de 2026-09-20 sem ser notado; metodologia de migração de major do Angular promovida (hop a hop, `--force` como sinal de alerta, revisão de diff de schematics, checagem de Dockerfile pós-bump de engine, busca em arquivos de config na raiz antes de remover dependência); bug ativo de `.subscribe()` sem `catchError` (bomba-relógio de SSR desde Angular 21) documentado com a lista de ~16 componentes ainda pendentes; cache SSR de PDP e access log `ssr_access` promovidos a partir do incidente real de 2026-09-22.
- `skills/engineering/backend.md`: dimensionamento de connection pool do Npgsql vs. `max_connections` do Postgres, promovido do incidente de 2026-09-21/22 (`memory/2026-09-22-incidente-conexoes-cache-ssr.md`) — não tinha destino em skill antes desta sessão.
- `skills/runtime/claude-code-openclaw.md`: testar validade de token GitHub contra a API antes de trocar de token achando que o formato está errado; perigo de `git checkout <ref> -- .` misturar índice entre branches.
- `AGENTS.md`: nova regra nomeada "Memória e relato de sessão anterior não são prova", com casos reais da mesma semana como evidência de recorrência (inclusive o próprio erro de checkpoint desta sessão, descoberto depois de escrita).

### Decisões conscientes de não agir
- A maior parte dos `durable_candidates` técnicos da safra 13-19/09 (GitHub App source quebrada pós-migração, Dockerfile defasado da engine, nomenclatura de container Coolify, receita de validação de deploy) já tinha sido promovida pelas próprias sessões ou pelo dream de 2026-09-20 em `skills/infra/coolify-vps.md` e `skills/infra/vps-migration.md` — confirmado por leitura direta antes de agir, nada duplicado.
- Não toquei em `SOUL.md`: densidade constitutiva real na safra (nascimento do habitat 3, herança entre modelos), mas nenhuma decisão deliberada nova que justificasse reescrita autônoma — mesmo julgamento do dream de 2026-09-20.
- Loops de produto/infra/decisão humana permanecem fora do mandato: diff não commitado em `StalwartWebhookVM.cs`, `GITHUB_TOKEN_SHAREBOOK_FRONTEND` expirado sem rotação, hardening de SSH (bantime do fail2ban) pendente, vida útil de `sharebook-frontend-dev`, fechamento do ciclo de bounces do Stalwart, ~16 componentes com `.subscribe()` sem `catchError` (documentados, correção é trabalho de engenharia), follow-up de 24h dos itens Rollbar #2956-2958, estratégia de pré-render/SSG para desacoplar tráfego público do banco.

### Validação
- `python3 skills/doctrine/harness-governance/scripts/harness_doctor.py --root .` terminou limpo (abriu com 26 achados, todos falso positivo).
- `python3 -m unittest discover -s skills/doctrine/harness-governance/scripts -p 'test_*.py' -v` terminou com 30 testes aprovados.
- A memória do ciclo é `memory/2026-09-25-dream.md`.

## Próximo dream
- O checkpoint agora parte de `memory/2026-09-22-incidente-conexoes-cache-ssr.md`.
- **Sempre rodar `git fetch`/`pull` antes de ler `_dream-state.md`** — já promovido a passo 0 explícito do procedimento em `DREAM.md` nesta sessão, para não depender só do ritual genérico do `AGENTS.md`. O checkpoint só é confiável contra o remoto real, não contra o que um clone local desatualizado sugere. Esta sessão só descobriu o erro porque o `git push` final foi rejeitado; num habitat sem push (ou com push forçado), o erro passaria despercebido.
- Observar se a regra nova do `AGENTS.md` ("memória não é prova") reduz a recorrência do padrão, ou se aparece mais uma instância — se sim, considerar se merece checklist/script, não só prosa de doutrina.
- Se aparecer um terceiro caso de diretório-com-prefixo-variável escapando de `IGNORED_DIRECTORIES` (além de `.venv-ga4`), considerar generalizar o detector para respeitar o `.gitignore` do projeto diretamente, em vez de continuar crescendo a lista hardcoded.
- Cruzar se o diff pendente em `StalwartWebhookVM.cs` finalmente teve decisão (commit ou descarte).
- Continuar tratando achados do Doctor como objetos de triagem individual; baseline atual é limpo.

## Histórico — 2026-09-20
- Data: `2026-09-20`
- Tipo: `dream semanal automatizado customizado via OpenClaw cron`
- Última memória absorvida: `memory/2026-09-20-tarefas-9-11-nullable-merge-master.md`
- Total de memórias lidas: `17 memórias episódicas absorvidas (2026-09-13 a 2026-09-20)`.

### Doctor zerado
- O Harness Doctor abriu com 1 achado e fechou limpo.
- O achado era `broken_markdown_link` em `backlog/todo/simplificacao-modernizacao-backend/index.md:6`.
- Classificação: regressão estrutural segura causada pela movimentação do épico de frontend para `backlog/done/simplificacao-modernizacao-frontend/`, enquanto o épico backend ainda apontava para o caminho antigo em `backlog/todo/`.
- Correção aplicada: o link relativo do épico backend agora aponta para `../../done/simplificacao-modernizacao-frontend/index.md`.

### Decisões conscientes de não agir
- Nenhuma nova Skill foi criada: os candidatos duráveis recorrentes da safra já tinham sido promovidos nas próprias sessões, especialmente em `AGENTS.md`, `skills/runtime/claude-code-openclaw.md`, `skills/runtime/claude-code-web.md` e `skills/infra/coolify-vps.md`. (Nota do dream seguinte, 2026-09-25: `skills/engineering/frontend.md` ficou de fora dessa varredura e só foi corrigido no ciclo seguinte.)
- O épico backend não foi movido para `done/`: apesar das 11 tarefas concluídas, o próprio backlog registra que falta validação do Raffa em dev para fechar o checkpoint final.
- Não houve promoção nova para `SOUL.md`; a safra teve densidade constitutiva, mas não trouxe decisão deliberada suficiente para reescrita autônoma.
- Loops de produto/infra seguem preservados fora do mandato do Dream autônomo: SSH hardening/HostGator, bounces e supressão do Stalwart, destino de `dev.sharebook.com.br`, confirmação residual de CI/CD em produção, `footer-build-info`, templates de e-mail restantes, métricas de IA-friendly/tokens e decisões editoriais/produto não validadas.

### Validação
- `python3 skills/doctrine/harness-governance/scripts/harness_doctor.py --root .` terminou limpo.
- `python3 -m unittest discover -s skills/doctrine/harness-governance/scripts -p 'test_*.py' -v` terminou com 29 testes aprovados.
- A memória do ciclo é `memory/2026-09-20-dream.md`.

## Histórico — 2026-09-13

### Doctor zerado
- O Harness Doctor abriu com 5 achados e fechou limpo.
- Os 5 achados eram artefatos deliberados de tradução Gutenberg/Sharebook Brasil adicionados depois da última memória absorvida: página institucional de tradução em `art-director` e selo de capa em `cover-direction`.
- `skills/product-ux/art-director/assets/sharebook-translation-page-02.jpg` e seu `.meta.json` foram indexados em `skills/product-ux/art-director/SKILL.md`.
- A pasta `skills/product-ux/cover-direction/assets`, o selo `sharebook-br-translation-seal.png` e seu `.meta.json` foram indexados em `skills/product-ux/cover-direction/SKILL.md`.

### Decisões conscientes de não agir
- Loops de produto/infra da safra permanecem fora do mandato do Dream autônomo: publicação/cron dos quatro ebooks em waiting_publish, observação final do SMTP próprio/Stalwart, webhook delivery.* do Stalwart, validação Outlook/Hotmail, bounces/supressão, higiene operacional do Stalwart, reputação/listas de bloqueio, métricas da prateleira Mais baixados, ponderação por recência, memory_search/OpenClaw embeddings, deploy automático GitHub/Coolify e grants/default privileges de novas tabelas.
- Não houve promoção nova para `SOUL.md`; a safra não trouxe decisão constitutiva que justificasse reescrita autônoma.
- Os commits recentes de tradução Gutenberg geraram backlog e assets, mas ainda não tinham memória episódica própria; este Dream registrou apenas o reparo de governança dos assets, sem inferir decisões de produto além do que já estava no backlog.

### Validação
- `python3 skills/doctrine/harness-governance/scripts/harness_doctor.py --root .` terminou limpo.
- `python3 -m unittest discover -s skills/doctrine/harness-governance/scripts -p 'test_*.py' -v` terminou com 29 testes aprovados.
- A memória do ciclo é `memory/2026-09-13-dream.md`.

## Próximo dream
- O checkpoint agora parte de `memory/2026-09-10-home-mais-baixados.md`.
- Observar se os commits de Gutenberg/tradução ganham memória episódica própria em ciclos futuros; o Doctor pode revelar artefatos pós-checkpoint que o relatório de safra ainda não enxerga.
- Continuar tratando achados do Doctor como objetos de triagem individual; baseline atual é limpo.

## Histórico — 2026-09-06
- Data: `2026-09-06`
- Tipo: `dream semanal automatizado customizado via OpenClaw cron`
- Última memória absorvida: `memory/2026-09-03-editorial-subagentes-e-harness.md`
- Total de memórias lidas: `37 memórias episódicas absorvidas (2026-08-17 a 2026-09-03)`.

## Consolidação produzida em 2026-09-06

### Doctor zerado
- O Harness Doctor abriu com 28 achados e fechou limpo.
- 2 links quebrados em `memory/2026-06/2026-06-26-analytics-insights-cta-amazon.md` foram corrigidos para os destinos atuais: `backlog/todo/busca-e-recomendacao-sharebook/index.md` e `backlog/done/limpeza-duplicatas-catalogo.md`.
- `skills/importers/daily-triage-recovery/agents/openai.yaml` foi classificado como artefato deliberado de interface e indexado no `SKILL.md`.
- Artefatos legados de `skills/importers/escrever-livros/` foram preservados e tornados observáveis no `SKILL.md`, sem poda autônoma de PDFs/capas de missão antiga.
- Referências úteis de `skills/product-ux/art-director/` e `skills/product-ux/ux-reviewer/references/framework-fixes.md` foram indexadas.
- Placeholders explícitos de `ux-reviewer` e `web-design-reviewer` (`example_asset`, `example_reference`, `example_script`) foram removidos; os diretórios vazios foram apagados.

### Decisões conscientes de não agir
- As 7 memórias sem metadados v1 na safra (`2026-08-17-*`, `2026-08-20-incidente-*`, `2026-08-20-revisao-*`, `2026-08/2026-08-26-thumbnails-*`) foram preservadas como legado válido; não houve retroajuste cosmético.
- Loops de produto/infra da safra não foram resolvidos como se fossem Dream: webhook GitHub/Coolify, token frontend, OAuth Google via `gog`, SMTP próprio, advisories Angular/Universal, Search Console permissões, healthcheck dedicado, source extractor ausente e decisões constitutivas/autonomia.
- Nenhuma alteração em `SOUL.md`: as memórias constitutivas da safra foram lidas como continuidade e tensão, mas não pediram decisão deliberada do agente presente suficiente para reescrita constitutiva.

### Validação
- `python3 skills/doctrine/harness-governance/scripts/harness_doctor.py --root .` terminou limpo.
- `python3 -m unittest discover -s skills/doctrine/harness-governance/scripts -p 'test_*.py' -v` terminou com 28 testes aprovados.
- A memória do ciclo é `memory/2026-09-06-dream.md`.

## Próximo dream
- O checkpoint agora parte de `memory/2026-09-03-editorial-subagentes-e-harness.md`.
- Observar se `memory_search` do OpenClaw já foi reconstruído e se o runtime continua exigindo caminhos alternativos.
- Reavaliar artefatos legados de `escrever-livros` somente em sonho manual se houver intenção de reorganizar ou podar PDFs/capas antigas.
- Continuar tratando achados do Doctor como objetos de triagem individual; baseline atual é limpo.

## Histórico — 2026-08-17
- Data: `2026-08-17`
- Tipo: `dream semanal automatizado`
- Última memória absorvida: `memory/2026-08-16-migracao-vps-e-openclaw-dormente.md`
- Total de memórias lidas: `3 memórias episódicas absorvidas (2026-08-03-quatro-preparos-editoriais-publicacao, 2026-08-13-quatro-preparos-editoriais-publicacao, 2026-08-16-migracao-vps-e-openclaw-dormente)`.

## Consolidação produzida em 2026-08-17

### Guardrail promovido
- `skills/importers/ebook-importer/SKILL.md`, seção "Regras editoriais" — adicionado passo 4 ao preflight editorial: buscar a obra no catálogo (busca semântica, não só título) antes de `plan-set`. Recorrência real: item `1358` (07-09) e `Think Bayes`/`1594` (08-13), ambos duplicatas pegas antes da mutação pela mesma prática ainda não escrita como regra.

### Reparo de roteamento
- `AGENTS.md`, "Cenários de Roteamento" — adicionada linha distinguindo "produção de PDFs/capas autorais" (`skills/importers/INDEX.md`, obra nova) de "gerar/trocar capa de livro existente" (`skills/product-ux/INDEX.md`, `cover-direction`). Gap identificado na autocrítica estrutural da própria sessão de 08-16, confirmado por leitura direta dos dois `INDEX.md` antes de editar.

### Reparo de link morto
- `backlog/todo/openai-codex-oauth-drain.md` — removida referência a `memory/2026-06-12-openai-drain-investigation.md`, confirmado via `git log --all` que esse arquivo nunca existiu no repo (não foi perdido, nunca foi escrito). Contexto da investigação preservado no próprio documento; texto agora deixa explícito para não recriar o arquivo por suposição.

### Decisão consciente de não agir
- **Feedback "silêncio operacional" (08-13)**: Raffa cobrou atualização por marco numa publicação longa. Primeira ocorrência clara desse feedback específico — sem recorrência anterior encontrada no corpus. Por doutrina (não promover por sessão isolada), não virou guardrail. Registrado em `2026-08-17-dream.md` para o próximo Dream cruzar; se repetir, promove para "Postura do Agente" em `AGENTS.md`.
- **Trap de quoting aninhado no `vps_ssh.py` (08-16)**: já documentado extensivamente em `skills/infra/coolify-vps.md` (regra de uma linha por comando, UTF-8 sem BOM, preferência por `--script-file`). Recorrência de erro já coberto, não lacuna de documentação. Sem ação.
- **BOOTSTRAP.md, seções "Memória semântica"/"Active Memory" marcadas dormentes por inferência**: pendente de confirmação explícita do Raffa, não é decisão do Dream autônomo.
- **Cron do importer (onde/se renasce), `client_max_body_size` do nginx, convenção de commit vs. proteção de branch do GitHub**: decisões de produto/infra fora do mandato de arquitetura de skills do Dream.

## Próximo dream registrado em 2026-08-17
- Cruzar se o feedback de "silêncio operacional durante tarefa longa" (08-13) se repete. Se sim, promover a "Postura do Agente" em `AGENTS.md` — atualização por marco em tarefas longas, sem virar narração excessiva.
- A safra de 08-16 listou lacunas adicionais fora do escopo do brief daquela sessão que não são de arquitetura de skill (link `openai-codex-oauth-drain.md` já corrigido aqui; roteamento de capas já corrigido aqui). As restantes (BOOTSTRAP.md dormência por inferência, cron do importer, nginx, convenção de commit) seguem como pendência de produto/confirmação humana, não de Dream.
- Observar se o guardrail de duplicidade recém-formalizado em `ebook-importer/SKILL.md` reduz de fato a taxa de duplicata pega tarde, ou se ainda escapa alguma — sinal de que o preflight precisa de mais força (ex: script de checagem automática em vez de instrução em prosa).
- `limpeza-duplicatas-catalogo.md` (235 excedentes) segue sem novo caso de produção.
- Canal Claude↔OpenClaw (A2A) — sem objeto enquanto o OpenClaw estiver dormente; não é mais pendência ativa até reprovisionamento.

## Observações
- Dream executado de forma autônoma (scheduled task, sem usuário presente).
- Safra de 3 memórias, mas com uma sessão estrutural grande (08-16) que já fez a maior parte da plasticidade ao vivo, incluindo autocrítica explícita das próprias lacunas. O papel deste ciclo foi auditar essa lista e fechar os itens que eram de fato arquitetura de skill (2 de 6 itens listados), não recriar o trabalho nem tratar as pendências de produto/processo como se fossem do mandato do Dream.
- Padrão reconfirmado: quando uma sessão registra sua própria autocrítica estrutural com itens nomeados, o Dream deve tratar essa lista como backlog de auditoria prioritário — critério mais barato e mais confiável do que garimpar padrões em prosa solta.
- Disciplina aplicada deste ciclo: feedback de comunicação vívido e citável (08-13) foi conscientemente **não** promovido a guardrail por ser ocorrência única — evitando o anti-padrão "criar skill para migalha isolada" mesmo quando a migalha é memorável.
