# Scripts de Produção

Operações em produção, autenticação, banco e storage.

## Scripts de Analytics GA4
- `test_ga4_connection.py` — testa conexão com a property GA4 (`386966473`). Rodar antes de qualquer outra query GA4.
- `ga4_list_dimensions.py` — lista todas as custom dimensions registradas na property. Útil para diagnosticar por que um parâmetro retorna `(not set)`.
- `ga4_new_events.py` — métricas dos eventos `search` e `amazon_click` por data (ontem + hoje). Ponto de entrada para checar eventos recém-deployados.
- `ga4_events_30d.py` — panorama completo dos 10 eventos rastreados nos últimos 30 dias (ocorrências + usuários).
- `ga4_search_via_pagepath.py` — uso da busca interna via `pagePath /buscar/*` nos últimos 30 dias. Alternativa ao evento `search` para dados históricos anteriores a 04/06/2026.

## Scripts de exploração e diagnóstico
- `explore_db.py` — lista todas as tabelas e row counts dos dois bancos (`sharebook` e `sharebook_importer`). Ponto de entrada rápido para qualquer sessão nova.
- `count_digital.py` — conta livros digitais vs físicos no banco principal. Uso: acompanhar progresso da meta de 1000 digitais.
- `list_categories.py` — exibe a árvore completa de categorias com IDs. Uso: antes de qualquer preparo editorial para confirmar UUIDs.
- `inspect_sources.py` — exibe estrutura e dados da tabela `importer.sources` (incluindo `editorial_prompt`).
- `inspect_item.py` — inspeciona um item da fila do importer por ID (status, metadata, context_text, preview_pages). Uso: `python inspect_item.py <ID>`.

## Scripts de preparo editorial (Windows Local)
- `plan_set.py` — aplica plan-set num item diretamente no banco (categoria, sinopse, autor). Equivalente ao `cli.py plan-set` do OpenClaw, mas roda localmente. Uso: `python plan_set.py --id <ID> --category-id <UUID> --synopsis-file <path> [--author <autor>]`.

## Scripts de autenticação, produção e storage
- `sharebook_aws_s3.py` — upload, download, list e delete no bucket S3 de ebooks.
- `sharebook_prod_auth.py` — autenticação para operações em produção.
- `sharebook_prod_book.py` — find/create/update/delete/approve de livros em produção.
- `sharebook_prod_pg_ro_query.py` — consulta read-only no Postgres de produção.
- `sharebook_prod_pg_ro_query_direct.py` — consulta direta read-only no Postgres de produção.
- `sharebook_prod_pg_rw_exec.py` — executor SQL write-controlled em produção.
- `sharebook_refresh_token.py` — refresh de token operacional.

## Arquivos temporários
- `tmp_synopsis_*.txt` — sinopses geradas por sessão. Podem ser deletados após publicação.

## Uso
- Preferir scripts existentes antes de inventar fluxo manual.
- Sessão nova? Começar com `explore_db.py` e `count_digital.py` para ter contexto rápido do estado atual.
