# Proteção contra sobrecarga: SSR → API → Postgres

## Estado

**Aberto em 2026-11-12, decisões tomadas pelo Raffa na mesma sessão.**

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
- `pre-renderizacao-paginas-publicas.md`: solução estrutural; este item é a rede de proteção enquanto ela não existe.

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

A mediana caiu de 221,69 para 191,92 ms (p95 de 425,90 para 319,43 ms): ganho **modesto**. A estimativa inicial de "ordem de grandeza" valia para a **carga no banco** (o catálogo deixou de ser carregado a cada visita), e essa carga **não foi medida diretamente** (não há série histórica do Postgres). A latência quase não mudou porque o custo restante é **CPU na API**: em `BookRecommendationRanker.Rank`, cada cache miss ainda reconstrói os vetores tf-idf do catálogo inteiro (`BuildRawVector` e `BuildDocumentFrequency` sobre todos os candidatos). O cache por livro (10 min) só ajuda visitas repetidas; um crawler passando por livros diferentes ainda paga ~190 ms de CPU por livro. **Hipótese a confirmar** (não medida): sob rajada, o gargalo passa a ser CPU da API, e não conexões do banco. Melhoria possível, **fora do escopo de fechamento deste item**: guardar em cache os vetores já ponderados do catálogo e calcular por requisição só o vetor do livro de origem e as similaridades. Mexe na fórmula de idf (o corpus hoje inclui o livro de origem), então precisa preservar os resultados dos testes do ranker.

