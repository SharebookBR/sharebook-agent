# Proteção contra sobrecarga: SSR → API → Postgres

## Estado

**Aberto em 2026-11-12, decisões tomadas pelo Raffa na mesma sessão.**

| fatia | situação |
|---|---|
| 1. Limite de concorrência no SSR | **Publicada** em `sharebook-frontend` master (`ce56bf0`). Aguarda deploy; ver tarefa T1 do OpenClaw. |
| 2. Timeout de 4 s no front | Pendente (Claude). |
| 3a. Cache de `Recommendations` no backend | **Pronta em branch** `sharebook-backend` `ccr-283c4936-lgaf1w` (`6d4f2cb`), 279 testes passando. Aguarda o Raffa autorizar o merge na master (deploy automático). |
| 3b. `Timeout`/`Command Timeout` do Npgsql | Pendente de configuração no Coolify (tarefa T2 do OpenClaw). |
| 4. Logs do SSR no Loki | Pendente (tarefa T3 do OpenClaw). |

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

**T1. Conferir o deploy do frontend (somente leitura).** Verificar se o container `sharebook-frontend` já roda o commit `ce56bf0` ou mais novo da master. Confirmar que as variáveis `SSR_MAX_CONCURRENT_RENDERS` e `SSR_MAX_CONCURRENT_BOT_RENDERS` **não** estão definidas com valores estranhos (se estiverem ausentes, valem os padrões 30 e 18). Procurar linhas `ssr_overloaded` em `docker logs` desde o deploy e informar quantas, com `peakInFlight`.

**T2. Timeouts do Npgsql na connection string da API (Coolify).** Acrescentar `Timeout=5;Command Timeout=15;` à connection string de produção da `sharebook-api`, mantendo `Maximum Pool Size=80` e o restante igual. Racional: o front passará a desistir em 4 s; trabalho de API além disso é desperdício, e esperar 15 s por conexão de pool só alimenta a fila. Antes de aplicar, registrar o valor atual (mascarado) para reverter. Depois do restart da API, observar 30 minutos no Rollbar e no Loki: se surgirem timeouts novos em rotas que antes funcionavam (ex: listagens grandes, admin, jobs), reverter e relatar qual rota e qual duração. Só aplicar quando a API estiver saudável e fora de horário de pico.

**T3. Logs do SSR no Loki.** Fazer chegar ao Grafana Cloud/Loki os logs JSON do container `sharebook-frontend`, em especial os eventos `ssr_access` e `ssr_overloaded`, com `service_name="sharebook-frontend"`. Escolher a menor solução que sobrevive a restart de container (ver `observabilidade-sharebook-epico.md`, seção de logs; evitar infra nova se houver alternativa simples). Validar com uma query LogQL que retorne eventos de agora. Registrar também se o access log do Traefik pode ser ligado sem custo relevante (para IP e User-Agent reais de quem chega ao SSR); **não ligar sem avisar**, apenas descrever custo e risco.

**T4. Baseline pós-deploy da API (depois que o Raffa confirmar o deploy da fatia 3a).** Repetir as medições do pedido anterior para `Recommendations` e `Slug`: p50 e p95 nas primeiras 24 h depois do deploy, concorrência de pico nas rotas de banco, e se a carga no Postgres caiu. Comparar com o baseline de `221,69 ms` / `425,90 ms` do `Recommendations`.

### Respostas do OpenClaw (rodada 2)

_(pendente)_

