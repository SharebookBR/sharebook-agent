# Scripts de Produção

Operações em produção, autenticação, banco e storage.

## Credenciais — ponto único
- `prod_env.py` — **módulo base, não é executável**. Lê o `.env` da raiz do `sharebook-agent` via `python-dotenv` e expõe `pg_ro(dbname=None)`, `pg_rw(dbname=None)` e `ssh_credentials(prefix)`. Todo script novo desta pasta que fale com banco ou SSH deve importar daqui.
  ```python
  from prod_env import pg_ro, pg_rw, ssh_credentials
  conn = pg_rw(dbname="sharebook_importer")   # sem dbname, usa o do .env
  ```
  `ssh_credentials()` aponta por padrão para a HostGator (produção desde 2026-08-17); use `ssh_credentials("VPS_SSH")` para a caixa antiga da Hostinger.
  **Nunca hardcode host, usuário ou senha em script.**

## Scripts de Analytics GA4
→ Indexados em `skills/engineering/analytics/SKILL.md`

## Scripts de exploração e diagnóstico
- `explore_db.py` — lista todas as tabelas e row counts dos dois bancos (`sharebook` e `sharebook_importer`). Ponto de entrada rápido para qualquer sessão nova.
- `count_digital.py` — conta livros digitais vs físicos no banco principal. Uso: acompanhar progresso da meta de 1000 digitais.
- `list_categories.py` — exibe a árvore completa de categorias com IDs. Uso: antes de qualquer preparo editorial para confirmar UUIDs.
- `inspect_sources.py` — exibe estrutura e dados da tabela `importer.sources` (incluindo `editorial_prompt`).
- `inspect_item.py` — inspeciona um item da fila do importer por ID (status, metadata, context_text, preview_pages, `triage_attempts`/`publish_attempts`). Carrega credenciais via `.env`. Uso: `python inspect_item.py <ID>`.

## Scripts de preparo editorial (Windows Local)
- `plan_set.py` — wrapper fino: encaminha os argumentos para `cli.py plan-set` da CLI canônica do importer via subprocess. Não duplica SQL nem credenciais localmente. Uso: `python plan_set.py --id <ID> --category-id <UUID> --synopsis-file <path> [--author <autor>]`.

## Scripts de autenticação, produção e storage
- `sharebook_aws_s3.py` — upload, download, list e delete no bucket S3 de ebooks.
- `sharebook_prod_auth.py` — autenticação para operações em produção.
- `sharebook_prod_book.py` — find/create/update/delete/approve de livros em produção.
- `sharebook_prod_pg_ro_query.py` — consulta read-only no Postgres de produção via SSH, usando o `psql` do host remoto.
- `sharebook_prod_pg_ro_query_direct.py` — consulta direta read-only no Postgres de produção; usa `psql` quando disponível e recorre a `psycopg2` no Windows.
- `sharebook_prod_pg_rw_exec.py` — executor SQL write-controlled em produção.
- `sharebook_refresh_token.py` — refresh de token operacional.

## Arquivos temporários
- `tmp_synopsis_*.txt` — sinopses geradas por sessão. Podem ser deletados após publicação.

## Uso
- Preferir scripts existentes antes de inventar fluxo manual.
- Sessão nova? Começar com `explore_db.py` e `count_digital.py` para ter contexto rápido do estado atual.
