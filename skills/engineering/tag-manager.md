# Tag Manager (Tags do Sharebook)

Skill operacional para gerir as tags do catálogo do Sharebook: modelo de dados, motor mecânico, vocabulário controlado, scripts e endpoints. Cobre backend (`sharebook-backend`), operação de produção (`scripts/production/` no `sharebook-agent`) e regras editoriais.

## Quando usar

- Criar, renomear, desativar ou ajustar alias/família de uma tag
- Taggear ou retaggear livros (manual ou por backfill)
- Adicionar regra ao motor mecânico de tags
- Diagnosticar por que um livro nasceu com (ou sem) uma tag
- Varrer o catálogo por livros de um tema para aplicar uma tag

## Modelo de dados

- **Tag**: `Id` = slug texto (ex: `kubernetes`, `csharp`), `Name`, `Aliases` (text[]), `Family`, `Status` (Active/Inactive/Deprecated), `IsPublic`, `Description`, `UsageNotes`.
- **BookTag** (join): `BookId`, `TagId`, `Position` (1..3), `Source` (Manual/Assisted/Backfill/Mechanical), `ReviewStatus` (Approved/Pending/Rejected).
- Máximo **3 tags visíveis por livro** (CHECK constraint `CK_BookTags_Position`).

## Regras editoriais (duráveis)

- Tag = eixo transversal de descoberta; categoria = prateleira principal. Não são a mesma coisa.
- Máx 3 tags por livro; 2 é bom quando mais honesto; 1 é aceitável se o livro é monodimensional.
- `Nível` NÃO é tag (é campo separado). `Machine Learning` fica em inglês.
- Tag pode existir e navegar publicamente mesmo com poucos livros.
- Cobertura não é meta: não inflar tags para "fechar 100%".
- Vocabulário fechado: nem usuário nem IA criam tag livre; só curadoria editorial.

## Motor mecânico (`BookTagRuleEngine.cs`)

- Determinístico (regex título+sinopse → vocabulário fechado), sem IA.
- A regra exige que o **título** case (a sinopse só reforça o score). Por isso não acende em romance/filosofia.
- Normalização: `C++`→`cplusplus`, `C#`→`csharp`, `.NET`→`dotnet`, acentos removidos, minúsculas.
- Hook em `BookService.InsertAsync` (best-effort, `try/catch`): todo livro novo (físico ou digital) recebe tags mecânicas com `Source = Mechanical` + `ReviewStatus = Approved`.
- Para ajustar regra: editar `BuildRules()` e os testes `BookTagRuleEngineTests.cs`.

## Endpoints

- `GET /api/Tag` — lista pública (com `totalBooks`).
- `GET /api/Tag/Admin` — lista admin (com aliases). Requer permissão ApproveBook.
- `POST /api/Tag` — cria tag. `PUT /api/Tag/{id}` — atualiza. `DELETE /api/Tag/{id}` — deprecia.
- `GET /api/Tag/Book/{bookId}` — tags de um livro.
- `PUT /api/Tag/Book/{bookId}` body `{TagIds:[...]}` — **substitui** a lista inteira (máx 3).
- `GET /api/Tag/{id}/Books/{page}/{items}` — livros por tag.

## Criar uma tag nova (gotchas)

1. **Checar conflito de alias**: o id novo não pode repetir id nem alias de tag existente (`EnsureTagIsValidAsync` rejeita). Se o termo já é alias de outra tag (ex: `vim` era alias de `editores-de-texto`), remover o alias primeiro e depois criar.
2. Escolher família coerente (ex: `linguagens-plataformas-frameworks`, `dados-ia`, `backend-arquitetura`, `fundamentos-computacao`).
3. Criar via `POST /api/Tag` com `status: "Active"`, `isPublic: true`.
4. Adicionar regra no `BookTagRuleEngine` + teste, para livros futuros nascerem com ela.

## Achar livros para uma tag (backfill manual)

- Buscar via `GET /api/Book/FullSearch/{criteria}/{page}/{items}` (URL-encode do critério).
- **Atenção a falso positivo**: a palavra pode ser homônima (ex: "vim" = verbo *vir* em "Pai, de Onde eu Vim?"; "vim" citado só na sinopse). Conferir título/autor antes de taggear.
- Aplicar com `PUT /api/Tag/Book/{id}`, preservando tags existentes (máx 3).

## Scripts

- `scripts/production/seed_tags_v0.py` — seed inicial do vocabulário.
- `scripts/production/backfill_technical_tags.py` — backfill regex (dry-run por padrão, `--apply`).
- `scripts/production/complete_technical_tags.py` — completa cobertura (cria tags + tagueia).
- `scripts/production/refine_technical_tag_overrides.py` — overrides editoriais explícitos.
- `scripts/production/verify_tags_e2e.py` — verificação ponta a ponta.
- Auth via `sharebook_prod_auth.py` (`.env` na raiz do `sharebook-agent`); API pode dar 503 transitório (retry ~10s).

## Fluxo do importer

Ao publicar um ebook pelo importer (`editor-next` → `plan-set` → `publish-once`), o livro passa por `POST /Book` → `InsertAsync` → recebe tags mecânicas automaticamente (`Source = Mechanical`). Nenhuma chamada extra é necessária.

## Fronteiras

Não guardar aqui: números datados do catálogo (contagens de livros por tag), estado da fila do importer, prioridades do backlog, marcos concluídos. Isso vive em memória episódica ou em `backlog/`.
