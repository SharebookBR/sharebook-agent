# Scripts do Importer

Regra: consultar este índice antes de inventar fluxo. Se não está aqui, não existe — crie e documente no mesmo commit.

Scripts vivem em `skills/importers/ebook-importer/scripts/` — dentro da skill, não em pasta separada.

---

## Ciclo manual Windows

Sequência para itens `source_blocked` com PDF disponível localmente. Ver `windows-manual.md` para o fluxo completo.

| Script | Comando | O que faz |
|---|---|---|
| `manual_triage_windows.py` | `python ... --ids <ids>` | Triagem: valida PDF, extrai texto, monta metadata → `waiting_editor` |
| `render_covers.py` | `python ... --ids <ids>` | Renderiza página 1 como PNG, atualiza `triage.preview_pages` |
| `publish_fake_pdf.py` | `python ... --id <id>` | Publica com fake.pdf, faz S3 upload do real, marca `done` |

> O plano editorial é salvo via `cli.py plan-set`, não por script.

---

## Crawlers / alimentação de sources

| Script | O que faz |
|---|---|
| `crawl_baixelivros_quadrinhos.py` | Raspa BaixeLivros Quadrinhos, insere `waiting_triage`. Idempotente. **Template para novas sources `baixelivros_*`** |
| `crawl_ebook_foundation_subjects.py` | Parseia `free-programming-books-subjects.md`, insere entradas com PDF direto. Idempotente. **Template para novas sources `ebook_foundation_*`** |
| `inspect_baixelivros_listing.py` | Diagnóstico de estrutura de listagem. Usar ao criar nova source |

---

## Consulta e diagnóstico

| Script | O que faz |
|---|---|
| `query_importer_db.py` | Consultas gerais no banco |
| `query_importer_v2.py` | Variante de consulta |
| `query_triage_debug.py` | Debug de triagem |
| `query_triage_fila.py` | Inspeção da fila |
| `query_triage_rw.py` | Operações write-controlled |
| `triage_get_queue.py` | Obtém fila de triagem |
| `triage_stats.py` | Métricas da fila |
| `triage-batch.sh` | Batch operacional de triagem (shell) |
| `query_importer_wrapper.sh` | Wrapper shell para consultas |

---

## Publicação legacy (OpenClaw)

| Script | O que faz |
|---|---|
| `sharebook_register_ebook_foundation_item.py` | Registra item `ebook_foundation` |
| `sharebook_run_ebook_foundation_worker.py` | Roda worker `ebook_foundation` |
| `sharebook_source_extract.py` | Extrai metadados e PDF da fonte |

---

## Archive

Scripts já executados ou substituídos vivem em `scripts/archive/`. Ver `scripts/archive/README.md`.

Scripts temporários (`tmp_*.py`) são ignorados pelo git (`scripts/.gitignore`).
