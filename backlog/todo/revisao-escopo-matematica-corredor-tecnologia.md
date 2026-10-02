# Categoria "Matemática & Lógica": separar matemática do corredor de Tecnologia

## Estado

**Executado no banco de produção pelo OpenClaw e confirmado na API pública em 2026-10-02** (verificação feita pela sessão do claude-code-web, não pelo relatório do OpenClaw, que ainda não foi registrado no repo). Falta fechar a verificação (ver "Ainda não verificado") e as decisões abertas.

**Verificado na API (consultas sem cache):**

| Verificação | Esperado | Observado |
|---|---|---|
| Matemática & Lógica (raiz, `CategoryTree`) | 50 | **50** |
| Tecnologia (raiz, `CategoryTree`) | 324 − 50 = 274 | **274** |
| Tecnologia › Geral | 111 → 63 | **63** |
| Tecnologia › Dados | 33 → 31 | **31** |

Dois livros amostrados (*Calculus Volume 1*, *The Open Logic Text*) aparecem na subcategoria certa (Cálculo e Análise; Fundamentos e Lógica), com a raiz Matemática & Lógica como pai, e com capa (`imageUrl`) e sinopse intactas.

IDs observados: raiz Matemática & Lógica `d18ba112-a3bd-46ec-83d0-e7fef50ac4ec`; Cálculo e Análise `01a0fa32-7241-7000-0a4c-ecbc93ec5a0f`; Fundamentos e Lógica `01a0fa32-7243-7000-1ce3-26de718ab1ba`.

**Ainda não verificado:**
1. **`GET /api/Category` está com cache:** devolveu a árvore antiga, sem a raiz nova, enquanto o livro individual já mostra a categoria nova. Enquanto durar, menus e Home podem não exibir a categoria. Conferir de novo e descobrir o TTL.
2. Contagem por subcategoria (esperado 11, 12, 7, 10, 3, 7). Só o total da raiz foi conferido.
3. Páginas públicas (livro e categoria) com HTTP 200, e se a Home mostra a nova raiz.
4. Relatório do OpenClaw e o arquivo de rollback dele: não há registro no repo. Se não existir, a reversão exigiria reconstruir a categoria original a partir do CSV (`categoria_atual_id`).

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
4. **Home:** o `HomeService` trata categorias raiz de forma especial. Verificar se a nova raiz aparece e se faz sentido.
5. **Cache:** conferir cache de Home/SSR/categorias depois da mudança.
6. O OpenClaw deve registrar o relatório dele (IDs criados, contagens, caminho do rollback) neste arquivo e na memória dele. Ainda não está no repo.

## Riscos

- Mover livros muda contagens e navegação de categoria. O slug do livro não inclui a categoria, então as URLs dos livros não quebram. Páginas de categoria precisam ser conferidas.
- O esquema real das tabelas (nomes de tabela e coluna) foi inferido das migrations. O Passo 0 do prompt manda o OpenClaw confirmar antes de escrever.
- Classificação por título e sinopse, sem abrir os livros. Os 50 são uma proposta revisada, não um veredito editorial final.

## Validação

- Dry-run antes de escrever: 50 livros encontrados e `CategoryId` atual igual ao do CSV.
- Contagem por subcategoria igual à tabela acima.
- API pública conferida depois: árvore de categorias, contagem por categoria, 3 livros amostrados (capa e sinopse intactas), páginas públicas respondendo.
- Esperado e observado (ver Estado): Geral 111 → 63 e Dados 33 → 31.

## Evidência

- [tarefa01-resultado.md](tags-e-conhecimento-estruturado/tarefa01-resultado.md): contagens por tag e exemplos.
- [matematica-lista-movimentacao.csv](matematica-lista-movimentacao.csv): lista final.
- API pública: `GET /api/Book/CategoryTree/{categoryId}/{page}/{items}` (Tecnologia: `1dc0f9e3-70d9-4bc8-a76c-90d7144e318c`) e `GET /api/Category`.
- `memory/2026-10-02-tags-e-categoria-matematica.md`: relato da sessão.
