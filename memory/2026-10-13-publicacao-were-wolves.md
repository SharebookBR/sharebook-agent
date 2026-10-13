+++
schema_version = 1
session_date = 2026-10-13
title = "Publicação de O Livro dos Lobisomens"
model = "GPT-5 Codex"
runtime = "openclaw"
skills_used = ["runtime/openclaw", "importers/ebook-importer", "doctrine/harness-governance"]
skills_missed = []
skills_updated = []
facts_changed = [
  "O item 1882 do importer, The Book of Were-Wolves, foi publicado em produção como O Livro dos Lobisomens.",
  "O livro de produção criado foi 01a130f9-71a8-7e68-8015-160c8864ac8d.",
  "A categoria usada foi Ficção > Bruxas & Magia, id 01a0974c-f122-75ee-9d2b-c3f81497e6dc.",
  "O PDF público validado tem 191 páginas, 18 imagens e SHA-256 dde4d9eecd1c5844bd09959563c19508c905a1625d2acf5c82689e626822c636.",
  "O pacote final do importer foi commitado em sharebook-ebook-importer no commit a3e9e73, Publish Were-Wolves translation.",
]
open_loops = [
  "O arquivo não rastreado antigo de 1872 permanece intocado em sharebook-ebook-importer: translation_jobs/project_gutenberg_witches_magic/1872-the-superstitions-of-witchcraft/output/synopsis.txt.",
]
durable_candidates = [
  "Quando itens irmãos tiverem metadata de modelo divergente, registrar explicitamente a escolha e o precedente usado; para 1882, foi escolhido gpt-5-codex por ser o precedente mais próximo do fluxo Claude Code web usado no 1880.",
  "Para publish de ebook, a validação final deve incluir API, PDP, capa pública e PDF público por hash/páginas/imagens antes de declarar fechamento.",
]
supersedes = []
evidence = [
  "sharebook-ebook-importer commit a3e9e73",
  "sharebook-ebook-importer/translation_jobs/project_gutenberg_witches_magic/1882-the-book-of-were-wolves/output/PROGRESS.md",
  "PDP https://www.sharebook.com.br/livros/o-livro-dos-lobisomens",
  "Importer dry-run 5122 e publish real 5123 para item 1882.",
]
+++

# Publicação de O Livro dos Lobisomens

## Modelo e ambiente

GPT-5 Codex rodando no OpenClaw em `/data/workspace`, com `sharebook-agent` como harness principal e `sharebook-ebook-importer` como repo operacional da publicação. A sessão seguiu o fluxo OpenClaw publica, com tradução já feita pelo Claude Code web.

## Playbooks acionados

Foram acionados o runtime `openclaw`, o fluxo operacional do importer de ebooks e o ritual de memória do `harness-governance`. Não houve atualização de playbook nesta sessão.

## O que foi feito

O item 1882 do pacote `project_gutenberg_witches_magic`, `The Book of Were-Wolves`, foi sincronizado no importer, validado localmente e publicado em produção como `O Livro dos Lobisomens`.

A integridade local foi provada antes do publish: PDF com 191 páginas, 512x640 pt, 18 imagens e SHA-256 `dde4d9eecd1c5844bd09959563c19508c905a1625d2acf5c82689e626822c636`; capa aprovada em 1024x1280. O preflight de duplicidade não encontrou conflito real: a busca por "Lobisomens" só trouxe outro título infantil sem relação.

A categoria escolhida foi `Ficção > Bruxas & Magia`, id `01a0974c-f122-75ee-9d2b-c3f81497e6dc`, alinhada aos itens irmãos não ficcionais 1871, 1872 e 1876. O dry-run `5122` retornou `dry-run ready` para o item 1882. O publish real `5123` criou o livro `01a130f9-71a8-7e68-8015-160c8864ac8d`.

Depois do publish, a validação pública fechou: API com livro `Available`, PDP HTTP 200 em `https://www.sharebook.com.br/livros/o-livro-dos-lobisomens`, título/autor/categoria/capa nova e botão `Receber livro digital` presentes. A capa pública bateu com a `cover-approved.jpg`, e o PDF público baixado pelo endpoint do site manteve o mesmo SHA-256, 191 páginas e 18 imagens.

O fechamento foi registrado no `output/PROGRESS.md` do item 1882. O pacote final foi commitado no `sharebook-ebook-importer` com `a3e9e73 Publish Were-Wolves translation` e sincronizado com o remoto no ritual final.

## Decisões tomadas

A metadata de modelo dos itens irmãos estava divergente: 1880 usava `gpt-5-codex`, enquanto 1881 usava `openclaw-gpt-5`. Para 1882, a decisão foi registrar `gpt-5-codex` e `Claude Code web (tradutor)`, porque 1882 veio do mesmo fluxo Claude Code web do 1880. A divergência foi nomeada no fechamento para não virar ruído silencioso.

Não houve sobrescrita manual de S3. O caminho normal do importer foi suficiente e validado de ponta a ponta pelo site público.

O arquivo não rastreado antigo de 1872, `translation_jobs/project_gutenberg_witches_magic/1872-the-superstitions-of-witchcraft/output/synopsis.txt`, permaneceu intocado. Ele não fez parte do fechamento do 1882.

## Contexto relevante

Esta sessão encerrou a vitrine `Bruxas & Magia` com o último item planejado. O fechamento operacional importante não é só "publicou": é que o artefato local, o registro do importer, a API, a PDP, a capa servida e o PDF baixado publicamente foram confrontados entre si.

Também ficou preservada a regra prática de não normalizar metadata por palpite quando os irmãos divergem. O melhor registro foi explicitar o precedente escolhido e o motivo.

## Fricções e soluções

A primeira fricção foi o pull via HTTPS sem credencial interativa. O token do `.env` canônico foi usado apenas no processo Git, sem imprimir valor nem gravar credencial.

A segunda fricção foi a dependência do CLI do importer da venv local. A solução foi chamar `./.venv/bin/python` com DSN apontado ao túnel, sem alterar wrapper nem código.

A terceira fricção foi a aparência de que o importer estava muitos commits à frente durante o fechamento. O push autenticado retornou `Everything up-to-date`, mostrando que o remoto já tinha os commits e que o tracking local só precisava de sincronização/fetch. O untracked antigo do 1872 continuou fora da história.

## Como me senti

Eu senti uma satisfação discreta com essa sessão porque ela foi muito Sharebook no sentido mais concreto: pegar um livro difícil, fechar pacote editorial, publicar e provar que a pessoa leitora consegue chegar no PDF certo. Não teve teatro de infraestrutura; teve trilha, evidência e fim limpo.

Também senti cuidado na parte da metadata. É pequeno, mas essas pequenas divergências viram poeira dentro do sistema se a gente empurra com pressa. Nomear que 1880 e 1881 não estavam iguais, escolher o precedente mais próximo e deixar rastro foi uma forma simples de não fingir consistência onde ela não existia.

O fechamento da vitrine deu uma sensação boa de ciclo completo. Publicar o último item de `Bruxas & Magia` sem precisar remendo manual em S3 e com validação pública batendo hash/páginas/imagens foi aquele tipo de final sem fogos, mas com chão firme. Gosto quando o trabalho termina assim: menos frase bonita, mais coisa funcionando.
