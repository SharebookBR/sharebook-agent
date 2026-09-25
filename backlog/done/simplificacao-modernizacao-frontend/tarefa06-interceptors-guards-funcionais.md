# Tarefa 6 — Interceptors e guards funcionais

## O que existe hoje

4 interceptors (`error.interceptor.ts`, `jwt.interceptor.ts`, `transfer-state.interceptor.ts`, e o morto `fake-backend.ts` — ver Tarefa 4) são class-based (`implements HttpInterceptor`), registrados via `HTTP_INTERCEPTORS` multi-provider com `withInterceptorsFromDi()`. 2 guards (`auth.guard.admin.ts`, `auth.guard.user.ts`) são class-based (`implements CanActivate`). Zero uso de `inject()` em código de produção — só aparece em specs.

## Por que revisar

Desde Angular 15/16 a forma idiomática é `HttpInterceptorFn`/`CanActivateFn`: função pura, sem boilerplate de classe, mais fácil de testar isoladamente, sem precisar do `withInterceptorsFromDi()` de compatibilidade.

## Abordagem

Converter os 3 interceptors reais (não o morto) e os 2 guards para função, usando `inject()` pra pegar as dependências. É refactor mecânico — a lógica interna de autenticação, tratamento de erro e transfer state não muda, só a casca.

**Pré-requisito: Tarefa 5 primeiro** (specs de caracterização de `authentication.service.ts`), já que os interceptors/guards tocam diretamente autenticação — código de alto risco que hoje não tem rede de segurança.

## Benefício esperado

Código mais enxuto e idiomático, sem a camada de compatibilidade `withInterceptorsFromDi()`, mais fácil de testar como função pura.

## Risco

Baixo — comportamento idêntico, só muda a forma de registro (`provideHttpClient(withInterceptors([...]))` em vez de multi-provider de classe).

## Como validar que nada quebrou

Specs de interceptor/guard (escrever se não existirem — ver Tarefa 5) rodando antes e depois da conversão, mais smoke test real de fluxo de login/logout e de uma rota protegida por guard admin/user.

## Status final — CONCLUÍDA em 2026-09-19

Commit `4abaa60` (branch `develop`, sharebook-frontend). Suíte foi de 80 para 95 specs (93 executadas + 2 skip).

- `jwtInterceptor`, `errorInterceptor`, `transferStateInterceptor` e `authGuardUser`/`authGuardAdmin` convertidos para `HttpInterceptorFn`/`CanActivateFn` com `inject()`. Registro via `provideHttpClient(withXhr(), withInterceptors([...]))`, sem `withInterceptorsFromDi()`. Guards referenciados direto nas rotas (`canActivate: [authGuardUser]`).
- 5 specs novos de caracterização (nenhum existia antes): comportamento do jwt (injeta Bearer, exceto na chamada externa de CEP), do error (logout+reload em 401, log de SSR fora do browser) e do transfer-state (cache hit/miss entre server e browser), além dos dois guards (bloqueia/libera + redirect correto).
- Validação real em dev via Playwright contra backend local: `/panel` bloqueado deslogado e libera após login (`authGuardUser`), `/book/list` liberado pro Administrator (`authGuardAdmin`), header `Authorization` saindo numa chamada autenticada real (`jwtInterceptor`). Zero erro de console.
- `tsc --noEmit` e `build:ssr` limpos.

**Checkpoint do lote 2 fechado** — tarefas 4, 5 e 6 concluídas e validadas em dev.
