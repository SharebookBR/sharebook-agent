# Épico — Simplificação e modernização do código (sharebook-backend)

## Estado

- **Status:** diagnóstico entregue e revisado pelo Raffa em 2026-09-19. Tarefas de execução fatiadas (2-11). Tarefas 2 e 3 concluídas, PRs abertos.
- **Prioridade:** logo depois de [Simplificação e modernização do código (frontend)](../simplificacao-modernizacao-frontend/index.md), como continuação natural da mesma frente de redução de custo cognitivo, agora do lado do backend.
- **Valor:** alto — mesmo racional do épico do frontend: reduzir custo cognitivo de manutenção e destravar features futuras com menos atrito.
- **Origem:** pedido direto do Raffa em 2026-09-19. O `sharebook-backend` carrega muitos anos de história (.NET, camadas, patterns) que nunca foram revisados com a lente de "isso ainda paga o próprio custo cognitivo?".
- **Diagnóstico completo:** feito em sessão de 2026-09-19, com leitura real do código na branch `develop` pós-sync com `master` (commit `b27a6a6`), depois refinado numa rodada de revisão com o Raffa. Ver [`diagnostico.md`](diagnostico.md), incluindo a seção "Atualização pós-revisão".

## Diagnóstico — números que sustentam o épico

- 9 projetos .NET 10 organizados por camada técnica, com grafo de dependências limpo e sem ciclos (`Domain → Helper` · `Repository → Domain` · `Service → Helper, Repository` · `Jobs/Api` no topo).
- `BookController` com 823 linhas e `BookService` com 1101 linhas / 30 métodos públicos, misturando CRUD, aprovação de doação, admin/stats, sitemap, busca full-text, recomendações e e-book num único arquivo cada.
- `OperationsController` (313 linhas) esconde todo o domínio do importer de ebooks atrás de um nome de infraestrutura — e o mesmo cheiro atravessa pro frontend: `OperationsService` lá tem 6 de 7 métodos que são do importer.
- Camada dupla `RepositoryGeneric<T>` + `BaseService<T>` reimplementando, com indireção extra, o que `DbSet<T>`/`IQueryable<T>` do EF Core já resolve nativamente — decisão tomada de remover a camada genérica de repository, mantendo `BaseService<T>`.
- 28 das 29 interfaces em `ShareBook.Service` têm exatamente 1 implementação — existem só para permitir mock em teste.
- `Thread.CurrentPrincipal?.Identity?.Name` repetido 20 vezes, `DateTime.UtcNow` direto 16 vezes — ambos sem abstração testável.
- Pastas `AWSSQS/`/`AwsSqs/` duplicadas por casing (**resolvido na Tarefa 2**). `BookDownload` (abril) e `BookDownloadEvent` (setembro) coexistindo como duas fontes paralelas do mesmo dado — decisão tomada e validada contra o frontend: manter `BookDownloadEvent`.
- `Nullable` nunca ligado em nenhum projeto de produção; só 1 arquivo usa primary constructors (C# 12); `DatabaseProvider` cai pro motor errado (`sqlserver`, morto desde a migração pra Postgres) quando não configurado (**resolvido na Tarefa 3**).
- Cobertura de teste: 11/27 services (41%) e 3/10 controllers (Category, Meetup, Home) — `BookController` e `AccountController`, os dois mais críticos, sem nenhuma cobertura direta ou de integração.

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

Cada tarefa é de tema único e fecha com build limpo, suíte de teste verde (validado nesta sessão com o SDK do .NET 10 instalado: `dotnet build`/`dotnet test` rodam de verdade) e commit isolado — nunca lote misturado. A Tarefa 4 (decisão de banco de dados de tracking) e a Tarefa 5 (extração do importer, cross-repo com o frontend) são as que pedem mais cuidado de coordenação — ver risco em cada arquivo de tarefa.

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

## Tarefas

| # | Tarefa | Benefício | Risco | Status |
|---|---|---|---|---|
| 1 | [Diagnóstico de arquitetura e custo cognitivo](tarefa01-diagnostico.md) | Alto — base de evidência para todo o resto do épico | Baixo (é investigação) | **Entregue e revisado em 2026-09-19** |
| 2 | [Limpeza mecânica: AWSSQS/AwsSqs + namespaces file-scoped](tarefa02-limpeza-mecanica-namespaces.md) | Legibilidade generalizada | Zero | **Concluída em 2026-09-19** — [PR #611](https://github.com/SharebookBR/sharebook-backend/pull/611) |
| 3 | [Default de banco local: sqlite](tarefa03-default-banco-local-sqlite.md) | Zero fricção de onboarding | Baixo | **Concluída em 2026-09-19** — [PR #612](https://github.com/SharebookBR/sharebook-backend/pull/612) |
| 4 | [Aposentar BookDownload, manter BookDownloadEvent](tarefa04-aposentar-bookdownload.md) | Elimina duplicação + reduz PII guardada à toa | Alto — única tarefa que dropa tabela de produção | Pendente |
| 5 | [Extrair domínio do importer (backend + frontend)](tarefa05-extracao-importer-backend-frontend.md) | Descoberta melhora nos dois repositórios | Médio — coordenação de deploy cross-repo | Pendente |
| 6 | [Dividir BookController/BookService](tarefa06-divisao-god-classes-book.md) | Maior redução de custo cognitivo do épico | Médio — acoplamento interno sutil entre métodos | Pendente |
| 7 | [Remover repository genérico](tarefa07-remocao-repository-generico.md) | Menos indireção, EF Core exposto direto | Médio — toca lógica de query real | Pendente |
| 8 | [Primary constructors](tarefa08-primary-constructors.md) | Menos boilerplate, alto volume | Zero | Pendente |
| 9 | [Nullable + required](tarefa09-nullable-e-required.md) | Pega bug em compile-time | Baixo por projeto, alto volume de warning inicial | Pendente |
| 10 | [TimeProvider + acessor único de usuário](tarefa10-timeprovider-e-current-user.md) | Testabilidade real de regra sensível a tempo | Baixo, repetitivo | Pendente |
| 11 | [Investigar rate limiter nativo](tarefa11-investigar-rate-limiter-nativo.md) | Menos código próprio, se cobrir 1:1 | Baixo — pode terminar em "não mexer" | Pendente |
