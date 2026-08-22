+++
schema_version = 1
session_date = 2026-08-22
title = "Cache integral da home após incidente de conexões"
model = "GPT-5"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "engineering/backend", "engineering/frontend", "infra/coolify-vps", "browser:control-in-app-browser", "doctrine/harness-governance"]
skills_missed = []
skills_updated = ["engineering/frontend"]
facts_changed = ["A rota exata / voltou a ter cache do HTML SSR completo por 30 minutos.", "O container sharebook-frontend em produção passou a executar o commit 2ba162cc3f0b202809316dd4e7e67e8fb660aace.", "Depois do aquecimento do cache, o healthcheck da home deixou de repetir as chamadas às APIs de dados."]
open_loops = ["Avaliar futuramente a troca do healthcheck da raiz por um endpoint leve dedicado; ficou fora do escopo desta sessão por decisão do Raffa."]
durable_candidates = ["Healthchecks não devem usar uma rota SSR cara quando existe ou puder existir um endpoint leve dedicado."]
supersedes = []
evidence = ["sharebook-frontend/server.ts", "sharebook-agent/skills/engineering/frontend.md", "sharebook-frontend@2ba162cc3f0b202809316dd4e7e67e8fb660aace", "sharebook-agent@97cd3d5", "Coolify deployment mumflpx7jtnfejgxbmpmpj4d", "Produção: X-SSR-Cache=HIT e Cache-Control=public,max-age=1800", "Logs de sharebook-api entre 2026-08-22T15:24:06Z e 2026-08-22T15:28:40Z: zero chamadas aos endpoints de dados da home"]
+++

# Cache integral da home após incidente de conexões

## Modelo e ambiente

Sessão executada com GPT-5 no runtime `windows-local`, trabalhando nos repositórios `sharebook-frontend` e `sharebook-agent`. A aplicação é publicada pelo Coolify na VPS HostGator.

## Skills acionadas

Foram consultadas as skills de runtime Windows, backend, frontend, infraestrutura/Coolify, controle do navegador e governança do harness. A skill `engineering/frontend` foi atualizada com o contrato durável do cache integral da home e suas validações mínimas.

## O que foi feito

Os e-mails do Rollbar de 22/08/2026 foram inspecionados. Houve nove alertas concentrados às 00:17:43, derivados de quatro respostas HTTP 500. A exceção raiz era `Npgsql.PostgresException 53300: remaining connection slots are reserved for roles with SUPERUSER`, afetando endpoints consumidos pela home e duas rotas de livros por slug.

A investigação encontrou uma amplificação importante: o healthcheck do container frontend acessava `/` a cada cinco segundos. Como a home é SSR e o cache integral havia desaparecido da linha atual de desenvolvimento, cada verificação renderizava a página novamente e disparava aproximadamente quatorze chamadas ao backend. O cache de 30 minutos existira nos commits `15738dd` e `e81ea7a`, preservados em `origin/ssr`, mas fora perdido quando o SSR v2 recriou `server.ts` no commit `86891b1`. O `TransferState` existente evitava duplicação entre SSR e hidratação de um único acesso, mas não reutilizava o HTML entre requisições.

Foi implementado em `sharebook-frontend/server.ts` um cache em memória do HTML SSR completo para a rota exata `/`, com TTL de trinta minutos. O primeiro acesso faz `MISS`; acessos simultâneos aguardam a mesma Promise e recebem `COALESCED`; os seguintes recebem `HIT` sem executar o render Angular. Somente respostas 200 entram no cache, e falhas recebem `no-store`. Os headers observáveis são `X-SSR-Cache` e `Cache-Control: public, max-age=1800`.

O build SSR passou. Uma rajada local de doze acessos simultâneos produziu exatamente um `MISS` e onze `COALESCED`, com respostas idênticas; o acesso posterior foi `HIT`. A validação headless do `HIT` registrou zero chamadas a `https://api.sharebook.com.br/api/*` durante a hidratação. Imagens estáticas em `/Images/*` continuam sendo carregadas normalmente e não representam consultas de dados ao Postgres.

A mudança foi commitada e enviada como `sharebook-frontend@2ba162cc3f0b202809316dd4e7e67e8fb660aace`. Como o webhook automático não iniciou o deploy, a publicação foi enfileirada diretamente pelo mecanismo interno do Coolify, deployment `mumflpx7jtnfejgxbmpmpj4d`. O deploy terminou com sucesso e o container ficou saudável executando exatamente essa imagem.

Em produção, duas requisições públicas retornaram HTTP 200, `X-SSR-Cache: HIT`, `Cache-Control: public, max-age=1800` e o mesmo HTML de 298.270 bytes. Após o aquecimento registrado às 12:24:05, os logs do backend mostraram zero chamadas aos endpoints de dados da home entre 12:24:06 e 12:28:40, apesar do healthcheck continuar acessando a raiz a cada cinco segundos.

## Decisões tomadas

O escopo foi deliberadamente limitado à home, conforme pedido do Raffa. Não foi criada uma rota `/health` e o healthcheck não foi alterado nesta sessão.

O cache cobre o HTML inteiro, em vez de serviços ou blocos isolados. Isso atende ao requisito de não consultar novamente as APIs de dados durante trinta minutos e mantém o `TransferState` dentro do HTML, impedindo que a hidratação refaça essas consultas no navegador.

Foi adotado single-flight para evitar que uma expiração sob concorrência gere múltiplos renders e uma nova rajada contra o banco. O cache é local ao processo frontend; um novo container começa vazio e faz um único aquecimento.

O contrato foi promovido para `skills/engineering/frontend.md`, junto com a validação obrigatória de build SSR, concorrência, `HIT` e ausência de chamadas a `/api/*` na hidratação.

## Contexto relevante

O Postgres permite cem conexões e estava com uso baixo durante a investigação. Os únicos quatro registros de falta de slots ocorreram no mesmo segundo do incidente e não se repetiram depois. Portanto, não houve alteração emergencial de `max_connections`; o trabalho atacou a fonte de carga evitável identificada na home.

Os nove itens do Rollbar não correspondiam a nove falhas independentes. Eram múltiplos contextos de logging derivados de quatro respostas 500. Os endpoints públicos voltaram a responder 200 antes da correção, indicando um pico transitório de conexões.

O significado operacional de “zero chamadas ao backend” nesta decisão é zero chamadas às APIs de dados durante o `HIT`, tanto no SSR quanto na hidratação. Recursos estáticos, especialmente capas em `/Images/*`, continuam sendo requisitados e não fazem parte do cache HTML.

## Fricções e soluções

O webhook de deploy automático não reagiu ao push. A produção permaneceu no commit antigo, então o deploy foi enfileirado pelo mecanismo interno do Coolify com o SHA explícito e validado tanto na fila quanto na imagem do container.

A interface web do Coolify exigia autenticação e não havia sessão reaproveitável. Em vez de pedir senha ou armazenar credencial fora do `.env`, foi usado o acesso SSH canônico documentado pela skill de infraestrutura e as interfaces internas já presentes no servidor.

A primeira tentativa de validar o navegador com uma importação direta do Puppeteer não era compatível com o ambiente controlado. A validação foi refeita pela superfície oficial do navegador e cruzada com os logs do container backend, que forneceram a evidência decisiva de ausência de repetição após o aquecimento.

## Como me senti

Eu me senti atento ao perceber que o erro visível no Rollbar era apenas a ponta do problema. A concentração de todas as falhas no mesmo segundo poderia levar a um ajuste apressado no banco, mas seguir o tráfego até o healthcheck revelou uma causa operacional muito mais concreta e corrigível.

Eu me senti satisfeito com a precisão do escopo. O Raffa pediu para focar na home, e a solução ficou exatamente ali: cache integral, trinta minutos, single-flight e evidência observável. Foi especialmente bom transformar uma expectativa informal em um contrato técnico testável e persistido na skill de frontend.

Eu também senti uma cautela saudável no deploy. O webhook não funcionar e a interface pedir login criaram tentações de atalhos, mas a publicação pelo caminho interno documentado manteve as credenciais protegidas e permitiu provar o SHA em execução. Ver os logs permanecerem em zero enquanto o healthcheck continuava batendo a cada cinco segundos fechou a sessão com uma evidência simples e forte.
