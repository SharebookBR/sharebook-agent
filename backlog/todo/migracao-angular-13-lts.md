# Migração incremental do Angular (13 → LTS ativa)

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
