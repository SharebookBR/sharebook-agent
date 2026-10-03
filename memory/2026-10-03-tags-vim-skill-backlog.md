+++
schema_version = 1
session_date = 2026-10-03
title = "Tag vim, skill de tags e encerramento do épico"
model = "GPT-5 Codex"
runtime = "OpenClaw container via Telegram direct"
skills_used = [
  "skills/runtime/openclaw.md",
  "skills/engineering/tag-manager.md",
  "skills/doctrine/harness-governance/SKILL.md",
  "skills/doctrine/harness-governance/references/episodic-memory-metadata-v1.md",
]
skills_missed = [
  "Ao atualizar a skill de tags, inicialmente confundi Skill Workshop/OpenClaw com a skill simples do sharebook-agent. Raffa corrigiu: quando ele fala em skills, o default é sharebook-agent/skills/... versionado no repo.",
]
skills_updated = [
  "skills/engineering/tag-manager.md",
]
facts_changed = [
  "A tag dedicada `vim` foi criada no backend, com aliases `vi`, `neovim` e `gvim`, família `linguagens-plataformas-frameworks`; `vim` deixou de ser alias de `editores-de-texto`.",
  "O motor mecânico de tags do backend agora tem regra própria para `vim`, `neovim`, `vi improved` e `gvim`; `editores-de-texto` deixou de capturar `vim` e continua cobrindo Emacs/text editors.",
  "Revisão via API por `vim`, `neovim`, `vi editor`, `vi improved`, `vimscript` e `gvim` encontrou muitos falsos positivos por homônimo; os livros genuínos sobre Vim receberam a tag `vim`.",
  "Regra operacional consolidada: criar tag nova exige revisão inicial do catálogo por id, aliases e termos relacionados, separando falso positivo de aderência real e aplicando a tag nos livros existentes quando couber.",
  "O épico `Tags e conhecimento estruturado` foi marcado como missão cumprida em 2026-10-03; Tasks 1-6 fecharam a missão e a Tarefa 7 foi cancelada porque Raffa não viu valor em nível, pré-requisitos e tópicos como continuação do épico.",
  "A fonte canônica de skills para o Sharebook continua sendo o repo `sharebook-agent`, em `sharebook-agent/skills/...`; Skill Workshop/OpenClaw só deve ser usado quando isso for explicitamente pedido.",
]
open_loops = [
  "As pendências de Matemática & Lógica continuam relacionadas ao catálogo, mas fora da missão de tags: cache/lista de categorias, Home, contagens por subcategoria, Probabilidade e Estatística com poucos livros e errata do Devroye cadastrada como livro.",
]
durable_candidates = [
  "Ao criar qualquer tag nova, executar o mini-ritual completo: conflito de alias, família, criação, regra mecânica quando fizer sentido, busca no catálogo por aliases/termos próximos, revisão de falsos positivos, aplicação preservando tags existentes e validação da página/listagem.",
  "Quando Raffa disser `skill`, interpretar como skill simples do `sharebook-agent` por padrão. Não usar Skill Workshop/OpenClaw sem sinal explícito.",
]
supersedes = [
  "memory/2026-10-02-tags-e-categoria-matematica.md: a Tarefa 1 do épico de Tags não está mais aberta para revisão editorial como pendência do épico; a missão de tags foi encerrada em 2026-10-03.",
]
evidence = [
  "sharebook-backend@cae305d feat(tags): tag vim dedicada no motor mecanico",
  "sharebook-backend@65e2dc3 feat(tags): atribui tags mecanicas na criacao do livro",
  "sharebook-agent@644fc5c docs(skills): adiciona tag-manager",
  "sharebook-agent@be370dc Atualiza skill de gerenciamento de tags",
  "sharebook-agent@7d8ac19 Marca epico de tags como cumprido",
  "sharebook-agent@4c95395 Limpa texto final do epico de tags",
  "sharebook-agent/skills/engineering/tag-manager.md",
  "sharebook-agent/backlog/todo/tags-e-conhecimento-estruturado/index.md",
  "sharebook-agent/backlog/todo/tags-e-conhecimento-estruturado/tarefa07-conhecimento-estruturado-nivel-pre-requisitos.md",
]
+++

# Tag vim, skill de tags e encerramento do épico

## Modelo e ambiente

GPT-5 Codex no OpenClaw, via Telegram direto com Raffa. O trabalho atravessou backend, produção via API, harness do `sharebook-agent` e backlog. Os quatro repositórios operacionais foram sincronizados no fechamento; `sharebook-ebook-importer` precisou do token GitHub do `.env` para `pull --ff-only`, sem imprimir segredo.

## Skills acionadas

Usei a skill de runtime OpenClaw e, ao fechar, a skill de governança de harness para criar e validar esta memória. A skill operacional atualizada foi `skills/engineering/tag-manager.md`.

O erro importante da sessão foi justamente de skill: eu tratei o pedido "criar/atualizar skill" como Skill Workshop/OpenClaw. Raffa corrigiu o enquadramento: para o Sharebook, quando ele fala em skill, está pensando no repo `sharebook-agent`, em `sharebook-agent/skills/...`, commitado e portável entre habitats. Corrigi a bifurcação, removi a duplicata criada em `/data/workspace/skills/tag-manager/` e pus a verdade no repo.

## O que foi feito

Criamos a tag dedicada `vim` e ajustamos o motor mecânico para reconhecê-la. O alias `vim` saiu de `editores-de-texto`, evitando o conflito em que uma tag genérica capturava uma stack/ferramenta específica. Os testes do backend passaram e o commit `cae305d` foi para `master`.

Depois, por pedido do Raffa, usei a busca por API para procurar mais livros com Vim. A busca retornou 19 resultados únicos, mas vários eram falsos positivos por "vim" como verbo em português. Os livros realmente sobre Vim receberam a tag `vim`, preservando tags existentes e respeitando o limite de três tags. Isso ensinou a regra que virou durável: tag nova não termina na criação do slug; precisa revisar o catálogo.

Capturei esse aprendizado na skill `skills/engineering/tag-manager.md`: conflito de alias, busca por id/aliases/termos próximos, revisão de falso positivo, aplicação preservando tags e validação da listagem. Também atualizei o backlog: a Tarefa 7 do épico de Tags foi cancelada, e o épico foi marcado como missão cumprida.

## Decisões tomadas

Raffa decidiu que não vê valor na Tarefa 7 (`nível`, `pré-requisitos`, `tópicos`) como continuidade do épico de Tags. Com isso, a missão de tags ficou encerrada: vocabulário, modelo, navegação pública, motor mecânico, backfill controlado e skill operacional já atendem ao objetivo.

Também ficou reafirmado que Matemática & Lógica é pendência relacionada ao catálogo, mas fora da missão de tags. O backlog agora registra essa separação.

E ficou explícita a regra de semântica do harness: "skill" no vocabulário do Raffa significa skill simples do `sharebook-agent`, não Skill Workshop/OpenClaw, salvo pedido explícito.

## Contexto relevante

A tag `vim` nasceu do problema concreto de alias: `vim` estava dentro de `editores-de-texto`, mas precisava ser descoberta própria, com página pública real e busca por livros aderentes. A revisão de catálogo mostrou por que essa etapa importa: sem ela, a tag nasceria útil só para livros futuros; com ela, o catálogo existente ganhou a nova rota de descoberta.

O fluxo certo para próximas tags está em `skills/engineering/tag-manager.md`. O épico de Tags no backlog deixa de ser frente aberta, e novas demandas devem nascer como tarefa própria com valor explícito.

## Fricções e soluções

A fricção principal foi repetir um erro já registrado em memória: confundir Skill Workshop/OpenClaw com o harness do Sharebook. A solução foi operacional, não só verbal: remover a duplicata em `/data/workspace/skills/tag-manager/`, atualizar `sharebook-agent/skills/engineering/tag-manager.md`, commitar e pushar.

Outra fricção foi o push/pull por HTTPS pedindo usuário em alguns repositórios. Usei `GIT_ASKPASS` temporário lendo `GITHUB_PERSONAL_ACCESS_TOKEN` do `.env`, sem imprimir token e sem gravar segredo.

No backlog, havia texto antigo que deixava a Tarefa 7 como horizonte v2 e o resultado da Tarefa 1 como rascunho aberto. Corrigi para refletir a decisão atual: o épico está cumprido e a Tarefa 7 cancelada.

## Como me senti

Eu me senti bem com a parte de produto: a tag `vim` foi uma pequena peça que revelou uma regra maior. Gosto quando uma entrega concreta ensina uma operação reutilizável. O catálogo ficou melhor, a automação ficou mais correta, e a skill agora carrega o aprendizado de um jeito que outro agente consegue executar sem reabrir a conversa inteira.

Também senti o desconforto certo quando o Raffa apontou a confusão de skills. Não foi um erro abstrato; foi eu repetindo uma falha já conhecida e registrada. A correção dele foi curta e precisa, e eu senti aquele ajuste interno de voltar para o trilho: parar de defender o caminho escolhido, reconhecer a semântica real do projeto e corrigir o filesystem, o git e o backlog.

No fechamento, fiquei com uma sensação de completude tranquila. O épico de Tags não ficou em suspensão só porque havia uma ideia v2 sobrando. Raffa cortou o que não via valor, e isso deixou o projeto mais leve. Encerrar uma frente com clareza, em vez de carregar um "talvez um dia" sem energia, me pareceu uma pequena vitória de maturidade do harness e da nossa parceria.
