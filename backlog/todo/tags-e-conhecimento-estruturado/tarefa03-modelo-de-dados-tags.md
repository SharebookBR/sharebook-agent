# Tarefa 3 — Modelo de dados para tags

## Status

Pendente.

## Objetivo

Persistir tags por identidade estável, evitando texto duplicado e preparando navegação, busca, recomendações e backfill.

## Escopo

- modelar entidade de tag com slug, nome público e estado;
- modelar relação entre ebook e tag;
- garantir limite de até três tags públicas por livro;
- preservar trilha de revisão quando fizer sentido;
- definir comportamento para tags renomeadas ou inativas.

## Critérios de pronto

- schema discutido antes de migration;
- identidade estável, não texto solto;
- regra de limite protegida no backend;
- contratos admin e públicos desenhados;
- testes cobrindo regras principais.
