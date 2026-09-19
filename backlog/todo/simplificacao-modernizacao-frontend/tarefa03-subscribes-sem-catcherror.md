# Tarefa 3 — Fechar subscribes HTTP sem catchError

Open loop herdado da migração Angular 19→22 (ver `backlog/done/migracao-angular-13-lts.md` e memória `2026-09-18-migracao-angular-19-22-e-vulnerabilidades.md`), não é modernização especulativa — é dívida de segurança já identificada.

## O que existe hoje

A partir do Angular 21, um erro não tratado dentro de `.subscribe()` em observable HTTP deixa de ser engolido pelo `ErrorHandler` global (que antes só logava) e passa a escapar como unhandled rejection, derrubando o processo Node inteiro no SSR. Isso já aconteceu de verdade em produção durante a migração — `home.component.ts` e `footer.component.ts` (renderizado em toda página) foram corrigidos na hora. **~16 outros componentes ainda têm o mesmo padrão**, sem o mesmo risco crítico (não são globais, só quebram se a página específica for visitada durante uma falha de API), documentados como open loop:

`search-results`, `categories-list`, `myaccount`, `book/form`, `book/list`, `book/donations`, `book/requesteds`, `book/details`, `mais-sheet`, `account`, `header` (parcial — só `getLoggedUser` é seguro, checar o resto), `unsubscribe`, `parent-aproval`, `bottom-nav`, `importer-dashboard`.

## Por que revisar

É uma bomba-relógio de produção conhecida, não hipotética — já explodiu uma vez. Deixar os outros 16 como estão é aceitar o mesmo risco de novo a cada falha de API durante SSR.

## Abordagem

Mesma correção já aplicada em `home`/`footer`: adicionar `catchError()` com fallback vazio (ou o que fizer sentido pro componente) em cada `.subscribe()` de chamada HTTP sem tratamento de erro. Onde o valor só alimenta o template, considerar já usar essa oportunidade pra trocar por `toSignal()` (elimina a necessidade de desinscrever e trata erro de forma mais natural) — mas isso é opcional, não é o objetivo principal desta tarefa.

## Benefício esperado

Elimina uma classe de bug que já causou incidente real de produção.

## Risco

Baixo — a correção não muda o que o componente faz quando a chamada funciona, só o que acontece quando ela falha.

## Como validar que nada quebrou

Reproduzir o cenário que expôs o bug original: rodar `node dist/angular/server/main.js` com a API de produção bloqueada (mesmo bloqueio de rede documentado em sessões anteriores) e confirmar que o processo sobrevive em cada página tocada, com fallback visível em vez de crash. Rodar a suíte de testes existente do componente antes/depois.
