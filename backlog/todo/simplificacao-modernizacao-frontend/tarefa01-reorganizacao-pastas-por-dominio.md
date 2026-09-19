# Tarefa 1 — Reorganização de pastas por domínio

## Status final — CONCLUÍDA em 2026-09-19

Todos os 7 lotes fechados, commitados e pushados em `claude/agents-md-reading-ybnyaq` (sharebook-frontend), na ordem planejada (menor pro maior risco):

| Lote | Commit | Validação |
|---|---|---|
| static-pages | `d573e5b` | tsc + testes + SSR real |
| contact | `65fad22` | idem + removida duplicata morta (`ContactUsComponent` 2x em declarations) |
| category | `99a0db5` | idem + confirmado que crash em `/categorias/:slug` já era pré-existente |
| account | `28ec35a` | idem |
| auth | `7ce9439` | **funcional real** — backend local (.NET 10 + SQLite) + login via Playwright com credencial do seed |
| admin | `8a180e5` | idem, 4 dashboards navegados autenticado, 1 com dado real (Painel de Jobs) |
| book | `6e0c5c8` | idem, mais espalhado do épico — home (21 book-card reais), detalhe de livro real, 4 telas autenticadas de gestão |

Estrutura final: `core/` só com singleton de app inteiro; `shared/` criado pela primeira vez (`book-card`, `book-shelf`); `features/{static-pages,contact,category,account,auth,admin,book}/` com colocation componente+service+model por domínio.

Decisão consistente aplicada em todos os lotes: services/models genuinamente cross-cutting (`UserService`, `AuthenticationService`) ficaram em `core/`; services/models que são "donos conceituais" de um domínio (`CategoryService`, `BookService`, `book.ts`) foram para o respectivo `features/`, mesmo quando consumidos por outras features — cross-import entre features é normal em feature-folder.

Unificação de convenção de nome dos models (PascalCase, sem sufixo `VM` inconsistente) foi **adiada deliberadamente**, não feita ad hoc por lote — fica como decisão própria futura, se for retomada.

Achado incidental corrigido no caminho: bug real de rota no backend (`AmbiguousMatchException` em `CategoryController`) que parecia atual — investigação revelou que já tinha sido corrigido na master do `sharebook-backend` em 23/08/2026; o problema era a branch de trabalho do backend estar divergida da master (resetada por pedido do Raffa).

**Prioridade #1 do épico**, por pedido explícito do Raffa (2026-09-19): "o objetivo é diminuir o custo cognitivo e facilitar a descoberta. Com desapego total ao passado. Com coragem."

## O que existe hoje

Organização por **tipo técnico**, não por **domínio**: `components/` (58 pastas, quase todas no mesmo nível), `core/services/` (19), `core/models/` (43 arquivos soltos), `core/helpers/` (grab-bag: 3 interceptors + `fake-backend.ts` + barrel), `core/utils/`.

Evidência do problema: entender o domínio "book" (doação de livro) exige abrir 4 lugares diferentes que não se referenciam na árvore:
- `core/services/book/book.service.ts`
- `core/models/`: `book.ts`, `bookVM.ts`, `bookVMItem.ts`, `adminBookList.ts`, `adminBookSummary.ts`, `BookToAdminProfile.ts`, `BookDonationStatus.ts`, `BookRequestStatus.ts`, `trackingNumberBookVM.ts`, `facilitatorNotes.ts` — 10 arquivos misturados com os outros 33 do resto do app
- `components/book/*` — 13 componentes (form, list, details, donations, tracking, request(s), donate(-page), main-users, winner-users, donor-modal, crop-image-dialog, freight-incentive-dialog, facilitator-notes)
- `components/book-card/` e `components/book-shelf/` — irmãos soltos de `components/`, fora de `book/`, mas são o mesmo domínio

`core/models/` mistura convenção de nome: PascalCase (`AnonymizeUserVM.ts`) ao lado de lowercase (`book.ts`, `card.ts`, `address.ts`) — impossível prever o nome sem procurar.

## Por que revisar

Isso é exatamente "custo cognitivo alto, descoberta difícil". Ninguém abre a árvore e enxerga "isso é o domínio de livro" — precisa saber de antemão onde cada pedaço mora.

## Abordagem

Reorganizar por **feature folder** (colocation), não por tipo técnico:

```
src/app/
  core/                    # só singleton de app inteiro: guards, interceptors (renomeado de "helpers"), router
  shared/                  # UI reutilizável sem estado de negócio: book-card, book-shelf, input-search, card-meetup, confirmation-dialog, recaptcha
  layout/                  # casca do app: header, footer, bottom-nav, mais-sheet, cookieconsent, dev-mode-banner
  features/
    home/
    book/                  # form, list, details, donations, tracking, request(s), donate(-page), main-users, winner-users, donor-modal, crop-image-dialog, freight-incentive-dialog, facilitator-notes + book.service.ts + models do domínio
    category/
    account/               # account, myaccount, change-password, settings
    auth/                  # login, register, forgot-password, reset-password, parent-aproval, unsubscribe + authentication.service.ts
    admin/                 # importer-dashboard, jobs-dashboard, analytics-dashboard, download-logs-dashboard
    static-pages/           # about, contribute-project, privacy-policy, terms-of-use, data-anonymization-info, not-found(-page)
    contact/
```

Cada feature carrega seus próprios componentes, service(s) e models — `core/models/` deixa de existir como cesto único. Aproveitar a mudança pra unificar a convenção de nome dos models (todos PascalCase por tipo, sem sufixo `VM` inconsistente), já que todo import vai ser tocado de qualquer forma.

**Esta reorganização define a mesma fronteira que a Tarefa 7 (lazy loading/standalone) vai usar depois** — fazer essa primeiro facilita a extração de rotas lazy, não compete com ela.

## Benefício esperado

Descoberta imediata: abrir `features/book/` mostra o domínio inteiro. Também abre caminho pra atacar os componentes gigantes (Tarefa 7/8) — uma vez isolado do ruído dos outros 57 componentes, fica óbvio separar responsabilidades dentro do arquivo.

## Risco

Mecânico, não lógico: o projeto usa import absoluto via `baseUrl` (`src/app/...`), então mover um arquivo quebra referência em **tempo de compilação**, não em produção. `tsc --noEmit`/`ng build` apontam exatamente o que sobrou. Diff grande em número de arquivos ≠ risco lógico alto, desde que seja só move+rename.

## Como validar que nada quebrou

Por domínio movido (não big-bang):
1. `git mv` (preserva histórico) do domínio inteiro.
2. Corrigir imports até `tsc --noEmit` limpo.
3. `npm test` do que foi tocado.
4. `ng build` + `npm run build:ssr` limpos.
5. Smoke test real (curl no SSR local, ou Playwright) da(s) rota(s) do domínio antes de passar pro próximo.

## Ordem de execução sugerida

Do menor pro maior risco: `static-pages` (sem lógica, prova o processo) → `contact` → `category` → `account` → `auth` → `admin` → `book` (mais espalhado e mais arriscado, por último). Cada lote é um commit isolado e revertível — pode pausar entre lotes sem deixar nada quebrado.

Aproveitar o primeiro lote pra remover `fakeBackendProvider`/`fake-backend.ts` (ver Tarefa 4 — código morto, achado de graça durante o diagnóstico).
