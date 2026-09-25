# Diagnóstico — Simplificação e modernização do código (sharebook-backend)

Investigação real de código na branch `develop` pós-sync com `master` (commit `b27a6a6`, 2026-09-19). Nenhuma refatoração foi feita — isto é só o diagnóstico pedido na Tarefa 1.

---

## 1. Mapa da arquitetura atual

9 projetos .NET 10, organizados por **camada técnica** (não por domínio):

```
ShareBook.Domain (54 arquivos, 1524 linhas)
  → entidades soltas na raiz (Book.cs, User.cs, Category.cs...)
  → Common/ (BaseEntity, PagedList, Result)
  → DTOs/, Enums/, Exceptions/, Validators/
  depende de: Helper

ShareBook.Helper (10 arquivos, 477 linhas)
  → sem dependências internas

ShareBook.Repository (42 arquivos, 2149 linhas + 13 migrations)
  → Repository/<Entidade>/I<X>Repository.cs + <X>Repository.cs (um par por entidade)
  → Repository/Generic/ (RepositoryGeneric<T> — genérico sobre EF Core)
  → UoW/ (IUnitOfWork/UnitOfWork — transação)
  → Mapping/ (EF Fluent API)
  depende de: Domain

ShareBook.Infra.CrossCutting.Identity (4 arquivos, 94 linhas)
  → JWT: SigningConfigurations, TokenConfigurations, ApplicationSignInManager
  depende de: Domain

ShareBook.Service (87 arquivos, 7332 linhas) — maior projeto, de longe
  → 25 subpastas por domínio (Book/, User/, Category/, Meetup/, Email/, AwsSqs/, AWSSQS/, Analytics/...)
  → Generic/ (BaseService<T> — genérico sobre IRepositoryGeneric<T>)
  depende de: Helper, Repository

Sharebook.Jobs (14 arquivos, 1631 linhas)
  → Jobs/0..9 - <Nome>.cs (prefixo numérico expressando ordem do ciclo de vida da doação) + GenericJob/IJob
  depende de: Domain, Repository, Service

ShareBook.Api (66 arquivos, 3987 linhas)
  → Controllers/ (10 controllers)
  → Controllers/Generic/ (BaseController<T,R,A> → BaseCrudController → BaseDeleteController)
  → ViewModels/ (33 VMs), AutoMapper/ (2 profiles), Configuration/, Filters/, Middleware/, RateLimiting/
  depende de: Infra.CrossCutting.Identity, Service, Jobs

ShareBook.Test.Unit (30 arquivos, 3564 linhas) — 11/27 services com teste direto (41%)
ShareBook.Test.Integration (8 arquivos, 509 linhas) — 3/10 controllers com cobertura (Category, Meetup, Home)
```

**Grafo de dependências entre projetos** (sem ciclos — ponto positivo real):
`Domain → Helper` · `Repository → Domain` · `Identity → Domain` · `Service → Helper, Repository` · `Jobs → Domain, Repository, Service` · `Api → Identity, Service, Jobs`

**Onde vivem as coisas:**
- Regra de negócio: majoritariamente em `ShareBook.Service/<Domínio>/<Domínio>Service.cs`, mas boa parte também dentro dos próprios `Controllers` (checagens, mapeamento de status HTTP, extração de `Thread.CurrentPrincipal`).
- Persistência: `ShareBook.Repository`, com EF Core + Npgsql (PostgreSQL).
- Integrações externas: espalhadas dentro de `ShareBook.Service` por pasta própria — `AwsSqs`/`AWSSQS` (fila SQS), `Email` (MailKit/Rollbar), `Muambator` (rastreio de encomenda), `Recaptcha`, `Analytics` (GA4/Search Console), `PushNotification` (OneSignal), `Upload` (S3).
- O domínio do **importer de ebooks** (dashboard, prompts editoriais/tradução, notas admin, histórico de itens) não tem pasta própria — vive dentro de `OperationsController` e `ShareBook.Service/Importer` (só 2 arquivos), e o grosso do processamento real mora no repositório separado `sharebook-ebook-importer`, que lê/escreve direto no mesmo banco. **O cheiro atravessa a fronteira do sistema**: o `sharebook-frontend` tem um `OperationsService` de 7 métodos, dos quais 6 são do importer e só 1 é operação de verdade — o front já "sabe" que aquilo é tudo importer, só copiou a mesma mistura do backend (confirmado lendo o código do frontend).

---

## 2. Principais fontes de custo cognitivo (com exemplos concretos)

1. **`BookController.cs` — 823 linhas, `BookService.cs` — 1101 linhas / 30 métodos públicos.** Um único `BookService` acumula: CRUD, aprovação de doação, admin summaries, sitemap, busca full-text, navegação por categoria, recomendações, histórico de doações do usuário, stats, notas de facilitador, denúncia de copyright e contagem de download. Para saber "onde mexo pra mudar X do livro" é preciso já ter memorizado qual dos 30 métodos é o certo.

2. **`OperationsController.cs` (313 linhas) é uma gaveta genérica disfarçada de "operações".** Ela mistura health check (`Ping`, `ForceException`), teste manual de e-mail/job — com **todo o domínio do importer de ebooks**: dashboard, editorial prompt, translation prompt, notas admin de item, histórico de item, listagem de itens, jobs. Ninguém adivinha que o domínio "importer" mora dentro de um controller chamado "Operations". Confirmado que esse cheiro atravessa pro frontend (ver seção 1).

3. **Camada genérica dupla reimplementando o EF Core.** `RepositoryGeneric<T>` (EF puro por baixo) e `BaseService<T>` (que só repassa pra `IRepositoryGeneric<T>`) duplicam praticamente a mesma superfície de `Find`/`Get` com 4-5 overloads cada, para todo `TEntity`. Isso existe porque o EF Core **já é** o Repository + Unit of Work — a camada `Repository` do projeto reconstrói, com mais indireção, algo que `DbSet<T>`/`IQueryable<T>` já resolve nativamente.

4. **28 de 29 interfaces em `ShareBook.Service` têm exatamente 1 implementação.** `IUserService`, `IEmailService`, `IAwsSqsQueue`, `IHomeService`... nenhuma é implementada mais de uma vez — a única razão de existir é permitir `Mock<T>` em teste com Moq. Isso significa que, pra cada conceito de serviço, é preciso abrir 2 arquivos (interface + implementação) pra ler 1 conceito.

5. **Padrão `Thread.CurrentPrincipal?.Identity?.Name` repetido 20 vezes** em `AccountController`, `BookController`, `BookService`, `UserService`, `BookUserService`, sustentado por um filtro manual (`GetClaimsFilter`) que copia `HttpContext.User` pra `Thread.CurrentPrincipal` a cada request — desnecessário em ASP.NET Core, que já expõe `HttpContext.User`/`ClaimsPrincipal` nativamente via DI. Sem um helper único (`ICurrentUserAccessor`/extension method), cada lugar reinventa o `new Guid(...)`.

6. **Pastas `AWSSQS/` e `AwsSqs/` coexistem como irmãs**, com arquivos de um mesmo namespace (`ShareBook.Service.AwsSqs`) fisicamente divididos entre as duas — provavelmente um artefato de dev em máquina Windows (case-insensitive) que criou pasta nova sem perceber a duplicata. Achado cosmético, mas confunde: abre-se a pasta errada procurando o outro arquivo.

7. **Inconsistência de convenção recém-criada:** `IBookDownloadRepository`/`BookDownloadRepository` estão soltos na raiz de `Repository/`, enquanto toda entidade (Book, Category, Meetup, User...) tem sua própria subpasta. É o rastro do merge que acabamos de fazer entre `develop` (feature de abril, `BookDownload`) e `master` (feature de setembro, `BookDownloadEvent`) — as duas convivem hoje fazendo praticamente a mesma coisa (registrar quem baixou qual ebook). **Decisão tomada** (ver seção "Atualização pós-revisão" abaixo): manter `BookDownloadEvent`, aposentar `BookDownload`.

8. ~~Nomeação de Jobs por prefixo numérico manual~~ — **achado retratado.** Confirmado com o Raffa que o prefixo (`0 - CancelAbandonedDonations.cs` ... `9 - CleanupLogsTable.cs`) é convenção legítima e intencional, expressando a ordem do ciclo de vida conceitual da doação (cancelamento → lembrete → notificação tardia → some da vitrine → ...), não bagunça nem tentativa de expressar ordem de execução real. Removido do plano de ação.

9. **`Nullable` (nullable reference types) nunca é ligado em nenhum projeto de produção**, apesar de todos rodarem .NET 10 com `ImplicitUsings` habilitado — só `ShareBook.Test.Integration` tem `Nullable: enable`. É o mesmo ponto que travou o frontend na migração (código legado assume que `.Get()` nunca retorna null).

10. **Boilerplate de construtor e tipagem pouco idiomática pro .NET 10/C# 12-13**: só 1 arquivo usa primary constructors (contra ~90 classes de Service/Api que ainda escrevem `private readonly X _x; public Ctor(X x) => _x = x;` na mão); zero uso de `required` nos 33 ViewModels; `DateTime.UtcNow` chamado direto 16 vezes sem abstração (`TimeProvider`, disponível desde .NET 8, não é usado); `DatabaseProvider` cai pro valor `"sqlserver"` (motor morto, não usado em produção desde a migração pra Postgres) quando não configurado — achado que também gera fricção real de onboarding local.

---

## 3. Análise IA-friendly

- **Onde um agente gastaria contexto à toa:** para entender "o que acontece quando um livro é publicado", é preciso abrir `BookController` (823 linhas, achar o método certo entre ~25), depois `BookService` (1101 linhas, achar `InsertAsync` entre 30 métodos), e ler método a método pra separar mentalmente "isso é regra de negócio do book" de "isso é sitemap" ou "isso é stats admin" que não tem nada a ver com a pergunta.
- **Descoberta ruim, concretamente:** um agente instruído a "mudar o prompt editorial do importer" jamais adivinharia que isso mora em `OperationsController`, um nome que sinaliza infraestrutura/health-check, não domínio de produto — e o mesmo agente, se olhar o frontend achando que ali seria diferente, encontra a mesma confusão em `OperationsService`.
- **Onde nomes ajudam:** os nomes de arquivo dentro de cada domínio de `Service/<Domínio>/` são bons e previsíveis (`BookService`, `IBookService`, `BooksEmailService`) — o problema não é o nome do arquivo, é o **tamanho e a mistura de responsabilidades** dentro dele.
- **Onde a estrutura ajuda:** o grafo de dependências entre projetos é limpo e sem ciclos — um agente consegue confiar que mexer em `Domain` nunca quebra `Repository` por engano de dependência circular. A convenção de prefixo numérico dos Jobs também ajuda, não atrapalha, uma vez que se sabe o que ela significa.
- **Custo de abrir "dois arquivos pra um conceito":** 28 pares interface+implementação no Service, cada um exigindo navegação dupla sem ganho real (não há segunda implementação nem plano de ter).

---

## 4. O que eliminaria

- **A camada `RepositoryGeneric<T>`/`IRepositoryGeneric<T>`** (decisão tomada — ver seção abaixo). `BaseService<T>` fica, `DbContext`/`DbSet<T>` do EF Core assume o papel de repository direto.
- **As 28 interfaces de serviço com implementação única** que só existem para permitir mock — ou substituídas por injeção direta da classe concreta (Moq consegue mockar classes com métodos `virtual`), ou mantidas apenas onde houver razão real de swap futuro.
- **A tabela/serviço `BookDownload`** (decisão tomada — ver seção abaixo), mantendo `BookDownloadEvent`.
- **A hierarquia genérica de controllers de 3 níveis** (`BaseController<T,R,A>` → `BaseCrudController` → `BaseDeleteController`, ~460 linhas) — hoje serve **um único consumidor real** (`CategoryController`, 76 linhas). Fica como observação para decisão futura — não entrou no plano incremental desta rodada por ter só 1 consumidor e baixo risco de manutenção no estado atual.
- **A cópia manual de `HttpContext.User` para `Thread.CurrentPrincipal`** via `GetClaimsFilter`, junto com os 20 usos espalhados de `new Guid(Thread.CurrentPrincipal?.Identity?.Name)` — substituir por um único acessor de usuário autenticado.

## 5. O que uniria, dividiria, moveria ou renomearia

- **Dividir `BookService`** em responsabilidades menores e nomeáveis: ciclo de vida da doação (aprovar/entregar/cancelar/status), busca e navegação (full-text, categoria, sitemap), admin/stats. Cada pedaço vira um arquivo pequeno que se lê sozinho, sem precisar entender os outros 29 métodos.
- **Mover o domínio do importer para fora de `OperationsController`, nos dois repositórios** — `ImporterController`/`Service/Importer/` no backend, `ImporterService` extraído de `OperationsService` no frontend. Sem alias/redirect de rota — atualizar os dois lados juntos, coordenando o deploy.
- **Unificar `AWSSQS/` e `AwsSqs/`** numa única pasta (mesmo namespace já é idêntico — é troca mecânica de `git mv`).
- Manter a numeração dos Jobs como está — é convenção legítima, não achado.

## 6. Arquitetura que escolheria hoje

Sem compromisso com a estrutura histórica: o backend não precisa de Clean/Hexagonal/DDD/CQRS para o tamanho e a complexidade real do domínio Sharebook — a maior dor hoje **não é arquitetura em camadas** (o grafo Domain→Repository→Service→Api é limpo e sem ciclos), é **concentração de responsabilidades dentro de arquivos individuais** e **indireção genérica sem consumidor que justifique o custo**. A resposta certa não é trocar de arquitetura, é **enxugar** a atual:

- Manter os 9 projetos e o grafo de dependências como está — ele já é simples e correto.
- Dentro de `ShareBook.Service`, dividir os poucos "god services" (Book) em arquivos por sub-responsabilidade, mas ainda na mesma pasta de domínio — sem introduzir camada nova.
- Eliminar a camada de repository genérico; EF Core assume esse papel diretamente.
- Remover interface onde não há segunda implementação nem plano de ter — usar a classe concreta.
- Dar ao domínio do importer um lugar com nome próprio, fora de "Operations", nos dois repositórios.

Árvore de exemplo (mudança mínima, não big-bang):

```
ShareBook.Service/
  Book/
    BookService.cs              # CRUD + regra de negócio de doação
    BookSearchService.cs        # full-text, categoria, sitemap, recomendações (extraído)
    BookAdminService.cs         # admin summaries, stats (extraído)
    IBookService.cs             # só onde teste realmente mocka
  Importer/
    ImporterDashboardService.cs
    ImporterEditorialService.cs # prompts, notas, histórico (hoje em OperationsController)
  AwsSqs/                       # pasta única, sem duplicata de casing
    ...
ShareBook.Api/
  Controllers/
    ImporterController.cs       # extraído de OperationsController
    OperationsController.cs     # só health-check/diagnóstico real
```

## 7. Comparação antes/depois (fluxos reais investigados)

**Cadastrar/publicar um livro:**
- Antes: `BookController` (achar o endpoint certo entre ~25 ações) → `IBookService`/`BookService` (achar `InsertAsync` entre 30 métodos, 1101 linhas no arquivo) → `BookValidator` → `IBookRepository`/`BookRepository` → `RepositoryGeneric<Book>` → EF. 5-6 arquivos, sendo 2 deles enormes e cheios de responsabilidades não relacionadas à publicação.
- Depois: `BookController.CreateAsync` → `BookService.InsertAsync` (arquivo focado só em CRUD/regra de doação, sem os outros 25 métodos ao lado) → `BookValidator` → EF direto (sem repository genérico intermediário). Menos arquivos pra abrir, e o arquivo que sobra tem só o que importa pra essa tarefa.

**Autenticar usuário (login):**
- Já é razoavelmente contido: `AccountController.LoginAsync` → `UserService.AuthenticationByEmailAndPasswordAsync` → `ApplicationSignInManager.GenerateTokenAndSetIdentity` → `SigningConfigurations`/`TokenConfigurations`. 4-5 arquivos, cruzando 2 projetos (`Api` + `Infra.CrossCutting.Identity`) — aceitável, não é o ponto de maior dor.

**Mudar o prompt editorial do importer:**
- Antes: "onde procuro isso?" → não há pista no nome — está em `OperationsController` no backend e `OperationsService` no frontend, entre health-check e teste de e-mail. Depende de saber de cor que o importer mora ali, nos dois repositórios.
- Depois: `ImporterController`/`Service/Importer/ImporterEditorialService.cs` no backend, `ImporterService` no frontend — o nome já entrega a resposta dos dois lados, sem precisar de memória prévia do projeto.

**Rastrear download de ebook (achado incidental do merge desta sessão):**
- Antes: duas tabelas/serviços paralelos fazendo o mesmo (`BookDownload`/`BookDownloadService` de abril, `BookDownloadEvent`/`BookDownloadEventService` de setembro), ambos chamados no mesmo endpoint depois do merge.
- Depois: uma única fonte de verdade (`BookDownloadEvent`) — decisão tomada e validada contra o frontend (único consumidor do backend).

## 8. Plano incremental de migração

Refinado após discussão com o Raffa — 10 tarefas de execução, cada uma com arquivo próprio em `tarefa02-*.md` a `tarefa11-*.md` (a Tarefa 1 é este diagnóstico), fatiadas por tema único, não por "hygiene geral":

| # | Tarefa | Risco |
|---|---|---|
| 2 | [Limpeza mecânica: AWSSQS/AwsSqs + namespaces file-scoped](tarefa02-limpeza-mecanica-namespaces.md) | Zero |
| 3 | [Default de banco local: sqlite](tarefa03-default-banco-local-sqlite.md) | Baixo |
| 4 | [Aposentar BookDownload, manter BookDownloadEvent](tarefa04-aposentar-bookdownload.md) | Alto — única tarefa que dropa tabela de produção |
| 5 | [Extrair domínio do importer (backend + frontend)](tarefa05-extracao-importer-backend-frontend.md) | Médio — coordenação de deploy cross-repo |
| 6 | [Dividir BookController/BookService](tarefa06-divisao-god-classes-book.md) | Médio — acoplamento interno sutil entre métodos |
| 7 | [Remover repository genérico](tarefa07-remocao-repository-generico.md) | Médio — toca lógica de query real, não só move arquivo |
| 8 | [Primary constructors](tarefa08-primary-constructors.md) | Zero |
| 9 | [Nullable + required](tarefa09-nullable-e-required.md) | Baixo por projeto, alto volume de warning inicial |
| 10 | [TimeProvider + acessor único de usuário](tarefa10-timeprovider-e-current-user.md) | Baixo, repetitivo |
| 11 | [Investigar rate limiter nativo](tarefa11-investigar-rate-limiter-nativo.md) | Baixo — pode terminar em "não mexer" |

Cada tarefa fecha com build limpo, suíte de teste verde (validado nesta sessão: `dotnet build`/`dotnet test` rodam de verdade — 145/146 passando, 1 falha ambiental sem relação) e commit isolado, nunca lote misturado.

## Atualização pós-revisão (2026-09-19)

Depois da entrega inicial, o Raffa revisou e discutimos ponto a ponto:

- **Numeração dos Jobs**: retratado — é convenção legítima (ver item 8 da seção 2), removida do plano.
- **`BookDownload` vs `BookDownloadEvent`**: decisão tomada por `BookDownloadEvent`. Validado contra o código do frontend (único consumidor do backend) que nenhum campo específico da tabela antiga (`ipAddress`, `userAgent`, `downloadedAt`) é lido de volta em lugar nenhum — seguro aposentar.
- **Extração do importer**: escopo ampliado para cross-repo (backend + frontend) por pedido do Raffa — "extrair sem atualizar as URLs é meio porco". Achado a mais durante a investigação do frontend: o `OperationsService` de lá tem o mesmo problema (6 de 7 métodos são do importer).
- **Repository genérico**: confirmado com o Raffa que EF Core já cumpre esse papel — decisão de remover `IRepositoryGeneric`/`RepositoryGeneric`, mantendo `BaseService<T>` (que tem valor real de validação).
- **Modernização .NET 10/C# 12-13**: investigação adicional pedida pelo Raffa depois da entrega inicial, resultando nas Tarefas 8-11 (primary constructors, `Nullable`/`required`, `TimeProvider`, rate limiter nativo) — gaps reais que a primeira entrega, focada em custo cognitivo estrutural, não tinha coberto.
- **Ambiente de validação**: o .NET 10 SDK foi instalado nesta sessão (`apt-get install dotnet-sdk-10.0` — o mirror padrão do Ubuntu tinha o pacote, só precisou `apt-get update` primeiro), permitindo build e teste reais em vez de só leitura estática de código.
