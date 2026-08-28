# Tarefa 4 — Recomendações semânticas na PDP

## Status

**Pendente. Depende das Tarefas 2 e 3 e de catálogo editorialmente confiável.**

## Objetivo

Mostrar livros semanticamente parecidos na página de um livro usando embeddings e `pgvector`.

Não substitui a busca principal. A intenção aqui é descoberta contextual: “se gostei ou me interessei por este livro, o que mais se parece com ele?”.

## Por que embeddings

FTS trabalha principalmente com palavras. Embeddings representam significado aproximado e conseguem aproximar obras relacionadas mesmo quando não compartilham o mesmo vocabulário.

## Documento canônico do embedding

Construir a representação a partir de:

- título;
- autor;
- categoria-folha e categoria-pai;
- sinopse limpa;
- futuramente, tags e atributos editoriais aprovados.

## Armazenamento e operação

- habilitar `pgvector`;
- escolher coluna na tabela de livros ou tabela auxiliar;
- gerar embeddings offline para o catálogo existente;
- regenerar somente após alteração relevante de título, autor, categoria, sinopse ou tags;
- nunca gerar embedding durante a leitura da PDP.

## Fluxo

1. usuário abre o livro X;
2. backend lê o embedding armazenado de X;
3. busca os vetores mais próximos entre livros `Available`;
4. remove o próprio X;
5. aplica guardrails editoriais;
6. devolve inicialmente 3 ou 6 recomendações.

## Validação

Embeddings parecem convincentes em demonstrações isoladas. A tarefa só estará pronta após revisão editorial de uma amostra diversa:

- tecnologia;
- literatura clássica;
- infantil;
- desenvolvimento pessoal;
- obras com sinopse curta ou genérica;
- categorias com grande volume.

## Riscos

- sinopse genérica aproximar livros por linguagem promocional, não conteúdo;
- modelo ou dimensão escolhidos exigirem reprocessamento futuro;
- custo e latência de geração em lote;
- recomendações coerentes matematicamente, mas fracas para produto;
- investir em enriquecimento de acervo com base jurídica duvidosa.

## Fora de escopo

- transformar a busca principal em busca semântica;
- personalização;
- re-ranking complexo por popularidade;
- geração de texto ou bibliotecário conversacional.

## Critérios de pronto

- embeddings gerados offline e armazenados de forma reproduzível;
- atualização ocorre somente em eventos relevantes;
- endpoint retorna apenas livros disponíveis e exclui o livro atual;
- PDP mostra 3 ou 6 recomendações;
- amostra editorial apresenta boa coerência na maioria dos casos;
- latência e custo ficam medidos e aceitáveis;
- cliques nas recomendações são observáveis.
