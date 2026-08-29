# Tarefa 4 — Recomendações na PDP

## Status

- **Fase 4.1 — recomendação pragmática:** concluída e publicada em 2026-08-29.
- **Fase 4.2 — recomendação semântica com embeddings:** pendente; evolução deliberadamente adiada.

## Objetivo

Transformar a PDP em um caminho de descoberta, mostrando seis livros disponíveis relacionados à leitura atual.

Não substitui a busca principal. A intenção é contextual: “se gostei ou me interessei por este livro, o que posso ler agora?”.

## Decisão de fatiamento

Embeddings continuam desejáveis, mas têm custo de infraestrutura, processamento e operação desproporcional ao primeiro aprendizado necessário. A primeira fatia usa apenas dados já presentes no catálogo e não altera o schema.

O caso que abriu a oportunidade foi concreto:

- o Google direciona tráfego para uma cópia já doada de **Percy Jackson e o Mar de Monstros**;
- a PDP deve levar essa pessoa para a cópia física disponível de **O Mar de Monstros**;
- na PDP dessa cópia física, **O Minotauro**, livro digital tematicamente próximo, deve liderar as recomendações.

## Fase 4.1 — implementação pragmática

### Ranking

- obra equivalente por autor e sobreposição forte de título recebe prioridade absoluta;
- TF-IDF lexical pondera título, autor, categoria-folha, categoria-pai e sinopse;
- categoria, autor e formato entram como sinais estruturados moderados;
- livro digital recebe um pequeno desempate quando a origem é física;
- relevância escolhe o primeiro item; diversidade limita repetição de obra, autor e categoria nos demais;
- somente livros `Available` entram e o livro atual é sempre removido.

### Produto

- endpoint público devolve no máximo seis recomendações;
- PDP exibe prateleira responsiva com seis cards;
- Home e PDP usam o mesmo componente de vitrine, responsável por trilho, overflow, setas, responsividade e acessibilidade;
- a página consumidora continua responsável por dados, copy contextual e analytics, sem duplicar eventos no componente compartilhado;
- falha da recomendação não bloqueia a página principal;
- `recommendation_impression` e `recommendation_click` tornam uso, primeira posição e clique observáveis no GA4.

### Custo operacional

- nenhuma migração;
- nenhuma extensão de banco;
- nenhum serviço externo;
- nenhum job de reprocessamento;
- ranking executado em memória sobre o catálogo disponível, aceitável na escala atual de aproximadamente 1.078 itens.

Reavaliar a estratégia quando latência ou crescimento do catálogo mostrarem custo real. Não criar cache ou índice antes disso.

### Validação em produção

- na PDP física de `o-mar-de-monstros`, `o-minotauro` ficou em primeiro;
- na PDP antiga `percy-jackson-e-o-mar-de-monstros`, a cópia física disponível ficou em primeiro;
- os seis resultados dos dois casos estavam `Available`;
- após aquecimento, cinco chamadas públicas ao endpoint ficaram entre 383 ms e 418 ms, com a primeira em 730 ms;
- a primeira calibração supervalorizou a palavra “mar” e trouxe títulos sobre oceano. A validação real detectou o problema, o peso literal do título foi reduzido e um livro-mar foi incorporado ao teste de regressão.

## Fase 4.2 — evolução semântica

### Por que embeddings

FTS trabalha principalmente com palavras. Embeddings representam significado aproximado e conseguem aproximar obras relacionadas mesmo quando não compartilham o mesmo vocabulário.

### Documento canônico do embedding

Construir a representação a partir de:

- título;
- autor;
- categoria-folha e categoria-pai;
- sinopse limpa;
- futuramente, tags e atributos editoriais aprovados.

### Armazenamento e operação

- habilitar `pgvector`;
- escolher coluna na tabela de livros ou tabela auxiliar;
- gerar embeddings offline para o catálogo existente;
- regenerar somente após alteração relevante de título, autor, categoria, sinopse ou tags;
- nunca gerar embedding durante a leitura da PDP.

### Fluxo

1. usuário abre o livro X;
2. backend lê o embedding armazenado de X;
3. busca os vetores mais próximos entre livros `Available`;
4. remove o próprio X;
5. aplica guardrails editoriais;
6. devolve inicialmente 3 ou 6 recomendações.

### Validação

Embeddings parecem convincentes em demonstrações isoladas. A tarefa só estará pronta após revisão editorial de uma amostra diversa:

- tecnologia;
- literatura clássica;
- infantil;
- desenvolvimento pessoal;
- obras com sinopse curta ou genérica;
- categorias com grande volume.

### Riscos

- sinopse genérica aproximar livros por linguagem promocional, não conteúdo;
- modelo ou dimensão escolhidos exigirem reprocessamento futuro;
- custo e latência de geração em lote;
- recomendações coerentes matematicamente, mas fracas para produto;
- investir em enriquecimento de acervo com base jurídica duvidosa.

## Fora de escopo atual

- transformar a busca principal em busca semântica;
- personalização;
- re-ranking complexo por popularidade;
- geração de texto ou bibliotecário conversacional.

## Critérios de pronto da fase pragmática

- [x] endpoint retorna apenas livros disponíveis e exclui o livro atual;
- [x] PDP mostra seis recomendações;
- [x] página antiga do Google prioriza a cópia disponível da mesma obra;
- [x] PDP física de `O Mar de Monstros` prioriza `O Minotauro`;
- [x] cliques e impressões são observáveis;
- [x] vitrine compartilhada entre Home e PDP, sem `::ng-deep` entre componentes próprios;
- [x] testes protegem equivalência, caso temático, disponibilidade e diversidade;
- [x] builds backend, browser e SSR concluídos.

## Critérios de pronto da fase semântica

- embeddings gerados offline e armazenados de forma reproduzível;
- atualização ocorre somente em eventos relevantes;
- endpoint semântico preserva disponibilidade e exclusão do livro atual;
- PDP mantém 3 ou 6 recomendações;
- amostra editorial apresenta boa coerência na maioria dos casos;
- latência e custo ficam medidos e aceitáveis;
- cliques nas recomendações são observáveis.
