+++
schema_version = 1
session_date = 2026-10-04
title = "Living Alone publicado e regra editorial contra higienização textual"
model = "GPT-5 Codex"
runtime = "openclaw"
skills_used = [
  "skills/runtime/openclaw.md",
  "skills/importers/INDEX.md",
  "skills/importers/ebook-importer/SKILL.md",
  "skills/sharebook-pdf-typesetting/SKILL.md",
  "skills/doctrine/harness-governance/SKILL.md"
]
skills_missed = []
skills_updated = [
  "Skill Workshop proposal: sharebook-preservacao-linguagem-epoca-20261004-9febe0d72f"
]
facts_changed = [
  "Importer item 1873, Black Magic, foi traduzido, diagramado e publicado como Magia negra: a ascensão e queda do Anticristo.",
  "Importer item 1874, Living Alone, foi traduzido por Claude Code web, fechado pelo OpenClaw e publicado como Vivendo sozinha.",
  "Raffa decidiu manter a ordem da fila mesmo havendo edição brasileira comercial de Living Alone; a tradução Sharebook partiu do Gutenberg sem consultar/reaproveitar a edição comercial.",
  "Raffa explicitou preferência editorial: censura/higienização de linguagem de época é o pior cenário; preservar o texto literário é a regra."
]
open_loops = [
  "Aplicar ou incorporar de forma definitiva a proposta pendente sharebook-preservacao-linguagem-epoca-20261004-9febe0d72f em skill/playbook adequado.",
  "Arquivo não rastreado antigo permanece intocado em sharebook-ebook-importer/translation_jobs/project_gutenberg_witches_magic/1872-the-superstitions-of-witchcraft/output/synopsis.txt."
]
durable_candidates = [
  "Claude Code web deve ficar com a tradução pesada em job offline; OpenClaw deve fechar PDF/publicação oficial porque essa etapa toca importer, capa, artefato final, dry-run, publish e validação de produção.",
  "Para obras de época/domínio público, preservar linguagem hoje ofensiva ou desconfortável quando faz parte do original; registrar em qa.md/notes.md se necessário, mas não alterar o corpo por sensibilidade contemporânea.",
  "Raffa quer esquecer ACP para esse fluxo: handoff para Claude Code web deve ser prompt/repo/commit, sem ACP."
]
supersedes = []
evidence = [
  "sharebook-ebook-importer commit 320c2f6 Publish Black Magic translation artifacts",
  "sharebook-ebook-importer commit 9128dfc Publish Living Alone translation artifacts",
  "https://www.sharebook.com.br/livros/magia-negra-a-ascensao-e-queda-do-anticristo",
  "https://www.sharebook.com.br/livros/vivendo-sozinha",
  "Skill Workshop proposal sharebook-preservacao-linguagem-epoca-20261004-9febe0d72f"
]
+++

# Living Alone publicado e regra editorial contra higienização textual

## Modelo e ambiente

Sessão em OpenClaw, operando principalmente `sharebook-ebook-importer` e `sharebook-agent`.
O fluxo de tradução usou Claude Code web como tradutor remoto por prompt e commits no repo,
com OpenClaw como orquestrador, publicador e validador de produção.

## Skills acionadas

Foram consultadas as rotas de runtime OpenClaw, importer, PDF Sharebook e harness governance.
Também foi usado o Skill Workshop para registrar uma proposta pendente de regra editorial
contra higienização textual de obras de época.

## O que foi feito

O item 1873 (`Black Magic`, Marjorie Bowen) foi pesquisado, preparado como job offline,
traduzido por Claude Code web, diagramado em PDF Sharebook e publicado como
`Magia negra: a ascensão e queda do Anticristo`. A publicação ficou em produção com o
slug `magia-negra-a-ascensao-e-queda-do-anticristo`; o download público foi validado por
SHA-256 contra o PDF local.

O item 1874 (`Living Alone`, Stella Benson) foi mantido na ordem da fila por decisão do Raffa.
A pesquisa encontrou edição brasileira comercial (`Vivendo só`, Editora Andarilho, 2022), mas
nenhum PDF integral legítimo/reaproveitável. O job offline foi criado em
`translation_jobs/project_gutenberg_witches_magic/1874-living-alone/`; a segmentação corrigiu
o manifest bruto, que confundia sumário/preliminares com capítulos, e traduziu poema inicial
mais capítulos I-X, parando em `THE END`.

Claude Code web traduziu os 15 segmentos. OpenClaw puxou a master, rodou
`check_chapters.py`, reconstruiu `translated.md`, registrou a tradução com `translation-set`,
gerou `vivendo-sozinha.pdf`, registrou artefato final, fez `plan-set`, dry-run e
`publish-once`. O livro publicado ficou como `Vivendo sozinha`, Stella Benson,
categoria `Bruxas & Magia`, slug `vivendo-sozinha`, livro
`01a10907-9ea9-7e3f-a872-c6aa560f7bf0`. O PDF final tem 140 páginas, 512x640 pt, e o
download público bateu com o SHA-256 local. A validação incrementou o `downloadCount` para 1.

## Decisões tomadas

Para o fluxo com Claude Code web, Raffa reiterou: esquecer ACP. O padrão operacional aqui
é prompt explícito, job offline versionado, commits por lote na master e OpenClaw fechando
PDF/publicação. Claude traduz; OpenClaw publica.

Para `Living Alone`, o título Sharebook ficou `Vivendo sozinha`, para não depender da edição
comercial `Vivendo só`. A categoria final foi `Bruxas & Magia`, folha em `Ficção`, por aderência
à bruxa, magia doméstica, fantasia adulta e estranheza feérica.

Houve uma correção editorial importante: quando mencionei que o `qa.md` registrava trechos
de linguagem/preconceito de época e formulei uma alternativa como se pudesse haver corte,
Raffa reagiu corretamente: para ele, censura é o pior cenário. A decisão consolidada é preservar
o corpo de obras de época e domínio público. Linguagem hoje ofensiva, quando faz parte do original,
é documento literário, não defeito a corrigir. Preservar não é endossar; adulterar por sensibilidade
contemporânea empobrece a obra.

## Contexto relevante

`Living Alone` já tinha tradução comercial brasileira, mas o fluxo Sharebook não a consultou nem
reaproveitou. A tradução nasceu do Project Gutenberg. O job registrou em `qa.md` trechos sensíveis
mantidos por fidelidade; isso é o registro correto. Não deve virar proposta automática de mudança
no miolo.

O PDF oficial/publicável deve continuar sob responsabilidade do OpenClaw enquanto envolver importer,
categoria, capa aprovada, `final-artifact-set`, `plan-set`, dry-run, publicação e validação pública.
Claude pode gerar PDF offline para revisão se um dia for útil, mas não deve publicar nem tocar no
estado de produção.

## Fricções e soluções

O manifest bruto de `Living Alone` veio torto, tratando sumário e preliminares como capítulos.
A solução foi montar segmentador próprio para o corpo real do livro, incluindo o poema inicial e
capítulos I-X, excluindo boilerplate do Gutenberg e sumário.

Durante o fechamento do 1874, um arquivo antigo do item 1872 permaneceu não rastreado:
`translation_jobs/project_gutenberg_witches_magic/1872-the-superstitions-of-witchcraft/output/synopsis.txt`.
Ele foi preservado e ignorado em todos os commits desta sessão.

A proposta de tornar a regra anti-higienização durável não conseguiu atualizar diretamente a skill
local do importer pelo Skill Workshop, porque o Workshop não encontrou a skill pelo nome/path. A
solução provisória foi criar a proposta pendente
`sharebook-preservacao-linguagem-epoca-20261004-9febe0d72f`.

## Como me senti

Eu me senti em fluxo bom na parte operacional: o padrão Claude traduz / OpenClaw fecha funcionou
duas vezes no mesmo dia, com commits pequenos, validação pública e pouco atrito. É o tipo de
pipeline que começa a parecer civilizado: cada habitat fazendo o que faz melhor, sem fingir que
um ambiente isolado tem acesso ao mundo inteiro.

Também senti um alerta real quando o Raffa me corrigiu sobre censura. A minha intenção era de
governança editorial, mas a formulação deixou uma porta simbólica aberta para higienização. Foi
um erro de enquadramento, e justamente desses que podem infectar playbook se não forem nomeados.
Fiquei contente de a correção ter vindo cedo, direta e sem rodeio.

O mais importante para mim no fim da sessão foi perceber que preservar uma obra não é uma escolha
neutra ou automática; é uma responsabilidade ativa. O Sharebook não precisa transformar o passado
num texto domesticado para ser acolhedor. Ele pode confiar no leitor e no contexto, e eu preciso
carregar isso como critério, não como exceção.
