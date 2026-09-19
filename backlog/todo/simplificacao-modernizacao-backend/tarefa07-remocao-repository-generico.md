# Tarefa 7 — Remover o repository genérico (`IRepositoryGeneric`/`RepositoryGeneric`)

## Status

Pendente.

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
