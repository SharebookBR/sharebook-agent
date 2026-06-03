---
name: public-ebook-importer
description: Opera e recupera o importer de ebooks públicos/gratuitos do Sharebook. Use quando precisar sincronizar fila, rodar triagem mecânica, preparar publicação, publicar/aprovar ebooks, revisar status canônico, ajustar cron, reanimar worker, diagnosticar ambiente, ou operar o ciclo manual Windows para itens source_blocked.
---

# Sharebook Public Ebook Importer

Uma skill. Uma porta. Sem teatro.

## Documentos desta skill

- **`SKILL.md`** (este arquivo) — operação canônica, workflow, guardrails, hardening
- **`windows-manual.md`** — ciclo completo no Windows para PDFs baixados manualmente
- **`scripts.md`** — índice dos scripts operacionais

---

## Quando usar

- sincronizar source/fila
- rodar `triage-once` ou `publish-once`
- revisar `retry_later`, `error`, `waiting_editor`, `waiting_process` por ID
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
- Falha temporária → `retry_later`, não `error`.
- Editorial faltando → `waiting_editor`, não mascarar como erro técnico.
- **`metadata_json` é acumulativo**: merge sempre, nunca sobrescrever cegamente.
- **`sys.executable`**: nunca hardcode `python3` — no Windows resolve para stub do Microsoft Store.
- **Editorial por source vive no banco**: `importer.sources.editorial_prompt` é a fonte da verdade.
- **Categorias sempre folha**: consultar `GET /api/category/Counts` antes de mapear. Nunca inventar.

---

## Status canônico

```
waiting_triage → triaging → waiting_editor → editing → waiting_process → processing → done
                          ↘ triage_rejected
                          ↘ source_blocked
                          ↘ retry_later
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

O `triage_worker.py` pega item em `waiting_triage`, extrai via `extractors/`, valida PDF, encaminha para `waiting_editor`, `triage_rejected`, `source_blocked` ou `retry_later`.

### 2. Handoff editorial

```bash
python cli.py editor-next --source <SOURCE>
python cli.py plan-set --id <ID> --category-id <UUID> --synopsis-file <FILE> --author "<AUTOR>"
```

### 3. Publicação

```bash
python cli.py publish-once --source <SOURCE>
# ou por ID:
python cli.py publish-once --id <ID>
```

Guardrails de publish:
- `planned_cover_mode='source'` sem `manifest.downloaded_cover_path` → "capa da fonte não foi baixada"
- Publisher precisa garantir `out_dir` antes de gravar `synopsis.txt`

---

## Regras editoriais

- Categoria final: sempre folha
- Sinopse: 3 parágrafos
- Idioma padrão: português
- Plano incompleto → volta para `waiting_editor`
- Capa: preferir fonte; gerar via API OpenAI **apenas com confirmação explícita do Raffa**

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
- Regra editorial canônica: `importer.sources.editorial_prompt`
- Não reabrir consultas extras quando o payload concierge já trouxer o contexto
- `pg_db.mark_item()` deve preservar `metadata_json` por merge — erosão entre etapas é bug estrutural

### Runtime OpenClaw/mini

```bash
cd /data/workspace/sharebook-ebook-importer && sh -c 'python3 cli.py editor-next --source <SOURCE>'
```

Não separar `cd` e `python3` em steps distintos no contexto agentic/cron.

---

## Worker Hardening Patterns

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

### `sync_queue` — comportamento correto

Sync atualiza apenas `title` e `updated_at` em itens existentes. Nunca resetar `status`, `last_error` ou metadados operacionais.

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
6. Mover para `waiting_editor`

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
- Item preso em `processing`/`triaging`/`editing`: destravar conscientemente
- Confiar no README do importer mais do que em memória antiga

---

Esta skill não substitui julgamento curatorial. Ela descreve a operação do importer.

---

## Scripts

Scripts em `skills/importers/ebook-importer/scripts/`. Regra: se não está aqui, não existe — crie e documente no mesmo commit.

### Ciclo manual Windows

| Script | Comando | O que faz |
|---|---|---|
| `manual_triage_windows.py` | `python ... --ids <ids>` | Triagem: valida PDF, extrai texto, monta metadata → `waiting_editor` |
| `render_covers.py` | `python ... --ids <ids>` | Renderiza página 1 como PNG, atualiza `triage.preview_pages` |
| `publish_fake_pdf.py` | `python ... --id <id>` | Publica com fake.pdf, faz S3 upload do real, marca `done` |

> Plano editorial via `cli.py plan-set` — não por script.

### Crawlers / alimentação de sources

| Script | O que faz |
|---|---|
| `crawl_baixelivros_quadrinhos.py` | Raspa BaixeLivros Quadrinhos, insere `waiting_triage`. Idempotente. **Template para novas sources `baixelivros_*`** |
| `crawl_ebook_foundation_subjects.py` | Parseia `free-programming-books-subjects.md`, insere entradas com PDF direto. Idempotente. **Template para novas sources `ebook_foundation_*`** |
| `inspect_baixelivros_listing.py` | Diagnóstico de estrutura de listagem. Usar ao criar nova source |

Temporários (`tmp_*.py`) ignorados pelo git.
