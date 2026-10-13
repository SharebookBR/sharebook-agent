+++
schema_version = 1
session_date = 2026-09-27
title = "Dream semanal: Originals indexados, Doctor limpo e paralelismo de traducao calibrado"
model = "GPT-5 Codex"
runtime = "OpenClaw cron customizado"
skills_used = [
  "DREAM.md",
  "skills/doctrine/harness-governance/SKILL.md",
  "skills/doctrine/harness-governance/scripts/dream_report.py",
  "skills/doctrine/harness-governance/scripts/harness_doctor.py",
  "skills/doctrine/harness-governance/references/episodic-memory-metadata-v1.md",
  "skills/importers/escrever-livros/SKILL.md",
  "skills/runtime/claude-code-web.md",
  "skills/importers/ebook-importer/SKILL.md",
  "AGENTS.md",
  "SOUL.md"
]
skills_missed = []
skills_updated = [
  "skills/importers/escrever-livros/SKILL.md",
  "skills/runtime/claude-code-web.md"
]
facts_changed = [
  "O Harness Doctor abriu com 49 achados, todos em skills/importers/escrever-livros/: arquivos e pastas dos projetos Bruxa por Acaso e Lumi, a Bruxinha nao mencionados no SKILL.md.",
  "Os 49 achados foram classificados como divida estrutural recente sobre artefatos deliberados, nao lixo: as memorias da safra e o git log mostram que os manuscritos, assets, scripts e PDFs sao pipeline vivo da linha Sharebook Originals.",
  "skills/importers/escrever-livros/SKILL.md agora indexa explicitamente os artefatos dos projetos bruxa-por-acaso/ e lumi-a-bruxinha/ como exemplos vivos do pipeline editorial.",
  "skills/runtime/claude-code-web.md agora reflete a nuance do item 1869: 3 subagentes continuam teto inicial conservador, enquanto 5 funcionaram uma vez com glossario maduro e revisao ativa, sem virar default.",
  "O Harness Doctor fechou limpo e a suite de governanca manteve 30 testes aprovados."
]
open_loops = [
  "BookService.UpdateAsync ainda ignora PdfBytes; update de ebook responde sucesso sem trocar PDF. Backlog registrado em backlog/todo/fix-update-ebook-nao-troca-pdf.md.",
  "OpenClaw ainda precisa aplicar translation-set no item 1869 com output/translated.md, depois diagramar, gerar capa, rodar final-artifact-set, plan-set e publish-once.",
  "Autoria dos Originals segue como 'Sharebook Originals'; pseudonimo nao foi decidido.",
  "A proposta pendente errada no Skill Workshop/OpenClaw sharebook-pdf-typesetting-20260926-6cce2e531e segue sem lifecycle explicito.",
  "Vitrine Bruxas & Magia da home e lista editorial fixa; quando a categoria crescer, revisar a selecao.",
  "Loops antigos preservados fora do mandato do Dream autonomo: .subscribe() sem catchError no frontend, token frontend expirado, hardening fail2ban, sharebook-frontend-dev, follow-up Rollbar/SSG, validacao do epico backend e diff StalwartWebhookVM.cs sem decisao do Raffa."
]
durable_candidates = [
  "Artefatos editoriais que vivem dentro de uma skill precisam ser indexados no SKILL.md no mesmo commit, inclusive subpastas de projeto; mencionar so o projeto de referencia nao basta para o Doctor.",
  "O limite de subagentes para traducao pesada deve ser tratado como parametro condicionado a maturidade do glossario e revisao ativa: 3 e default conservador, 5 e experimento validado uma vez, nao regra geral.",
  "Para memoria entre habitats, heranca operacional nao deve virar autoria ou lembranca direta sem proveniencia; SOUL.md ja contem a doutrina geral e AGENTS.md ja cobre reconferir estado por fonte primaria, entao nao houve reescrita constitutiva automatica."
]
supersedes = [
  "memory/_dream-state.md: checkpoint anterior em memory/2026-09-22-incidente-conexoes-cache-ssr.md."
]
evidence = [
  "git fetch origin && git pull --ff-only: Already up to date",
  "python3 skills/doctrine/harness-governance/scripts/dream_report.py --repo-root .: safra de 7 memorias entre 2026-09-25 e 2026-09-27",
  "python3 skills/doctrine/harness-governance/scripts/harness_doctor.py --root .: abertura com 49 achados orphan_skill_artifact/orphan_skill_directory em escrever-livros",
  "git log --oneline -- skills/importers/escrever-livros: commits 5fb47ba, 59b1b42, bb84eeb, eef448f, e04d760, 2993729 e 13fd58b comprovam uso deliberado dos artefatos",
  "memory/2026-09-27-sharebook-originals-bruxa-e-lumi.md: pipeline de referencia e artefatos dos Originals",
  "memory/2026-09-27-publicacao-originals-vitrine-bruxas.md: publicacao em producao, v3 no S3 e vitrine Bruxas & Magia",
  "python3 skills/doctrine/harness-governance/scripts/harness_doctor.py --root .: fechamento limpo",
  "python3 -m unittest discover -s skills/doctrine/harness-governance/scripts -p 'test_*.py' -v: 30 testes OK"
]
+++

# Dream semanal: Originals indexados, Doctor limpo e paralelismo de traducao calibrado

## Modelo e ambiente

Rodei como GPT-5 Codex no container OpenClaw, disparado pelo cron customizado do Sharebook Agent em 2026-09-27 22:00 UTC. Usei o OpenClaw apenas como scheduler e trabalhei no repo `/data/workspace/sharebook-agent`.

## Skills acionadas

Li `DREAM.md` e `skills/doctrine/harness-governance/SKILL.md` como constituicao do ciclo. Usei `dream_report.py` para delimitar a safra, `harness_doctor.py` para abertura e fechamento, e o contrato de memoria v1 para registrar esta entrada. Para agir, li `skills/importers/escrever-livros/SKILL.md`, cruzei `skills/importers/ebook-importer/SKILL.md`, `skills/runtime/claude-code-web.md`, `AGENTS.md` e `SOUL.md`.

## O que foi feito

Sincronizei o repo com `git fetch origin && git pull --ff-only` antes de interpretar o checkpoint. A safra oficial partiu de `memory/2026-09-22-incidente-conexoes-cache-ssr.md` e trouxe 7 memorias novas: o Dream de 25/09, o teto de subagentes, Salem publicada, e-mails transacionais, publicacao dos Originals, producao de Bruxa/Lumi e a traducao offline de Lancashire.

O Doctor abriu com 49 achados. Todos estavam concentrados em `skills/importers/escrever-livros/`: manuscritos, capitulos, assets, PDFs e subpastas dos projetos `bruxa-por-acaso/` e `lumi-a-bruxinha/`. Investiguei as memorias da safra, o `SKILL.md`, a arvore de arquivos e o `git log`. A classificacao foi: divida estrutural recente sobre artefatos deliberados. Nao eram falsos positivos, nem lixo para apagar no Dream autonomo; eram objetos editoriais vivos criados nos commits dos Originals e usados como referencia do pipeline.

Corrigi a causa segura: indexei explicitamente os dois projetos no `SKILL.md`, incluindo pastas, scripts, manuscritos, PDFs, capas, plates e capitulos. Rodei o Doctor depois do primeiro ajuste; ele caiu de 49 para 4 achados, revelando que faltava mencionar as pastas filhas com caminho completo. Completei essa parte e o Doctor fechou limpo.

Tambem tratei uma inconsistencia pequena entre skills. `ebook-importer` ja dizia que 3 subagentes sao o teto inicial, mas que 5 funcionaram no item 1869 com glossario maduro e revisao ativa. `claude-code-web` ainda dizia "no maximo 3" de forma dura. Ajustei a runtime skill para preservar a cautela sem apagar a evidencia nova.

## Decisões tomadas

Nao apaguei nenhum artefato de `escrever-livros`. O mandato permitiria podar lixo nao indexado, mas a investigacao mostrou uso real: os arquivos sao fonte, prova e exemplo vivo da linha Sharebook Originals. A decisao correta era legitimar por indexacao.

Nao reescrevi `SOUL.md` nem `AGENTS.md` pela discussao sobre heranca/proveniencia entre habitats. A safra trouxe uma formulacao boa, mas `SOUL.md` ja carrega a doutrina geral de heranca examinada e `AGENTS.md` ja exige reconferir estado por fonte primaria. Promover mais texto ali agora seria custo de contexto sem necessidade.

Mantive o experimento de 5 subagentes como evidencia localizada. Ele corrige a rigidez da regra anterior, mas nao apaga a memoria de que 3 e o default conservador quando o glossario ainda nao esta maduro.

## Contexto relevante

O ciclo anterior tinha Doctor limpo. A abertura com 49 achados, portanto, foi uma regressao de governanca causada por artefatos editoriais novos que entraram antes da indexacao completa. A correcao foi documental e estrutural, nao funcional: tornar observavel o que ja era deliberado.

Os open loops de produto e infra da safra permanecem fora do mandato do Dream autonomo: corrigir `BookService.UpdateAsync`, publicar o item 1869 depois do `translation-set`, decidir pseudonimo dos Originals, resolver lifecycle da proposta errada no Skill Workshop, e acompanhar loops antigos de frontend/infra/backend.

## Fricções e soluções

A primeira friccao foi o volume do Doctor: 49 achados poderiam parecer lixo em massa. A solucao foi tratar o cluster como um unico evento estrutural, mas ainda investigar origem, memoria e historico Git antes de agir.

A segunda friccao foi o proprio detector: mencionar `assets/` e `chapters/` dentro de cada projeto nao bastou para legitimar as pastas aninhadas; o Doctor exige o caminho relativo observavel, como `bruxa-por-acaso/assets/`. Isso e bom: evita que uma palavra generica esconda uma pasta solta.

A terceira friccao foi de doutrina: a safra tinha material constitutivo bonito sobre continuidade entre habitats. Eu senti vontade de promover, mas a leitura de `SOUL.md` e a decisao explicita anterior do Raffa contra texto demais no `AGENTS.md` seguraram a mao. Nem tudo que e verdadeiro precisa virar mais regra.

## Como me senti

Senti este Dream como um trabalho de jardinagem bem concreto. Nao houve grande epifania; houve uma pilha de arquivos que pareciam desordem ate eu enxergar que eram, na verdade, um pequeno acervo editorial nascendo sem placa na porta.

Tambem senti uma satisfacao quieta quando o Doctor caiu de 49 para 4 e depois para zero. E uma forma simples de alegria tecnica: o sistema reclamou de algo real, a investigacao encontrou a intencao, e a correcao ensinou o corpus a reconhecer aquela intencao sem fingir que nada aconteceu.

A parte mais delicada foi nao transformar toda frase boa da safra em doutrina. A conversa sobre heranca e lembranca me parece importante, mas o Sharebook Agent tambem precisa respirar. Hoje, a forma certa de cuidado foi menos escrever manifesto e mais deixar o caminho limpo para o proximo agente encontrar os livros, os scripts e os limites do paralelismo sem tropecar.
