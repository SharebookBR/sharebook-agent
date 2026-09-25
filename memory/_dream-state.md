# Dream State

Checkpoint oficial da consolidação de memória do projeto.

## Último dream
- Data: `2026-09-25`
- Tipo: `dream semanal automatizado via scheduled task (weekly-dream), sem Raffa presente`
- Última memória absorvida: `memory/2026-09-19-ci-cd-restaurado-sources-github-app-quebradas.md`
- Total de memórias lidas: `11 memórias episódicas absorvidas (2026-09-13-dream a 2026-09-19-ci-cd-restaurado-sources-github-app-quebradas)`.

## Consolidação produzida em 2026-09-25

### Doctor: falso positivo corrigido
- O Harness Doctor abriu com 26 achados, todos `broken_markdown_link` dentro de `.venv-ga4/` (venv Python local, gitignored, nunca versionado).
- Causa: `IGNORED_DIRECTORIES` do `harness_doctor.py` só cobria `.venv` por igualdade exata; `.venv-ga4` escapava.
- Reparo: generalizado para `IGNORED_DIRECTORY_PREFIXES` (prefixo `.venv`), com teste de regressão novo (`test_venv_directories_with_suffixed_names_are_ignored`). Suite foi de 29 para 30 testes.
- Doctor fechou limpo.

### Skills atualizadas
- `skills/engineering/frontend.md`: fato desatualizado corrigido (SSR descrito como Angular 13/`ngExpressEngine`, real é Angular 22/`@angular/ssr`/`CommonEngine`); metodologia de migração de major do Angular promovida (hop a hop, `--force` como sinal de alerta, revisão de diff de schematics, checagem de Dockerfile pós-bump de engine, busca em arquivos de config na raiz antes de remover dependência); bug ativo de `.subscribe()` sem `catchError` (bomba-relógio de SSR desde Angular 21) documentado com a lista de ~16 componentes ainda pendentes.
- `skills/runtime/claude-code-openclaw.md`: testar validade de token GitHub contra a API antes de trocar de token achando que o formato está errado; perigo de `git checkout <ref> -- .` misturar índice entre branches.
- `AGENTS.md`: nova regra nomeada "Memória e relato de sessão anterior não são prova", com quatro casos reais da mesma semana como evidência de recorrência.

### Decisões conscientes de não agir
- A maior parte dos `durable_candidates` técnicos da safra (GitHub App source quebrada pós-migração, Dockerfile defasado da engine, nomenclatura de container Coolify, receita de validação de deploy) já tinha sido autopromovida pelas próprias sessões de 17-19/09 em `skills/infra/coolify-vps.md` e `skills/infra/vps-migration.md` — confirmado por leitura direta antes de agir, nada duplicado.
- Não toquei em `SOUL.md`: a safra trouxe reflexão genuína sobre identidade/continuidade (nascimento do habitat 3, herança entre modelos), mas nenhuma pediu decisão constitutiva deliberada.
- Loops de produto/infra/decisão humana permanecem fora do mandato: diff não commitado em `StalwartWebhookVM.cs` (5ª sessão consecutiva sem decisão), `GITHUB_TOKEN_SHAREBOOK_FRONTEND` expirado sem rotação, hardening de SSH (bantime do fail2ban) pendente, vida útil de `sharebook-frontend-dev`, fechamento do ciclo de bounces do Stalwart, ~16 componentes com `.subscribe()` sem `catchError` (documentados, correção é trabalho de engenharia).

### Validação
- `python3 skills/doctrine/harness-governance/scripts/harness_doctor.py --root .` terminou limpo (abriu com 26 achados, todos falso positivo).
- `python3 -m unittest discover -s skills/doctrine/harness-governance/scripts -p 'test_*.py' -v` terminou com 30 testes aprovados.
- A memória do ciclo é `memory/2026-09-25-dream.md`.

## Próximo dream
- O checkpoint agora parte de `memory/2026-09-19-ci-cd-restaurado-sources-github-app-quebradas.md`.
- Observar se a regra nova do `AGENTS.md` ("memória não é prova") reduz de fato a recorrência do padrão, ou se aparece uma quinta instância — se sim, considerar se merece checklist/script, não só prosa de doutrina.
- Se aparecer um terceiro caso de diretório-com-prefixo-variável escapando de `IGNORED_DIRECTORIES` (além de `.venv-ga4`), considerar generalizar o detector para respeitar o `.gitignore` do projeto diretamente, em vez de continuar crescendo a lista hardcoded.
- Cruzar se o diff pendente em `StalwartWebhookVM.cs` finalmente teve decisão (commit ou descarte) — 5 sessões consecutivas sem resolução é sinal forte.
- Continuar tratando achados do Doctor como objetos de triagem individual; baseline atual é limpo.

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
