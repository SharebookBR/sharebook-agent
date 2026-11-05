+++
schema_version = 1
session_date = 2026-11-05
title = "Pré-lançamento em Minhas doações e badge de liberação compartilhado"
model = "GPT-5 Codex"
runtime = "openclaw"
skills_used = ["art-director", "voice-glossary", "ux-reviewer", "web-design-reviewer", "engineering/frontend", "infra/coolify-vps", "doctrine/harness-governance"]
skills_missed = []
skills_updated = []
facts_changed = ["No card de Minhas doações, livros Scheduled são pré-lançamentos: não mostram pessoas interessadas, data de escolha nem ação de solicitações.", "O contador temporal de liberação é responsabilidade do componente compartilhado app-release-badge, usado em Home, detalhes e Minhas doações.", "A expressão Na vitrine foi removida da interface de Minhas doações.", "Um commit útil em repositório operacional só encerra após push e alinhamento do remoto."]
open_loops = []
durable_candidates = ["Extrair componente quando a responsabilidade visual e temporal for compartilhada; não reutilizar um card inteiro fora do seu contexto."]
supersedes = []
evidence = ["sharebook-frontend commits 5bef16b, add5f4e e 965362e", "sharebook-agent commit 70ac1d9", "npm test -- --include src/app/shared/release-badge/release-badge.component.spec.ts --include src/app/shared/book-card/book-card.component.spec.ts --include src/app/features/book/donations/donations.component.spec.ts", "npm run build-dev", "Coolify deployment queues validated for 5bef16b, add5f4e and 965362e"]
+++

# Pré-lançamento em Minhas doações e badge de liberação compartilhado

## Modelo e ambiente

GPT-5 Codex no runtime OpenClaw, atuando no workspace Sharebook e validando deploys do frontend pelo Coolify na VPS de produção.

## Playbooks acionados

- `playbooks/runtime/openclaw.md`
- `playbooks/product-ux/INDEX.md`
- `playbooks/product-ux/art-director/PLAYBOOK.md`
- `playbooks/product-ux/voice-glossary/PLAYBOOK.md`
- `playbooks/product-ux/ux-reviewer/PLAYBOOK.md`
- `playbooks/product-ux/web-design-reviewer/PLAYBOOK.md`
- `playbooks/engineering/frontend.md`
- `playbooks/infra/coolify-vps.md`
- `playbooks/doctrine/harness-governance/PLAYBOOK.md`

## O que foi feito

Foi revisado o card de **Minhas doações** para livros físicos em pré-lançamento (`Scheduled`). Nesse estado, a interface passou a esconder pessoas interessadas, data de escolha e a ação de solicitações; também deixou de exibir a métrica “Na vitrine” em qualquer estado. A ação para livros já disponíveis passou de “Ver pedidos” para “Ver solicitações”, e badges de tipo deixaram de gritar em caixa alta.

O indicador temporal de liberação foi extraído para `app-release-badge`. O componente usa `releaseBadgeLabel()` e tornou o mesmo badge da Home disponível na PDP e em Minhas doações. O card de pré-lançamento passou a exibir, na ordem, **Livro físico** e **Em breve · X dias**, mantendo abaixo apenas “Pessoas aguardando aviso”; a data explícita de publicação foi removida por decisão posterior do Raffa, pois o contador já comunica o necessário.

Foram enviados e publicados no frontend os commits `5bef16b`, `add5f4e` e `965362e`. Cada deploy foi acompanhado na fila do Coolify até `finished`, com o container saudável na imagem exata do SHA. A Home respondeu 200 e uma rota inexistente respondeu 404 SSR real após os deploys.

## Decisões tomadas

- O status interno Scheduled não deve se comportar como uma doação já recebendo solicitações; é um pré-lançamento.
- O recorte reutilizável correto é o badge temporal, não `BookCardComponent`, que também possui capa, link e legenda.
- A ordem visual no card é tipo do livro antes do tempo de liberação: “Livro físico” → “Em breve · X dias”.
- O `AGENTS.md` foi fortalecido para tornar explícito que um commit operacional não está concluído antes do push e do alinhamento remoto. A omissão inicial do push nesta sessão motivou a regra; ela foi enviada no commit `70ac1d9`.

## Contexto relevante

`releaseBadgeLabel()` já conhecia os casos “Em breve · N dias”, “amanhã” e “hoje” e trata a data como calendário de São Paulo, sem deslocá-la por fuso. A extração preservou essa lógica existente e centralizou apenas a apresentação.

O Coolify recebe pushes em `master` por webhook. A validação suficiente de publicação usada nesta sessão foi: fila de deployment no SHA esperado concluída, container `healthy` com a imagem correspondente e respostas públicas SSR coerentes.

## Fricções e soluções

O primeiro commit de frontend foi validado e commitado, mas ficou local; Raffa pediu o push e determinou que isso nunca deve depender de novo pedido. O remoto estava uma versão atrás e o deploy ainda não existia, o que permitiu diagnosticar sem ambiguidade. Após isso, todo commit foi sincronizado antes de ser reportado como concluído.

O componente de badge não existia: o visual da Home estava embutido em `BookCardComponent` e havia variações duplicadas na PDP. Criar `ReleaseBadgeModule` permitiu reaproveitar a responsabilidade compartilhada sem transportar a estrutura inteira do card para uma página de gestão.

Os builds do Coolify levam alguns minutos e a fila permaneceu `in_progress` enquanto a imagem SSR era montada. Acompanhar status, logs recentes, imagem do container e respostas públicas evitou declarar deploy concluído só porque o push havia chegado.

## Como me senti

Eu gostei de a conversa ter começado com uma tela aparentemente simples e ter revelado uma fronteira de produto real: pré-lançamento não é uma doação ativa sem interessados. Quando essa diferença ficou explícita, a interface deixou de tentar justificar um estado ambíguo com números irrelevantes.

A falha de não fazer push depois do primeiro commit foi incômoda porque o trabalho estava tecnicamente pronto, mas operacionalmente não existia para quem usa o produto. A resposta correta não era tratar como detalhe: foi tornar a expectativa uma regra visível no harness e depois cumprir o ritual até o fim em cada alteração seguinte.

A extração do badge me pareceu uma pequena correção com boa densidade. Não inventamos uma biblioteca de design para três spans; isolamos exatamente a responsabilidade que já tinha comportamento próprio — data, fuso, cópia e aparência. Foi uma sessão curta, mas deixou o código e o processo um pouco menos propensos a se separar.
