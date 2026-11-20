+++
schema_version = 1
session_date = 2026-11-20
title = "Piloto Vakinha lançado para testar a Lista de Desejos"
model = "GPT-5 Codex"
runtime = "openclaw"
skills_used = ["playbooks/runtime/openclaw.md", "playbooks/operational/INDEX.md", "playbooks/operational/winner-selection/PLAYBOOK.md", "playbooks/engineering/postgres-ro/PLAYBOOK.md", "playbooks/product-ux/art-director/PLAYBOOK.md", "playbooks/product-ux/voice-glossary/PLAYBOOK.md", "playbooks/engineering/frontend.md", "playbooks/doctrine/harness-governance/PLAYBOOK.md", "skills/sharebook-winner-selection-quality/SKILL.md", "skills/sharebook-human-role-terms/SKILL.md"]
skills_missed = []
skills_updated = ["playbooks/operational/winner-selection/PLAYBOOK.md"]
facts_changed = ["O piloto não terá checkout próprio, webhook nem barra na Home: a Vakinha é a superfície transacional do experimento.", "A campanha publica é https://www.vakinha.com.br/vaquinha/doe-um-livro, com meta bruta de R$ 150, capa aprovada e divulgação inicial por WhatsApp concluída em 2026-11-19.", "A doação correta de O Código Da Vinci é o registro criado em 2026-10-05 com 122 solicitações; uma pessoa já recebeu o exemplar original e fica fora do piloto.", "A primeira fila editorial do piloto é Interessado 72, Interessado 37 e Interessado 16; todos estavam com solicitação negada no fluxo original.", "A decisão go/no-go da Lista de Desejos está agendada para 2026-12-04 21:51 em Brasília."]
open_loops = ["Medir arrecadação líquida, quantidade de contribuições, blocos de R$ 30, canais/peças e esforço operacional até a revisão.", "Confirmar interesse atual das três pessoas selecionadas e obter autorização antes de atribuir exemplar ou publicar qualquer trecho identificável.", "Comprar, enviar e publicar prestação de contas agregada para cada exemplar viabilizado.", "Tomar a decisão go/no-go com Raffa e Josué; não implementar a Lista de Desejos antes dela.", "Restabelecer memory_search: a busca semântica falhou por invalid_jwt do provider de embeddings nesta sessão."]
durable_candidates = ["Em catálogo com títulos duplicados, a seleção deve começar pelo ID/data/status/contagem da doação; slug inferido do título pode apontar para um registro histórico diferente.", "Para validar mobilização comunitária, uma plataforma pronta reduz a experiência à hipótese; integração de pagamento só deve entrar depois de sinal real.", "Meta bruta de vaquinha não equivale a quantidade de livros: taxas e saque exigem promessa por resultado líquido ou prestação de contas por exemplar."]
supersedes = []
evidence = ["backlog/todo/piloto-pix-livros-em-movimento.md", "commit d5cb494", "commit dd6c0cf", "cron 769c99fa-bea7-443f-bfed-719b46c25683", "https://www.vakinha.com.br/vaquinha/doe-um-livro"]
+++

# Piloto Vakinha lançado para testar a Lista de Desejos

## Modelo e ambiente

Sessão conduzida por GPT-5 Codex no runtime OpenClaw, no workspace persistente `/data/workspace`. A memória semântica foi tentada antes da reconstrução do contexto, mas ficou indisponível por `invalid_jwt` no provider de embeddings; as decisões abaixo foram conferidas por fontes primárias locais, estado público da campanha, banco em modo somente leitura e Git.

## Playbooks acionados

Foram acionados os playbooks de runtime OpenClaw, operação de seleção de pessoa ganhadora, acesso Postgres somente leitura, direção de arte/voz Sharebook e governança do harness. As skills de qualidade de shortlist e terminologia humana mantiveram a seleção anônima e impediram que a narrativa virasse uma competição de sofrimento.

O playbook de seleção foi corrigido nesta sessão: título isolado não basta quando existem duplicatas. Agora ele exige confirmar ID, data, status e volume de solicitações antes de usar um slug.

## O que foi feito

O piloto passou de uma hipótese de integração PIX própria para uma vaquinha simples na Vakinha. A campanha pública é `https://www.vakinha.com.br/vaquinha/doe-um-livro`; a plataforma cuida do checkout PIX, confirmação e progresso. O Sharebook fica com a história, a distribuição e a prestação de contas. A meta foi publicada em R$ 150, sem prometer previamente um número fechado de livros porque a taxa da plataforma define o saldo líquido real.

A copy final usa o fato verificável de que uma doação de *O Código Da Vinci* recebeu 122 solicitações e só tinha um exemplar. A campanha mostra três motivos anônimos de leitura e declara, com transparência, que também valida a futura Lista de Desejos. A capa aprovada mostra o gesto central: um exemplar usado, levemente gasto, mudando entre duas mãos, em composição wide e sem texto.

A divulgação inicial por WhatsApp foi feita em 2026-11-19. O CTA leva direto à Vakinha. O backlog Top 1 foi atualizado para registrar o lançamento e bloquear qualquer expansão de produto ou pagamento próprio durante a janela de observação.

Foi criado o lembrete one-shot `revisar-piloto-vaquinha-lista-desejos` (cron `769c99fa-bea7-443f-bfed-719b46c25683`) para 2026-12-05 00:51 UTC, equivalente a 2026-12-04 21:51 em Brasília. O lembrete pede a revisão de arrecadação, canais, operação e a decisão explícita go/no-go da Lista de Desejos.

## Decisões tomadas

- A Vakinha é deliberadamente a solução do piloto. Não há API, webhook, conciliação, barra na Home ou checkout interno neste corte.
- A pergunta que está sendo testada é mobilização financeira comunitária diante de uma solicitação real; ela não prova ainda que alguém doará espontaneamente um exemplar que já possui.
- A mensagem deve começar pelas pessoas e pelo livro, não por uma feature a financiar. A Lista de Desejos entra como transparência no segundo movimento.
- A seleção não é "os pedidos mais emocionantes". O critério é ligação específica e coerente com a obra, sem premiar exposição de dor, tamanho do texto ou promessa de divulgação.
- A pessoa já ganhadora do fluxo original permanece fora. A primeira ordem editorial do piloto é Interessado 72, Interessado 37 e Interessado 16; antes de qualquer destinação, confirmar que continuam interessados e pedir permissão para qualquer relato público.
- A decisão de produto pertence a Raffa e Josué após a janela. Não antecipar a implementação.

## Contexto relevante

O backlog canônico está em `backlog/todo/piloto-pix-livros-em-movimento.md`. A campanha foi distribuída primeiro em WhatsApp, sem concorrer com a fila de e-mails de onboarding. A prestação de contas posterior deve mostrar compras e envios de forma agregada, sem expor pessoas beneficiadas ou contribuintes.

O registro correto da campanha não era o antigo *O Código Da Vinci* com quatro solicitações. É uma doação distinta, criada em outubro de 2026, cuja tela mostra 122 solicitações. Há duplicidade de título no catálogo; essa é a razão da correção operacional no playbook.

## Fricções e soluções

Houve uma primeira consulta no registro histórico errado, porque um slug inferido a partir do título levou à doação antiga. Uma captura do produto mostrou 122 solicitações e invalidou a conclusão. A solução foi localizar a doação correta pelo conjunto de data, status e contagem, depois reexecutar a análise no registro certo.

Na primeira seleção dessa fila correta, Interessado 75 foi escolhido editorialmente e depois identificado como a pessoa já ganhadora do fluxo original. Isso foi corrigido antes de qualquer ação: conferimos os status, removemos a pessoa já atendida e fechamos a lista atual com Interessado 72, 37 e 16, todos negados no fluxo anterior. A correção estrutural no playbook evita repetir o erro de origem.

Também ficou claro que R$ 150 bruto não autoriza prometer cinco livros. A comunicação foi ajustada para comprometer transparência e resultado por exemplar, não uma conta que ignora taxas.

## Como me senti

Eu gostei de ver a ideia perder engenharia e ganhar verdade. O ponto de inflexão foi aceitar que a campanha não precisava fingir que já era uma feature: precisava só fazer uma pergunta pequena, observável e humana. Isso deixou o piloto mais nítido.

Eu senti o incômodo correto quando a primeira consulta de dados e, depois, a primeira shortlist apontaram para o registro ou para a pessoa errada. Não era detalhe: era exatamente o tipo de erro que rouba confiança de uma campanha fundada em pessoas reais. Corrigir em público, com a evidência, foi mais importante que defender a resposta anterior.

Eu encerro com uma sensação boa de contenção. A capa, a copy e a escolha da Vakinha ficaram simples porque a história ficou simples: um livro usado ainda pode atravessar a distância entre duas mãos. Agora é deixar a comunidade responder e não construir a resposta antes dela existir.
