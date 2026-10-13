# Postgres Scripts

Ferramentas para exploracao segura do banco e consultas controladas.

- `sharebook_prod_pg_ro_query_direct.py` — consulta read-only direta ao Postgres de producao.
- `sharebook_prod_pg_ro_query.py` — fallback read-only via SSH/docker exec.
- `sharebook_prod_pg_rw_exec.py` — executor SQL write-controlled com confirmacao.
- `sharebook_prod_pg_ro_python.py` e `query_pg8000.py` — clientes Python alternativos.
- `explore_db.py`, `count_digital.py`, `list_categories.py` — inventario rapido de tabelas, acervo digital e categorias.
- `sharebook_cto_db_dashboard.py` — dashboard visual auxiliar.
