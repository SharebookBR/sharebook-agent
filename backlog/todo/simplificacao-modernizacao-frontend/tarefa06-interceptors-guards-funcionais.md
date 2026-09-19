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
