# Tarefa 6 — Re-ranking com popularidade

## Status

**Horizonte v2. Só ativar após a Tarefa 5 produzir uso observável.**

## Objetivo

Adicionar um sinal moderado de tração real às recomendações sem destruir a coerência semântica.

## Sinais candidatos

- visualizações da PDP;
- downloads;
- solicitações;
- avaliações e nota média;
- recência, se houver hipótese clara.

## Estratégia inicial

1. buscar candidatos por similaridade semântica;
2. separar um conjunto pequeno, como top 20;
3. reordenar moderadamente com um sinal de popularidade;
4. devolver o top final.

Popularidade não deve transformar recomendação em ranking geral dos mesmos livros de sempre.

## Pré-condições

- recomendação semântica da PDP validada;
- eventos e métricas confiáveis;
- volume suficiente para distinguir tração de ruído;
- hipótese de produto explícita.

## Critérios de pronto

- coerência semântica permanece forte;
- livros com tração legítima ganham algum destaque;
- cauda relevante não desaparece;
- regra de re-ranking é explicável e reversível;
- ganho é demonstrado por métrica de navegação ou conversão.
