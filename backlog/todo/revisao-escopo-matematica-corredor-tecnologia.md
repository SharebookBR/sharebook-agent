# Categoria "Matemática & Lógica": separar matemática do corredor de Tecnologia

## Estado

**Executado no banco de produção pelo OpenClaw em 2026-10-02 e verificação pública fechada em 2026-10-05.** A categoria já aparece na API de categorias, na Home, nas páginas públicas e nas contagens por subcategoria. Restam apenas decisões curatoriais pequenas, listadas em "Pendências e decisões abertas".

**Verificado na API (consultas sem cache):**

| Verificação | Esperado | Observado |
|---|---|---|
| Matemática & Lógica (raiz, `CategoryTree`) | 50 | **50** |
| Tecnologia (raiz, `CategoryTree`) | 324 − 50 = 274 | **274** |
| Tecnologia › Geral | 111 → 63 | **63** |
| Tecnologia › Dados | 33 → 31 | **31** |

Livros amostrados (*Calculus Volume 1*, *The Open Logic Text*, *Computação: Matemática Discreta*) aparecem na subcategoria certa, com a raiz Matemática & Lógica como pai, capa (`imageUrl`) e sinopse intactas.

IDs observados: raiz Matemática & Lógica `d18ba112-a3bd-46ec-83d0-e7fef50ac4ec`; Cálculo e Análise `01a0fa32-7241-7000-0a4c-ecbc93ec5a0f`; Fundamentos e Lógica `01a0fa32-7243-7000-1ce3-26de718ab1ba`.

**Verificado em 2026-10-05:**
1. `GET /api/Category` já devolve a raiz Matemática & Lógica e as 6 filhas; cache antigo expirou.
2. `GET /api/category/Counts` devolve raiz com 50 livros e filhas com 11, 12, 7, 10, 3 e 7 livros.
3. `GET /api/book/CategoryTree/{id}/1/100` confirmou as mesmas contagens por folha, todas ebooks.
4. Páginas públicas HTTP 200: `/categorias`, `/categorias/matematica-logica`, `/categorias/matematica-logica/calculo-e-analise`, `/livros/calculus-volume-1`, `/livros/the-open-logic-text`, `/livros/computacao-matematica-discreta`.
5. Home pública e `GET /api/home/categories-showcase` já mostram Matemática & Lógica com livros.
6. Rollback localizado na memória `memory/2026-10-02-matematica-categorias-migracao.md`: `/tmp/sharebook_matematica_20261002-012005/{rollback_books.csv,categories_backup.csv}`.

## O que é

O corredor `Tecnologia › Geral` concentra 111 dos 324 ebooks de Tecnologia (34%). Uma parte relevante é matemática pura, que não responde a nenhuma intenção de busca de dev ou tech lead. Toda a matemática do acervo mora em Tecnologia: conferidas as raízes Conhecimento & Carreira, Sociedade & Mundo, Vida & Bem-estar e Filosofia (36 livros), sem nenhum livro de matemática.

## Decisão

Criar a categoria raiz **"Matemática & Lógica"** com 6 subcategorias (livros ficam só nas folhas):

| Subcategoria | Livros |
|---|---|
| Cálculo e Análise | 11 |
| Álgebra e Teoria dos Números | 12 |
| Geometria e Topologia | 7 |
| Matemática Discreta e Grafos | 10 |
| Probabilidade e Estatística | 3 |
| Fundamentos e Lógica | 7 |
| **Total** | **50** (48 saem de Geral, 2 de Dados) |

Lista exata em [matematica-lista-movimentacao.csv](matematica-lista-movimentacao.csv) (slug, subcategoria, categoria atual e id).

**Nome:** "Matemática & Lógica" cobre o que o acervo tem (cálculo, álgebra, discreta, lógica, fundamentos) sem prometer estatística aplicada, que fica em Dados. "Ciências Exatas" foi descartado: nenhum livro de física ou química foi encontrado.

**Regra de corte:**
- Livro que **ensina matemática** vai para Matemática & Lógica.
- Livro que **usa matemática para computar** (programação, algoritmos, machine learning, teoria da computação) fica em Tecnologia.
- **Regra do Raffa:** título com "computer science", "algorithm", "Online" ou "R" fica em Tecnologia. A tag `Matemática` do épico de Tags cuida da descoberta transversal.

**Execução:** direto no banco, pelo OpenClaw, em uma transação, com arquivo de rollback. Motivo: o `PUT /api/Book/{id}` já apagou capas no passado (correção `12368a2`), e é arriscado em mudança em massa. A busca monta o `to_tsvector` na hora da consulta, então não precisa reindexar.

## Como chegamos na lista (evidência)

1. Contagem por palavra-chave nos 324 títulos e sinopses.
2. Classificação inicial **só por título** (47 livros "mover" e 7 "decidir").
3. Análise independente por subagente, lendo as 324 sinopses às cegas e comparando depois: coincidiu nos 47, moveria 6 dos 7 borderline e achou a folha de errata (abaixo). A leitura das sinopses mudou 3 das sugestões iniciais, então a classificação só por título não é confiável para casos de fronteira.
4. A regra do Raffa tirou 3 livros dos 53 resultantes (Algorithmic Graph Theory, Online Statistics Education, Probability and Statistics with Examples using R).

## Fica em Tecnologia (decidido ou adiado)

- Barrados pela regra do Raffa: *Algorithmic Graph Theory*, *Online Statistics Education*, *Probability and Statistics with Examples using R*, *Mathematics for Computer Science*, *Foundations of Computer Science*.
- Apontados pelo subagente como dúvida, deixados em Tecnologia por ora: *Category Theory for Programmers*, *Mathematics for Machine Learning*, *The Functional Analysis of Quantum Information Theory*, *Otimização Combinatória*, *Computational Mathematics with SageMath*. Revisitar quando as tags existirem.
- *Non-Uniform Random Variate Generation*: ver pendência 3.

## Pendências e decisões abertas

1. **Probabilidade e Estatística ficou com só 3 livros.** Manter ou fundir em "Fundamentos e Lógica"? Como a mudança já está em produção, fundir agora exige um novo UPDATE no banco (e remover a subcategoria) via OpenClaw. Decisão do Raffa ainda não tomada.
2. ***Computação: Matemática Discreta* foi movido** porque o título diz "Computação" e não "computer science". Se o Raffa quiser aplicar a regra a ele, é preciso devolver o livro a Tecnologia › Geral no banco (Discreta cai para 9, total 49).
3. **Folha de errata cadastrada como livro:** *Non-Uniform Random Variate Generation* (slug `non-uniform-random-variate-generation`). A sinopse descreve uma "corrigenda sheet" do livro do Devroye, não o livro. É problema de qualidade do catálogo. Abrir item próprio (substituir pelo livro real ou remover). Aguardando ok do Raffa.

## Riscos

- Mover livros muda contagens e navegação de categoria. O slug do livro não inclui a categoria, então as URLs dos livros não quebram. Páginas de categoria precisam ser conferidas.
- O esquema real das tabelas (nomes de tabela e coluna) foi inferido das migrations. O Passo 0 do prompt manda o OpenClaw confirmar antes de escrever.
- Classificação por título e sinopse, sem abrir os livros. Os 50 são uma proposta revisada, não um veredito editorial final.

## Validação

- Dry-run antes de escrever: 50 livros encontrados e `CategoryId` atual igual ao do CSV.
- Contagem por subcategoria igual à tabela acima.
- API pública conferida depois: árvore de categorias, contagem por categoria e subcategoria, livros amostrados (capa e sinopse intactas), páginas públicas e Home respondendo.
- Esperado e observado (ver Estado): Geral 111 → 63 e Dados 33 → 31.

## Evidência

- [tarefa01-resultado.md](../done/tags-e-conhecimento-estruturado/tarefa01-resultado.md): contagens por tag e exemplos.
- [matematica-lista-movimentacao.csv](matematica-lista-movimentacao.csv): lista final.
- API pública: `GET /api/Book/CategoryTree/{categoryId}/{page}/{items}` (Tecnologia: `1dc0f9e3-70d9-4bc8-a76c-90d7144e318c`) e `GET /api/Category`.
- `memory/2026-10-02-tags-e-categoria-matematica.md`: relato da sessão.
- `memory/2026-10-02-matematica-categorias-migracao.md`: execução OpenClaw, IDs, contagens, correção de `CategoryService.LoadCategoriesWithCountsAsync` e caminho do rollback.
- Verificação 2026-10-05: `GET /api/Category`, `GET /api/category/Counts`, `GET /api/book/CategoryTree/{id}/1/100`, `GET /api/home/categories-showcase` e páginas públicas `/categorias/matematica-logica` e `/categorias/matematica-logica/calculo-e-analise`.
