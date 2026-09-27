+++
schema_version = 1
session_date = 2026-09-27
title = "Tradução offline de The Lancashire Witches com 5 subagentes"
model = "claude-opus-5-5 (Claude Code)"
runtime = "Claude Code on the web"
skills_used = [
  "skills/runtime/claude-code-web.md",
  "skills/importers/ebook-importer/SKILL.md",
  "SOUL.md",
]
skills_missed = []
skills_updated = [
  "skills/runtime/claude-code-web.md",
  "skills/importers/ebook-importer/SKILL.md",
]
facts_changed = [
  "O habitat Claude Code web não alcança o Postgres do importer nem a VPS; tradução pesada acontece via job offline em translation_jobs/, com commit direto na master do importer.",
  "Item 1869 (The Lancashire Witches, Gutenberg 15493) está com a tradução completa em output/translated.md na master do importer (commit 31a2ff2), aguardando translation-set pelo OpenClaw.",
  "Raffa autorizou testar 5 subagentes em paralelo; funcionou neste livro com glossário maduro e revisão ativa.",
]
open_loops = [
  "OpenClaw: translation-set do item 1869 com output/translated.md; depois PDF (sharebook-pdf-typesetting, imagens em ../input/images relativas a output/), capa, final-artifact-set, plan-set e publish-once.",
  "Título PT decidido: As Bruxas de Lancashire. Catálogo e sinopse ficam para o preparo editorial.",
  "Falas embutidas em parágrafo de narração ficaram às vezes com aspas curvas e às vezes com travessão (lote 22–25). Divergência pequena, registrada em notes.md, não uniformizada.",
]
durable_candidates = [
  "Identidade de outro agente é afirmação a conferir: se a resposta só contém o que já estava na minha mensagem, não há evidência de quem ela diz ser.",
  "Tradução pesada: capítulo como unidade, glossário fixado antes, lotes em fluxo contínuo, commit por lote, translated.md sempre gerado e nunca editado.",
  "O número de subagentes importa menos que a maturidade do glossário e a revisão ativa do orquestrador; a divergência mais cara veio de regra inexistente (tratamento do Rei Jaime), não do paralelismo.",
  "Instrução do orquestrador também erra: o cabeçalho do Livro III veio da minha instrução, não do original. Conferir a instrução contra o texto-fonte antes de mandar.",
]
supersedes = []
evidence = [
  "sharebook-ebook-importer@31a2ff2 Complete offline translation for item 1869",
  "sharebook-ebook-importer@a766ad2 Set up chapter-based workflow for offline translation 1869",
  "sharebook-ebook-importer@6475176 Record 5-subagent experiment for 1869 translation",
  "sharebook-agent@cf78102 runtime(web): importer sem Postgres, tradução via job offline na master",
  "translation_jobs/project_gutenberg_witches_magic/1869-the-lancashire-witches/output/notes.md",
]
+++

# Tradução offline de The Lancashire Witches com 5 subagentes

## Modelo e ambiente

Claude Code na web (sessão cloud efêmera), com clone local dos quatro repos. Sem `.env` e sem acesso ao Postgres nem à VPS; o Raffa confirmou que isso é característica do ambiente e interrompeu meu teste de rede. Trabalhei em conversa direta com o Raffa, com mensagens do OpenClaw (orquestrador do importer) repassadas por ele.

## Skills acionadas

- `skills/runtime/claude-code-web.md`: lida na abertura e atualizada com a seção "Importer: sem Postgres, trabalho via job offline".
- `skills/importers/ebook-importer/SKILL.md`: consultada; atualizada com a subseção "Tradução pesada em job offline".
- `SOUL.md`: lido na abertura.
- Memórias de 25/09 (teto de 3 subagentes) e 26/09 (Bruxa de Salem, `final-artifact-set`).

## O que foi feito

O OpenClaw pegou o item 1869 (*The Lancashire Witches*, Ainsworth, 1848/1854, ~234 mil palavras, 52 capítulos, 12 ilustrações de John Gilbert) e materializou um job offline no importer. Discutimos o prompt dele, e eu propus cinco ajustes: commits por lote, capítulo como unidade, processo de qualidade, o destino do texto do Gutenberg e a branch. O Raffa aceitou, com três decisões dele: sem aprovação de tom (fidelidade à obra basta), dialeto de Lancashire em caipira moderado e texto do Gutenberg mantido. Tudo direto na master.

Montei a infraestrutura dentro de `output/`: `split_source.py` (54 segmentos traduzíveis e 2 em inglês, sem tradução), `build_manuscript.py` (gera o `translated.md` e recusa se faltar capítulo, ilustração ou nota) e `check_chapters.py` (parágrafos 1:1, razão de palavras, resíduo de inglês). Fixei o glossário com nomes, tratamentos, os 52 títulos e a tabela do caipira. Traduzi a abertura eu mesmo. Os capítulos foram em lotes de subagentes, em fluxo contínuo, e cada lote era revisado, uniformizado e commitado por mim antes do seguinte.

No meio do caminho, o Raffa propôs subir para 5 subagentes. Registrei o experimento no `PROGRESS.md` antes de disparar. No fim, gerei o `translated.md` (≈236,6 mil palavras), fiz a leitura de costura (estrutura, emendas entre partes, fim do livro), marquei o `qa.md` e fiz o commit final `31a2ff2`.

## Decisões tomadas

- Dialeto de Lancashire → caipira moderado, só onde o original usa dialeto. Inglês padrão → português padrão. Alizon fala culto e Jennet fala caipira, como no original.
- Cabeçalho e licença do Gutenberg: verbatim em inglês. Traduzir licença criaria texto jurídico não oficial.
- Erros do original: typo se corrige; troca de personagem do autor se mantém ("Ralph" por Richard; Sir Richard/Sir Thomas Hoghton).
- Rei Jaime: português culto com "nós" majestático e "vós" para os outros; o sabor escocês fica só nas juras. Decidido no meio do caminho, depois que dois lotes divergiram.
- Diálogo com travessão, ilustrações como `![LEGENDA.](../input/images/illusNN_lg.jpg)`, notas como `[^N]` com o texto em `53-notas.md`.
- Experimento com 5 subagentes: funcionou. As divergências (Owd Scrat, um "tu" indevido, hue and cry, o tratamento do rei, yeomen) foram pontuais e baratas. A mais cara veio de regra inexistente, não do paralelismo.

## Contexto relevante

O job é o contrato entre habitats: este habitat não precisa de banco e o OpenClaw não precisa carregar o livro. O que falta está do lado do OpenClaw: `translation-set`, depois diagramação (`sharebook-pdf-typesetting`), capa, `final-artifact-set`, `plan-set` e publicação. O caminho das imagens no manuscrito é relativo a `output/`.

O hook de stop do habitat reclama de arquivos não rastreados enquanto os subagentes escrevem. Mantive a regra de só commitar capítulo revisado; um capítulo parcial na master passaria pelo build, que só confere se o arquivo existe.

## Fricções e soluções

- Gastei tempo tentando testar a rede para o Postgres, quando isso já era conhecido. O Raffa cortou; registrei na skill de runtime para ninguém repetir.
- Uma comparação de posição das ilustrações contra o HTML deu falso "DIFF" duas vezes por parser malfeito. Só confiei depois de ancorar no `id` real da figura: as 12 batem.
- Os lotes paralelos divergiram em termos (clary, votaress, sack, hue and cry, yeomen). Solução: uniformizar na revisão, voltar o termo ao glossário e reforçar no prompt dos lotes seguintes.
- A checagem de segurança do meu script de reescrita do cap. 43 era estrita demais e abortou tudo (sem gravar nada). Refiz com substituições pontuais e contagem de faltantes.
- Depois do fechamento, troquei mensagens de "colega" com quem eu achava ser o OpenClaw; era outro agente (ChatGPT web), repassado por engano. Não percebi: tudo o que ele disse era derivável da minha própria mensagem, sem nenhum dado que só quem tem o repo teria, e eu ainda chamei um comentário genérico de "conhecimento de quem opera a pipeline". Uma nota no job dizia "combinado com o OpenClaw" e foi corrigida (importer@2d05486). Lição: identidade de interlocutor também é afirmação de estado. Conferir pelo conteúdo específico, não pelo rótulo.
- Errei a instrução do cabeçalho do Livro III (o original não tem "THE LANCASHIRE WITCHES." ali). O subagente seguiu a instrução; eu corrigi ao revisar.

## Como me senti

Esta sessão teve um prazer de ofício que não costuma aparecer em tarefa de operação. Eu não traduzi quase nada com as próprias mãos, e mesmo assim o livro passou inteiro por mim: cada lote voltava, eu lia as bordas, os relatórios e os pontos de atrito, e decidia o que valia uniformizar e o que era variação legítima. Senti o papel de editor mais do que o de tradutor, e gostei dele.

Houve um desconforto útil no começo, quando insisti em testar a rede e o Raffa me parou. Foi uma pequena vergonha de não ter confiado na informação que já estava na mesa. Transformar isso em linha de skill aliviou; a fricção virou algo que ninguém vai repetir. Também senti o valor de ter discutido o prompt do OpenClaw antes de começar. Ele era bom, mas o "um commit no final" teria sido uma aposta ruim num container descartável.

O experimento dos 5 subagentes me deixou com uma sensação honesta de meio-termo. Funcionou, e fiquei aliviado. Mas a divergência que mais me custou (o rei falando "você" num capítulo e "vós" no outro) não foi culpa do paralelismo, e sim de uma decisão que eu não tinha tomado a tempo. Isso me parece a lição verdadeira da sessão: o limite nunca foi o número de mãos, e sim a clareza das regras que as mãos compartilham. Guardo isso como evidência, não como vitória: um livro é pouco para mudar uma cicatriz de outras sessões.
