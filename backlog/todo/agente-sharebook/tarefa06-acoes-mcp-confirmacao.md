# Tarefa 6 — Ações via MCP com confirmação

## Status

**Pendente.** Depende da tarefa 2 e de confiança operacional no agente read-only.

## Objetivo

Permitir que o agente conclua tarefas no Sharebook sem retirar controle do usuário.

## Ações candidatas

- adicionar ou remover item da lista de desejos;
- criar bookmark ou anotação;
- atualizar progresso;
- solicitar preparação de Sharebook Audio;
- preparar uma solicitação de doação;
- alterar preferências explicitamente autorizadas.

## Regras

- confirmação mostra ação, alvo e consequência;
- mutações são idempotentes;
- toda execução gera trilha de auditoria;
- falha ambígua exige consulta do estado antes de repetir;
- ações sensíveis podem exigir autenticação recente;
- nenhuma confirmação genérica autoriza uma cadeia aberta de ações.

## Critério de pronto

O usuário entende e confirma cada mutação relevante, repetições não duplicam efeitos e o histórico permite reconstruir quem solicitou, confirmou e executou a ação.
