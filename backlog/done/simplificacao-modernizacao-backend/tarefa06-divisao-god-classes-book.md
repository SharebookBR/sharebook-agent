# Tarefa 6 — Dividir `BookController`/`BookService`

## Status

**Concluída em 2026-09-20** — commit `aa36087` direto em `develop`.

## O que existe hoje

- `BookController.cs` — 823 linhas, ~25 ações.
- `BookService.cs` — 1101 linhas, 30 métodos públicos, misturando: CRUD/regra de doação, aprovação/entrega/cancelamento, admin summaries, sitemap, busca full-text, navegação por categoria, recomendações, histórico de doações do usuário, stats, notas de facilitador, denúncia de copyright e contagem de download.

## Abordagem

Dividir por sub-responsabilidade, **mantendo `IBookService` como fachada estável** no primeiro momento (os métodos continuam acessíveis pelo mesmo contrato, só o arquivo por trás muda) — assim nenhum consumidor (controller, job, teste) precisa mudar na mesma tacada:

- `BookService.cs` — CRUD + ciclo de vida da doação (aprovar/entregar/cancelar/status).
- `BookSearchService.cs` — busca full-text, navegação por categoria, sitemap, recomendações.
- `BookAdminService.cs` — admin summaries, stats.

`BookController` divide de forma equivalente, ou pelo menos reorganiza os ~25 métodos em regiões claras por sub-responsabilidade dentro do mesmo arquivo, se dividir o controller em si não valer a pena nesse primeiro momento.

## Benefício

Maior redução de custo cognitivo do épico inteiro — é o arquivo mais lido/mexido do sistema. Depois de dividido, mudar uma regra de busca não exige mais entender as outras 25 responsabilidades do arquivo.

## Risco

O mais trabalhoso do épico, não o mais perigoso tecnicamente — mas tem uma pegadinha real: alguns métodos têm uso cruzado interno (ex: `InsertAsync` chama `GetAvailableSlugAsync` e `IsLeafCategory`, que hoje são privados/protegidos do mesmo arquivo). Dividir errado quebra esse acoplamento sutil sem gerar erro de compilação óbvio se os métodos virarem `public`/`internal` demais. Mitigação: mapear as chamadas internas entre métodos antes de mover, não só separar por "parece que é sobre busca".

## Como validar

- `dotnet build`/`dotnet test` limpos — a suíte de `BookServiceTests.cs` já existente é a rede de segurança principal aqui (cobre boa parte do CRUD e algumas regras).
- Smoke test manual dos fluxos principais: publicar livro, buscar, navegar por categoria, ver stats admin.
- Cada sub-serviço extraído em commit próprio, não uma reescrita monolítica.

## Execução real

Antes de mover qualquer método, o arquivo inteiro (1101 linhas) foi lido de ponta a ponta para mapear o acoplamento interno real, confirmando a pegadinha citada acima: `InsertAsync` depende de `IsLeafCategory`, `GetAvailableSlugAsync` e `DeleteUploadedPdfAfterSlugConflictAsync`; `UpdateAsync` também depende de `IsLeafCategory`; `BySlugAsync`/`RecentEBooksAsync` dependem do `SearchBooksAsync` privado; várias rotas de busca e admin dependem do `SetImageUrls` privado.

Decisão de implementação: em vez de composição com serviços concretos separados (que exigiria decidir qual classe "dona" de cada helper privado compartilhado, arriscando exatamente o acoplamento sutil citado no risco), a divisão foi feita com **C# partial class** — `BookService` continua sendo uma única classe em tempo de compilação, só que espalhada em três arquivos:

- `BookService.cs` (269 linhas) — construtor, CRUD (`InsertAsync`/`UpdateAsync`/`DeleteAsync`/`FindAsync`/`GetAllAsync`/`GetAsync`), ciclo de vida da doação (`ApproveAsync`, `ReceivedAsync`, `MarkAsDeliveredAsync`, `UpdateBookStatusAsync`, `RenewChooseDateAsync`, choose-date, `AddFacilitatorNotesAsync`, `ReportCopyrightAsync`, `IncrementDownloadCountAsync`) e os helpers privados compartilhados (`SetImageUrls`, `IsLeafCategory`, `GetAvailableSlugAsync`, `DeleteUploadedPdfAfterSlugConflictAsync`).
- `BookService.Search.cs` — busca full-text, navegação por categoria, sitemap, recomendações, `Random15BooksAsync`/`GetNewest15EBooksAsync`/`RecentEBooksAsync`, `SearchBooksAsync` privado.
- `BookService.Admin.cs` — admin summaries (`GetAdminBooksAsync` e query builders), stats (`GetStatsAsync`), doações do usuário (`GetUserDonationsAsync` × 2, summaries e filtros).

Como é a mesma classe, acesso a membro privado entre "arquivos" continua funcionando sem promover nada a `internal`/`public` — o risco central da tarefa foi neutralizado pela escolha de mecanismo, não só por mapeamento cuidadoso. `IBookService` e a assinatura pública de todo método permaneceram idênticos; nenhum consumidor (`BookController`, jobs, testes) precisou mudar.

`BookController` foi reorganizado com `#region` por sub-responsabilidade (CRUD, ciclo de vida da doação, busca/navegação, admin, solicitações, minhas doações, copyright/download de e-book, helpers privados) — optou-se por não dividir o arquivo em si, conforme a tarefa permite ("se dividir o controller em si não valer a pena nesse primeiro momento"), já que o controller não tem o mesmo grau de acoplamento privado interno que justificasse o mecanismo de partial class, e dividir em múltiplos arquivos de controller não traria ganho adicional relevante frente ao custo de mexer em todas as rotas.

Validação real, não só leitura de código:
- `dotnet build` limpo nos dois momentos (após dividir `BookService`, e de novo após reorganizar `BookController`).
- `dotnet test` rodado nos dois momentos: 145/146 — a mesma falha pré-existente e já documentada do `HelperTests.ImageResize` (chamada HTTP real, ver [Débitos técnicos backend](../debitos-tecnicos-backend.md)), zero regressão.
- Smoke test manual via `curl` contra a API rodando localmente (SQLite), cobrindo pelo menos uma rota de cada grupo: `Sitemap` (200, pública), `Ping` (200), `FreightOptions` (200), `Random15Books`, `GetNewest15EBooks`, `RecentEBooks`, `ByCategoryId`, `BySlug`, `Recommendations`, `AdminBooks`, `Stats`, `Create` (todas resolvendo rota e caindo em 401 de auth como esperado, sem exceção não tratada nos logs).
- Achado incidental durante o smoke test: `Random15BooksAsync` retorna 500 com o provider SQLite porque `.OrderBy(x => Guid.NewGuid())` não é traduzível pelo LINQ provider do SQLite (funciona em SQL Server via `NEWID()`). Confirmado que é pré-existente (mesmo código, só mudou de arquivo) rodando a mesma rota contra o binário anterior à divisão — não é regressão desta tarefa. Registrado como achado incidental no índice do épico, não corrigido aqui (fora de escopo, só afeta ambiente local).

Commit único (`aa36087`), sem PR, direto em `develop`, cobrindo os dois arquivos (`BookService` dividido + `BookController` reorganizado) — não foi feito em dois commits separados porque a validação (build/test/smoke) só faz sentido rodada contra o par completo controller+service.
