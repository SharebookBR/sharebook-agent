# Tarefa 2 — Hydration no SSR

## O que existe hoje

`app.server.module.ts` sobe `ServerModule`, mas **`provideClientHydration()` não existe em nenhum lugar do código** (confirmado por grep na árvore inteira).

## Por que revisar

Sem hydration, o Angular descarta o DOM renderizado no servidor e remonta tudo do zero no cliente (destroy+rebuild). Isso anula boa parte do ganho de ter SSR: flicker visível, custo de CPU maior no cliente — é a funcionalidade headline que o Angular moderno oferece pra SSR, e o app não usa.

## Abordagem

Adicionar `provideClientHydration(withEventReplay())` no bootstrap (`main.ts`/`app.module.ts`, ou o provider equivalente na configuração de app usada hoje). Esforço de código é baixo — é a validação que exige cuidado.

## Benefício esperado

Menos flicker, menos trabalho no cliente, ganho real de performance percebida e Core Web Vitals — relevante pra SEO/conversão numa app pública de doação.

## Risco

Médio, concentrado na validação, não na implementação. Hydration mismatch aparece quando o HTML gerado difere entre server e client: `Math.random()`, `Date.now()`, acesso direto a `window`/`localStorage` fora de guard de plataforma (`isPlatformBrowser`), etc.

## Como validar que nada quebrou

- `curl` comparando o HTML retornado pelo servidor antes/depois da mudança.
- Abrir cada página real no browser e checar o console por warnings de "hydration mismatch" (Angular loga isso explicitamente em dev mode).
- Testar particularmente páginas com dado dinâmico: busca, detalhes de livro, home (tem cache SSR próprio — conferir que hydration não interfere no `X-SSR-Cache MISS/HIT` documentado em `backlog/done/migracao-angular-13-lts.md`).
- Rodar os smoke tests de Playwright existentes (home, 404, register) e considerar adicionar um teste específico de hydration mismatch (checar ausência de warning no console via `page.on('console')`).
