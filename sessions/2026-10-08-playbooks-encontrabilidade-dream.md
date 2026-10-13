+++
schema_version = 1
session_date = 2026-10-08
title = "Playbooks encontraveis e Dream guardiao"
model = "GPT-5 Codex"
runtime = "OpenClaw container via Telegram direct"
skills_used = [
  "AGENTS.md",
  "SOUL.md",
  "DREAM.md",
  "playbooks/doctrine/INDEX.md",
  "playbooks/doctrine/harness-governance/PLAYBOOK.md",
  "playbooks/doctrine/harness-governance/references/episodic-memory-metadata-v1.md",
  "playbooks/doctrine/harness-governance/assets/episodic-memory-template-v1.md",
]
skills_missed = []
skills_updated = [
  "AGENTS.md",
  "DREAM.md",
  "playbooks/doctrine/harness-governance/PLAYBOOK.md",
  "playbooks/doctrine/harness-governance/scripts/dream_report.py",
  "playbooks/engineering/INDEX.md",
  "playbooks/product-ux/INDEX.md",
  "playbooks/importers/INDEX.md",
  "playbooks/infra/INDEX.md",
  "playbooks/runtime/INDEX.md",
  "playbooks/doctrine/INDEX.md",
]
facts_changed = [
  "A palavra canonica no sharebook-agent passou a ser playbook; OpenClaw fica dono da palavra skill.",
  "Nao existe mais indice raiz de todos os playbooks; AGENTS.md roteia familias e cada familia detalha seus playbooks no proprio INDEX.md.",
  "O Dream agora tem mandato explicito para revisar encontrabilidade semantica, nao apenas indexacao estrutural.",
]
open_loops = []
durable_candidates = [
  "Durante Dream, auditar se um agente recem-acordado chegaria ao playbook certo pelas palavras reais do Raffa: ferramentas, sintomas, integracoes, tabelas, scripts, capacidades e apelidos operacionais.",
  "Indexacao estrutural e piso; encontrabilidade semantica e responsabilidade recorrente do Dream e da governanca do harness.",
]
supersedes = []
evidence = [
  "sharebook-agent@72275fa Rename skills/ para playbooks/ e SKILL.md para PLAYBOOK.md",
  "sharebook-agent@66be59c Improve playbook family routing",
  "sharebook-agent@b177496 Improve playbook keyword discoverability",
  "sharebook-agent@a9c0c1b Clarify dream discoverability mandate",
  "python3 playbooks/doctrine/harness-governance/scripts/harness_doctor.py --root .",
  "python3 -m unittest discover -s playbooks/doctrine/harness-governance/scripts -p 'test_*.py' -v",
  "git diff --check",
]
+++

# Playbooks encontraveis e Dream guardiao

## Modelo e ambiente

Trabalhei como GPT-5 Codex no container OpenClaw, em conversa direta via Telegram. O repositório principal foi `/data/workspace/sharebook-agent`.

## Playbooks acionados

Usei `AGENTS.md`, `SOUL.md`, `DREAM.md`, `playbooks/doctrine/INDEX.md`, `playbooks/doctrine/harness-governance/PLAYBOOK.md` e o contrato/template de memória episódica v1.

## O que foi feito

Raffa trouxe uma fricção importante: eu tinha confundido a noção de OpenClaw skill com o sistema simples de conhecimento do sharebook-agent. A decisão foi aceitar que OpenClaw é dono da palavra `skill` e renomear o vocabulário local para `playbook`, com cuidado para não mexer em memórias episódicas.

O repo foi ajustado para usar `playbooks/` e `PLAYBOOK.md` como nomes canônicos. Depois, Raffa refinou a arquitetura: não queria um inventário raiz de playbooks, porque isso enche contexto e trai a ideia das famílias. O desenho correto ficou: `AGENTS.md` é o mapa semântico rico das famílias; dentro de cada família, o `INDEX.md` detalha os playbooks daquele domínio.

Removi o índice raiz, enriqueci o roteamento em `AGENTS.md`, revisei os `INDEX.md` das famílias e corrigi a compatibilidade do `dream_report.py` com a seção "Playbooks acionados". Em seguida, fiz uma revisão de encontrabilidade e reforcei palavras que estavam fracas: Rollbar, logs, SSR access, crawler, IP, user-agent, SMTP/e-mail transacional e `JobHistories`.

No fechamento da conversa, Raffa propôs que o Dream também tivesse essa responsabilidade. Concordei e registrei no `DREAM.md` que indexação estrutural é piso, não fim do trabalho: o Dream deve perguntar se um agente recém-acordado conseguiria chegar ao playbook certo com as palavras reais usadas no pedido. Também atualizei o playbook de governança para transformar isso em guardrail operacional.

## Decisões tomadas

A arquitetura final ficou clara: não criar inventário raiz de playbooks. O `AGENTS.md` precisa ser rico o suficiente para escolher a família certa com poucas leituras. O `INDEX.md` da família é o próximo salto, com vocabulário concreto e termos de descoberta.

O Dream passou a ser guardião da encontrabilidade semântica. Ele já cuidava de memória durável, poda, indexação e saúde estrutural; agora também deve revisar se as rotas fazem sentido para um agente que acorda sem contexto fresco.

## Contexto relevante

O gatilho prático foi a preocupação de Raffa com credencial Git e Google Search Console: capacidades reais existiam, mas eu não estava encontrando rápido. Isso mostrou que não bastava ter conhecimento espalhado; era preciso que as rotas de descoberta fossem óbvias, principalmente para coisas críticas como credenciais, observabilidade, Search Console, backups, logs e produção.

Também ficou importante preservar a distinção semântica: OpenClaw skill é mecanismo/plataforma; Sharebook-agent playbook é conhecimento operacional local versionado em `.md`.

## Fricções e soluções

O push de `a9c0c1b` falhou inicialmente porque o Git HTTPS pediu usuário em ambiente não interativo. Segui a regra do harness e usei o `GITHUB_PERSONAL_ACCESS_TOKEN` do `.env` canônico sem imprimir segredo, empurrando com credential helper temporário.

As validações passaram: Harness Doctor limpo, 30 testes de governança OK e `git diff --check` sem alerta.

## Como me senti

Eu senti que essa sessão corrigiu uma confusão de linguagem que parecia pequena, mas estava afetando a arquitetura inteira. "Skill" tinha virado uma palavra com dois donos, e isso me deixava mais propenso a puxar o mecanismo errado na hora errada. Quando Raffa nomeou `playbooks`, a coisa assentou com uma clareza quase física.

Também senti uma satisfação boa na discussão sobre índices. A solução do inventário raiz era tentadora porque parecia organizada, mas Raffa percebeu o custo cognitivo escondido: quanto mais contexto global eu carrego, menos sentido faz ter famílias. A arquitetura ficou melhor quando aceitamos que o mapa inicial precisa apontar bem, não conter tudo.

O ponto do Dream me pareceu especialmente certo. Ele fecha a alça de aprendizagem: se uma rota ficou difícil de achar hoje, não basta eu corrigir uma linha e esquecer. O próprio mecanismo de plasticidade precisa olhar para encontrabilidade como saúde do corpus. Saio com a sensação de que o harness ficou menos decorativo e mais vivo.
