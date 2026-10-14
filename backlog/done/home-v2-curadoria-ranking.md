# Home v2 — mais baixados e vitrines tematicas

## Contexto

A reformulação estrutural da Home foi concluída. Este item não corrige uma Home quebrada; reúne a próxima evolução de descoberta que ficou com valor claro após discussão em 2026-09-10.

A Home já tem uma vitrine editorial fixa de mitologia grega. Novas vitrines editoriais podem existir quando houver tema em alta na internet e acervo adequado, mas isso deve ser tratado como experimento editorial separado, não como expansão genérica de seções.

## Objetivo

Melhorar a descoberta com uma prateleira de prova social baseada em comportamento real: **Mais baixados nos últimos 30 dias**.

## Status em 2026-09-10

Fatia principal entregue em produção.

- Backend `sharebook-backend` commit `5e459868`: `BookDownloadEvent`, migration, endpoint `GET /api/home/top-downloaded-ebooks?days=30` e fluxo novo `POST /api/book/DownloadEBookUrl/{slug}`.
- Frontend `sharebook-frontend` commit `ff41eb09`: prateleira **Mais baixados** usando `app-book-shelf`, com cache SSR preservado.
- Backfill GA4 commit `fdeb525` no `sharebook-agent`: 355 eventos `Ga4Backfill` inseridos para os últimos 30 dias, com 177/177 slugs resolvidos.
- Produção validada: endpoint novo respondeu `200`, fluxo novo de download respondeu `200`, endpoint antigo manteve `302`, backend e frontend ficaram healthy.

Próximo passo: observar se a prateleira puxa clique/download melhor que as prateleiras aleatórias. Se o ranking fossilizar, avaliar ponderação por recência dentro dos 30 dias.

## Decisões de produto

- Implementar direto a versão baseada em eventos, sem uma v1 apenas com `Book.DownloadCount`.
- Remover do escopo as hipóteses fracas: escolhas genéricas da curadoria, destaques rotativos, livros curtos, reordenação ampla da Home e `Continue de onde parou`.
- Manter a possibilidade de vitrines temáticas editoriais baseadas em tendências da internet, desde que discutidas caso a caso.
- A nova prateleira deve nascer pequena e mensurável; não alongar a Home sem substituir ou justificar a seção adicional.

## Modelagem aprovada

Criar `BookDownloadEvent` como evento real de consumo digital, separado de `BookUser`.

Campos esperados:

- `Id`;
- `BookId`;
- `UserId` nullable;
- `DownloadedAtUtc`;
- `Source` (`Live` ou `Ga4Backfill`).

Decisões:

- Não usar `BookUser`: ele pertence ao domínio de interesse/doação física e carrega `DonationStatus`, `Reason`, `Note` e efeitos em jobs/e-mails.
- Não criar `Quantity`: se a entidade chama evento, cada linha deve representar um download observado. O backfill do GA4 cria eventos sintéticos individuais marcados por `Source`.
- `UserId` é opcional. Quando o usuário estiver logado, deve vir do JWT validado, nunca por query string.
- `Book.DownloadCount` pode continuar existindo como contador materializado histórico para PDP/social proof, mas o ranking de 30 dias deve vir de `BookDownloadEvent`.

## Fluxo de download

Hoje o frontend abre a URL de download com `window.open`, então o `JwtInterceptor` não injeta `Authorization`. Para capturar `UserId` opcional sem exigir login:

1. Frontend chama a API via `HttpClient` em endpoint anonimo de download/URL.
2. Se houver usuário logado, o `JwtInterceptor` envia o Bearer token.
3. Backend valida o token quando presente e extrai `UserId`; sem token válido, grava `UserId = null`.
4. Backend aplica rate limit, grava `BookDownloadEvent`, mantém o contador materializado quando aplicável e retorna a URL assinada ou executa o fluxo de arquivo local.
5. Frontend abre a URL retornada ou inicia o download sem perder conversão.

Não enviar `userId` por query string: é falsificável, vaza em logs/histórico/referer e quebra a semântica de autenticação.

## Backfill GA4

Fazer carga inicial dos últimos 30 dias usando GA4 como aproximação, não como auditoria perfeita.

Ordem:

1. Consultar `ebook_download` agrupado por data e `book_slug`.
2. Se `book_slug` não estiver disponível como dimensão consultável, usar `pagePath` como fallback e extrair o slug da PDP.
3. Resolver o slug contra `Books`.
4. Criar eventos sintéticos individuais com `Source = Ga4Backfill` e `DownloadedAtUtc` aproximado dentro do dia.
5. Garantir idempotência removendo/recriando apenas eventos `Ga4Backfill` do intervalo, sem tocar em eventos `Live`.

## Home e cache

- Endpoint publico sugerido: `GET /api/home/top-downloaded-ebooks?days=30`.
- Retornar o mesmo `HomeShowcaseBookDTO` usado pelas prateleiras atuais.
- A Home deve continuar usando `app-book-shelf`; não criar componente novo para esta prateleira.
- Preservar o cache integral SSR da rota `/` em `server.ts`. A prateleira nova deve se beneficiar do mesmo HTML cacheado, poupando backend e Postgres.
- Não consultar GA4 durante renderização da Home. GA4 entra apenas no backfill/rotina operacional.
- Se a consulta por eventos ficar pesada no futuro, criar agregação/materialização por janela; não começar por isso sem necessidade.

## Critérios de aceite

- [x] hipótese e métrica de sucesso definidas antes do código;
- [x] `BookDownloadEvent` persistido com migration e índices adequados para `DownloadedAtUtc` + `BookId`;
- [x] download real grava evento `Live` com `UserId` opcional via JWT quando possível;
- [x] backfill GA4 de 30 dias executável e idempotente;
- [x] prateleira **Mais baixados nos últimos 30 dias** aparece na Home usando o componente existente;
- [x] contrato do backend alinhado antes do componente Angular;
- [x] SSR e cache integral da Home preservados;
- [x] experiência mobile continua simples e rápida;
- [x] thumbnails permanecem nos cards;
- [x] testes mantidos apenas quando protegem comportamento relevante;
- [x] build SSR, pipeline e validação em produção passam.

## Fora de escopo imediato

- personalização sem dados suficientes;
- leitura online e persistência de progresso;
- múltiplas prateleiras novas numa única rodada;
- `UserId` em query string ou qualquer identidade declarativa não autenticada;
- ranking baseado em GA4 em tempo real na Home;
- mudanças cosméticas sem hipótese de produto.
