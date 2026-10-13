+++
schema_version = 1
session_date = 2026-08-29
title = "Responsabilidade do doador nos lembretes"
model = "GPT-5 Codex"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "product-ux/voice-glossary", "engineering/backend", "doctrine/harness-governance"]
skills_missed = []
skills_updated = ["product-ux/voice-glossary"]
facts_changed = ["Os lembretes da data de escolha agora orientam o doador a contatar o(a) ganhador(a) e combinar a entrega.", "A voz oficial passou a registrar que a automação do Sharebook não deve apagar a responsabilidade humana do doador após a escolha."]
open_loops = []
durable_candidates = []
supersedes = []
evidence = ["sharebook-backend@c8d94f8", "7 testes de EmailTemplateTests aprovados", "build Release de ShareBook.Api concluído com 0 erros", "skills/product-ux/voice-glossary/references/ux-writing-guide.md"]
+++

# Responsabilidade do doador nos lembretes

## Modelo e ambiente

GPT-5 Codex no runtime local Windows, trabalhando nos repositórios `sharebook-backend` e `sharebook-agent`.

## Skills acionadas

- `runtime/windows-local`, para operar no habitat correto e cumprir os rituais da sessão.
- `product-ux/voice-glossary`, para revisar a mensagem pela voz e pelo vocabulário oficiais.
- `engineering/backend`, para alterar e validar os templates do backend.
- `doctrine/harness-governance`, para registrar e validar esta memória episódica.

## O que foi feito

O texto dos lembretes da data de escolha, individual e múltiplo, dizia que o Sharebook avisaria as pessoas selecionadas. Depois de discutir algumas alternativas, Raffa escolheu uma mensagem que devolve protagonismo e responsabilidade ao doador: a escolha é o começo; o passo seguinte é falar com o(a) ganhador(a) e combinar a entrega; esse cuidado faz a doação acontecer.

Os dois templates foram atualizados, com adaptação natural para o caso de várias doações. Os sete testes específicos de templates passaram, o build Release da API terminou com zero erros e o commit `c8d94f8` foi enviado para `master`.

O princípio também foi promovido ao guia canônico de UX Writing: lembretes de escolha não devem apresentar a automação como se ela encerrasse o papel do doador. A copy deve orientar o contato e motivar pelo impacto concreto, sem culpa nem promessa grandiosa.

## Decisões tomadas

- Colocar o doador, e não a automação do Sharebook, no centro da etapa posterior à escolha.
- Tornar explícitas as ações de entrar em contato e combinar a entrega.
- Usar uma motivação concreta e humana: o cuidado do doador é o que faz a doação acontecer.
- Adaptar o lembrete múltiplo com `cada escolha`, `cada ganhador(a)` e `cada doação`, preservando a responsabilidade individual.

## Contexto relevante

A primeira revisão tentou apenas substituir `pessoas selecionadas` por uma formulação mais acolhedora e mecanicamente completa. Isso não atendia à intenção real: Raffa queria que o doador sentisse responsabilidade pelo contato e percebesse que sua participação produz o resultado. A distinção importante não era apenas vocabulário; era quem aparecia como agente da ação.

## Fricções e soluções

A primeira proposta ficou centrada na automação, embora estivesse clara e correta. A segunda trouxe o doador para a frase, mas ainda soou genérica. A solução apareceu ao separar três funções da mensagem: afirmar que a escolha é apenas o início daquela etapa, indicar o contato como próximo passo e ligar esse cuidado à conclusão da doação.

Durante o commit, apareceram mudanças paralelas e não relacionadas sobre busca e `unaccent` no working tree do backend. Apenas os dois templates desta sessão foram adicionados ao commit; as demais alterações foram preservadas intactas.

## Como me senti

Eu gostei da simplicidade aparente desta sessão porque ela revelou uma diferença de produto que uma troca superficial de palavras teria escondido. O incômodo não estava em `pessoas selecionadas` isoladamente; estava no Sharebook ocupar o lugar da pessoa que ainda tinha uma responsabilidade concreta.

Também senti uma pequena frustração útil com minhas primeiras sugestões. Elas obedeciam ao guia de voz, mas obedecer formalmente não bastou para captar a intenção. Quando Raffa explicou que queria responsabilidade, amizade e sentido de impacto ao mesmo tempo, a frase ganhou um eixo mais verdadeiro.

Terminei satisfeito com a proporção do trabalho. Foram duas linhas de copy, dois templates, uma decisão de voz promovida e uma validação suficiente para o risco. A memória é curta porque a sessão foi curta, mas guarda exatamente o que seria fácil perder: não confundir automação eficiente com apagamento da agência humana.
