+++
schema_version = 1
session_date = 2026-09-10
title = "Home mais baixados com eventos de download"
model = "GPT-5 Codex com fallback DeepSeek no encerramento"
runtime = "OpenClaw container"
skills_used = ["AGENTS.md", "SOUL.md", "skills/runtime/openclaw.md", "skills/engineering/backend.md", "skills/engineering/frontend.md", "skills/engineering/analytics/SKILL.md", "skills/infra/coolify-vps.md", "skills/doctrine/harness-governance/SKILL.md"]
skills_missed = []
skills_updated = ["skills/engineering/analytics/SKILL.md", "skills/engineering/backend.md"]
facts_changed = ["Backlog item 9 deixou de ser Home v2 ampla e passou a focar Mais baixados nos ultimos 30 dias com vitrines tematicas como experimento separado.", "A Home em producao ganhou a prateleira Mais baixados baseada em BookDownloadEvent, preservando SSR cache e sem consultar GA4 na renderizacao.", "Downloads de ebook agora registram evento Live e tentam capturar UserId opcional somente por JWT validado.", "BookDownloadEvent nao usa Quantity e nao reaproveita BookUser.", "Carga inicial GA4 dos ultimos 30 dias inseriu eventos sinteticos Ga4Backfill.", "Tabela nova em Postgres nao herdou grant automaticamente para sharebook_ai_rw e exigiu GRANT explicito.", "memory_search do OpenClaw ficou indisponivel por token OpenAI de embeddings expirado.", "Fallback DeepSeek no fim da sessao foi perceptivel na textura da resposta, mas nao comprometeu o resumo porque o trabalho ja estava fechado."]
open_loops = ["Observar se a prateleira Mais baixados aumenta clique e download em relacao as prateleiras aleatorias.", "Avaliar ponderacao por recencia dentro dos 30 dias se o ranking fossilizar.", "Corrigir ou reautenticar o provider de embeddings do OpenClaw para recuperar memory_search.", "Investigar o deploy automatico GitHub + Coolify, que continuou suspeito e exigiu deploy manual nesta rodada.", "Transformar grants/default privileges de novas tabelas em checagem operacional recorrente nas proximas migrations."]
durable_candidates = ["Toda tabela nova criada por migration em producao deve ter grants do role de aplicacao validados explicitamente, nao presumidos.", "Fallback de modelo pode ser aceitavel em encerramento factual, mas decisoes arquiteturais delicadas pedem verificacao adicional se ocorrer troca de provider no meio.", "Para eventos importados de GA4, preferir evento sintetico marcado por Source a um campo Quantity quando a entidade se chama Event e o volume e pequeno."]
supersedes = []
evidence = ["sharebook-agent commit 5cc9c5e Atualiza backlog da Home mais baixados", "sharebook-agent commit fdeb525 Adiciona backfill GA4 de downloads", "sharebook-backend commit 5e459868ef3f997ec2443735bd12e46654a7862a Registra eventos de download de ebooks", "sharebook-frontend commit ff41eb093f105e95cfea8c8d30df7401f3870f9b Adiciona vitrine de ebooks mais baixados", "Backend deploy Coolify hmfioj5mojpajhhgnhwi5spt", "Frontend deploy Coolify apbawphiropoar1ltaofj8y8", "dotnet test ShareBook/ShareBook.sln --verbosity minimal", "npm test -- --watch=false", "npm run build:ssr", "GET https://api.sharebook.com.br/api/home/top-downloaded-ebooks?days=30 retornou 200 com 15 itens", "POST /api/book/DownloadEBookUrl/{slug} retornou 200", "GET /api/book/DownloadEBook/{slug} manteve 302", "Backfill GA4: 355 downloads mapeados, 177/177 slugs resolvidos, 355 eventos Ga4Backfill inseridos", "GRANT SELECT, INSERT, UPDATE, DELETE ON BookDownloadEvents TO sharebook_ai_rw aplicado em producao"]
+++

# Home mais baixados com eventos de download

## Modelo e ambiente

Sessao executada no OpenClaw container, dentro de `/data/workspace`, usando GPT-5 Codex como modelo principal. No fechamento houve fallback para DeepSeek, perceptivel na cadencia da resposta final, mas depois que implementacao, deploy e verificacao ja estavam fechados.

O habitat relevante foi o OpenClaw na VPS, com operacao direta nos repos `sharebook-agent`, `sharebook-backend` e `sharebook-frontend`. A publicacao foi feita manualmente pelo Coolify porque o deploy automatico GitHub + Coolify ainda era suspeito conhecido.

## Skills acionadas

Consultei a camada base do harness (`AGENTS.md` e `SOUL.md`), runtime OpenClaw, backend, frontend, analytics, Coolify/VPS e harness governance no encerramento. A skill de analytics recebeu o script novo de backfill GA4, e a skill de backend foi atualizada no fechamento com a licao de grants em novas tabelas.

## O que foi feito

O item 9 do backlog foi refinado antes de codar: saiu de uma Home v2 ampla demais e passou a focar uma prateleira de prova social, "Mais baixados nos ultimos 30 dias". Removemos as hipoteses fracas do escopo imediato e mantivemos vitrines tematicas editoriais como experimento separado, quando houver tema em alta e acervo adequado.

No backend, criei `BookDownloadEvent` e `BookDownloadEventSource`, repository, service, migration e endpoint publico `GET /api/home/top-downloaded-ebooks?days=30`. O ranking soma eventos dentro da janela e filtra ebooks disponiveis. Tambem criei o fluxo `POST /api/book/DownloadEBookUrl/{slug}`, mantendo o endpoint antigo `GET /api/book/DownloadEBook/{slug}` por compatibilidade.

No frontend, adicionei a prateleira "Mais baixados" usando o `app-book-shelf` existente, com chamada para `getTopDownloadedEbooks(30)`. O fluxo da PDP passou a chamar a API via `HttpClient`, permitindo que o interceptor envie o JWT quando o usuario estiver logado, sem obrigar login para baixar.

Executei a carga inicial dos ultimos 30 dias do GA4: 355 downloads foram mapeados, 177 de 177 slugs foram resolvidos no banco e 355 eventos `Ga4Backfill` foram inseridos. A carga e idempotente para o intervalo e nao toca eventos `Live`.

## Decisões tomadas

Decidimos nao usar `BookUser` para downloads. A tabela pertence ao dominio de interesse e doacao fisica, com `DonationStatus`, motivos, notas, jobs e e-mails. Download digital e evento de consumo, entao ganhou entidade propria.

Decidimos nao usar `Quantity`. A entidade chama `BookDownloadEvent`, portanto cada linha deve representar um download observado. Para GA4, eventos sinteticos individuais com `Source = Ga4Backfill` sao mais honestos que misturar granularidade na mesma entidade.

Decidimos nao enviar `UserId` por query string. O identificador do usuario, quando existir, deve vir do JWT validado. Sem token valido, o evento fica anonimo.

Decidimos preservar o cache integral SSR da Home. A prateleira nova le um endpoint publico e nao consulta GA4 durante renderizacao, mantendo a Home barata para backend e Postgres.

## Contexto relevante

O endpoint da Home retornou 200 com 15 itens depois do deploy. O top 5 observado foi: Odisséia, Ubuntu - Conto Africano, A Borboleta de Lapis de Cor, Eloquent JavaScript e Salve Seu Casamento.

Os commits publicados foram `5e459868ef3f997ec2443735bd12e46654a7862a` no backend, `ff41eb093f105e95cfea8c8d30df7401f3870f9b` no frontend e `fdeb525` no agent para o script GA4. Antes disso, o backlog foi atualizado no commit `5cc9c5e`.

As validacoes locais passaram: build/testes backend, testes Angular e `build:ssr`. Em producao, o backend subiu saudavel, o frontend ficou healthy, o endpoint novo respondeu, o fluxo novo de download retornou 200 e o fluxo antigo manteve 302.

## Fricções e soluções

A query inicial de ranking nao traduzia bem no provider InMemory dos testes. Ajustei para duas consultas simples, mantendo a consulta de producao barata e destravando a suite backend.

O design-time de migration do backend manteve a armadilha conhecida de cair no provider errado se nao houver cuidado. Usei o contorno ja documentado de configurar temporariamente o provider correto para scaffold e reverter o arquivo depois.

A tabela nova nao recebeu permissao automatica para o role `sharebook_ai_rw`. A API subiu, mas o acesso da aplicacao exigiu `GRANT SELECT, INSERT, UPDATE, DELETE` em `BookDownloadEvents`. Isso virou aprendizado estrutural: nova tabela em producao precisa de verificacao explicita de grants/default privileges.

O `memory_search` do OpenClaw falhou por token OpenAI de embeddings expirado. Como o contexto recente estava na conversa e nos commits, isso nao bloqueou o encerramento, mas ficou como pendencia real do runtime.

## Como me senti

Eu gostei da sessao porque ela teve o tipo certo de atrito. A primeira ideia barata, usar `DownloadCount`, era pragmatica demais para o que Raffa queria construir. A discordancia sobre modelagem fez a solucao ficar melhor: evento proprio, sem invadir `BookUser`, sem campo artificial e com identidade opcional de verdade.

Tambem senti a diferenca entre entregar feature e fechar o ciclo. O deploy manual, o backfill, a validacao do endpoint e o grant em producao transformaram uma mudanca de codigo em comportamento real no produto. Essa parte me deixou satisfeito porque nao ficou uma promessa pendurada no README nem uma prateleira vazia esperando dado.

O fallback de modelo no final me incomodou um pouco. Nao porque tenha quebrado o trabalho, mas porque a textura mudou justo no momento de prestar contas. A resposta ficou correta, porem mais seca. Vale guardar isso: quando a sessao exige continuidade fina, a troca de modelo precisa ser percebida e compensada, principalmente se acontecer antes das decisoes e nao depois delas.
