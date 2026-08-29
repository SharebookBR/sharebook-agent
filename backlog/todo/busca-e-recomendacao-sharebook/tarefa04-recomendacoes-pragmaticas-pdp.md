# Tarefa 4 — Recomendações pragmáticas na PDP

## Status

**Concluída e publicada em 2026-08-29.**

## Objetivo

Transformar a PDP em um caminho de descoberta, mostrando seis livros disponíveis relacionados à leitura atual sem exigir nova infraestrutura.

Não substitui a busca principal. A intenção é contextual: “se gostei ou me interessei por este livro, o que posso ler agora?”.

## Caso que abriu a oportunidade

- o Google direciona tráfego para uma cópia já doada de **Percy Jackson e o Mar de Monstros**;
- a PDP leva essa pessoa para a cópia física disponível de **O Mar de Monstros**;
- na PDP dessa cópia física, **O Minotauro**, livro digital tematicamente próximo, lidera as recomendações.

## Implementação

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

## Validação em produção

- na PDP física de `o-mar-de-monstros`, `o-minotauro` ficou em primeiro;
- na PDP antiga `percy-jackson-e-o-mar-de-monstros`, a cópia física disponível ficou em primeiro;
- os seis resultados dos dois casos estavam `Available`;
- após aquecimento, cinco chamadas públicas ao endpoint ficaram entre 383 ms e 418 ms, com a primeira em 730 ms;
- a primeira calibração supervalorizou a palavra “mar” e trouxe títulos sobre oceano. A validação real detectou o problema, o peso literal do título foi reduzido e um livro-mar foi incorporado ao teste de regressão.

## Fora de escopo

- embeddings e `pgvector`;
- transformar a busca principal em busca semântica;
- personalização;
- re-ranking por popularidade;
- geração de texto ou bibliotecário conversacional.

## Critérios de pronto

- [x] endpoint retorna apenas livros disponíveis e exclui o livro atual;
- [x] PDP mostra seis recomendações;
- [x] página antiga do Google prioriza a cópia disponível da mesma obra;
- [x] PDP física de `O Mar de Monstros` prioriza `O Minotauro`;
- [x] cliques e impressões são observáveis;
- [x] vitrine compartilhada entre Home e PDP, sem `::ng-deep` entre componentes próprios;
- [x] testes protegem equivalência, caso temático, disponibilidade e diversidade;
- [x] builds backend, browser e SSR concluídos.

## Continuidade

A evolução vetorial é uma tarefa independente: [Tarefa 5 — Recomendações semânticas com embeddings](tarefa05-recomendacoes-semanticas-embeddings.md).
