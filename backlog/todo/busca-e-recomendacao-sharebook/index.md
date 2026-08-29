# Épico — Busca e recomendação do Sharebook

## Estado

- **Status:** em andamento, estacionado entre fatias
- **Prioridade:** fatiada no backlog; tarefa 3 em 4º e tarefa 4 em 8º
- **Valor:** altíssimo
- **Marco atual:** busca lexical publicada e validada
- **Próxima tarefa:** [Tarefa 3 — Tolerância a erro com trigram e fallback fuzzy](tarefa03-tolerancia-a-erro.md)
- **Critério de retomada:** buscas sem resultado e termos reais indicarem que typos estão custando descoberta

## Objetivo

Evoluir a descoberta de livros sem misturar problemas diferentes nem cair em overengineering.

O épico tem dois pilares:

1. melhorar a busca principal para consultas digitadas;
2. criar recomendações inteligentes na PDP para descoberta contextual.

A ordem importa. Primeiro a busca pública precisa ser correta. Depois ganha relevância lexical e tolerância a erro. Só então entram recomendações semânticas com embeddings.

## Tarefas

| # | Tarefa | Status | Depende de | Resultado |
|---|---|---|---|---|
| 1 | [Disponibilidade pública canônica](tarefa01-disponibilidade-publica.md) | **Concluída** em 2026-08-28 | — | Público recebe somente `Available`; admin preserva escopo ampliado. |
| 2 | [Busca textual com Full-Text Search](tarefa02-busca-textual-fts.md) | **Concluída** em 2026-08-29 | 1 | Busca lexical ranqueada, normalizada e validada em 40 consultas reais. |
| 3 | [Tolerância a erro com trigram e fallback fuzzy](tarefa03-tolerancia-a-erro.md) | **Pendente** | 2 | Typos e pequenas variações deixam de produzir falso zero. |
| 4 | [Recomendações semânticas na PDP](tarefa04-recomendacoes-semanticas-pdp.md) | **Pendente** | 2 e 3 | Livros parecidos por significado usando embeddings e `pgvector`. |
| 5 | [Re-ranking com popularidade](tarefa05-reranking-popularidade.md) | **Horizonte v2** | 4 + evidência de uso | Similaridade recebe sinal moderado de tração real. |
| 6 | [Personalização por usuário](tarefa06-personalizacao.md) | **Horizonte v2** | 4 + sinais confiáveis | Recomendações combinam contexto do livro e gosto do usuário. |

## Fronteira da v1

A v1 deste épico termina quando as tarefas 1–4 estiverem concluídas e validadas:

1. busca pública consistente;
2. busca textual relevante com FTS;
3. tolerância mínima a erro com trigram;
4. recomendação semântica funcional na PDP.

As tarefas 5 e 6 são evoluções condicionadas a evidência. Elas não mantêm a v1 artificialmente aberta.

## Arquitetura conceitual

### Busca principal

- correspondência exata e prefixo para intenção explícita;
- PostgreSQL Full-Text Search para palavras, pesos e ranking;
- `pg_trgm` como fallback controlado para erro de digitação;
- filtros explícitos para formato, categoria e outros atributos estruturados.

### Recomendação na PDP

- embeddings para representar significado editorial;
- `pgvector` para encontrar livros semanticamente próximos;
- processamento offline na criação ou alteração relevante do livro;
- somente livros `Available` entre os candidatos.

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
