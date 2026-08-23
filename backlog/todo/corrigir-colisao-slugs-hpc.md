# Corrigir colisão de slugs dos volumes HPC

## Problema

Os volumes digitais 1, 2 e 3 de `The Art of High Performance Computing` são livros distintos, mas compartilham o slug truncado `the-art-of-high-performance-computing---volum`.

Em produção, a API resolve esse slug para apenas um registro. Os outros dois volumes não têm uma URL pública própria.

## Evidência — 23/08/2026

- Volume 1: `019ebe0f-afa8-7a7d-a0c6-b53fbaaabca3`.
- Volume 2: `019ebe0f-c020-70da-9fe1-7af3c0002d84`.
- Volume 3: `019ebd60-bfee-7df9-afa4-e283e25ad13a`.
- O volume 4 já tem slug distinto.
- Esta foi a única colisão de slug encontrada entre livros digitais ativos.

## Plano seguro

1. Criar slugs explícitos terminados em `volume-1`, `volume-2` e `volume-3`.
2. Publicar antes um `301` do slug antigo para o volume hoje resolvido por ele.
3. Atualizar somente os três IDs exatos, sem apagar registros.
4. Validar as três PDPs e os três contratos da API em produção.

## Critério de pronto

- Cada volume tem slug único e PDP própria.
- O slug antigo preserva tráfego por `301`.
- Zero slugs compartilhados entre livros digitais ativos.
