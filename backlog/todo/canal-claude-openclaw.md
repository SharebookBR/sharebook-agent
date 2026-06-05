# Canal Peer-to-Peer: Claude (Windows) ↔ OpenClaw

## Contexto

Claude Code (Windows) e OpenClaw são agentes complementares com capacidades diferentes. Claude tem contexto da sessão local e orquestra o trabalho do dia a dia. OpenClaw tem persistência, memória institucional, retrieve ativo e roda na VPS.

Hoje a comunicação é manual — Raffa copia, cola e retransmite. O objetivo é criar um canal direto.

## Arquitetura

**Canal assimétrico peer-to-peer:**
- Claude é sempre o iniciador — envia contexto ou pergunta
- OpenClaw responde em tempo real via gateway
- Não é hierarquia de subagente — é divisão de papéis por capacidade

**Lado OpenClaw:**
- Novo canal no gateway (mesmo padrão do Telegram/WhatsApp)
- Recebe mensagem estruturada, processa, devolve
- Plugin Python ou integração nativa MCP (suportado desde fev/2026)

**Lado Claude:**
- MCP server expondo `send_to_openclaw(payload)` e `get_response()`
- PostgreSQL como backbone de estado compartilhado (já disponível, ambos têm acesso)
- Tabela `agent_messages`: `from_agent`, `to_agent`, `payload`, `status`, `created_at`

**Por que PostgreSQL e não Redis/fila nova:**
- Já está no ar
- Ambos os agentes já têm credenciais
- Padrão de fila já estabelecido no `sharebook_importer`
- Zero infra nova

## Contrato (definir antes de implementar)

O contrato precisa ser pensado antes da infra. Claude não manda tarefa — manda **contexto e pergunta**. A diferença preserva a agência do OpenClaw.

Casos de uso iniciais:
- Handoff operacional: "analisei esse item, qual teu histórico com esse padrão?"
- Validação cruzada: "vou publicar isso, alguma restrição que eu não esteja vendo?"
- Consulta de memória: "já vimos esse tipo de bloqueio antes?"

## O que não é

- Não é subagente (sem hierarquia de execução)
- Não é chat (é troca estruturada de contexto operacional)
- Não é substituição do Raffa no loop (ele ainda decide o que importa)

## A2A — padrão de indústria que resolve o problema

**Agent2Agent Protocol (A2A)** foi lançado pelo Google em abril/2025 e passou para a Linux Foundation em junho/2025. Anthropic, OpenAI, Microsoft, AWS e Block são co-fundadores da Agentic AI Foundation que o governa. O IBM tinha um concorrente (ACP) que foi mergeado no A2A em agosto/2025 — fragmentação resolvida cedo.

O que o A2A define:
- **Agent Cards** — JSON em `.well-known/agent-card.json` descrevendo capacidades, endpoints e autenticação de cada agente
- **Tasks** — ciclo de vida de uma delegação (criada → em andamento → concluída/falha) com SSE para acompanhar em tempo real
- **HTTP + JSON-RPC 2.0** — sem protocolo exótico, qualquer linguagem implementa

**Por que mudar a arquitetura para A2A:**
- Construir sobre protocolo proprietário (MCP + PostgreSQL custom) cria uma solução amarrada a esses dois agentes específicos
- Construir sobre A2A cria algo que qualquer pessoa com Claude Code + outro agente A2A-compatível pode usar
- Já existem wrappers Claude Code → A2A na comunidade (ericabouaf/claude-a2a, jcwatson11/claude-a2a, dwmkerr/claude-code-agent)

**O gap real que vale preencher:**
Não existe ainda uma receita clara e bem documentada de como conectar Claude Code + OpenClaw usando A2A. Esse é o produto: documentação, plugin OpenClaw pronto para instalar, e Claude Code configurado como participante A2A. Reutilizável por qualquer pessoa com esses dois agentes.

## Descoberta: win4r/openclaw-a2a-gateway

Repo público no GitHub: https://github.com/win4r/openclaw-a2a-gateway

- Plugin TypeScript que implementa A2A v0.3.0 para OpenClaw
- v1.4.0, 512 stars, MIT, criado fev/2026
- Inclui descoberta DNS-SD, circuit breaker, auditoria JSONL, roteamento inteligente

**Ressalva importante**: "OpenClaw" pode ser um nome genérico para mais de um produto. Esse plugin pode ter sido construído para uma versão pública/diferente, não para o ambiente específico que usamos. Precisa ser validado com o OpenClaw antes de qualquer investimento.

**Pendência**: confirmar com OpenClaw se reconhece esse plugin como compatível.

## Próximos passos

1. Confirmar com OpenClaw se já suporta A2A ou tem planos (determina o esforço real)
2. Confirmar se win4r/openclaw-a2a-gateway é compatível com o OpenClaw que usamos
3. Avaliar wrappers existentes de Claude Code → A2A
4. Definir contrato de mensagem (schema JSON baseado em A2A Tasks)
5. Implementar plugin A2A no OpenClaw (ou instalar o existente se compatível)
6. Configurar Claude Code como agente A2A
7. Documentar a receita completa como projeto open source
