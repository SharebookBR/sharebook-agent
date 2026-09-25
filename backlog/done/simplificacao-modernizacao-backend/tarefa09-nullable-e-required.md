# Tarefa 9 — Ligar `Nullable` + usar `required` nos ViewModels

## Status

**Concluída em 2026-09-20** — commits `7a54043`, `28b4b6b`, `500948b`, `4fa178b` e `3296dd3`, todos direto em `develop`.

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

## Execução real

Feita em 5 fatias, exatamente na ordem proposta na abordagem, cada uma com commit isolado direto em `develop`:

1. `ShareBook.Helper` + `Sharebook.Jobs` — commit `7a54043`.
2. `ShareBook.Domain` — commit `28b4b6b`.
3. `ShareBook.Repository` + `ShareBook.Infra.CrossCutting.Identity` — commit `500948b`. A maioria dos arquivos de `Repository` são migrations do EF Core com `#nullable disable` no topo, então não precisaram de mudança.
4. `ShareBook.Service` (47 arquivos, ~260 warnings) — commit `4fa178b`.
5. `ShareBook.Api` (67 arquivos, ~460 warnings) + `required` nos ViewModels de entrada — commit `3296dd3`.

Resultado final: `dotnet build ShareBook.sln` limpo (0 warnings, 0 errors) em todos os 9 projetos de produção. 146/146 testes unitários + 24/24 de integração passando a cada fatia. Smoke test manual via `curl` contra a API local (SQLite) validando health check, endpoints públicos e fluxos de login/registro/erro em cada uma das duas últimas fatias (as que tocam a camada exposta via HTTP).

Framework de decisão usado de forma consistente nas ~110 propriedades/parâmetros ambíguos:
- String simples: `string.Empty` por padrão; `string?` só com evidência concreta de opcionalidade (call site que atribui null, coluna de banco nullable, `ForMember` do AutoMapper com branch nulo).
- Coleção: `= []` ou `new List<T>()`.
- Navegação/referência obrigatória: `= null!` (ex.: `BookUser.Book`/`BookUser.User`, sempre populados).
- Navegação/referência opcional: `Type?` (ex.: `Book.User`/`Book.UserFacilitator` — nem todo book tem facilitador).
- POCO de Settings ligado via `services.Configure<T>()`: `string.Empty` nos defaults (não `required` — ver achado abaixo sobre `TokenConfigurations`).
- Retorno de `FindAsync`/`BySlugAsync`/repositório: sempre `T?`, propagado pelas interfaces (`IBaseService<T>`, `IBookService`, `IBookUserService`, `ICategoryService`, `IUploadService`, `IEBookService`) até onde o warning aparecia — em vários casos isso expôs chamador que não checava null.

**Achados reais corrigidos ao longo do processo** (não só warnings silenciados):
- `TokenConfigurations`: usar `required` quebrava com `CS9035` porque a classe é populada via `new T()` + `ConfigureFromConfigurationOptions<T>(...).Configure(instance)` — revertido para `string.Empty` assim que descoberto, virou regra do framework de decisão.
- `UserService.ConfirmHashCodePasswordAsync`: `HashCodePassword.Equals(...)` quebrava com NRE pra qualquer usuário que nunca pediu reset de senha.
- `UploadService.BackfillBookThumbnailsAsync`: arquivo com extensão não suportada no diretório de capas derrubava o backfill inteiro com NRE; agora vira falha registrada e o backfill segue.
- `BookUserService`/`BookUserEmailService`: 3 pontos (`NotifyInterestedAboutBooksWinnerAsync`, `InformTrackingNumberAsync`, `SendEmailBookInterestedAsync`) usavam resultado de `FirstOrDefault`/navegação opcional sem checar null antes de usar.
- `EmailService.SendToAdminsAsync`: quebrava se não houvesse nenhum admin cadastrado.
- `BookController.MainUsers`/`_IsBookMainUserAsync`/`_IsDonatorAsync`/`RequestBookAsync`/`CancelRequestAsync`: usuário ou livro buscado por Id sem checar null — vira 401/404 em vez de 500.
- `BookController.DownloadEBook`: `RemoteIpAddress` pode ser null atrás de certos proxies/hosts; caía em `IPAddress.None` como fallback seguro do rate limiter em vez de quebrar.

`required` aplicado de forma seletiva nos ViewModels de entrada (nunca nos de saída): só onde havia evidência concreta — `[Required]` já existente, `FluentValidation.NotEmpty()` no `BookValidator`/`UserValidator` do domínio de destino, ou checagem explícita no controller antes do uso. Exemplos: `CreateBookVM.Title/Author/ImageName/ImageBytes`, `LoginUserVM.Email/Password`, `UpdateUserVM.Name/Email`. Campos genuinamente opcionais (`Synopsis`, `FreightOption`, `ImageBytes` no update — imagem é opcional ao editar mas obrigatória ao criar) viraram nullable em vez de `required`.
