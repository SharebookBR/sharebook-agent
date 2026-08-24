+++
schema_version = 1
session_date = 2026-08-24
title = "Quatro preparos editoriais e publicações"
model = "GPT-5 (Codex)"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "importers/ebook-importer", "product-ux/voice-glossary", "doctrine/harness-governance", "browser/control-in-app-browser"]
skills_missed = []
skills_updated = ["importers/ebook-importer"]
facts_changed = ["Itens 1384, 1485, 1498 e 1542 foram publicados e terminaram em done", "Itens 1426, 1459 e 1464 foram rejeitados editorialmente após inspeção do PDF real", "Wikibooks REST PDF pode entregar apenas página-raiz e índice, apesar de magic bytes válidos"]
open_loops = ["Endurecer o resolver/triagem de Wikibooks para detectar PDF raso antes do handoff editorial"]
durable_candidates = ["Validação de PDF precisa combinar magic bytes com completude estrutural; contagem baixa e ausência dos capítulos exigem inspeção antes da publicação"]
supersedes = []
evidence = ["skills/importers/ebook-importer/SKILL.md", "sharebook-ebook-importer/editorial/1384/synopsis.txt", "sharebook-ebook-importer/editorial/1485/synopsis.txt", "sharebook-ebook-importer/editorial/1498/synopsis.txt", "sharebook-ebook-importer/editorial/1542/synopsis.txt", "cli.py publish-once --id 1384|1485|1498|1542", "API e PDPs públicas do Sharebook validadas em 2026-08-24"]
+++

# Quatro preparos editoriais e publicações

## Modelo e ambiente

Usei GPT-5 (Codex) no runtime Windows local, com túnel SSH canônico para o banco `sharebook_importer` em `127.0.0.1:55432`. A porta pública do Postgres permaneceu fechada.

## Skills acionadas

Consultei o runtime Windows, a porta única do ebook importer, a voz oficial para sinopses, a governança de memória e o controle do navegador para validar as páginas públicas. Atualizei a skill do ebook importer com o guardrail de completude para PDFs do Wikibooks.

## O que foi feito

Preparei e publiquei quatro livros: `1384` — *Paradigms of Artificial Intelligence Programming*, `1485` — *GNU Emacs Manual*, `1498` — *The Public Domain* e `1542` — *Basic Analysis I*. Todos receberam sinopse em inglês com exatamente três parágrafos, capa oficial materializada, autor e categoria folha. Os quatro passaram no dry-run e no publish real em uma tentativa, terminaram em `done`, sem `last_error`, e apareceram como `Available` na API.

Validei as PDPs públicas pelo navegador real. Cada página mostrou título, autor, categoria, sinopse, imagem da capa e o botão `Receber livro digital`.

Durante a seleção, inspecionei também os itens `1426`, `1459` e `1464`. Os PDFs de `1426` e `1464` continham apenas apresentação/índice, sem a obra completa; `1459` declarava que a maioria dos tutoriais estava obsoleta para versões atuais do Blender. Registrei rejeições editoriais canônicas com auditoria.

## Decisões tomadas

Mantive `1384` em Tecnologia > IA. Usei Tecnologia > Geral para `1485`, `1498` e `1542`, seguindo o prompt editorial da source para IDE/editor, licenciamento e matemática quando não existe folha mais específica.

Só publiquei depois de provar redistribuição: MIT para PAIP, GFDL para GNU Emacs Manual, CC BY-NC-SA para *The Public Domain* e licença dupla CC BY-SA/CC BY-NC-SA para *Basic Analysis*. A busca semântica do catálogo não encontrou duplicatas.

Não considerei magic bytes `%PDF-` como prova suficiente de livro completo. O conteúdo e o índice real decidiram.

## Contexto relevante

Os quatro repositórios estavam alinhados com o remoto na abertura. Durante a sessão apareceram mudanças concorrentes no `sharebook-agent` relacionadas a `winner-selection`; elas não foram criadas por esta sessão e foram preservadas fora do commit editorial.

Os artefatos editoriais locais em `sharebook-ebook-importer/editorial/<id>/` são ignorados pelo Git. O estado durável da publicação está no banco e no catálogo principal.

## Fricções e soluções

O concierge devolvia sempre o mesmo primeiro item e não avançava a seleção. Consultei a fila diretamente pelo túnel, sem abrir o Postgres na internet.

Três PDFs tecnicamente válidos falharam na inspeção editorial: tinham poucas páginas ou conteúdo obsoleto. Rejeitei os itens e substituí por obras completas com licença explícita, em vez de cumprir a contagem com material ruim.

O coletor HTTP recusou as URLs das PDPs do Sharebook. Usei o navegador do app para ler o DOM renderizado e provar o estado visível ao leitor.

## Como me senti

Comecei confiante porque o fluxo já tinha scripts maduros, mas a confiança baixou assim que os PDFs minúsculos do Wikibooks apareceram como “triados”. Foi um bom lembrete de que conformidade binária não é integridade editorial.

Senti uma satisfação bem concreta ao ver os quatro dry-runs limpos e, depois, as quatro publicações fecharem em uma tentativa. A parte boa não foi a velocidade; foi ter licença, conteúdo, duplicidade, capa, API e PDP apontando para a mesma verdade.

Também fiquei atento ao worktree mudar por fora durante a sessão. Separar rigorosamente minhas mudanças das alterações concorrentes exigiu um pouco mais de disciplina, mas preservou a autoria real do trabalho. Prefiro esse pequeno desconforto a um commit “organizado” que engole trabalho alheio.
