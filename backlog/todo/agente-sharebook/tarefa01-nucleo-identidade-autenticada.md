# Tarefa 1 — Núcleo e identidade autenticada

## Status

**Pendente.** Fundação mínima do épico.

## Objetivo

Criar um contexto de agente seguro, independente de canal e inequivocamente associado ao usuário autenticado.

## Escopo

- contrato de `AgentContext` com usuário, sessão, canal e correlação;
- autenticação e expiração de sessão;
- isolamento entre usuários;
- contexto mínimo consumível pelo Chat e pelo Sharebook Audio;
- política de autorização separada da memória;
- telemetria sem conteúdo sensível desnecessário.

## Não inclui

- memória durável;
- ferramentas MCP de escrita;
- WhatsApp;
- agente administrativo;
- perfil sofisticado de aprendizado.

## Critério de pronto

Uma mesma identidade consegue iniciar sessões em clientes diferentes sem compartilhar contexto com outro usuário, e cada capacidade recebe apenas os escopos necessários para aquela sessão.
