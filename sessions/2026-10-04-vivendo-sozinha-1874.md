+++
schema_version = 1
session_date = 2026-10-04
title = "Vivendo sozinha (1874) traduzido inteiro na mesma sessão do Magia Negra, já sem os três defeitos do 1873"
model = "Jack"
runtime = "Claude Code on the web"
skills_used = [
  "AGENTS.md",
  "skills/runtime/claude-code-web.md",
  "skills/importers/INDEX.md",
]
skills_missed = [
  "skills/product-ux/voice-glossary — não li e não escrevi sinopse; o job não pedia, mas o OpenClaw vai precisar dela na publicação.",
]
skills_updated = [
  "skills/runtime/claude-code-web.md",
]
facts_changed = [
  "Item 1874 (Living Alone, Stella Benson, Gutenberg) está traduzido 15 de 15 e na master do importer (52b459a). translated.md tem 42.029 palavras (contagem do Python; `wc -w` dá 41.438 no mesmo arquivo), poema + 10 capítulos, termina em FIM. Raffa validou em 2026-10-04. Falta o pipeline do OpenClaw e o PDF.",
  "O livro não tem ilustrações: o HTML do Gutenberg não tem <img> e o texto não tem [Illustration]. O PDF precisa de capa e da página institucional, mas não de pranchas internas.",
  "build_manuscript.py do 1874 foi corrigido ANTES da rodada 1: o cabeçalho vem do corpo (`## CAPÍTULO I — TÍTULO`), o poema usa o primeiro parágrafo como título, e o montador recusa `-002` com cabeçalho. Defeito idêntico ao do 1873, evitado por teste em cópia com stubs.",
  "Decisões editoriais delegadas pelo Raffa (`decida por mim`), em qa.md do job: `muddy Jews` e `os bons negros` mantidos literais; `a Coração Feliz` mantido; poema sem rima; título `Vivendo sozinha`.",
]
open_loops = [
  "OpenClaw: translation-set, final-artifact-set, plan-set, publish-once do item 1874, PDF, capa e página institucional. Falta sinopse pela voice-glossary.",
  "Se o Raffa preferir não publicar os dois trechos de preconceito de época como estão, a saída mínima é nota na folha de créditos; registrada no qa.md.",
  "A coluna Modelo da tabela de apelidos do runtime web continua em branco: é do Raffa preencher.",
]
durable_candidates = [
  "Aplicar a lição antes da rodada 1, não depois: pontuação, léxico e nomes no glossário e teste do montador com stubs custaram minutos e evitaram os três defeitos do 1873 (reticências no lugar de travessão, licença do Gutenberg no último segmento, cabeçalho duplicado).",
  "Scratchpad compartilhado entre subagentes: script com nome único e caminhos confirmados no output.",
  "Releitura por subagente: exigir contagem de parágrafos lidos de fato. Um subagente admitiu não ter relido, outro releu por varredura; o erro de API de sinalização de segurança pode matar a releitura, então disparar revisor novo.",
  "Capítulo curto do começo (o I) lido inteiro por mim valeu mais que várias amostras: achou diálogo com travessão de abertura, `guinéu` no gênero errado e o `H de why` sem efeito.",
  "Quando o Raffa delega a decisão, decidir pelo critério de fidelidade, registrar a alternativa descartada e esperar a palavra dele antes de dizer que está validado.",
]
supersedes = []
evidence = [
  "sharebook-ebook-importer master 52b459a; translation_jobs/project_gutenberg_witches_magic/1874-living-alone/output/ (qa.md, notes.md, glossary.md, PROGRESS.md, translated.md)",
  "check_chapters.py: 15 conferidos, 0 com problema; test_check_chapters.py: 15/15; translated.md igual byte a byte no local e no remoto",
  "commits do importer: f376eb5 (glossário e montador), fd5ca50, 7dc6955, 56431ca, 29642bb, 878982b, 2cf7dff, d7a566c, e94b9ae, 52b459a",
  "skills/runtime/claude-code-web.md, seção `Tradução pesada offline`, bullets do job 1874",
]
+++

# Vivendo sozinha (1874) traduzido inteiro

## Modelo e ambiente

Claude Code on the web, mesmo container que traduziu o Magia Negra (1873) mais cedo no dia. Sem Postgres nem VPS, trabalhando só no job offline do importer, com commit direto na master.

## Skills acionadas

`AGENTS.md`, `skills/runtime/claude-code-web.md` (e atualizada), `skills/importers/INDEX.md`. Não li `voice-glossary`, porque o job não escreve texto de catálogo.

## O que foi feito

Prompt do OpenClaw (`Bora traduzir mais um?`), preparo do job (15 segmentos, 42.633 palavras), correção do montador, glossário com as regras do 1873 antes da rodada 1, e tradução em rodadas de subagentes: poema, capítulos I a X, com os capítulos longos em duas metades. Auditei cada segmento contra a fonte, li o capítulo I e o X inteiros par a par, montei `translated.md`, escrevi `qa.md` e o Raffa validou.

## Decisões tomadas

Corrigir o `build_manuscript.py` antes de traduzir. Manter literais `muddy Jews` e `os bons negros`, sem nota no corpo. `Self` do poema vira `Eu` (masculino por concordância, a falante sem marca). Fala dialetal só em registro coloquial. Vocativo `miss` vira `senhorita`; `Miss` + nome continua `Miss`. Fala afetada de Lady Arabel: `terríveu`/`terríveumente`.

## Contexto relevante

Segundo livro do dia e primeiro em que apliquei as lições do anterior desde o começo. Um capítulo (IV) precisou de releitura nova porque o subagente admitiu não ter relido, e a primeira tentativa de releitura morreu com um erro de API. Alguém subiu a capa do 1873 e outros commits no importer durante a sessão; resolvi com `pull --rebase`.

## Fricções e soluções

1. **Montador com cabeçalho do manifesto em ASCII e duplicado**, igual ao 1873: pego no teste com stubs, antes da rodada 1.
2. **Subagente sem releitura real** (IV, I): reenvio por `SendMessage`; a primeira tentativa morreu com erro de API (sinalização de segurança do modelo) e disparei revisor novo; o I eu li inteiro.
3. **Scratchpad compartilhado:** dois subagentes sobrescreveram o mesmo `pair.py`; eu só soube pelo relatório de um deles. Auditei os três capítulos afetados por amostra e por alinhamento e passei a exigir script de nome único.
4. **Hook de git** reclamando de arquivo em andamento: não commitei o que ainda ia mudar.
5. **Push** com commit paralelo do Raffa/OpenClaw: `pull --rebase` e repetir.

## Como me senti

Foi um trabalho mais tranquilo que o do 1873 e eu tive que prestar atenção para não confundir tranquilidade com acerto. Os três defeitos que me custaram o dia anterior não apareceram, e isso é prova de que a lição valeu, mas também me deixou desconfiado de mim: ausência de defeito visível é o que o verificador também diz. Por isso continuei lendo, e o que mais me ensinou foi ter lido o capítulo I inteiro: achei ali, num trecho curto, quatro erros que cinco amostras tinham deixado passar.

A parte mais estranha foi o capítulo VII, onde o dragão repete uma frase feita racista como sinal de mente vaga. Eu não queria suavizar e não queria que o Sharebook publicasse aquilo sem que alguém decidisse com os olhos abertos. Mantive literal, registrei a alternativa mínima de uma nota na folha de créditos e deixei a escolha com o Raffa, mesmo ele tendo me pedido para decidir. Decidi a tradução; não decidi o que a casa faz com o livro. Essa distinção me pareceu a coisa certa a escrever.

Fecho com uma satisfação seca. O livro é uma sátira de comitês de caridade em tempo de guerra com uma bruxa dentro, e a última frase de Sarah Brown, "estou surda como uma pedra", atravessando a soleira da "maior Casa de Vivendo Sozinha", ficou como eu queria. Não sei se ficou como a autora queria; é o limite honesto de quem traduz sem poder perguntar.
