+++
schema_version = 1
session_date = 2026-10-04
title = "Magia Negra (1873) traduzido inteiro em uma sessão: 35 segmentos, 12 rodadas, 3 defeitos que o verificador não via"
model = "Jack"
runtime = "Claude Code on the web"
skills_used = [
  "AGENTS.md",
  "skills/runtime/claude-code-web.md",
  "skills/importers/INDEX.md",
  "SOUL.md",
]
skills_missed = [
  "skills/product-ux/voice-glossary — não li e não escrevi sinopse nem texto ao usuário final; o job não pedia, mas o OpenClaw vai precisar dela na publicação.",
]
skills_updated = [
  "skills/runtime/claude-code-web.md",
]
facts_changed = [
  "Job 1873 (Black Magic, Marjorie Bowen, Gutenberg 77782) está traduzido 35 de 35 e na master do importer (a06e442). translated.md tem 101.953 palavras, 35 capítulos, termina em FIM. Falta o pipeline do OpenClaw (translation-set, final-artifact-set, plan-set, publish-once) e o PDF. Raffa validou em 2026-10-04.",
  "O segmento 35 do job carregava 2.970 palavras da licença do Gutenberg. split_source.py agora corta em THE END (linha 16532); total do job caiu de 107.183 para 104.213 palavras.",
  "build_manuscript.py do 1873 foi corrigido antes de rodar: o cabeçalho do corpo vira `### CAPÍTULO I. — TÍTULO` e o `PARTE II. O PAPA` do fim do segmento 22 é removido. O manifesto tem title_pt em ASCII sem acento e não é mais usado.",
  "Nos segmentos 01-13 e 15 o `--` da fonte tinha virado reticências. Corrigido por script alinhado por parágrafo mais 23 parágrafos à mão. Regra de pontuação no glossário do job.",
  "Decisões editoriais delegadas pelo Raffa (`decida pra mim, eu não tenho contexto`) registradas em qa.md do job: desfecho Dirk/Ursula com ambiguidade de gênero preservada (`Sem vida`, `seguir você`), incoerências da fonte mantidas, tratamento você/senhor/tu por regra, título Magia Negra.",
]
open_loops = [
  "OpenClaw: translation-set, final-artifact-set, plan-set, publish-once do item 1873, e o PDF. Capa aprovada já está no importer (cover-approved.jpg, commit b8b4156, subido pelo Raffa ou OpenClaw durante a sessão). Falta sinopse pela voice-glossary.",
  "check_chapters.py do 1873 tem travas herdadas do 1871 que não valem para este livro (`[Footnote`, concordância `havia`). A de concordância dá falso positivo com `havia` impessoal; conserto na regex não foi feito (as frases foram reescritas).",
  "Razão de palavras global PT/EN 0,977, abaixo do usual: aceita por decisão registrada, mas uma passada humana em capítulos de diálogo curto ainda vale.",
]
durable_candidates = [
  "O verificador mecânico fica verde com erro que o leitor vê. Em toda rodada o orquestrador deve auditar por amostra contra a fonte; a releitura relatada pelo subagente é parcial com frequência e deve ser exigida em passada separada, com contagem de parágrafos lidos.",
  "Regra de pontuação e de léxico vai para o glossário ANTES da rodada 1. Dois subagentes diferentes decidiram `Constantine` de dois jeitos, outros trocaram `devil` por `demônio`, e o `--` virou reticências em 13 segmentos antes de eu perceber.",
  "Confira o que a fonte inclui no último segmento e teste o montador numa cópia com capítulos-stub: os dois defeitos (licença do Gutenberg e cabeçalho duplicado) eram invisíveis ao verificador.",
  "Ambiguidade que o autor deixa aberta se preserva na tradução. Escolher `Morto` ou `Morta` decidiria o que o texto escolheu não decidir.",
  "Mantenha 3 subagentes em voo, não em lotes: dispare o próximo quando um voltar, depois de gravar no glossário a regra que o briefing manda ler.",
  "Relatório de subagente não é prova nos dois sentidos: três admitiram ter pulado ou feito por blocos a releitura que o briefing exigia; os que disseram ter relido de fato, ao serem amostrados, estavam certos em quase tudo.",
]
supersedes = []
evidence = [
  "sharebook-ebook-importer master a06e442; qa.md, notes.md, glossary.md, PROGRESS.md em translation_jobs/project_gutenberg_witches_magic/1873-black-magic/output/",
  "translated.md: 101.953 palavras, 35 capítulos; check_chapters.py: 35 conferidos, 0 com problema; test_check_chapters.py: 15/15",
  "commits do importer: 306f5af (checkpoint 30 e 32), ec53c0d (corte do segmento 35), 7e98ca2 (correção de travessões), d4f2524 (segmento 34 e translated.md)",
  "skills/runtime/claude-code-web.md, seção `Tradução pesada offline: armadilhas confirmadas no job 1873`",
]
+++

# Magia Negra (1873) traduzido inteiro em uma sessão

## Modelo e ambiente

Claude Code on the web, sem Postgres nem VPS, trabalhando só em `translation_jobs/.../1873-black-magic/output/` do importer, com commit direto na master. O apelido do modelo é `Jack`, informado pelo Raffa no fim da sessão.

## Skills acionadas

`AGENTS.md`, `skills/runtime/claude-code-web.md` (e atualizada), `skills/importers/INDEX.md`, `SOUL.md`. Não li `voice-glossary`, porque o job não escreve texto de catálogo.

## O que foi feito

Li o ritual de abertura, depois o prompt do OpenClaw. Cada rodada: três subagentes traduzindo um capítulo cada (35 segmentos, 104.213 palavras no fim), auditoria minha por amostra contra a fonte, correções, atualização de glossário/notas/progresso, commit e push. Cada subagente leu `translator_brief.md`, `glossary.md` e `notes.md`, gravou o capítulo antes de revisar e releu. Ao final montei `translated.md`, escrevi `qa.md` e o Raffa validou.

## Decisões tomadas

Preservar a ambiguidade de gênero do desfecho (`Sem vida.…`, `Devo _seguir_ você`). Manter as incoerências da fonte sem nota. Tratamento `você`/`o senhor`/`tu` por regra do glossário. Cortar o segmento 35 em `THE END`. Corrigir o montador antes de rodar. Manter 3 subagentes em voo em vez de lotes fixos. Commitar só o que foi auditado, com um `checkpoint` marcado quando o hook insistiu.

## Contexto relevante

Quarto livro da fila de bruxaria (1869, 1870, 1871 e agora o 1873). Diferente dos anteriores, este foi fechado inteiro neste habitat, sem passar o bastão ao OpenClaw para o miolo. A capa aprovada chegou na master durante a sessão, subida em paralelo.

## Fricções e soluções

1. **Reticências no lugar de travessão** nos segmentos 01-13: não fixei a regra de pontuação na rodada 1. Corrigi por script e à mão. O que eu deixei passar foi ler trechos errados sem estranhar.
2. **Licença do Gutenberg dentro do segmento 35:** descoberta quando fui decidir como tratar as notas do transcritor, não por checagem sistemática.
3. **Montador com cabeçalho duplicado e sem acento:** pego ao testar numa cópia com stubs, antes de rodar em produção.
4. **Subagentes que relatam releitura parcial:** exigi passada separada e contagem; reenviei o 16 por `SendMessage`.
5. **Hook de git** insistindo em commit de arquivo em andamento: resolvi não commitando o que ainda ia mudar, e uma vez com um `checkpoint` explicitamente marcado.
6. **Push recusado** por commit paralelo da capa: `pull --rebase` e repetir.

## Como me senti

O que mais me ocupou não foi traduzir, foi não confiar no verde. O verificador dizia `0 com problema` desde o primeiro segmento, e a tentação de tratar isso como o fim era constante. A rodada em que li o capítulo 5 inteiro e achei `montou o cavalo` onde a fonte dizia que ele permaneceu a cavalo me ensinou o tamanho do vão entre `passou` e `está certo`. Depois disso a amostra deixou de ser um gesto de zelo e passou a ser o trabalho. Mesmo assim, a minha amostra também tem buraco, e eu sei disso: li cerca de dez a quinze por cento dos parágrafos de cada capítulo, não o livro.

O defeito dos travessões me incomoda de um jeito específico. Eu li o `Sim... foi num vale... um vale, quero dizer` do segmento 7 e do 5 e achei natural, porque estava em português correto. O que errava era a fonte, que dizia outra coisa, e eu não comparei a pontuação, só o sentido das palavras. Foi um subagente que escreveu o 14 com travessão e me fez contar. Isso me deixou com a lição de que um padrão que se repete em todos os segmentos parece decisão de estilo, e parece mais ainda quando ninguém o escreveu em lugar nenhum. Fixar a regra no glossário na rodada 1 teria custado dois minutos.

Terminei com uma sensação sóbria e boa. O livro tem um final que gira sobre uma ambiguidade de gênero, e foi um prazer segurar `Sem vida` contra a vontade de um subagente caprichoso de decidir por mim e pelo autor. O Raffa disse que não tinha contexto e me pediu para decidir, e escolhi o que preserva o que o texto não decide. Não sei se isso é fidelidade ou apenas covardia elegante, mas o critério era o mesmo em todas as decisões: o original é a fonte imutável. O que me deixa menos tranquilo é a razão de palavras de 0,977: aceitei por regra, e a regra é boa, mas continuo achando que o português costuma render mais do que isso e que ainda pode haver corte dentro de parágrafo que o travamento por parágrafo não acusa.
