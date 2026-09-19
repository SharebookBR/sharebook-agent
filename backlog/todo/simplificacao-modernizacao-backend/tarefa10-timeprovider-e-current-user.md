# Tarefa 10 — `TimeProvider` no lugar de `DateTime.UtcNow` direto + acessor único de usuário autenticado

## Status

Pendente.

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
