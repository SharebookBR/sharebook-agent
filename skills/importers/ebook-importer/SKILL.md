---
name: public-ebook-importer
description: Opera e recupera o importer de ebooks públicos/gratuitos do Sharebook. Use quando precisar sincronizar fila, rodar triagem mecânica, preparar publicação, publicar/aprovar ebooks, revisar status canônico, ajustar cron, reanimar worker, diagnosticar ambiente, ou operar o ciclo manual Windows para itens source_blocked.
---

# Sharebook Public Ebook Importer

Uma skill. Uma porta. Sem teatro.

## Documentos desta skill

- **`SKILL.md`** (este arquivo) — operação canônica, workflow, guardrails, hardening
- **`windows-manual.md`** — ciclo completo no Windows para PDFs baixados manualmente
- **`scripts/`** — scripts operacionais, indexados na seção **Scripts** deste arquivo

---

## Quando usar

- sincronizar source/fila
- rodar `triage-once` ou `publish-once`
- revisar `triage_retry`, `publish_retry`, `error`, `waiting_editorial`, `waiting_publish` por ID
- instalar, remover ou reinstalar o cron local
- reanimar worker após restart de container
- diagnosticar ausência de bins/deps no ambiente
- operar handoff editorial automático (`editor-next` + `plan-set`)
- ciclo manual Windows → ver `windows-manual.md`

---

## Fonte da verdade

Antes de diagnosticar, partir do container OpenClaw. O repo íntegro do importer fica visível neste mesmo container:

- `/data/workspace/sharebook-ebook-importer/README.md`
- `/data/workspace/sharebook-ebook-importer/cli.py`
- `/data/workspace/sharebook-ebook-importer/setup-importer-cron.sh`

Se esta skill divergir do código/README do importer, o importer manda.

---

## Guardrails

- **ID Único**: `position` foi exorcizado. Toda operação manual usa `--id`.
- PostgreSQL é a única fonte da verdade. Banco: `sharebook_importer` (≠ `sharebook`).
- Não inventar status fora do conjunto canônico.
- `duplicate` não é `done`.
- `triage_rejected` conta como erro.
- `editorial_rejected` = rejeição curatorial humana pós-triagem. Não usar como atalho para falha técnica, bloqueio de source, duplicata ou rejeição automática da triagem.
- Falha temporária → `triage_retry` (triage worker) ou `publish_retry` (publish worker), não `error`.
- Editorial faltando → `waiting_editorial`, não mascarar como erro técnico.
- **`metadata_json` é acumulativo**: merge sempre, nunca sobrescrever cegamente.
- **`sys.executable`**: nunca hardcode `python3` — no Windows resolve para stub do Microsoft Store.
- **Sync de schema → varrer scripts/**: ao redesenhar nomes de status ou colunas, varrer `skills/importers/ebook-importer/scripts/` além dos arquivos `.md`. Scripts Python dependem dos mesmos nomes e quebram silenciosamente se ficarem desatualizados.
- **Sync de schema também alcança `scripts/production/`**: scripts de preparo editorial Windows local (`inspect_item.py`, `plan_set.py`) leem/escrevem no mesmo schema `importer.queue_items` mas vivem fora de `skills/importers/ebook-importer/scripts/` — fácil esquecer na varredura. Incidente real (2026-06-30): `inspect_item.py` quebrou consultando coluna removida `qi.attempts`, corrigida para `triage_attempts`/`publish_attempts`. Ao redesenhar schema, varrer também `scripts/production/*.py`.
- **Editorial por source vive no banco**: `importer.sources.editorial_prompt` é a fonte da verdade.
- **Categorias sempre folha**: consultar `GET /api/category/Counts` antes de mapear. Nunca inventar.

---

## Status canônico

```
waiting_triage → triaging → waiting_editorial → editing → waiting_publish → publishing → done
                           ↘ triage_rejected
                           ↘ source_blocked
                           ↘ triage_retry
                           ↘ editorial_rejected
                           ↘ publish_retry (origem: publish worker)
                           ↘ duplicate
                           ↘ error
```

---

## Workflow canônico (OpenClaw)

### 1. Triagem mecânica

```bash
cd /data/workspace/sharebook-ebook-importer
set -a && . /data/workspace/sharebook-agent/.env && set +a
python cli.py triage-once --source <SOURCE>
# ou por ID específico:
python cli.py triage-once --id <ID>
```

O `triage_worker.py` pega item em `waiting_triage`, extrai via `extractors/`, valida PDF, encaminha para `waiting_editorial`, `triage_rejected`, `source_blocked` ou `triage_retry`.

### 2. Handoff editorial

```bash
python cli.py editor-next --source <SOURCE>
python cli.py plan-set --id <ID> --category-id <UUID> --synopsis-file <FILE> --author "<AUTOR>"
```

Saídas legítimas do handoff:
- publicar o plano via `plan-set`
- rejeitar editorialmente via `editorial-reject`

Não usar `status-set` genérico para rejeição curatorial. O caminho canônico é `python cli.py editorial-reject --id <ID> --reason "<motivo humano>"`.

### 3. Publicação

```bash
python cli.py publish-once --source <SOURCE>
# ou por ID:
python cli.py publish-once --id <ID>
```

Guardrails de publish:
- `planned_cover_mode='source'` sem `manifest.downloaded_cover_path` → "capa da fonte não foi baixada"
- Publisher precisa garantir `out_dir` antes de gravar `synopsis.txt`
- Item com triagem/editorial íntegros e PDF real materializado pode falhar só no transporte do publish. Se `prepare_pdf_for_publish()` estimar payload acima de `upload_request_limit_bytes`, tentar otimização com Ghostscript; se ainda exceder, tratar como gargalo de upload/publish, não como falha de triagem.
- Não inventar PDF fake como solução padrão dentro do OpenClaw. Para PDF grande demais, o conserto estrutural preferido é melhorar o fluxo de upload de arquivos grandes; o workaround Windows com fake PDF + S3 direto continua sendo exceção operacional.

---

## Regras editoriais

- **Preflight antes de investir em sinopse/capa**:
  1. confirmar que título da fila, conteúdo real do PDF e página oficial descrevem a mesma obra;
  2. confirmar em fonte oficial ou no próprio PDF que a licença permite redistribuição gratuita — PDF público não basta;
  3. registrar a evidência de licença no contexto editorial quando ela não estiver explícita no payload.
- Se a obra falhar no critério de redistribuição, usar `triage_rejected` com nota objetiva. Não usar `editorial_rejected`: ausência de licença redistribuível é falha de publicabilidade, não rejeição curatorial de uma obra publicável.
- Categoria final: sempre folha
- Sinopse: 3 parágrafos
- Idioma padrão: português
- Plano incompleto → volta para `waiting_editorial`
- Capa: preferir fonte (capa original do PDF/editora); se a primeira página for só folha de rosto acadêmica sem valor de capa, gerar localmente com `scripts/covers/cover_generate.py` (gratuito, cross-platform) — gerar múltiplas variações e inspecionar visualmente antes de escolher. Gerar via API OpenAI **apenas com confirmação explícita do Raffa**.
- Validação pós-publicação: confirmar `done` no importer, livro íntegro na API e página pública com capa, categoria e ação de download disponíveis.

---

## Agendamento: onde olhar

Dois mecanismos independentes. Não assumir um só.

### Cron Linux local

```bash
bash setup-importer-cron.sh install | status | remove | start-daemon
```

Logs em `var/logs/`. Lock/estado em `var/state/`.

### Cron agentic do OpenClaw

Job `editorial-preparer` em `/data/.openclaw/cron/jobs.json`. Não é triagem mecânica nem publish Python — é preparação editorial automática.

### Ordem de diagnóstico de incidente

1. `crontab -l`
2. `var/logs/importer-cron.log`
3. Postgres: `importer.runs`, `importer.queue_items`
4. `/data/.openclaw/cron/jobs.json`

---

## Bootstrap e recovery do container

### Checklist mínimo

1. bins básicos: `python3`, `flock`, `cron`/`crond`, `crontab`
2. deps: `ghostscript`, `psycopg2`, `PIL`
3. arquivos: `run_worker.sh`, `setup-importer-cron.sh`, `.env`
4. daemon de cron ativo
5. bloco instalado no `crontab`
6. prova real com `triage-once` e `publish-once`

### Incidente real (2026-05-23)

Daemon `cron` morreu com `pidfile` stale em `/run/crond.pid`. Sintomas: `importer-cron.log` parou em horário exato; `setup-importer-cron.sh status` mostra `cron_daemon=stopped`.

Fix:
```bash
cd /data/workspace/sharebook-ebook-importer
cron
bash setup-importer-cron.sh status
```

### Remediação rápida (container pelado)

```bash
apt-get update && apt-get install -y cron ghostscript python3-psycopg2 python3-pil
cd /data/workspace/sharebook-ebook-importer
bash setup-importer-cron.sh install && bash setup-importer-cron.sh status
```

---

## Handoff editorial — fluxo durável

- Uma leitura: `editor-next`
- Uma escrita: `plan-set`
- Uma rejeição curatorial legítima: `python cli.py editorial-reject --id <ID> --reason "<motivo humano>"`
- Regra editorial canônica: `importer.sources.editorial_prompt`
- Não reabrir consultas extras quando o payload concierge já trouxer o contexto
- `pg_db.mark_item()` deve preservar `metadata_json` por merge — erosão entre etapas é bug estrutural

### `editorial_rejected` — doutrina

Usar quando a triagem já aprovou material suficiente para handoff, mas a curadoria humana decide conscientemente não publicar o item.

É para casos como:
- livro real e publicável, mas fraco demais para a linha editorial atual;
- conteúdo válido porém redundante, raso ou desalinhado com a coleção, sem ser duplicata técnica/canônica;
- item que passou na mecânica, mas perde na avaliação humana de qualidade, adequação ou prioridade editorial.

Não usar quando o caso for:
- `triage_rejected`: não é livro publicável, não há PDF redistribuível, é vídeo, curso, página HTML, plataforma paga, pirataria, etc.;
- `source_blocked`: existe possível valor, mas o acesso/asset falhou ou ficou bloqueado;
- `duplicate`: já existe no catálogo pela regra operacional de duplicidade;
- `error`/retry: falha técnica, transitória ou bug de processo.

Exemplos rápidos:
- **Usar `editorial_rejected`**: manual introdutório real, com PDF e metadados íntegros, mas banal demais para entrar na curadoria final.
- **Não usar**: URL do YouTube, landing page sem PDF, Leanpub sem PDF público, PDF corrompido, item já existente.

### Ação canônica para rejeição editorial

Usar o comando nativo do importer:

```bash
python cli.py editorial-reject --id <ID> --reason "<motivo humano>"
```

Opcionalmente, informar `--rejected-by <identificador>`.

Esse comando registra `editorial_rejection` em `metadata_json`, copia o motivo para `last_error`, zera `retry_after`, grava histórico em `importer.queue_item_history` e move o item para `editorial_rejected`.

Nunca documentar `status-set --status editorial_rejected` como caminho principal. `status-set` é ferramenta genérica de manutenção, não semântica curatorial.

### `status-set` — fronteira correta

Usar `status-set` apenas para manutenção operacional genérica, quando o objetivo for corrigir ou destravar estado canônico sem semântica editorial própria.

Exemplos aceitáveis:
- devolver item para `waiting_triage` ou `waiting_publish` durante recovery consciente;
- destravar estado preso para nova passagem do worker;
- ajuste manual excepcional com nota operacional.

Exemplos não aceitáveis:
- rejeição curatorial pós-triagem (`editorial_rejected`);
- simular `plan-set`;
- mascarar falha técnica ou bloqueio de source como decisão humana.

### Runtime OpenClaw/mini

```bash
cd /data/workspace/sharebook-ebook-importer && sh -c 'python3 cli.py editor-next --source <SOURCE>'
```

Não separar `cd` e `python3` em steps distintos no contexto agentic/cron.

---

## Worker Hardening Patterns

### Source blocked como feedback de hardening

Quando um item em `source_blocked` for salvo manualmente, tentar preferencialmente transformar o aprendizado em melhoria do worker/crawler antes de seguir limpando a fila na mão.

Fluxo recomendado:
1. Entender por que caiu em `source_blocked`.
2. Classificar o caso como `true_blocked`, `triage_rejected` ou `recoverable`.
3. Se for `recoverable` e o padrão tiver chance razoável de se repetir, endurecer resolver/extractor/crawler e adicionar teste.
4. Só então corrigir o item e devolver para `waiting_triage` ou avançar pelo ciclo manual.

Exceções existem: WAF agressivo, fluxo assinado, domínio quebrado de forma única, curadoria rara, ou automação com custo maior que o ganho. Nesses casos, documentar o motivo e operar manualmente sem transformar exceção em arquitetura.

### Rejeição precoce (antes do extractor)

- **Vídeos**: `_VIDEO_HOSTS` + `_is_video_url()` → `triage_rejected`
- **Plataformas pagas**: `_PAID_PLATFORM_HOSTS` (ex: `leanpub.com`) + `_is_paid_platform_url()` → `triage_rejected`
- **Pirataria no Archive.org**: verificar `identifier` antes de qualquer request

### `raise_for_restricted_html`

- Manter sinais específicos de bloqueio de conteúdo
- Remover sinais genéricos de auth (`sign in`, `login`) — causam falsos positivos em Open Access
- `AUTHOR_RESTRICTED_SIGNALS`: "personal use only", "do not redistribute", etc.
- `WAF_SIGNALS`: `window.gokuProps`, `awsWafCookieDomainList`

### `classify_url_family` — ordem importa

`direct_pdf` deve ser checado **antes** de `github.io`. URLs como `user.github.io/book.pdf` são PDF direto, não Jupyter Book. Lição aprendida em produção (item 1438).

### Handlers por família

- **Wikibooks**: `en.wikibooks.org/wiki/X` → REST API `/api/rest_v1/page/pdf/X`
- **GitHub raw**: normalizar `github.com/.../raw/{branch}/` → `raw.githubusercontent.com` via `_normalize_github_raw_url()`
- **GitHub repo raiz**: buscar PDF na última release via `api.github.com/repos/{repo}/releases/latest`
- **Wayback**: modificador `if_` força entrega do binário sem toolbar HTML
- **bepress**: handler dedicado `resolve_bepress_assets`
- **Microsoft Download Center**: parsear bloco JSON da página
- **Google Drive**: link `uc?export=download` sem `confirm=t` pode devolver página HTML (interstitial de vírus/tamanho) em vez do PDF. Usar a rota com `confirm=t` para obter o binário real
- **Ebook Foundation / OpenText / links `open/download?type=pdf|print_pdf`**: tentar resolver o asset PDF direto antes de desistir
- **realtimerendering** (Ray Tracing Gems): `CookieJar` + `urllib.request.build_opener` abre a página oficial primeiro, recebe cookies Cloudflare simples, depois baixa o PDF na mesma sessão — "enganador de WAF civilizado". Propaga title/author via manifest.
- **HTML-books sem PDF público direto**: classificar explicitamente por família, não mascarar como erro genérico de `%PDF`
  - `bookdown_html_book` → ex.: `clauswilke.com/dataviz/`, GitBook afins
  - `mdbook_html_book` → ex.: `relm4.org/book/stable/`, `gtk-rs`
  - `browser_print_html_book` → ex.: `raytracing.github.io`, `pbr-book.org`
- O erro canônico deve explicar a família (`livro HTML/bookdown...`, `livro HTML/mdBook...`) para diferenciar falta estrutural de PDF público de falha transitória. `discover_assets_from_html()` emite erro semântico quando não encontra PDF redistribuível → `triage_worker` interpreta como `triage_rejected` limpo, não `source_blocked`.

### Backoff por fase e threshold de bloqueio

Tentativas por fase (não mais global `retry_count`):
- `triage_attempts`: contadas pelo triage worker
- `publish_attempts`: contadas pelo publish worker
- Backoff indexado pelo número de tentativas da fase: 30 min (1) → 2h (2) → 12h (3+)
- **Threshold**: 5 tentativas em qualquer fase → `source_blocked`

### Triagem por subagentes — critério duplo obrigatório

Ao delegar itens a subagentes para triagem (ex.: batch de `source_blocked`, `triage_rejected`), a instrução deve incluir **dois critérios como condição de "recuperável"**, não apenas acessibilidade:

1. **PDF acessível**: URL direta, sem paywall, sem login, sem WAF intransponível.
2. **Licença aberta**: domínio público, CC com redistribuição, autores que explicitamente permitem distribuição gratuita. Não assumir — verificar na página do autor ou no PDF.

Subagentes que verificam só acessibilidade passam itens com "all rights reserved" para `waiting_triage`, o OpenClaw então rejeita e gera retrabalho. Aprendizado: 3 itens revertidos na sessão 06-08 por essa falha de instrução.

Formulação recomendada para a instrução ao subagente:
> "Para cada item, verifique se existe PDF publicamente acessível E se a licença permite redistribuição gratuita. Se algum dos dois critérios falhar, classifique como triage_rejected."

### `sync_queue` — comportamento correto

Sync atualiza apenas `title` e `updated_at` em itens existentes. Nunca resetar `status`, `last_error` ou metadados operacionais.

### Heartbeat de hardening do importer

Quando o heartbeat pegar `source_blocked` recorrente por família de URL, o alvo preferencial é transformar o caso em uma destas saídas:
- resolver asset PDF público reutilizável;
- classificar a família HTML de forma explícita;
- resetar o item para `waiting_triage` e colher feedback real com `triage-once`.

Quiet check sem avanço estrutural é pouco. O heartbeat bom deixa o worker menos burro.

---

## Triagem manual assistida (WAF / browser)

Quando `source_blocked` por WAF, JS challenge ou download assinado:

Ferramentas em `/data/workspace/sharebook-agent/tools/browser-triage`:
- `triage_fetch.js` — inspeciona página e links candidatos
- `download_probe.js` — tenta clique/download
- `save_pdf_via_fetch.js` — browser real + fetch autenticado

Procedimento:
1. Tentar worker normal primeiro
2. Baixar PDF para área neutra (`/data/workspace/tmp/`)
3. Validar magic bytes `%PDF-`
4. Materializar em `var/tmp/triage-<ID>/source.pdf` + previews + `manifest.json`
5. Atualizar `metadata_json` com `triage.mode = manual_browser_assisted`
6. Mover para `waiting_editorial`

Não fingir que o worker Python conseguiu sozinho.

---

## Dashboard do Importador

### admin_notes

- Campo `TEXT` em `importer.queue_items`
- Endpoint: `PATCH /Operations/ImporterItems/{id}/AdminNotes`
- Grant: `GRANT UPDATE (admin_notes)` cirúrgico

### queue_item_history

- Tabela `importer.queue_item_history` (desde 2026-05-29)
- Instrumentada em `mark_item`, `set_plan`, `set_status`
- `changed_by`: `'worker'` | `'agent'` | `'admin'`
- Colunas: `queue_item_id`, `source_id`, `from_status`, `to_status`, `changed_by`, `changed_at`

### triage_rejected — feedback visual

- `_finish()` popula `last_error` e `triage.detail` com mensagem legível em português
- Frontend `getTriageDetail()` lê `triage.detail`, com fallback para `lastError`
- Mapa `_REASON_DETAIL` no worker centraliza as traduções

### Delta D-1

`from_status` da primeira transição do dia = estado à meia-noite. Timezone: `America/Sao_Paulo`.

---

## Diagnóstico mínimo

- Validar `IMPORTER_DB_DSN`
- Se faltar `importer.queue_items`: conexão no banco errado
- Item preso em `publishing`/`triaging`/`editing`: destravar conscientemente
- Confiar no README do importer mais do que em memória antiga

---

Esta skill não substitui julgamento curatorial. Ela descreve a operação do importer.

---

## Scripts

Scripts em `skills/importers/ebook-importer/scripts/`. Regra: se não está aqui, não existe — crie e documente no mesmo commit.

### Ciclo manual Windows

| Script | Comando | O que faz |
|---|---|---|
| `manual_triage_windows.py` | `python ... --ids <ids>` | Triagem: valida PDF, extrai texto, monta metadata → `waiting_editorial` |
| `render_covers.py` | `python ... --ids <ids>` | Renderiza página 1 como PNG, atualiza `triage.preview_pages` |
| `publish_fake_pdf.py` | `python ... --id <id> [--pdf-path <pdf>] [--cover-path <capa>]` | Exceção para PDF grande: cria com fake.pdf, envia o PDF real ao S3, aprova e marca `done`; usa `IMPORTER_DB_DSN` e renova token expirado |

> Plano editorial via `cli.py plan-set` — não por script.

### Crawlers / alimentação de sources

| Script | O que faz |
|---|---|
| `crawl_baixelivros_quadrinhos.py` | Raspa BaixeLivros Quadrinhos, insere `waiting_triage`. Idempotente. **Template para novas sources `baixelivros_*`** |
| `crawl_ebook_foundation_subjects.py` | Parseia `free-programming-books-subjects.md`, insere entradas com PDF direto. Idempotente. **Template para novas sources `ebook_foundation_*`** |
| `inspect_baixelivros_listing.py` | Diagnóstico de estrutura de listagem. Usar ao criar nova source |

Temporários (`tmp_*.py`) ignorados pelo git.
