# Revisão de escopo: livros de matemática no corredor de Tecnologia

## Estado

**Aberto, sem dono.** Descoberto em 2026-10-02 durante o ciclo manual do épico de Tags ([tarefa 1](tags-e-conhecimento-estruturado/tarefa01-resultado.md)). O Raffa concordou que o ponto precisa ser endereçado. Nada foi alterado no catálogo.

## O que é

O corredor `Tecnologia › Geral` concentra 111 dos 324 ebooks de Tecnologia (34%). Uma parte relevante é matemática pura, que não responde a nenhuma intenção de busca de dev ou tech lead.

Contagem por palavra-chave em título e sinopse (324 livros, a refinar):

- Cálculo/Álgebra/Análise: **43** livros (19 deles com a palavra no título).
- Matemática Discreta/Combinatória: 15.
- Teoria da Computação: 10.

Exemplos vistos: *Beginning and Intermediate Algebra*, *Active Calculus*, *Basic Analysis I*, *Combinatorics Through Guided Discovery*, *A Gentle Introduction to the Art of Mathematics*, *Geometry with an Introduction to Cosmic Topology*.

Matemática Discreta e Teoria da Computação são vizinhas diretas de computação e provavelmente ficam em Tecnologia. O núcleo da dúvida é Cálculo, Álgebra e Análise.

## Por que importa

- A categoria "Geral" não diz nada ao leitor e é o maior balde do corredor.
- Misturar matemática pura com livros técnicos dilui as vitrines e as tags do épico de Tags.
- Pelo `skills/product-ux/catalog-strategy/SKILL.md`, categoria é a prateleira principal. Um livro de cálculo numa prateleira de tecnologia é ruído de descoberta.

## Opções a avaliar (nenhuma decidida)

1. **Manter em Tecnologia** e resolver só com tags (por exemplo `Matemática`). Custo mínimo, mas mantém o ruído na prateleira.
2. **Criar uma categoria própria** (nome a definir, por exemplo "Matemática" ou "Ciências Exatas") e mover os livros. Custo médio, melhora a descoberta. Exige decidir se é categoria principal ou subcategoria.
3. **Mover para uma categoria existente** que já acomode ciências. Precisa checar se alguma serve.

## Escopo

- Listar todos os livros candidatos com revisão humana (palavra-chave não basta).
- Decidir a opção acima.
- Se houver movimentação: executar de forma idempotente e reversível.

## Valor e esforço

- **Valor:** médio. Limpa o corredor de Tecnologia e destrava vitrines melhores.
- **Esforço:** baixo a médio, dependendo da opção.
- **Dependência:** a decisão de escopo influencia o vocabulário v0 do épico de Tags (tarefa 2). Convém decidir antes ou junto.

## Riscos

- Mover livros muda contagens e navegação de categoria. Checar páginas de categoria, sitemap e URLs públicas (o slug do livro não inclui a categoria, o que ajuda, mas precisa confirmar nas páginas de categoria).
- Categoria nova no backend e no frontend pode exigir mudança de código, não só de dados. Verificar antes de prometer prazo.
- Contagem por palavra-chave tem falsos positivos e negativos. Não executar movimentação sem lista revisada.

## Validação

- Lista revisada por humano antes de qualquer movimentação.
- Contagem por categoria antes e depois.
- Conferir que nenhum livro movido fica sem categoria e que as páginas públicas respondem.
- Reabrir a contagem de `Geral` ao final: deve cair visivelmente.

## Evidência

- `backlog/todo/tags-e-conhecimento-estruturado/tarefa01-resultado.md` — contagens e exemplos.
- API pública: `GET /api/Book/CategoryTree/{categoryId}/{page}/{items}` (Tecnologia: `1dc0f9e3-70d9-4bc8-a76c-90d7144e318c`).
