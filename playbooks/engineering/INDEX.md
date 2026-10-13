# Família de Playbooks — Engenharia

Conhecimento de frontend, backend, banco, analytics, observabilidade, logs, error tracking, tags do catálogo, mecanismos de descoberta e performance técnica.

## Playbooks
- `./frontend.md` — Angular, UI patterns, Mobile, SSR v2, `ssr_access`, crawler/bot em SSR, JWT interceptor e download de ebook (URL assinada, rate limit, clique repetido).
- `./backend.md` — .NET, EF Core, migrations, arquitetura hexagonal, logs da API, Rollbar, `JobHistories`, `JobExecutor`, SMTP/e-mail transacional e incidentes.
- `./tag-manager/PLAYBOOK.md` — Tags do catálogo: modelo de dados, motor mecânico, vocabulário, scripts de backfill/refinamento/verificação e endpoints.
- `./postgres-ro/PLAYBOOK.md` — Consultas SQL seguras e exploração de dados.
- `./postgres-slow-query-analysis/PLAYBOOK.md` — Diagnóstico e otimização de performance no banco.
- `./analytics/PLAYBOOK.md` — GA4, GSC, SEO, Business Intelligence, Grafana/Loki e scripts de métricas/dashboards.
- `./search-console-explorer/PLAYBOOK.md` — investigação ad hoc de aquisição orgânica, comparação de períodos e oportunidades de SEO no GSC.
- `./grafana-cloud-explorer.md` — Grafana Cloud como superfície única de investigação: Prometheus/Mimir, Loki, OTLP, métricas, logs, PromQL, LogQL, GC, active series, cardinalidade, `ClientIp`, `UserAgent` e saúde da API.

## Uso
- Ler quando a tarefa envolver implementação, diagnóstico técnico, queries, analytics, SEO técnico, observabilidade, Grafana Cloud, Prometheus/Mimir, Loki, OpenTelemetry/OTLP, PromQL, LogQL, Rollbar, logs, SSR access, crawler, bot, erro em produção, SMTP/e-mail transacional, tags do catálogo, vocabulário controlado, mecanismos de descoberta ou performance.

## Scripts úteis da família

- `../../playbooks/engineering/analytics/scripts/grafana_logs.py` — consulta Grafana Cloud Logs/Loki lendo o `.env` canônico sem expor credenciais. Usar para explorar logs da API com baixo custo de tokens:

```bash
python3 playbooks/engineering/analytics/scripts/grafana_logs.py --since 30m --errors --limit 20
python3 playbooks/engineering/analytics/scripts/grafana_logs.py --contains openclaw-logs-validation --limit 20
python3 playbooks/engineering/analytics/scripts/grafana_logs.py --route /api/Category --user-agent openclaw-logs-validation
```
