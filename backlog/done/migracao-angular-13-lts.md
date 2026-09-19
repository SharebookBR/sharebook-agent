# Migração incremental do Angular (13 → LTS ativa)

## Status final — CONCLUÍDO em 2026-09-18

Migração foi além do alvo original (Angular 20 LTS): chegou a **Angular 22** por decisão explícita do Raffa ("não se apegue a dependências velhas... quero um upgrade de verdade e corajoso"), depois que os hops 13→16 (registrados abaixo) destravaram o caminho. Hops 17→22 resolveram cada trava de peer dependency pela causa raiz em vez de `--force`: `ng-recaptcha` removido (substituído por integração própria com o script do Google), `tslint`→`eslint` (schematic oficial de conversão já descontinuado, config escrita manual), Node 24 LTS via `nvm`/`.nvmrc`. `@nguniversal` migrado para `@angular/ssr` conforme previsto no hop 16→17.

Todos os pré-requisitos listados abaixo foram cumpridos: `rxjs-compat` eliminado, `.nvmrc`/`engines` fixados, lint em `eslint`, Protractor descontinuado em favor de Playwright (decisão do Raffa), `core-js@2` removido.

Um bug de produção real foi descoberto e corrigido no caminho: a partir do Angular 21, `.subscribe()` sem `catchError` em chamada HTTP deixa de ser engolido pelo `ErrorHandler` global e derruba o processo Node inteiro no SSR. Corrigido nos componentes globais (`home`, `footer`); ~16 componentes com o mesmo padrão ficaram como open loop — hoje endereçado como tarefa própria em `simplificacao-modernizacao-frontend/`.

Detalhe completo hop a hop, evidências e fricções: memórias `2026-09-18-migracao-angular-19-22-e-vulnerabilidades.md` e `2026-09-18-promocao-angular-22-dev-e-prod-habitat3.md`.

## Objetivo

Sair do Angular 13 (end-of-life, sem patch de segurança) e pousar numa versão sob LTS ativa, sem salto cego de major — respeitando a Regra de Ouro já registrada em `seguranca-e-vulnerabilidades.md`.

## Correção de baseline — 2026-09-17

A primeira versão deste plano (16/09) foi auditada em cima da branch `develop` do `sharebook-frontend`, que estava **meses desatualizada em relação ao `master`** (o Raffa confirmou não usar `develop` há tempos). O `master` real trouxe, entre outras coisas, **SSR com Angular Universal ativo de verdade** — algo que a versão anterior deste documento afirmava não existir. Baseline abaixo já corrigida, auditada depois do merge de `origin/master` para a branch de trabalho.

Isso também resolve a "discrepância" registrada na versão anterior: `base64-img` já estava removido no `master` desde 31/08; só não tinha chegado na `develop`. O baseline de segurança do `seguranca-e-vulnerabilidades.md` está correto — era a `develop` que estava errada, não o registro.

## Baseline real (`sharebook-frontend`, branch `master`, auditado em 17/09/2026)

- `@angular/core` `~13.3.12`, `@angular/cli` `^13.2.5`.
- `typescript` `~4.5.5`, `zone.js` `~0.12.0`.
- `rxjs` `~6.6.7` **com `rxjs-compat` ainda instalado** — sinal de uso de API estilo RxJS 5 no código.
- `@angular/material` / `@angular/cdk` `^13.3.9` — pré-rewrite MDC.
- **SSR real e ativo**: `@angular/platform-server`, `@nguniversal/builders`, `@nguniversal/express-engine` (`^13.1.1`), `server.ts`, `app.server.module.ts`, `main.server.ts`, `tsconfig.server.json`. Scripts `build:ssr`, `dev:ssr`, `serve:ssr`, `prerender` todos ativos e usados — o app roda com SSR em produção, não é resíduo.
- `core-js@^2.5.4` — polyfill legado, provável resíduo de suporte a IE11.
- Lint em `tslint` (descontinuado desde 2019) + `codelyzer`.
- E2E em `protractor` (sunset oficial em 2022, builder removido do CLI a partir do Angular ~15/16).
- Dependências de terceiro adicionais não vistas na auditoria anterior: `chart.js@^4.5.1`, `easymde@^2.21.0` (editor markdown, puxa `codemirror`/`codemirror-spell-checker` via CommonJS — já gera warning de bailout de otimização no build).
- Sem `.nvmrc` nem `engines` no `package.json` — versão de Node não está fixada em lugar nenhum.
- Builder ainda é `@angular-devkit/build-angular:browser` (webpack clássico), não esbuild/Vite.

### Validação da baseline (17/09/2026, pós-merge `origin/master`)

- `npm ci`: instalou limpo (1345 pacotes).
- `npm test -- --watch=false`: `44 SUCCESS`.
- `npm run build:ssr`: browser + servidor buildaram sem erro; só warnings pré-existentes (budget CSS em `app.component`, `home.component`, `importer-dashboard.component`; CommonJS bailout do `easymde`/`codemirror`).

## Progresso — 2026-09-17

Hops 13→14→15→16 concluídos e validados localmente (branch `claude/angular-lts-migration`, `sharebook-frontend`), commits `90d478e`, `b2ae442`, `a5df5cd`, `392af3a`, `ebeedad`, `3eba54f`. **Push para o remoto ainda bloqueado** — Claude Code on the web não tem acesso de escrita ao GitHub nesta sessão (nem por App nem por token pessoal, é bloqueio de rede da plataforma, não de credencial); commits ficam locais até resolução externa (admin da org libera o GitHub App, ou o Raffa puxa os commits e dá push de outro habitat).

Achados por hop:
- **13→14**: `ng update` em fatias (core+cli+nguniversal juntos primeiro, material+cdk depois — juntar tudo num comando só confundiu a resolução de peer deps e tentou pular pra Angular 15). Migração automática de Typed Forms trocou `FormBuilder`/`FormControl`/`FormGroup` por `Untyped*` em 15 arquivos — opção conservadora, sem forms tipados forçados.
- **14→15**: `ng-recaptcha` precisou subir de 9 para 11 (trava peer dep em `@angular/core ^13`, não estendia até 15; a lib segue a major do Angular 1:1). O rewrite MDC do Material **não quebrou nada visualmente** — o schematic escolheu o caminho `Legacy*` (`MatLegacyDialogModule`, `mat.legacy-core()`), preservando DOM/CSS pré-MDC; confirmado via classes `mat-*` renderizadas na Home (não `mdc-*`). O próprio schematic tem um bug: corrompeu um import em `donations.component.ts` (`MMatLegacyDialog`, `@@angular/...`, string sem fechar) — corrigido manualmente, sem outras ocorrências no repo. `@import '~bootstrap/scss/bootstrap'` (sintaxe tilde) virou erro duro nesta versão, trocado para import sem tilde.
- **15→16**: `ng-recaptcha` 11→12 (mesmo padrão 1:1). **`BrowserTransferStateModule` foi removido de `@angular/platform-browser`** (TransferState agora é provido automaticamente) — quebrava o build. Corrigido em `app.module.ts` (produção) e no spec do `FormComponent`. `TransferStateInterceptor` continua funcionando sem erro de DI.
- **Cache da Home**: validado hop a hop (MISS→HIT, corpo idêntico, coalescing) em todos os 3 hops. `server.ts` e a camada de cache nunca foram tocados pelas migrações automáticas — risco antecipado no plano original não se concretizou até aqui.
- **Limitação de validação**: não foi possível confirmar o payload real de `TransferState` fim a fim porque toda chamada à API de produção retorna 403 neste sandbox (bloqueio de rede da plataforma, documentado à parte). Isso já era assim na baseline pré-migração — não é regressão, mas significa que a hidratação real com dados nunca foi exercitada de fato nesta sessão, só a mecânica de cache/render.

Pendências antes do próximo hop (17): decidir o que fazer com o Protractor (segue não tocado), fixar `.nvmrc`/`engines`, migrar `tslint`→`eslint`, remover `core-js@2`, eliminar `rxjs-compat` — nenhum desses bloqueou os hops 1-3, mas ficam mais urgentes a partir do hop 16→17 (onde `@nguniversal` precisa virar `@angular/ssr`).

### Push e impacto em segurança — 2026-09-17

Os 3 repos foram pushados com sucesso depois que o Raffa instalou o Claude GitHub App na org (`https://github.com/apps/claude/installations/select_target` — reconectar a conta pessoal em claude.ai/customize/connectors não bastou, é um passo diferente). Branch `claude/angular-lts-migration` em `sharebook-frontend`, `sharebook-agent` e `sharebook-backend`.

Rodei `npm audit --omit=dev` antes e depois: **105 → 31** vulnerabilidades de produção só com o salto 13→16 do Angular (3 críticas→2, 58 altas→14, 36 moderadas→8, 8 baixas→7 — números do branch padrão antigo reportados pelo próprio GitHub no push). Depois, `npm audit fix` (sem `--force`) resolveu mais 9 dentro dos ranges semver já existentes no `package.json` (`engine.io`, `form-data`, `immutable`, `picomatch`, `socket.io-parser`) — **31 → 22**, sem nenhum bump de major manual. Commit `b40ce7e`.

Das 22 restantes: a maioria está presa em `@angular/*` (fix real é saltar pra v21, fora do hop atual) ou em `@nguniversal/*` — incluindo as 2 críticas — cujo fix real não é patch, é a migração pra `@angular/ssr` já prevista no hop 16→17.

## Alvo recomendado

Angular 22 é a release ativa (jun/2026); Angular 21 e 20 estão em LTS (até 19/05/2027 e 28/11/2026 respectivamente). Dado o tamanho do salto (13 → 22 = 9 majors), o risco concentrado em Angular Material (rewrite MDC no v15) **e agora o SSR real a carregar em cada hop**, recomendo:

1. **Primeira parada obrigatória: Angular 20 (LTS)** — já elimina 100% dos advisories presos em Angular 13/Universal citados no `seguranca-e-vulnerabilidades.md` e devolve o projeto a uma posição sob suporte.
2. **Reavaliar depois**: continuar até 21 ou 22 é uma decisão separada, sem urgência de segurança, tomada quando a v20 estiver estável em produção.

## Pré-requisitos (antes do primeiro `ng update`)

1. **Eliminar `rxjs-compat`**: mapear todo uso de API RxJS 5 (`.toPromise()` antigo, operators fora de `.pipe()`, imports de `rxjs/Rx`) e migrar para RxJS 6 puro. `rxjs-compat` não sobrevive a mais de 1–2 majors adiante.
2. **Fixar versão de Node**: criar `.nvmrc` + `engines` no `package.json`. Cada major do Angular eleva o mínimo de Node (13→14: Node 14.15+; a partir do 19: Node 18.19+/20.11+; a partir do 20: Node ≈20.19+/22.12+). Confirmar o mínimo exato no changelog de cada hop antes de subir — não assumir por analogia.
3. **Migrar `tslint` → `eslint`**: rodar `ng add @angular-eslint/schematics` e `ng g @angular-eslint/schematics:convert-tslint-to-eslint` enquanto ainda estamos numa versão onde o schematic de conversão é suportado oficialmente. Adiar isso piora a migração, não facilita.
4. **Decidir o destino do e2e em Protractor**: está morto e o builder some do CLI a partir de ~v15/16. Opções: migrar para Cypress/Playwright ou descontinuar e2e automatizado em favor de unitários + smoke manual. **Decisão do Raffa, não assumir.**
5. **Remover `core-js@2`** e conferir `polyfills.ts` — suporte a IE11 já não é target há várias majors; validar se ainda há import ativo antes de remover.
6. **Validar `build:ssr` a cada hop, não só o build browser**: com SSR real em produção, um hop que só valida `ng build` (browser) e ignora `ng run angular:server`/`angular:prerender` pode dar falso verde. Todo hop deste plano precisa rodar `npm run build:ssr` completo.

## Sequência de hops (uma major por vez, `ng update` oficial)

Regra fixa por hop: `ng update @angular/core@N @angular/cli@N` (+ pacotes associados: `@angular/cdk`, `@angular/material`, `@angular/platform-server`), rodar suíte, `npm run build:ssr` (não só browser), smoke manual das telas críticas, **commit isolado por hop** (permite bisect e rollback sem perder os hops anteriores).

| Hop | Ponto de atenção específico |
|---|---|
| 13 → 14 | TypeScript 4.6/4.7 exigido. Sem breaking grande esperado. |
| 14 → 15 | **Angular Material reescrito sobre MDC** — mudança visual/DOM real nos componentes Material. Exige QA visual manual em todas as telas que usam `@angular/material`, não só teste automatizado. |
| 15 → 16 | Node 16.14+, TypeScript 4.9+. Router ganha guards funcionais (opcional). Builder esbuild vira opção (não obrigatório adotar ainda). |
| 16 → 17 | Node 18.13+, TypeScript 5.2+. **`@nguniversal/*` é unificado em `@angular/ssr`** a partir daqui — rodar o schematic oficial de migração (`ng add @angular/ssr`) em vez de manter os pacotes `@nguniversal` soltos; validar que `server.ts`/`app.server.module.ts` continuam funcionando após a migração do schematic. Nova sintaxe de control flow (`@if`/`@for`) em developer preview — não migrar templates existentes nesse hop. |
| 17 → 18 | Node 18.19+/20.11+, TypeScript 5.4+. Material 3 experimental. |
| 18 → 19 | TypeScript 5.5+. Standalone vira default nos schematics de novos componentes (não afeta código existente com NgModules). |
| 19 → 20 | TypeScript 5.8+. **Parada recomendada — LTS.** |

(21 e 22 ficam para uma segunda rodada, decisão futura.)

## Riscos concentrados em dependências de terceiros

Auditar compatibilidade antes de cada hop, não só depois de quebrar:
- `ngx-image-cropper`, `ngx-image2dataurl` — libs pequenas, checar se ainda recebem release compatível com a major alvo ou se precisam de substituto.
- `ngx-mask`, `ngx-toastr`, `ng-recaptcha` — mesma checagem.
- `easymde` — depende de `codemirror`/`codemirror-spell-checker` via CommonJS; já causa bailout de otimização hoje. Confirmar que continua funcionando em SSR conforme o Angular evolui a forma de lidar com dependências CommonJS (fica mais rígido a partir do v17/18).
- `chart.js@4` — biblioteca ativa, risco baixo, só confirmar compatibilidade de peer deps a cada hop.
- `bootstrap@4` convive com Angular Material — não faz parte deste plano trocar, só confirmar que não quebra com o bump.

## Critério de pronto

- Cada hop com `npm test` + `npm run build:ssr` verdes e commit próprio.
- Chegada ao Angular 20 elimina os advisories de `@angular/*` e `@angular/ssr`/`@nguniversal/*` registrados em `seguranca-e-vulnerabilidades.md`.
- `.nvmrc`/`engines` fixados, lint em `eslint`, decisão sobre e2e registrada e executada, `@nguniversal` migrado para `@angular/ssr`.
- Decisão explícita registrada (com o Raffa) sobre continuar até 21/22 ou estabilizar em 20.
