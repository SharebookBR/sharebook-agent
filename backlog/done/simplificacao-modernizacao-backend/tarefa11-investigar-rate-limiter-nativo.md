# Tarefa 11 — Investigar rate limiter nativo do .NET vs `IEBookDownloadRateLimiter` caseiro

## Status

**Concluída em 2026-09-20 — decisão: manter o caseiro.** Investigação pura, sem mudança de código (o resultado esperado pelo próprio backlog era um resultado válido).

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

## Execução real

Leitura completa de `EBookDownloadRateLimiter.cs` (75 linhas), `IEBookDownloadRateLimiter.cs`,
`EBookDownloadRateLimitOptions.cs` e dos 3 pontos de uso em `BookController`
(`DownloadEBookAsync`, `GetDownloadEBookUrlAsync` e o fluxo de storage local legado — os três
compartilham o mesmo limite por IP), comparados com `System.Threading.RateLimiting`/
`AddRateLimiter()` (nativo desde .NET 7, com `FixedWindowRateLimiter` como candidato mais
próximo do comportamento atual).

**O que o caseiro faz hoje:**
- Partição por IP (normalizando IPv4-mapeado-em-IPv6 pra não duplicar o limite do mesmo
  cliente atrás de um proxy dual-stack — achado de teste real, coberto por
  `Ipv4MappedAddress_SharesTheSameLimit` na suíte de integração).
- Janela fixa configurável (`PermitLimit`/`WindowHours`, default 5 downloads / 24h).
- Resposta 429 com corpo JSON em português (`"Limite diário de downloads atingido..."`) e
  campo `retryAfterSeconds`, mais o header `Retry-After` padrão HTTP.
- Log de negócio específico a cada tentativa (permitida ou negada), com `slug`, `bookId`,
  `Remaining` e `RetryAfterSeconds` — usado para observabilidade do funil de download, não é
  genérico de throttle.
- Já usa `TimeProvider` (desde a Tarefa 10) — testável sem esperar tempo real de verdade, com
  4 testes de integração cobrindo os casos reais (limite estourado, IPs independentes,
  expiração da janela, IP mapeado).

**O que o `FixedWindowRateLimiter` nativo cobriria:**
- Particionamento por chave (IP) e janela fixa — sim, é literalmente o caso de uso que essa
  classe do BCL resolve.
- `QueueLimit = 0` reproduziria o comportamento de rejeitar na hora, sem enfileirar (o caseiro
  nunca enfileira, e enfileirar não faz sentido pra download de ebook).
- Resposta customizada (mensagem em português, `retryAfterSeconds`, header `Retry-After`) via
  callback `OnRejected` — dá pra fazer, mas o callback do `AddRateLimiter()` é configurado
  globalmente no middleware pipeline (`Startup.cs`), não por controller/endpoint agindo como
  hoje. Pra manter a mensagem específica desse fluxo (e não virar um 429 genérico pra qualquer
  rate limit futuro que a API venha a ter), seria necessário nomear uma policy específica
  (`[EnableRateLimiting("ebook-download")]`) e replicar a mesma lógica de mensagem/log dentro
  do `OnRejected` dessa policy — ou seja, a mesma quantidade de código de "tradução pra
  resposta HTTP específica do produto" que já existe em `DailyDownloadLimitExceeded`, só que
  vivendo na configuração do middleware em vez do controller.
- O log de negócio (`LogRateLimitOutcome`, com `slug`/`bookId`) só é possível no controller,
  onde esses dados existem — isso não muda trocando de limiter, é orquestração do fluxo de
  download, não do rate limiting em si.

**Decisão: manter o `IEBookDownloadRateLimiter` caseiro.** Não é resistência a usar o nativo
por hábito — é que a troca não elimina nenhuma linha de "lógica específica do produto"
(mensagem em português, formato de resposta, log de negócio), só desloca o armazenamento de
contagem de `IMemoryCache` (explícito, testável, ~30 linhas) para uma API do BCL com uma forma
de configuração diferente (middleware global + policy nomeada) que exigiria uma refatoração
estrutural real (mover a decisão de rate limit pra fora do controller, pro pipeline) só pra
manter o mesmo comportamento observável — exatamente o risco que o próprio backlog já
apontava ("trocar por trocar, só por ser mais nativo"). A implementação atual já usa
`TimeProvider`, `record struct`, primary constructor e tem cobertura de teste real dos 4
cenários que importam. Não há ganho líquido de custo cognitivo em trocar.

Nenhuma mudança de código nesta tarefa — só esta investigação registrada, para não reabrir a
mesma pergunta daqui a alguns meses.
