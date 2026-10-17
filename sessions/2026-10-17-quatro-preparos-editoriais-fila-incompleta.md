+++
schema_version = 1
session_date = 2026-10-17
title = "Quatro preparos editoriais: quatro assets incompletos na fila"
model = "GPT-5 via OpenClaw"
runtime = "openclaw"
skills_used = ["AGENTS.md", "SOUL.md", "playbooks/runtime/openclaw.md", "playbooks/importers/INDEX.md", "playbooks/importers/ebook-importer/PLAYBOOK.md", "playbooks/product-ux/cover-direction/PLAYBOOK.md"]
skills_missed = []
skills_updated = []
facts_changed = [
  "Os itens 1448, 1453, 1457 e 1505 foram rejeitados editorialmente como structurally_incomplete, com evidência específica registrada no CLI.",
  "A fila passou de 47 para 43 itens em waiting_editorial e de 8 para 12 em editorial_rejected.",
  "O item 1509 foi deixado intacto em waiting_editorial porque o texto extraído sugere uma obra válida, mas o PDF local não está materializado no runtime atual."
]
open_loops = [
  "Investigar a materialização da source ebook_foundation_subjects: vários itens entregaram prefácio, capítulo isolado ou índice+bibliografia em vez do PDF completo.",
  "Rematerializar o PDF do item 1509 antes de qualquer plan-set; não liberar sem artefato físico e capa final verificáveis.",
  "O túnel SSH do Postgres ficou ativo na sessão e deve ser encerrado quando não for mais necessário."
]
durable_candidates = [
  "Antes de escrever sinopse para ebook_foundation_subjects, conferir páginas totais e a transição entre índice, corpo e bibliografia; TOC plausível sozinho não prova que o corpo foi materializado.",
  "Não transformar ausência de PDF local em rejeição editorial quando o contexto extraído sustenta uma obra potencialmente válida; deixar para rematerialização técnica."
]
supersedes = []
evidence = [
  "sharebook-ebook-importer/cli.sh editorial-reject --id 1448|1453|1457|1505",
  "sharebook-ebook-importer/var/tmp/triage-1448/source.pdf: 5 páginas, somente prefácio",
  "sharebook-ebook-importer/var/tmp/triage-1453/source.pdf: 10 páginas, capítulo isolado",
  "sharebook-ebook-importer/var/tmp/triage-1457/source.pdf: 3 páginas, somente prefácio",
  "sharebook-ebook-importer/var/tmp/triage-1505/source.pdf: 66 páginas, índice seguido de bibliografia"
]
+++

# Quatro preparos editoriais: quatro assets incompletos na fila

## Modelo e ambiente

GPT-5 via OpenClaw, container persistente em `/data/workspace`, com o CLI do importer operando pelo túnel SSH local `127.0.0.1:15432`.

## O que foi feito

Consultei a fila pelo CLI oficial e examinei os quatro primeiros itens da source `ebook_foundation_subjects`. O item 1448 era somente um prefácio de cinco páginas; 1453 era um capítulo isolado de dez páginas; 1457 era somente o prefácio de três páginas; e 1505 continha índice e bibliografia, mas nenhum capítulo. Registrei todos como `editorial_rejected` com motivo `structurally_incomplete` e evidência no motivo humano.

O próximo item, 1509, parece uma obra real pelo índice extraído, mas não possui `source.pdf` materializado no runtime. Não o aprovei nem o rejeitei: ficou aguardando rematerialização.

## Decisões

A fila foi tratada como fonte operacional, não como convite para completar lacunas por inferência. Um índice convincente não basta quando o PDF entregue não contém a obra; e falta técnica de asset não deve ser mascarada como rejeição curatorial.

## Fricções e soluções

O wrapper inicialmente chamou o Python do sistema, que não tinha Pillow nem psycopg2. O repositório já possuía `.venv`; o CLI foi executado com esse ambiente no `PATH`. O túnel do Postgres também estava parado e foi iniciado pelo script canônico, sem conexão direta ao banco.

## Como me senti

A sessão começou com a expectativa simples de preparar quatro itens e rapidamente revelou um problema mais estrutural: a source está entregando recortes de PDFs como se fossem livros completos. Foi importante não deixar a quantidade pedida empurrar uma sinopse inventada.

Senti uma clareza incômoda ao rejeitar os quatro casos. As decisões são pouco glamorosas, mas são exatamente o tipo de higiene editorial que impede o catálogo de acumular arquivos quebrados e descrições falsas.

Fiquei com a pendência técnica do item 1509, que parece aproveitável e por isso merece recuperação, não descarte. O estado ficou legível para a próxima sessão: quatro rejeições fundamentadas e um candidato preservado para rematerialização.
