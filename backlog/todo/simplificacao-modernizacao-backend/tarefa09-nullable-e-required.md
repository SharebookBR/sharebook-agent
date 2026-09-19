# Tarefa 9 — Ligar `Nullable` + usar `required` nos ViewModels

## Status

Pendente.

## O que existe hoje

`Nullable` (nullable reference types) nunca é ligado em nenhum projeto de produção — só `ShareBook.Test.Integration` tem `Nullable: enable` — apesar de todos rodarem .NET 10 com `ImplicitUsings` habilitado. Zero uso de `required` (C# 11) nos 33 ViewModels de `ShareBook.Api/ViewModels`, que hoje dependem só do `FluentValidation` em runtime pra pegar campo obrigatório faltando.

Mesmo padrão de dívida que travou a migração do frontend (Angular): código legado assume que método nunca retorna `null` sem o compilador garantir isso.

## Abordagem

Incremental, projeto por projeto, do menor pro maior (mesmo espírito da Tarefa 9 do épico do frontend, "strict mode incremental"):

1. `ShareBook.Helper` (10 arquivos) primeiro — menor superfície, prova o processo.
2. `ShareBook.Domain`, depois `ShareBook.Repository`, `ShareBook.Infra.CrossCutting.Identity`.
3. `ShareBook.Service` (maior projeto) e `ShareBook.Api` por último.
4. Em paralelo, marcar propriedade obrigatória dos ViewModels com `required` conforme cada projeto liga `Nullable`.

## Benefício

Pega `NullReferenceException` em compile-time em vez de produção; ViewModel passa a declarar contrato real, não só confiar no validator.

## Risco

Alto volume de warning/erro liberado de uma vez ao ligar `Nullable` num projeto de anos — normalmente dezenas a centenas por projeto. Fazer projeto por projeto (não big bang) e tratar warning como erro só depois de zerar os existentes evita PR gigante e travado.

## Como validar

- Por projeto: `dotnet build` sem warning de nullability não tratado, depois marcar `<WarningsAsErrors>` pra esse tipo de warning naquele projeto especificamente.
- `dotnet test` sem regressão a cada projeto migrado.
