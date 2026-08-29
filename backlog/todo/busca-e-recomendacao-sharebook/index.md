# Épico — Busca e recomendação do Sharebook

## Estado

- **Status:** em andamento, com núcleo e recomendação pragmática publicados
- **Prioridade:** fatiada no backlog; tarefa 3 em 4º e tarefa 5 em 8º
- **Valor:** altíssimo
- **Marco atual:** busca lexical e recomendações pragmáticas na PDP publicadas e validadas
- **Próxima tarefa:** [Tarefa 3 — Tolerância a erro](tarefa03-tolerancia-a-erro.md) ou [Tarefa 5 — Recomendações semânticas com embeddings](tarefa05-recomendacoes-semanticas-embeddings.md), conforme evidência
- **Critério de retomada:** buscas sem resultado mostrarem custo real de typos ou recomendações lexicais mostrarem limite editorial recorrente

## Objetivo

Evoluir a descoberta de livros sem misturar problemas diferentes nem cair em overengineering.

O épico tem dois pilares:

1. melhorar a busca principal para consultas digitadas;
2. criar recomendações inteligentes na PDP para descoberta contextual.

A ordem importa. Primeiro a busca pública precisa ser correta. Depois ganha relevância lexical. Recomendações pragmáticas podem usar os dados editoriais já existentes; tolerância a erro e embeddings entram apenas quando seus custos resolverem problemas observados.

## Tarefas

| # | Tarefa | Status | Depende de | Resultado |
|---|---|---|---|---|
| 1 | [Disponibilidade pública canônica](tarefa01-disponibilidade-publica.md) | **Concluída** em 2026-08-28 | — | Público recebe somente `Available`; admin preserva escopo ampliado. |
| 2 | [Busca textual com Full-Text Search](tarefa02-busca-textual-fts.md) | **Concluída** em 2026-08-29 | 1 | Busca lexical ranqueada, normalizada e validada em 40 consultas reais. |
| 3 | [Tolerância a erro com trigram e fallback fuzzy](tarefa03-tolerancia-a-erro.md) | **Pendente** | 2 | Typos e pequenas variações deixam de produzir falso zero. |
| 4 | [Recomendações pragmáticas na PDP](tarefa04-recomendacoes-pragmaticas-pdp.md) | **Concluída** em 2026-08-29 | 2 | Seis livros disponíveis por obra, tema e metadados, com navegação e analytics publicados. |
| 5 | [Recomendações semânticas com embeddings](tarefa05-recomendacoes-semanticas-embeddings.md) | **Pendente** | 4 + evidência de limite lexical | Similaridade vetorial aproxima livros por significado editorial. |
| 6 | [Re-ranking com popularidade](tarefa06-reranking-popularidade.md) | **Horizonte v2** | 5 + evidência de uso | Similaridade recebe sinal moderado de tração real. |
| 7 | [Personalização por usuário](tarefa07-personalizacao.md) | **Horizonte v2** | 5 + sinais confiáveis | Recomendações combinam contexto do livro e gosto do usuário. |

## Fronteira da v1

A v1 de valor do épico está entregue com:

1. busca pública consistente;
2. busca textual relevante com FTS;
3. recomendação contextual funcional na PDP.

Tolerância a erro, embeddings, popularidade e personalização são evoluções condicionadas a evidência. Elas não mantêm a v1 artificialmente aberta.

## Arquitetura conceitual

### Busca principal

- correspondência exata e prefixo para intenção explícita;
- PostgreSQL Full-Text Search para palavras, pesos e ranking;
- `pg_trgm` como fallback controlado para erro de digitação;
- filtros explícitos para formato, categoria e outros atributos estruturados.

### Recomendação na PDP

- primeira camada pragmática com obra equivalente, autor, categoria, título e sinopse;
- TF-IDF lexical em memória para diminuir o peso de termos genéricos;
- relevância antes da diversidade, com limites para repetição de obra, autor e categoria;
- somente livros `Available` entre os candidatos.

Na evolução semântica:

- embeddings representam significado editorial além do vocabulário compartilhado;
- `pgvector` encontra livros semanticamente próximos;
- processamento ocorre offline na criação ou alteração relevante do livro.

Busca principal e recomendação na PDP são irmãs, não gêmeas. Misturá-las cedo demais piora precisão e torna o sistema difícil de explicar.

## Capacidade atual

A VPS possui 4 vCPU e 16 GB de RAM. Em 2026-08-28, o catálogo tinha 2.734 livros, dos quais 1.078 estavam disponíveis. Nessa escala:

- FTS, `pg_trgm` e `pgvector` cabem com folga;
- relevância é mais importante que performance bruta;
- não há justificativa para Elasticsearch, pipeline em tempo real ou arquitetura distribuída.

## Métricas do épico

### Busca

- aderência dos primeiros resultados;
- taxa de clique nos resultados e posição clicada;
- buscas sem resultado;
- uso de fallback fuzzy;
- latência percebida.

### Recomendações

- cliques em livros recomendados;
- navegação entre PDPs;
- downloads iniciados após recomendação;
- coerência editorial em amostra revisada.

## Princípios

- medir qualidade contra consultas reais antes de sofisticar;
- correspondência exata nunca perde para aproximação;
- sinopse enriquece o ranking, não o domina;
- fuzzy é fallback, não ruído permanente;
- embedding é gerado offline, nunca durante a leitura da PDP;
- personalização só entra quando existirem sinais confiáveis;
- nenhuma etapa pode esconder regra de disponibilidade no frontend.

## Fora de escopo agora

- transformar toda a busca principal em busca semântica;
- recalcular embeddings por acesso;
- personalizar antes de validar recomendação simples;
- somar scores lexical e vetorial sem calibração;
- usar sinopse ou fuzzy de forma indiscriminada;
- criar infraestrutura maior que o problema.
