# Update de ebook não troca o PDF

## Status final — CONCLUÍDO em 2026-10-16

`BookService.UpdateAsync` agora trata `PdfBytes` para ebooks: usa o slug do livro salvo para sobrescrever a chave correta, persiste `EBookPdfPath` e mantém o PDF atual quando nenhum novo PDF é enviado. A validação de tamanho existente do `EBookService` continua sendo respeitada.

## Validação

- Testes unitários completos: `205/205` passando.
- Testes focados do `BookService`: `20/20` passando.
- Build Release da API: sucesso, 0 erros.
- `git diff --check`: limpo.
- Backend enviado para `master`/`origin/master` no commit `6550162` (`fix ebook PDF updates and vulnerable PKCS dependency`).

O build mantém apenas warnings preexistentes de dependências e nullable; nenhum foi introduzido pela correção.

## Pendência operacional

Não houve deploy nem validação de troca pelo download público nesta sessão. Isso fica como verificação do próximo deploy; a correção de código e sua cobertura de testes estão concluídas.

## Origem

- Item aberto em 2026-09-27 após o update responder sucesso sem trocar o PDF público.
- Implementação e testes registrados no commit `6550162` do `sharebook-backend`.
