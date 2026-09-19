# Tarefa 11 — Investigar rate limiter nativo do .NET vs `IEBookDownloadRateLimiter` caseiro

## Status

Pendente. **Esta tarefa pode terminar em "não mexer" — isso é um resultado válido, não falha.**

## O que existe hoje

`ShareBook.Api/RateLimiting/IEBookDownloadRateLimiter` é um rate limiter caseiro pra download de ebook, com resultado tipado (`EBookDownloadRateLimitResult`, já um `record struct` — bom sinal de que o time já usa feature moderna quando esbarra nela). O .NET 7+ embarca `System.Threading.RateLimiting`/`AddRateLimiter()` nativo no ASP.NET Core.

## Abordagem

1. Ler o que `EBookDownloadRateLimiter` faz hoje de verdade: janela de tempo, contagem por IP, mensagem de "tente novamente em X segundos", cabeçalho de resposta.
2. Comparar com o que o middleware nativo (`FixedWindowRateLimiter`/`SlidingWindowRateLimiter`) expõe de fábrica — cabeçalho `Retry-After`, particionamento por IP, etc.
3. Só propor a troca se o nativo cobrir o comportamento observável de hoje sem perda (mensagem amigável em português, específica de download de ebook, é característica do produto — não pode virar genérica).

## Benefício se trocar

Menos código próprio pra manter e testar; usa o que o framework já dá de graça.

## Risco

O risco real aqui é o oposto do normal: **trocar por trocar, só por ser "mais nativo"**, e perder alguma característica específica do produto (mensagem de erro amigável, formato de resposta que o frontend já espera). Se o nativo não cobrir 1:1, a decisão correta é manter o caseiro — documentar a decisão no código ou no backlog, não deixar como dúvida recorrente.

## Como validar

- Se decidir manter: nenhuma mudança de código, só registrar a decisão e o motivo (evita alguém reabrir a mesma pergunta daqui a 6 meses).
- Se decidir trocar: `dotnet test` cobrindo o comportamento de rate limit antes e depois (a suíte de integração já tem `EBookDownloadRateLimiterTests.cs`), smoke test manual do fluxo de download batendo o limite de verdade.
