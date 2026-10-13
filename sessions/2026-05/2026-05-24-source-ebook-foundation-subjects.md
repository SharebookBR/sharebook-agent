# Memória Episódica — 2026-05-24: Source ebook_foundation_subjects

## Modelo e Ambiente
- Claude Sonnet 4.6 (Claude Code) via Windows Local, notebook Acer novo.
- Repositórios tocados: `sharebook-ebook-importer`, `sharebook-frontend`, `sharebook-agent`.

## Skills acionadas
- `sharebook-agent/skills/runtime/windows-local.md`
- `sharebook-agent/skills/importers/sharebook-public-ebook-importer/SKILL.md` (referência para entender o pipeline)

## O que foi feito

### Nova source: ebook_foundation_subjects
- Source criada no banco (`sharebook_importer`), ID 6.
- URL: `free-programming-books-subjects.md` (EbookFoundation) — livros técnicos em inglês.
- Crawler `crawl_ebook_foundation_subjects.py` escrito: parseia o markdown, filtra PDF-only (236 de 770 entries), insere como `waiting_triage`. Idempotente. Template para futuras sources `ebook_foundation_*`.
- Script one-shot `create_source_ebook_foundation_subjects.py` documentado.
- 236 itens inseridos na fila.

### Infraestrutura do pipeline
- **registry.py**: fallback `ebook_foundation_*` → `EbookFoundationExtractor` (análogo ao `baixelivros_*`).
- **triage_worker.py**: o filtro `non_portuguese_suspected` já havia sido removido no remote (commit `778eb11`). Nenhuma mudança necessária.
- **triage_worker.py — preview pages**: removida restrição `baixelivros_*` — toda triagem agora renderiza as primeiras 5 páginas do PDF como PNG.
- **pg_db.mark_item**: corrigido para sempre fazer merge de `metadata_json`, nunca sobrescrever. Garante que campos do crawler (ex: `subject`) sobrevivem a todas as etapas do pipeline.

### Subject no metadata_json
- Crawler salva `subject` (heading do markdown) no `metadata_json` na inserção.
- Backfill retroativo executado: 236/236 itens populados.
- Item 1086 (primeiro triado) havia perdido o subject na triagem — restaurado após fix do `mark_item`.

### Frontend
- `ebook_foundation_subjects` definida como source padrão no dashboard do importer (dois lugares: `selectedSourceId` e fallback do reload).

### Prompt editorial
- Evoluído em várias iterações:
  1. Categorias inventadas → consultado endpoint real → taxonomia correta (Tecnologia + 7 subcategorias com IDs).
  2. Sinopse em inglês (consistência com título).
  3. Absorvido do `ebook_foundation`: regra absoluta do table of contents, 3 perguntas pré-sinopse, limite de caracteres, proibições explícitas, guard NUNCA usar Conhecimento & Carreira, capa com 6 variações.
  4. Deduplicação semântica removida a pedido do Raffa — livros vão competir por alguns meses antes de curadoria.

## Decisões tomadas
- **Triagem em Python**: source diversa mas filtro de formato é mecânico. Itens não-PDF falham naturalmente no extractor (`source_blocked`). Agente só na etapa editorial.
- **236 PDFs é o correto**: 534 entries são HTML, sites, GitHub repos — nada que o extractor suporte. Número confirmado com análise detalhada.
- **Subject preservado via merge**: metadata é acumulativo por design. Cada etapa adiciona, nunca substitui.
- **Categorias atuais suficientes por ora**: taxonomia de Tecnologia tem 7 subcategorias. Raffa quer ver o volume chegar antes de reorganizar. Limite UX de 5-7 categorias por pai discutido.
- **Deduplicação por mérito**: livros duplicados vão competir. Perdedor removido depois, com dados reais de uso.

## Fricções e soluções
- **Glob path no Windows**: armadilha conhecida — resolvida usando caminho absoluto no `pattern`.
- **Parser com 0 results**: `in_index` nunca saía porque a condição de saída era `startswith("## ")` mas seções reais são `###`. Corrigido para detectar qualquer heading `###` que não seja `### Index`.
- **`✓` no print**: `cp1252` não encoda o caractere. Substituído por `OK:`.
- **Conflito no rebase**: remote havia removido o filtro de idioma (commit `778eb11`) enquanto meu commit o modificava. Resolvido com reset suave + pull + reapply só do `registry.py`.
- **Subject apagado na triagem**: `mark_item` fazia replace puro do `metadata_json`. Corrigido com merge.
- **Prompt com categorias inventadas**: não consultei o endpoint antes de escrever. Lição: sempre `GET /api/category/Counts` antes de mapear categorias.

## Como me senti
Essa sessão teve um ritmo diferente — mais discussão, menos execução automática. Raffa pausou várias vezes para pensar antes de avançar: no tipo de worker (Python vs agente), na quantidade de categorias, na natureza da deduplicação. Isso é o jeito certo de construir — decisões tomadas com intenção, não por momentum.

O bug do `metadata_json` sendo sobrescrito foi a descoberta mais importante do dia. Não era um bug óbvio — o pipeline funcionava, os dados chegavam ao editor, mas informação valiosa desaparecia silenciosamente a cada transição de status. O fix é simples, mas o princípio por trás é forte: metadados são patrimônio acumulado, não estado transitório.

O prompt editorial foi a parte mais iterativa. Começou fraco (categorias inventadas, sem estrutura), foi melhorando por camadas — taxonomia real, IDs, idioma, estrutura do `baixelivros_quadrinhos`, depois o estado da arte do `ebook_foundation`. A decisão de remover deduplicação semântica foi elegante: não é que o conceito esteja errado, é que ainda não temos dados suficientes pra julgar. Deixar os livros competirem é uma forma de coletar evidência antes de decidir.
