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
