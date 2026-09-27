# Update de ebook responde sucesso mas não troca o PDF

## Estado

Aberto desde 2026-09-27. Achado pelo OpenClaw ao trocar o PDF de *Bruxa por Acaso & o Galã de Milhões*. A causa foi confirmada no código pela sessão Claude Code web do mesmo dia. Existe contorno manual, então não é urgente, mas o erro é silencioso e já enganou uma operação real.

## Sinal observado

`sharebook_prod_book.py update --id <id> --pdf-path <novo.pdf>` respondeu "Livro alterado com sucesso!". O download público continuou servindo o PDF antigo (27 MB em vez de 5 MB).

## Causa

`BookService.UpdateAsync` (`sharebook-backend/ShareBook/ShareBook.Service/Book/BookService.cs`) nunca olha para `PdfBytes`. O `UpdateBookVM` aceita o campo e o AutoMapper o copia para a entidade, mas o método só trata imagem, título, autor, categoria, sinopse e afins. O upload do PDF (`_ebookService.UploadPdfAsync`) existe apenas no `InsertAsync`. O PDF novo é descartado sem erro.

## Escopo da correção

- Em `UpdateAsync`, quando `entity.HasPdfToUpload()` e o livro salvo é ebook, fazer o upload do PDF e atualizar `savedBook.EBookPdfPath`.
- Atenção: a entidade vinda do VM não traz `Slug`, e a chave é `ebooks/{Slug}.pdf` (`Book.GetPdfFileName()`). O upload precisa usar o `Slug` do `savedBook`, senão grava em `ebooks/.pdf`.
- Mesma chave de antes significa sobrescrever o arquivo, sem deixar lixo no S3. Se o slug mudou em algum momento, apagar o PDF antigo, como o fluxo de imagem já faz com `DeleteReplacedImageAsync`.
- Respeitar a validação de tamanho máximo já existente no `EBookService`.
- Teste unitário: update com `PdfBytes` chama `UploadPdfAsync` com o slug salvo e persiste `EBookPdfPath`. Update sem `PdfBytes` não mexe no PDF.

## Contorno enquanto não corrige

Sobrescrever direto no S3 a chave `ebooks/<slug>.pdf` e validar pelo download público (tamanho e páginas). Registrado também em `skills/importers/escrever-livros/SKILL.md`, seção "Armadilhas de publicação".

## Valor, esforço e risco

- **Valor:** médio. Todo ajuste de PDF de ebook (correção de texto, recompressão, nova edição) hoje exige acesso manual ao S3, e o script mente o resultado.
- **Esforço:** baixo. Um método, um teste, build e deploy.
- **Risco:** baixo, desde que a chave use o slug salvo.

## Validação

1. Build e testes do backend verdes.
2. Em dev, rodar `update --pdf-path` num ebook de teste e conferir pelo download público que o arquivo mudou (tamanho e páginas).
3. Depois do deploy, repetir num ebook real de baixo risco.

## Evidência

- `memory/2026-09-27-sharebook-originals-bruxa-e-lumi.md`, com o relato do OpenClaw e a leitura do código.
- Bruxa por Acaso: ID `01a0e34d-294d-75f1-b8b1-7952bd01650d`, PDF trocado manualmente no S3 para 5.116.691 bytes.
