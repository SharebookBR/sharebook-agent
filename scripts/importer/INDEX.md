# Scripts do Importer

Regra: consultar este índice antes de inventar fluxo manual. Se o script não está aqui, não existe — crie e documente no mesmo commit.

---

## Ciclo manual Windows (source_blocked → done)

Scripts do fluxo para itens que o worker automático não consegue processar. Sequência canônica:

1. `manual_triage_windows.py --ids <ids>` — triagem: valida PDF, extrai texto, monta metadata → `waiting_editor`
2. `cli.py plan-set --id <id> ...` — plano editorial (título, sinopse, categoria, autor) → `waiting_process`
3. `render_covers.py --ids <ids>` — renderiza capa (página 1 do PDF como PNG), atualiza metadata
4. `publish_fake_pdf.py --id <id>` — publica com PDF fake, faz upload do real no S3 → `done`

### Detalhes

- **`manual_triage_windows.py`** — replica `TriageWorker.run_once()` no Windows. PDFs em `Downloads/<id>.pdf`. Aceita múltiplos IDs. Tem `--dry-run`.
- **`render_covers.py`** — renderiza página 1 via pdftoppm. Normaliza sufixo do PNG (1, 01, 001). Aceita múltiplos IDs.
- **`publish_fake_pdf.py`** — lê plano do banco, publica com `C:\Temp\fake.pdf`, faz S3 upload do PDF real, marca `done`. Requer token válido (rodar `sharebook_refresh_token.py` se 401).

---

## Crawlers / alimentação de sources

- **`crawl_baixelivros_quadrinhos.py`** — raspa BaixeLivros Quadrinhos e insere itens como `waiting_triage`. Idempotente. **Template para novas sources `baixelivros_*`**: copiar, ajustar `SOURCE_NAME`, `SOURCE_URL`, `BOOK_PREFIX`.
- **`crawl_ebook_foundation_subjects.py`** — parseia `free-programming-books-subjects.md` (EbookFoundation) e insere entradas com link direto de PDF. Filtra só PDFs. Idempotente. **Template para novas sources `ebook_foundation_*`**.
- **`inspect_baixelivros_listing.py`** — diagnóstico de estrutura de listagem BaixeLivros. Usar ao criar nova source.

---

## Consulta e diagnóstico

- **`query_importer_db.py`** — consultas gerais no banco do importer.
- **`query_importer_v2.py`** — variante de consulta.
- **`query_triage_debug.py`** — debug de triagem.
- **`query_triage_fila.py`** — inspeção da fila.
- **`query_triage_rw.py`** — operações write-controlled na triagem.
- **`triage_get_queue.py`** — obtém fila de triagem.
- **`triage_stats.py`** — métricas da fila.
- **`triage-batch.sh`** — batch operacional de triagem (shell).
- **`query_importer_wrapper.sh`** — wrapper shell para consultas.

---

## Publicação legacy (OpenClaw)

- **`sharebook_register_ebook_foundation_item.py`** — registra item `ebook_foundation`.
- **`sharebook_run_ebook_foundation_worker.py`** — roda worker `ebook_foundation`.
- **`sharebook_source_extract.py`** — extrai metadados e PDF da fonte.

---

## Archive

Scripts já executados ou substituídos vivem em `archive/`. Ver `archive/README.md`.

Scripts temporários (`tmp_*.py`) são ignorados pelo git (`.gitignore`) e não devem ser commitados.
