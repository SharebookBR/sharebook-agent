# Grafana Cloud Explorer

Playbook para investigar Grafana Cloud no Sharebook sem vazar segredos. Este e o ponto de entrada unico para metricas, logs, OTLP, Prometheus/Mimir, Loki, queries e validacao operacional.

## Use quando

- Raffa pedir Grafana Cloud, observabilidade, OpenTelemetry, OTLP, Prometheus, Mimir, PromQL, Loki, LogQL, logs da API ou Grafana Explore.
- A pergunta envolver latencia, P95/P99, saude da API, GC, heap, allocation rate, active series, cardinalidade, request logs, `ClientIp` ou `UserAgent`.
- For preciso validar se metricas ou logs do `sharebook-api` chegaram ao Grafana Cloud.
- For preciso separar ingestao aceita de dado realmente consultavel.

## Capacidade atual

- A API `sharebook-api` exporta metricas OpenTelemetry via OTLP direto para Grafana Cloud.
- A API `sharebook-api` envia logs Serilog via OTLP para Grafana Cloud Logs/Loki quando `GrafanaLogs__Endpoint` e `GrafanaLogs__Headers` estao configuradas no ambiente da aplicacao.
- Request logs usam `service_name="sharebook-api"` e carregam `ClientIp` e `UserAgent` como labels/metadata.
- Health checks bem-sucedidos (`/api/Operations/Ping`, `/hc`, `/health`) sao suprimidos do sink normal por design; falhas continuam relevantes.
- Nao ha Collector local nesta POC. Nao assumir Tempo/traces sem validar no stack.

## Segredos e variaveis

Nunca imprimir valores de token, header `Authorization`, `.env` completo, Basic Auth ou base64 de credencial.

Variaveis canonicas no `.env`:

- `GRAFANA_CLOUD_OTLP_ENDPOINT`
- `GRAFANA_CLOUD_OTLP_INSTANCE_ID`
- `GRAFANA_CLOUD_OTLP_TOKEN`
- `GRAFANA_CLOUD_PROM_READ_TOKEN_NAME`
- `GRAFANA_CLOUD_PROM_READ_TOKEN`
- `GRAFANA_CLOUD_PROM_USER`
- `GRAFANA_CLOUD_LOGS_OTLP_ENDPOINT`
- `GRAFANA_CLOUD_LOGS_OTLP_INSTANCE_ID`
- `GRAFANA_CLOUD_LOGS_OTLP_TOKEN`
- `GRAFANA_CLOUD_LOGS_LOKI_URL`
- `GRAFANA_CLOUD_LOGS_READ_USER`
- `GRAFANA_CLOUD_LOGS_READ_TOKEN`

Inventario seguro: listar somente nomes de variaveis. Para valores, carregar em memoria dentro do script e nunca ecoar.

## OTLP write vs Loki read

- OTLP e caminho de ingestao. Para logs, a URL sinal-especifica termina em `/otlp/v1/logs`.
- Loki e caminho de leitura. A query usa `GET <LOKI_URL>/loki/api/v1/query_range`.
- `204` no OTLP prova que o gateway aceitou o payload; nao prova que voce consegue consultar no Loki.
- O usuario/tenant do Loki pode ser diferente do instance id OTLP. Nao reaproveitar no chute; ler `GRAFANA_CLOUD_LOGS_READ_USER` ou o card Grafana Cloud Logs > Details.
- `401` no Loki quase sempre e `LOKI_URL`, user ou token `logs:read` errado.

## Validacao manual de logs

Preferir o helper compacto quando a tarefa for apenas consultar logs:

```bash
python3 playbooks/engineering/analytics/scripts/grafana_logs.py --since 30m --contains VALIDATION_ID --limit 20
```

Ele le `GRAFANA_CLOUD_LOGS_LOKI_URL`, `GRAFANA_CLOUD_LOGS_READ_USER` e `GRAFANA_CLOUD_LOGS_READ_TOKEN` do `.env` canonico, mascara/classifica `ClientIp` e evita despejar JSON bruto do Loki no contexto.

1. Criar um `validation_id` unico sem dados pessoais.
2. Enviar um log OTLP sintetico para `GRAFANA_CLOUD_LOGS_OTLP_ENDPOINT` com Basic Auth `GRAFANA_CLOUD_LOGS_OTLP_INSTANCE_ID:GRAFANA_CLOUD_LOGS_OTLP_TOKEN`, sem imprimir o header.
3. Esperar cerca de 30 segundos.
4. Consultar Loki com `GRAFANA_CLOUD_LOGS_LOKI_URL`, `GRAFANA_CLOUD_LOGS_READ_USER` e `GRAFANA_CLOUD_LOGS_READ_TOKEN`.

LogQL util:

```logql
{service_name="sharebook-api"} |= "VALIDATION_ID"
```

Busca mais ampla se o label de servico estiver em duvida:

```logql
{service_name=~".*"} |= "VALIDATION_ID"
```

Se o log aparece na ampla mas nao na primeira, o problema e label/mapeamento de `service.name`. Se nenhuma aparece, investigar tenant/token/endpoint antes de mexer na API.

## Validacao da API em producao

1. Confirmar o commit em producao no Coolify/container.
2. Confirmar que `GrafanaLogs__Endpoint` e `GrafanaLogs__Headers` existem no container novo, imprimindo apenas nomes de env, nunca valores.
3. Redeploy/restart e validar container `healthy`.
4. Confirmar `/api/Operations/Ping` com `200`.
5. Gerar 2 ou 3 chamadas reais com User-Agent unico, por exemplo `openclaw-logs-validation`.
6. Consultar Loki por `service_name="sharebook-api"` e o User-Agent de validacao.
7. Confirmar que chamadas de teste aparecem, que `UserAgent` aparece, que `ClientIp` existe e que health checks bem-sucedidos nao aparecem.

Cuidado: o sink Serilog pode falhar silenciosamente se endpoint ou credencial estiverem errados. Container saudavel nao prova envio de log.

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
6. Se houver erro de aplicacao, cruzar Loki/Grafana Logs com Rollbar.
7. Se houver investigacao de IP/user-agent, verificar se `ClientIp` e real; se vier privado/interno, tratar como problema de ForwardedHeaders/proxy, nao do sink Grafana.

## Armadilhas reais

- Nao assumir que usuario Loki e instance id OTLP sao iguais.
- Nao tratar `204` de ingestao como validacao ponta a ponta.
- Nao consultar endpoint OTLP como se fosse Loki.
- Nao editar env vars do Coolify com `insert/update` cru no banco: valores de `environment_variables.value` sao criptografados pelo model do Coolify.
- Nao imprimir header `Authorization=Basic ...`; montar em memoria.
- Nao confiar em `ClientIp` ate validar contra uma chamada externa conhecida.

## Dashboard recomendado

Grafana Dashboard ID `23179` - Dotnet Runtime Metrics.

Use como ponto de partida para runtime .NET e ajuste filtros para `sharebook-api` quando necessario.
