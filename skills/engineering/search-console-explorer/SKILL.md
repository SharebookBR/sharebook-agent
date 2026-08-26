---
name: search-console-explorer
description: Investiga aquisição orgânica do Sharebook no Google Search Console, compara períodos e transforma queries, páginas, CTR, impressões e posição em oportunidades priorizadas. Use para análises ad hoc, diagnóstico de quedas ou crescimento, canibalização e escolha de ações de SEO; não use para métricas comportamentais internas, que pertencem ao GA4.
---

# Search Console Explorer

Explorar o Search Console para responder perguntas e orientar ação. O dashboard mostra o pulso; esta skill investiga o porquê.

## Fonte e ferramenta

- Propriedade: `sc-domain:sharebook.com.br`.
- Credencial local protegida: `sharebook-agent/scripts/production/ga4-key.json`.
- Service account: `sharebook-analytics-agent@sharebook-a174c.iam.gserviceaccount.com`.
- Escopo: `https://www.googleapis.com/auth/webmasters.readonly`.
- Script canônico: `scripts/search_console_query.py` nesta skill.

Reutilizar essa credencial. Não criar outro segredo, não imprimir a chave e não pedir OAuth humano enquanto a service account continuar autorizada.

## Workflow

1. Traduzir a pergunta em recorte, dimensões e comparação. Não começar despejando todas as queries.
2. Consultar dias consolidados. O padrão é 28 dias terminando 3 dias antes da data atual do Search Console.
3. Buscar primeiro o agregado; depois abrir somente as dimensões que explicam o movimento.
4. Comparar com janela anterior de igual duração quando a pergunta envolver crescimento, queda ou prioridade.
5. Separar descoberta de decisão: uma correlação vira hipótese até existir evidência suficiente.
6. Entregar uma shortlist pequena, com potencial, esforço provável e próximo passo verificável.

## Escolha da investigação

- **Pulso geral:** `overview` para cliques, impressões, CTR e posição contra o período anterior.
- **Queries ou páginas:** `query --dimensions query` ou `query --dimensions page`.
- **Query → landing page:** `query --dimensions query,page`.
- **Mudanças:** adicionar `--compare`; `positionChange` positivo significa melhora.
- **Dispositivo, país ou recorte de URL:** usar `--filter DIMENSION OPERATOR EXPRESSION`.
- **Quick wins de CTR:** `opportunities`; tratar a pontuação como heurística de triagem, não previsão.
- **Canibalização:** agrupar por `query,page` e procurar uma query relevante dividida entre duas ou mais páginas. Confirmar intenção antes de recomendar canonical, redirect ou consolidação.

Exemplos e interpretação ficam em [query-recipes.md](references/query-recipes.md). Ler esse arquivo quando a pergunta envolver queda, canibalização, marca vs. não marca, ou priorização editorial.

## Comandos essenciais

Usar o Python 3.12 operacional do Windows:

```powershell
& 'C:\Users\raffa\AppData\Local\Programs\Python\Python312\python.exe' `
  'C:\Repos\SHAREBOOK\sharebook-agent\skills\engineering\search-console-explorer\scripts\search_console_query.py' sites
```

```powershell
& 'C:\Users\raffa\AppData\Local\Programs\Python\Python312\python.exe' `
  'C:\Repos\SHAREBOOK\sharebook-agent\skills\engineering\search-console-explorer\scripts\search_console_query.py' overview
```

```powershell
& 'C:\Users\raffa\AppData\Local\Programs\Python\Python312\python.exe' `
  'C:\Repos\SHAREBOOK\sharebook-agent\skills\engineering\search-console-explorer\scripts\search_console_query.py' query `
  --dimensions query,page --compare --max-rows 25000
```

```powershell
& 'C:\Users\raffa\AppData\Local\Programs\Python\Python312\python.exe' `
  'C:\Repos\SHAREBOOK\sharebook-agent\skills\engineering\search-console-explorer\scripts\search_console_query.py' opportunities `
  --min-impressions 20 --target-ctr 0.05 --max-position 20 --top 10
```

## Invariantes de leitura

- Datas do GSC são rotuladas em Pacific Time. Não comparar um dia do GSC como se fosse o mesmo corte diário do GA4.
- CTR vem como fração: `0.0484` significa `4,84%`.
- Posição menor é melhor. No script, `positionChange = posição anterior - posição atual`; valor positivo é avanço.
- Média de posição não é ranking fixo de uma URL. É uma média condicionada às impressões registradas.
- Somar linhas de query ou página pode não reproduzir o agregado por privacidade, truncamento e agregação.
- A API devolve as linhas principais, não promete o long tail completo. Paginação reduz a perda, mas não elimina o limite interno.
- Filtrar por query remove queries anonimizadas do universo comparado. Não vender marca vs. não marca como decomposição exata.
- GSC mede presença e clique no Google; GA4 mede sessões e comportamento no site. Divergência entre ambos é esperada.

## Saída esperada

Responder com:

1. período atual e comparação;
2. movimento principal em cliques, impressões, CTR e posição;
3. até cinco achados sustentados pelos dados;
4. oportunidades ordenadas por valor provável versus esforço;
5. próximo passo concreto e a métrica que confirmará ou rejeitará a hipótese.

Evitar JSON bruto no chat. Dizer quando a amostra é pequena, a query está anonimizada ou a recomendação depende de inspeção da SERP/PDP.

## Guardrails

- Esta skill é somente leitura. Alterações em conteúdo, metadata, redirects, sitemap ou permissões exigem pedido explícito do usuário.
- Não atribuir causalidade a uma mudança recente de SEO sem janela suficiente e comparação coerente.
- Não otimizar CTR sacrificando intenção, precisão editorial ou promessa real da página.
- Não recomendar consolidar páginas apenas porque compartilham uma query; exemplares físicos duplicados podem ser legítimos no produto.
- Para o snapshot já servido no admin, começar por `GET /api/analytics/dashboard`. Usar esta skill quando for preciso granularidade ou investigação além do dashboard.

## Fontes oficiais

- [Search Analytics API](https://developers.google.com/webmaster-tools/v1/searchanalytics/query)
- [Como obter dados de performance](https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data)
- [Limitações e discrepâncias dos dados](https://support.google.com/webmasters/answer/17010575)
