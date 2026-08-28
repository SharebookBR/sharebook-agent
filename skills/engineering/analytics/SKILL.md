---
name: analytics
description: Especialista em Google Analytics 4 e Google Search Console para o Sharebook. Use para extrair métricas de tráfego e busca orgânica, investigar comportamento em PDPs, comparar `page_view` vs `ebook_download`, inferir busca interna, cruzar queries com landing pages e explicar limites do GA4 versus GSC e tracing/observability.
---

# Sharebook Analytics Expert

Operar GA4 e Search Console como ferramentas de investigação, não como painel decorativo.

## Atalho operacional — endpoint consolidado

Antes de abrir a API do GA4 diretamente, usar o endpoint do Sharebook que já agrega tudo:

```
GET https://api.sharebook.com.br/api/analytics/dashboard
Authorization: Bearer <SHAREBOOK_PROD_ACCESS_TOKEN>
```

Retorna em uma chamada: sessões por semana (13 semanas), downloads, logins, cadastros, top 10 livros por views e downloads (acumulado e por semana), busca interna e visão orgânica do Search Console. Cache de 12h no backend — resposta instantânea na maioria das vezes.

Usar as APIs GA4 ou Search Console diretamente só quando precisar de granularidade, filtros ou métricas que o endpoint não expõe.

Para investigação ad hoc no Search Console — queries, páginas, comparação de períodos, canibalização e oportunidades — ler e usar [`../search-console-explorer/SKILL.md`](../search-console-explorer/SKILL.md). Esta skill de analytics permanece como visão consolidada e ponte entre GA4, GSC e produto.

## Fonte da verdade

- **GCP Key:** `sharebook-agent/scripts/production/ga4-key.json` (protegida)
- **Property ID:** `386966473`
- **GA4 API:** Google Analytics Data API v1beta
- **Search Console property:** `sc-domain:sharebook.com.br`
- **Search Console API:** Search Analytics REST API, escopo readonly
- **Service account:** `sharebook-analytics-agent@sharebook-a174c.iam.gserviceaccount.com`

As duas integrações reutilizam a mesma credencial via `GA4__CredentialsBase64`. Não criar um segundo segredo para o Search Console.

## Perguntas que esta skill deve responder bem

- Quantos acessos tivemos em um período?
- Quais PDPs tiveram mais views e quais converteram em download?
- Um download veio de Google orgânico ou de navegação interna?
- A busca interna foi usada, mesmo sem evento GA4 dedicado?
- Um fluxo `buscar -> PDP` aconteceu de fato?
- A home está empurrando PDPs ou o usuário já entra dirigido?

## Leituras canônicas

### Origem de sessão
Confiar primeiro em:
- `sessionSourceMedium`
- `sessionDefaultChannelGroup`

Usar `pageReferrer` como pista complementar, não como verdade única.

Exemplo:
- `sessionSourceMedium = google / organic`
- `sessionDefaultChannelGroup = Organic Search`

Isso sustenta a leitura de origem orgânica melhor do que o `pageReferrer` cru sozinho.

### Funil de ebook
A leitura mais útil hoje é:
1. `page_view` ou `screenPageViews` da PDP
2. `ebook_download`

Calcular taxa analítica:
- `downloads / views`

Guardrail:
- isso não é reconciliação contábil 1:1
- o GA4 pode mostrar `downloads > views` em casos pontuais
- tratar isso como sinal comportamental, não verdade forense

### Busca interna sem evento dedicado
Hoje a busca interna pode ser inferida pela rota:
- `/buscar/:criteria`

Mesmo sem `search`, `view_search_results` ou `internal_search`, ainda dá para extrair:
- volume de buscas
- termos buscados
- tendência por período
- indícios de fluxo `buscar -> PDP`

### Cruzamento `buscar -> PDP`
Para validar se a busca levou à PDP:
- filtrar `pagePath` começando com `/livros/`
- cruzar com `pageReferrer` contendo `/buscar/`
- comparar o termo da rota `/buscar/:criteria` com a PDP acessada

Quando isso bater, tratar como evidência real de navegação interna dirigida.

## Rituais de análise

### Check de saúde diário
Verificar:
- home (`/`) no dia de ontem
- top PDPs por `screenPageViews`
- `ebook_download` por `pagePath`
- origem por `sessionSourceMedium` quando houver conversão

### Leitura de PDP de ontem
Entregar preferencialmente:
- nome da PDP
- total de visualizações
- total de downloads
- creation date do livro no produto

Usar `creation date` para inferência de tempo de indexação, mas sem forçar causalidade cedo demais.

### Leitura de descoberta
Quando surgirem muitos livros novos em PDP:
- testar hipótese de home
- testar hipótese de Google orgânico
- testar hipótese de busca interna

Não cravar autoria do tráfego sem cruzamento.

## Limites reais do GA4

Explicar sem floreio:
- GA4 é mais estatístico do que determinístico
- não é tracing
- não é replay perfeito de sessão
- não é investigação forense no estilo Grafana

Comparação útil:
- **GA4**: tendência, funil, canal, atribuição, conversão
- **Tracing/observability**: trilha exata, causalidade técnica, request path, falha por operação

## Guardrails

- Sempre verificar se a chave JSON existe antes de rodar queries.
- Não expor o conteúdo da chave ou segredos em logs/mensagens.
- Mastigar a saída da API. Não despejar JSON bruto no chat.
- Em Telegram, preferir **bullets**. Evitar tabela rígida porque quebra fácil.
- Quando `pageReferrer` conflitar com origem de sessão, priorizar a atribuição de sessão do GA4 e explicar a divergência.
- Quando a análise depender de `screenPageViews`, lembrar que pode haver pequenas esquisitices em SPA.

## Dashboard Analytics — Integração Sharebook

Dashboard integrado ao painel admin em 2026-06-01.

### Acesso
- Rota Angular: `/admin/analytics` (protegida por `AuthGuardAdmin`)
- Endpoint backend: `GET /api/analytics/dashboard` (admin only, `[AuthorizationFilter(Permissions.Permission.ApproveBook)]`)
- Cache `IMemoryCache` com TTL 12h — primeira request bate no GA4, restante instantâneo

### Eventos rastreados

Todos usam `GoogleAnalyticsService.sendEvent` em `src/app/core/services/analytics/google-analytics.service.ts`. Só dispara em `environment.production` e `isBrowser()`.

| Evento | Quando dispara | Componente | Parâmetros enviados | No dashboard |
|---|---|---|---|---|
| `login` | auth bem-sucedida | `login.component.ts` | `method: 'email'` | ✅ |
| `sign_up` | cadastro bem-sucedido | `register.component.ts` | `method: 'email'` | ✅ |
| `ebook_download` | clique em download na PDP | `details.component.ts` | `book_title`, `book_slug` | ✅ |
| `amazon_click` | clique no botão Amazon na PDP | `details.component.ts` | `book_title`, `book_slug` | ✅ |
| `amazon_click` | clique no CTA Amazon na página de zero-resultado | `search-results.component.ts` | `book_title` (= search_term, sem slug) | ✅ |
| `share_modal_open` | clique em "Compartilhar com amigos" na PDP | `details.component.ts` | `book_title`, `book_slug` | ✅ |
| `social_share` | escolha do canal no modal de compartilhamento | `details.component.ts` | `book_title`, `book_slug`, `method` (canal) | ✅ |
| `search` | busca concluída e página de resultados carregada | `search-results.component.ts` | `search_term`, `results_count` | ✅ |
| `book_request_modal_open` | abriu modal de pedido de livro | `request.component.ts` | `book_id`, `book_title` | ✅ |
| `book_request_success` | pedido enviado com sucesso | `request.component.ts` | `book_id`, `book_title` | ✅ |
| `book_request_error` | pedido falhou | `request.component.ts` | `book_id`, `book_title` | ✅ |

**Botões sem evento GA4** (intencional): "Denunciar direitos autorais" e "Editar livro".

**Busca tem um único ponto de disparo:** `search-results.component.ts`, depois que a API responde e a lista de resultados disponíveis é formada. Os disparos no header desktop e no bottom sheet mobile foram removidos em 25/06/2026 porque duplicavam a mesma busca. Portanto, `eventCount(search)` representa buscas concluídas, sem precisar dividir o total por dois.

`results_count` é enviado, mas ainda não foi registrado como custom metric no GA4. Enquanto isso não acontecer, a Data API não consegue separar buscas com e sem resultado; não inferir zero-resultados pelo termo ou pelo `pagePath`.

**`amazon_click` tem dois contextos distintos:**
- PDP (`details.component.ts`): envio de `book_title` + `book_slug` — representa "quero comprar este livro específico".
- Zero-resultado (`search-results.component.ts`): envio de `book_title` = search_term (sem `book_slug`) — representa "busca sem resultado, monetizar a frustração". Distinguível no GA4 pela ausência de `book_slug`.

**Funis úteis:**
- Pedido: `book_request_modal_open` → `book_request_success` (conversão de pedido)
- Compartilhamento: `share_modal_open` → `social_share` (conversão de share)

### Custom Dimensions registradas na property

Parâmetros só ficam disponíveis na Data API após registro em **GA4 Admin → Exibição de dados → Definições personalizadas**. Não retroage.

| Dimensão (API) | Parâmetro | Eventos que enviam | Registrada em |
|---|---|---|---|
| `customEvent:search_term` | `search_term` | `search` | 04/06/2026 |
| `customEvent:book_title` | `book_title` | `amazon_click`, `ebook_download`, `share_modal_open`, `social_share`, `book_request_*` | 04/06/2026 |
| `customEvent:book_slug` | `book_slug` | `amazon_click`, `ebook_download`, `share_modal_open`, `social_share` | 04/06/2026 |

**Parâmetros enviados mas NÃO registrados:** `method` (canal do `social_share`) e `book_id` (eventos de pedido) como custom dimensions; `results_count` (evento `search`) como custom metric.

**Regra:** ao criar evento novo com parâmetros relevantes, registrar a custom dimension imediatamente — dados não retroagem.

### Configuração de credenciais

Credenciais via variável de ambiente `GA4__CredentialsBase64` (base64 do `ga4-key.json`). No Coolify, duplo underscore é separador de seção. O `appsettings.json` tem a seção `GA4.CredentialsBase64` vazia (só documentação).

### Dashboard Analytics (`/admin/analytics`)

Endpoint: `GET /api/analytics/dashboard` — cache 12h no backend (`IMemoryCache`).

**Payload retornado:**
- `sessions`, `downloads`, `logins`, `signups` — séries semanais (12 semanas)
- `totalDownloads`, `totalLogins`, `totalSignups` — totais do período
- `topBooksByViews`, `topBooksByDownloads` — top 10 acumulado
- `topBooksByViewsPerWeek`, `topBooksByDownloadsPerWeek` — top 10 por semana
- `eventSummary` — contagem de todos os eventos rastreados (período completo)
- `eventSummaryPerWeek` — contagem por semana (filtro de semana client-side)
- `searchAnalytics` — recorte fixo dos últimos 30 dias (`29daysAgo` até hoje, datas inclusivas): total de buscas, usuários, termos distintos, top 10 termos e divisão por dispositivo
- `searchConsole` — disponibilidade, datas, KPIs do período atual e anterior, série diária e até cinco oportunidades por query + landing page

**KPIs:** sessões, downloads, logins, cadastros — filtrados pela semana selecionada.
**Select de semana:** ISO week internamente, display `YYYY-MM-Wn`. Semana corrente com highlight laranja.

**Seção de busca:** é fixa em 30 dias e deliberadamente independente do select semanal. `DistinctTerms` usa os termos exatamente como foram digitados; diferenças de caixa, acento e typo permanecem separadas para expor o comportamento real da busca.

**Seção Google orgânico:** usa os últimos 28 dias consolidados, encerrando 3 dias antes de hoje, e compara com os 28 dias anteriores. Exibe cliques, impressões, CTR, posição média, série diária e até cinco oportunidades. Uma oportunidade precisa ter pelo menos 20 impressões, CTR abaixo de 5% e posição média até 20; a ordenação estima cliques perdidos até o limiar de 5%.

O Search Console é buscado em paralelo ao GA4. Se falhar, `searchConsole.available` fica falso e o restante do dashboard continua disponível. Não remover esse isolamento ao evoluir a integração.

### Biblioteca de charts

Chart.js via npm (`npm install chart.js`).

---

## Padrões de análise descobertos

### Gargalo de busca: relevância, não acervo

Análise GA4 de 90 dias (junho 2026) revelou padrão recorrente: termos como "acotar" (= "Corte de espinhos e rosas"), "ruivantes" (typo de "divergente") indicam que o usuário não encontra livros que JÁ ESTÃO no catálogo. O problema é de relevância, não de falta de acervo. Antes de concluir que "não temos o livro", cruzar o termo buscado com o catálogo usando alias, série e variações de título.

Implicação para roadmap: FTS (fase 1–2 do backlog busca-e-recomendacao) resolve typos e stemming. Sinônimo de série (ex: "acotar" = "A Corte de Espinhos e Rosas") requer registro manual ou thesaurus — não é automático.

### Orgânico converte mais no afiliado Amazon

Análise de `amazon_click` por canal (jun/2026): tráfego Organic Search gera mais cliques no afiliado Amazon do que Direct, mesmo em volume menor. Hipótese: usuário que veio pelo Google para um livro específico já tem intenção de compra — se não temos grátis, clica na Amazon. Tráfego direto costuma ser navegação casual, menos comprometido.

Implicação: CTA Amazon em zero-resultado de busca orgânica tem ROI alto. Monitorar `amazon_click` com segmentação por `sessionDefaultChannelGroup` para validar ao longo do tempo.

---

## SEO Operacional

### Soft 404 (SSR)

Em Angular Universal, quando um livro não existe, o componente sabe mas o servidor retorna HTTP 200. O Google conta como "soft 404" e para de indexar a URL.

Fix em `details.component.ts`:
```typescript
// Injetar no construtor:
@Inject(RESPONSE) @Optional() private response: any,

// Nas condições de not-found:
this.response?.status(404);
```

Verificar no Google Search Console > Cobertura > "Soft 404" — tendência deve cair após deploy.

### Canonical e domínio

- Domínio oficial: `https://www.sharebook.com.br` (com `www`)
- Redirect non-www → www configurado no Coolify
- `SeoService` e meta OG tags devem sempre usar `www`
- Share link vai direto para a PDP — não precisa de endpoint de redirect no backend (SSR já serve HTML com meta OG)

### Paginação de categorias — risco conhecido

A listagem pública de uma categoria-folha carrega 100 livros por página. Em 27/08/2026, apenas duas categorias-folha ultrapassavam esse limite (`Geral`, com 104, e `Valores e Emoções`, com 102), deixando 6 livros além da primeira página. Categorias-raiz maiores exibem subcategorias, não a grade paginada. Como todas as PDPs continuam no sitemap, paginação indexável foi avaliada e não justificou prioridade própria nessa escala. Reavaliar somente quando o volume tornar material a perda de navegação ou linkagem interna.

---

## Scripts disponíveis

Todos em `scripts/production/`. Preferir scripts existentes antes de inventar query manual.

| Script | Quando usar |
|---|---|
| `test_ga4_connection.py` | Testar conexão com a property. Rodar primeiro se a API não responder. |
| `ga4_list_dimensions.py` | Listar custom dimensions registradas. Diagnosticar `(not set)` na API. |
| `ga4_new_events.py` | Checar `search` e `amazon_click` por data (ontem + hoje). Útil após deploy. |
| `ga4_events_30d.py` | Panorama completo dos 10 eventos rastreados nos últimos 30 dias. |
| `ga4_search_via_pagepath.py` | Uso da busca via `/buscar/*` nos últimos 30 dias. Alternativa histórica ao evento `search` (custom dim só a partir de 04/06/2026). |

---
Para instalação de novos ambientes, consulte `sharebook-agent/skills/engineering/analytics/BOOTSTRAP.md`.
