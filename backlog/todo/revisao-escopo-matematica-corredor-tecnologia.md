# Categoria "Matemática & Lógica": separar matemática do corredor de Tecnologia

## Estado

**Decidido, aguardando execução pelo OpenClaw no banco de produção.** Decisões do Raffa em 2026-10-02. **Nada foi executado ainda**: a sessão do OpenClaw estourou o limite e volta cerca de 5 horas depois do fim da sessão que preparou isto.

**Próximo passo:** colar o prompt de [matematica-prompt-openclaw.md](matematica-prompt-openclaw.md) no OpenClaw. Ao receber o relatório dele, registrar o resultado neste arquivo e na memória do dia, e só então voltar à tarefa 2 do épico de [Tags](tags-e-conhecimento-estruturado/index.md).

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

1. **Probabilidade e Estatística ficou com só 3 livros.** Manter ou fundir em "Fundamentos e Lógica"? Se fundir: editar o CSV (coluna `subcategoria_destino`), o prompt e as contagens esperadas. Decisão do Raffa ainda não tomada.
2. ***Computação: Matemática Discreta* foi movido** porque o título diz "Computação" e não "computer science". Se o Raffa quiser aplicar a regra a ele, remover do CSV e baixar Discreta para 9 (total 49).
3. **Folha de errata cadastrada como livro:** *Non-Uniform Random Variate Generation* (slug `non-uniform-random-variate-generation`). A sinopse descreve uma "corrigenda sheet" do livro do Devroye, não o livro. É problema de qualidade do catálogo. Abrir item próprio (substituir pelo livro real ou remover). Aguardando ok do Raffa.
4. **Home:** o `HomeService` trata categorias raiz de forma especial. Verificar se a nova raiz aparece e se faz sentido.
5. **Cache:** conferir cache de Home/SSR/categorias depois da mudança.
6. Registrar o resultado da execução aqui e na memória, e atualizar o item 20 do índice.

## Riscos

- Mover livros muda contagens e navegação de categoria. O slug do livro não inclui a categoria, então as URLs dos livros não quebram. Páginas de categoria precisam ser conferidas.
- O esquema real das tabelas (nomes de tabela e coluna) foi inferido das migrations. O Passo 0 do prompt manda o OpenClaw confirmar antes de escrever.
- Classificação por título e sinopse, sem abrir os livros. Os 50 são uma proposta revisada, não um veredito editorial final.

## Validação

- Dry-run antes de escrever: 50 livros encontrados e `CategoryId` atual igual ao do CSV.
- Contagem por subcategoria igual à tabela acima.
- API pública conferida depois: árvore de categorias, contagem por categoria, 3 livros amostrados (capa e sinopse intactas), páginas públicas respondendo.
- Esperado: Geral 111 → 63 e Dados 33 → 31.

## Evidência

- [tarefa01-resultado.md](tags-e-conhecimento-estruturado/tarefa01-resultado.md): contagens por tag e exemplos.
- [matematica-lista-movimentacao.csv](matematica-lista-movimentacao.csv): lista final.
- API pública: `GET /api/Book/CategoryTree/{categoryId}/{page}/{items}` (Tecnologia: `1dc0f9e3-70d9-4bc8-a76c-90d7144e318c`) e `GET /api/Category`.
- `memory/2026-10-02-tags-e-categoria-matematica.md`: relato da sessão.
