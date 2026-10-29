# Família de Playbooks — Importers e Curadoria Operacional

Fluxos de ingestão, triagem, preparo editorial, tradução, PDFs, categorias e publicação no catálogo.

## Playbooks

- `./ebook-importer/PLAYBOOK.md` — **Porta única da fila de importação**: workflow, statuses, CLI, hardening, ciclo manual Windows, `triage_retry`, `publish_retry`, `error`, `source_blocked`, handoff editorial e doutrina de `editorial_rejected`.
- `./sharebook-pdf-typesetting/PLAYBOOK.md` — Baseline editorial de miolo PDF Sharebook em 4:5; leitura obrigatória para preparo editorial de sources Project Gutenberg com tradução e PDF final.
- `./illustrated-edition/PLAYBOOK.md` — Edição ilustrada de livro traduzido: uma prancha por capítulo gerada por IA de imagem, escolha de cenas delegada ao agente, prompts um de cada vez, lobo de referência, legenda "criado com IA", assets no job e PDF com pranchas.
- `./daily-triage-recovery/PLAYBOOK.md` — Recorte diário da triagem: analisar itens processados hoje, recuperar `source_blocked`, decidir rejeição limpa, rejeição editorial posterior ou hardening.
- `./physical-book-importer/PLAYBOOK.md` — Cadastro, doação, importação e validação de livros físicos em produção.
- `./category-organizer/PLAYBOOK.md` — Gestão, taxonomia e hierarquia de categorias.
- `./escrever-livros/PLAYBOOK.md` — Produção editorial de Originals, manuscritos, PDFs, capas autorais e assets de obras novas. Inclui a linha **Vida Real** (livros de divulgação/não ficção): página de posição, verificação de fontes (Crossref/PubMed), `references.md`, `revisao-factual`, sinopse em modo clique e as lições de escrita (definir uma vez, ajuda profissional em um lugar só, sem meta-hedges). Também: leitura obrigatória antes de escrever, autonomia, posição editorial, PDF v1 com a página institucional canônica de Originals. Teste da versão confiante (revisão). Termos: Vida Real, não ficção, divulgação científica, manuscrito, referências, burnout, saúde, tom, medo de se posicionar.

## Uso

- Ler quando a tarefa envolver fila, triagem, preparo editorial, tradução, Project Gutenberg, publicação, categorias, taxonomia, livro físico, doação física, frete, Originals, manuscritos, PDF ou produção de ativos do catálogo.
- Quando a tarefa também decidir quais títulos, sources ou categorias merecem prioridade, ler antes `../product-ux/catalog-strategy/PLAYBOOK.md`.
- Para qualquer coisa relacionada à fila de importação de ebooks: abrir `./ebook-importer/PLAYBOOK.md` — ela contém tudo.
- Para preparo editorial de source Project Gutenberg com tradução/PDF final, abrir também `./sharebook-pdf-typesetting/PLAYBOOK.md` antes de validar ou gerar o PDF.
- Para tradução pesada de livro (job offline em `translation_jobs/`, subagentes, glossário, `check_chapters.py`, montagem do `translated.md`): ler `../runtime/claude-code-web.md`, seções `Importer: sem Postgres, trabalho via job offline` e `Tradução pesada offline: armadilhas confirmadas no job 1873`. Termos de descoberta: traduzir livro, tradução, bruxa, subagentes, glossário, verificador, travessão, reticências, licença do Gutenberg.
- Para ilustrar um livro (prancha por capítulo, prompt para IA de imagem, edição ilustrada, gravura, xilogravura, legenda de IA): `./illustrated-edition/PLAYBOOK.md`. Termos de descoberta: ilustração por capítulo, prancha, plate, IA de imagem, lobo estranho, edição ilustrada.
