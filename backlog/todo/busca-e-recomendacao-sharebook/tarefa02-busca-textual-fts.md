# Tarefa 2 — Busca textual com Full-Text Search

## Status

**Em discussão.**

## Objetivo

Substituir a busca literal por substring por uma busca lexical ranqueada, nativa do PostgreSQL e explicável.

FTS deve responder não apenas “este texto aparece?”, mas “quão relevante é este livro para esta consulta?”.

## Problema atual

A busca usa equivalentes de `Contains` em título, autor e categoria e ordena por data de criação. Isso prejudica:

- consultas com várias palavras;
- ranking de título exato;
- descoberta por categoria-pai;
- aproveitamento controlado da sinopse;
- evolução futura do catálogo.

## Pré-requisito de implementação — régua de relevância

Antes de escolher configuração textual ou pesos, montar uma bateria de 30 a 50 consultas com resultado esperado no topo ou no top 5.

Cobrir pelo menos:

- título exato;
- autor;
- termo composto;
- categoria-folha e categoria-pai;
- consulta em português e em inglês;
- variação de caixa e acento;
- termo amplo;
- termo inexistente;
- livro existente, mas indisponível;
- consultas reais do GA4.

Termos observados em agosto de 2026 incluem `odisseia`, `Odisséia`, `Orgulho e preconceito`, `a divina comédia`, `fisico` e `caverna de ssangue`.

## Campos candidatos e pesos iniciais

- título: peso máximo;
- autor: alto;
- categoria-folha e categoria-pai: médio;
- sinopse: baixo;
- data de criação: somente desempate, não relevância principal.

Correspondência exata de título e prefixo devem receber boost explícito antes do ranking textual geral.

## Decisões pendentes

- configuração `simple`, `portuguese` ou combinação para catálogo bilíngue;
- estratégia de remoção de acentos;
- documento calculado em consulta ou `tsvector` persistido;
- necessidade real de índice GIN na escala atual;
- peso relativo de título, autor, categorias e sinopse;
- tratamento de termos de formato como `fisico`, `impresso`, `ebook` e `digital`;
- paginação real da interface, que hoje solicita apenas página 1 com até 100 itens;
- contrato de observabilidade para resultado e clique.

## Direção inicial

Começar simples e mensurável. Com 1.078 livros disponíveis em 2026-08-28, relevância importa mais que pré-otimização. Evitar tabela auxiliar ou sincronização de índice enquanto uma consulta direta puder entregar qualidade e latência adequadas.

## Observabilidade mínima

- registrar `results_count` como métrica utilizável;
- rastrear clique em resultado;
- registrar posição clicada;
- preservar o termo pesquisado;
- permitir distinguir resultado lexical de fallback fuzzy quando a Tarefa 3 entrar.

Com o volume atual de busca, avaliação offline forte e acompanhamento pré/pós-release são mais honestos que teste A/B sem poder estatístico.

## Fora de escopo

- tolerância a typo com trigram;
- embeddings;
- busca semântica principal;
- popularidade e personalização;
- aliases editoriais como `acotar`.

## Critérios de pronto

- bateria de relevância documentada e executada antes/depois;
- público continua recebendo somente `Available`;
- título exato aparece acima de menção incidental na sinopse;
- consultas compostas apresentam melhora perceptível;
- ranking dos primeiros resultados é editorialmente coerente;
- paginação e `TotalItems` permanecem corretos;
- latência é aceitável e medida;
- testes e builds passam;
- produção é validada com consultas reais.
