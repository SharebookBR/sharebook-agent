# Correção da colisão de slugs dos volumes HPC

## Problema

Os volumes digitais 1, 2 e 3 de `The Art of High Performance Computing` são livros distintos, mas compartilhavam o slug truncado `the-art-of-high-performance-computing---volum`.

Em produção, a API resolvia esse slug para o volume 1. Os volumes 2 e 3 não tinham URL pública própria.

## Correção executada — 24/08/2026

- Foi publicado primeiro um redirect permanente do slug antigo para `the-art-of-high-performance-computing-volume-1`, preservando o recurso que a URL antiga entregava.
- O frontend foi publicado no commit `f532e3b18abaafb20efebe082d410bef12d56fc7`, pelo deployment Coolify `47doabjn0fth8ojsgemg9iqi`.
- Somente os três IDs exatos foram atualizados, em uma transação pelo túnel SSH:
  - Volume 1: `019ebe0f-afa8-7a7d-a0c6-b53fbaaabca3` → `the-art-of-high-performance-computing-volume-1`.
  - Volume 2: `019ebe0f-c020-70da-9fe1-7af3c0002d84` → `the-art-of-high-performance-computing-volume-2`.
  - Volume 3: `019ebd60-bfee-7df9-afa4-e283e25ad13a` → `the-art-of-high-performance-computing-volume-3`.

## Validação final

- A imagem exata do frontend ficou saudável em produção.
- O slug antigo responde `301` e chega ao volume 1 em um único redirect.
- As três APIs retornam o ID, o slug e o título correspondentes, com status `Available`.
- As três PDPs respondem `200`.
- A API do slug antigo responde `404`, eliminando a resolução ambígua no backend.
- Existem zero grupos de slug duplicado entre ebooks ativos.

