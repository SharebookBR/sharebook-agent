---
name: sharebook-analytics-expert
description: Especialista em Google Analytics 4 para o Sharebook. Use para extrair métricas de tráfego, investigar comportamento em PDPs, comparar `page_view` vs `ebook_download`, inferir busca interna pela rota `/buscar/:criteria`, cruzar `buscar -> PDP` por `pageReferrer`, analisar origem orgânica (`sessionSourceMedium`, `sessionDefaultChannelGroup`) e explicar limites do GA4 versus tracing/observability.
---

# Sharebook Analytics Expert

Operar o GA4 como ferramenta de investigação, não como painel decorativo.

## Fonte da verdade

- **GCP Key:** `sharebook-agent/scripts/production/ga4-key.json` (protegida)
- **Property ID:** `386966473`
- **API:** Google Analytics Data API v1beta

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
- Cache `IMemoryCache` com TTL 24h — primeira request do dia bate no GA4, restante instantâneo

### Eventos rastreados

| Evento | Onde dispara |
|---|---|
| `login` | `login.component.ts` após auth bem-sucedida |
| `sign_up` | `register.component.ts` após cadastro bem-sucedido |
| `ebook_download` | PDP ao clicar em download |
| `social_share` | PDP ao clicar em compartilhar |

Todos usam `GoogleAnalyticsService.sendEvent` já existente.

### Configuração de credenciais

Credenciais via variável de ambiente `GA4__CredentialsBase64` (base64 do `ga4-key.json`). No Coolify, duplo underscore é separador de seção. O `appsettings.json` tem a seção `GA4.CredentialsBase64` vazia (só documentação).

### KPIs e filtro de semana

- 4 KPIs: sessões, downloads, logins, cadastros — filtrados pela semana selecionada
- Tabelas: top livros por views e downloads — filtradas por semana
- Todos os dados chegam numa única chamada de API (filtro de semana é 100% client-side)
- Select de semana: ISO week internamente, conversão para `YYYY-MM-Wn` só no display
- Semana corrente com highlight laranja no select

### Biblioteca de charts

Chart.js instalado via npm (`npm install chart.js`). Usar para visualizações de tendência semanal.

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

11+ categorias com mais de 24 livros digitais. Livros além da página 1 ficam sem link acessível para o Google. Risco documentado, não atacado ainda.

---

## Scripts disponíveis

### Teste de conexão
```bash
python sharebook-agent/scripts/production/test_ga4_connection.py
```

### Dashboard estático (prova de conceito)
```bash
python sharebook-agent/scripts/production/ga4_dashboard.py
```
Gera HTML local com métricas de 12 semanas, downloads, logins, cadastros e top 10 livros.

---
Para instalação de novos ambientes, consulte `sharebook-agent/skills/engineering/sharebook-analytics-expert/BOOTSTRAP.md`.
