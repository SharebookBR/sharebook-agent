# Missão — Painel de Jobs

## Objetivo
Evoluir a monitoria e o diagnóstico dos jobs do Sharebook (Hangfire/Background Jobs), tornando a saúde da operação visível e acionável.

## Detalhes Técnicos

### Painel de Jobs (v2)
- Adicionar status calculado por job (`Saudável`, `Atrasado`, `Com erro`, `Inativo`) com base no intervalo esperado e na última execução registrada.

### Histórico
- Permitir expandir cada job para ver as últimas execuções, com `CreationDate`, `TimeSpentSeconds`, `IsSuccess` e `Details`.

### Diagnóstico
- Destacar melhor os jobs que só enfileiram trabalho (`NewBookGetInterestedUsers`, `NewEbookWeeklyDigest`) e o `MailSender`, deixando claro o fluxo “enfileirou” vs “consumiu fila”.

### Backend
- Criar endpoint dedicado para histórico paginado por job, evitando carregar tudo em um único payload.

### Frontend
- Manter a tela apenas como leitura no primeiro ciclo; qualquer ação manual de executar job ou editar configuração deve ser tratada separadamente e com mais cautela.
