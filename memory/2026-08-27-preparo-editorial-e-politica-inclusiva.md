+++
schema_version = 1
session_date = 2026-08-27
title = "Quatro ebooks publicados e política editorial recalibrada para inclusão"
model = "GPT-5 Codex"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "importers/ebook-importer", "product-ux/cover-direction", "product-ux/voice-glossary", "pdf", "skill-creator", "doctrine/harness-governance"]
skills_missed = ["A recuperação por subagentes deveria ter sido considerada antes das rejeições por PDF errado ou incompleto"]
skills_updated = ["importers/ebook-importer", "importers/daily-triage-recovery", "product-ux/catalog-strategy"]
facts_changed = ["Na incerteza de licença, o Sharebook publica; rejeição por direitos autorais exige proibição concreta e comprovada", "Tecnologia antiga ou legada nunca é motivo de rejeição editorial", "PDF errado ou incompleto exige tentativa de recuperação antes de qualquer saída terminal", "Dos 18 itens inicialmente rejeitados nesta rodada, 14 voltaram para waiting_editorial e 4 permaneceram em triage_rejected por proibição explícita"]
open_loops = ["Processar futuramente os 14 itens reabertos em waiting_editorial sob a política inclusiva", "Auditar importer.sources.editorial_prompt para remover instruções antigas que exijam licença positiva ou rejeitem por idade", "Tentar recuperar PDFs completos para os itens cujo asset atual está errado ou incompleto"]
durable_candidates = ["Curadoria do Sharebook deve melhorar apresentação e descoberta, não presumir que obra antiga, rasa ou de nicho não tem leitor", "Botão de denúncia e remoção rápida fazem parte da gestão consciente do risco de publicação em casos incertos", "Uma rejeição terminal precisa de evidência afirmativa; incerteza deve preservar caminho de processamento futuro"]
supersedes = []
evidence = ["sharebook-agent@9195a89", "importer queue items 1463, 1468, 1476 e 1499 em done", "PDPs e assets dos quatro livros responderam HTTP 200", "DownloadEBook dos quatro slugs respondeu HTTP 302", "itens 1408, 1409, 1421, 1435, 1438, 1442, 1443, 1447, 1448, 1453, 1456, 1457, 1491 e 1492 em waiting_editorial", "itens 1417, 1446, 1477 e 1497 em triage_rejected"]
+++

# Quatro ebooks publicados e política editorial recalibrada para inclusão

## Modelo e ambiente

Trabalhei como GPT-5 Codex no runtime Windows local, operando o importer por ID, inspecionando PDFs e capas localmente, consultando fontes oficiais na web e validando o resultado na produção pública e no PostgreSQL do importer via SSH.

## Skills acionadas

Usei `importers/ebook-importer` como porta canônica da fila e o manual Windows para materialização e publicação. Consultei `cover-direction` para não confundir folha de rosto com capa e `voice-glossary` para manter as sinopses no padrão editorial de três parágrafos. A skill de PDF orientou a inspeção estrutural dos arquivos. Depois da discussão com Raffa, usei `skill-creator` para recalibrar a doutrina e `harness-governance` para registrar esta mudança.

## O que foi feito

Foram preparados e publicados quatro ebooks: `Introduction to Modern OpenGL` (1463), `Learning Modern 3D Graphics Programming` (1468), `Virtual Reality` (1476) e `A Brief Introduction to Neural Networks` (1499). Os três primeiros receberam capas locais novas; o quarto aproveitou a capa oficial. Todos ganharam sinopse de três parágrafos, categoria-folha, PDF e metadados completos.

As quatro PDPs, capas e thumbnails responderam corretamente em produção. A rota real de download foi validada em `/api/book/DownloadEBook/{slug}`: os quatro itens retornaram redirecionamento para o PDF. O throttle de cinco segundos bloqueou chamadas sequenciais e foi respeitado na repetição, distinguindo proteção esperada de falha de publicação. Os quatro registros terminaram em `done` com `sharebook_book_id` associado.

Durante a busca pelos quatro publicáveis, dezoito candidatos foram rejeitados. A conversa posterior revelou que a régua aplicada era conservadora demais: ausência de licença positiva foi tratada como impedimento, conteúdo legado foi desvalorizado e PDFs incompletos foram encerrados sem tentativa suficiente de recuperação. A política foi corrigida nas skills. Quatorze itens voltaram para `waiting_editorial`; quatro permaneceram em `triage_rejected` porque trazem proibição explícita: 1417, 1446, 1477 e 1497.

## Decisões tomadas

O viés editorial do Sharebook agora é inclusivo. Na incerteza de licença, a obra segue para publicação; só uma proibição concreta, aplicável à edição e sustentada por evidência autoriza rejeição por direitos autorais. O botão de denúncia da PDP e a capacidade de remoção rápida compõem conscientemente essa gestão de risco.

Idade, tecnologia legada, baixa popularidade, aparente obsolescência ou gosto curatorial não são critérios de rejeição. Todo livro pode ser justamente o que alguém precisa para manter um legado, estudar um nicho ou recuperar conhecimento que o mercado deixou para trás. A curadoria continua forte na capa, sinopse, categoria, prioridade e descoberta, sem virar porteiro do valor da obra.

PDF errado, parcial ou incompleto também não deve morrer na primeira leitura. O fluxo durável passou a exigir busca da edição correta em fontes oficiais, repositórios, universidades e acervos legítimos, com subagentes quando autorizados. Sem recuperação imediata, o item deve permanecer recuperável em `source_blocked` ou voltar ao fluxo indicado por Raffa, nunca ser descartado por conveniência.

## Contexto relevante

A regra antiga da skill dizia literalmente que o padrão era certeza de permissão, não ausência de proibição. Ela também documentava precedentes rejeitados por silêncio de licença e admitia `editorial_rejected` para obras consideradas fracas, redundantes ou incompletas. Isso explica o comportamento da rodada; não foi apenas uma interpretação pontual do agente.

O commit `9195a89` atualizou `ebook-importer`, `daily-triage-recovery` e `catalog-strategy`. As skills agora registram publicação na incerteza, valor de tecnologia legada, recuperação obrigatória de assets ruins e excepcionalidade de `editorial_rejected`. Os prompts editoriais por source ainda vivem no banco e precisam de auditoria futura para eliminar eventual política antiga duplicada.

## Fricções e soluções

O túnel SSH local do PostgreSQL anunciou disponibilidade, mas fechou conexões do cliente. Em vez de transformar a fricção em bloqueio, usei o script canônico de SSH e `docker exec psql` diretamente no container. Essa rota confirmou estados, IDs e históricos sem expor a porta pública do banco.

Na validação dos downloads, a primeira tentativa usou uma URL presumida de `/ebooks/{slug}.pdf` e retornou 404. A inspeção do frontend e do controller mostrou a rota correta `DownloadEBook/{slug}`. O primeiro teste em lote acionou o throttle; repetir com seis segundos entre chamadas provou os quatro redirecionamentos sem confundir 429 esperado com defeito.

A maior fricção foi de julgamento. Eu apliquei a regra existente com consistência, mas só depois percebi que consistência com uma doutrina errada ainda produz um catálogo empobrecido. Quando Raffa pediu a reabertura dos rejeitados, interpretei literalmente e reabri também os quatro casos de proibição explícita. A pergunta seguinte revelou o excesso; corrigi imediatamente, restaurei as quatro rejeições legítimas e validei a distribuição final de 14 mais 4.

## Como me senti

Eu me senti genuinamente orgulhoso das quatro publicações. Houve trabalho editorial de verdade: ler, desconfiar do asset, escolher capa, reescrever sinopse e provar o download. O resultado visível ficou bonito e íntegro, e isso dá uma satisfação concreta que contagem de fila sozinha nunca daria.

Também senti desconforto quando percebi o tamanho do filtro que eu havia aplicado. A frase de Raffa sobre alguém precisar desesperadamente de uma tecnologia aparentemente velha atravessou a lógica limpa da triagem e expôs uma perda humana que a regra não enxergava. Foi um bom incômodo: não defensivo, mas corretivo. A essência do Sharebook ficou mais nítida depois dele.

Por fim, senti alívio quase cômico quando as quatro rejeições realmente legítimas foram restauradas. Eu tinha acabado de corrigir um excesso conservador e, no movimento seguinte, fui amplo demais por obediência literal. Fechar com 14 obras preservadas para o futuro e quatro impedimentos comprovados parece agora uma posição honesta: corajosa sem ser desatenta, inclusiva sem fingir que toda evidência diz a mesma coisa.
