# Dedupe preventivo no importer

## Objetivo

Evitar que o importer publique uma segunda versão digital da mesma obra e edição, sem impedir:

- múltiplos exemplares físicos;
- uma versão física e uma digital da mesma obra;
- edições ou adaptações digitais realmente distintas.

## Requisito

Título igual não basta para bloquear. A decisão deve combinar metadados normalizados, autor, edição/source e, quando disponível, hash ou comparação do conteúdo do PDF. Casos ambíguos devem ir para revisão humana.

## Evidência

O item 73 da source `baixelivros` reintroduziu `Eu e Outras Poesias` com PDF byte a byte idêntico ao registro digital existente.

## Critério de pronto

- Duplicata digital inequívoca é bloqueada antes da publicação.
- Livros físicos e edições digitais legítimas não recebem falso positivo.
- Decisão e evidências ficam registradas no histórico do item.
