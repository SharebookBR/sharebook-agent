# Scripts de Produção

Operações em produção, autenticação, banco e storage.

## Scripts
- `sharebook_aws_s3.py` — upload, download, list e delete no bucket S3 de ebooks.
- `sharebook_prod_auth.py` — autenticação para operações em produção.
- `sharebook_prod_book.py` — find/create/update/delete/approve de livros em produção.
- `sharebook_prod_pg_ro_query.py` — consulta read-only no Postgres de produção.
- `sharebook_prod_pg_ro_query_direct.py` — consulta direta read-only no Postgres de produção.
- `sharebook_prod_pg_rw_exec.py` — executor SQL write-controlled em produção.
- `sharebook_refresh_token.py` — refresh de token operacional.

## Uso
- Preferir scripts oficiais e mudanças incrementais.
