# Painel de Jobs v2

## Entregue em 2026-09-25

A v2 manteve o painel somente leitura e focado em diagnostico operacional, sem acoes manuais de execucao ou edicao de configuracao.

## O que mudou

- O endpoint do painel passou a listar tambem `CleanupLogsTable`, corrigindo a divergencia entre a lista do `JobExecutor` e a lista exposta em `/admin/jobs`.
- Cada job agora expoe saude calculada:
  - `Saudavel`;
  - `Atrasado`;
  - `Com erro`;
  - `Inativo`;
  - `Sem historico`.
- O contrato passou a expor `LastExecutionSuccess` por job.
- A tela mostra contadores de jobs saudaveis, atrasados e com erro.
- A tabela mostra o tipo de fluxo do job:
  - jobs que enfileiram e-mails;
  - `MailSender` como consumidor da fila;
  - demais rotinas como execucao direta.
- Cada job ganhou historico curto expandivel com as ultimas 5 execucoes, resultado, data, duracao e detalhes.

## Fora de escopo preservado

- Botao para executar job manualmente.
- Edicao de configuracao.
- Graficos.
- Alertas ou notificacoes.
- Substituir Rollbar, Coolify ou logs operacionais.

## Validacao

- `dotnet build ShareBook/ShareBook.Api/ShareBook.Api.csproj -m:1`
- `dotnet test ShareBook/ShareBook.Test.Unit/ShareBook.Test.Unit.csproj -m:1 --no-restore`
- `npx tsc -p tsconfig.app.json --noEmit`
- `npm run build-dev`
