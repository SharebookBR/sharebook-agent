# Receitas de investigação

Ler este arquivo quando a análise exigir mais do que o snapshot do dashboard.

## 1. Queda ou crescimento

1. Rodar `overview` para separar movimento de volume, CTR e posição.
2. Abrir `query --dimensions page --compare` para localizar onde o movimento se concentrou.
3. Nas páginas relevantes, abrir `query --dimensions query,page --compare`.
4. Segmentar por dispositivo somente se a hipótese justificar.

Leituras úteis:

- impressões sobem, posição estável, cliques sobem: expansão de demanda ou cobertura;
- impressões estáveis, posição melhora, CTR sobe: ganho provável de visibilidade/snippet;
- impressões caem e posição piora: perda de cobertura ou competitividade;
- posição melhora e impressões caem: o mix de queries pode ter mudado; não concluir vitória apenas pela média.

Verificar também [anomalias oficiais do Search Console](https://support.google.com/webmasters/answer/6211453) antes de explicar uma ruptura abrupta como efeito do produto.

## 2. Oportunidades de CTR

Começar com:

```powershell
python skills/engineering/search-console-explorer/scripts/search_console_query.py opportunities --min-impressions 20 --target-ctr 0.05 --max-position 20 --top 20
```

Depois revisar manualmente as primeiras candidatas:

- a landing page responde de fato à query?
- o title é específico e legível?
- a description acrescenta contexto verdadeiro?
- há intenção incompatível, marca alheia ou ambiguidade?
- a SERP tem recursos que naturalmente reduzem CTR?

`missedClicksAtTargetCtr` é `impressões × (CTR alvo − CTR atual)`. Serve para ordenar investigação; não é promessa de tráfego.

## 3. Posição 4–15

Usar `query --dimensions query,page --compare`. Priorizar combinações com demanda recorrente, página alinhada e ganho plausível via conteúdo, title, links internos ou dados estruturados.

Não tratar a posição média como rank fixo. Dispositivo, localização, query e aparência da busca mudam a média.

## 4. Canibalização

Consultar `query,page` e agrupar localmente por query. Sinal inicial: a mesma query relevante tem impressões materiais em duas ou mais URLs.

Antes de agir, classificar:

- páginas com intenções diferentes: coexistência pode ser correta;
- exemplares físicos do mesmo livro: duplicidade é legítima no produto;
- PDP e categoria: podem cobrir necessidades diferentes;
- URLs equivalentes ou históricas: podem justificar canonical, redirect ou consolidação.

Canibalização é hipótese estrutural, não mera repetição na tabela.

## 5. Marca vs. não marca

Rodar duas consultas filtradas, uma contendo `sharebook` e outra excluindo. Tratar a proporção como aproximação: filtros por query excluem consultas anonimizadas, portanto as duas partes não recompõem exatamente o total.

## 6. Coortes editoriais

Para livros publicados após uma ação editorial:

1. obter a lista e data de publicação no produto;
2. consultar páginas correspondentes com dimensão `date,page`;
3. calcular tempo até primeira impressão e primeiro clique;
4. comparar coortes semelhantes, sem misturar páginas antigas com autoridade acumulada;
5. registrar mudanças de title/description para não atribuir causalidade sem cronologia.

## Operadores de filtro

O script aceita os operadores da API: `contains`, `equals`, `notContains`, `notEquals`, `includingRegex` e `excludingRegex`.

Exemplo:

```powershell
python skills/engineering/search-console-explorer/scripts/search_console_query.py query `
  --dimensions query,page `
  --filter page contains /livros/ `
  --filter query notContains sharebook `
  --compare
```

## Limites que mudam a interpretação

- O Google omite queries raras ou sensíveis por privacidade.
- A API retorna no máximo 25 mil linhas por página e mantém limites internos de linhas principais.
- Totais agregados podem superar a soma das linhas dimensionadas.
- Dados costumam ficar disponíveis após 2–3 dias e usam Pacific Time.
- Agregação por propriedade e por página calcula impressão, clique e posição de maneiras diferentes.

Fontes: [documentação da query](https://developers.google.com/webmaster-tools/v1/searchanalytics/query), [extração de dados](https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data) e [explicação de agregação](https://support.google.com/webmasters/answer/17011364).
