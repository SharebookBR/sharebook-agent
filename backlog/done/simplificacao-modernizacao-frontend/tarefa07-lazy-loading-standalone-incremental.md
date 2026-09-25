# Tarefa 7 — Lazy loading + standalone incremental

## O que existe hoje

`AppModule` declara os 58 componentes num só `@NgModule`, bootstrap via `platformBrowserDynamic().bootstrapModule()`. `app-routing.module.ts` (216 linhas) não tem um único `loadChildren` — a rota `/admin`/dashboards carrega no mesmo bundle que a home pública. Zero componentes standalone em produção.

## Por que revisar

Todo visitante da home baixa o código de dashboard admin, importador e analytics junto, mesmo nunca acessando essas áreas. Bundle inicial e TTI maiores que o necessário, numa app pública com SSR onde first paint importa pra SEO/conversão de doação.

## Abordagem

**Depende da Tarefa 1 (reorganização de pastas) estar em andamento ou concluída** — a fronteira de domínio definida lá é a mesma fronteira de rota lazy aqui.

Migração incremental por feature, não big-bang:
1. Bootstrap via `bootstrapApplication` + `provideRouter`.
2. Rotas lazy (`loadComponent`) começando pelas áreas isoladas de baixo tráfego: `admin/` (importer-dashboard, jobs-dashboard, analytics-dashboard, download-logs-dashboard) primeiro — menor risco de regressão visual, menor exposição pública.
3. Componentes convertidos pra standalone conforme entram na rota lazy — não converter os 58 de uma vez.

## Benefício esperado

Bundle inicial menor, code-splitting real, elimina o "God module" — cada feature carrega só o que precisa.

## Risco

Médio-alto se feito de uma vez (58 componentes, DI implícito de módulo pode esconder dependência que só aparece em runtime). Baixo se feito por feature, uma rota por vez, começando pelas de menor tráfego.

## Como validar que nada quebrou

Por rota migrada: build + Playwright smoke test específico da rota, comparação de tamanho de bundle antes/depois (`ng build --stats-json` + `webpack-bundle-analyzer` ou equivalente), confirmação visual manual da área migrada (especialmente dashboards com Angular Material, que já passou por um rewrite MDC na migração anterior).

## Status final — CONCLUÍDA (parcialmente, escopo reduzido) em 2026-09-19

Commit `eeb0287` (branch `develop`, sharebook-frontend). Migradas as 4 rotas de admin (`importer-dashboard`, `jobs-dashboard`, `analytics-dashboard`, `download-logs-dashboard`) pra standalone + `loadComponent`.

**Divergência da abordagem original, decidida em execução:** não foi feita a migração de bootstrap pra `bootstrapApplication` + `provideRouter` (passo 1 do plano original). Não era pré-requisito real — `loadComponent` com componente standalone funciona dentro de uma app ainda bootstrada via `NgModule` desde o Angular 14+. Reduz drasticamente o risco (não mexe no bootstrap da app inteira) sem abrir mão do benefício de code-splitting. A migração de bootstrap fica como possível trabalho futuro, sem urgência — não há benefício adicional claro em fazê-la agora que o code-splitting já foi alcançado.

Resultado: bundle inicial do browser (produção) caiu de 3.19 MB pra 2.87 MB. Os 4 dashboards viraram chunks lazy carregados só ao navegar pra rota (`chart.js`, usado só em analytics/download-logs, saiu do bundle inicial).

Validação: `build:ssr` limpo, suíte 93/95 verde, smoke test real via Playwright contra backend local logado como Administrator — as 4 rotas renderizam sem erro de JS. `jobs` e `importer` com dados reais; `analytics` e `download-logs` mostram a tela e o estado de erro esperado (esse backend local de teste não tem os endpoints de GA4/Search Console — não é regressão da migração).

**Restam os outros 54 componentes não convertidos** — decisão consciente de escopo, não pendência esquecida: a abordagem incremental do próprio plano diz pra converter só quando entra numa rota lazy, e as próximas rotas de baixo risco já foram esgotadas nesta rodada. Próxima onda de lazy loading (se houver) é trabalho novo, não continuação desta tarefa.
