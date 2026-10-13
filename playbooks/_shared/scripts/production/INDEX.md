# Shared Production Scripts

Clientes compartilhados de producao. Scripts especificos de um playbook devem morar no pacote do proprio playbook; esta pasta fica para primitivas reutilizadas por varios fluxos.

- `prod_env.py` — ponto unico para credenciais de Postgres e SSH vindas do `.env`.
- `sharebook_prod_auth.py` — autenticacao e chamadas HTTP basicas contra a API de producao.
- `sharebook_prod_book.py` — find/create/update/delete/approve de livros em producao.
- `sharebook_aws_s3.py` — upload/download/list/delete no bucket S3 de ebooks.
- `sharebook_refresh_token.py` — renova o token operacional e atualiza o `.env` canonico.
