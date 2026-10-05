# Tarefa 4 — PDP e página pública por tag

## Status

Fechada para avanço.

## Objetivo

Tornar tags úteis para descoberta pública sem transformar a PDP em painel poluído.

## Escopo

- exibir tags discretas na PDP;
- criar página pública por tag, por exemplo `/tags/python`;
- listar livros disponíveis associados à tag;
- garantir SSR e navegação mobile/desktop;
- considerar título SEO do tipo "Livros gratuitos sobre Python".

## Critérios de pronto

- tags aparecem de forma discreta e clicável na PDP;
- página de tag funciona com SSR;
- somente livros disponíveis aparecem publicamente;
- UI passa por validação visual em desktop e mobile;
- busca e navegação preservam comportamento atual.

## Implementação realizada

- `51a0160 feat(tags): adiciona tags na PDP e pagina publica /tags/:slug`
  - PDP exibe até 3 tags discretas e clicáveis;
  - `/tags/:slug` lista livros por tag;
  - tags vêm embutidas em `BookVM`, sem chamada extra na PDP.
- `fe1d0ee fix(tags): ajusta breadcrumb da pagina de tag`
  - breadcrumb da página fica `Vitrine / tags / python`.
- `0fa8a88 feat(tags): adiciona indice publico de tags`
  - `/tags` lista as tags públicas.
- `c522629 fix(tags): simplify tag index cards`
  - cards mostram apenas o nome bonito;
  - tags sem livros aparecem desabilitadas usando `totalBooks`.
