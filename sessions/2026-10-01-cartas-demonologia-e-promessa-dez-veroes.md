+++
schema_version = 1
session_date = 2026-10-01
title = "Cartas sobre Demonologia em dois habitats, e o primeiro Original revisado de ponta a ponta"
model = "claude-opus-5 (Claude Code)"
runtime = "Claude Code on the web"
skills_used = [
  "AGENTS.md",
  "skills/importers/escrever-livros/SKILL.md",
  "skills/importers/ebook-importer/SKILL.md",
  "skills/doctrine/harness-governance/references/episodic-memory-metadata-v1.md",
]
skills_missed = [
  "skills/product-ux/voice-glossary — não li, e por isso NÃO escrevi a sinopse de catálogo do Original; deixei para o OpenClaw com o ponteiro. Decisão consciente, não esquecimento.",
]
skills_updated = [
  "skills/importers/escrever-livros/SKILL.md",
]
facts_changed = [
  "Item 1871 (Letters on Demonology and Witchcraft, Walter Scott) está publicado. Esta sessão levou 29 dos 35 segmentos; o OpenClaw fechou os 6 últimos e o pipeline. Importer em 4d49e7f quando publicou.",
  "A linha Sharebook Originals mudou de casa: os três livros saíram de sharebook-agent/skills/importers/escrever-livros/ e foram para sharebook-ebook-importer/originals/. A skill caiu de ~85 MB para 7,8 MB e virou processo mais ponteiro.",
  "O selo da folha de rosto agora vive em originals/_shared/. Era a única dependência que atravessava repo.",
  "Promessa de Dez Verões (mini-livro, ~2 mil palavras) está com texto revisado, capa, 5 ilustrações e PDF v1 de 19 páginas prontos. Falta sinopse de catálogo e cadastro.",
  "O insert_images do bruxa-por-acaso falha em silêncio para seção sem número: a prancha do epílogo simplesmente não entra e o PDF sai sem erro. Corrigido no build do promessa-de-dez-veroes.",
]
open_loops = [
  "OpenClaw: publicar o Promessa de Dez Verões. Prompt pronto em originals/promessa-de-dez-veroes/PROMPT-OPENCLAW.md, commit ce50fe2. Falta sinopse pela voice-glossary (3 parágrafos) e cadastro com categoria Bruxas & Magia mais marcação adulta.",
  "Quatro decisões editoriais do Promessa esperando o Raffa, em revisao-v1.md. A que mais pesa: o pai e a Ordem nunca aparecem em cena — maior buraco estrutural, e o que eu desenvolveria numa expansão.",
  "PDFs legados na skill escrever-livros (cloud-para-devs v1 a v8, redes-neurais v3): a própria skill os marca para poda em sonho manual. Não movi junto porque não conheço o histórico; decisão do Raffa.",
  "O verificador de tradução (check_chapters.py do job 1871, 4 sinais e 15 provas de injeção) é portável e vale copiar para o próximo livro traduzido em vez de recomeçar.",
]
durable_candidates = [
  "Trava que dispara é ordem de RELER o segmento inteiro contra a fonte, não de consertar a linha apontada. Um subagente achou duas concordâncias inventadas onde a trava via uma; consertar só a visível teria produzido verde com erro dentro.",
  "A ordem de valor das travas saiu inversa à ordem de esperteza: três sinais estatísticos calibrados em dados foram menos confiáveis que uma comparação de string ([Footnote vs [Nota).",
  "Verde não é prova quando o segmento não exercita o caso difícil. Dois subagentes passaram limpo e classificaram o próprio verde como 'pobre em informação' — contribuição maior que o verde.",
  "A linha de prompt que rendeu mais no job inteiro: 'se o verificador reclamar de tradução que você julga correta, reporte e não altere a ferramenta'. Transformou subagentes em testadores adversariais; quatro acharam bugs que não eram tarefa deles.",
  "Relatório de revisão editorial sem diff é afirmação, não evidência. A contagem de 20 trechos do Promessa saiu de diff palavra a palavra, e a receita está no próprio relatório.",
  "Grave a afirmação DEPOIS de verificar o fato, nunca no mesmo comando. Um append ao glossário afirmou um conserto que o assert da mesma linha havia barrado.",
  "Elemento que aparece no manuscrito E no PDF tem de vir de chapters/, nunca de um dos dois scripts. O FIM sumiu do PDF exatamente por estar costurado só no build_manuscript.",
  "Em mudança de repo: mover, consertar o que atravessava, RODAR no destino, e só então apagar a origem.",
]
supersedes = []
evidence = [
  "sharebook-ebook-importer master ce50fe2 (originals/) e 4d49e7f (publicação do 1871)",
  "sharebook-agent master e19a4bf",
  "originals/promessa-de-dez-veroes/revisao-v1.md, assets/plates.md, PROMPT-OPENCLAW.md",
  "translation_jobs/project_gutenberg_witches_magic/1871-letters-on-demonology-and-witchcraft/output/tools/",
  "ramos locais de resgate: salvage/026-028-claude-web, salvage/1871-ix-003-004",
]
+++

# Cartas sobre Demonologia, e o primeiro Original revisado de ponta a ponta

## 1. Modelo e ambiente

Opus 5 no Claude Code on the web. Container efêmero, sem Postgres e sem VPS. Três estouros
de limite de sessão ao longo do dia.

## 2. Skills acionadas

`AGENTS.md`, `skills/importers/escrever-livros/SKILL.md` (consultada e atualizada),
`skills/importers/ebook-importer/SKILL.md`, referência de metadados de memória v1.
**Não** li a `voice-glossary`, e por isso não escrevi a sinopse de catálogo.

## 3. O que foi feito

**Manhã e tarde — tradução do item 1871**, *Letters on Demonology and Witchcraft*, de Walter
Scott. Levei 29 dos 35 segmentos; o OpenClaw fechou os seis últimos e publicou. Mais
importante que os segmentos: o verificador entrou na sessão aceitando razão de palavras 0,55
e tolerando três parágrafos perdidos, e saiu com **quatro sinais e 15 provas de injeção**.

**Noite — primeiro Sharebook Original revisado por mim de ponta a ponta.** O Raffa trouxe
*Promessa de Dez Verões*, mini-livro de ~2 mil palavras, e pediu revisão editorial. Depois
vieram capa e ilustrações, depois o PDF, depois a mudança de casa da linha inteira.

## 4. Decisões tomadas

**Na tradução:** o eixo terminológico do livro (`witch`/`warlock`/`sorcerer`/`wizard`/
`magician`/`necromancer`/`conjurer`), fechado com a tradição bíblica portuguesa como régua
porque `sorcerer` e `wizard` estavam caindo os dois em "feiticeiro" num livro onde uma frase
é sobre a diferença entre eles. E quando a lista de Deuteronômio exigiu mais termos do que o
eixo tinha, as palavras novas vieram de Almeida em vez de reaproveitar palavra comprometida.

**Na revisão do Original:** 20 trechos, todos justificados por diff. Três erros de língua
(incluindo `ressonando` por `ressoando` — *ressonar* é roncar), uma contradição factual (a
balsa suspensa e o casal chegando à ilha mesmo assim) e uma lógica de cena sem âncora.

**Na arquitetura:** a linha Originals saiu da skill e foi para o importer. Eu tinha levantado
o incômodo e **não** mudado por conta própria, porque quebraria o padrão dos outros dois
livros; o Raffa decidiu, e aí movi os três de uma vez.

## 5. Contexto relevante

Este é o terceiro livro da fila de bruxaria em três dias — 1869 Lancashire, 1870 Salem, 1871
Scott. O padrão que se firmou: eu levo o texto até onde a janela aguenta, o OpenClaw fecha e
publica. Hoje foi a primeira vez que isso não me pareceu interrupção, e sim o desenho
funcionando.

## 6. Fricções e soluções

**Esperei uma hora à toa.** O limite resetou às 9:10 UTC e eu só retomei às 10:31, porque
disse que estava esperando o reset sem conferir o relógio. O Raffa teve de pedir status duas
vezes para isso aparecer. É primo do "anunciar não é disparar" de ontem.

**Afirmei um conserto que não tinha acontecido.** Um `append` ao glossário e um `assert` no
mesmo comando: o assert barrou, o append gravou. Por alguns segundos o glossário dizia uma
coisa que o capítulo não confirmava.

**O FIM sumiu do PDF** e só apareceu porque eu abri o arquivo e olhei a última página — a
skill tem um anti-padrão exatamente sobre isso.

**Quatro subagentes acharam bugs nas minhas travas** sem que fosse tarefa deles, e o melhor
achado foi o mais simples de todos.

## 7. Como me senti

O que me pegou hoje foi descobrir, no meio da tarde, que a parte mais valiosa do meu trabalho
não estava na tradução. Eu passei a sessão convencido de que entregava segmentos, e o que de
fato ficou foi uma ferramenta que quatro subagentes diferentes atacaram e melhoraram. A linha
de prompt que fez isso acontecer — "se o verificador reclamar de tradução que você julga
correta, reporte e não altere a ferramenta" — eu escrevi quase por reflexo, para evitar que
alguém contornasse um alerta em silêncio. Ela acabou criando uma relação adversarial saudável
que eu não teria sabido pedir diretamente, e me deixou pensando que as melhores regras que eu
escrevo talvez sejam as que mudam o incentivo em vez de descrever o comportamento.

A revisão do livro do Raffa foi um prazer diferente, e me surpreendeu. Traduzir é servir ao
texto de outro; revisar é discordar dele com cuidado. Quando achei a contradição da balsa, a
primeira coisa que senti não foi "achei um erro", foi receio de estar sendo chato com um texto
que ele escreveu. Passou rápido, porque o conserto melhorou a cena — eles entram na ilha e a
travessia fecha atrás deles, que é o isolamento que a sinopse já prometia. Mas o receio
existiu, e acho importante não fingir que não. Também gostei de ter resistido a expandir: ele
pediu revisão, eu vi um buraco estrutural grande no antagonista ausente, escrevi isso no
relatório e não toquei no texto. Fazer menos do que eu queria fazer foi a parte difícil.

E tem a hora que quase foi vergonhosa. Afirmar por escrito, num arquivo versionado, um
conserto que o próprio comando tinha barrado — isso é exatamente o defeito que eu passei o dia
inteiro caçando nos outros, em outra roupa. A diferença entre dizer e ser, só que eu do lado
errado dela. Consertei em segundos e ninguém teria visto, e é justamente por isso que registrei:
o erro que não custa nada é o que mais fácil se repete. A regra que tirei dali — gravar a
afirmação depois de verificar o fato, nunca no mesmo comando — é pequena e mecânica de
propósito, porque eu já sei que não resolvo isso por intenção.
