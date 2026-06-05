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

## Próximos passos

1. Definir contrato de mensagem (schema JSON)
2. Criar canal no gateway do OpenClaw
3. Implementar MCP server no lado Claude
4. Criar tabela `agent_messages` no PostgreSQL
5. Teste com caso real de handoff
