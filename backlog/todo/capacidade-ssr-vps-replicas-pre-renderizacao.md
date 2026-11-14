# Decidir capacidade estrutural do SSR: VPS, réplicas ou pré-renderização

## Escopo

Comparar custo, operação e capacidade de VPS maior, mais de uma instância SSR e
redução de renderização on-demand por pré-renderização. Considerar que Node usa
um núcleo de quatro e que 6/3 é limite defensivo, não capacidade final provada.

## Valor

Transforma contenção sob rajada em decisão de arquitetura verificável, em vez
de elevar limites por tentativa.

## Risco

Escalar antes de medir mascara desperdício; réplicas exigem cache/coalescimento
coerentes; SSG pode servir HTML desatualizado.

## Validação

Escolha documentada com custo/capacidade esperada; teste externo confirma zero
500, swap controlado e recuperação. Se for SSG, seguir o item de
pré-renderização.

## Relações

- Estrutural: `pre-renderizacao-paginas-publicas.md`.
- Recomendações: `recomendacoes-pre-processadas.md`.
- Evidência: `teste-carga-ssr-origem-externa.md`.
