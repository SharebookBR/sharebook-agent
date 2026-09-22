# Tarefa 7 — Remover o repository genérico (`IRepositoryGeneric`/`RepositoryGeneric`)

## Status

**Concluída em 2026-09-20** — commit `d93a67d` direto em `develop`.

## O que existe hoje

Camada dupla reimplementando o EF Core: `RepositoryGeneric<T>` (por baixo, é EF puro) e `BaseService<T>` (que só repassa pra `IRepositoryGeneric<T>`) duplicam a mesma superfície de `Find`/`Get` com 4-5 overloads cada, pra todo `TEntity`. `DbContext` já é o Unit of Work, `DbSet<T>` já é o Repository, `IQueryable<T>` já é a query spec — o projeto nunca troca de ORM, então a indireção não paga custo nenhum.

## Decisão (validada nesta sessão)

Manter `BaseService<T>` — tem valor real (`FluentValidation` + `Result<T>` wrapper). Remover `IRepositoryGeneric`/`RepositoryGeneric`; `BaseService<T>` (e os services concretos que hoje usam `IBookRepository`, `ICategoryRepository` etc. além do genérico) passam a falar direto com `DbContext`/`DbSet<T>` via LINQ.

## Abordagem

Migrar serviço por serviço, não em lote único — é a mudança que mais toca lógica real de query (não é só mover arquivo):

1. Trocar a injeção de `IRepositoryGeneric<T>` por `ApplicationDbContext` direto em `BaseService<T>`.
2. Reescrever cada chamada `_repository.GetAsync(filter, order, page, itemsPerPage, includes)` pro LINQ equivalente direto no `DbSet<T>` (`.Where().Include().OrderBy().Skip().Take()`).
3. Repositories específicos por entidade que têm query customizada de verdade (`IBookRepository.FullSearchAsync`, por exemplo) continuam existindo — a remoção é só da camada *genérica*, não de todo repository.
4. Fazer um serviço por vez, cada um em commit isolado, começando pelos menores/menos críticos (ex: `CategoryService`) antes de chegar em `BookService`/`UserService`.

## Benefício

Menos um par interface+implementação genérica pra manter e entender; quem lê o código vê EF Core direto, sem precisar aprender uma API própria que faz a mesma coisa com nomes diferentes.

## Risco

Médio — ao contrário da Tarefa 2 (mecânica), aqui a tradução de `GetAsync(...)` genérico pra LINQ específico pode introduzir diferença sutil de comportamento (ex: ordem de `Include` afetando N+1, ou um filtro `Where` aplicado depois do que devia). Migrar um serviço por vez, com teste rodando antes e depois de cada um, reduz o risco a algo administrável.

## Como validar

- Por serviço migrado: `dotnet test` do que foi tocado, mais smoke test manual do fluxo principal daquele domínio.
- Nenhum lote mistura mais de um serviço — reversível e revisável isoladamente.
- `dotnet build` limpo confirma que nada ficou órfão referenciando a interface removida.

## Execução real

A investigação inicial mudou o plano: a ideia original era migrar `CategoryService` primeiro, isolado, como piloto de baixo risco. Na prática, todos os 6 services que estendem `BaseService<T>` (Book, User, BookUser, Category, AccessHistory, Meetup) compartilham a MESMA classe base — trocar o construtor de `BaseService<T>` de `IRepositoryGeneric<T>` pra `ApplicationDbContext` é uma mudança atômica que obrigatoriamente afeta os 6 ao mesmo tempo (não dá pra fazer "só a Category" sem quebrar compilação dos outros 5). A tarefa foi executada como um commit único e coerente, mas com validação isolada por cada consumidor tocado.

**Achado crítico durante a investigação** (quase passou despercebido): `BookRepository` tinha três overrides comportamentais reais que dependiam de despacho polimórfico através do `_repository` do `BaseService` — como a injeção de dependência antes passava a MESMA instância de `IBookRepository` tanto pro campo específico do `BookService` quanto pro genérico do `BaseService`, chamadas como `_repository.InsertAsync(...)` dentro do `BaseService`/`BookService` na verdade executavam o override de `BookRepository`, não a lógica genérica:
- `InsertAsync`: traduzia violação de índice único de slug (Postgres/SQLite) pra `DuplicateBookSlugException`, usada pelo loop de retry de slug em `BookService.InsertAsync`.
- `UpdateAsync`: protegia `ImageSlug`/`Slug`/`UserId` contra sobrescrita acidental quando o objeto de entrada vem parcialmente populado.
- `GetAsync(filter,order,page,itemsPerPage,descending)`: sempre incluía `BookUsers`+`User`, ignorando a lista de includes genérica.

Como o novo `_repository` do `BaseService` é um helper genérico (`EntityCrud<T>`) sem essa possibilidade de override por entidade, os três comportamentos foram portados pra dentro do próprio `BookService` (fazendo mais sentido semântico ali do que escondidos na camada de repository). O mesmo padrão apareceu em `MeetupRepository` (um `GetAsync` que sempre ordenava descendente e ignorava includes) — também portado pro `MeetupService`. Sem esse mapeamento cuidadoso, a remoção teria silenciosamente quebrado o retry de slug duplicado e a proteção de campos no update de livro, exatamente o risco que esta tarefa já antecipava.

**Repositories completamente eliminados** (não só a camada genérica, a classe inteira): `IBookUserRepository`/`BookUserRepository` e `IMeetupRepository`/`MeetupRepository` eram wrappers vazios de `IRepositoryGeneric<T>` sem nenhum método próprio — os serviços donos passaram a usar o `_repository` herdado do `BaseService` diretamente. `IMeetupParticipantRepository`/`MeetupParticipantRepository` era ainda mais morto: não estava injetado em NENHUM construtor no projeto inteiro além do próprio registro de DI — achado incidental, removido também.

**Repositories que sobreviveram, mas emagrecidos**: `Book`, `User`, `Category`, `Job`, `AccessHistory`, `BookDownloadEvent` continuam existindo (têm método customizado real e/ou são consumidos diretamente por outros services fora do seu próprio `BaseService` — `HomeService`, `EmailService`, `ImporterDashboardService`, jobs, `AccountController`). Suas interfaces foram reduzidas ao subconjunto realmente consumido em algum lugar do código (`Get`, `GetAsync` paginado quando usado, `UpdateAsync` cru quando usado, mais os métodos customizados) em vez do contrato genérico de 15 métodos.

**Deduplicação sem reintroduzir a indireção**: para não repetir ~130 linhas de CRUD genérico em `BaseService` + `BookRepository` + `UserRepository` + `CategoryRepository`, a lógica foi centralizada em `EntityCrud<T>` — mas como uma classe utilitária comum, nunca injetada via DI nem exposta por interface (cada repository/o `BaseService` a constrói internamente a partir do próprio `ApplicationDbContext`). Isso elimina a abstração que causava o custo cognitivo original (uma interface genérica que qualquer service concreto satisfazia "por acidente" de herança dupla) sem voltar a copiar e colar a mesma query em 4 lugares.

**Validação real**:
- `dotnet build` limpo em todo o solution (0 warnings, 0 errors) — usado de forma iterativa, corrigindo um grupo de erros de cada vez, até zerar.
- `dotnet test`: 145/146, mesma falha pré-existente e documentada do `HelperTests.ImageResize`.
- `BookServiceTests.cs` e `UserServiceTests.cs` precisaram ser migrados de repository mockado (Moq) pra `ApplicationDbContext` real, porque a base agora persiste de verdade — não dá mais pra mockar o CRUD genérico. A maioria dos casos usa EF Core InMemory; dois casos usam SQLite real em memória porque dependem de comportamento específico de provider relacional que o InMemory não replica: violação de índice único (pro teste de retry de slug duplicado) e o fixup de troca de instância que `User.ChangeAddress()` faz ao substituir a navegação `Address` por um objeto novo reaproveitando o Id antigo (o InMemory não resolve esse padrão da mesma forma que Postgres faz em produção).
- Smoke test manual via `curl` contra a API rodando localmente (SQLite): `Ping`, `Sitemap`, `Category`, `FreightOptions`, `FullSearch`, `Meetup` (200, sem exceção não tratada nos logs) — cobrindo leitura via `Book`/`Category`/`Meetup`. `Account/Register` e `Account/Login` retornaram erros de validação de negócio esperados (endereço incompleto, recaptcha, gate de versão de app) em vez de erro 500, confirmando que o pipeline `UserService`→`EntityCrud`→`ApplicationDbContext` executa de ponta a ponta sem quebrar.

Commit único (`d93a67d`), sem PR, direto em `develop` — não foi possível dividir em commits por serviço porque todos compartilham a mesma mudança de base, mas cada consumidor tocado foi validado individualmente antes do commit final.
