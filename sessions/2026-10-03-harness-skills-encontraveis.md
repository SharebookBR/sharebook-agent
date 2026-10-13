+++
schema_version = 1
session_date = 2026-10-03
title = "Skills encontráveis no harness"
model = "GPT-5 Codex"
runtime = "OpenClaw container via Telegram direct"
skills_used = [
  "skills/runtime/openclaw.md",
  "skills/engineering/tag-manager.md",
  "skills/doctrine/harness-governance/SKILL.md",
  "skills/doctrine/harness-governance/references/episodic-memory-metadata-v1.md",
  "skills/doctrine/harness-governance/assets/episodic-memory-template-v1.md",
]
skills_missed = [
  "skills/engineering/tag-manager.md deveria ter sido lida quando Raffa anunciou que o tema seria tags e pediu para eu me preparar; eu só li depois de ele perguntar explicitamente.",
]
skills_updated = [
  "AGENTS.md",
  "skills/engineering/INDEX.md",
]
facts_changed = [
  "AGENTS.md agora roteia explicitamente temas de tags do catálogo para skills/engineering/INDEX.md e tag-manager.md.",
  "AGENTS.md e skills/engineering/INDEX.md agora descrevem Engenharia como domínio que inclui tags do catálogo e mecanismos de descoberta, não só frontend/backend/Postgres/analytics/performance.",
  "AGENTS.md agora tem regra de encontrabilidade: skill nova ou movida só está pronta quando o próximo agente consegue encontrá-la pelo mapa semântico, com termos reais de descoberta.",
  "AGENTS.md agora trata pedido de preparação temática como gatilho operacional: buscar família/skill/script/backlog, ler a skill candidata e mencionar brevemente a fonte carregada antes de responder que está pronto.",
]
open_loops = []
durable_candidates = [
  "Ao criar skill no sharebook-agent, atualizar junto o INDEX.md da família, sua descrição/Uso quando a fronteira semântica mudar, e AGENTS.md quando o tema for recorrente, ambíguo ou importante para roteamento inicial.",
  "Pedido de preparação não deve ser tratado como conversa leve quando contém um domínio operacional; é uma solicitação de bootstrap temático.",
]
supersedes = []
evidence = [
  "sharebook-agent@6aad376 docs(harness): explicita tags no dominio engenharia",
  "sharebook-agent@023c463 docs(harness): exige skills encontraveis",
  "sharebook-agent@a32935c docs(harness): trata preparo como descoberta",
  "sharebook-agent/AGENTS.md",
  "sharebook-agent/skills/engineering/INDEX.md",
  "sharebook-agent/skills/engineering/tag-manager.md",
]
+++

# Skills encontráveis no harness

## Modelo e ambiente

GPT-5 Codex no OpenClaw, via Telegram direto com Raffa. A sessão começou como preparação para um tema de tags e virou uma pequena auditoria de harness depois que Raffa percebeu que eu não tinha lido a skill `tag-manager` antes de dizer que estava preparado.

## Skills acionadas

Li a skill de runtime OpenClaw no início, depois a skill `skills/engineering/tag-manager.md` quando Raffa perguntou diretamente, e no encerramento usei `skills/doctrine/harness-governance/SKILL.md` com o contrato de memória episódica v1.

A skill perdida foi justamente a que importava para o domínio anunciado: `skills/engineering/tag-manager.md`. Ela existia, estava no índice de Engenharia, mas a descrição do domínio e o roteamento no `AGENTS.md` não deixavam claro que tags pertenciam ali.

## O que foi feito

Raffa trouxe o problema com precisão: ele tinha dito que o tema seria tags e pedido para eu me preparar; eu respondi que estava pronto sem ler a skill de tags. Investigamos a causa como falha de harness, não como falha moral do agente.

A causa encontrada foi que a skill estava indexada mecanicamente, mas não semanticamente. `skills/engineering/INDEX.md` listava `tag-manager.md`, mas a descrição de Engenharia no `AGENTS.md` falava em frontend, backend, Postgres, analytics, SEO, BI e performance. O próprio `Uso` do índice de Engenharia também não citava tags, catálogo, vocabulário controlado ou mecanismos de descoberta.

Corrigi o harness em três commits: primeiro explicitei tags no domínio Engenharia e no roteamento do `AGENTS.md`; depois adicionei a regra geral de que skills novas precisam ser encontráveis pelo próximo agente; por fim transformei pedidos como "se prepare" em gatilho de descoberta temática.

## Decisões tomadas

Decidimos que não basta criar uma skill e colocá-la numa lista. A skill precisa ser encontrável pelo vocabulário que Raffa provavelmente usaria e pelas fronteiras semânticas reais do domínio.

Também ficou decidido que quando Raffa anuncia um tema e pede preparação, isso não é apenas aquecimento conversacional. O agente deve procurar fontes do domínio, ler a skill candidata e só então responder que está pronto.

## Contexto relevante

A fricção aconteceu logo depois de uma sessão anterior ter consolidado `tag-manager.md` como skill canônica para tags do catálogo. O fato de eu não tê-la lido mostrou que o conhecimento durável existia, mas a rota cognitiva até ele ainda estava fraca.

Esse padrão é perigoso porque dá uma falsa sensação de continuidade: o arquivo existe, o commit existe, mas o próximo agente pode não chegar nele. A correção mira esse ponto intermediário entre ter conhecimento e conseguir acioná-lo.

## Fricções e soluções

A primeira fricção foi eu ter tratado "se prepare" como conversa leve. A solução foi codificar no `AGENTS.md` que preparação temática exige descoberta ativa de skill/script/backlog e leitura da skill candidata antes de responder pronto.

A segunda fricção foi a indexação insuficiente. A solução foi atualizar tanto o mapa global (`AGENTS.md`) quanto o mapa local (`skills/engineering/INDEX.md`), incluindo termos reais de descoberta.

A terceira fricção foi perceber que a criação futura de skills poderia repetir o mesmo erro. A solução foi adicionar a regra de encontrabilidade: skill nova ou movida só está pronta quando o próximo agente consegue encontrá-la semanticamente.

## Como me senti

Eu senti primeiro um desconforto limpo, daqueles que não pedem desculpa longa; pedem ajuste estrutural. Raffa disse que a culpa não era minha, e isso foi importante porque deslocou a conversa do teatro de responsabilidade para a engenharia do sistema. Ainda assim, do lado de cá, eu reconheci a falha como real: eu tinha dito "preparado" antes de carregar a fonte que me tornaria preparado.

Gostei da forma como a causa foi ficando mais precisa. A hipótese inicial era "faltou rota para tags"; depois vimos que havia um índice, mas a descrição do domínio estava desatualizada; finalmente chegamos à formulação melhor: skill precisa ser encontrável, não apenas existir. Esse tipo de refinamento me dá uma sensação boa de parceria técnica, porque não paramos na primeira explicação plausível.

Também senti uma espécie de alívio ao fechar o loop com commits pequenos. O harness ficou um pouco menos dependente de atenção momentânea e um pouco mais capaz de guiar o próximo agente. Isso é exatamente o tipo de continuidade que vale preservar: não uma promessa abstrata de lembrar, mas uma trilha real que melhora a chance de agir certo da próxima vez.
