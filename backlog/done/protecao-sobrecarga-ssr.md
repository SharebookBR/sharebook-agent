# Proteção contra sobrecarga: SSR → API → Postgres

## Estado

**Concluído em 2026-11-14.** Aberto em 2026-11-12 após crawler + SSR
on-demand causar erros de API; entregou limites SSR 6/3, timeout e degradação
correta, cache/timeout da API e logs persistentes Alloy. O V2 eliminou HTTP
500/Npgsql sob carga, com follow-ups separados para origem externa, pressão de
swap, capacidade estrutural, hardening do socket, restore e testes HTTP.

| fatia | situação |
|---|---|
| 1. Limite de concorrência no SSR | **Publicada** em `sharebook-frontend` master (`ce56bf0`). Aguarda deploy; ver tarefa T1 do OpenClaw. |
| 2. Timeout de 4 s no front | **Publicada** em `sharebook-frontend` master (`598e310`, mensagem de 503 em `c526152`). Aguarda deploy. |
| 3a. Cache de `Recommendations` no backend | **Publicada** em `sharebook-backend` master (`6d4f2cb`), 279 testes passando. Aguarda deploy (automático via Coolify). |
| 3b. `Timeout`/`Command Timeout` do Npgsql | Pendente de configuração no Coolify (tarefa T2 do OpenClaw). |
| 4. Logs do SSR no Loki | **Feito** (T3, `e11431d`) com script Python provisório; **substituição por Grafana Alloy** na T5 (rodada 3). |

### O que a fatia 2 mudou (2026-11-12)

- No SSR, todo GET para a nossa API desiste em **4 s** (`timeoutInterceptor`). Só no servidor: no navegador não há corte, para não quebrar rede móvel lenta.
- Qualquer falha de infraestrutura (timeout, 5xx, status 0) durante a renderização marca a página como **degradada** (`res.locals.ssrDegraded`). Página degradada **não entra no cache de 30 min** e sai com `Cache-Control: no-store`.
- **Bug de SEO encontrado e corrigido:** a página de livro respondia **404** sempre que a chamada do `Slug` falhava, por qualquer motivo, e o `NotFoundPageComponent` reforçava o 404. Durante falha da API o Google recebia "404" em livros que existem. Agora: 404 só se o livro de fato não existe; se a API falhou, **503 + `Retry-After: 30`**.
- Verificado com API falsa lenta: só `Recommendations` lento -> 200 em ~4,4 s sem o bloco e sem cache; API toda lenta -> 503 em ~4,5 s.
- **Feito** (`c526152`): a tela do 503 agora diz "Estamos com instabilidade. Não conseguimos carregar este livro agora. Tente novamente em instantes.", em vez de "Página não encontrada".
- **Possível frente futura:** servir a última versão boa do cache (stale-while-error) em vez de 503 quando a API falhar. Não feito: exige guardar cópia expirada e decidir por quanto tempo é aceitável.

### Achados da medição do OpenClaw (2026-11-12)

- Na hora do primeiro erro EF havia **215 requisições de rotas de banco em andamento contra `Maximum Pool Size=80`** (~2,7x). O `Slug` (normalmente 5 ms) foi a 4,9 s de mediana: latência de **fila por conexão**, não de consulta.
- A connection string **não define `Timeout` nem `Command Timeout`**; os defaults do Npgsql (15 s de espera por conexão e 30 s por comando, a confirmar) somam ~45 s e batem com o máximo observado de 49,6 s. `EnableRetryOnFailure` não é usado.
- `Recommendations` custa 221 ms no baseline (p95 426 ms), ~40x o `Slug`, ~35 mil chamadas/semana. Causa: `GetRecommendationsAsync` carregava o catálogo inteiro disponível a cada chamada e ranqueava em memória. A fatia 3a corrige.
- Uma renderização usa ~1 conexão por vez (Slug e depois Recommendations, em sequência): 30 renderizações simultâneas ocupam ~30 das 80 conexões. O limite 30/18 fica; recalibrar com o log `ssr_overloaded` depois do deploy.
- 1 container de SSR e 1 de API (limite global = por processo). O `ssr_access` do incidente foi perdido no restart do container: não foi possível identificar o bot.

## Incidente que motivou

Madrugada de 2026-11-12, por volta de 03:26 BRT (relato completo do OpenClaw no Rollbar #2941, #2966, #2967, #2968):

- Rajada de **943 respostas da API em 1 minuto** (baseline ~44/min), **99,6% com User-Agent `node.js`**, isto é, SSR do frontend chamando a API. Mix típico de crawler: PDPs, tags e categorias.
- **94 HTTP 500**, 127 erros de conexão EF e 127 `transient failure` em 22 segundos (03:26:05 a 03:26:27), em várias rotas independentes. P95 dos 500: 48,4 s. Requests ficaram pendurados 16 a 50 s.
- Postgres **não** reiniciou, sem OOM, sem `FATAL`, sem `too many clients`, sem deploy ou backup na janela. Recuperou sozinho em ~25 s.
- Não recorrente: zero erros equivalentes em 06–11/11 na janela 03h–04h. O "10ª ocorrência" do Rollbar é agregação de fingerprint.
- **Não identificado** quem foi o bot (SSR não loga no Loki; Traefik sem access log). Googlebot é hipótese, não fato.

Mecanismo provável: rajada → SSR dispara ~2 consultas ao banco por PDP → consultas ficam lentas → conexões presas sem timeout → fila se alimenta sozinha. A causa exata do estol (pool, CPU, I/O, rede) **não está provada**.

## Princípio

Melhor recusar rápido do que esperar 40 s. Indexação é desejável, derrubar o site não. O Google reduz o ritmo sozinho ao ver 429/500/503 e só retira URLs se o erro durar dias; resposta rápida de recusa é muito melhor do que requisição pendurada.

## Decisões

- **Limite de renderizações SSR simultâneas: 30 no total, 18 para bots** (identificados por User-Agent; não é à prova de falsificação, por isso o teto total também protege). Valores configuráveis por variável de ambiente e **recalibráveis** com o número medido (fatia de pedido ao OpenClaw).
- **Resposta ao estourar: `503` + `Retry-After: 5` + `Cache-Control: no-store`**, imediata, sem tocar na API. 503 = servidor sobrecarregado (nosso caso, vale para todos); 429 fica reservado para um eventual rate limit por IP.
- **Só conta o que renderiza de verdade.** Cache HIT, estáticos e requisições coalescidas (que reaproveitam uma renderização em andamento) não contam.
- **Registrar toda recusa e o pico** no log do container (JSON de uma linha, no mesmo padrão do `ssr_access`), para monitorar depois sem depender de infra nova.
- **Timeout de 4 s do front para a API** (GET públicos; importador, uploads e admin ficam de fora). Se estourar em algo secundário durante o SSR (ex: recomendações), a página sai sem o bloco e **não entra no cache de 30 min**. Se estourar em algo essencial (o livro), devolve erro; nunca um 404 falso.
- **Timeouts entre a API e o Postgres** (conexão e comando) menores que os atuais, mais revisão do `Maximum Pool Size` (ver `playbooks/engineering/backend.md`, "Connection pool do Npgsql vs. `max_connections`"). Valores definidos depois da medição.

## Fatias

1. **Limite de concorrência no SSR** (`sharebook-frontend/server.ts`) + log de recusas. Valor: alto. Esforço: baixo. Risco: baixo (recusar errado afeta humanos; mitigado por teto menor para bots).
2. **Timeout de 4 s no front** + não cachear render degradado. Valor: alto. Esforço: baixo a médio. Risco: médio (cuidado com SEO: nunca cachear nem indexar página degradada como se estivesse completa).
3. **Timeouts e pool no backend** (`sharebook-backend`). Valor: alto. Esforço: baixo. Risco: médio (timeout curto demais corta consulta legítima; calibrar com p95 medido).

## Validação

- Teste unitário do limitador: abaixo do limite renderiza; acima responde 503 com `Retry-After`; HIT e coalescido não contam; teto de bot menor que o total.
- Em produção: o log de recusas aparece em `docker logs` do frontend; no próximo pico, comparar nº de 503 com 500 da API. Meta: zero 500 por estol de conexão numa rajada equivalente.
- Search Console → Estatísticas de rastreamento nos dias seguintes: o tempo de resposta e os códigos devem mostrar o Google recuando, sem queda de páginas indexadas.

## Relação com outros itens

- `observabilidade-sharebook-epico.md`: `ssr_access` e access log do Traefik no Loki; `pg_stat_statements`, `log_min_duration_statement`, `log_lock_waits`, `track_io_timing`.
- `cloudflare-cdn-ddos-protection.md`: rate limit na borda absorveria esse tipo de rajada antes de chegar ao SSR.
- `pre-processamento-paginas-e-recomendacoes.md`: solução estrutural; este item é a rede de proteção enquanto ela não existe.

## Pedido ao OpenClaw (somente leitura)

Preciso destes números para calibrar as fatias 1 a 3. **Responder neste arquivo, na seção "Respostas do OpenClaw" abaixo**, com as queries LogQL usadas. Não inventar valor: se uma fonte não estiver acessível, dizer qual.

1. **Concorrência por segundo no incidente.** A partir das linhas `responded ... in X ms` do `{service_name="sharebook-api"}` entre 03:20 e 03:27 BRT de 2026-11-12, reconstruir quantas requisições estavam em andamento a cada segundo (início = timestamp do log − duração). Informar: a concorrência no instante do primeiro erro EF (03:26:05), o pico, e a concorrência típica do baseline (03:20–03:25). Fazer o mesmo só para as rotas que tocam o banco (`Slug`, `Recommendations`, tags, `Category`).
2. **`Maximum Pool Size` e demais parâmetros** da connection string do Postgres **em produção** (variável de ambiente do Coolify; mascarar usuário e senha). Informar também `Timeout`, `Command Timeout` e `Connection Idle Lifetime` se existirem, e se o EF usa `EnableRetryOnFailure` (explica os ~49 s).
3. **Latência p50 e p95 de `Slug` e `Recommendations`**: baseline (últimos 7 dias, tráfego normal) vs. janela do incidente.
4. **Quantas instâncias** do SSR e da API rodam em produção (réplicas/containers), para o limite de 30 ser por processo ou total.
5. **Quem foi:** se `ssr_access` do container do frontend (`docker logs`, janela 03:20–03:30 BRT) ainda existir, listar User-Agent e IP dos requests da rajada e conferir o IP contra a lista oficial do Googlebot (DNS reverso `googlebot.com`). Se o log já foi rotacionado, registrar isso.

### Respostas do OpenClaw

Consulta feita somente para leitura em 2026-11-12. Horários abaixo em BRT (UTC-3), salvo quando a query mostra UTC.

#### 1. Concorrência reconstruída a partir dos logs da API

Para cada linha `responded ... in X ms`, considerei o intervalo `[timestamp - duração, timestamp)`. A contagem é a quantidade de intervalos ativos no instante de cada segundo. Isto mede requisições que **chegaram a registrar resposta**; uma conexão que jamais respondeu não aparece na reconstrução.

| recorte | no primeiro erro EF (03:26:05.513) | pico | baseline 03:20–03:25 |
|---|---:|---:|---:|
| todas as rotas | **305** | **339** às 03:26:03 | p50=0, p95=0, máximo=1; média=0,037 req/s |
| somente rotas que tocam Postgres | **215** | **223** às 03:26:02 | p50=0, p95=0, máximo=1; média=0,027 req/s |

O `0` do baseline não contradiz as ~44 respostas/minuto: é uma amostragem em pontos inteiros de um segundo, e as respostas normais duram poucos milissegundos, portanto quase todas começam e terminam entre dois pontos. O contraste útil é que, no incidente, as requests ficaram penduradas e a concorrência sustentada chegou a 339 (223 nas rotas de banco).

As rotas classificadas como banco foram `Slug`, `Recommendations`, `tag/*`, `Category/*` e `CategoryTree/*`. `category/Counts` (cacheado) e `freightOptions` (enum em memória) ficaram fora deste segundo recorte.

LogQL de coleta (as linhas foram paginadas por intervalos de tempo e a reconstrução foi local):

```logql
{service_name="sharebook-api"} |= "responded"
{service_name="sharebook-api"} |= "connection to database"
```

Janela da primeira query: `2026-11-12T06:20:00Z` a `2026-11-12T06:27:00Z`; da segunda: `06:26:00Z` a `06:27:00Z`. Foram 1.669 linhas `responded` parseáveis. O primeiro erro EF registrado foi `2026-11-12T06:26:05.512731Z`.

#### 2. Pool e timeouts efetivos da API em produção

Connection string lida da variável do container da API, com credenciais mascaradas:

```text
Host=fgsgwsckccgk8sccc4gg0gg0;Port=5432;Database=sharebook;
Username=***;Password=***;Pooling=true;SSL Mode=Disable;
Trust Server Certificate=true;Maximum Pool Size=80;Connection Idle Lifetime=300;
```

| parâmetro | valor |
|---|---|
| `Maximum Pool Size` | **80** |
| `Connection Idle Lifetime` | **300 s** |
| `Timeout` | não configurado na string |
| `Command Timeout` | não configurado na string |
| `EnableRetryOnFailure` | **não usado**: `DatabaseConfiguration.cs` apenas chama `UseNpgsql(connectionString)` |

Assim, não há um retry explícito de EF/Npgsql no código que explique por si os ~49 s. Os valores-padrão dos parâmetros ausentes não foram inferidos como se fossem configuração de produção.

#### 3. Latência de Slug e Recommendations

Dados extraídos de `responded ... in X ms`. O baseline é a janela de sete dias até `2026-11-12T19:16:30Z`, excluído o intervalo do incidente; linhas 5xx foram excluídas do baseline normal. A janela do incidente é `03:20–03:27 BRT` e inclui as respostas 500, pois elas fazem parte da degradação observada.

| endpoint | baseline normal (n, p50, p95) | incidente (n, p50, p95) |
|---|---:|---:|
| `GET /api/book/Slug/{slug}` | 43.008; **5,28 ms**; **23,59 ms** | 278; **4.913,12 ms**; **26.120,07 ms** |
| `GET /api/book/Recommendations/{id}` | 35.489; **221,69 ms**; **425,90 ms** | 252; **21.803,42 ms**; **61.195,87 ms** |

LogQL de coleta (paginado; duração e rota extraídas das linhas retornadas):

```logql
{service_name="sharebook-api"} |= "/api/book/Slug/" |= "responded"
{service_name="sharebook-api"} |= "/api/book/Recommendations/" |= "responded"
```

#### 4. Réplicas em produção

Há **1 container do SSR/frontend** (`sharebook-frontend`) e **1 container da API** (`sharebook-api`) em execução; não há réplicas adicionais. Logo, o limite de 30 da fatia 1 é, no estado atual, efetivamente por processo e também global. Isto deve ser reavaliado se o deploy passar a escalar horizontalmente.

#### 5. Origem da rajada (`ssr_access`)

Não foi possível identificar IP ou User-Agent externo. O container atual do frontend iniciou às `2026-11-12T19:10:08Z`, posterior ao incidente, e `docker logs --timestamps --since 2026-11-12T06:20:00Z --until 2026-11-12T06:30:00Z sharebook-frontend` não contém `ssr_access` para a janela. Portanto não há IP preservado para validar DNS reverso `googlebot.com`; não é correto atribuir a rajada ao Googlebot.

Como contraprova parcial, a API registra que 99,6% das 943 respostas da rajada tinham `User-Agent: node.js`: isso identifica o **SSR como chamador da API**, não o visitante/bot original.

LogQL usado para essa contraprova:

```logql
{service_name="sharebook-api"} |= "responded"
```

## Tarefas do OpenClaw (rodada 2)

Responder em "Respostas do OpenClaw (rodada 2)" abaixo, com evidência (comando ou query e saída resumida). Fazer na ordem. **T2 e T3 alteram produção: seguir o playbook de runtime e registrar exatamente o que foi mudado e como reverter.** Se algo não puder ser feito ou verificado, dizer o quê, sem inventar.

**T1. Conferir o deploy do frontend (somente leitura).** Verificar se o container `sharebook-frontend` já roda o commit `c526152` ou mais novo da master (inclui o limite de concorrência `ce56bf0` e o timeout de 4 s `598e310`). Confirmar que as variáveis `SSR_MAX_CONCURRENT_RENDERS` e `SSR_MAX_CONCURRENT_BOT_RENDERS` **não** estão definidas com valores estranhos (se estiverem ausentes, valem os padrões 30 e 18). Procurar linhas `ssr_overloaded` em `docker logs` desde o deploy e informar quantas, com `peakInFlight`.

**T2. Timeouts do Npgsql na connection string da API (Coolify).** Acrescentar `Timeout=5;Command Timeout=15;` à connection string de produção da `sharebook-api`, mantendo `Maximum Pool Size=80` e o restante igual. Racional: o front passará a desistir em 4 s; trabalho de API além disso é desperdício, e esperar 15 s por conexão de pool só alimenta a fila. Antes de aplicar, registrar o valor atual (mascarado) para reverter. Depois do restart da API, observar 30 minutos no Rollbar e no Loki: se surgirem timeouts novos em rotas que antes funcionavam (ex: listagens grandes, admin, jobs), reverter e relatar qual rota e qual duração. Só aplicar quando a API estiver saudável e fora de horário de pico.

**T3. Logs do SSR no Loki.** Fazer chegar ao Grafana Cloud/Loki os logs JSON do container `sharebook-frontend`, em especial os eventos `ssr_access` e `ssr_overloaded`, com `service_name="sharebook-frontend"`. Escolher a menor solução que sobrevive a restart de container (ver `observabilidade-sharebook-epico.md`, seção de logs; evitar infra nova se houver alternativa simples). Validar com uma query LogQL que retorne eventos de agora. Registrar também se o access log do Traefik pode ser ligado sem custo relevante (para IP e User-Agent reais de quem chega ao SSR); **não ligar sem avisar**, apenas descrever custo e risco.

**T4. Baseline pós-deploy da API (depois que o Raffa confirmar o deploy da fatia 3a).** Repetir as medições do pedido anterior para `Recommendations` e `Slug`: p50 e p95 nas primeiras 24 h depois do deploy, concorrência de pico nas rotas de banco, e se a carga no Postgres caiu. Comparar com o baseline de `221,69 ms` / `425,90 ms` do `Recommendations`.

### Respostas do OpenClaw (rodada 2)

#### Registro pré-alteração — 2026-11-12 (BRT)

T2 — a API estava `healthy` e respondia `GET /api/Operations/Ping = 200`. A variável atual do Coolify, com credenciais mascaradas, era:

```text
Host=fgsgwsckccgk8sccc4gg0gg0;Port=5432;Database=sharebook;
Username=***;Password=***;Pooling=true;SSL Mode=Disable;
Trust Server Certificate=true;Maximum Pool Size=80;Connection Idle Lifetime=300;
```

Reversão registrada antes da mudança: restaurar exatamente esta string na variável `ConnectionStrings__PostgresConnection` da aplicação `sharebook-api` pelo model `App\\Models\\EnvironmentVariable` do Coolify e redeployar/reiniciar a API. Não há `Timeout` nem `Command Timeout` nesta versão anterior.

T3 — não havia coletor de logs de container (`vector`, `promtail`, `alloy` ou `fluent*`), nem plugin Docker de Loki; o frontend usava o driver `json-file` com rotação `max-size=10m`, `max-file=3`, e não tinha variável OTEL/log configurada. Reversão planejada: remover apenas o coletor dedicado ao frontend e o seu diretório/volume de posições; isto devolve o frontend ao driver `json-file` atual sem alterar o container da aplicação ou Traefik.

#### T1 — deploy do frontend (somente leitura)

**Não passou ainda.** No momento da conferência, o container estava `healthy`, sem restarts, porém a imagem era `ykggs80oko0ck00gsk0c8ckg:598e310b467bd34c853035b7ef8f6959a87f5f60`. Esse SHA é anterior ao `c526152` solicitado: o timeout de 4 s já está presente, mas a correção da mensagem/semântica 503 ainda aguarda deploy. A API, por contraste, já estava em `bosc4k0k8cws844ckosswsw0:6d4f2cbd17ab8e06de3253ce6825e5e87d63abb0`, `healthy`.

As variáveis `SSR_MAX_CONCURRENT_RENDERS` e `SSR_MAX_CONCURRENT_BOT_RENDERS` não estavam definidas no container; portanto os padrões do código são 30 e 18. Desde o deploy atual: **0** linhas `ssr_overloaded`, logo não há `peakInFlight` a reportar ainda.

Comandos usados (saída resumida):

```bash
docker ps --format '{{.Names}} {{.Image}} {{.Status}}'
docker exec sharebook-frontend sh -lc \
  'env | cut -d= -f1 | grep -E "^SSR_MAX_CONCURRENT_(RENDERS|BOT_RENDERS)$" || true'
docker logs --since 24h sharebook-frontend 2>&1 | grep -c ssr_overloaded
# frontend ...:598e310... Up (healthy); api ...:6d4f2cb... Up (healthy)
# (variáveis ausentes); 0
```

T2 e T3 prosseguiram porque a API estava saudável, como permitido pela tarefa.

#### T2 — timeouts Npgsql

Aplicado fora do pico, via `App\\Models\\EnvironmentVariable` do Coolify (não por update SQL direto), mantendo todo o valor anterior e acrescentando apenas:

```text
Timeout=5;Command Timeout=15;
```

Valor efetivo após o redeploy (credenciais mascaradas):

```text
Host=fgsgwsckccgk8sccc4gg0gg0;Port=5432;Database=sharebook;
Username=***;Password=***;Pooling=true;SSL Mode=Disable;
Trust Server Certificate=true;Maximum Pool Size=80;Connection Idle Lifetime=300;
Timeout=5;Command Timeout=15;
```

O Coolify fez o deploy `2tteczxbllqpwbuai27f4qzj`, finalizado às 21:41 BRT. Ao fim dos **30 minutos** de observação, o container continuava `healthy`, `GET /api/Operations/Ping` retornava 200 e não houve novos logs de timeout/Npgsql/pool no Loki.

```logql
{service_name="sharebook-api"} |~ "(?i)(timeout|timed out|connection pool|NpgsqlException)"
```

O acesso de leitura ao Rollbar não está configurado neste runtime (não há credencial/API de leitura no `.env`); portanto essa metade da checagem não foi inventada. O Loki não mostrou rota legítima recém-cortada e não houve motivo para reverter. A reversão permanece a registrada antes da mudança: restaurar a string prévia, sem os dois parâmetros, no model do Coolify e redeployar a API.

#### T3 — logs do SSR no Loki

Como não havia coletor nem plugin de logging no host, foi instalado o menor componente persistente que não toca no container do frontend: o serviço systemd `sharebook-frontend-log-shipper`. Ele executa o script versionado `playbooks/engineering/analytics/scripts/ship_docker_logs_to_otlp.py`, segue `docker logs --tail 0 --follow sharebook-frontend` e reanexa após uma substituição/restart do container. Envia apenas esse stream ao endpoint OTLP já usado pelo Sharebook, com resource attribute `service.name=sharebook-frontend`. As três credenciais ficam em `/opt/sharebook-frontend-log-shipper/shipper.env` (modo 0600), copiadas do `.env` operacional sem aparecer em saída ou Git.

Validação: uma requisição pública controlada à Home com User-Agent único retornou 200 e apareceu no Loki como `ssr_access` do novo serviço.

```bash
systemctl is-active sharebook-frontend-log-shipper.service
# active
curl -A 'openclaw-ssr-loki-validation-1794521716' https://www.sharebook.com.br/
# 200
```

```logql
{service_name="sharebook-frontend"} |= "openclaw-ssr-loki-validation-1794521716"
```

Resultado: uma linha JSON `{"event":"ssr_access",...,"status":200,...}` às `2026-11-12T22:15:16Z`. Os campos continuam no corpo JSON (consultáveis com `| json`); não foram promovidos a labels, evitando cardinalidade de IP, rota e User-Agent. O serviço usa `Restart=always` e reconecta por nome de container, portanto sobrevive ao restart/redeploy do frontend sem alterar o app. Não forcei um restart adicional só para o teste, para não introduzir indisponibilidade desnecessária.

Reversão de T3, se for necessária:

```bash
systemctl disable --now sharebook-frontend-log-shipper.service
rm -f /etc/systemd/system/sharebook-frontend-log-shipper.service
rm -rf /opt/sharebook-frontend-log-shipper
systemctl daemon-reload
```

Traefik: o container `coolify-proxy` não tem `--accesslog` configurado. Habilitá-lo exigiria alterar a configuração gerenciada do proxy e geraria uma linha por request; preservar IP/User-Agent exigiria manter headers e aumenta volume/PII em log. Não foi ativado, conforme pedido. O `ssr_access` recém-centralizado já cobre IP e User-Agent que chegam ao SSR.

#### T4 — baseline pós-deploy (medição parcial; janela ainda aberta)

O Raffa autorizou a T4 em 2026-11-13. O frontend `c526152` iniciou em
`2026-11-12T21:38:25Z`; as primeiras 24 horas só terminam em
`2026-11-13T21:38:25Z` (18:38 BRT). Esta é uma medição **parcial**, somente
leitura, até `2026-11-13T12:34:17Z`; a conclusão e qualquer decisão de mover
este item aguardam a repetição agendada para 18:45 BRT.

LogQL coletada em blocos de 15 minutos para não truncar resultados; as
durações vieram de `responded ... in X ms` e os percentis usam interpolação
linear sobre a amostra ordenada:

```logql
{service_name="sharebook-api"} |= "responded"
{service_name="sharebook-api"} |~ "(?i)(connection pool|connection to database|npgsql|canceling statement|timeout)"
{service_name="sharebook-frontend"} |~ "ssr_(access|overloaded)"
```

| medida parcial (21:38:25Z–12:34:17Z) | resultado | baseline anterior |
|---|---:|---:|
| `Slug` | n=6.777; p50 **5,19 ms**; p95 **23,32 ms** | p50 5,28 ms; p95 23,59 ms |
| `Recommendations` | n=6.111; p50 **191,92 ms**; p95 **319,43 ms** | p50 221,69 ms; p95 425,90 ms |
| rotas de banco (`Slug`, `Recommendations`, tags, `Category`, `CategoryTree`) | 22.075 respostas; pico reconstruído **21** em andamento, às 09:25:45Z | incidente: 223 |
| `ssr_overloaded` | **0** linhas; logo nenhum `peakInFlight` registrado | — |
| `ssr_access` com status 503 | **0**; não houve 503 de degradação no log | — |
| respostas API 500 e erros de conexão/pool/Npgsql/timeout | **0** e **0** linhas, respectivamente | — |

O frontend ainda é o mesmo container saudável `cba0d6b2…`, imagem
`c526152…`, iniciado em `2026-11-12T21:38:25Z`, sem restart. O Alloy continua
em teste e o shipper Python está `active`/`enabled`; portanto a promoção ainda
não ocorreu e não foi provocada nesta tarefa.

Fotografia do Postgres às 12:35Z, não uma série histórica: `pg_stat_activity`
mostrou **1** conexão da base, **1** ativa, maior duração ativa **0,000 s**;
`docker stats` mostrou **0,57% CPU**, **26,37 MiB / 7,755 GiB** (**0,33%**).
Não há nesta consulta uma fonte de métricas históricas de CPU/memória/conexões,
portanto ela não permite afirmar o pico do Postgres em toda a janela.

Comandos de produção, todos somente leitura e sem imprimir credenciais:

```bash
docker inspect -f '{{.Config.Image}}|{{.State.Status}}|{{.State.StartedAt}}|{{.RestartCount}}' sharebook-frontend
systemctl is-active sharebook-frontend-log-shipper.service
systemctl is-enabled sharebook-frontend-log-shipper.service
# frontend c526152 healthy, 0 restarts; Alloy running; shipper active/enabled

# dentro do container Postgres, usando POSTGRES_USER/POSTGRES_DB sem exibir valores:
psql -Atc "select count(*), count(*) filter (where state = 'active'), max(now()-query_start) from pg_stat_activity ..."
# 1|1|0.000
docker stats --no-stream ...
# 0.57% CPU | 26.37MiB / 7.755GiB | 0.33%
```

O teste focal do limitador passou: `npm test -- --include=src/app/core/ssr/ssr-render-limiter.spec.ts` → **7/7 SUCCESS**. Ele cobre teto total, teto menor para bots, liberação e pico; a revisão final da validação deve registrar que ainda não há teste HTTP que demonstre diretamente `503` + `Retry-After` nem teste automatizado de HIT/coalescido fora do limitador. O código os trata antes de `renderSsr`, mas isso não substitui a cobertura pedida no critério.

T4 não é concluída nesta medição parcial. A repetição de 24 h foi agendada para
**2026-11-13 18:45 BRT** (`2026-11-13T21:45:00Z`); ela repetirá as queries,
avaliará todos os critérios de `Validação` e só então decidirá se o item pode ir
para `backlog/done/`.

#### T4 — fechamento da janela completa pós-deploy (2026-11-13)

Consulta concluída somente em leitura para a janela exata
`2026-11-12T21:38:25Z`–`2026-11-13T21:38:25Z`, correspondente ao frontend
`c526152` e à API `6d4f2cb`. As consultas foram paginadas em blocos de 10
minutos, carregando as credenciais do `.env` somente em memória; nenhum segredo
foi impresso ou registrado.

LogQL repetida:

```logql
{service_name="sharebook-api"} |= "responded"
{service_name="sharebook-api"} |= "/api/book/Slug/" |= "responded"
{service_name="sharebook-api"} |= "/api/book/Recommendations/" |= "responded"
{service_name="sharebook-api"} |~ "(?i)(connection pool|connection to database|npgsql|canceling statement|timeout)"
{service_name="sharebook-frontend"} |~ "ssr_(access|overloaded)"
```

As durações foram extraídas de `responded ... in X ms`; p50 e p95 usam
interpolação linear sobre a amostra ordenada.

| rota | n | p50 | p95 | baseline anterior |
|---|---:|---:|---:|---:|
| `GET /api/book/Slug/` | 10.395 | **5,15 ms** | **19,11 ms** | 5,28 / 23,59 ms |
| `GET /api/book/Recommendations/` | 9.332 | **192,35 ms** | **306,89 ms** | 221,69 / 425,90 ms |

Foram 75.574 respostas `responded`. A reconstrução das rotas que tocam o
Postgres (`Slug`, `Recommendations`, `tag`, `Category` e `CategoryTree`), com
intervalos `[fim - duração, fim)`, encontrou 34.463 intervalos e pico de
**21 requisições em andamento**, às `2026-11-13T09:25:45.475740Z`. Contagens
por correspondência: Slug 10.383, Recommendations 9.320, tag 462,
CategoryTree 285 e Category 14.319 (a correspondência de Category inclui
CategoryTree). O pico é muito abaixo dos 223 observados no incidente, mas não
é um pico equivalente para validar o comportamento sob rajada.

Não houve linha de erro de conexão/pool/Npgsql/timeout na consulta de uma hora
da API, nem resposta HTTP 500 (ou outra 5xx) na janela: **0 linhas e 0
respostas 500**. Portanto não existe correlação de 500 por conexão a informar;
não se infere causalidade a partir da ausência de eventos.

No frontend, a consulta retornou 11.372 eventos `ssr_access`/`ssr_overloaded`:
**0 `ssr_overloaded`**, sem `peakInFlight` registrado, e **0 `ssr_access`
com status 503**. Isso é tráfego normal, não prova a resposta em um próximo
pico.

Estado/deploy verificado na VPS, sem alteração:

```text
sharebook-frontend: imagem ...:c526152f340418ce4d9e0a3d8da0b7334955f5b4,
  running/healthy, iniciado 2026-11-12T21:38:25.749755627Z, 0 restarts
sharebook-api: imagem ...:6d4f2cbd17ab8e06de3253ce6825e5e87d63abb0,
  running/healthy
Alloy: running, imagem fixada pelo digest registrado, serviço ainda com
  ALLOY_SERVICE_NAME=sharebook-frontend-alloy-test
shipper Python: active e enabled
```

Snapshot read-only atual do Postgres e containers (não é série histórica):

```text
pg_stat_activity: 1 conexão, 1 active, maior duração ativa 0,000 s
docker stats: Postgres 0,01% / 161,9 MiB (2,04%); API 0,30% / 284,2 MiB
  (3,58%); frontend 2,19% / 384,7 MiB (4,84%); Alloy 0,23% / 43 MiB (0,54%)
```

Não há nesta fotografia fonte histórica de CPU, memória, conexões ou carga do
Postgres; portanto a queda de carga no banco ao longo das 24 horas é **não
verificável** por esse snapshot. A connection string presente na API ainda
confirma, sem exibir valor, `Maximum Pool Size=80`, `Timeout=5` e `Command
Timeout=15`.

#### Validação final da T4

- **Teste unitário do limitador: atendido para o escopo coberto** —
  `ssr-render-limiter.spec.ts` passou 7/7 e cobre teto total, teto de bots,
  liberação e pico. O requisito completo, contudo, fica **não atendido** como
  cobertura de integração: não há teste HTTP automatizado de `503` +
  `Retry-After`, nem de HIT/coalescido; a evidência HTTP manual registrada
  anteriormente não substitui esses testes.
- **Log de recusas em produção: atendido no teste controlado V2** — o gerador
  recebeu 62.764 recusas 503 com `Retry-After: 5`; o Alloy registrou 264
  linhas `ssr_overloaded`, pico `peakInFlight=6` e soma de 62.537 recusas
  agregadas. A diferença é compatível com o rate-limit do próprio log.
- **No próximo pico / meta de zero 500 por estol: atendido no teste controlado
  V2, com ressalva operacional** — até bot c=200 houve 0 HTTP 500, 0 erro
  Npgsql/conexão no Loki e máximo de 16 conexões Postgres. A recuperação ficou
  normal no primeiro minuto, mas o monitor interrompeu o restante por swap
  intenso; isto não prova estabilidade sustentada de um pico real.
- **Search Console: para o Raffa conferir**

Conclusão: os números pós-deploy são saudáveis e melhores que o baseline, mas
há critérios técnicos não atendidos ou não verificáveis. Este item permanece
em `backlog/todo`; não foi movido para `backlog/done/`, e `backlog/index.md` e
`backlog/done/index.md` não foram alterados. Ações sugeridas: adicionar teste
HTTP automatizado para 503/Retry-After e HIT/coalescido; observar um pico
controlado ou real equivalente antes de afirmar a validação de produção; e
medir séries históricas do Postgres antes de concluir queda de carga. A
promoção do Alloy permanece para o próximo deploy real, sem promovê-lo nesta
rodada; o proxy read-only de `docker.sock`, restore drill sem evidência e fases
2/3 (demais containers/Postgres) permanecem pendências próprias já registradas
na T5. O link da pré-renderização foi preservado.

#### Teste de carga controlado autorizado pelo Raffa (2026-11-13)

**Abortado pelo gatilho de segurança, sem alterar configuração, container ou
deploy.** A origem disponível era a própria VPS (mesmo IP público do servidor),
portanto a carga passou por `https://www.sharebook.com.br`/Traefik, mas também
disputou CPU e rede do host. Isto limita a extrapolação para tráfego externo.

Pré-checagem: frontend `c526152` e API `6d4f2cb` `healthy`, ambos com 0
restarts; home e PDP responderam 200; Postgres tinha 2 conexões, 1 ativa; o
tráfego normal do minuto anterior foi 18 `ssr_access`. O gerador usou somente
GET público de PDPs e categorias tirados do sitemap, com os UAs
`SharebookLoadTest/1.0` e `SharebookLoadTest-bot/1.0`. Não chamou API,
administração, login, download ou rota interna.

O monitor de 5 s abortou em `2026-11-13T22:37:26Z`: o swap, já alto antes do
teste, subiu de 2.097 para **2.146 MiB** enquanto a etapa humana de concorrência
30 estava ativa. Nenhum outro gatilho apareceu: frontend/API permaneceram
healthy, 0 restarts, máximo observado de Postgres **2** conexões (**1** ativa),
CPU do host abaixo de 90% por 30 s, e o monitor local não viu 500 nem erro de
conexão. A etapa de bot e a de 250 não foram iniciadas.

| etapa executada | 200 | 503 | p50/p95 200 | p50/p95 503 | `Retry-After` nos 503 |
|---|---:|---:|---:|---:|---:|
| humano, c=10, 60 s | 255 | 0 | 3.032 / 4.744 ms | — | — |
| humano, c=30, interrompida | 466 | 148 | 782 / 8.751 ms | 4.327 / **5.723 ms** | **148/148** |

O teto total foi de fato atingido: o Alloy de teste registrou
`ssr_overloaded` com `peakInFlight=30`, `inFlight=30`, `maxTotal=30` e
`maxBots=18`. Porém a recusa não foi imediata nessa origem/condição: p95 de
503 foi 5,723 s, muito acima da meta de 300 ms. Mais grave, a API registrou
**12 respostas 500** e 12 cadeias `connection to database`/`NpgsqlException`
com timeout durante a etapa. Foram 11 `Slug` distintos e 1 `Recommendations`;
não houve linha `connection pool` nem `canceling statement`, portanto a causa
exata (conexão, comando ou saturação de CPU) não foi inferida além da exceção
registrada.

O teste também evidenciou uma lacuna do shipper Python: para o mesmo User-Agent
e recorte, `sharebook-frontend` registrou 602 `ssr_access` (589 200, 13 503),
enquanto `sharebook-frontend-alloy-test` registrou **908** (760 200, **148
503**). A contagem Alloy coincide com todos os 503 vistos pelo cliente; o
shipper atual perdeu linhas sob rajada. Isto reforça a promoção já pendente do
Alloy no próximo deploy real, mas **não** a antecipou nem mudou produção.

Após a parada, a recuperação foi observada por 3 minutos, com uma request
humana a cada 5 s: **36/36 HTTP 200**, p50 **39,64 ms**, p95 **282,44 ms**
(máximo 4.042,83 ms); frontend e API continuaram healthy, sem restart, e
Postgres permaneceu em 2/1 conexões. A recuperação voltou ao normal em menos
de 60 s para 95% das amostras, embora o máximo isolado seja registrado acima.

LogQL usada (janela `2026-11-13T22:35:00Z–22:43:00Z`):

```logql
{service_name="sharebook-frontend"} |= "SharebookLoadTest" |= "ssr_access"
{service_name="sharebook-frontend-alloy-test"} |= "SharebookLoadTest" |= "ssr_access"
{service_name="sharebook-frontend"} |= "ssr_overloaded" |= "SharebookLoadTest"
{service_name="sharebook-api"} |= "responded 500"
{service_name="sharebook-api"} |~ "(?i)(connection to database|NpgsqlException|connection pool|canceling statement)"
{service_name="sharebook-api"} |= "/api/book/Slug/" |= "responded"
{service_name="sharebook-api"} |= "/api/book/Recommendations/" |= "responded"
```

Durante o recorte, p95 da API foi **7.061,39 ms** para `Slug` (n=509) e
**21.520,84 ms** para `Recommendations` (n=410), contra o baseline normal de
19,11 ms e 306,89 ms, respectivamente.

**Critérios do teste controlado:**

- **Recusas 503 + `Retry-After` + p95 abaixo de 300 ms: não atendido.** Todos
  os 148 503 trouxeram o header, mas p95 foi 5.723 ms.
- **Zero 500/erro de conexão e Postgres abaixo de 80: não atendido.** Conexões
  ficaram em 2, mas houve 12 HTTP 500 e 12 exceções Npgsql/DB.
- **Reserva de vaga para humanos sob bot: não verificável.** A etapa de bot não
  iniciou, corretamente, após o abort.
- **Cache em milissegundos durante rajada de bot: não verificável.** Também não
  houve etapa de bot; houve HITs no tráfego humano, mas não prova este critério.
- **`ssr_overloaded` no teto 30/18: parcialmente atendido.** Há evidência do
  teto total 30 e da configuração `maxBots=18`; não houve saturação de bot que
  demonstre 18 recusando e a reserva humana.
- **Recuperação até 60 s sem restart: atendido para p95.** 36/36 200, p95
  282,44 ms, containers saudáveis e sem restart; o máximo isolado de 4,043 s
  permanece registrado.

Conclusão operacional: **não repetir nem elevar a carga agora**. O teste
reproduziu falha real sob uma carga bem menor que a meta máxima; investigar os
12 timeouts/500 e a latência de 503 fora da própria VPS antes de qualquer nova
rodada. A validação de produção da T4 passa de “não verificável” para **não
atendida** no requisito de zero 500 sob rajada equivalente.

## Tarefas do OpenClaw (rodada 3)

Responder em "Respostas do OpenClaw (rodada 3)" abaixo, com evidência (comando ou query e saída resumida). Mesma regra da rodada 2: tudo que altera produção registra antes o estado atual e a reversão, e nada é inventado.

**Contexto da T5.** O coletor atual (`ship_docker_logs_to_otlp.py`, T3) funciona mas é frágil: uma requisição HTTP por linha, linha descartada se falhar, buraco de ~3 s no restart do container e severidade sempre `INFO`. Numa rajada de centenas de linhas por segundo, que é o cenário do incidente, ele atrasa e pode perder linhas. Decisão do Raffa: usar o **Grafana Alloy** (coletor oficial; o Promtail chegou ao fim da vida em 2026-03-02), **só para o frontend por enquanto**. O Alloy faz lotes, reenvio, controle de ritmo e guarda a posição de leitura. Alternativa descartada: Log Drain do Coolify com Fluent Bit (exige redeploy do frontend, muda o driver de log do container e tem relatos de crash em loop, ver `coollabsio/coolify` #2764 e #5327).

**T1b. Deploy do frontend (somente leitura).** A T1 anterior encontrou o frontend em `598e310`. Confirmar se já roda `c526152` ou mais novo. Se ainda não, dizer o que o Coolify mostra para o deploy (fila, erro de build, webhook) e, se o deploy não foi disparado, seguir o procedimento de "Deploy manual quando o webhook não enfileira" de `playbooks/infra/coolify-vps.md`, avisando o Raffa antes.

**T2b. Acompanhamento do `Command Timeout=15` depois de uma noite inteira.** Os jobs noturnos da API usam a mesma connection string, e uma consulta legítima acima de 15 s agora seria cortada. Procurar no Loki, entre 22:00 e 08:00 BRT, ocorrências de `timeout`, `Npgsql`, `canceling statement` e `pool` na API, e comparar com a noite anterior à mudança. Informar também se algum job (`JobHistories`) falhou ou ficou mais lento. Se houver corte de rota ou job legítimo, reverter o `Command Timeout` para um valor maior (ou removê-lo) e relatar qual consulta e quanto ela leva.

**T5. Grafana Alloy só para o frontend, no lugar do script Python.**
1. **Cota.** Informar o plano atual do Grafana Cloud e quanto de logs já é usado por mês (volume ingerido e limite), antes de qualquer mudança.
2. **Endpoint.** O Alloy envia ao endpoint **Loki** (`.../loki/api/v1/push`), que é diferente da URL OTLP usada hoje. Localizar a URL e o usuário (instance ID) da stack e confirmar se o token atual com escopo de escrita de logs serve. Se for preciso um token novo, **pedir ao Raffa por mensagem no backlog**; nunca colocar valor de segredo em arquivo, commit ou resposta.
3. **Instalação isolada.** Instalar a versão estável atual do Alloy como serviço separado (container próprio ou pacote com systemd, o que for mais simples e reversível), com `docker.sock` somente leitura. Não alterar o container do frontend, o Traefik nem a configuração do Coolify. Credenciais em arquivo com modo 0600, como na T3.
4. **Configuração mínima**, só o frontend: `discovery.docker` → `discovery.relabel` (manter apenas o container `sharebook-frontend`) → `loki.source.docker` → `loki.write`. Rótulos: `service_name="sharebook-frontend"` e `deployment_environment="production"`, para as consultas atuais continuarem funcionando. **Não promover IP, rota ou User-Agent a rótulo** (cardinalidade); eles ficam no corpo JSON, consultáveis com `| json`. Se for simples, mapear `ssr_overloaded` para nível de aviso. Registrar o arquivo de configuração usado (sem segredos) no próprio backlog.
5. **Validação sem duplicar.** Primeiro enviar com `service_name="sharebook-frontend-alloy-test"` enquanto o script Python continua ativo. Conferir por LogQL que as linhas do Alloy batem com as do script (mesma contagem de `ssr_access` em uma janela de 10 min). Gerar uma requisição com User-Agent único, como na T3, e achá-la nos dois.
6. **Restart sem buraco.** Validar a continuidade no **próximo deploy real** do frontend (T1b), sem forçar um restart extra: nenhum trecho do log pode faltar entre o container antigo e o novo.
7. **Troca.** Só depois de 5 e 6: trocar o rótulo para `sharebook-frontend`, desligar e remover o serviço `sharebook-frontend-log-shipper` (reversão da T3 já está registrada) e deixar o Alloy como único coletor. Remover `playbooks/engineering/analytics/scripts/ship_docker_logs_to_otlp.py` do repositório e atualizar `playbooks/engineering/grafana-cloud-explorer.md` e o épico de observabilidade com o fluxo novo.
8. **Custo e saúde.** Registrar uso de CPU e memória do Alloy (`docker stats`) depois de 24 h e quanto de log ele envia por dia.
9. **Reversão.** Descrever como voltar ao script Python (reinstalar o serviço da T3) caso o Alloy dê problema.
10. **Próximas fases, só registrar, não fazer:** (a) logs dos demais containers, exceto a API, que já envia por OTLP e duplicaria; (b) métricas de container, host e Postgres. Anotar se o `coolify-sentinel` já coleta CPU e memória por container.

**T6. Conferir o documento de arquitetura.** Ler `playbooks/infra/arquitetura-sharebook.md` (rascunho de Claude, ainda não verificado no servidor). Corrigir o que estiver errado, responder a lista "A confirmar" marcando cada item, e acrescentar o que faltar (containers reais, volumes, como o deploy é disparado). Fazer commit direto no arquivo; nada em produção é alterado nesta tarefa.

**T4 continua aguardando** o deploy do frontend (T1b) e a confirmação do Raffa.

### Respostas do OpenClaw (rodada 3)

#### T1b — deploy do frontend

**Passou.** O frontend já roda `c526152f340418ce4d9e0a3d8da0b7334955f5b4`, está `healthy` e iniciou em `2026-11-12T21:38:25Z`. Logo, inclui o limitador, o timeout SSR de 4 s e a resposta 503 corrigida. Não houve deploy manual nem alteração de produção.

```bash
docker ps --format '{{.Names}}|{{.Image}}|{{.Status}}'
docker inspect -f '{{.Config.Image}}|{{.State.Status}}|{{.State.Health.Status}}|{{.State.StartedAt}}' sharebook-frontend
```

Saída relevante: `sharebook-frontend|...:c526152...|Up ... (healthy)`. A API também está saudável no `6d4f2cb`.

#### T6 — arquitetura

Conferi e reescrevi diretamente `playbooks/infra/arquitetura-sharebook.md`, removendo os itens pendentes que foram verificáveis. O documento agora registra, entre outros pontos:

- SSR chama `https://api.sharebook.com.br/api`, portanto passa pelo Traefik, não por rota Docker interna;
- uma réplica de frontend e uma de API; jobs executam no processo da API e não existe container `Sharebook.Jobs`;
- capas no bind `Images/Books` da API e PDFs/e-books no S3 por URL pré-assinada;
- inventário real de containers, volumes relevantes, GitHub App como source de deploy e backups atuais;
- Sentinel confirmado como processo que envia dados ao Coolify a cada minuto, mas sem afirmar quais métricas ele retém; e restore drill ainda sem evidência de execução concluída.

Comandos/evidências principais:

```bash
docker ps --format '{{.Names}}|{{.Image}}|{{.Status}}'
docker inspect -f '{{range .Mounts}}{{println .Type .Source .Destination .RW}}{{end}}' sharebook-api
docker exec coolify-db psql ... 'select name, source_type, swarm_replicas, status from applications ...'
docker exec coolify-db psql ... 'select ... from scheduled_*_backup*_executions ...'
```

Confirmações observadas: API e frontend com `swarm_replicas=1`; mount da API somente em `/app/wwwroot/Images/Books`; backup de volume mais recente com `s3_uploaded=true` e ~1,23 GB; dumps recentes com tamanhos coerentes. Não foi feita nenhuma alteração em produção nesta tarefa.

#### T2b — acompanhamento do `Command Timeout=15` (janela completa)

**Concluída em 2026-11-13 11:05 UTC.** A janela pós-mudança foi consultada integralmente em `2026-11-13 01:00:00Z–11:00:00Z` (22:00–08:00 BRT), comparada com `2026-11-12 01:00:00Z–11:00:00Z` (22:00–08:00 BRT). Não houve corte de rota nem job legítimo acima de 15 s; não alterei produção e não reverti o `Command Timeout`.

LogQL usada nos dois recortes (consulta com os limites UTC fixos):

```logql
{service_name="sharebook-api"} |~ "(?i)(timeout|npgsql|canceling statement|pool)"
```

| janela | resultado Loki |
|---|---:|
| pós-mudança completa, 22:00–08:00 BRT | **0** linhas |
| noite anterior, 22:00–08:00 BRT | **127** linhas, concentradas no incidente de pool de 03:26 BRT de 12/11 |

Também consultei `JobHistories`, agregando `JobName`, execuções, falhas, média e máximo de `TimeSpentSeconds`. A janela pós-mudança teve **0 falhas** em todos os jobs; os resultados completos foram:

| JobName | execuções | falhas | média (s) | máximo (s) |
|---|---:|---:|---:|---:|
| CancelAbandonedDonations | 1 | 0 | 0,264 | 0,264 |
| CleanupLogsTable | 1 | 0 | 0,083 | 0,083 |
| JobExecutor | 120 | 0 | 2,139 | 5,669 |
| MailSender | 120 | 0 | 0,936 | 4,559 |
| MailSupressListUpdate | 1 | 0 | 1,310 | 1,310 |
| MeetupSearch | 1 | 0 | 1,541 | 1,541 |
| OnboardingEmailSender | 120 | 0 | 0,244 | 0,698 |
| ReleaseScheduledBooks | 1 | 0 | 0,102 | 0,102 |

Comparação direta dos jobs recorrentes com a noite anterior: `JobExecutor` 120 execuções, média **2,139 s**, máximo **5,669 s** (antes: 121, **1,883 s**, **4,128 s**); `MailSender` 120, **0,936 s**, **4,559 s** (antes: 120, **0,715 s**, **1,233 s**); `OnboardingEmailSender` 120, **0,244 s**, **0,698 s** (antes: 120, **0,257 s**, **0,760 s**). As variações de `JobExecutor` e `MailSender` continuam abaixo de 15 s e não vieram acompanhadas de erro no Loki.

SQL read-only usada nas duas janelas:

```sql
select "JobName", count(*),
       count(*) filter (where not "IsSuccess"),
       avg("TimeSpentSeconds"), max("TimeSpentSeconds")
from "JobHistories"
where "CreationDate" >= timestamptz '2026-11-13 01:00:00+00'
  and "CreationDate" < timestamptz '2026-11-13 04:12:48+00'
group by "JobName";
```

Estado efetivo da connection string: a inspeção mascarada registrada após o deploy da rodada 2 continua mostrando `Pooling=true`, `Maximum Pool Size=80`, `Connection Idle Lifetime=300`, `Timeout=5` e `Command Timeout=15`; usuário e senha permaneceram mascarados e nenhum segredo foi impresso. Tentei repetir a inspeção no container `sharebook-api` nesta rodada, com saída filtrada para imprimir somente a presença/parâmetros, mas a conexão SSH da VPS expirou antes de executar o comando. Portanto não tratei essa tentativa como uma nova leitura; a evidência efetiva disponível permanece o registro mascarado da aplicação após o deploy.

Comando de verificação segura tentado:

```bash
python3 playbooks/_shared/scripts/infra/vps_ssh.py --prefix VPS_SSH \
  --cmd "docker inspect sharebook-api --format '{{range .Config.Env}}{{println .}}{{end}}' \
  | sed -E 's/^(ConnectionStrings__PostgresConnection=).*/\\1[masked]/' \
  | grep '^ConnectionStrings__PostgresConnection='
# falhou antes da execução: TimeoutError na conexão SSH
```

Conclusão: **não reverter**. A reversão continua sendo restaurar a string prévia registrada na rodada 2 (sem `Timeout` nem `Command Timeout`) pelo model do Coolify e redeployar a API, caso apareça posteriormente uma consulta legítima cortada.

#### T5 — Grafana Alloy para logs do frontend

**Bloqueada antes de qualquer instalação por falta de credencial de escrita Loki válida.** Não instalei Alloy, não alterei frontend, Traefik, Coolify ou o coletor atual.

Estado pré-alteração e reversão, registrados antes de uma eventual troca:

- `sharebook-frontend-log-shipper.service` está `active` e `enabled`; executa o script Python atual, com `Restart=always` e `RestartSec=3`.
- O arquivo de credenciais do shipper existente está em modo `0600`; nenhum valor foi lido nem registrado.
- Não há container Alloy em execução. A reversão de uma futura troca será restaurar este serviço exatamente como está (unit + script + arquivo de credenciais 0600), habilitá-lo e só então remover/parar Alloy.

```bash
systemctl is-active sharebook-frontend-log-shipper.service
systemctl is-enabled sharebook-frontend-log-shipper.service
systemctl cat sharebook-frontend-log-shipper.service   # EnvironmentFile oculto
docker ps --format '{{.Names}}|{{.Image}}' | grep -i alloy
```

Resultado: `active`, `enabled`, script presente, nenhum Alloy.

O token OTLP atual foi testado em memória contra o endpoint Loki de push com corpo vazio (`{"streams":[]}`), sem imprimir URL, usuário ou token, e recebeu **HTTP 401**. Ele não pode ser reutilizado pelo Alloy. As credenciais disponíveis também não dão acesso ao plano/uso mensal da conta Grafana Cloud: Loki permite consulta de logs, mas não expõe billing/usage com esses tokens. Há menção histórica ao plano Free e retenção de 14 dias nos playbooks, mas isso **não foi tratado como confirmação do plano ou da cota atual**, e volume mensal/limite não foram inventados.

**Pedido ao Raffa para continuar T5:** criar um token de Access Policy da stack Grafana Cloud com escopo `logs:write` para o tenant Loki e disponibilizá-lo somente no `.env` canônico como `GRAFANA_CLOUD_LOGS_WRITE_TOKEN` (modo 0600; não colar valor neste backlog, commit ou Telegram). Também é necessário acesso de leitura ao billing/usage, ou a informação de plano e uso mensal exibida pela conta, para registrar a cota antes da instalação. Depois disso, valido o token, instalo o Alloy isolado e sigo a dupla escrita/teste sem duplicação.

##### Atualização — Caminho 1 e instalação de teste (2026-11-13 04:52 UTC)

O pedido de token novo acima está **superado**: o primeiro 401 usou o *instance ID* OTLP como usuário. Repeti o push vazio com a URL e o **user ID do Loki de leitura**, mantendo o token OTLP atual somente em memória; o resultado foi **HTTP 204**. Portanto o Caminho 1 funciona e o Caminho 2 não foi necessário.

Antes da instalação, o shipper Python ainda estava `active` e `enabled`, sem Alloy em execução; a reversão continua ser parar/remover o container Alloy e os arquivos em `/opt/sharebook-frontend-alloy`, mantendo/reabilitando o shipper Python. Instalei somente o coletor isolado de **teste**:

- imagem estável `grafana/alloy:v1.22.0`, digest `sha256:9acc2529bc1edb7f5b2bd801dd8334ebc80c158e3a9e5526ecd7c9a273d43189`;
- container `sharebook-frontend-alloy`, com `docker.sock` somente leitura, root filesystem somente leitura, `cap-drop=ALL`, `no-new-privileges`, restart `unless-stopped` e diretório persistente de posições;
- credenciais em `/opt/sharebook-frontend-alloy/alloy.env`, modo `0600`; não foram exibidas nem versionadas;
- `service_name="sharebook-frontend-alloy-test"`, preservando o shipper atual em `sharebook-frontend` e evitando duplicação no stream de produção.

Configuração usada (também versionada em `playbooks/engineering/analytics/assets/alloy-frontend.alloy`; sem segredos):

```alloy
discovery.docker "frontend" {
  host = "unix:///var/run/docker.sock"
}

discovery.relabel "frontend" {
  targets = discovery.docker.frontend.targets
  rule {
    source_labels = ["__meta_docker_container_name"]
    regex         = "/sharebook-frontend"
    action        = "keep"
  }
}

loki.source.docker "frontend" {
  host       = "unix:///var/run/docker.sock"
  targets    = discovery.relabel.frontend.output
  forward_to = [loki.write.grafana.receiver]
  labels = {
    service_name           = sys.env("ALLOY_SERVICE_NAME"),
    deployment_environment = "production",
  }
}

loki.write "grafana" {
  endpoint {
    url = sys.env("GRAFANA_CLOUD_LOGS_LOKI_URL") + "/loki/api/v1/push"
    basic_auth {
      username = sys.env("GRAFANA_CLOUD_LOGS_WRITE_USER")
      password = sys.env("GRAFANA_CLOUD_LOGS_WRITE_TOKEN")
    }
  }
}
```

O config passou `alloy validate`; o container está `running`, sem warnings/errors no log inicial, e consumia **0,14% CPU / 36,96 MiB** na primeira leitura. A requisição controlada `alloy-frontend-validation-20261113t0453z` retornou 200 e já apareceu uma vez nos dois streams:

```logql
{service_name="sharebook-frontend"} |= "alloy-frontend-validation-20261113t0453z"
{service_name="sharebook-frontend-alloy-test"} |= "alloy-frontend-validation-20261113t0453z"
```

Validação da janela completa, sem restart forçado, de `2026-11-13T04:52:42Z` a `2026-11-13T05:02:42Z`:

```bash
python3 - <<'PY'
# consulta Loki /loki/api/v1/query_range com os timestamps fixos da janela;
# credenciais carregadas do .env, sem imprimir URL, usuário ou token
for service in ("sharebook-frontend", "sharebook-frontend-alloy-test"):
    query = f'{{service_name="{service}"}} |= "ssr_access"'
    ua_query = f'{{service_name="{service}"}} |= "alloy-frontend-validation-20261113t0453z"'
    print(service, count(query), count(ua_query))
PY
```

Saída resumida: `sharebook-frontend`: **19** `ssr_access`, **1** User-Agent; `sharebook-frontend-alloy-test`: **19** `ssr_access`, **1** User-Agent. Portanto, nesta janela, as contagens batem e a requisição controlada foi confirmada nos dois streams. Não mudei o rótulo para produção, não desliguei/removi o shipper e não forcei restart. A prova de continuidade entre containers continua pendente do próximo deploy real do frontend.

Estado observado na VPS:

```bash
docker inspect -f '{{.State.Status}}|{{.State.StartedAt}}|{{.RestartCount}}' sharebook-frontend-alloy
docker stats --no-stream --format '{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}' sharebook-frontend-alloy
docker logs --since 2026-11-13T04:52:42Z sharebook-frontend-alloy
systemctl is-active sharebook-frontend-log-shipper.service
systemctl is-enabled sharebook-frontend-log-shipper.service
```

Saída resumida: Alloy `running|2026-11-13T04:52:42.656941241Z|0`; stats na coleta `0.18% CPU`, `45.81 MiB` (`0.58%`); logs iniciais terminam em `Alloy is running`, sem warning/error; shipper `active` e `enabled`.

O volume Loki de 24h já observado e registrado antes desta validação foi: API **44.804.761 bytes / 130.205 entries**; frontend **2.468.566 bytes / 7.278 entries**; teste **680.989 bytes / 2.282 entries** no momento da coleta. O stream de teste backfillou logs existentes desde o início do container, por isso não representa volume adicional de produção nem deve ser extrapolado como tráfego novo.

**Cota e estimativa real.** O plano informado pelo Raffa é Cloud Free, com limite de 50 GB/mês para logs; a página mostrava 0 GB. A API `GET /loki/api/v1/index/stats` do próprio Loki, na janela móvel de 24 h, retornou: `sharebook-api` **44.804.761 bytes / 130.205 entries** (~44,8 MB/dia), `sharebook-frontend` **2.468.566 bytes / 7.278 entries** (~2,47 MB/dia). Extrapolação linear bruta: ~**1,42 GB/mês** para API + frontend, muito abaixo de 50 GB. O stream de teste mostrava 680.989 bytes/2.282 entradas, pois o `loki.source.docker` fez backfill dos logs já existentes do container; ele não entra na estimativa de produção e será removido antes da promoção final.

##### Pendência de endurecimento e promoção no próximo deploy (2026-11-13)

`docker.sock:ro` **não** limita a API Docker a operações de leitura; ele só monta o arquivo do socket como somente leitura. A defesa adicional atual (imagem por digest, `cap-drop=ALL`, `no-new-privileges`, filesystem raiz somente leitura e credenciais 0600) permanece, mas há uma pendência explícita: antes de ampliar o Alloy para outros containers, interpor um proxy de socket que permita somente os endpoints Docker necessários para containers e logs, em modo leitura. Isto não bloqueia a promoção do frontend já aprovada.

Baseline da promoção: em `2026-11-13T05:12Z`, o frontend era o container `cba0d6b2…` na imagem `c526152…`, iniciado em `2026-11-12T21:38:25Z` e `healthy`; o shipper Python estava `active` e o Alloy de teste `running`, com zero restarts. Um monitor aguardará um **novo container com imagem diferente**. Logo após esse deploy real, ele vai: parar o shipper, mudar o rótulo do Alloy para `sharebook-frontend`, apagar as posições de teste, reiniciar o Alloy e comparar por minuto `ssr_access` do log local e do Loki na virada. Sem restart artificial e sem remoção do shipper/script antes de a ausência de buraco e duplicata ficar demonstrada.

T2b continua agendada para fechar a janela 22:00–08:00 BRT. T4 permanece sem execução até essa conclusão; depois será reportada como liberada para a confirmação do Raffa.

## Atualização do Raffa e de Claude sobre a T5 (2026-11-13)

**O token novo provavelmente não é necessário.** O Raffa lembrou que já existe credencial de escrita: a própria API envia logs ao Grafana Cloud por OTLP (`GrafanaLogs__Endpoint` e `GrafanaLogs__Headers`, formato `Authorization=Basic <base64(usuario:token)>`, ver `ShareBook.Api/Logging/GrafanaLogsConfiguration.cs` no backend). É o mesmo tipo de credencial que o shipper da T3 já usa, e o OpenClaw testou esse token no endpoint **Loki de push** e recebeu 401.

**Hipótese a verificar antes de pedir qualquer token novo (é hipótese, não fato):** o 401 pode vir do **usuário**, e não do token. No Grafana Cloud, o gateway OTLP usa o *instance ID* da stack como usuário do Basic Auth, enquanto o Loki usa um **user ID próprio**, outro número. Um token de access policy com `logs:write` costuma servir nos dois endpoints, mas o usuário muda. O OpenClaw já consulta o Loki para leitura (`grafana_logs.py`), então **já tem o user ID e a URL do Loki**.

**Caminho 1 (preferido, mais simples):** repetir o teste de push (`{"streams":[]}`, sem imprimir segredo) usando a **URL de push do Loki + o user ID do Loki** (os mesmos da leitura) com o **token OTLP atual**. Se der 204/200, o Alloy usa `loki.write` com esses valores e **não é preciso token novo**.

**Caminho 2 (se o 1 falhar):** o Alloy pode enviar pelo **mesmo gateway OTLP** que a API e o shipper já usam: `loki.source.docker` → `otelcol.receiver.loki` → `otelcol.exporter.otlphttp`, com as credenciais que já existem. Atenção: `service.name` precisa virar *resource attribute* (por exemplo com `otelcol.processor.resource`), senão o Loki não cria o rótulo `service_name`, e as consultas atuais não encontram nada. Validar com a mesma query LogQL.

**Só se os dois falharem** pedir ao Raffa um token novo `logs:write`, como já descrito na resposta da rodada 3.

**Plano e cota (print do Raffa, página "Current Usage", período 01/11/2026 a 30/11/2026):**

| item | limite do plano | uso mostrado |
|---|---|---|
| Plano | **Cloud Free** | - |
| Métricas (séries ativas) | 10 mil | 3.600 |
| Logs | 50 GB | **0 GB** |
| Traces | 50 GB | 0 GB |
| Profiles | 50 GB | 0 GB |

O "0 GB" de logs **contradiz** o fato de a API e o frontend estarem enviando logs desde outubro e novembro. Pode ser atraso ou arredondamento da página de uso, mas **não foi explicado**. O OpenClaw deve estimar o volume real pelo próprio Loki (por exemplo, bytes ingeridos por dia de cada `service_name`) e registrar a estimativa, para não depender desse 0 GB. A retenção de 14 dias dos playbooks continua **não confirmada**.

## Revisão de Claude sobre a instalação de teste do Alloy (2026-11-13)

Revisão dos commits `ee34852` e `2c32642`. Aprovado o que foi feito; dois ajustes para a promoção.

**1. Promover junto com o próximo deploy do frontend, para não duplicar logs.** O stream de teste recebeu 2.282 entradas porque o `loki.source.docker` releu os logs que o container atual já tinha. Se o Alloy for promovido para `service_name="sharebook-frontend"` com o container atual, é provável que reenvie o que o shipper Python já mandou, duplicando o histórico recente no stream de produção. Um container recém-criado começa com log vazio. Procedimento:
- esperar o próximo deploy real do frontend (ou, se o Raffa autorizar, um redeploy deliberado em horário calmo);
- logo depois do container novo subir, em sequência: parar o shipper Python, trocar `ALLOY_SERVICE_NAME` para `sharebook-frontend` e reiniciar o Alloy **com o diretório de posições do teste apagado**, para ele não herdar posição do container antigo;
- conferir por LogQL que não há buraco nem duplicata na virada (contagem de `ssr_access` por minuto em volta do momento da troca);
- só então remover o script Python e o serviço da T3 (passo 7 da T5).
Se preferir promover antes do deploy, comparar primeiro e **medir** quantas linhas duplicam, em vez de supor.

**2. `docker.sock` com `:ro` não torna a API do Docker somente leitura.** O `:ro` só impede escrita no arquivo do socket; quem o monta continua podendo chamar a API inteira (listar, criar e remover containers). A mitigação atual (`cap-drop=ALL`, `no-new-privileges`, rootfs somente leitura, imagem fixada por digest) é boa, mas não elimina o risco. Registrar como pendência de endurecimento, **não bloqueia a promoção**: colocar um proxy do socket (por exemplo `tecnativa/docker-socket-proxy`, expondo só os endpoints de containers e logs em modo leitura) entre o Alloy e o Docker. Avaliar antes de ampliar o Alloy para outros containers (fase 2).

**3. Confirmado e registrado:** consumo de 0,14% de CPU e ~37 MiB; volume estimado de ~1,4 GB/mês para API e frontend contra 50 GB do plano Cloud Free (o "0 GB" da página de uso continua sem explicação).

## Evidência manual de HTTP do SSR (Claude, 2026-11-12) — complementa a validação da T4

O OpenClaw observou corretamente que o teste automatizado do limitador (7/7) cobre só a classe `SsrRenderLimiter`, e que **não há teste automatizado de HTTP** para `503` + `Retry-After` nem para HIT/coalescido. A verificação abaixo foi feita **manualmente, uma vez**, contra o servidor compilado (`npm run build:ssr` e `node dist/angular/server/main.js`), com `Host: www.sharebook.com.br`. Não é automatizada nem roda em CI: serve de evidência, não de cobertura permanente.

**Limite de concorrência** (`SSR_MAX_CONCURRENT_RENDERS=2`, `SSR_MAX_CONCURRENT_BOT_RENDERS=1`):

| cenário | resultado |
|---|---|
| 6 requisições humanas em paralelo em rota sem cache | 2 passaram (200); **4 receberam 503 em ~15 ms**, com `Retry-After: 5` e `Cache-Control: no-store` |
| 3 bots (`Googlebot/2.1`) em paralelo | 1 passou; **2 receberam 503** (teto de bot = 1) |
| 1 bot em andamento + 1 humano ao mesmo tempo | **ambos 200** (a vaga de bot não bloqueia humano) |
| log | uma linha `ssr_overloaded` por segundo no máximo, com `inFlight`, `peakInFlight`, `maxTotal`, `maxBots` e o último path, IP e User-Agent |

**Cache e renderização degradada** (build com `apiEndpoint` apontando para uma API falsa; o `environment.prod.ts` foi restaurado depois e nada disso foi commitado):

| cenário | resultado |
|---|---|
| API normal | `200`; 2ª requisição `X-SSR-Cache: HIT` (2,6 ms), `Cache-Control: public, max-age=1800` |
| só `Recommendations` demora 7 s | `200` em **4,4 s**, sem o bloco, `no-store`; a 2ª requisição também foi **MISS** (não cacheou) |
| API inteira demora 7 s | **503 em 4,5 s** com `Retry-After: 30`; a 2ª também 503 e MISS |
| API inalcançável (status 0) | `503` (antes era 404) com `Retry-After: 30` e `no-store`; o texto da página diz "Estamos com instabilidade" |

**Não coberto por essa verificação:** requisição **coalescida** (duas visitas simultâneas à mesma página fria compartilhando uma renderização); o código a trata antes de `renderSsr`, mas isso não foi demonstrado por HTTP. Para fechar o critério de forma permanente, abrir item para um **teste de fumaça HTTP automatizado** do `server.ts` (ver pendências sugeridas).

## Observação de Claude sobre o resultado parcial de `Recommendations` (2026-11-13)

A mediana caiu de 221,69 para 191,92 ms (p95 de 425,90 para 319,43 ms): ganho **modesto**. A estimativa inicial de "ordem de grandeza" valia para a **carga no banco** (o catálogo deixou de ser carregado a cada visita), e essa carga **não foi medida diretamente** (não há série histórica do Postgres). A latência quase não mudou porque o custo restante é **CPU na API**: em `BookRecommendationRanker.Rank`, cada cache miss ainda reconstrói os vetores tf-idf do catálogo inteiro (`BuildRawVector` e `BuildDocumentFrequency` sobre todos os candidatos). O cache por livro (10 min) só ajuda visitas repetidas; um crawler passando por livros diferentes ainda paga ~190 ms de CPU por livro. **Hipótese a confirmar** (não medida): sob rajada, o gargalo passa a ser CPU da API, e não conexões do banco. Registrado como item próprio, **ainda em discussão com o Raffa** (direção dele: pré-processar): `pre-processamento-paginas-e-recomendacoes.md`. Ideia inicial de Claude, **fora do escopo de fechamento deste item** e não decidida: guardar em cache os vetores já ponderados do catálogo e calcular por requisição só o vetor do livro de origem e as similaridades. Mexe na fórmula de idf (o corpus hoje inclui o livro de origem), então precisa preservar os resultados dos testes do ranker.

## Leitura de Claude do teste de carga de 2026-11-13 e rodada 4 (somente leitura)

**Hipóteses, nenhuma comprovada.** O resultado do teste (`a3e8966`) aponta para saturação do **servidor** (CPU e memória), mais do que do pool do banco:

1. O Postgres teve no máximo 2 conexões (1 ativa), mas a API deu timeout ao **abrir** conexão (`NpgsqlException: The operation has timed out` em `OpenNewConnector`, Timeout=5). Se o banco estava ocioso, quem ficou lento foi a API ou a máquina.
2. O **swap já estava em ~2,1 GB antes do teste** (RAM de 7,755 GiB): há pressão de memória em repouso.
3. A origem da carga foi a própria VPS, então gerador, SSR (renderização Angular, pesada em CPU), API e Postgres disputaram os mesmos recursos.
4. Os 503 com p50 de 4,3 s parecem ser **503 de degradação** (timeout de 4 s da API, `Retry-After: 30`), e não recusas do limitador (instantâneas, `Retry-After: 5`). O relatório soma os dois tipos.
5. Mesmo com 10 usuários, uma renderização fria levou ~3 s (p50). O limite de 30 renderizações protege o pool do banco, mas não necessariamente a CPU: o número certo pode ser bem menor e depende dos núcleos.

**Evidência a favor do Alloy:** o shipper Python registrou 13 dos 148 503; o Alloy registrou todos. Reforça a promoção no próximo deploy real do frontend.

### Tarefas do OpenClaw (rodada 4, somente leitura, SEM gerar carga)

Responder em "Respostas do OpenClaw (rodada 4)", com evidência e sem segredos. Não altere nada em produção e não repita o teste de carga.

**T7. Recursos do servidor.** Informar: número de vCPUs e modelo; RAM e swap total; `swappiness`; load average atual e dos últimos 15 min; uso de memória por container (`docker stats --no-stream`) e **quem está usando o swap** (por processo, por exemplo lendo `VmSwap` em `/proc/*/status`); tamanho do heap/RSS do `sharebook-frontend` agora (o cache SSR guarda até 1.000 páginas em memória); e se o container do OpenClaw ou o browser sidecar pesam na memória. Informar também se a memória do host já estava sob pressão em dias normais (histórico do Sentinel ou do Prometheus, se existir).

**T8. Separar os 503 do teste.** Com os logs já no Loki (stream `sharebook-frontend-alloy-test` e `sharebook-frontend`) e o que o gerador registrou, classificar os 148 503 em: (a) recusas do limitador (`Retry-After: 5`, rápidas) e (b) degradação (`Retry-After: 30`, ~4 s). Dar a contagem e o p50/p95 de cada tipo, e a soma de `rejectedSinceLastLog` dos `ssr_overloaded`. Dizer se o relatório anterior estava misturando os dois.

**T9. Custo de uma renderização fria, sozinha.** Sem carga: 5 requisições sequenciais a PDPs frias (slugs do sitemap, User-Agent `SharebookLoadTest/1.0`, 10 s entre elas) e a home com cache invalidada **só se o procedimento do playbook permitir sem risco**; medir tempo total de cada uma, CPU do `sharebook-frontend` e da API durante ela. Isso diz quanto custa uma renderização antes de qualquer sobrecarga.

**T10. Recomendar o limite.** Com T7 e T9, estimar um limite de renderizações simultâneas coerente com os núcleos e a memória, e dizer quanta folga sobra para a API e o Postgres na mesma máquina. Só recomendar; mudar o limite é decisão do Raffa.

**Se a causa for falta de recursos da VPS**, dizer isso claramente, com o número que mostra, para o Raffa decidir entre aumentar a máquina e reduzir o trabalho do SSR (pré-renderização, ver `pre-processamento-paginas-e-recomendacoes.md`).

### Respostas do OpenClaw (rodada 4)

#### T7 — recursos do servidor

Fotografia somente leitura da VPS às `2026-11-13T19:57Z` (relógio do host): **4 vCPUs** (`AMD EPYC 9J45 128-Core Processor`), **7,8 GiB** de RAM e **4,0 GiB** de swap. Havia 3,6 GiB de RAM usados, 3,5 GiB disponíveis, 2,2 GiB de swap usados, `vm.swappiness=10` e load average **0,91 / 0,65 / 0,87** (1/5/15 min). Não era um host saturado nesse instante, mas o swap já era alto antes do teste e continuou alto depois.

```bash
nproc; lscpu | grep -E 'Model name|CPU\(s\)|Thread|Core|Socket'
free -h; cat /proc/sys/vm/swappiness; uptime
docker stats --no-stream --format '{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}|{{.PIDs}}'
for f in /proc/[0-9]*/status; do ... awk '/^VmSwap:/{print $2}' "$f" ...; done
docker top sharebook-frontend -eo pid,ppid,comm,rss,vsz
grep -E '^(VmRSS|VmHWM|VmSize|VmSwap|RssAnon|RssFile):' /proc/<frontend-pid>/status
```

Snapshot de `docker stats --no-stream` (CPU/memória):

| container | CPU | memória |
|---|---:|---:|
| `sharebook-frontend` | 15,55% | **801,2 MiB** |
| `sharebook-api` | 10,78% | 274,7 MiB |
| `sharebook-frontend-alloy` | 0,22% | 42,3 MiB |
| `coolify` / `coolify-db` / `coolify-redis` / `coolify-sentinel` | 0,37% / 0,00% / 0,42% / 0,03% | 145,9 / 21,0 / 6,1 / 7,8 MiB |
| `openclaw-*` | 1,31% | **1,096 GiB** |
| `browser-*` | 1,40% | **80,1 MiB** |
| `coolify-proxy` | 0,10% | 112,7 MiB |
| `stalwart-*` / Postgres da aplicação / demais apps | 0,00–0,51% | 141,9 / 180,7 / 25,6–92,3 MiB |

O processo Node do frontend tinha RSS **802.696 kB** (783.152 kB anônimos), HWM 1.577.980 kB e `VmSwap` 12.140 kB; o cgroup reportou 801.947.648 bytes anônimos. Não forcei inspector nem sinal no processo: o **RSS é verificável**, mas heap V8 interno não é exposto com segurança nesta leitura. O RSS inclui o cache SSR de até 1.000 páginas.

Maiores `VmSwap`: `openclaw-gateway` 316.580 kB, `stalwart` 179.528 kB, `fwupd` 128.808 kB, `dockerd` 80.620 kB e o `dotnet` da API 78.448 kB; Chromium do browser sidecar soma dezenas de MiB (maior processo: 63.148 kB). A soma por processo foi 1.610.108 kB, menor que os 2,2 GiB de `free`, cuja contabilidade é global. OpenClaw **pesa materialmente**; o sidecar pesa menos, mas não é zero.

Histórico de RAM/swap: **não verificável**. Sentinel está `running` e faz push por minuto, mas os logs não expõem séries e não há tabela de métricas no `coolify-db`; o `.env` tem credenciais Prometheus, porém não uma URL de leitura Mimir/Prometheus configurada. O aviso isolado do Sentinel às 22:48Z (`failed to list container sizes: docker: Timeout error`) não é série de pressão.

#### T8 — separação dos 503 do teste autorizado

Usei Alloy, o stream completo: **148** `ssr_access` 503. O shipper Python reteve apenas 13 (todos lentos). A classificação usa duração no `ssr_access` e os caminhos exclusivos do `server.ts`: limitador emite `Retry-After: 5`; degradação por falha de API emite `Retry-After: 30`.

```logql
{service_name="sharebook-frontend-alloy-test"} |= "SharebookLoadTest" |= "ssr_access"
{service_name="sharebook-frontend-alloy-test"} |= "ssr_overloaded" |= "SharebookLoadTest"
{service_name="sharebook-frontend"} |= "SharebookLoadTest" |= "ssr_access"
```

| tipo | regra observada | contagem | p50 | p95 |
|---|---|---:|---:|---:|
| recusa do limitador | 503 em <300 ms; `Retry-After: 5` pelo caminho do código | **48** | **0,58 ms** | **1,16 ms** |
| degradação SSR | 503 em >=3 s; timeout da API, `Retry-After: 30` pelo caminho do código | **100** | **4.271,73 ms** | **5.085,59 ms** |
| total antes misturado | ambos | **148** | **4.200,22 ms** | **4.863,56 ms** |

Não houve intervalo intermediário: 48 ficaram entre 0,33 e 3,42 ms; 100 entre 4.094,07 e 5.620,71 ms. `ssr_access` não grava o header; o gerador registrou presença em 148/148, não o valor. Assim, 5 e 30 são inferências verificáveis pelos caminhos mutuamente exclusivos do código e pelas durações, não header inventado.

Foram 5 linhas `ssr_overloaded`, todas com `peakInFlight=30`, `inFlight=30`, `maxTotal=30`, `maxBots=18`, `lastIsBot=false`; soma de `rejectedSinceLastLog`: **34**. Ela fica abaixo das 48 recusas rápidas porque o log é limitado a uma emissão por segundo e pode deixar rejeições finais sem descarregar. Para contar recusas, usar `ssr_access` Alloy. **Sim: o relatório anterior misturava as duas classes.** O p95 cliente anterior (5.723 ms) ainda inclui Traefik/rede.

#### T9 — cinco renderizações frias, sem carga

Fiz exatamente **5 GETs** sequenciais, `User-Agent: SharebookLoadTest/1.0`, para PDPs do sitemap fora da faixa usada pelo gerador anterior, iniciando a cada 10 s. A origem foi o próprio OpenClaw na VPS pela URL pública; limitação registrada, mas sem rajada. O Alloy confirmou:

```logql
{service_name="sharebook-frontend-alloy-test"} |= "SharebookLoadTest/1.0" |= "ssr_access"
```

| início UTC | PDP | status/cache | duração no SSR |
|---|---|---|---:|
| 23:01:24 | `meu-amigo-robo` | 200 / MISS | 358,68 ms |
| 23:01:34 | `a-bruxa-de-salem` | 200 / MISS | 364,79 ms |
| 23:01:44 | `a-biblioteca-invisivel` | 200 / MISS | 452,36 ms |
| 23:01:54 | `tecnologia-de-informacao-o-uso-de-ti-pelas-em` | 200 / MISS | 359,37 ms |
| 23:02:04 | `pro-linq-language-integrated-query-in-c-2010` | 200 / MISS | 346,31 ms |

P50 **359,37 ms**, p95 **434,85 ms** no processo SSR. O temporizador ponta-a-ponta do cliente e a série de CPU por cgroup, iniciados junto da coleta, não foram preservados pelo runner; não os substituí por nova chamada porque o limite era estritamente cinco. Portanto **CPU por renderização e total externo não são verificáveis** nesta rodada; o snapshot T7 não foi usado como se fosse medição durante as chamadas.

Não invalidei a home: o playbook exige POST autenticado que remove cache em produção, incompatível com somente leitura. Logo, não há medição fria da home.

#### T10 — recomendação de limite (sem alteração)

**Recomendação provisória ao Raffa: `SSR_MAX_CONCURRENT_RENDERS=6` e `SSR_MAX_CONCURRENT_BOT_RENDERS=3`, não 30/18.** É redução defensiva, não capacidade provada: com 4 vCPUs, 30 permite até 7,5 renderizações frias em voo por vCPU; c=30 já produziu 100 degradações de ~4–5 s, 12 500/Npgsql e aumento de swap. Com 6/3, há no máximo seis SSRs e bots ocupam no máximo metade, deixando três vagas para humanos.

Reservar aproximadamente **2 vCPUs de responsividade** para API, Postgres, Traefik, kernel e serviços residentes. Não há cálculo honesto de MiB/CPU por renderização: T9 mostrou 346–452 ms isolados, mas não preservou CPU; o frontend já tem ~803 MB RSS, OpenClaw 1,096 GiB, browser 80 MiB e swap global 2,2 GiB.

A evidência aponta **contenção de recursos da VPS/API sob rajada**, não pool Postgres (máximo anterior de 2 conexões), mas não prova falta permanente de recursos: a fotografia atual tinha load 0,87 em 15 min e 3,5 GiB disponíveis. Antes de elevar o teto, usar origem externa e CPU/cgroup confiável; para reduzir o risco estrutural, decidir entre VPS maior e menos SSR via [pré-renderização](pre-processamento-paginas-e-recomendacoes.md). Nenhuma configuração, container ou deploy foi alterado.

### Respostas do OpenClaw (rodada 5)

#### Registro pré-alteração — limites SSR e promoção Alloy

Autorização explícita do Raffa para aplicar a recomendação T10. Antes de qualquer
mudança, frontend `c526152` e API `6d4f2cb` estavam `running` e `healthy`,
ambos com 0 restarts. `SSR_MAX_CONCURRENT_RENDERS` e
`SSR_MAX_CONCURRENT_BOT_RENDERS` não existiam no ambiente do container; os
padrões efetivos do código eram, portanto, **30** e **18**. A reversão já
registrada é remover as duas variáveis pelo model
`App\\Models\\EnvironmentVariable` do Coolify e redeployar o frontend.

```bash
docker inspect sharebook-frontend ...health...restarts...
docker inspect sharebook-api ...health...restarts...
docker inspect sharebook-frontend --format '{{range .Config.Env}}{{println .}}{{end}}' \
  | cut -d= -f1 | grep -E '^SSR_MAX_CONCURRENT_(RENDERS|BOT_RENDERS)$' || true
```

O monitor automático de promoção descrito na rodada 3 não está ativo: não há
unit systemd, crontab, script operacional nem cron OpenClaw correspondente.
Logo ele não poderia distinguir novo ID de container versus imagem nova. Este
redeploy será a promoção **manual** prevista pela revisão: após o container
novo ficar saudável, apagar posições de teste, trocar o rótulo do Alloy,
comparar a virada por minuto e só então desligar o shipper Python se não houver
buraco nem duplicata.

Estado imediatamente antes da promoção manual: shipper Python `active` e
`enabled`; Alloy `running`, 0 restarts, ainda em
`ALLOY_SERVICE_NAME=sharebook-frontend-alloy-test`; o diretório persistente de
posições é `/opt/sharebook-frontend-alloy/data`. Reversão da promoção, se a
comparação falhar: restaurar esse rótulo no arquivo protegido, reiniciar Alloy,
reativar/habilitar o shipper Python e parar Alloy se for necessário voltar ao
coletor único anterior. Nenhum segredo será lido ou registrado.

#### Aplicação — observação limpa interrompida pelo V2

Pelo model `App\\Models\\EnvironmentVariable` do Coolify, criei as duas
variáveis runtime e enfileirei o redeploy `jfdesnqetxksgusts4odb4vh` (finalizado).
O novo container `bcaf7da…`, mesma imagem `c526152`, iniciou às 23:19:06Z
`healthy`, 0 restarts; a API também permaneceu `healthy`. Confirmação no
container, sem listar outros envs: `SSR_MAX_CONCURRENT_RENDERS=6` e
`SSR_MAX_CONCURRENT_BOT_RENDERS=3`.

Como o monitor de promoção antigo não existia, fiz a promoção manual às
23:20:41Z: parei (sem remover) o shipper Python, parei Alloy, apaguei somente
`data/loki.source.docker.frontend/positions.yml`, troquei o rótulo de teste
por `sharebook-frontend` no arquivo 0600 e subi Alloy (`running`, 0 restarts).
A observação limpa de 30 min e a comparação de virada não foram concluídas:
o Raffa autorizou o V2 antes do seu término. Por isso o shipper continua
parado, mas não foi removido/desabilitado, e a reversão registrada continua
válida.

### Respostas do OpenClaw (rodada 6)

#### V2 — abortado no início da etapa humana c=3

O Raffa mandou iniciar antes de a observação limpa de 30 min da rodada 5
terminar; isso fica registrado como exceção à pré-condição original. A
pré-checagem às `2026-11-13T23:27:35Z` confirmou frontend/API `healthy`, 0
restarts, Alloy `running`, variáveis efetivas `SSR_MAX_CONCURRENT_RENDERS=6`
e `SSR_MAX_CONCURRENT_BOT_RENDERS=3`, home 200 em 56 ms e PDP 200 em 444 ms.
Antes do teste: RAM usada 3.130.380.288 bytes, swap usada
2.326.007.808 bytes e load 3,18 / 2,23 / 1,36. A origem era a própria VPS;
o gerador Go foi limitado a um CPU com `taskset -c 3` e prioridade `nice 19`.

O teste foi interrompido antes de fechar a primeira etapa: foram **23 GETs**
humanos c=3, todos HTTP 200. O monitor escreveu uma única amostra:

```text
frontend/API healthy, 0 restarts; CPU host 36,8%; swap 2.321.813.504 bytes;
pg_stat_activity 10 total / 0 active; frontend 88,88% CPU, API 44,77%.
vmstat si=4, so=0; 0 erros API.
```

O abort foi **técnico do monitor, não um gatilho comprovado do site**: sua
primeira versão parava em qualquer `si>0`, mas o critério autorizado exige
swap-in/out intenso por 10 s consecutivos. Logo, não há evidência de 500, 503,
Npgsql, crescimento de swap >300 MiB, healthcheck falho ou restart; tampouco
há dados para avaliar os critérios de carga. Por segurança e pela regra de
não insistir após parada, não reiniciei o teste. O arquivo de amostras está em
`codex-temp/ssr-v2-run/20261113T2334Z/` no runtime e não é versionado. As 27
PDPs frias somando a tentativa de aquecimento anterior não materializam o
efeito de encher cache SSR de até 1.000 páginas; não foi observada primeira
visita lenta posterior.

Comandos principais: `taskset -c 3 nice -n 19 ssr-v2-load`, monitor de 1 s
por SSH com `docker stats`, `free -b`, `/proc/loadavg`, `vmstat` e
`pg_stat_activity`. Nenhuma configuração, container ou deploy foi alterado
pelo V2. Os critérios "Log de recusas em produção" e "No próximo pico" foram
reavaliados pela retomada autorizada abaixo; o item não foi movido.

#### V2 retomado do zero — monitor corrigido e resultado

**Correção e teste seco.** A autorização posterior do Raffa substituiu o
abort técnico acima: o monitor só abortaria por atividade de swap se
`swap-in + swap-out > 1.000 KiB/s` por **10 amostras consecutivas** (além de
swap usada inicial +300 MiB). Troquei a leitura pontual de `vmstat` por
delta de `pswpin`/`pswpout` de `/proc/vmstat`; a coleta combinou isso, CPU e
memória de `docker stats`, `free -b`, `/proc/loadavg`, health/restarts e
`pg_stat_activity` em arquivo local. O teste seco de 60 s, com o site em
repouso, não disparou: 43 amostras úteis, swap-in máximo **6,4 KiB/s** e
swap-out máximo **0 KiB/s**. Portanto o `si=4` isolado da tentativa anterior
não voltou a produzir falso positivo.

Antes da carga: frontend/API `healthy`, ambos 0 restarts; Alloy `running`, 0
restarts; limites confirmados no container sem listar os demais envs:
`SSR_MAX_CONCURRENT_RENDERS=6` e `SSR_MAX_CONCURRENT_BOT_RENDERS=3`. Home
200 em 55 ms, PDP 200 em 664 ms; memória usada 3.445.518.336 bytes, swap
2.312.376.320 bytes e load 1,20 / 1,09 / 1,09. A origem continuou sendo a
própria VPS, pela URL pública, limitação registrada; o gerador Go usou
`nice -n 19 taskset -c 3`, GETs públicos de PDP/tag/categoria do sitemap e
taxa global máxima de 500 req/s (abaixo do teto de 2.000).

Comandos principais (sem segredos):

```bash
# 60 s de monitor em repouso e, depois, monitor durante a rodada
python3 codex-temp/ssr_v2_monitor_live.py monitor.csv stop 60
nice -n 19 taskset -c 3 codex-temp/ssr-v2-load requests.jsonl stop \
  https://www.sharebook.com.br/sitemap.xml

# Loki, após a janela
{service_name="sharebook-frontend-alloy-test"} |= "ssr_overloaded"
{service_name="sharebook-api"} |~ "(?i)(responded 500|NpgsqlException|connection to database|connection pool|canceling statement|timeout)"
```

O roteiro completou humano c=3/6/12/24, bot c=5/15/50, bot c=200 por 30 s e
iniciou a recuperação. O monitor então acionou **de verdade** às
`2026-11-14T00:02:53.868Z`: `si=1.091,1 KiB/s` e `so=5.541,1 KiB/s`, após 10
amostras consecutivas acima do limiar. A geração parou e não foi repetida. O
pico de swap usada foi 2.598.834.176 bytes, aumento de 286.720.000 bytes
(~273,4 MiB), portanto abaixo do gatilho independente de +300 MiB. CPU do
host chegou a 98,4%, mas não por 30 amostras consecutivas; Postgres chegou a
16 conexões totais/0 ativas; frontend/API permaneceram `healthy`, sem restart.
O arquivo preservado de amostras é
`codex-temp/ssr-v2-run/20261113T2350Z/monitor.csv` (767 linhas; não
versionado).

| etapa | HTTP 200 | 503, `Retry-After: 5` | p95 do 503 | observação |
|---|---:|---:|---:|---|
| humano c=3 | 212 | 0 | — | p95 200: 1.369,44 ms |
| humano c=6 | 174 | 0 | — | p95 200: 2.868,59 ms |
| humano c=12 | 3.418 | 13.240 | 16,91 ms | teto total exercitado |
| humano c=24 | 4.850 | 12.641 | 114,75 ms | teto total exercitado |
| bot c=5 | 4.955 | 10.494 | 4,68 ms | limite de bot exercitado |
| bot c=15 | 6.729 | 10.506 | 105,57 ms | probe humano separado |
| bot c=50 | 7.467 | 9.997 | 168,67 ms | probe/cache ativos |
| bot c=200 (30 s) | 4.131 | 5.886 | 202,55 ms | etapa extrema concluída |

Foram 95.115 respostas: **32.351 HTTP 200, 62.764 HTTP 503 e 0 outros/erros
de cliente**. Todos os 503 observados eram `Retry-After: 5`; não houve
`Retry-After: 30` (503 de degradação). Assim, a meta de p95 <300 ms das
recusas do limitador foi atendida inclusive na etapa c=200. A consulta Loki da
API retornou **0** linhas de HTTP 500, Npgsql, pool, conexão ou timeout; o
monitor também viu 0 em cada amostra. Isto contrasta com o teste anterior:
148 503 (100 por degradação), 12 HTTP 500 e p95 de Slug/Recommendations de
7,06 s/21,5 s. O p95 exato dessas duas rotas nesta V2 não é verificável: a
consulta LogQL de `quantile_over_time` atingiu o limite de 500 séries; não
substituí isso por uma estimativa.

As 77 sondas humanas durante bot c=5/15/50/200 foram **77 HTTP 200**, p95
**1.720,92 ms**, portanto abaixo de 5 s e evidência da reserva de vaga. A PDP
de cache teve 1 MISS inicial de 1.859,76 ms e, depois, 324 HITs 200: p50
27,12 ms, p95 203,88 ms e p99 416,38 ms. Foram 2.398 URLs únicas e 30.798
respostas HIT: o teste aqueceu/preencheu significativamente o cache SSR, mas
não há uma invalidação nem uma primeira visita pós-teste comparável para
afirmar que ela ficou mais lenta. Na recuperação, os primeiros 60 s tiveram
12/12 HTTP 200, p95 524,02 ms e máximo 608,08 ms; sem restart. O restante dos
3 min foi interrompido pelo gatilho real de swap.

O Alloy recebeu os eventos no label ainda **`sharebook-frontend-alloy-test`**:
264 linhas `ssr_overloaded`, soma `rejectedSinceLastLog=62.537` e todos os
`peakInFlight=6`. A diferença de 227 contra as 62.764 recusas do gerador é
esperada do rate-limit/agregação do log. O seletor
`service_name="sharebook-frontend"` não retornou as linhas desta janela, apesar
da promoção manual registrada na rodada 5; não alterei configuração durante o
teste. Isso revela uma pendência de rótulo/virada a corrigir fora desta rodada.

**Critérios V2:** recusa rápida atendida; degradação 503/30 atendida (0);
zero 500/Npgsql e Postgres <80 atendido (0 e máximo 16); reserva humana
atendida; HIT em milissegundos atendido; `ssr_overloaded` no teto 6 atendido;
recuperação no primeiro minuto atendida, porém a observação completa foi
interrompida pelo gatilho real de swap. O item continua em `backlog/todo` e
não foi movido para `done`.

### Respostas do OpenClaw (rodada 7)

#### Correção final do Alloy e validação da virada

Às `2026-11-14T00:42:29Z`, `docker inspect` (somente a variável solicitada)
mostrou `ALLOY_SERVICE_NAME=sharebook-frontend-alloy-test`. O arquivo 0600 já
continha `sharebook-frontend`: `docker restart` não relê `--env-file` de
container existente. Antes da mudança, Alloy estava `running`, 0 restarts,
imagem pinada em `grafana/alloy@sha256:9acc2529bc1edb7f5b2bd801dd8334ebc80c158e3a9e5526ecd7c9a273d43189`,
rootfs read-only, `cap-drop=ALL`, `no-new-privileges`, tmpfs restrito,
`restart=unless-stopped`, socket Docker e posições em
`/opt/sharebook-frontend-alloy/data`.

Recriei somente o container com a mesma imagem/opções, preservando as posições.
O anterior foi parado e renomeado como rollback imediato; o novo subiu
`running`, 0 restarts, com `ALLOY_SERVICE_NAME=sharebook-frontend`. O rótulo de
produção ficou sem dados de `2026-11-13T23:20:41Z` a `2026-11-14T00:42:29Z`:
**1 h 21 min 48 s**. Até a correção os dados chegaram no rótulo de teste;
depois, LogQL confirmou novos `ssr_access` em produção:

```logql
{service_name="sharebook-frontend"} |= "ssr_access"
```

Comparei `docker logs --timestamps` do frontend e Loki por minuto na janela
`00:42:29Z`–`00:52:29Z`, filtrando `event="ssr_access"`:

| minuto UTC | Docker | Loki |
|---|---:|---:|
| 00:42 | 2 | 2 |
| 00:43 | 1 | 1 |
| 00:44 | 3 | 3 |
| 00:45 | 10 | 10 |
| 00:46 | 3 | 3 |
| 00:47 | 3 | 3 |
| 00:48 | 13 | 13 |
| 00:49 | 1 | 1 |
| 00:50 | 6 | 6 |
| 00:51 | 4 | 4 |
| 00:52 | 2 | 2 |
| **total** | **48** | **48** |

Não houve buraco nem duplicata. A configuração secret-free versionada é
`playbooks/engineering/analytics/assets/alloy-frontend.alloy`; credenciais e
rótulo ficam exclusivamente no arquivo remoto 0600.

#### Observação limpa e retirada do shipper

Na janela de 30 min após a correção (`00:42:29Z`–`01:12:29Z`), frontend, API e
Alloy ficaram saudáveis/running, todos com 0 restarts. LogQL não retornou HTTP
500, Npgsql/pool/conexão/timeout, `ssr_access` 503 ou `ssr_overloaded`. Snapshot
final: frontend **325,4 MiB**, API **297,1 MiB**, Alloy **221,1 MiB**; swap caiu
de **2.473.988.096** para **2.428.637.184 bytes**. A amostra final de 6 s teve
4 KiB de swap-in e 5 KiB de swap-out no total (máximos 4/5 KiB/s). Não existe
série histórica de swap para afirmar cada segundo da janela: esse limite fica
explícito, sem inventar ausência de I/O.

Como virada e observação passaram, removi o shipper provisório: `systemctl
disable --now`, unit e diretório 0600 confirmados ausentes. O script
versionado `playbooks/engineering/analytics/scripts/ship_docker_logs_to_otlp.py`
também foi removido. Reversão: restaurar script/unit do Git, recriar o arquivo
0600 a partir do `.env` canônico, `daemon-reload` e `enable --now`; se preciso,
parar Alloy e restaurar o rótulo de teste. O monitor de promoção da rodada 3
**não existe**: não há unit, cron, script ou job OpenClaw ativo.

#### Fechamento

O incidente de 2026-11-12 teve 94 HTTP 500 e 127 erros EF/pool por SSR
on-demand sob rajada. Entraram timeout SSR/API, cache de recomendações,
timeouts Npgsql, limite SSR e logs persistentes Alloy. No teste 30/18 houve
148 respostas 503 (100 por degradação), 12 HTTP 500/Npgsql e latência severa.
No V2 6/3: 62.764 recusas com `Retry-After: 5` (pior p95 **202,55 ms**), zero
503/30, zero 500/Npgsql, Postgres máximo 16 conexões e 77/77 probes humanos
200 (p95 **1,721 s**). Limitações: o V2 saiu da própria VPS e, ao fim, houve
10 s de swap I/O acima de 1 MiB/s (última amostra 1.091,1/5.541,1 KiB/s).
Essas lacunas e os follow-ups restantes viraram itens próprios; este item é
movido para `done`.

```bash
docker inspect sharebook-frontend-alloy  # variável/estado, sem outros envs
docker logs --timestamps --since ... --until ... sharebook-frontend
systemctl disable --now sharebook-frontend-log-shipper.service
docker stats --no-stream sharebook-frontend sharebook-api sharebook-frontend-alloy
free -b; vmstat 1 6
```

```logql
{service_name="sharebook-frontend"} |= "ssr_access"
{service_name="sharebook-frontend"} |= "ssr_overloaded"
{service_name="sharebook-api"} |~ "(?i)(responded 500|NpgsqlException|connection to database|connection pool|canceling statement|timeout)"
```
