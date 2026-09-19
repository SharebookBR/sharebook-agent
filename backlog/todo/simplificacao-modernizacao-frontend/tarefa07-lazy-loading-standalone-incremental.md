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
