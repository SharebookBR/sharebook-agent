# Tarefa 6 — Backfill controlado do catálogo técnico

## Status

Pendente.

## Objetivo

Preencher tags do catálogo técnico atual de forma idempotente, revisável e sem gerar taxonomia acidental.

## Escopo

- selecionar primeiro recorte técnico do catálogo;
- gerar sugestões em lote com vocabulário controlado;
- revisar antes de publicar;
- tornar execução retomável e auditável;
- medir cobertura e principais lacunas do vocabulário.

## Critérios de pronto

- backfill é idempotente;
- lote pode ser interrompido e retomado;
- revisão editorial acontece antes de publicar;
- cobertura e rejeições são registradas;
- nenhum domínio fora do recorte técnico é afetado sem decisão explícita.
