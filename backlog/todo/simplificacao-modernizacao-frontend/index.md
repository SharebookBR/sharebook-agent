# Épico — Simplificação e modernização do código (sharebook-frontend)

## Estado

- **Status:** planejado, diagnóstico concluído, nenhuma tarefa iniciada
- **Prioridade:** logo depois de "Dependências e Segurança" (concluído em 2026-09-18, ver `backlog/done/seguranca-e-vulnerabilidades.md`)
- **Valor:** alto — reduz custo cognitivo de manutenção e destrava as próximas features com menos atrito
- **Origem:** o `sharebook-frontend` acabou de migrar de Angular 13 para 22 (ver `backlog/done/migracao-angular-13-lts.md`), mas a migração deliberadamente não tocou estrutura, organização nem padrões — só o motor. Esta é a fase de modernizar a carroceria.
- **Diagnóstico completo:** feito em sessão de 2026-09-19 (claude-code-web), com leitura real do código na branch `master` pós-migração (HEAD `d234bf6`). Números abaixo vêm dessa auditoria, não de estimativa.

## Objetivo

Tornar o código mais simples, mais fácil de entender, mais fácil de manter, mais idiomático pra Angular 22, menos dependente de padrão legado e melhor organizado — **sem perder funcionalidade**.

Regra do Raffa, textual: **"sem apego ao passado, mas sem perder funcionalidades"**. Não preservar abstração/estrutura só porque já existe; não fazer mudança cosmética sem benefício concreto de simplicidade, clareza, manutenção, segurança ou arquitetura.

Prioridade #1 explícita do Raffa (2026-09-19): **simplificação, refactoring e nova organização de pastas/arquivos** — o objetivo é diminuir custo cognitivo e facilitar descoberta, com desapego total ao passado e coragem. As demais tarefas (hydration, RxJS, DI, testes) são reais, mas a reorganização estrutural vem primeiro porque define a fronteira física que todo o resto (lazy loading, standalone, extração de componentes gigantes) vai usar depois.

## Diagnóstico — números que sustentam as tarefas

- 58 componentes, 19 services, `AppModule` único com todos os 58 declarados nele — zero lazy loading (`grep loadChildren` não retorna nada).
- Zero componentes standalone, zero `signal()`/`computed()`/`input()` em código de produção (só aparece em uma spec), zero `inject()` fora de teste, zero `ChangeDetectionStrategy.OnPush`.
- `provideClientHydration()` **não existe em lugar nenhum** — SSR roda sem hydration, o Angular descarta e remonta o DOM inteiro no cliente.
- `package.json` declara `rxjs: ~6.6.7`, mas o `package-lock.json` resolve `7.8.2` de fato (versão declarada mentindo).
- 118 `.subscribe()` em 41 arquivos, nenhum usa `takeUntilDestroyed()`. ~16 componentes ainda têm subscribe HTTP sem `catchError` — mesma classe de bug que já derrubou o processo Node em produção (Angular 21+, ver `backlog/done/migracao-angular-13-lts.md`), documentado como open loop herdado da migração.
- 4 interceptors e 2 guards são class-based (`HTTP_INTERCEPTORS` multi-provider + `withInterceptorsFromDi()`), não funcionais.
- Apenas 10/58 componentes (17%) e 2/19 services têm spec. `authentication.service.ts`, `book.service.ts` e `user.service.ts` — os mais centrais — **não têm nenhum teste**.
- `core/models/` tem 43 arquivos soltos, sem agrupamento por domínio, convenção de nome mista (`AnonymizeUserVM.ts` vs `book.ts`). O domínio "book" sozinho está espalhado em 4 lugares diferentes da árvore: `core/services/book/`, 10 arquivos de `core/models/`, `components/book/*` (13 componentes) e `components/book-card/`+`components/book-shelf/` como irmãos soltos.
- Componentes gigantes (linhas): `importer-dashboard.component.ts` (770), `book/form/form.component.ts` (673), `book/list/list.component.ts` (512), `book/details/details.component.ts` (498), `book/donations/donations.component.ts` (480), `analytics-dashboard.component.ts` (474).
- `fakeBackendProvider` é importado em `app.module.ts` mas nunca aparece no array de `providers` — código morto encontrado durante o diagnóstico.
- `tsconfig.json` tem `strict: false` e `strictNullChecks: false` explícitos, herdados deliberadamente da migração (TypeScript 6.0 expôs código legado que assumia `AbstractControl.get()` nunca null). 29 usos de `: any`.

## Tarefas

| # | Tarefa | Benefício | Risco | Esforço | Status |
|---|---|---|---|---|---|
| 1 | [Reorganização de pastas por domínio](tarefa01-reorganizacao-pastas-por-dominio.md) | Alto — resolve o problema #1 apontado pelo Raffa: custo cognitivo e descoberta | Mecânico (detectável 100% por `tsc`), não lógico | Alto (toca quase todo import), mas fatiável por domínio | **Pendente — começar por aqui** |
| 2 | [Hydration no SSR](tarefa02-hydration-ssr.md) | Alto — elimina flicker e trabalho duplicado no cliente | Médio na validação (hydration mismatch) | Baixo | Pendente |
| 3 | [Fechar subscribes HTTP sem catchError](tarefa03-subscribes-sem-catcherror.md) | Alto — já causou incidente real de produção | Baixo | Baixo-médio | Pendente |
| 4 | [Higiene: versão do rxjs + código morto](tarefa04-higiene-rxjs-e-codigo-morto.md) | Baixo, mas grátis | Baixo | Trivial | Pendente |
| 5 | [Specs de caracterização dos services críticos](tarefa05-specs-caracterizacao-services-criticos.md) | Alto — habilita com segurança tudo que vem depois | Baixo | Médio | **Pendente — antes de mexer nos 3 services sem teste** |
| 6 | [Interceptors e guards funcionais](tarefa06-interceptors-guards-funcionais.md) | Médio — idiomático, menos boilerplate | Baixo | Médio | Pendente |
| 7 | [Lazy loading + standalone incremental](tarefa07-lazy-loading-standalone-incremental.md) | Alto — bundle inicial, code-splitting real | Médio-alto se em massa, baixo por feature | Alto | Pendente |
| 8 | [OnPush/Signals oportunista](tarefa08-onpush-signals-oportunista.md) | Médio, cauda longa | Médio | Contínuo, não é frente própria | Sem prazo — só ao tocar componente por outro motivo |
| 9 | [Strict mode incremental](tarefa09-strict-mode-incremental.md) | Alto, longo prazo | Alto | Alto | Fase 3 — só depois da reorganização e da rede de testes |

## Princípios

- Modernização incremental e verificável, não reescrita. Preservar comportamento antes de melhorar implementação.
- Usar os testes existentes como rede de segurança; onde não existir rede (tarefa 5), construir antes de mexer em código de risco.
- Nenhuma tarefa aqui muda comportamento visível do usuário — são todas de estrutura, organização ou tipagem interna. Se uma tarefa exigir mudança de comportamento, ela sai deste épico e vira decisão de produto à parte.
- Reorganização de pasta é mecânica (move + ajuste de import), não reescrita de lógica — `tsc --noEmit` limpo prova que nada ficou órfão. É o tipo de mudança onde "diff grande em número de arquivos" não significa "risco lógico alto".
- Cada tarefa termina com build (`ng build` + `build:ssr`) limpo, suíte de teste verde e commit isolado — nunca lote misturado de tarefas diferentes.

## Fora de escopo agora

- Reescrever o app do zero ou trocar de framework.
- "Modernização por checklist" — se um padrão atual já é a solução mais simples, ele fica como está (ex.: não converter os 58 componentes pra Signals de uma vez só por ser "mais moderno").
- Mudar comportamento de negócio, UX visível ou contrato de API.
- As 4 vulnerabilidades moderadas remanescentes de dev-tooling sem fix disponível (decisão já tomada em `backlog/done/seguranca-e-vulnerabilidades.md`: deixar pra depois).
