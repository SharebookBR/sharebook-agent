# Migração incremental do Angular (13 → LTS ativa)

## Objetivo

Sair do Angular 13 (end-of-life, sem patch de segurança) e pousar numa versão sob LTS ativa, sem salto cego de major — respeitando a Regra de Ouro já registrada em `seguranca-e-vulnerabilidades.md`.

## Baseline real (`sharebook-frontend`, branch `develop`, auditado em 16/09/2026)

- `@angular/core` `~13.3.12`, `@angular/cli` `~13.2.5`.
- `typescript` `~4.5.5`, `zone.js` `~0.12.0`.
- `rxjs` `~6.6.7` **com `rxjs-compat` ainda instalado** — sinal de uso de API estilo RxJS 5 no código.
- `@angular/material` / `@angular/cdk` `^13.3.9` — pré-rewrite MDC.
- `core-js@^2.5.4` — polyfill legado, provável resíduo de suporte a IE11 (já não é alvo do Angular há várias majors).
- Lint em `tslint` (descontinuado desde 2019) + `codelyzer`.
- E2E em `protractor` (sunset oficial em 2022, builder removido do CLI a partir do Angular ~15/16).
- **Sem SSR/Angular Universal no repo** — não há `@nguniversal`, `@angular/ssr` nem `server.ts`. Confirmado por busca no repo; qualquer menção anterior a advisories de `platform-server`/`@nguniversal` no `npm audit` não corresponde a dependência direta atual.
- Sem `.nvmrc` nem `engines` no `package.json` — versão de Node não está fixada em lugar nenhum.
- Builder ainda é `@angular-devkit/build-angular:browser` (webpack clássico), não esbuild/Vite.

### Discrepância encontrada (verificar antes de começar)

O `seguranca-e-vulnerabilidades.md` registra, em 2026-08-31, a remoção de `base64-img` do `sharebook-frontend`. `base64-img` **continua presente** em `package.json` na `develop` atual (`git diff origin/develop -- package.json` não mostra diferença, ou seja, a remoção nunca chegou nesse branch, ou foi revertida). Confirmar com o Raffa se essa fatia foi perdida num merge ou se ficou presa em outro branch antes de assumir o baseline de segurança como válido.

## Alvo recomendado

Angular 22 é a release ativa (jun/2026); Angular 21 e 20 estão em LTS (até 19/05/2027 e 28/11/2026 respectivamente). Dado o tamanho do salto (13 → 22 = 9 majors) e o risco concentrado em Angular Material (rewrite MDC no v15), recomendo:

1. **Primeira parada obrigatória: Angular 20 (LTS)** — já elimina 100% dos advisories presos em Angular 13 citados no `seguranca-e-vulnerabilidades.md` e devolve o projeto a uma posição sob suporte.
2. **Reavaliar depois**: continuar até 21 ou 22 é uma decisão separada, sem urgência de segurança, tomada quando a v20 estiver estável em produção.

## Pré-requisitos (antes do primeiro `ng update`)

1. **Eliminar `rxjs-compat`**: mapear todo uso de API RxJS 5 (`.toPromise()` antigo, operators fora de `.pipe()`, imports de `rxjs/Rx`) e migrar para RxJS 6 puro. `rxjs-compat` não sobrevive a mais de 1–2 majors adiante.
2. **Fixar versão de Node**: criar `.nvmrc` + `engines` no `package.json`. Cada major do Angular eleva o mínimo de Node (13→14: Node 14.15+; a partir do 19: Node 18.19+/20.11+; a partir do 20: Node ≈20.19+/22.12+). Confirmar o mínimo exato no changelog de cada hop antes de subir — não assumir por analogia.
3. **Migrar `tslint` → `eslint`**: rodar `ng add @angular-eslint/schematics` e `ng g @angular-eslint/schematics:convert-tslint-to-eslint` enquanto ainda estamos numa versão onde o schematic de conversão é suportado oficialmente. Adiar isso piora a migração, não facilita.
4. **Decidir o destino do e2e em Protractor**: está morto e o builder some do CLI a partir de ~v15/16. Opções: migrar para Cypress/Playwright ou descontinuar e2e automatizado em favor de unitários + smoke manual. **Decisão do Raffa, não assumir.**
5. **Remover `core-js@2`** e conferir `polyfills.ts` — suporte a IE11 já não é target há várias majors; validar se ainda há import ativo antes de remover.

## Sequência de hops (uma major por vez, `ng update` oficial)

Regra fixa por hop: `ng update @angular/core@N @angular/cli@N` (+ pacotes associados: `@angular/cdk`, `@angular/material`), rodar suíte, buildar todas as configurações usadas (`build-dev`, `build-stg`, `build-prod`), smoke manual das telas críticas, **commit isolado por hop** (permite bisect e rollback sem perder os hops anteriores).

| Hop | Ponto de atenção específico |
|---|---|
| 13 → 14 | TypeScript 4.6/4.7 exigido. Sem breaking grande esperado. |
| 14 → 15 | **Angular Material reescrito sobre MDC** — mudança visual/DOM real nos componentes Material. Exige QA visual manual em todas as telas que usam `@angular/material`, não só teste automatizado. |
| 15 → 16 | Node 16.14+, TypeScript 4.9+. Router ganha guards funcionais (opcional). Builder esbuild vira opção (não obrigatório adotar ainda). |
| 16 → 17 | Node 18.13+, TypeScript 5.2+. Nova sintaxe de control flow (`@if`/`@for`) em developer preview — não migrar templates existentes nesse hop. |
| 17 → 18 | Node 18.19+/20.11+, TypeScript 5.4+. Material 3 experimental. |
| 18 → 19 | TypeScript 5.5+. Standalone vira default nos schematics de novos componentes (não afeta código existente com NgModules). |
| 19 → 20 | TypeScript 5.8+. **Parada recomendada — LTS.** |

(21 e 22 ficam para uma segunda rodada, decisão futura.)

## Riscos concentrados em dependências de terceiros

Auditar compatibilidade antes de cada hop, não só depois de quebrar:
- `ngx-image-cropper`, `ngx-image2dataurl` — libs pequenas, checar se ainda recebem release compatível com a major alvo ou se precisam de substituto.
- `ngx-mask`, `ngx-toastr`, `ng-recaptcha` — mesma checagem.
- `bootstrap@4` convive com Angular Material — não faz parte deste plano trocar, só confirmar que não quebra com o bump.

## Critério de pronto

- Cada hop com build + suíte de testes verdes e commit próprio.
- Chegada ao Angular 20 elimina os advisories de `@angular/*` e `@nguniversal/*` registrados em `seguranca-e-vulnerabilidades.md` (o segundo grupo só se aplicar caso a discrepância do `base64-img` acima revele dependência real de Universal — a auditoria atual não encontrou SSR ativo no repo).
- `.nvmrc`/`engines` fixados, lint em `eslint`, decisão sobre e2e registrada e executada.
- Decisão explícita registrada (com o Raffa) sobre continuar até 21/22 ou estabilizar em 20.
