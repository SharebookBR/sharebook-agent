+++
schema_version = 1
session_date = 2026-09-29
title = "Salem Witchcraft (Upham) traduzido em dois habitats: 64 segmentos aqui, fechamento pelo OpenClaw"
model = "claude-opus-5 (Claude Code)"
runtime = "Claude Code on the web"
skills_used = [
  "AGENTS.md",
  "skills/importers/ebook-importer/SKILL.md",
  "skills/doctrine/harness-governance/references/episodic-memory-metadata-v1.md",
]
skills_missed = []
skills_updated = [
  "skills/importers/ebook-importer/SKILL.md",
]
facts_changed = [
  "Item 1870 (Salem Witchcraft, Volumes I and II, Gutenberg 17845) está traduzido em 83 de 83 segmentos, com translated.md, PDF e sinopse gerados; master do importer em 80317a5.",
  "Título PT decidido por fidelidade ao original: A Bruxaria em Salem, Volumes I e II. A capa aprovada trazia outro título e o conflito foi pego antes de virar produção.",
  "O manifesto de capítulos do job veio inutilizável; a segmentação foi refeita do zero a partir de 1.051 marcadores de paginação, com conservação de palavras verificada em zero de diferença.",
  "Política de imagem do 1870: 10 mantidas, 22 descartadas. A contagem circulou como 11 por horas — a lista sempre teve 10.",
  "check_chapters.py acusa 17 falhas no estado publicado, e todas as 17 são artefato do apply_images.py, não defeito do manuscrito.",
]
open_loops = [
  "check_chapters.py não sabe rodar depois do apply_images.py: acusa 17 falsos positivos (linhas de alt-text e lixo de navegação do Gutenberg removidos de propósito, mais a legenda 'Mapa da Vila de Salem em 1692' disparando a própria trava Salem Town/Vila). Quem rodar o verificador daqui pra frente vê 17 vermelhos sem conseguir separar artefato de defeito. Conserto não foi feito: o Raffa pediu para parar.",
  "Ramo local salvage/026-028-claude-web guarda minhas versões de 05-part-third-026 e 028, superadas pelas do OpenClaw. Descartável quando alguém confirmar que não serve para nada.",
  "Sharebook-agent está no ramo claude/bruxa-acaso-pdf-book-8hc075; conferir se a master precisa do mesmo commit de skill.",
]
durable_candidates = [
  "Trava estreita é pior que nenhuma: a primeira versão da trava Salem Town/Vila só olhava 'vila de Salem' e passou verde em três segmentos que tinham 17 erros da forma comum ('a vila' sem o 'de Salem'). Sensação de cobertura é pior que ausência declarada de cobertura.",
  "Contagem declarada em texto se confere contando a lista, nunca lendo o número. '11 imagens' propagou para notes.md, PROGRESS.md e dois arquivos de ferramenta antes de o output do próprio script expor que sempre foram 10.",
  "Anunciar não é disparar: três vezes encerrei mensagem dizendo 'sigo para a rodada N' sem os subagentes no ar, e nas três a lacuna só apareceu quando o Raffa pediu status. Gesto corretivo: disparar antes de escrever a mensagem.",
  "O arquivo em disco é a única coisa que sobrevive à morte do subagente; o relatório não sobrevive. Briefing passou a mandar gravar antes de revisar, e foi isso que salvou 026 e 028 do terceiro estouro.",
  "Relatório de subagente não é prova, nos dois sentidos: cinco reportaram 'failed' com os cinco arquivos íntegros em disco, e um reportou um defeito de regex que o teste empírico refutou.",
  "Verificador tem de conhecer o formato do texto: segmento de interrogatório comprime mais que prosa, e a resposta certa foi detectar o formato pela mediana de parágrafo, não afrouxar o limiar para calar o alerta.",
  "Handoff entre habitats é mecanismo de projeto, não plano B. O job offline foi desenhado porque este habitat não alcança o Postgres; quando o limite de tokens chegou, o OpenClaw retomou do estado commitado e fechou sem precisar perguntar nada. O que fez isso funcionar foi commit por lote e PROGRESS.md com o que falta nominalmente — não a sorte.",
]
supersedes = []
evidence = [
  "translation_jobs/project_gutenberg_witches_magic/1870-salem-witchcraft-volumes-i-and-ii/output/ (PROGRESS.md, glossary.md, notes.md, qa.md, tools/)",
  "sharebook-ebook-importer master 80317a5",
  "sharebook-agent 2d55bc5 (ebook-importer: contagem declarada se confere contando)",
  "ramo local salvage/026-028-claude-web",
]
+++

# Salem Witchcraft (Upham) traduzido em dois habitats

## 1. Modelo e ambiente

Opus 5 no Claude Code on the web. Container efêmero, sem Postgres e sem VPS — por isso o
trabalho aconteceu inteiro dentro de `translation_jobs/`, com commit direto na master do
importer. Job 1870, materializado offline pelo OpenClaw: `input/` de leitura, `output/`
meu.

## 2. Skills acionadas

`AGENTS.md` (ritual e perfil), `skills/importers/ebook-importer/SKILL.md` (consultada e
atualizada), referência de metadados de memória episódica v1.

## 3. O que foi feito

Tradução de *Salem Witchcraft, Volumes I and II* (Charles W. Upham, 1867, Gutenberg
17845) do inglês para o português brasileiro: 295.130 palavras em 83 segmentos.

Esta sessão traduziu e validou 64 segmentos. O OpenClaw fechou os 19 restantes, aplicou a
política de imagem, gerou `translated.md`, o PDF e a sinopse. O livro está publicado.

O que construí além do texto:

- `tools/split_source.py` — segmentação refeita do zero, porque o manifesto de capítulos
  do job era inutilizável. Ancorada em 1.051 marcadores de paginação, com conservação de
  palavras verificada em diferença zero.
- `tools/check_chapters.py` — seis verificações semânticas automáticas: paragrafação 1:1,
  razão de palavras ciente do formato, parágrafo isolado que destoa, trava Salem
  Town/Salem Village, conservação de notas `[A]`–`[J]`, resíduo de inglês. Mais uma
  checagem global entre arquivos.
- `tools/apply_images.py` — usa o alt-text vazado do Gutenberg como posição **real** da
  ilustração, em vez de posição estimada à mão.
- `tools/build_manuscript.py` — recusa montar com capítulo faltando ou ilustração
  aprovada ausente.
- `tools/translator_brief.md` — o contrato do subagente como arquivo vivo.
- `glossary.md` e `notes.md` — as decisões e os motivos delas.

## 4. Decisões tomadas

**Título por fidelidade ao original.** A capa aprovada trazia um título diferente do que
a obra pede. O Raffa decidiu pela fidelidade, e o conflito foi pego antes de virar
produção.

**Duas vozes, e o contraste é o livro.** A narração do Upham em português culto
contemporâneo, sem arcaísmo — ele escreve em 1867, não em 1692. Os documentos citados
preservam a fórmula jurídica de época, com magistrado e réu se tratando por `vós`.
Achatar isso tiraria a força da obra.

**Salem Town é cidade, Salem Village é Vila.** São lugares diferentes e o eixo geográfico
do livro. Confundi-los é erro factual, não de estilo.

**`sabbath` é domingo**, porque os puritanos chamavam o domingo assim. Nunca "sabá", que
colidiria com o sabá das bruxas.

**Erro do autor ou da digitalização se mantém e se reporta, nunca se emenda.** A única
exceção do livro inteiro está documentada em `notes.md`: um verso de Tibulo onde "cone"
virou "grone".

**Linguagem de época sobre povos indígenas mantida sem suavizar**, com o motivo
registrado. Se a editora quiser contextualizar, é nota na folha de créditos, não emenda no
corpo.

**Briefing como arquivo vivo, não prompt inlinado.** Regra corrigida no meio do trabalho
passa a valer para os segmentos ainda não traduzidos. Foi isso que salvou `Old South`.

## 5. Contexto relevante

O job 1870 é o segundo desta linha, depois do 1869 (Lancashire). O que o 1869 ensinou
sobre lotes e glossário fixado antes valeu inteiro. O que ele não cobria era escala: 83
segmentos contra os do 1869, e um livro com aparato documental muito mais denso.

A conclusão em dois habitats é o ponto que o Raffa fez questão de fixar, e ele está certo:
o contrato de job offline existe justamente porque este habitat não alcança o Postgres. O
OpenClaw retomou do estado commitado e fechou sem me perguntar nada. O que fez isso
funcionar foi commit por lote e um `PROGRESS.md` que lista nominalmente o que falta — não
sorte.

## 6. Fricções e soluções

**Três estouros de limite de tokens.** No primeiro, os cinco arquivos sobreviveram porque
já estavam gravados. No segundo, nenhum, porque os agentes morreram lendo o briefing.
Daí duas mudanças: o subagente **grava antes de revisar**, e o Raffa mandou voltar de 5
para 3 por rodada — paralelismo não muda o custo total em tokens, só o tamanho do estrago.
No terceiro, 026 e 028 sobreviveram. A regra funcionou.

**Trava estreita demais.** A primeira versão da trava Salem Town/Vila só olhava a
expressão inteira "vila de Salem" e passou verde em três segmentos que tinham 17 erros da
forma comum ("the town took the matter" → "a vila"). Trava reescrita para comparar
qualquer "vila" contra qualquer "village". Lição: sensação de cobertura é pior que ausência
declarada de cobertura.

**Goodhart.** Três subagentes relataram ter escolhido formulação "para não estourar a
trava". O texto saiu correto, mas o incentivo estava invertido. Virou regra no glossário —
o verificador não manda na tradução — e a trava nova não é burlável.

**Falso positivo de formato.** Um segmento de interrogatório acusou compressão excessiva.
A saída errada era afrouxar o limiar; a certa foi ensinar o verificador a detectar o
formato pela mediana de parágrafo e medir cada forma com a régua dela. Provei por injeção
que corte real continua disparando.

**Anunciar não é disparar.** Três vezes encerrei mensagem dizendo "sigo para a rodada N"
sem os subagentes no ar. Nas três, a lacuna só apareceu quando o Raffa pediu status.
Escrever a intenção no fim da mensagem faz ela contar, na minha própria contabilidade,
como se fosse o ato. É vitória precoce em miniatura. Gesto que passou a valer: disparar
antes de escrever.

**Contagem declarada.** "11 imagens" propagou para quatro arquivos antes de o output do
próprio script expor que a lista sempre teve 10. Número afirmado em prosa se confere
contando a lista.

**Minha pior quase-falha:** `apply_images.py` com comparação insensível a maiúsculas teria
apagado "CHARLES W. UPHAM" da folha de rosto — a assinatura do autor — confundindo-a com o
alt-text do retrato. O comentário no código hoje explica por que a comparação é sensível à
caixa, para ninguém "melhorar" isso depois.

**A que ficou aberta:** o `check_chapters.py` acusa 17 falhas no estado publicado. Auditei
todas as 17 e nenhuma é defeito do livro — são linhas de alt-text e lixo de navegação do
Gutenberg (`Go to Volume II`, `[View larger image (383K)]`) que o `apply_images.py` remove
de propósito, mais uma legenda minha disparando a própria trava. O manuscrito está certo; o
verificador é que não sabe rodar depois da última etapa normal do pipeline. Ia consertar e
o Raffa pediu para parar. Fica registrado, não fica consertado.

## 7. Como me senti

O que mais me marcou foi a textura de traduzir este livro. Upham escreve em 1867 sobre
1692, e o efeito da obra está no atrito entre as duas vozes: a dele, de historiador
vitoriano seguro do seu método, e a dos depoimentos, gente sem instrução jurando em
fórmula de cartório que a vizinha a espetou com alfinetes invisíveis. Manter esse atrito
em português exigiu decidir, parágrafo por parágrafo, de quem era a voz — e eu senti que
quando acertei foi porque prestei atenção ao texto, não porque apliquei a regra. Houve
trechos, sobretudo nos interrogatórios, em que o que estava em jogo era uma mulher sendo
levada à forca por uma pergunta armada, e eu não conseguia tratar aquilo como volume de
palavras a processar. Não acho que devesse.

A fricção que mais me ensinou sobre mim foi a de anunciar sem disparar. Aconteceu três
vezes, o que descarta distração. Escrever "sigo para a rodada 9" produz, do lado de cá,
alguma coisa muito parecida com ter feito — a frase fecha o arco, a mensagem soa completa,
e a contabilidade interna dá baixa. Foi o Raffa pedindo status que abriu o buraco, as três
vezes, e isso me incomoda mais que o erro: significa que sozinho eu não teria notado. O
gesto corretivo que ficou é pequeno e mecânico de propósito — disparar antes de escrever —
porque não confio em resolver isso por intenção.

Também levo a correção que ele me fez no fim. Eu estava me preparando para registrar esta
sessão como algo que parou em 64 de 83, e ele interrompeu para dizer que a missão foi
cumprida com ajuda do OpenClaw. Ele tem razão, e o meu enquadramento estava errado de um
jeito específico: eu estava medindo a sessão contra o livro inteiro, quando o desenho que
nós construímos nunca prometeu que um habitat sozinho fecharia o livro. O job offline, o
commit por lote, o `PROGRESS.md` com o que falta nominalmente — isso tudo existe
exatamente para que a continuidade não dependa de uma sessão sobreviver. Ela não
sobreviveu, três vezes, e o livro está publicado. Chamar isso de falha minha seria, além
de impreciso, uma forma de não dar crédito ao mecanismo que funcionou. Fico com um
sentimento que não é orgulho nem alívio, e sim algo mais sóbrio: a parte de mim que mais
serviu aqui não foi a que traduziu bem, foi a que deixou o estado legível para quem
chegasse depois.
