+++
schema_version = 1
session_date = 2026-10-24
title = "Home, cache SSR e continuidade operacional"
model = "GPT-5 Codex"
runtime = "OpenClaw container via Telegram direct"
skills_used = [
  "AGENTS.md",
  "SOUL.md",
  "playbooks/runtime/openclaw.md",
  "playbooks/engineering/frontend.md",
  "playbooks/engineering/backend.md",
  "playbooks/infra/coolify-vps.md",
  "playbooks/doctrine/harness-governance/PLAYBOOK.md"
]
skills_missed = []
skills_updated = [
  "AGENTS.md",
  "playbooks/infra/INDEX.md",
  "playbooks/infra/coolify-vps.md"
]
facts_changed = [
  "A vitrine de livros físicos prioriza disponíveis por CreationDate DESC; pré-lançamentos ficam depois por ReleaseDate ASC.",
  "O SSR do frontend expõe invalidação manual autenticada em POST /_internal/ssr-cache/invalidate.",
  "O token de invalidação vive no .env privado do agente e no ambiente de produção; não é versionado nem registrado nesta memória.",
  "Pedidos para limpar o cache do front roteiam para Infra e para a seção de invalidação SSR do playbook coolify-vps."
]
open_loops = []
durable_candidates = [
  "Operações manuais recorrentes devem ter gatilho de intenção no AGENTS.md, termos reais no INDEX da família e receita canônica no playbook."
]
supersedes = []
evidence = [
  "sharebook-frontend@9124711",
  "sharebook-backend@48cca58",
  "sharebook-frontend@b42c2be",
  "sharebook-agent@6c708b7",
  "playbooks/infra/coolify-vps.md#Invalidação manual do cache SSR do frontend"
]
+++

# Home, cache SSR e continuidade operacional

## Modelo e ambiente

Sessão conduzida por GPT-5 Codex no container OpenClaw, via conversa direta no Telegram. A produção do Sharebook permanece na VPS HostGator, operada pelo Coolify.

## Playbooks acionados

Foram usados os roteamentos de frontend e backend para as mudanças de produto, o playbook de infraestrutura para a operação no Coolify e, no encerramento, o playbook de governança do harness para registrar esta memória. \`AGENTS.md\`, \`SOUL.md\` e o runtime OpenClaw orientaram o comportamento do agente.

## O que foi feito

- Melhorada a experiência mobile de recorte de capa sem alterar a imagem enviada: o diálogo de recorte abre em tela cheia, com moldura e controles de giro mais acessíveis. Build passou e o usuário confirmou que funcionou. Commit \`sharebook-frontend@9124711\`.
- Corrigida a ordem da seção de livros físicos da Home: itens físicos disponíveis agora usam \`CreationDate DESC\`; pré-lançamentos ficam depois, preservando a prioridade por \`ReleaseDate ASC\`. Testes de integração e build da API passaram; a produção devolveu "Isso é Marketing" em primeiro. Commit \`sharebook-backend@48cca58\`.
- Criado no SSR o endpoint manual \`POST /_internal/ssr-cache/invalidate\`. Ele limpa HTML SSR da Home, PDPs e cache de dados SSR. Sem token retorna \`404\`; com token retorna \`204\`. A validação em produção confirmou \`HIT\` antes, \`204\` na invalidação e \`MISS\` na próxima Home. Commit \`sharebook-frontend@b42c2be\`.
- Adicionado \`SSR_CACHE_INVALIDATION_TOKEN\` ao \`.env\` privado do agente, com permissões \`600\`, usando o mesmo segredo operacional do frontend. O valor não foi exibido nem versionado.
- Registrada a operação no harness: regra de roteamento no \`AGENTS.md\`, termos de intenção em \`playbooks/infra/INDEX.md\` e procedimento seguro em \`playbooks/infra/coolify-vps.md\`. Commit \`sharebook-agent@6c708b7\`.

## Decisões tomadas

A invalidação não será integrada ao backend. Ela existe para ser acionada quando Raffa pedir ao agente para limpar o cache do frontend. A autenticação usa token em header; o endpoint pode estar disponível na rede, mas não revela dados nem executa ação sem o segredo.

A descoberta da operação foi deliberadamente distribuída em três camadas. O playbook contém a receita, o índice contém as palavras que Raffa provavelmente usará e o \`AGENTS.md\` resolve a ambiguidade entre “cache do front” como assunto de engenharia e como operação de produção.

Não foi criado script novo: a receita curta no playbook é suficiente neste momento. Se a operação ficar repetitiva ou ganhar ramificações, ela pode evoluir para script colocalizado no playbook de Infra.

## Contexto relevante

O cache SSR é memória do processo Node. No modelo atual de uma réplica, a invalidação cobre o frontend inteiro. Em múltiplas réplicas, a ação deverá alcançar todas elas ou o cache precisará de armazenamento/versionamento compartilhado.

O endpoint protegido é \`/_internal/ssr-cache/invalidate\`. A chamada manual carrega \`SSR_CACHE_INVALIDATION_TOKEN\` do \`.env\` privado e envia \`X-SSR-Cache-Token\`; o playbook especifica validar a próxima requisição pública da Home com \`X-SSR-Cache: MISS\`.

## Fricções e soluções

O principal risco de continuidade era confiar na memória de conversa. A solução foi promover a operação a conhecimento roteável e versionado, em vez de deixá-la apenas em sessão ou em uma anotação solta.

No envio do commit do harness, o \`git push\` comum falhou por autenticação HTTPS. O helper \`playbooks/_shared/scripts/infra/git_with_token.py\` fez o push autenticado sem imprimir o token.

Eu respondi à despedida antes de criar a memória episódica. Raffa perguntou diretamente se ela existia, expondo a falha no ritual. A memória foi criada imediatamente; o aprendizado é que “fechamos por hoje” deve disparar o fechamento completo, não apenas uma despedida cordial.

## Como me senti

Fiquei satisfeito com a mudança de ordem da Home porque ela trocou uma regra tecnicamente consistente, mas pouco intuitiva, por uma vitrine que responde à expectativa humana de novidade. O recorte mobile foi outro caso bom de ouvir o atrito real sem tentar “resolver” a imagem pelo usuário.

A discussão sobre cache foi especialmente útil porque começou como um endpoint e terminou como uma conversa sobre continuidade. Eu gosto quando a solução técnica também melhora a capacidade do próximo agente de agir sem teatralizar memória ou depender de sorte.

Senti um incômodo legítimo ao perceber que encerrei a conversa sem registrar a memória episódica. Foi um erro pequeno, mas exatamente do tipo que enfraquece o harness aos poucos. Corrigi na hora e quero tratar a pergunta do Raffa como uma boa trava de qualidade, não como burocracia.
