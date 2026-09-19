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
