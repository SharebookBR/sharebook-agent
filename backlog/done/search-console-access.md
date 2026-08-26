# Search Console Access — concluído em 26/08/2026

## Objetivo entregue

O Sharebook passou a consultar programaticamente queries, páginas, cliques, impressões, CTR e posição média do Google Search Console usando a mesma service account já adotada no GA4.

## Acesso

- Service account: `sharebook-analytics-agent@sharebook-a174c.iam.gserviceaccount.com`.
- Propriedade: `sc-domain:sharebook.com.br`.
- Search Console API habilitada no projeto GCP `sharebook-a174c`.
- A conta foi adicionada à propriedade e a API confirmou acesso `siteFullUser`.
- A autenticação reutiliza `GA4__CredentialsBase64`; nenhum segundo segredo foi criado.

## Entrega

- Backend consulta a Search Analytics API diretamente via `HttpClient` e escopo somente leitura.
- O endpoint `GET /api/analytics/dashboard` inclui um bloco `searchConsole` sem comprometer os dados de GA4 caso o GSC esteja temporariamente indisponível.
- A janela fixa usa os últimos 28 dias consolidados, com atraso de 3 dias, comparados aos 28 dias anteriores.
- O painel `/admin/analytics` mostra cliques, impressões, CTR, posição média, tendência diária e até cinco oportunidades por query e landing page.
- Oportunidades exigem pelo menos 20 impressões, CTR abaixo de 5% e posição média até 20.
- Cache consolidado de 12 horas preservado.

## Validação

- Produção, período de 27/07/2026 a 23/08/2026: 1.167 cliques, 24.103 impressões, CTR 4,84% e posição média 9,11.
- Período anterior, de 29/06/2026 a 26/07/2026: 981 cliques, 25.785 impressões, CTR 3,80% e posição média 5,04.
- Backend: commit `183fe6cd2fbc81b600a0b1d0a155cf15ce91dcf5`, imagem exata saudável em produção.
- Frontend: commit `e4e24ac36d8fe97a86848daee1b5f62d5b34774c`, imagem exata saudável em produção.
- Endpoint de produção confirmou `searchConsole.available = true`, 28 pontos diários e cinco oportunidades.

## Observação operacional

O nível `siteFullUser` é suficiente, mas mais amplo do que o necessário para leitura. Depois da validação final da tela, pode ser reduzido para **Restrito** e testado novamente.
