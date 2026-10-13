# Analytics Scripts

Ferramentas do playbook de analytics, GA4, SEO, BI e observabilidade.

- `test_ga4_connection.py` — valida conexao com a property GA4.
- `ga4_list_dimensions.py` — lista custom dimensions registradas.
- `ga4_new_events.py` — checa eventos recentes como `search` e `amazon_click`.
- `ga4_events_30d.py` — panorama de eventos dos ultimos 30 dias.
- `ga4_search_via_pagepath.py` — leitura historica de busca via path.
- `backfill_book_download_events_ga4.py` — backfill controlado de downloads GA4 para o banco.
- `grafana_logs.py` — consulta Grafana Cloud Logs/Loki lendo credenciais do `.env`.
- `check_weekly_digest.py` — checa consistencia de digest semanal.
- `ga4_channel_deepdive.py` — aprofunda canais e origem de sessoes.
- `ga4_dashboard.py` — monta snapshot analitico em CLI.
- `ga4_downloads_7d.py` — recorte rapido de downloads dos ultimos sete dias.
- `ga4_seo_check.py` — checagem de sinais SEO via GA4.
- `ga4_weekly_sessions.py` — serie semanal de sessoes.
- `generate_sample_dashboard.py` — gera amostra local de dashboard.
- `render_weekly_chart.py` — renderiza grafico semanal.
