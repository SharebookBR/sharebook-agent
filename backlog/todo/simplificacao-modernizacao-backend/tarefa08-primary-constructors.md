# Tarefa 8 — Primary constructors (C# 12)

## Status

**Concluída em 2026-09-20** — commit `5bb2482` direto em `develop`.

## O que existe hoje

Só 1 arquivo no projeto usa primary constructors. Praticamente todo `Service`/`Controller` ainda escreve o padrão clássico:

```csharp
private readonly IBookService _service;
private readonly IUserService _userService;
// ... mais N campos

public BookController(IBookService bookService, IUserService userService, /* ... */)
{
    _service = bookService;
    _userService = userService;
    // ...
}
```

`BookController` sozinho tem 5 campos desse tipo — puro boilerplate repetido em quase 90 classes de `Service`+`Api`.

## Abordagem

Converter construtores simples (só atribuição de campo, sem lógica extra) pra primary constructor, classe por classe ou em lote por pasta — é transformação mecânica e de baixíssimo risco, boa candidata a fazer junto com `dotnet format`/analyzer, se houver regra automatizável; senão, manual mas trivial de revisar (compilador garante equivalência).

## Benefício

Menos boilerplate por classe — puramente cosmético, mas em volume alto (quase todo Service/Controller do projeto).

## Risco

Nenhum — mudança de sintaxe equivalente, compilador garante. Único cuidado é com construtores que têm lógica além da atribuição simples (validação, valor default calculado) — esses não viram primary constructor sem reescrever a lógica, então pular esses casos.

## Como validar

- `dotnet build` limpo.
- `dotnet test` sem regressão.
- Prioridade baixa — fazer quando for tocar um arquivo por outro motivo (ex: junto com a Tarefa 5 ou 6, que já vão editar `BookService`/`BookController`), não como frente isolada de alta prioridade.

## Execução real

A tarefa tinha uma pista explícita ("boa candidata a fazer junto com `dotnet format`/analyzer, se houver regra automatizável") — o analyzer existe: `IDE0290` (Roslyn code style rule "use primary constructor"), com code-fix automático disponível via `dotnet format style --diagnostics IDE0290`. Testado primeiro num arquivo isolado (`BookService.cs`) pra validar que o resultado era correto e que o analyzer realmente só mexe em construtores de atribuição pura (confirmado: construtores com lógica extra, como o de `BookUserService` que faz `logger ?? NullLogger<T>.Instance`, foram corretamente ignorados pelo analyzer). Depois disso, rodado em lote no solution inteiro numa única passada.

Resultado bem menor do que a estimativa inicial da tarefa ("quase 90 classes"): **56 arquivos** convertidos entre `ShareBook.Api`, `ShareBook.Domain`, `ShareBook.Repository`, `ShareBook.Service` e `ShareBook.Test.Integration` — o restante das classes tinha lógica extra no construtor (validação, valor default calculado, `??`) e por isso ficou de fora automaticamente, como o analyzer deveria fazer.

Validação real: `dotnet build` limpo (0 errors, 3 warnings novos — ver achado abaixo), `dotnet test` 145/146 (mesma falha pré-existente do `HelperTests.ImageResize`), smoke test manual via `curl` contra a API rodando localmente cobrindo `Book`, `Category`, `Meetup` e `Home` (200, sem exceção não tratada).

**Achado incidental** (não corrigido, fora de escopo): a conversão em `BooksEmailService` expôs 3 warnings novos do compilador (`CS9113`, "parameter is unread") — os parâmetros `serverSettings`, `configuration` e `mailSenderHighPriorityQueue` são injetados no construtor mas nunca lidos em nenhum método da classe. Não é código morto introduzido por esta tarefa; só ficou visível porque virar parâmetro de primary constructor faz o compilador rastrear leitura de parâmetro, algo que não acontecia com um campo silenciosamente atribuído e nunca lido. Vale uma limpeza futura (remover a injeção não utilizada), mas não fazia sentido misturar com uma tarefa puramente mecânica.

Commit único (`5bb2482`), sem PR, direto em `develop` — fazia sentido em lote único aqui porque é literalmente a mesma transformação sintática repetida, sem nenhuma decisão de design por arquivo.
