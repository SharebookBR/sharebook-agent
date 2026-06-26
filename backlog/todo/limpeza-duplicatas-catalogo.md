# Limpeza de duplicatas no catálogo

## Problema
O catálogo tem volume relevante de livros duplicados — mesmo título cadastrado
várias vezes. Medição em 25/06/2026 (banco `sharebook`, tabela `"Books"`):

- **2677 livros** no total
- **163 grupos** de título duplicado (`lower(btrim(Title))`)
- **235 registros excedentes** (~9% do catálogo é duplicata)

Top ofensores: `orgulho e preconceito` (9×), `muito mais que 5inco minutos` (5×),
`fallen`, `diário de um banana`, `a moreninha`, `romeu e julieta`, `1984`,
`a culpa é das estrelas`, `memórias póstumas de brás cubas`, `bíblia sagrada` (4× cada).
Há também lixo de teste (`teste` 4×, `seleções de livros` 4×).

## Por que importa (retorno triplo)
1. **Busca**: duplicata fragmenta resultado e atrapalha ranking — o usuário vê o
   mesmo livro repetido em vez de descobrir variedade.
2. **SEO**: múltiplas PDPs do mesmo título brigam por canonical e diluem
   autoridade da URL que deveria indexar.
3. **Analytics / afiliado**: clique e view se espalham por N slugs do mesmo
   livro, fragmentando a atribuição (visto no GA4: `amazon_click` distribuído).

## Origem provável
- Importação repetida da mesma obra por sources diferentes.
- Variação de escrita do título (acento, espaço, "5inco"/"5") que escapou de dedupe.
- Cadastros de teste que vazaram pra produção (`teste`).

## Ações candidatas (a detalhar antes de executar)
- Levantar os grupos duplicados com slug, source, status (`Available`), views e
  downloads de cada cópia.
- Definir regra de sobrevivente: preferir o de maior tração (views/downloads) e
  metadado mais completo; redirecionar/aposentar os demais.
- **Não apagar cego** — PDP indexada que sumir vira 404/soft-404. Avaliar
  301 do slug perdedor para o vencedor (alinhar com SEO).
- Dedupe preventivo no importer para não reabastecer o problema.

## Critério de pronto
- Um título canônico por obra no público.
- Slugs aposentados com redirect adequado (sem soft-404 novo).
- Lixo de teste fora de produção.
- Guarda no importer contra reintrodução.

## Relações
- Pré-condição de qualidade para `busca-e-recomendacao-sharebook.md` (Fase 3 pede
  "catálogo minimamente limpo" antes de embeddings).
