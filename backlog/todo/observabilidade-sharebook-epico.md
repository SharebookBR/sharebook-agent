# Observabilidade Sharebook - saude, diagnostico e continuidade

## Estado

Aberto em 2026-10-08 apos a POC de metricas .NET mostrar valor real em producao: conseguimos observar GC, latencia, cardinalidade, crawlers, SSR e impacto operacional sem depender de intuicao.

Este epico substitui a ideia de uma POC isolada por uma frente permanente e leve de observabilidade do Sharebook.

O objetivo nao e recriar Datadog/Dynatrace inteiro. O objetivo e ter visibilidade suficiente para responder rapido:

> O Sharebook esta saudavel? Se nao esta, onde olhar primeiro?

## Contexto atual

Hoje ja temos algumas pecas importantes:

- **Grafana Cloud / Prometheus / OpenTelemetry**: metricas da API .NET publicadas por OTLP direto, sem Collector local.
- **Rollbar**: error tracking da aplicacao, stack traces e agrupamento de erros.
- **Logs locais na VPS**: `docker logs`, incluindo `ssr_access` do frontend, uteis para investigar crawler, IP, rota e user-agent.
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
- Traces, Loki e logs centralizados entram apenas quando houver pergunta operacional clara.
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

Primeira fatia: `observabilidade-dotnet-laboratorio-24h.md`.

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

### 4. Logs locais e enriquecimento minimo

Enquanto Loki nao existir, usar logs da VPS de forma disciplinada:

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

Loki entra quando depender de `docker logs` virar gargalo real:

- necessidade de busca historica;
- investigacao sem SSH;
- correlacao metricas -> logs na UI;
- multiplos containers/hosts tornando logs locais insuficientes.

Antes disso, nao adicionar Loki apenas por completude arquitetural.

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

Status: em andamento.

- API instrumentada com OpenTelemetry metrics.
- Grafana Cloud Free recebendo metricas via OTLP direto.
- Prometheus read-only consultavel via API.
- GC, heap, allocation rate, latencia e cardinalidade observaveis.

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

Adicionar request id / trace id / duracao / status de forma consistente nos logs da API e, quando fizer sentido, do SSR.

### M4 - Traces amostrados

Adicionar Tempo/Grafana Cloud Traces com sampling conservador para responder onde requests lentas gastam tempo.

### M5 - Backup/restore observavel

Criar rotina simples para verificar backups e executar restore drill periodico sem risco para producao.

## Criterios de sucesso

- Um agente consegue responder "a API esta saudavel?" em ate 5 minutos.
- Um pico de latencia pode ser explicado por rota, volume, erro, crawler ou pressao de runtime.
- Rollbar e Prometheus sao usados juntos durante incidentes.
- Logs locais continuam uteis enquanto Loki nao existir.
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

- `observabilidade-dotnet-laboratorio-24h.md`
- `manutencao-autonoma-producao-rollbar-openclaw.md`
- `migracao-backups-gcp-aws.md`
