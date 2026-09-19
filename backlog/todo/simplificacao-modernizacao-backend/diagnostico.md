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
  → Jobs/0..9 - <Nome>.cs (prefixo numérico manual) + GenericJob/IJob
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
- O domínio do **importer de ebooks** (dashboard, prompts editoriais/tradução, notas admin, histórico de itens) não tem pasta própria — vive dentro de `OperationsController` e `ShareBook.Service/Importer` (só 2 arquivos), e o grosso do processamento real mora no repositório separado `sharebook-ebook-importer`, que lê/escreve direto no mesmo banco.

---

## 2. Principais fontes de custo cognitivo (com exemplos concretos)

1. **`BookController.cs` — 823 linhas, `BookService.cs` — 1101 linhas / 30 métodos públicos.** Um único `BookService` acumula: CRUD, aprovação de doação, admin summaries, sitemap, busca full-text, navegação por categoria, recomendações, histórico de doações do usuário, stats, notas de facilitador, denúncia de copyright e contagem de download. Para saber "onde mexo pra mudar X do livro" é preciso já ter memorizado qual dos 30 métodos é o certo.

2. **`OperationsController.cs` (313 linhas) é uma gaveta genérica disfarçada de "operações".** Ela mistura health check (`Ping`, `ForceException`), teste manual de e-mail/job — com **todo o domínio do importer de ebooks**: dashboard, editorial prompt, translation prompt, notas admin de item, histórico de item, listagem de itens, jobs. Ninguém adivinha que o domínio "importer" mora dentro de um controller chamado "Operations".

3. **Camada genérica dupla reimplementando o EF Core.** `RepositoryGeneric<T>` (EF puro por baixo) e `BaseService<T>` (que só repassa pra `IRepositoryGeneric<T>`) duplicam praticamente a mesma superfície de `Find`/`Get` com 4-5 overloads cada, para todo `TEntity`. Isso existe porque o EF Core **já é** o Repository + Unit of Work — a camada `Repository` do projeto reconstrói, com mais indireção, algo que `DbSet<T>`/`IQueryable<T>` já resolve nativamente.

4. **28 de 29 interfaces em `ShareBook.Service` têm exatamente 1 implementação.** `IUserService`, `IEmailService`, `IAwsSqsQueue`, `IHomeService`... nenhuma é implementada mais de uma vez — a única razão de existir é permitir `Mock<T>` em teste com Moq. Isso significa que, pra cada conceito de serviço, é preciso abrir 2 arquivos (interface + implementação) pra ler 1 conceito.

5. **Padrão `Thread.CurrentPrincipal?.Identity?.Name` repetido 20 vezes** em `AccountController`, `BookController`, `BookService`, `UserService`, `BookUserService`, sustentado por um filtro manual (`GetClaimsFilter`) que copia `HttpContext.User` pra `Thread.CurrentPrincipal` a cada request — desnecessário em ASP.NET Core, que já expõe `HttpContext.User`/`ClaimsPrincipal` nativamente via DI. Sem um helper único (`ICurrentUserAccessor`/extension method), cada lugar reinventa o `new Guid(...)`.

6. **Pastas `AWSSQS/` e `AwsSqs/` coexistem como irmãs**, com arquivos de um mesmo namespace (`ShareBook.Service.AwsSqs`) fisicamente divididos entre as duas — provavelmente um artefato de dev em máquina Windows (case-insensitive) que criou pasta nova sem perceber a duplicata. Achado cosmético, mas confunde: abre-se a pasta errada procurando o outro arquivo.

7. **Inconsistência de convenção recém-criada:** `IBookDownloadRepository`/`BookDownloadRepository` estão soltos na raiz de `Repository/`, enquanto toda entidade (Book, Category, Meetup, User...) tem sua própria subpasta. É o rastro do merge que acabamos de fazer entre `develop` (feature de abril, `BookDownload`) e `master` (feature de setembro, `BookDownloadEvent`) — as duas convivem hoje fazendo praticamente a mesma coisa (registrar quem baixou qual ebook), uma delas provavelmente redundante.

8. **Nomeação de Jobs por prefixo numérico manual** (`0 - CancelAbandonedDonations.cs` ... `9 - CleanupLogsTable.cs`). Não expressa ordem de execução real (jobs rodam por schedule, não em sequência), e obriga quem cria job novo a "adivinhar" ou renumerar.

9. **`Nullable` (nullable reference types) nunca é ligado em nenhum projeto de produção**, apesar de todos rodarem .NET 10 com `ImplicitUsings` habilitado — só `ShareBook.Test.Integration` tem `Nullable: enable`. É o mesmo ponto que travou o frontend na migração (código legado assume que `.Get()` nunca retorna null).

---

## 3. Análise IA-friendly

- **Onde um agente gastaria contexto à toa:** para entender "o que acontece quando um livro é publicado", é preciso abrir `BookController` (823 linhas, achar o método certo entre ~25), depois `BookService` (1101 linhas, achar `InsertAsync` entre 30 métodos), e ler método a método pra separar mentalmente "isso é regra de negócio do book" de "isso é sitemap" ou "isso é stats admin" que não tem nada a ver com a pergunta.
- **Descoberta ruim, concretamente:** um agente instruído a "mudar o prompt editorial do importer" jamais adivinharia que isso mora em `OperationsController`, um nome que sinaliza infraestrutura/health-check, não domínio de produto.
- **Onde nomes ajudam:** os nomes de arquivo dentro de cada domínio de `Service/<Domínio>/` são bons e previsíveis (`BookService`, `IBookService`, `BooksEmailService`) — o problema não é o nome do arquivo, é o **tamanho e a mistura de responsabilidades** dentro dele.
- **Onde a estrutura ajuda:** o grafo de dependências entre projetos é limpo e sem ciclos — um agente consegue confiar que mexer em `Domain` nunca quebra `Repository` por engano de dependência circular.
- **Custo de abrir "dois arquivos pra um conceito":** 28 pares interface+implementação no Service, cada um exigindo navegação dupla sem ganho real (não há segunda implementação nem plano de ter).

---

## 4. O que eliminaria

- **Uma das duas camadas genéricas** (`RepositoryGeneric<T>` **ou** `BaseService<T>`) — hoje ambas expõem quase a mesma API de `Find`/`Get` com overloads redundantes. Manter as duas significa que toda mudança de assinatura precisa ser replicada duas vezes.
- **As 28 interfaces de serviço com implementação única** que só existem para permitir mock — ou substituídas por injeção direta da classe concreta (Moq consegue mockar classes com métodos `virtual`), ou mantidas apenas onde houver razão real de swap futuro.
- **Uma das duas tabelas de tracking de download de ebook** (`BookDownload` vs `BookDownloadEvent`) — investigar com o Raffa qual delas é a fonte de verdade atual e aposentar a outra (achado que já apareceu no merge de `develop`↔`master` desta sessão).
- **A hierarquia genérica de controllers de 3 níveis** (`BaseController<T,R,A>` → `BaseCrudController` → `BaseDeleteController`, ~460 linhas) — hoje serve **um único consumidor real** (`CategoryController`, 76 linhas). O custo de manter 3 classes genéricas parametrizadas pra economizar CRUD de 1 controller é alto pra pouco benefício.
- **A cópia manual de `HttpContext.User` para `Thread.CurrentPrincipal`** via `GetClaimsFilter`, junto com os 20 usos espalhados de `new Guid(Thread.CurrentPrincipal?.Identity?.Name)` — substituir por um único acessor de usuário autenticado.

## 5. O que uniria, dividiria, moveria ou renomearia

- **Dividir `BookService`** em responsabilidades menores e nomeáveis: ciclo de vida da doação (aprovar/entregar/cancelar/status), busca e navegação (full-text, categoria, sitemap), admin/stats, e-book (download, contagem). Cada pedaço vira um arquivo pequeno que se lê sozinho, sem precisar entender os outros 29 métodos.
- **Mover o domínio do importer para fora de `OperationsController`** — um `ImporterController` dedicado (ou pasta própria dentro de features), deixando `OperationsController` só com health-check/diagnóstico real.
- **Unificar `AWSSQS/` e `AwsSqs/`** numa única pasta (mesmo namespace já é idêntico — é troca mecânica de `git mv`).
- **Renomear os Jobs** tirando o prefixo numérico do nome do arquivo — se a ordem de exibição em teste importa, isso já está resolvido por `Xunit.Extensions.Ordering` ou por convenção de teste, não precisa vazar pro nome do arquivo de produção.
- **Aproximar `Repository/BookDownloadRepository` (e a decisão sobre `BookDownload` vs `BookDownloadEvent`) da mesma convenção de subpasta por entidade** que todo o resto já segue.

## 6. Arquitetura que escolheria hoje

Sem compromisso com a estrutura histórica: o backend não precisa de Clean/Hexagonal/DDD/CQRS para o tamanho e a complexidade real do domínio Sharebook — a maior dor hoje **não é arquitetura em camadas** (o grafo Domain→Repository→Service→Api é limpo e sem ciclos), é **concentração de responsabilidades dentro de arquivos individuais** e **indireção genérica sem consumidor que justifique o custo**. A resposta certa não é trocar de arquitetura, é **enxugar** a atual:

- Manter os 9 projetos e o grafo de dependências como está — ele já é simples e correto.
- Dentro de `ShareBook.Service`, dividir os poucos "god services" (Book, User) em arquivos por sub-responsabilidade, mas ainda na mesma pasta de domínio — sem introduzir camada nova.
- Eliminar uma das duas camadas genéricas de CRUD (repository genérico ou base service genérico, não as duas).
- Remover interface onde não há segunda implementação nem plano de ter — usar a classe concreta.
- Dar ao domínio do importer um lugar com nome próprio, fora de "Operations".

Árvore de exemplo (mudança mínima, não big-bang):

```
ShareBook.Service/
  Book/
    BookService.cs              # CRUD + regra de negócio de doação
    BookSearchService.cs        # full-text, categoria, sitemap (extraído)
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
- Antes: "onde procuro isso?" → não há pista no nome — está em `OperationsController`, entre health-check e teste de e-mail. Depende de saber de cor que o importer mora ali.
- Depois: `ImporterController`/`Importer/ImporterEditorialService.cs` — o nome já entrega a resposta, sem precisar de memória prévia do projeto.

**Rastrear download de ebook (achado incidental do merge desta sessão):**
- Antes: duas tabelas/serviços paralelos fazendo o mesmo (`BookDownload`/`BookDownloadService` de abril, `BookDownloadEvent`/`BookDownloadEventService` de setembro), ambos chamados no mesmo endpoint depois do merge.
- Depois: uma única fonte de verdade, decidida com o Raffa.

## 8. Plano incremental de migração

Pequeno, reversível, testável, sem big bang — mesmo espírito do épico do frontend (lotes por domínio, checkpoint em dev a cada lote):

1. **Lote 0 (mecânico, risco zero):** unificar `AWSSQS/`↔`AwsSqs/` via `git mv`; tirar prefixo numérico dos nomes de arquivo de Job. Zero mudança de comportamento, só organização.
2. **Lote 1 (decisão + limpeza):** resolver com o Raffa qual tabela de download vence (`BookDownload` vs `BookDownloadEvent`) e aposentar a outra — inclui migration de dados se necessário.
3. **Lote 2 (extração, sem mudar contrato de API):** extrair o domínio do importer de `OperationsController` para `ImporterController` + pasta `Service/Importer/` própria. Endpoints continuam nas mesmas rotas (ou com redirect/alias, se o front já os consome).
4. **Lote 3 (divisão de god classes):** dividir `BookService` em arquivos por sub-responsabilidade (busca, admin/stats, core CRUD), mantendo a interface pública `IBookService` intacta no primeiro momento pra não quebrar consumidores — merge de arquivo é reversível e testável isoladamente.
5. **Lote 4 (redução de indireção):** escolher uma das duas camadas genéricas (repository genérico ou base service genérico) pra manter, migrando os serviços um a um; remover interfaces de implementação única que nenhum teste mocka de verdade.
6. **Lote 5 (higiene contínua):** ligar `Nullable: enable` projeto por projeto (começando pelo menor, `Helper`), consolidar os 20 usos de `Thread.CurrentPrincipal` num único acessor.

Cada lote fecha com build limpo (quando houver ambiente com .NET SDK disponível — este diagnóstico foi feito sem ele, só leitura estática de código), suíte de teste verde e commit isolado, igual à regra já em vigor pro frontend.
