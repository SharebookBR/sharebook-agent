# Tarefa 5 — Recomendações semânticas com embeddings

## Status

**Pendente. Evolução deliberadamente adiada até existir evidência de limite recorrente na recomendação pragmática.**

## Objetivo

Evoluir as recomendações da PDP para aproximar livros por significado editorial mesmo quando eles não compartilham o mesmo vocabulário.

## Dependência e gatilho de retomada

- depende da [Tarefa 4 — Recomendações pragmáticas na PDP](tarefa04-recomendacoes-pragmaticas-pdp.md);
- retomar quando amostra editorial ou dados de navegação mostrarem limites lexicais recorrentes;
- não iniciar apenas porque embeddings são tecnicamente interessantes.

## Por que embeddings

FTS e TF-IDF trabalham principalmente com palavras. Embeddings representam significado aproximado e conseguem aproximar obras relacionadas mesmo quando título e sinopse usam vocabulários diferentes.

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
6. devolve inicialmente seis recomendações.

## Validação

Embeddings parecem convincentes em demonstrações isoladas. A tarefa só estará pronta após revisão editorial de uma amostra diversa:

- tecnologia;
- literatura clássica;
- infantil;
- desenvolvimento pessoal;
- obras com sinopse curta ou genérica;
- categorias com grande volume.

Comparar a qualidade com a recomendação pragmática, preservando os casos concretos já protegidos e medindo latência e navegação entre PDPs.

## Riscos

- sinopse genérica aproximar livros por linguagem promocional, não conteúdo;
- modelo ou dimensão escolhidos exigirem reprocessamento futuro;
- custo e latência de geração em lote;
- recomendações coerentes matematicamente, mas fracas para produto;
- somar scores lexical e vetorial sem calibração;
- investir em enriquecimento de acervo com base jurídica duvidosa.

## Fora de escopo

- transformar a busca principal em busca semântica;
- personalização;
- re-ranking complexo por popularidade;
- gerar embeddings durante o acesso à PDP;
- geração de texto ou bibliotecário conversacional.

## Critérios de pronto

- [ ] embeddings gerados offline e armazenados de forma reproduzível;
- [ ] atualização ocorre somente em eventos relevantes;
- [ ] endpoint semântico preserva disponibilidade e exclusão do livro atual;
- [ ] PDP mantém seis recomendações e o contrato analítico existente;
- [ ] amostra editorial apresenta boa coerência na maioria dos casos;
- [ ] casos concretos da tarefa 4 continuam protegidos;
- [ ] latência e custo ficam medidos e aceitáveis;
- [ ] ganho sobre a abordagem pragmática é demonstrado.
