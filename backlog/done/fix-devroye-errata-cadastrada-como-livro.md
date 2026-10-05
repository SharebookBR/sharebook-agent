# Non-Uniform Random Variate Generation cadastrado como errata

## Estado

Concluído em 2026-10-05. O livro foi removido do catálogo público via `DELETE /api/Book/{id}`.

O livro público **Non-Uniform Random Variate Generation**, de Luc Devroye, slug `non-uniform-random-variate-generation`, parece frustrar a promessa da PDP: o PDF publicado não é o livro completo, mas uma errata/corrigenda de 7 páginas.

## Evidência

- API pública em 2026-10-05:
  - título: `Non-Uniform Random Variate Generation`
  - categoria: `Tecnologia > Geral`
  - tags: `Estatística`, `Algoritmos`
  - `eBookPdfPath`: `ebooks/non-uniform-random-variate-generation.pdf`
- PDF baixado pelo fluxo público:
  - arquivo: 87 KB
  - páginas: 7
  - metadado `Title: errors.dvi`
  - primeira linha extraída: `Corrigenda and addenda for “Non-Uniform Random Variate Generation” by Luc Devroye, Springer-Verlag, 1986`

## Problema

O usuário espera baixar o livro **Non-Uniform Random Variate Generation**. Receber apenas uma errata do livro é uma quebra forte de confiança.

Isso não é problema de categoria. É qualidade de acervo e asset errado.

## Correção esperada

1. Verificar se existe PDF completo legítimo e reutilizável do livro.
2. Se existir, substituir o PDF publicado e revalidar a PDP/download.
3. Se não existir, remover/cancelar o livro do catálogo público ou trocar o registro para representar honestamente a errata, caso isso tenha algum valor editorial.
4. Atualizar sinopse/metadados somente depois de decidir qual objeto será publicado.

## Validação

- `GET /api/book/Slug/non-uniform-random-variate-generation` retorna 404.
- `GET /api/Book/{id}` autenticado retorna 404.
- `GET /api/Book/FullSearch/Non-Uniform%20Random%20Variate%20Generation/1/10` retorna `totalItems: 0`.
- PDP pública `/livros/non-uniform-random-variate-generation` retorna 404.
- `GET /api/book/CategoryTree/1dc0f9e3-70d9-4bc8-a76c-90d7144e318c/1/100` voltou a Tecnologia = 274.
- `GET /api/book/CategoryTree/019dcbfc-0a09-702e-a0ab-090acb5597b6/1/100` voltou a Tecnologia > Geral = 63.
