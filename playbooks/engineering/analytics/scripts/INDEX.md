# Analytics Scripts

Ferramentas do playbook de analytics, GA4, SEO, BI e observabilidade.

- `test_ga4_connection.py` — valida conexao com a property GA4.
- `ga4_list_dimensions.py` — lista custom dimensions registradas.
- `ga4_new_events.py` — checa eventos recentes como `search` e `amazon_click`.
- `ga4_events_30d.py` — panorama de eventos dos ultimos 30 dias.
- `ga4_search_via_pagepath.py` — leitura historica de busca via path.
- `backfill_book_download_events_ga4.py` — backfill controlado de downloads GA4 para o banco.
- `grafana_logs.py` — consulta Grafana Cloud Logs/Loki lendo credenciais do `.env`.
