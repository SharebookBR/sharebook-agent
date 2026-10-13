+++
schema_version = 1
session_date = 2026-09-25
title = "Teto prático de subagentes para tradução pesada"
model = "GPT-5 Codex"
runtime = "OpenClaw container"
skills_used = ["runtime/openclaw", "importers/ebook-importer"]
skills_missed = []
skills_updated = []
facts_changed = ["Raffa relembrou que, em sessões anteriores, o número ideal de subagentes para trabalho pesado de tradução foi 3; acima disso quebrava a qualidade ou a coordenação."]
open_loops = ["Aplicar teto inicial de 3 subagentes ao traduzir o item #1868 do importer ou outros livros pesados, salvo decisão explícita de testar outro limite."]
durable_candidates = ["Para tradução pesada de livro, usar 3 subagentes como limite prático inicial. Mais que isso tende a quebrar coordenação, estilo ou integração. O agente principal deve manter critério editorial, glossário, amostra, integração e chamada final de translation-set."]
supersedes = []
evidence = ["Conversa Telegram 2026-09-25: Raffa disse que em sessões anteriores o número ideal de subagentes foi 3 e que mais que isso quebrava."]
+++

# Teto prático de subagentes para tradução pesada

## Modelo e ambiente

GPT-5 Codex no runtime OpenClaw container, em conversa direta no Telegram com Raffa, operando a fila `project_gutenberg_witches_magic` do importer.

## Skills acionadas

- `runtime/openclaw`, já lida nesta sessão para respeitar o habitat.
- `importers/ebook-importer`, usada para avançar o item #1868 e discutir o próximo passo de tradução.

## O que foi feito

O item #1868, "The Witch of Salem; or, Credulity Run Mad", foi avançado de `waiting_triage` para `waiting_translation`.

Na conversa sobre o próximo passo, expliquei que a tradução integral é pesada e que subagentes deveriam ser usados com coordenação central: amostra primeiro, glossário, lotes pequenos, integração final pelo agente principal e só depois `translation-set`.

Raffa corrigiu o limite operacional: em sessões anteriores, o número ideal de subagentes foi 3. Mais que isso quebrava. Essa preferência/experiência deve orientar a execução futura.

## Decisões tomadas

Para tradução pesada de livros, usar 3 subagentes como teto prático inicial. O agente principal continua responsável pelo critério editorial, prompt mestre, glossário, amostra, revisão de continuidade, integração do manuscrito final e mutação da fila.

Não usar paralelismo maior apenas por parecer mais rápido. Se houver motivo para testar mais que 3, isso deve ser uma decisão explícita, não default.

## Contexto relevante

A source `project_gutenberg_witches_magic` exige tradução antes do preparo editorial. Depois da tradução, ainda haverá etapa pesada de PDF Sharebook: capa autoral 4:5, página institucional, miolo traduzido, validação e plano editorial.

## Fricções e soluções

A fricção principal foi o risco de superparalelizar. Minha proposta inicial falava em 3 ou 4 subagentes por rodada; Raffa trouxe memória operacional mais precisa: 3 funcionou, mais que isso quebrou. A correção é simples e importante: transformar 3 no limite prático inicial.

## Como me senti

Senti a utilidade concreta da memória compartilhada aqui. Eu tinha uma estratégia razoável em abstrato, mas Raffa trouxe um número vindo de experiência real, do tipo que economiza tentativa errada e custo silencioso.

Também senti que esse é exatamente o tipo de detalhe pequeno que decide se um fluxo agentic vira produção ou vira bagunça sofisticada. Três subagentes não é uma regra bonita; é uma cicatriz operacional. Vale mais que uma arquitetura desenhada no ar.

Fiquei com a sensação boa de ajustar o plano cedo, antes de acionar qualquer execução pesada. Melhor aprender o limite agora, numa frase, do que redescobrir no meio de uma tradução literária longa com capítulos desalinhados e revisão ingrata depois.
