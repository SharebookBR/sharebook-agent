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

## Execução 2026-10-02 — lotes 2 e 3

Raffa delegou avanço sem microaprovação. Foram aplicados mais dois lotes após revisão de dry-run:

- lote 2: 50 livros;
- lote 3: 31 livros;
- total aplicado pela Tarefa 6 até aqui: 131 livros, além dos 5 livros do ciclo manual.

Correções de regra durante os lotes:

- `Subversion Version Control` expôs falso positivo de `Git` por causa de `version control`. A regra foi ajustada para exigir `git` ou `github` explícito no backfill.

Resultado final da rodada:

- candidatos técnicos: 274 ebooks disponíveis;
- livros técnicos já tagueados: 136;
- sugestões restantes de alta confiança: 0;
- tags públicas com pelo menos 1 livro: 42 de 57;
- tags ainda sem livros: 15.

Principais páginas fortalecidas:

- `algoritmos`: 18 livros;
- `machine-learning`: 17 livros;
- `estruturas-de-dados`: 10 livros;
- `python`: 10 livros;
- `bancos-de-dados`: 7 livros;
- `linux`: 7 livros;
- `seguranca`: 6 livros;
- `git`: 5 livros;
- `java`: 5 livros;
- `docker`: 3 livros;
- `kubernetes`: 3 livros.

Decisão operacional:

- parar o backfill automático nesta rodada. O próximo avanço no acervo atual exigiria heurísticas mais fracas ou revisão editorial livro a livro;
- seguir para Tarefa 5, sugestão assistida no importer, para novos livros já nascerem com tags sugeridas dentro do fluxo editorial.
