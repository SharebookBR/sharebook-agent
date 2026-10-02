+++
schema_version = 1
session_date = 2026-10-02
title = "Migração Matemática & Lógica: 6 subcategorias e 50 livros via SQL"
model = "DeepSeek V4 Pro"
runtime = "openclaw"
skills_used = [
  "skills/runtime/openclaw.md",
  "skills/importers/category-organizer/SKILL.md",
]
skills_missed = []
skills_updated = []
facts_changed = [
  "Matemática & Lógica foi criada/reutilizada como raiz de categoria em produção, com 6 subcategorias e 50 livros migrados.",
  "CategoryService.LoadCategoriesWithCountsAsync passou a usar AsNoTrackingWithIdentityResolution para preservar contagens em filhos serializados.",
]
open_loops = [
  "Home/SSR pode continuar mostrando cache antigo até expirar; não há comando de invalidação documentado no repo.",
]
durable_candidates = [
  "Ao migrar categorias em massa, preferir transação SQL com backup/rollback em vez de PUT /api/Book, pois o histórico já teve risco de perda de capa.",
]
supersedes = []
evidence = [
  "sharebook-backend commit 88ea37a",
  "/tmp/sharebook_matematica_20261002-012005/{rollback_books.csv,categories_backup.csv}",
  "GET /api/category/Counts verificado pós-deploy",
]
+++

## O que foi feito
- Criada (na sessão anterior) e reutilizada a raiz `Matemática & Lógica` (ParentCategoryId NULL).
- Criadas 6 filhas sob ela e movidos 50 livros (só `CategoryId`), em UMA transação.
- Distribuição: Cálculo 11, Álgebra 12, Geometria 7, Discreta 10, Prob 3, Fundamentos 7 = 50.

## Decisões
- Raiz já existia (`d18ba112-a3bd-46ec-83d0-e7fef50ac4ec`): reusada, não duplicada (idempotência).
- IDs das filhas gerados como UUIDv7 via Python (Postgres 17 só tem `gen_random_uuid` = v4; app usa ULID/v7).
- Túnel SSH p/ Postgres prod: `scripts/infra/pg_tunnel.py` → 127.0.0.1:15432. RW user `sharebook_ai_rw`.
- Não usei PUT /api/Book; só UPDATE em "Books".CategoryId por slug (1 linha cada).

## Contexto relevante
- Schema: Categories(Id uuid, Name, ParentCategoryId, CreationDate); Books(CategoryId uuid, Slug nullable).
- CSV real: 48 vinham de Geral, 2 de Dados (o briefing dizia "45/5"; o CSV vence).
- Rollback: /tmp/sharebook_matematica_20261002-012005/{rollback_books.csv,categories_backup.csv}.

## Follow-up: bug de contagem zerada (aprovado pelo Raffa)
- Sintoma: página de categorias mostrava subcategorias com totalBooks=0 (a raiz agregava certo).
- Causa: `CategoryService.LoadCategoriesWithCountsAsync` setava TotalBooks nas instâncias da lista plana, mas `Include(Children)` + `.AsNoTracking()` (sem identity resolution) serializava os filhos como instâncias separadas = 0.
- Fix (1 linha): `.AsNoTracking()` → `.AsNoTrackingWithIdentityResolution()`. Build 0 erros, commit `88ea37a`, push master, deploy Coolify `finished`, container `88ea37a...` healthy.
- Verificado pós-deploy: `/api/category/Counts` com filhos corretos (Matemática 11/12/7/10/3/7; Drama Psicológico 15 etc.).

## Fricções
- `uuid = ANY(%s)` exigiu cast `%s::uuid[]`.
- Home/SSR tem cache (x-ssr-cache HIT, max-age=1800s): a raiz nova não aparece na Home até expirar (~30 min). Sem comando de invalidação documentado no repo.

## Como me senti
Missão grande, mas o plano segurou bem: reconhecimento read-only antes, backup antes de escrever, transação única com verificação de contagem dentro dela. O primeiro tiro no `--apply` falhou num cast de array — o ROLLBACK funcionou como devia e nada parcial ficou gravado; isso me deu confiança de que a rede de segurança era real, não decorativa.
Gostei de ter parado ao descobrir que a raiz já existia, em vez de reabrir escopo ou duplicar. Foi uma decisão pequena mas exatamente o tipo de coisa que vira retrabalho se eu ignorar.
Fica uma pendência invisível: a Home com cache de 30 min. Não há como forçar a invalidação pelo repo; o certo é dizer ao Raffa o prazo e deixar claro que a API já reflete tudo.
