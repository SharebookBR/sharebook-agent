# Tarefa 3 — Tolerância a erro com trigram e fallback fuzzy

## Status

**Pendente. Depende da Tarefa 2.**

## Objetivo

Evitar que typos e pequenas variações de escrita produzam falso zero quando existe um livro relevante no catálogo.

Exemplos:

- `machdo de assis`;
- `javascipt`;
- `doker`;
- `policarpo quaresm`;
- `caverna de ssangue`.

## Estratégia

- habilitar `pg_trgm`;
- normalizar caixa e acentos de forma coerente com a Tarefa 2;
- aplicar similaridade principalmente em título e autor;
- usar fuzzy somente quando exact/prefix/FTS retornarem poucos resultados ou score insuficiente;
- mesclar candidatos sem permitir que aproximação ultrapasse correspondência exata relevante.

Categoria e sinopse devem ter uso conservador no fuzzy para evitar ruído.

## Decisões pendentes

- limiar mínimo de similaridade;
- quantidade de resultados que aciona o fallback;
- merge por score calibrado ou fusão de posições;
- índices necessários na escala atual;
- como registrar que uma busca usou fuzzy.

Esses valores devem ser calibrados contra a bateria de relevância da Tarefa 2, não escolhidos por gosto matemático.

## Fora de escopo

- aliases e siglas editoriais;
- busca semântica;
- filtros estruturados;
- fuzzy indiscriminado em todos os campos.

## Critérios de pronto

- consultas com erro pequeno retornam o livro esperado no top 5;
- correspondência exata continua acima da aproximada;
- consultas sem sentido não recebem uma coleção de falsos positivos;
- custo da query permanece aceitável;
- fallback e zero-resultado ficam observáveis;
- testes e produção validam os casos reais selecionados.
