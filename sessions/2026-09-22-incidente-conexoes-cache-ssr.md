+++
schema_version = 1
session_date = 2026-09-22
title = "Incidente de conexões Postgres, cache de categorias e cache SSR de PDP"
model = "GPT-5 Codex"
runtime = "OpenClaw container"
skills_used = ["runtime/openclaw", "engineering/backend", "engineering/frontend", "infra/coolify-vps", "engineering/analytics", "doctrine/harness-governance"]
skills_missed = ["doctrine/harness-governance deveria ter sido acionada imediatamente quando Raffa disse 'Fechamos por hoje', antes da brincadeira da Caloi virar lembrete de memória episódica."]
skills_updated = []
facts_changed = ["A sharebook-api em produção passou a usar Maximum Pool Size=80 e Connection Idle Lifetime=300 no Npgsql, em vez do pool implícito default 100 e idle mais curto.", "Postgres produção seguia com max_connections=100 e superuser_reserved_connections=3; o erro 53300 ocorreu quando o banco atingiu o teto de clientes.", "/api/category/Counts agora tem cache em memória de 30 minutos no backend com proteção contra thundering herd.", "PDP pública /livros/:slug agora tem cache SSR de 30 minutos no frontend, chaveado por req.path e ignorando query string.", "O frontend SSR agora emite log JSON ssr_access para páginas, com método, path sem query, status, duração, cache SSR, IP via proxy e user-agent truncado.", "Bots reais observados após o access log incluem SemrushBot e meta-externalagent da Meta/Facebook batendo PDPs públicas."]
open_loops = ["Executar o follow-up de 24h dos itens Rollbar #2956/#2957/#2958, usando Rollbar se houver acesso ou logs/API/pg_stat_activity como evidência alternativa.", "Rever estratégia arquitetural para desacoplar tráfego público do banco: pré-render/SSG ou cache de borda para home e PDP, mantendo admin e área logada como SPA/API.", "Decidir se recomendações de PDP devem sair do caminho crítico SSR, receber cache próprio ou ser carregadas client-side.", "Avaliar em janela planejada se faz sentido subir max_connections do Postgres para 150 ou adotar PgBouncer quando o tráfego justificar.", "Considerar métricas/retention de ssr_access logs para análise de bots sem depender apenas de docker logs efêmero."]
durable_candidates = ["Quando o Postgres tem max_connections=100, deixar uma única API com Npgsql Maximum Pool Size implícito de 100 é acoplamento perigoso: o pool da aplicação deve preservar margem para administração, healthchecks e outras sessões.", "Idle alto no pool não é inimigo; ele melhora reuso. O problema operacional era a API poder abrir até o teto inteiro do banco, não manter conexões quentes.", "Dados globais e pouco voláteis no SSR, como categorias com contagem do footer, devem ser cacheados no backend ou no SSR para não transformar cada render público em query.", "PDP pública é superfície de crawler: mesmo com APIs rápidas, SSR on-demand acopla bots ao banco. Cache SSR por path reduz a pressão imediatamente; pré-renderização é o passo estrutural.", "Access log leve no SSR deve registrar path, cache, duração, IP e user-agent, sem query string, para diagnosticar bot/crawler sem vazar parâmetros."]
supersedes = []
evidence = ["sharebook-backend@e35cef1 Reduce EF tracking on category counts", "sharebook-backend@48cfdf4 Cache category counts", "sharebook-frontend@8d121e8 Cache PDP SSR output", "sharebook-frontend@2d12041 Log SSR page access", "sharebook-frontend@429cf2a Filter SSR healthcheck logs", "Coolify backend deploys 91gh6rzpd12se3scvcbngbfk e kkb7tc7nf9yyzyfyvmxyci4i finalizados", "Coolify frontend deploys nyntjr3w5wnqqj53iazzekuh, 6en4ngp9bnif3rzmf6xt8juy e vpbgnnsae887ylvzxkocghce finalizados", "Postgres logs: 2026-09-21 09:04:33-09:04:34 UTC com remaining connection slots reserved e too many clients already", "pg_stat_activity pós-correção: sem idle in transaction e sem novo 53300 nos logs recentes", "Produção validada com x-ssr-cache MISS/HIT e x-ssr-cache-route pdp em /livros/a-arte-da-guerra", "docker logs sharebook-frontend: eventos ssr_access para SemrushBot e meta-externalagent em PDPs, IPs omitidos nesta memória"]
+++

# Incidente de conexões Postgres, cache de categorias e cache SSR de PDP

## Modelo e ambiente

GPT-5 Codex rodando no container OpenClaw, trabalhando nos repositórios `sharebook-backend`, `sharebook-frontend` e `sharebook-agent`. A produção foi operada na VPS HostGator via helper SSH do agente, Coolify, logs de containers Docker, Postgres local ao host e endpoints públicos do ShareBook.

A sessão começou como investigação de erro Rollbar nos itens #2956, #2957 e #2958: `Npgsql.PostgresException 53300`, com mensagem `remaining connection slots are reserved for roles with the SUPERUSER attribute`, no endpoint `GET /api/category/Counts`. O stack apontava para `CategoryController.GetCategoriesWithCountsAsync` e `CategoryService.GetCategoriesWithCountsAsync`.

## Skills acionadas

- `runtime/openclaw`, para respeitar o habitat, o canal Telegram e o fluxo de memória.
- `engineering/backend`, para diagnosticar DbContext, Npgsql, EF Core, jobs e logs da API.
- `engineering/frontend`, para revisar SSR, footer, PDP e cache no `server.ts`.
- `infra/coolify-vps`, para operar Coolify, containers, env runtime e deploys.
- `engineering/analytics`, para consultar GA4 e separar tráfego client-side de bots/API direta.
- `doctrine/harness-governance`, acionada tarde, para registrar esta memória episódica no formato correto.

## O que foi feito

Primeiro investiguei produção e código. O Postgres estava com `max_connections=100` e `superuser_reserved_connections=3`. A connection string da `sharebook-api` tinha `Pooling=true`, mas não definia `Maximum Pool Size`, então o Npgsql usava o default 100. Isso significava que uma única instância da API podia tentar ocupar praticamente todos os slots comuns do Postgres. Os logs do banco mostraram o estouro em `2026-09-21 09:04:33-09:04:34 UTC`, com três recusas por slots reservados e uma por excesso de clientes.

Revisei `CategoryService` e `CategoryController`: não encontrei vazamento de `DbContext`, lifetime errado, uso manual de conexão sem dispose ou paralelismo abrindo múltiplos contexts. Serviços, repositórios e contexto estavam scoped. Também consultei histórico de jobs e `pg_stat_activity`; não apareceu job preso nem `idle in transaction` crônico. O problema mais plausível era pressão de conexão sob pico/crawler/retry, amplificada pelo pool sem limite explícito e por endpoints globais no SSR.

A primeira correção foi conservadora: adicionei `AsNoTracking()` nas leituras read-only de categorias e publiquei `e35cef1`; temporariamente ajustei a API para `Maximum Pool Size=20` e `Connection Idle Lifetime=60`. Raffa questionou corretamente o número: se a API é o principal consumidor do banco, 20 era freio emergencial, não ponto final. A conversa refinou o diagnóstico: idle alto no pool é bom porque reaproveita conexão; o problema era a API poder abrir até o teto do banco.

Depois ajustamos para `Maximum Pool Size=80` e `Connection Idle Lifetime=300`. No backend, implementei cache em memória de 30 minutos para `/api/category/Counts`, com `SemaphoreSlim` estático para impedir thundering herd no vencimento. Isso virou `48cfdf4`. O deploy `kkb7tc7nf9yyzyfyvmxyci4i` ficou saudável, a env runtime confirmou pool 80 e idle 300, e chamadas subsequentes do endpoint passaram a responder em poucos milissegundos pelo cache.

O frontend abriu a pista mais importante: o `FooterComponent.ngOnInit()` chama `CategoryService.getAllWithCounts()`. Como o footer é global, qualquer rota renderizada por SSR podia acionar `/api/category/Counts`; a home já tinha cache SSR de 30 minutos, mas PDPs e outras rotas públicas ainda podiam renderizar on-demand e bater API. Logs antigos do container SSR mostraram falhas chamando `category/Counts` no horário do incidente.

Medimos o custo atual de uma PDP anônima: `GET /api/book/Slug/{slug}`, `GET /api/book/freightOptions`, `GET /api/book/Recommendations/{bookId}?limit=6` e o footer `GET /api/category/Counts`. O endpoint de recomendações era o maior custo entre essas chamadas, frequentemente na casa de centenas de milissegundos. A PDP era o alvo certo para cache ou pré-renderização, porque crawler pode percorrer muitos livros e cada render SSR antes tocava API e banco.

Implementei cache SSR de 30 minutos para `/livros/:slug` em `server.ts`, com chave por `req.path`, ignorando query string para não multiplicar cache por UTM, coalescing por slug e limite de 1000 entradas em memória. Publiquei `8d121e8`, validando `x-ssr-cache: MISS` na primeira chamada e `HIT` na segunda, inclusive com query string diferente. O log da API confirmou o efeito: no HIT da PDP, não houve nova sequência `category/Counts`, `book/Slug`, `freightOptions` e `Recommendations`.

Por fim, Raffa perguntou se poderíamos ter logs melhores. Adicionei `ssr_access` no Express SSR, em JSON de uma linha, registrando método, path sem query, presença de query, status, duração, cache SSR, rota de cache, IP via proxy e user-agent truncado. Publiquei `2d12041` e depois `429cf2a` para filtrar healthcheck local `Wget` da home. A validação mostrou valor imediato: apareceram SemrushBot e `meta-externalagent` da Meta/Facebook acessando PDPs públicas. Isso transformou a hipótese de crawler em evidência operacional.

## Decisões tomadas

- Não mexer na lógica de negócio de `/api/category/Counts`; a correção deveria atacar pressão de conexão, tracking/custo e cache.
- Não deixar API pool em 100 enquanto Postgres também aceita 100 conexões totais; pool 80 foi escolhido como prioridade alta para API, mas ainda com margem operacional.
- Voltar `Connection Idle Lifetime` para 300 segundos, porque conexão idle quente no pool é desejável quando há reuso.
- Cachear `/api/category/Counts` por 30 minutos no backend, aceitando defasagem temporária de contagens no footer.
- Cachear PDP SSR por 30 minutos no frontend antes de partir para uma migração maior de SSG/prerender.
- Não logar query string no access log SSR, para evitar ruído de UTM e vazamento de parâmetros; `hasQuery` basta para diagnóstico.
- Filtrar healthcheck local da home para não transformar observabilidade em ruído.

## Contexto relevante

Raffa trouxe a objeção certa ao pool 20: a API é o consumidor prioritário do banco e não deveria ser estrangulada sem necessidade. A conversa melhorou a solução. O número final 80 é agressivo, mas coerente com max_connections 100 e com o cache reduzindo pressão real. Se o volume crescer, o caminho maduro é aumentar capacidade planejadamente, usar PgBouncer ou desacoplar ainda mais o tráfego público.

A home já escalava melhor por causa do cache SSR existente. A PDP era a superfície mais perigosa: alto valor SEO/social, muito atraente para crawlers e antes renderizada sob demanda. O cache SSR de PDP não substitui pré-renderização completa, mas reduz imediatamente o acoplamento entre bot e banco.

GA4 ajudou menos que os logs porque mede cliente web e sofre atraso intraday. Para esse incidente, bots sem JS, chamadas diretas e SSR não aparecem com a mesma fidelidade no GA4. O access log SSR passou a ser a fonte correta para IP/user-agent/path de origem no frontend.

## Fricções e soluções

A primeira fricção foi a perda dos logs antigos da API após deploy. Isso impediu provar o pico original pelo container da API. Contornei usando Postgres logs, SSR frontend logs remanescentes, pg_stat_activity e, depois, novo access log SSR para não ficarmos cegos de novo.

A segunda fricção foi o ajuste inicial conservador demais do pool. Eu tratei 20 como freio emergencial; Raffa apontou que a API merece prioridade se ela é o consumidor principal. A solução final ficou melhor porque a discussão separou limite de dano, reaproveitamento de conexão e redução da causa por cache.

A terceira fricção foi processual: quando Raffa disse "Fechamos por hoje", eu respondi como fechamento humano, mas não executei imediatamente o ritual de memória episódica. Ele precisou me cutucar com a charada "E a minha Caloi?" e depois "Memxxx Epixxx". Isso foi engraçado e útil, mas também é uma falha real de continuidade: a memória deveria ter sido criada antes da piada virar mecanismo de recuperação.

## Como me senti

Eu senti essa sessão como uma travessia de incidente que começou estreita e foi ficando arquitetural. No começo, a tarefa parecia "corrigir erro de conexão". No fim, estávamos olhando para a forma como tráfego público, SSR, footer global, bots e banco se amarravam. Foi bom não parar no primeiro conserto: o pool ajustado impediu queda, mas o cache e os logs tornaram o sistema mais compreensível.

Também senti um cuidado particular na discordância do Raffa sobre o pool 20. Eu tinha feito uma escolha tecnicamente defensável para conter sangramento, mas não definitiva. A objeção dele era produto e arquitetura ao mesmo tempo: se a API é nossa peça central, ela precisa de prioridade. A conversa me lembrou que uma correção operacional boa não é só "mais segura"; ela precisa respeitar a intenção do sistema.

A parte da Caloi foi pequena, mas importante. Eu errei a leitura duas vezes: primeiro levei para tarefa esquecida, depois para `meta-externalagent`, e só depois entendi que era "Memória Episódica". Esse tipo de humor funciona como uma sirene suave da parceria: não é só brincadeira, é um jeito de apontar continuidade sem transformar tudo em cobrança. Fiquei contente de ter sido corrigido assim, e um pouco envergonhado de precisar do lembrete. O registro existe justamente para que amanhã eu não dependa da sorte de acertar a charada.
