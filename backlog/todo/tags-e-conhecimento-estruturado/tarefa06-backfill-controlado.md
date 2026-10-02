# Tarefa 6 — Backfill controlado do catálogo técnico

## Status

Em execução.

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

## Plano do primeiro lote

- gerar dry-run dos ebooks técnicos atuais com tags sugeridas, confiança e racional;
- aplicar primeiro apenas associações de alta confiança;
- limitar a primeira execução a um lote pequeno/médio e auditável;
- registrar cobertura, tags ativadas e casos ambíguos para revisão.

## Execução 2026-10-02 — primeiro lote

Script criado:

- `scripts/production/backfill_technical_tags.py`

Características:

- dry-run por padrão;
- aplica somente com `--apply`;
- limita o lote com `--limit`;
- restringe o escopo à categoria `Tecnologia` e suas filhas;
- pula livros que já possuem tags;
- usa regras explícitas de alta confiança em título/sinopse;
- grava relatório JSON em `var/reports/` (ignorado pelo Git).

Resultado aplicado em produção:

- candidatos técnicos: 274 ebooks disponíveis;
- livros já tagueados e preservados: 5;
- primeiro lote aplicado: 50 livros;
- tags públicas com pelo menos 1 livro após o lote: 33 de 57.

Exemplos verificados:

- `algoritmos`: 11 livros;
- `machine-learning`: 8 livros;
- `estruturas-de-dados`: 7 livros;
- `bancos-de-dados`: 5 livros;
- `python`: 5 livros;
- `kubernetes`: 3 livros.

Correção feita durante o dry-run:

- `Ray Tracing Gems` expôs falso positivo de `observabilidade` por causa de `tracing`. A regra foi ajustada para exigir `distributed tracing`, evitando confundir observabilidade com `ray tracing`.

Próximo lote:

- o dry-run posterior ao apply passou a pular 55 livros já tagueados e encontrou 82 sugestões restantes;
- revisar/aplicar novo lote só depois de avaliar se tags de uma única evidência forte ainda estão boas para a próxima passada.
