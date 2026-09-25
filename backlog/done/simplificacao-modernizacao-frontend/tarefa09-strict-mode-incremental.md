# Tarefa 9 — Strict mode incremental

**Fase 3 do épico** — só depois da reorganização de pastas (Tarefa 1) e de reconstruir a rede de testes (Tarefa 5), nunca antes.

## O que existe hoje

`tsconfig.json` tem `strict: false` e `strictNullChecks: false` explícitos, decisão deliberada da migração Angular 19→22: o TypeScript 6.0 (peer dep do Angular 22) expôs código legado que assumia `AbstractControl.get()` nunca retorna null. Refatorar a base inteira pra `strictNullChecks` estava fora de escopo daquela migração. 29 usos de `: any` na árvore hoje.

## Por que revisar

`strict`/`strictNullChecks` capturam uma classe inteira de bug (acesso a `null`/`undefined` não tratado) que hoje só aparece em runtime, se aparecer. É a mesma classe de problema, em espírito, do bug de `.subscribe()` sem `catchError` (Tarefa 3) — erro que o compilador poderia ter pego, mas não pega porque a leniência está ligada.

## Por que é fase 3, não agora

Ligar `strict`/`strictNullChecks` globalmente numa base com 29 `any` e histórico de anos vai gerar uma enxurrada de erros de compilação que ninguém vai revisar com atenção de uma vez — é o tipo de mudança que convida a "corrigir" com `!` (non-null assertion) só pra calar o compilador, o que é pior que não ligar. Só faz sentido depois que:
1. A reorganização de pastas (Tarefa 1) já deu visibilidade de domínio — mais fácil ligar `strict` por pasta/feature do que pro projeto inteiro de uma vez.
2. Existe rede de teste mínima (Tarefa 5) pra confirmar que uma correção de tipo não mudou comportamento.

## Abordagem

Depois que as duas dependências acima estiverem resolvidas: ligar `strictNullChecks` por feature (usando o suporte do TypeScript a strictness por diretório, ou um `tsconfig` incremental), não no projeto inteiro de uma vez. Resolver os `any` restantes caso a caso, tipando de verdade — não com `unknown` só pra sair do `any` sem ganhar nada.

## Benefício esperado

Alto no longo prazo — captura em compile-time uma classe de bug que hoje só aparece em produção ou não aparece nunca (silenciosamente ignorado).

## Risco

Alto se feito de uma vez ou apressado — é a tarefa deste épico com maior chance de gerar correção superficial (`!`, `as any`) que piora a base em vez de melhorar.

## Como validar

Por feature convertida: `tsc --noEmit` limpo sem uso de `!`/`as any` novo introduzido só pra silenciar erro, suíte de teste da feature passando, revisão manual de cada ponto onde o compilador apontou null/undefined não tratado (não assumir que "não pode ser null" sem checar a evidência real do fluxo de dado).

## Status final — CONCLUÍDA em 2026-09-19

Commit `b76eb61` (branch `develop`, sharebook-frontend). **Última tarefa do épico — fecha o lote 3 e o épico inteiro.**

Antes de decidir estratégia, medi o impacto real em vez de supor: `strictNullChecks: true` sozinho expôs **64 erros em 16 arquivos** — bem menos do que o diagnóstico original temia. Como o TypeScript não suporta strictness parcial por pasta dentro de um único `tsconfig`, corrigi todos os 64 nesta sessão (o "por feature" da abordagem original virou "por domínio, na mesma sessão, com commits organizados por área").

`strict: true` completo foi testado à parte e **descartado deliberadamente**: gera 340 erros, 289 deles `strictPropertyInitialization` (campos de componente Angular sem inicializador no construtor — padrão legítimo do framework, não um bug; "corrigir" em massa significaria `!` espalhado por toda parte). Mantido `strict: false`, só `strictNullChecks: true` ligado.

Padrões corrigidos de verdade (confirmado por grep no diff: zero `!`/`as any` novos introduzidos):
- Fallback `catchError(() => of(null as X))` (repetido em ~9 arquivos) → `of<X | null>(null)` tipado corretamente.
- `formGroup.get(name)` do Reactive Forms em `form.component.ts` (28 dos 64 erros, o maior arquivo do domínio book): helper `getRequiredControl()` que lança erro claro se o controle não existir, em vez de assumir silenciosamente.
- `RouteReuseStrategy.retrieve()` tinha assinatura mais estreita que a interface real do Angular (`DetachedRouteHandle` vs. `DetachedRouteHandle | null`) — corrigida com guard clauses.
- Modelos `Address` e `BookToAdminProfile` mentiam sobre nulabilidade real (a própria implementação do serviço/API deixa campos `null`/`undefined`) — corrigidos os modelos, não só os pontos de uso.
- `PasswordValidation.MatchPassword` e `SeoService.generateTags`: resolvidos de forma tipada, sem repetir null-check ad-hoc.

Durante a validação, um fixture de teste (`form.component.spec.ts`) que eu tinha "corrigido" de `null` pra `undefined` quebrou uma asserção real — investiguei, descobri que o modelo `BookToAdminProfile` é que estava errado (campos de API devem aceitar `null`, não só `undefined`), revertido o fixture e corrigido o modelo. Exemplo concreto do próprio risco que esta tarefa avisa: a correção óbvia não é sempre a certa.

Validação: `tsc --noEmit` limpo (app + specs), suíte 93/95 verde, `build:ssr` limpo, e interação real via Playwright no formulário de doação (toggle físico↔digital, que exercita a cadeia inteira de `getRequiredControl` — o ponto de maior risco do refactor) sem nenhum erro de JS.
