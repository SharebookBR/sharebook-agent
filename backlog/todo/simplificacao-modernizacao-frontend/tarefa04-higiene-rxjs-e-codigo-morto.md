# Tarefa 4 — Higiene: versão do rxjs + código morto

Duas correções triviais, sem debate, encontradas durante o diagnóstico.

## Versão do rxjs desalinhada

`package.json` declara `"rxjs": "~6.6.7"`, mas o `package-lock.json` resolve `7.8.2` de fato — alguma dependência transitiva força a resolução real pra cima. A versão declarada é uma mentira que só não quebrou porque ninguém rodou `npm install` limpo num ambiente onde a resolução transitiva difere.

**Correção:** ajustar `package.json` pra `"rxjs": "^7.8.0"` (ou o que refletir a realidade), rodar `npm install` e confirmar que o lockfile não muda de forma inesperada.

## `fakeBackendProvider` morto

`app.module.ts` importa `fakeBackendProvider` de `core/helpers`, mas **nunca aparece no array de `providers`** — importado, nunca usado.

**Correção:** remover o import em `app.module.ts` e avaliar se `core/helpers/fake-backend.ts` tem algum outro uso real na árvore (specs, outro módulo). Se não tiver, remover o arquivo inteiro.

## Benefício esperado

Higiene — elimina uma fonte de confusão futura (alguém pode assumir que o fake backend está ativo) e uma declaração de dependência que mente sobre a versão real em uso.

## Risco

Baixo em ambos. A correção do rxjs é só metadado (a versão resolvida não muda). A remoção do `fakeBackendProvider` remove código nunca executado em produção — não pode ter efeito colateral porque não está no grafo de providers.

## Como validar que nada quebrou

`npm install` limpo + `tsc --noEmit` + `ng build` + `build:ssr` + suíte de testes completa. Se `fake-backend.ts` for removido, grep final confirmando zero referência restante antes de apagar o arquivo.

## Status final — CONCLUÍDA em 2026-09-19

Commit `a23acf4` (branch `develop`, sharebook-frontend).

- `rxjs` ajustado para `^7.8.0`; `npm install` dedupou 5 cópias aninhadas do rxjs puxadas por `@angular-devkit/*` (lockfile líquido: -170 linhas). Resolução real continua `7.8.2`, como esperado.
- `fakeBackendProvider` removido de `app.module.ts`; `fake-backend.ts` apagado (grep confirmou zero uso restante); export removido de `core/helpers/index.ts`.
- Bônus não previsto: a dedup do rxjs expôs um erro de tipo real em `details.component.ts` (`myUser = x || {}` não era assignable a `UserInfo`) que antes passava batido pela resolução de tipos duplicada. Corrigido para `new UserInfo()`.
- Validação: `tsc --noEmit` limpo, suíte Karma 44/44 (42 executados + 2 skip, mesmo baseline de antes), `build:ssr` limpo.
