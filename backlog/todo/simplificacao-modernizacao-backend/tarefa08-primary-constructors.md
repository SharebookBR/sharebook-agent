# Tarefa 8 — Primary constructors (C# 12)

## Status

Pendente.

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
