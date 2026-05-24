# Scripts do Importer

Consulta, triagem, extração e operações do pipeline de importação.

## Scripts de alimentação de sources (Windows Local)
- `crawl_baixelivros_quadrinhos.py` — raspa a listagem do BaixeLivros Quadrinhos (todas as páginas) e insere itens como `waiting_triage` no banco. Idempotente. **Template para novas sources `baixelivros_*`**: copiar e ajustar `SOURCE_NAME`, `SOURCE_URL` e `BOOK_PREFIX`.
- `crawl_ebook_foundation_subjects.py` — parseia o `free-programming-books-subjects.md` (EbookFoundation) e insere entradas com link direto de PDF como `waiting_triage`. Filtra só PDFs. Idempotente. **Template para novas sources `ebook_foundation_*`**.
- `create_source_ebook_foundation_subjects.py` — one-shot: cria a source `ebook_foundation_subjects` no banco com `editorial_prompt`. Já foi executado.
- `inspect_baixelivros_listing.py` — diagnóstico de estrutura de página de listagem do BaixeLivros (URLs, paginação). Usar ao criar nova source para validar padrões antes de crawlar.

## Scripts de consulta e triagem
- `query_importer_db.py` — consultas no banco do importer.
- `query_importer_v2.py` — variante de consulta do importer.
- `query_importer_wrapper.sh` — wrapper shell para consultas do importer.
- `query_triage_debug.py` — debug de triagem.
- `query_triage_fila.py` — inspeção da fila de triagem.
- `query_triage_rw.py` — operações write-controlled na triagem.
- `triage_get_queue.py` — obtém fila de triagem.
- `triage_stats.py` — métricas da fila.
- `triage-batch.sh` — batch operacional de triagem.

## Scripts de publicação (OpenClaw)
- `sharebook_register_ebook_foundation_item.py` — registra item `ebook_foundation`.
- `sharebook_run_ebook_foundation_worker.py` — roda worker `ebook_foundation`.
- `sharebook_source_extract.py` — extrai metadados e PDF da fonte (livrosdominiopublico).

## Uso
- Preferir estes scripts antes de inventar fluxo manual para importer/triagem.
- Para nova source BaixeLivros: copiar `crawl_baixelivros_quadrinhos.py`, ajustar `SOURCE_NAME`, `SOURCE_URL` e `BOOK_PREFIX`.
