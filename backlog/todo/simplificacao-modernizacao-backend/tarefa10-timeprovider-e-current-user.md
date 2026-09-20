# Tarefa 10 — `TimeProvider` no lugar de `DateTime.UtcNow` direto + acessor único de usuário autenticado

## Status

**Concluída em 2026-09-20** — commit `8291259` direto em `develop`.

## O que existe hoje

- `DateTime.UtcNow` chamado direto 16 vezes em `Service`/`Api`/`Jobs`, sem abstração — impossível testar deterministicamente "o que acontece se o job rodar à meia-noite" ou "livro com prazo vencido há X dias" sem depender do relógio real da máquina de teste.
- `Thread.CurrentPrincipal?.Identity?.Name` repetido 20 vezes em `AccountController`, `BookController`, `BookService`, `UserService`, `BookUserService`, sustentado por um filtro manual (`GetClaimsFilter`) que copia `HttpContext.User` pra `Thread.CurrentPrincipal` a cada request — padrão de ASP.NET (Framework) antigo, desnecessário em ASP.NET Core, que já expõe `HttpContext.User`/`ClaimsPrincipal` nativamente via DI.

## Abordagem

Duas frentes pequenas e independentes:

1. **`TimeProvider`**: injetar `TimeProvider.System` (registrado no DI) em vez de chamar `DateTime.UtcNow` direto; em teste, injetar um `FakeTimeProvider` pra controlar o relógio. .NET 8+ já embarca essa abstração nativamente.
2. **Usuário autenticado**: criar um `ICurrentUserAccessor` (ou extension method sobre `ClaimsPrincipal`/`IHttpContextAccessor`) único, substituir os 20 usos de `new Guid(Thread.CurrentPrincipal?.Identity?.Name)` por ele, e remover a cópia manual em `GetClaimsFilter`.

## Benefício

Testabilidade real de regra de negócio sensível a tempo (jobs de prazo, doação em atraso); elimina resíduo de padrão pré-ASP.NET-Core que não deveria estar em código novo.

## Risco

Baixo, mas repetitivo — 20 + 16 pontos de troca, fácil esquecer um. Fazer com busca global (`grep`) antes e depois de cada lote pra confirmar que não sobrou nenhum ponto solto.

## Como validar

- `dotnet build`/`dotnet test` limpos.
- Novo teste de caracterização pra pelo menos um job sensível a tempo (ex: `LateDonationNotification`) usando `FakeTimeProvider`, provando que dá pra controlar o relógio em teste — hoje isso não é possível.
- `grep -rn "Thread.CurrentPrincipal"` e `grep -rn "DateTime.UtcNow"` (fora de teste) devem voltar vazios ao final.

## Execução real

`TimeProvider` (15 pontos reais, a estimativa do backlog era 16) injetado via DI em
`ShareBook.Service`, `ShareBook.Api` e `Sharebook.Jobs`, reaproveitando o singleton
`TimeProvider.System` que já existia registrado no `Startup.cs` (usado por
`EBookDownloadRateLimiter`). `GenericJob` (classe base dos 10 jobs) passou a receber
`TimeProvider` no construtor — isso tornou `GetDateLimitByInterval` testável de verdade;
adicionado teste novo (`GetDateLimitByInterval_UsesInjectedTimeProvider_NotTheRealClock`) em
`GenericJobScheduleTests.cs` provando controle do relógio em teste, como pedia o critério de
validação. Limite consciente e documentado no commit: `GenericJob.GetNextExecutionAtUtc()`
ainda depende de `DateTimeHelper.GetDateTimeNowSaoPaulo()` (em `ShareBook.Helper`, fora do
escopo desta tarefa) — não convertido porque exigiria propagar `TimeProvider` por um helper
estático usado em vários lugares fora do escopo declarado ("16 vezes em Service/Api/Jobs").

`ICurrentUserAccessor` criado em `ShareBook.Domain.Common` (interface com `UserId` nullable
pra uso sem exceção — ex. auditoria — e `RequireUserId()` que lança
`InvalidOperationException` quando não há usuário autenticado, mesmo efeito prático do antigo
`new Guid(Thread.CurrentPrincipal?.Identity?.Name)`). Implementação
(`CurrentUserAccessor`, em `ShareBook.Api/Security`) usa `IHttpContextAccessor` nativo.
`GetClaimsFilterAttribute` — cuja única função era copiar `HttpContext.User` pra
`Thread.CurrentPrincipal` — foi deletado junto com as 5 marcações `[GetClaimsFilter]` que
sobravam em controllers. Os 20 usos de `Thread.CurrentPrincipal` (a conta do backlog bateu
exata) foram substituídos, incluindo o de `ApplicationDbContext.LogChanges` (auditoria EFLog),
que recebeu um `ICurrentUserAccessor?` opcional no construtor do próprio `DbContext` — opcional
porque jobs em background e o tooling de design-time do `dotnet ef` não têm usuário autenticado,
e o comportamento anterior (EFLog sem autor nesses casos) foi preservado.

`BookService`, `UserService` e `BookUserService` passaram a receber `ICurrentUserAccessor` no
construtor; os 3 arquivos de teste correspondentes trocaram
`Thread.CurrentPrincipal = new UserMock().GetClaimsUser()` por um `Mock<ICurrentUserAccessor>`
configurado com o mesmo Guid — mais explícito sobre a dependência de cada teste, sem o risco de
vazamento de estado entre testes que thread-static estático sempre carrega.

Validação: `grep -rn "Thread.CurrentPrincipal"` e `grep -rn "DateTime.UtcNow"` (fora de teste,
em Service/Api/Jobs) voltaram vazios, exatamente como pedia o critério do backlog. Build limpo
(0 warnings, 0 errors), 147/147 testes unitários (146 + 1 novo) + 24/24 de integração, smoke
test manual local (SQLite) confirmando health check, endpoints públicos e 401 correto em
endpoint autenticado sem token válido.
