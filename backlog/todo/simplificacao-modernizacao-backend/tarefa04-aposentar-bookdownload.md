# Tarefa 4 — Aposentar `BookDownload`, manter `BookDownloadEvent`

## Status

Pendente.

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
