# Observabilidade Sharebook - saude, diagnostico e continuidade

## Estado

Aberto em 2026-10-08 apos a POC de metricas .NET mostrar valor real em producao: conseguimos observar GC, latencia, cardinalidade, crawlers, SSR e impacto operacional sem depender de intuicao.

Atualizado em 2026-10-12: o epico esta em cerca de **45%**. A fase de prova de valor foi vencida; agora o trabalho e manter e amadurecer a observabilidade minima.

Concluido desde a abertura:

- metricas .NET via OpenTelemetry/OTLP no Grafana Cloud;
- Prometheus/Mimir consultavel por API;
- Grafana Cloud Logs/Loki recebendo request logs da API via Serilog OTLP;
- leitura programatica de Loki com `scripts/observability/grafana_logs.py`;
- playbook unico `playbooks/engineering/grafana-cloud-explorer.md`;
- `ClientIp` validado como publico para trafego real direto na API, downloads e imagens;
- decisao: chamadas internas SSR Node -> API podem permanecer `private/internal`; o `ssr_access` do frontend e a fonte certa para IP real de SSR.

Aberto:

- dashboard minimo formal/versionado;
- correlacao operacional Rollbar + Grafana;
- restore drill;
- traces/Tempo, apenas quando houver pergunta operacional clara.

Resolvido em 2026-10-12: `memory_search` voltou apos restart controlado do Gateway/OpenClaw. O indice e a CLI estavam saudaveis; o problema era estado velho na tool dinamica.

Este epico substitui a ideia de uma POC isolada por uma frente permanente e leve de observabilidade do Sharebook.

O objetivo nao e recriar Datadog/Dynatrace inteiro. O objetivo e ter visibilidade suficiente para responder rapido:

> O Sharebook esta saudavel? Se nao esta, onde olhar primeiro?

## Contexto atual

Hoje ja temos algumas pecas importantes:

- **Grafana Cloud / Prometheus / OpenTelemetry**: metricas da API .NET publicadas por OTLP direto, sem Collector local.
- **Grafana Cloud Logs / Loki**: request logs da API publicados via OTLP e consultaveis por Loki API. Usar `playbooks/engineering/grafana-cloud-explorer.md` e `scripts/observability/grafana_logs.py`.
- **Rollbar**: error tracking da aplicacao, stack traces e agrupamento de erros.
- **Logs locais na VPS**: `docker logs`, incluindo `ssr_access` do frontend, ainda uteis para investigar crawler, IP, rota e user-agent do SSR.
- **GA4 e Search Console**: sinais de produto, SEO e comportamento organico. Search Console usa a mesma credencial de service account do GA4.
- **Coolify + GCP bucket**: backups de bancos e volume `sharebook-wwwroot` configurados e enviados para GCS.
- **Git/backlog/harness**: capacidade de transformar achados em tarefa, patch, deploy e validacao.

## Principios

- Comecar com o que ja existe e custa pouco.
- Manter o plano gratuito do Grafana Cloud saudavel.
- Evitar labels de alta cardinalidade: `user_id`, slug real, query de busca, IP completo, email, token, payload etc.
- Preferir acesso read-only quando possivel.
- Guardar segredos somente em `.env`, Coolify ou secret store; nunca em Git, backlog, memoria ou logs.
- Observar primeiro, formular hipotese depois, otimizar por ultimo.
- Traces entram apenas quando houver pergunta operacional clara. Loki/logs centralizados ja entraram porque a lacuna de observabilidade da API ficou concreta.
- Backup bom e backup que sabemos restaurar; sucesso de job nao substitui teste de restore.

## Workstreams

### 1. Metricas e saude da API

Manter e evoluir a POC atual:

- RPS por rota;
- p50, p95 e p99;
- 4xx e 5xx;
- CPU e memoria do processo;
- allocation rate;
- heap por geracao;
- Gen0, Gen1, Gen2;
- LOH/POH;
- fragmentacao;
- pause time de GC;
- active series e cardinalidade.

Primeira fatia concluida: `backlog/done/observabilidade-dotnet-laboratorio-24h.md`.

### 2. Dashboards Grafana

Criar dashboards simples, versionaveis e baratos:

- `Sharebook - API Health`;
- `Sharebook - .NET Runtime / GC`;
- `Sharebook - Crawlers e SSR`;
- `Sharebook - Observability Budget`.

Evitar dashboard bonito que nao responde pergunta operacional.

### 3. Rollbar e erros de aplicacao

Integrar o uso do Rollbar ao fluxo de investigacao:

- consultar ocorrencias por janela de tempo;
- correlacionar picos de 5xx/latencia com erros;
- identificar regressao por deploy;
- registrar stack trace relevante no diagnostico, sem vazar dado sensivel.

Desejo operacional: acesso Rollbar API read-only.

### 4. Logs centralizados e logs locais

Loki/Grafana Cloud Logs agora e a fonte principal para request logs persistentes da API:

- `service_name="sharebook-api"`;
- `UserAgent` e `ClientIp` como labels/metadata;
- health checks bem-sucedidos suprimidos por design;
- helper compacto: `scripts/observability/grafana_logs.py`.

Logs locais continuam uteis como fallback e para SSR:

- `docker logs` da API;
- `docker logs` do frontend;
- `ssr_access` para IP, user-agent, rota e crawler;
- janelas UTC consistentes com Prometheus.

Proximo passo pequeno:

- enriquecer logs com request id, trace id, rota, status e duracao;
- manter formato facil de filtrar por `rg`, `jq` ou ferramentas simples.

### 5. Traces / Tempo

Adicionar traces somente quando a pergunta exigir:

> Uma request lenta gastou tempo onde?

Quando chegar a hora:

- ativar tracing ASP.NET Core;
- usar sampling conservador;
- incluir spans de HTTP, controller/service e banco quando possivel;
- exportar para Tempo/Grafana Cloud Traces se a cota permitir;
- correlacionar trace id com logs e Rollbar.

### 6. Loki / logs centralizados

Status: operacional desde 2026-10-11/12.

O que ja funciona:

- escrita OTLP logs para Grafana Cloud;
- leitura Loki por API;
- CLI compacto para reduzir custo de tokens;
- validacao de `UserAgent`, `ClientIp` e ausencia de health checks bem-sucedidos.

Ainda falta amadurecer:

- painel/queries padrao para operacao diaria;
- correlacao metricas -> logs na UI;
- alertas ou saved queries somente quando houver uso recorrente.

Atualizacao 2026-10-11: o gatilho aconteceu (restart do container apagou os logs da janela de um incidente do Rollbar). Primeira fatia entregue so para a API, sem infra nova: sink OTLP do Serilog direto para Grafana Cloud Logs, com `ClientIp` e `UserAgent` em todo log da requisicao. Ver `playbooks/engineering/backend.md`, secao "Onde estao os logs". Pendente: `ssr_access` do frontend, e access log do Traefik (hoje desligado).

### 7. Crawlers, SEO e trafego nao humano

Usar metricas, logs SSR e Search Console para separar:

- Googlebot e crawlers com valor SEO;
- crawlers legitimos mas caros;
- bots sem valor claro;
- trafego humano;
- rajadas que funcionam como stress test involuntario.

Exemplo inicial: pico de 2026-10-07 atribuido ao `ShapBot/0.1.0`, com IPs compatveis com a lista oficial da Parallel Web Systems.

Possiveis acoes:

- cachear melhor rotas e servicos acionados por SSR;
- melhorar `CategoryService.getAllWithCounts()`;
- ajustar `robots.txt` apenas se houver custo recorrente;
- rate limit seletivo se virar abuso operacional.

### 8. Backups e continuidade operacional

Tratar backups como parte da observabilidade:

- job executou?
- tamanho faz sentido?
- `s3_uploaded=true`?
- objeto existe no bucket remoto?
- tamanho remoto bate com o registro local?
- quando foi o ultimo restore testado?

Estado verificado em 2026-10-08:

- bancos `sharebook`, `sharebook_importer`, `pegasus_core`, `simula_plus` e `coolify` com ultimos backups `success`;
- ultimos objetos remotos encontrados no bucket GCS `pegasus-coolify-backups`;
- tamanhos remotos batendo com registros locais;
- volume `sharebook-wwwroot` com backup remoto por volta de 1.28 GB;
- auto-update do Coolify em 04:00 UTC, apos janela de backup em 03:00 UTC.

Gap importante:

- ainda falta um ritual de restore drill controlado.

## Marcos

### M0 - POC de metricas .NET

Status: concluido. Movido para `backlog/done/observabilidade-dotnet-laboratorio-24h.md`.

- API instrumentada com OpenTelemetry metrics.
- Grafana Cloud Free recebendo metricas via OTLP direto.
- Prometheus read-only consultavel via API.
- GC, heap, allocation rate, latencia e cardinalidade observaveis.

### M0.5 - Logs da API no Grafana Cloud

Status: concluido em nivel operacional minimo.

- Serilog OTLP logs ativo no `sharebook-api`.
- Loki read validado.
- Helper `grafana_logs.py` criado para consultas compactas.
- Playbook `grafana-cloud-explorer.md` criado.
- `ClientIp` publico validado para trafego direto relevante.

### M1 - Dashboard minimo de saude

Criar dashboard simples para responder:

- a API esta saudavel agora?
- quais rotas mais recebem trafego?
- p95/p99 estao aceitaveis?
- existe 5xx?
- GC parece pressionado?
- active series continuam dentro do plano gratuito?

### M2 - Correlacao Rollbar + Prometheus

Permitir investigacao do tipo:

> P95 subiu as 18:12. Teve exception no Rollbar na mesma janela?

### M3 - Logs mais investigaveis

Status: parcialmente concluido.

Request logs da API ja estao persistentes em Loki com duracao/status/rota, `UserAgent` e `ClientIp`. Ainda falta request id / trace id consistente e convencoes de correlacao com Rollbar.

### M4 - Traces amostrados

Adicionar Tempo/Grafana Cloud Traces com sampling conservador para responder onde requests lentas gastam tempo.

### M5 - Backup/restore observavel

Criar rotina simples para verificar backups e executar restore drill periodico sem risco para producao.

## Criterios de sucesso

- Um agente consegue responder "a API esta saudavel?" em ate 5 minutos.
- Um pico de latencia pode ser explicado por rota, volume, erro, crawler ou pressao de runtime.
- Rollbar e Prometheus sao usados juntos durante incidentes.
- Logs centralizados via Loki respondem investigacoes basicas sem SSH; logs locais continuam uteis como fallback e para SSR.
- Active series ficam dentro do plano gratuito com margem clara.
- Backups nao sao apenas "jobs verdes": ha evidencia de objeto remoto, tamanho coerente e plano de restore.
- Achados viram tarefas pequenas, nao reescritas prematuras.

## Riscos

- Virar stack demais para um produto ainda pequeno.
- Queimar cota gratuita com cardinalidade acidental.
- Otimizar memoria sem dor real.
- Confundir crawler legitimo com ataque.
- Confiar em backup nunca restaurado.
- Espalhar segredo operacional em backlog, memoria ou logs.

## Referencias internas

- `backlog/done/observabilidade-dotnet-laboratorio-24h.md`
- `manutencao-autonoma-producao-rollbar-openclaw.md`
- `migracao-backups-gcp-aws.md`
