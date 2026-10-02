# Tarefa 6 — Backfill controlado do catálogo técnico

## Status

Fechada para avanço.

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

## Execução 2026-10-02 — completion editorial para 100%

Raffa delegou avanço com autonomia para chegar o mais perto possível de 100% sem depender de revisão micro. A rodada anterior tinha parado corretamente em 49,6% de cobertura porque a régua de alta confiança havia zerado; para completar a cobertura, foi criada uma fase separada de completion editorial, não uma flexibilização silenciosa do backfill original.

Scripts criados:

- `scripts/production/complete_technical_tags.py`
- `scripts/production/refine_technical_tag_overrides.py`

Características:

- cria lacunas reais de vocabulário técnico antes de taguear;
- aplica apenas em ebooks técnicos ainda sem tags, preservando curadoria anterior;
- usa fallback editorial por categoria só quando não há evidência específica melhor;
- grava relatórios em `var/reports/`;
- inclui uma passada posterior de overrides explícitos para corrigir casos em que o fallback ficou correto, mas pobre.

Lacunas de vocabulário adicionadas nesta rodada incluem:

- `Inteligência Artificial`, `IA Generativa`, `Prompt Engineering`, `Processamento de Linguagem Natural`, `Aprendizado por Reforço`, `MLOps`;
- `Programação Funcional`, `Programação Orientada a Objetos`, `Métodos Formais`, `Concorrência`, `Engenharia de Software`;
- `Computação Quântica`, `Fundamentos da Computação`, `Pensamento Computacional`, `Lógica`, `Circuitos Digitais`;
- `Realidade Virtual`, `Processamento de Imagens`, `Editores de Texto`, `Escrita Técnica`;
- `Software Livre`, `Gestão de Tecnologia`, `Internet das Coisas`, `Sistemas Embarcados`, `Blockchain`, `Criptomoedas`;
- linguagens/ferramentas específicas que apareceram no acervo: `Bash`, `Lisp`, `LaTeX`, `Pascal`, `Julia`, `Fortran`, `Assembly`, `Small Basic`, `Tkinter`, `Yii`.

Validação final em produção:

- candidatos técnicos: 274 ebooks disponíveis;
- livros técnicos com pelo menos 1 tag: 274;
- livros técnicos sem tag: 0;
- cobertura: 100,0%;
- tags públicas com livros: 91 de 100;
- dry-run posterior: 0 sugestões restantes, 274 livros pulados por já estarem tagueados.

Tags mais frequentes após a completion:

- `fundamentos-da-computacao`: 48 livros;
- `backend`: 32;
- `algoritmos`: 26;
- `inteligencia-artificial`: 25;
- `machine-learning`: 17;
- `devops`: 17;
- `data-science`: 14;
- `estruturas-de-dados`: 13;
- `python`: 10.

Observação editorial:

- 100% aqui significa cobertura útil mínima para a navegação pública. Não significa que cada livro recebeu sua classificação ideal definitiva. A Tarefa 5 deve impedir a volta do problema: novos livros precisam nascer com sugestão assistida de tags no fluxo editorial, em vez de exigir novo backfill depois.
