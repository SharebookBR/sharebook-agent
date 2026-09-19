# Tarefa 4 — Aposentar `BookDownload`, manter `BookDownloadEvent`

## Status

**Concluída em 2026-09-19** — commit `3b98ef1` direto em `develop` do `sharebook-backend` (a partir desta tarefa, sem PR — commit direto, por decisão do Raffa).

## O que existe hoje

Duas tabelas/services paralelos registrando a mesma coisa (quem baixou qual ebook), achado durante o merge `develop`↔`master` desta sessão:

- **`BookDownload`/`BookDownloadService`** (abril/2026): grava `BookId`, `UserId`, `UserAgent`, `IpAddress`, `DownloadedAt`. Sem índice pensado pra analytics. Feature que nunca decolou — não há nenhum consumidor real encontrado.
- **`BookDownloadEvent`/`BookDownloadEventService`** (setembro/2026): grava `BookId`, `UserId`, `Source`, `DownloadedAtUtc`, com índices compostos pra analytics (`BookId+DownloadedAtUtc`, `UserId+DownloadedAtUtc`). **Já alimenta a prateleira "Mais baixados" da Home v2**, já em produção.

Depois do merge, `BookController.DownloadEBookAsync` chama as duas.

## Decisão (validada nesta sessão)

Manter **`BookDownloadEvent`**, aposentar **`BookDownload`**.

Motivos:
1. `BookDownloadEvent` já é a fonte de verdade de uma feature em produção; `BookDownload` não tem consumidor conhecido.
2. `BookDownload` guarda `IpAddress`/`UserAgent` por linha — dado mais sensível (LGPD) — sem que nada leia esse dado de volta. Menos dado sensível guardado à toa.
3. **Verificado no frontend** (único consumidor do backend, branch `develop` sincronizada): busca por `ipAddress`, `userAgent`, `downloadedAt`/`downloadedAtUtc` no `src/` inteiro não retorna nenhum resultado — o frontend nunca lê esses campos de volta, só dispara o download via `DownloadEBookUrl`/`DownloadEBook`. Confirma que aposentar a tabela antiga é seguro do lado do único consumidor.

## Abordagem

1. Remover a chamada a `_bookDownloadService.RegisterDownloadAsync` em `BookController.DownloadEBookAsync` (as duas ocorrências, ver `diagnostico.md`).
2. Remover `IBookDownloadService`/`BookDownloadService`, `IBookDownloadRepository`/`BookDownloadRepository`, o registro de DI correspondente.
3. Migration de `DROP TABLE BookDownloads` — só depois de confirmado com o Raffa que não existe consumidor fora do código (script manual, BI, dashboard interno) lendo a tabela direto no banco.
4. Remover a entidade `BookDownload`, o validator e o mapping EF.

## Risco

O lote de decisão mais delicado do épico: é o único que envolve **dropar tabela de produção**, não é reversível como um rename. Mitigação: confirmar antes com o Raffa se não há leitura direta no banco (fora do código-fonte) antes de rodar a migration de drop. Se restar dúvida, primeiro lote pode só parar de escrever na tabela (remover a chamada no controller) e deixar o drop pra um lote seguinte, depois de um tempo de observação.

## Como validar

- `dotnet build`/`dotnet test` limpos após a remoção de código.
- Smoke test real do endpoint `DownloadEBook`/`DownloadEBookUrl` confirmando que `BookDownloadEvent` continua sendo gravado normalmente.
- Confirmar em produção (ou staging) que a prateleira "Mais baixados" da Home continua funcionando sem alteração — ela depende só de `BookDownloadEvent`.

## Execução real (2026-09-19)

Removido: entidade `BookDownload`, `BookDownloadValidator`, `BookDownloadService`/`IBookDownloadService`, `BookDownloadRepository`/`IBookDownloadRepository`, `BookDownloadMap`, `DbSet<BookDownload>` do `ApplicationDbContext`, os 3 registros de DI e as duas chamadas em `BookController.DownloadEBookAsync`.

**Achado real durante a execução — o diff automático do EF não funcionava.** A migration anterior da linha `master` (`AddBookDownloadEvents`) tem o próprio snapshot congelado (`.Designer.cs`) sem `BookDownload`, porque na `master` essa tabela nunca existiu — só na `develop`, de abril. Isso fazia `dotnet ef migrations add` gerar `Up()`/`Down()` vazios (o EF achava que não havia diferença a aplicar). Migration `DropBookDownloads` escrita manualmente, revertendo o `CreateTable` exato da migration original `AddBookDownload`.

**Achado extra, independente, corrigido no caminho**: `ApplicationDbContextFactory` (usado só em design-time pelo `dotnet ef`) nunca lia variável de ambiente, só `appsettings.json`/`appsettings.Development.json` — então `DatabaseProvider=postgres` no shell não tinha efeito nenhum ali, mesmo funcionando em `dotnet run`. Sem esse fix, **toda migration nova geraria coluna tipada pra SQLite por engano**, desde que a Tarefa 3 mudou o default do `appsettings.json` pra sqlite. Corrigido adicionando `.AddEnvironmentVariables()` + pacote `Microsoft.Extensions.Configuration.EnvironmentVariables`.

**Validação real, não só leitura de código**: subiu Postgres 16 local (`apt-get install postgresql`), criou a tabela `BookDownloads` com o DDL original da migration `AddBookDownload`, inseriu uma linha de dado real, e aplicou a cadeia completa de migrations até `DropBookDownloads` via `dotnet ef database update` — dropou limpo, sem afetar `Books`/`BookDownloadEvents`. Build limpo, 145/146 testes (mesma falha ambiental de sempre), app sobe e responde `Healthy` em `/health`.

**Achado à parte, fora de escopo, não corrigido**: a migration `RenameEFLogs` (pré-existente) depende de um nome de índice hardcoded específico do banco de produção real (`idx_17657_...`), impedindo rodar a cadeia de migrations do zero num banco limpo. Sem relação com esta mudança — candidato a item futuro de backlog (facilitaria a Tarefa 3/onboarding se corrigido).
