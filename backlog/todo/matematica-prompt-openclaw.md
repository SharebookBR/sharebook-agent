# Prompt do OpenClaw: criar "Matemática & Lógica" e mover 50 livros

Contexto e decisões em [revisao-escopo-matematica-corredor-tecnologia.md](revisao-escopo-matematica-corredor-tecnologia.md). Lista de livros em [matematica-lista-movimentacao.csv](matematica-lista-movimentacao.csv).

**Antes de colar:** conferir as duas decisões abertas desse item (Probabilidade e Estatística com 3 livros; *Computação: Matemática Discreta*). Se alguma mudar, ajustar o CSV e as contagens esperadas abaixo.

**Estado:** executado pelo OpenClaw em 2026-10-02 e conferido na API (ver o item de backlog). Não rodar de novo: o prompt é idempotente, mas não há motivo para repetir.

```text
Missão: criar a categoria raiz "Matemática & Lógica" com 6 subcategorias e mover 50 livros para elas, DIRETO NO BANCO DE PRODUÇÃO. Decisão já aprovada pelo Raffa. Não reabra a discussão de escopo e não reclassifique livros.

ECONOMIA DE TOKENS (obrigatório)
- Não leia o catálogo nem sinopses. A classificação está pronta no CSV.
- Escreva UM script Python (psql/psycopg) que faça tudo. Não faça um turno de LLM por livro.
- Imprima só resumos: contagens e as linhas que divergirem. Nunca despeje JSON ou tabelas inteiras.

ENTRADA
Repo sharebook-agent, branch master, arquivo backlog/todo/matematica-lista-movimentacao.csv
(git pull na master e leia o arquivo).
Colunas: slug, titulo, subcategoria_destino, categoria_atual, categoria_atual_id, status. São 50 linhas, todas status=mover.

CATEGORIAS A CRIAR (nesta ordem)
Raiz: "Matemática & Lógica" (ParentCategoryId = NULL)
Filhas (ParentCategoryId = id da raiz):
 1. Cálculo e Análise
 2. Álgebra e Teoria dos Números
 3. Geometria e Topologia
 4. Matemática Discreta e Grafos
 5. Probabilidade e Estatística
 6. Fundamentos e Lógica
Livros devem ficar só em categorias-folha (as 6 filhas). Nunca na raiz.

ACESSO
Use o caminho de acesso ao banco de produção que você já usa (veja playbooks/runtime e memory; não invente conexão, host ou credencial). Se não houver caminho seguro, PARE e me avise. Não imprima credenciais.

PASSO 0: reconhecimento (somente leitura)
- Inspecione o esquema real das tabelas de categorias e de livros (nomes de tabela/coluna, NOT NULL, defaults, tipo do Id). Meu palpite, a CONFIRMAR: tabela "Categories" ("Id","Name","ParentCategoryId", talvez colunas de BaseEntity como data de criação) e coluna "CategoryId" em "Books". Se houver colunas NOT NULL extras, preencha como o resto da tabela faz.
- Confirme que "Matemática & Lógica" e as 6 filhas NÃO existem (compare ignorando caixa e acento). Se existirem, PARE e me avise.
- Dry-run: para cada slug do CSV, confira que o livro existe, que o slug é único e que o CategoryId atual == categoria_atual_id do CSV. Reporte: total encontrado (esperado 50) e divergências (lista curta). Se QUALQUER divergência, PARE e me mostre antes de escrever.

PASSO 1: backup e rollback
- Antes de escrever, grave localmente (fora do repo) um arquivo de rollback com (BookId, slug, CategoryId_original) dos 50 livros, e um dump/backup lógico das tabelas de categorias (ou confirme backup recente do banco). Informe o caminho.

PASSO 2: execução (uma única transação)
- BEGIN; inserir raiz e 6 filhas (Ids novos; use o mesmo padrão de geração de Id das categorias existentes, que parecem UUID v7; se não for possível, gen_random_uuid()); UPDATE dos 50 livros pelo slug, conferindo que cada UPDATE afeta exatamente 1 linha; verificar contagens por subcategoria; só então COMMIT.
  Esperado: Cálculo e Análise 11, Álgebra e Teoria dos Números 12, Geometria e Topologia 7, Matemática Discreta e Grafos 10, Probabilidade e Estatística 3, Fundamentos e Lógica 7 = 50.
  Qualquer desvio: ROLLBACK e me avise.
- Não altere nenhuma outra coluna de livro (título, sinopse, imagem, PDF, status, downloads, slug). Só CategoryId.
- Não use PUT /api/Book (risco conhecido de apagar capas). A mudança é só no banco.

PASSO 3: verificação (pela API pública, poucas chamadas)
- GET https://api.sharebook.com.br/api/Category: confirmar a árvore nova (raiz + 6 filhas).
- Contagem por categoria via GET /api/Book/Category/{id}/1/1 (campo totalItems) para as 6 filhas: deve bater com o esperado.
- Amostrar 3 livros em subcategorias diferentes via GET /api/Book/Slug/{slug}: categoria nova correta, imageUrl intacto, synopsis intacta.
- Conferir que Tecnologia › Geral perdeu 48 livros (111 → 63) e Tecnologia › Dados perdeu 2 (33 → 31). Confirme pelas contagens reais da API; se divergir, me avise.
- Cache: veja se Home/SSR/categorias têm cache que esconda a mudança; se houver comando de invalidação documentado no repo, use-o; se não, me diga quanto tempo esperar. A Home trata categorias raiz de forma especial: confirme se a nova raiz aparece e me diga o que viu.
- Abra a página pública de 2 livros e de 1 categoria nova (curl ou navegador) e confirme HTTP 200.

REGRAS
- Idempotente: se rodar de novo, deve detectar que já foi feito e não duplicar categorias.
- Em caso de dúvida, pare e pergunte. Não improvise correção em produção.
- Não crie PR. Registre o resultado em memory/ seguindo o padrão do repo, curto, e atualize o estado em backlog/todo/revisao-escopo-matematica-corredor-tecnologia.md.

RELATÓRIO FINAL (máx. 15 linhas)
IDs das 7 categorias criadas; contagem por subcategoria; caminho do rollback; resultado da verificação (ok/divergência); o que viu na Home; o que ficou pendente.
```
