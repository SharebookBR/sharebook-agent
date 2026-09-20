# Épico — Simplificação e modernização do código (sharebook-backend)

## Estado

- **Status:** diagnóstico entregue e revisado pelo Raffa em 2026-09-19. Tarefas 2, 3, 4, 5, 6 e 7 concluídas. A partir da Tarefa 4, commit direto em `develop`, sem PR (decisão do Raffa: "pare de abrir PR").
- **Prioridade:** logo depois de [Simplificação e modernização do código (frontend)](../simplificacao-modernizacao-frontend/index.md), como continuação natural da mesma frente de redução de custo cognitivo, agora do lado do backend.
- **Valor:** alto — mesmo racional do épico do frontend: reduzir custo cognitivo de manutenção e destravar features futuras com menos atrito.
- **Origem:** pedido direto do Raffa em 2026-09-19. O `sharebook-backend` carrega muitos anos de história (.NET, camadas, patterns) que nunca foram revisados com a lente de "isso ainda paga o próprio custo cognitivo?".
- **Diagnóstico completo:** feito em sessão de 2026-09-19, com leitura real do código na branch `develop` pós-sync com `master` (commit `b27a6a6`), depois refinado numa rodada de revisão com o Raffa. Ver [`diagnostico.md`](diagnostico.md), incluindo a seção "Atualização pós-revisão".

## Diagnóstico — números que sustentam o épico

- 9 projetos .NET 10 organizados por camada técnica, com grafo de dependências limpo e sem ciclos (`Domain → Helper` · `Repository → Domain` · `Service → Helper, Repository` · `Jobs/Api` no topo).
- `BookController` com 823 linhas e `BookService` com 1101 linhas / 30 métodos públicos, misturando CRUD, aprovação de doação, admin/stats, sitemap, busca full-text, recomendações e e-book num único arquivo cada (**resolvido na Tarefa 6** — `BookService` dividido em partial classes por sub-responsabilidade; `BookController` reorganizado em regions).
- `OperationsController` escondia todo o domínio do importer de ebooks atrás de um nome de infraestrutura — e o mesmo cheiro tinha atravessado pro frontend: `OperationsService` lá tinha 6 de 7 métodos que eram do importer (**resolvido na Tarefa 5** — `ImporterController`/`ImporterService` novos nos dois repositórios).
- Camada dupla `RepositoryGeneric<T>` + `BaseService<T>` reimplementando, com indireção extra, o que `DbSet<T>`/`IQueryable<T>` do EF Core já resolve nativamente (**resolvido na Tarefa 7** — `IRepositoryGeneric`/`RepositoryGeneric` deletados; `BaseService<T>` fala direto com `ApplicationDbContext`; repositories vazios de CRUD genérico também foram eliminados).
- 28 das 29 interfaces em `ShareBook.Service` têm exatamente 1 implementação — existem só para permitir mock em teste.
- `Thread.CurrentPrincipal?.Identity?.Name` repetido 20 vezes, `DateTime.UtcNow` direto 16 vezes — ambos sem abstração testável.
- Pastas `AWSSQS/`/`AwsSqs/` duplicadas por casing (**resolvido na Tarefa 2**). `BookDownload` (abril) e `BookDownloadEvent` (setembro) coexistindo como duas fontes paralelas do mesmo dado (**resolvido na Tarefa 4** — `BookDownload` aposentado, tabela dropada por migration).
- `Nullable` nunca ligado em nenhum projeto de produção; só 1 arquivo usa primary constructors (C# 12); `DatabaseProvider` cai pro motor errado (`sqlserver`, morto desde a migração pra Postgres) quando não configurado (**resolvido na Tarefa 3**).
- Cobertura de teste: 11/27 services (41%) e 3/10 controllers (Category, Meetup, Home) — `BookController` e `AccountController`, os dois mais críticos, sem nenhuma cobertura direta ou de integração.

## Achados adicionais durante a execução

Dois achados incidentais viraram item próprio de backlog: **[Débitos técnicos backend](../debitos-tecnicos-backend.md)** — `HelperTests.ImageResize` (teste "unitário" que faz chamada HTTP de verdade pra URL externa de terceiro, frágil por design) e a migration `RenameEFLogs` (nome de índice hardcoded do banco de produção real, impede rodar a cadeia de migrations do zero num ambiente limpo — descoberto validando a Tarefa 4). Nenhum dos dois é causado por este épico, mas ambos foram encontrados no caminho.

O fix de `ApplicationDbContextFactory` (design-time do `dotnet ef` nunca lia variável de ambiente) já foi corrigido dentro da própria Tarefa 4 — não precisou virar item de backlog à parte, porque sem ele a Tarefa 4 não seria concluída corretamente.

Achado extra na Tarefa 5: o `AGENTS.md` do `sharebook-frontend` ainda documentava Node 20 como versão de teste/build, mas o projeto já exige Node 22.22.3+ desde a migração pra Angular 22 — desatualizado, vale corrigir a documentação (não fez parte desta tarefa).

Achado extra na Tarefa 6: `Random15BooksAsync` já retornava 500 antes desta tarefa quando rodado com o provider SQLite (default local desde a Tarefa 3), porque `.OrderBy(x => Guid.NewGuid())` não é traduzível pelo provider SQLite do EF Core (funciona em SQL Server via `NEWID()`). Código idêntico, só mudou de arquivo na divisão — não é regressão da Tarefa 6, mas é um bug real de compatibilidade de provider que vale investigar depois (fora de escopo agora).

Achado extra na Tarefa 7: `IMeetupParticipantRepository`/`MeetupParticipantRepository` não estava injetado em nenhum construtor do projeto além do próprio registro de DI — código morto, removido junto. E um achado crítico que quase passou despercebido: `BookRepository` tinha três overrides comportamentais reais (tradução de violação de slug único, proteção de campos no update, Include hardcoded no GetAsync) que só funcionavam por despacho polimórfico através do `_repository` do `BaseService` — teriam sido silenciosamente perdidos se a remoção fosse feita sem mapear esse acoplamento; foram portados pra dentro do próprio `BookService`/`MeetupService`, ver detalhes na [Tarefa 7](tarefa07-remocao-repository-generico.md).

## Objetivo

Igual ao do frontend, adaptado para o backend: o objetivo **não é** atualizar tecnologia ou aplicar patterns modernos por si só. A prioridade é **reduzir custo cognitivo e tornar o backend humano-friendly e IA-friendly** — fácil de descobrir, navegar, entender e modificar, tanto por um dev novo quanto por um agente de IA com contexto limitado.

Pergunta central a repetir durante todo o diagnóstico:

> Se estivéssemos construindo este backend hoje, conhecendo o domínio do Sharebook como conhecemos agora, ele teria esta forma?

Sem apego ao passado (pastas, layers, abstrações, interfaces, services, repositories, helpers, DTOs, patterns não sobrevivem só porque já existem e funcionam), mas **sem perder funcionalidade**. Não é troca de arquitetura antiga por arquitetura sofisticada nova — é entregar uma arquitetura que precise de **menos explicação**, não uma mais bonita.

### IA-friendly como requisito arquitetural

Um agente deveria conseguir entrar no repositório e descobrir rapidamente: onde mora uma regra de negócio, onde começa um caso de uso, quais arquivos participam dele, onde estão os contratos de entrada/saída, onde ocorre persistência, onde estão as integrações externas, quais são as fronteiras entre domínios, quais dependências uma mudança pode afetar, e onde criar código novo para uma funcionalidade.

Pergunta a fazer durante o diagnóstico: **quanto contexto um agente precisa carregar para alterar com segurança uma regra de negócio?** O objetivo é reduzir esse custo — sem criar arquivos, comentários ou documentação só para "explicar" o código a uma IA. A melhor documentação arquitetural é uma estrutura óbvia por si mesma.

## Não partir de arquitetura pronta

Não assumir de antemão que a solução é Clean Architecture, Hexagonal, Vertical Slice, DDD, CQRS, MediatR, Repository Pattern, Unit of Work ou qualquer outro pattern. São ferramentas, não objetivos. Se algo disso já existe no backend hoje, questionar se está pagando o próprio custo cognitivo. Se alguma dessas ideias simplificar concretamente o Sharebook, propor; se aumentar arquivos/indireções/conceitos sem benefício proporcional, não propor. Também não copiar automaticamente a organização adotada no frontend — o backend deve encontrar suas próprias fronteiras naturais.

## Cadência de execução

Cada tarefa é de tema único e fecha com build limpo, suíte de teste verde (validado nesta sessão com o SDK do .NET 10 instalado: `dotnet build`/`dotnet test` rodam de verdade) e commit isolado — nunca lote misturado. Commit direto em `develop`, sem PR, a partir da Tarefa 4. A Tarefa 8 (primary constructors) é a próxima, de risco zero.

## Princípios (herdados do épico do frontend, válidos aqui também)

- Modernização incremental e verificável, não reescrita. Preservar comportamento antes de melhorar implementação.
- Nenhuma tarefa deste épico muda comportamento visível do usuário ou contrato de API sem que isso vire decisão de produto à parte.
- Cada tarefa de execução termina com build limpo, suíte de teste verde e commit isolado — nunca lote misturado de tarefas diferentes.
- Nada de "modernização por checklist": se um padrão atual já é a solução mais simples, ele fica como está.

## Fora de escopo agora

- Reescrever o backend do zero ou trocar de framework/tecnologia de base.
- Mudar comportamento de negócio, UX visível ou contrato de API.
- Adotar arquitetura sofisticada só por ser mais moderna — a métrica de sucesso é custo cognitivo, não quantidade de patterns aplicados.
- A hierarquia genérica de controllers de 3 níveis (`BaseController<T,R,A>`/`BaseCrudController`/`BaseDeleteController`) — tem só 1 consumidor real (`CategoryController`), mas baixo risco de manutenção no estado atual; fica como observação para decisão futura, não entrou nesta rodada.
- Corrigir o `HelperTests.ImageResize` flaky e a migration `RenameEFLogs` — achados incidentais, viraram [item de backlog próprio](../debitos-tecnicos-backend.md).
- Atualizar o `AGENTS.md` do frontend (Node 20 → 22.22.3+) — achado incidental da Tarefa 5, sem urgência.
- Corrigir `Random15BooksAsync` com provider SQLite — achado incidental da Tarefa 6, sem urgência (só afeta ambiente local; produção usa Postgres).

## Tarefas

| # | Tarefa | Benefício | Risco | Status |
|---|---|---|---|---|
| 1 | [Diagnóstico de arquitetura e custo cognitivo](tarefa01-diagnostico.md) | Alto — base de evidência para todo o resto do épico | Baixo (é investigação) | **Entregue e revisado em 2026-09-19** |
| 2 | [Limpeza mecânica: AWSSQS/AwsSqs + namespaces file-scoped](tarefa02-limpeza-mecanica-namespaces.md) | Legibilidade generalizada | Zero | **Concluída em 2026-09-19** — [PR #611](https://github.com/SharebookBR/sharebook-backend/pull/611) |
| 3 | [Default de banco local: sqlite](tarefa03-default-banco-local-sqlite.md) | Zero fricção de onboarding | Baixo | **Concluída em 2026-09-19** — [PR #612](https://github.com/SharebookBR/sharebook-backend/pull/612) |
| 4 | [Aposentar BookDownload, manter BookDownloadEvent](tarefa04-aposentar-bookdownload.md) | Elimina duplicação + reduz PII guardada à toa | Alto — única tarefa que dropa tabela de produção | **Concluída em 2026-09-19** — commit `3b98ef1` direto em `develop` |
| 5 | [Extrair domínio do importer (backend + frontend)](tarefa05-extracao-importer-backend-frontend.md) | Descoberta melhora nos dois repositórios | Médio — coordenação de deploy cross-repo | **Concluída em 2026-09-20** — commits `2e4ecc1` (backend) + `6891a1d` (frontend) |
| 6 | [Dividir BookController/BookService](tarefa06-divisao-god-classes-book.md) | Maior redução de custo cognitivo do épico | Médio — acoplamento interno sutil entre métodos | **Concluída em 2026-09-20** — commit `aa36087` direto em `develop` |
| 7 | [Remover repository genérico](tarefa07-remocao-repository-generico.md) | Menos indireção, EF Core exposto direto | Médio — toca lógica de query real | **Concluída em 2026-09-20** — commit `d93a67d` direto em `develop` |
| 8 | [Primary constructors](tarefa08-primary-constructors.md) | Menos boilerplate, alto volume | Zero | Pendente |
| 9 | [Nullable + required](tarefa09-nullable-e-required.md) | Pega bug em compile-time | Baixo por projeto, alto volume de warning inicial | Pendente |
| 10 | [TimeProvider + acessor único de usuário](tarefa10-timeprovider-e-current-user.md) | Testabilidade real de regra sensível a tempo | Baixo, repetitivo | Pendente |
| 11 | [Investigar rate limiter nativo](tarefa11-investigar-rate-limiter-nativo.md) | Menos código próprio, se cobrir 1:1 | Baixo — pode terminar em "não mexer" | Pendente |
