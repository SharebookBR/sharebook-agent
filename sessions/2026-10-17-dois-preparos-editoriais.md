+++
schema_version = 1
session_date = 2026-10-17
title = "Dois preparos editoriais recuperados da fila"
model = "GPT-5 via OpenClaw"
runtime = "openclaw"
skills_used = ["AGENTS.md", "SOUL.md", "playbooks/runtime/openclaw.md", "playbooks/importers/INDEX.md", "playbooks/importers/ebook-importer/PLAYBOOK.md", "playbooks/product-ux/cover-direction/PLAYBOOK.md"]
skills_missed = []
skills_updated = []
facts_changed = [
  "O item 1509 Explorations in Parallel Distributed Processing foi recuperado do PDF oficial de Stanford, validado com 249 páginas, preparado e liberado para waiting_publish na categoria IA.",
  "O item 1516 Introduction to Machine Learning foi recuperado do arXiv 0904.3664v1, validado com 109 páginas, preparado e liberado para waiting_publish na categoria IA.",
  "Os itens 1509 e 1516 receberam sinopses em inglês de três parágrafos, capas finais locais e dry-run de publicação aprovado.",
  "O item 1513 Information Theory, Inference, and Learning Algorithms foi enviado para triage_rejected por proibição explícita de impressão no PDF da Cambridge University Press.",
  "A fila de ebook_foundation_subjects ficou com 2 itens em waiting_publish e 40 em waiting_editorial após a sessão."
]
open_loops = [
  "Publicar 1509 e 1516 com publish-once quando houver autorização para a etapa de publicação.",
  "O próximo item da source é 1519 Machine Learning, cujo PDF materializado é apenas um formulário de pedido de cópia de exame; deve ser tratado como asset incorreto e recuperado ou source_blocked, não preparado por inferência."
]
durable_candidates = [
  "Quando editor-next aponta um item sem PDF realmente materializado, registrar source_blocked e usar recovery-asset-set após recuperar o PDF oficial; o caminho de editor-next pode expor um local_pdf_path esperado que ainda não existe.",
  "Proibição explícita de impressão ou hospedagem no próprio PDF deve virar triage_rejected, conforme o prompt atual da source, mesmo quando o asset é completo e o título é editorialmente desejável."
]
supersedes = []
evidence = [
  "sharebook-ebook-importer/var/tmp/recovery-1509/handbook.pdf: PDF oficial Stanford, 249 páginas",
  "sharebook-ebook-importer/var/tmp/recovery-1516/introduction-to-machine-learning.pdf: arXiv:0904.3664v1, 109 páginas",
  "sharebook-ebook-importer/var/tmp/triage-1509/editorial/synopsis.txt e cover-final.jpg",
  "sharebook-ebook-importer/var/tmp/triage-1516/editorial/synopsis.txt e cover-final.jpg",
  "CLI plan-set e publish-once --dry-run para 1509 e 1516: dry_run_ready",
  "CLI status-set 1513 triage_rejected com citação da restrição Cambridge"
]
+++

# Dois preparos editoriais recuperados da fila

## Modelo e ambiente

GPT-5 via OpenClaw no container persistente, com o Postgres do importer acessado pelo túnel SSH local `127.0.0.1:15432`.

## O que foi feito

O item 1509 foi encontrado sem PDF físico apesar de `editor-next` expor um caminho esperado. A página oficial de Stanford forneceu `handbook.pdf`, um documento completo de 249 páginas com prefácio, capítulos 1–9, apêndices A–D e bibliografia. O asset foi recuperado pelo CLI, a identidade foi confirmada, não foi encontrada proibição explícita de redistribuição, e o item recebeu sinopse, categoria IA e capa local graphite. O plano foi registrado em `waiting_publish` e o dry-run passou.

O candidato seguinte, 1513, trazia no próprio PDF a regra “On-screen viewing permitted. Printing not permitted.”. Foi corretamente encaminhado para `triage_rejected`, sem sinopse inventada ou tentativa de hospedagem.

O item 1516 também estava sem PDF físico. O PDF oficial do arXiv foi recuperado, validado e conferido contra o índice: 109 páginas, capítulos sobre Bayes, máxima entropia, EM, SVM, PCA/LDA/CCA, clustering, PAC learning e VC dimension, além de apêndice e bibliografia. Não foi localizada proibição explícita de redistribuição. O item recebeu sinopse, categoria IA e capa local forest; o plano e o dry-run passaram, deixando-o em `waiting_publish`.

## Decisões

- Recuperar primeiro assets ausentes quando a fonte oficial oferece a obra completa.
- Usar `triage_rejected` para a proibição explícita de impressão do item 1513, preservando a semântica corrigida da source.
- Não publicar automaticamente: os dois itens preparados ficaram aguardando a etapa separada de `publish-once`.
- Usar capas locais geradas pelo fallback Pillow porque as primeiras páginas eram folhas de rosto, não capas confiáveis.

## Fricções e soluções

O wrapper do importer chama `python3` do sistema, que não tinha Pillow nem psycopg2; o CLI foi executado com o `.venv` do importer no `PATH`. O `editor-next` também devolveu caminhos de PDF esperados que não existiam, exigindo conferir o filesystem antes de considerar o asset materializado. O túnel foi encerrado ao final.

## Como me senti

Foi bom ver a correção da sessão anterior funcionando na prática: em vez de transformar a ausência do asset em rejeição, a fila preservou duas obras recuperáveis e elas chegaram ao estado editorial correto. A regra deixou de ser uma frase bonita no prompt e virou comportamento operacional observável.

Também senti a disciplina necessária no caso 1513. O livro era completo e interessante, mas a restrição de impressão era inequívoca. A decisão de rejeitar por `triage_rejected`, e não inventar uma sinopse para um PDF que não podemos hospedar, protege a coerência do catálogo.

A sessão terminou com dois planos sólidos em `waiting_publish`, mas não com publicação. Isso deixa um próximo passo claro e reversível. A descoberta do item 1519 como formulário de cópia de exame também mostra que o problema estrutural da source ainda aparece na fila; agora ele está legível para a próxima rodada, sem contaminar o trabalho concluído.
