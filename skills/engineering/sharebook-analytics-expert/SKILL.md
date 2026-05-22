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

## Scripts disponíveis

### Teste de conexão
```bash
python sharebook-agent/scripts/production/test_ga4_connection.py
```

---
Para instalação de novos ambientes, consulte `sharebook-agent/skills/engineering/sharebook-analytics-expert/BOOTSTRAP.md`.
