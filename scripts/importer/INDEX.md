# Scripts do Importer

Consulta, triagem, extração e operações do pipeline de importação.

## Scripts
- `query_importer_db.py` — consultas no banco do importer.
- `query_importer_v2.py` — variante de consulta do importer.
- `query_importer_wrapper.sh` — wrapper shell para consultas do importer.
- `query_triage_debug.py` — debug de triagem.
- `query_triage_fila.py` — inspeção da fila de triagem.
- `query_triage_rw.py` — operações write-controlled na triagem.
- `sharebook_register_ebook_foundation_item.py` — registra item `ebook_foundation`.
- `sharebook_run_ebook_foundation_worker.py` — roda worker `ebook_foundation`.
- `sharebook_source_extract.py` — extrai metadados e PDF da fonte.
- `triage-batch.sh` — batch operacional de triagem.
- `triage_get_queue.py` — obtém fila de triagem.
- `triage_stats.py` — métricas da fila.

## Uso
- Preferir estes scripts antes de inventar fluxo manual para importer/triagem.
