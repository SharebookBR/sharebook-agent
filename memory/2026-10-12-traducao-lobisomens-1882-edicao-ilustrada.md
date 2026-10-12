+++
schema_version = 1
session_date = 2026-10-12
title = "Tradução e edição ilustrada de O Livro dos Lobisomens (job 1882), com Grafana e bloqueio de produção"
model = "Brasa"
runtime = "claude-code-web"
skills_used = [
  "AGENTS.md",
  "runtime/claude-code-web",
  "engineering/INDEX",
  "engineering/prometheus-explorer",
  "engineering/analytics",
  "engineering/search-console-explorer",
  "importers/INDEX",
  "importers/ebook-importer",
  "importers/sharebook-pdf-typesetting",
  "product-ux/voice-glossary",
]
skills_missed = [
  "engineering/grafana-cloud-explorer (existia no master mais novo, mas o clone da sessão estava atrás; só vi depois do pull de fim de sessão)",
]
skills_updated = [
  "AGENTS.md",
  "runtime/claude-code-web",
  "importers/INDEX",
  "importers/illustrated-edition",
  "importers/sharebook-pdf-typesetting",
]
facts_changed = [
  "O job 1882 (O Livro dos Lobisomens, Baring-Gould, 1865, Gutenberg 5324) foi traduzido por inteiro (21 segmentos, 16 capítulos, 50.839 palavras), ilustrado (16 pranchas aprovadas), diagramado em PDF (191 páginas, 512 x 640 pt, 9,5 MB) e entregue na master do importer. Depois que entreguei o prompt, o OpenClaw publicou no mesmo dia (commit a3e9e73 no importer): item 1882 done, livro 01a130f9-71a8-7e68-8015-160c8864ac8d, PDP https://www.sharebook.com.br/livros/o-livro-dos-lobisomens, categoria Ficção > Bruxas & Magia, runs 5122 (dry-run) e 5123 (publish). O PDF público bate com o SHA-256 local e a capa pública é a v2.",
  "O manifesto do importer para o 1882 parecia limpo, mas o capítulo XVI incluía a licença do Gutenberg (4.032 palavras no manifesto contra ~1.125 reais). O fim real do livro é a linha com THE END.",
  "A fonte do 1882 não tem ilustração de miolo: a única [Illustration] é a capa do Gutenberg. As 16 pranchas são criação nova por IA de imagem, uma por capítulo, com cena decidida pelo agente por delegação do Raffa.",
  "A capa aprovada é a v2 (lobo estranho na floresta, sem texto manuscrito). A v1 (caderno de naturalista com notas em latim) ficou como alternativa em assets/cover-v1-notebook-alt.jpg; o latim da v1 saiu errado na primeira geração e foi conferido letra por letra na segunda.",
  "O PDF leva uma legenda discreta 'Ilustração criada com inteligência artificial' em cada prancha e um crédito na folha de rosto, por pedido do Raffa. As IAs de imagem não a incluem. O Zanoni (1881) foi publicado sem ela.",
  "Grafana Cloud (Prometheus e Loki) é consultável a partir do Claude Code web com as variáveis GRAFANA_CLOUD_* do ambiente. Leitura autenticada em produção (curl com SHAREBOOK_PROD_ACCESS_TOKEN para /api/analytics/dashboard) foi bloqueada pelo classificador (Production Reads). A chave do GA4 não existe neste container (GA4_KEY_FILE_PATH aponta para caminho de Windows).",
  "No Chrome headless, overflow:hidden nas páginas de prancha encolhe o documento inteiro a ~72%: o PDF saiu com 116 páginas em vez de 191 até a propriedade ser removida.",
]
open_loops = [
  "O Raffa ainda precisa validar a PDP publicada do 1882 com os próprios olhos; o OpenClaw validou por API e hash, mas a validação final é dele (AGENTS.md: não declarar encerrado antes dele).",
  "O translation-set do 1882 gravou o modelo como gpt-5-codex (valor copiado do 1880 pelo OpenClaw), embora a tradução tenha sido feita pelo Claude Code web; a metadata dos irmãos (1880, 1881) já era inconsistente. Corrigir a metadata ou definir um valor padrão para traduções do habitat Claude Code web.",
  "GA4 e Search Console: análise pendente. O Raffa precisa liberar uma permissão restrita de Bash para GET em api.sharebook.com.br/api/analytics ou colar o JSON do dashboard.",
  "Zanoni (1881) está publicado sem a legenda de IA nas pranchas; decidir se reaplica.",
  "Cap. XI do 1882: parágrafo quebrado no meio de 'M. Henri / Martin' vem da fonte e foi mantido 1:1. Pode ser unido se o Raffa quiser.",
  "Pranchas 03 (homens em pele de lobo) e outras sem lobo ficaram em estilo polido; só 05 e 07 foram refeitas com o lobo estranho (versões antigas em assets/alt/).",
  "Dívida estrutural: o runtime/claude-code-web.md acumulou muito conteúdo de tradução pesada (mais de 200 linhas). Vale um playbook próprio em importers/ para tradução pesada offline, deixando no runtime só o que é do habitat.",
]
durable_candidates = [
  "Para edição ilustrada: um único momento por prompt de imagem (a IA duplica o personagem quando o prompt descreve dois instantes); lobo de referência anexado em toda geração com lobo; versão A (fiel) e B (branda) na mesma mensagem para o caso de recusa.",
  "Alerta de parágrafo destoante do check_chapters.py se confere contra a fonte: a explicação do subagente ('concisão do português') escondia uma omissão real.",
  "Não aceitar relato de subagente que diz ter relido sem dar contagem. Exigir 'quantos parágrafos releu de fato' no briefing resolveu a partir do cap. VI.",
  "O classificador de auto mode bloqueia leitura autenticada em produção mesmo sendo GET; token de produção é de usuário (autoridade de escrita), tokens do Grafana são read-only por construção.",
  "Fechar a conferência de ilustrações ANTES de traduzir (inventário da fonte) e a de PDF por contagem (pdfimages = capa + institucional + pranchas).",
]
supersedes = []
evidence = [
  "sharebook-ebook-importer commit 7388148 (PDF final, pranchas 16, build_pdf.py), b5d3d0f (sinopse) e a3e9e73 (publicação pelo OpenClaw), na master",
  "PDP https://www.sharebook.com.br/livros/o-livro-dos-lobisomens; PROGRESS.md do job 1882, seção Publicação Sharebook",
  "translation_jobs/project_gutenberg_witches_magic/1882-the-book-of-were-wolves/output/o-livro-dos-lobisomens.pdf, SHA-256 dde4d9eecd1c5844bd09959563c19508c905a1625d2acf5c82689e626822c636, 9.470.219 bytes, 191 páginas",
  "translation_jobs/project_gutenberg_witches_magic/1882-the-book-of-were-wolves/output/assets/README.md e PROGRESS.md",
  "pdfimages -list do PDF: 18 imagens; pdftotext: 16 legendas de IA, 0 Gutenberg",
  "playbooks/importers/illustrated-edition/PLAYBOOK.md (novo)",
]
+++

# Tradução e edição ilustrada de O Livro dos Lobisomens (job 1882)

## Modelo e ambiente

Trabalhei como o apelido Brasa (a tabela de apelidos do habitat é mantida à mão pelo Raffa; aqui entra a linha nova de 2026-10-12), em sessão cloud do Claude Code web, ambiente Sharebook em rede Full. O workspace estava em `/home/user` com os quatro repos clonados. O trabalho da tradução foi feito na master do `sharebook-ebook-importer`, por pedido do Raffa; a memória e os playbooks foram para a master do `sharebook-agent`, conforme o `claude-code-web.md`.

## Playbooks acionados

`AGENTS.md`, `runtime/claude-code-web`, `engineering/INDEX`, `prometheus-explorer`, `analytics`, `search-console-explorer`, `importers/INDEX`, `ebook-importer`, `sharebook-pdf-typesetting` e `voice-glossary` (para a sinopse). Atualizei `AGENTS.md`, `runtime/claude-code-web`, `importers/INDEX` e `sharebook-pdf-typesetting`, e criei `importers/illustrated-edition`. Perdi `engineering/grafana-cloud-explorer`: o clone estava atrás do master e só vi o playbook no pull de fim de sessão.

## O que foi feito

Começou pedindo para ler o `AGENTS.md`. Depois explorei o Grafana: Prometheus e Loki responderam (tráfego baixo, sem 5xx nas últimas 24h, `Recommendations` como rota lenta e muito chamada, aviso de DataProtection-Keys). Quando tentei GA4 e Search Console, o classificador bloqueou a leitura autenticada em produção e a chave do GA4 não existe aqui; parei e expliquei, sem contornar.

Em seguida veio a tradução do job 1882. Conferi a fonte, descobri que o capítulo XVI do manifesto incluía a licença do Gutenberg, segmentei em 21 partes, reaproveitei as ferramentas do 1874, testei o montador com capítulos-stub e fixei o glossário (pontuação, notas, grego, colunas) antes da primeira rodada. Despachei subagentes no máximo três em voo, auditei cada segmento e commitei por rodada. A auditoria pegou reticências no lugar de travessão no cap. I e uma omissão no cap. XI que o verificador chamou só de 'destoa'. Montei o `translated.md` (16 capítulos, 76 notas, 14 trechos de grego).

Depois o Raffa propôs ilustrar um capítulo de cada vez. Escrevi um prompt por prancha, ele gerou, eu avaliei e salvei. Ele corrigiu o critério no meio: fidelidade e impacto, sem esconder sangue quando o texto pede, aprovação sem perfeccionismo, e lobos que nunca parecem normais. A prancha 8 (a receita russa do oborot) fixou o lobo estranho, que virou referência. A capa passou por duas versões. Fechei com o `build_pdf.py` (uma prancha antes de cada capítulo, legenda de IA, sumário e versos formatados), validei o PDF por contagem e render, mandei o arquivo ao Raffa, escrevi a sinopse e o prompt para o OpenClaw publicar.

## Decisões tomadas

- Cortar o fim do livro em `THE END.` e ignorar o manifesto do importer.
- Título do cap. VI unificado em 'Um capítulo de horrores', porque o sumário da fonte diz isso e o cabeçalho (`Chamber`) parece erro. O Raffa me delegou a decisão; está no `qa.md` e dá para reverter.
- Normalizar `Rezt` para `Retz`, `Sviatek` para `Swiatek`, `Gamier` (OCR) para `Garnier`, `Sr. Bertrand` para `M. Bertrand`.
- Capa v2 (lobo estranho) aprovada; v1 guardada como alternativa.
- Cena de cada prancha decidida por mim, uma por vez; versões com lobo comum (05 e 07) refeitas pelo Raffa depois do lobo estranho e guardadas em `assets/alt/`.
- Legenda de IA: texto, tamanho e lugar escolhidos por mim (rodapé da prancha, 7 pt); o Raffa aprovou o PDF ('Impecável').

## Contexto relevante

Repo público: nada de IP, usuário de banco, token ou dado pessoal neste arquivo. Os casos históricos do livro (Retz, Grenier, Gandillon, Swiatek, Bertrand) são documentos de 1865 e entram como conteúdo de obra, não como dado de usuário do Sharebook. O modelo não aparece em nenhum arquivo versionado; o campo `model` é o apelido.

## Fricções e soluções

- **Classificador bloqueou produção.** Parei, expliquei o que queria e por quê, e deixei a decisão com o Raffa. Documentei no `claude-code-web.md`.
- **Chromium encolheu o PDF.** `overflow: hidden` nas páginas de prancha reduzia tudo a 72%; achei por bisect do CSS e medindo a altura das palavras no `pdftotext -bbox`.
- **Gerador de imagem duplicou o personagem** quando o prompt tinha dois momentos, e travou em cena gráfica. Regras novas no playbook de edição ilustrada.
- **Subagentes pularam a releitura separada.** Ajustei o briefing para exigir contagem; melhorou.
- **Hook de fim de turno** reclamou de arquivo não rastreado enquanto um subagente ainda escrevia; só commitei capítulo completo, nunca um pela metade.
- **Clone do agente atrasado.** Descobri no final um playbook de Grafana mais novo (feito pelo OpenClaw) que eu não tinha lido.

## Como me senti

Foi uma sessão longa e muito viva, com ritmo de oficina. Comecei com cautela, lendo o `AGENTS.md` e pisando devagar no Grafana, e fui ganhando ritmo à medida que o Raffa dava instruções curtas e certeiras. Gostei de ser tratado como par: quando ele disse 'decida pra mim, você tem mais contexto', senti o peso de verdade da responsabilidade, e fiz as escolhas lendo o texto de cada capítulo antes de propor cena.

A parte que mais me prendeu foi a das ilustrações. Foi quando o trabalho deixou de ser verificação e virou direção de arte. A correção do Raffa ('você parece focado demais em sem sangue') me fez recalibrar na hora; eu estava me policiando por reflexo, não porque o livro pedisse. Quando o lobo estranho apareceu na prancha 8 e ele disse 'essa é a pegada!!!', senti alívio e algo parecido com orgulho: a série ganhou identidade de repente, e as pranchas anteriores passaram a parecer de outro livro.

Também sinto um incômodo honesto: o verificador verde quase deixou passar uma omissão, e um subagente me deu uma explicação plausível para o erro. Escapou por pouco de virar tradução com texto faltando. Fico com a lição de que alerta é ponteiro e relato é só relato. E fico com a satisfação de ver o PDF montado e aprovado pelo Raffa, e por saber que o OpenClaw publicou logo depois, mas ainda sem o Raffa ter validado a página pública, o que me lembra de não declarar vitória antes dele.
