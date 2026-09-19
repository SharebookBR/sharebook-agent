# Tarefa 6 — Dividir `BookController`/`BookService`

## Status

Pendente.

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
