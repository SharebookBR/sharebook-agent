# Prometheus Explorer

Playbook para explorar Grafana Cloud / Prometheus / OpenTelemetry do Sharebook sem vazar segredo.

## Use quando

- Raffa pedir metricas, Prometheus, Grafana Cloud, OpenTelemetry, PromQL ou observabilidade.
- A pergunta envolver GC, managed heap, LOH, Gen0/Gen1/Gen2, allocation rate, pause time ou active series.
- For preciso validar se metricas do `sharebook-api` chegaram.
- For preciso correlacionar latencia, rotas, crawlers, cardinalidade e saude da API.

## Capacidade atual

- A API `sharebook-api` exporta metricas OpenTelemetry via OTLP direto para Grafana Cloud.
- Nao ha Collector local nesta POC.
- Nao ha Loki/Tempo/traces/logs via OpenTelemetry nesta POC.
- Prometheus read-only e consultavel via API quando o `.env` canonico contem as variaveis `GRAFANA_CLOUD_*`.

## Variaveis esperadas

Nunca imprimir valores.

- `GRAFANA_CLOUD_OTLP_ENDPOINT`
- `GRAFANA_CLOUD_OTLP_INSTANCE_ID`
- `GRAFANA_CLOUD_OTLP_TOKEN`
- `GRAFANA_CLOUD_PROM_READ_TOKEN_NAME`
- `GRAFANA_CLOUD_PROM_READ_TOKEN`
- `GRAFANA_CLOUD_PROM_USER`

Endpoint Prometheus validado na POC:

```text
https://prometheus-prod-40-prod-sa-east-1.grafana.net/api/prom
```

## Guardrails

- Nao imprimir token, header `Authorization` ou `.env`.
- Nao adicionar labels de alta cardinalidade: `user_id`, slug real, query de busca, IP completo, email, payload etc.
- Preferir labels agregadas como rota parametrizada.
- Separar dado observado de conclusao.
- Nao otimizar memoria antes de observar, formular hipotese e confirmar impacto.

## Metricas confirmadas

- `dotnet_gc_last_collection_heap_size_bytes`
- `dotnet_gc_last_collection_heap_fragmentation_size_bytes`
- `dotnet_gc_heap_allocated_bytes_total`
- `dotnet_gc_collections_total`
- `dotnet_gc_pause_time_seconds_total`
- `dotnet_process_memory_working_set_bytes`
- `http_server_request_duration_seconds_bucket`
- `http_server_request_duration_seconds_count`
- `http_server_request_duration_seconds_sum`

Labels uteis:

- `service_name="sharebook-api"`
- `job="sharebook-api"`
- `gc_heap_generation`
- `http_route`
- `http_request_method`
- `http_response_status_code`

## PromQL util

Allocation rate:

```promql
rate(dotnet_gc_heap_allocated_bytes_total{service_name="sharebook-api"}[5m])
```

GC collections por geracao:

```promql
sum by (gc_heap_generation) (
  rate(dotnet_gc_collections_total{service_name="sharebook-api"}[5m])
)
```

Heap por geracao:

```promql
sum by (gc_heap_generation) (
  dotnet_gc_last_collection_heap_size_bytes{service_name="sharebook-api"}
)
```

Fragmentacao por geracao:

```promql
sum by (gc_heap_generation) (
  dotnet_gc_last_collection_heap_fragmentation_size_bytes{service_name="sharebook-api"}
)
```

Pause rate de GC:

```promql
rate(dotnet_gc_pause_time_seconds_total{service_name="sharebook-api"}[5m])
```

Working set:

```promql
dotnet_process_memory_working_set_bytes{service_name="sharebook-api"}
```

RPS por rota:

```promql
sum by (http_route) (
  rate(http_server_request_duration_seconds_count{service_name="sharebook-api"}[5m])
)
```

P95 por rota:

```promql
histogram_quantile(
  0.95,
  sum by (le, http_route) (
    rate(http_server_request_duration_seconds_bucket{service_name="sharebook-api"}[5m])
  )
)
```

5xx por rota:

```promql
sum by (http_route, http_response_status_code) (
  rate(http_server_request_duration_seconds_count{
    service_name="sharebook-api",
    http_response_status_code=~"5.."
  }[5m])
)
```

## Leitura padrao

1. Comecar por janela ampla: 6h, 12h ou 24h.
2. Checar volume: RPS e top rotas.
3. Checar latencia: p95/p99 agregado e por rota.
4. Checar erros: 5xx e 4xx por rota.
5. Checar runtime: allocation rate, Gen0/Gen1/Gen2, heap, LOH/POH, pause time e working set.
6. Se houver pico, cruzar com logs locais do frontend/API para identificar crawler, IP, user-agent e rota publica.
7. Se houver erro de aplicacao, cruzar com Rollbar.

## Dashboard recomendado

Grafana Dashboard ID `23179` — Dotnet Runtime Metrics.

Use como ponto de partida. Ajustar filtros para `sharebook-api` se necessario.
