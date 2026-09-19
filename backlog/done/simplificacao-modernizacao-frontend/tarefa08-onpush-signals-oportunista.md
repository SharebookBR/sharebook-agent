# Tarefa 8 — OnPush/Signals oportunista

Diferente das demais tarefas deste épico, **esta não é uma frente própria com data de início** — é uma prática a adotar oportunisticamente.

## O que existe hoje

Todos os 58 componentes rodam com detecção de mudança padrão (zone.js completo, sem `OnPush`). Nenhum usa `signal()`/`computed()`/`input()` em produção — o único uso registrado foi um experimento numa spec de teste durante a investigação do bug NG0100 em `header.component.spec.ts` (ver `backlog/done/migracao-angular-13-lts.md`), que não resolveu o problema e foi descartado.

## Por que não é prioridade isolada

Zone.js completo ainda funciona — não é "prática antiga quebrada", é a maior lacuna entre o app e o que o Angular 22 oferece de ganho de performance real (menos ciclos de detecção, caminho pra zoneless). Mas convertê-la em massa (58 componentes) é o tipo de "modernização por checklist" que o Raffa pediu explicitamente pra evitar — não traz benefício concreto proporcional ao esforço/risco se feita de forma isolada.

## Abordagem

Componente novo, ou componente tocado por outro motivo (bug, feature, uma das outras tarefas deste épico), já nasce ou sai com `input()`/`OnPush` quando fizer sentido. Não abrir uma tarefa dedicada só pra converter os 58 de uma vez.

## Benefício esperado

Real, mas de cauda longa — amortizado ao longo do tempo junto com outro trabalho, não como investimento isolado.

## Risco

Médio-alto se feito em massa (OnPush pode expor bug de mutação que o CD default escondia); baixo se feito componente a componente, junto de um toque já planejado.

## Como validar

Por componente convertido: teste de interação real (não só snapshot), já que `OnPush` pode alterar timing de atualização visual que testes superficiais não capturam.

## Status final — CONCLUÍDA (escopo redefinido: home + PDP) em 2026-09-19

Decisão do Raffa: em vez de deixar 100% oportunista/sem prazo, aplicar `OnPush` de forma deliberada nas duas páginas de maior importância de negócio — home (maior tráfego) e PDP/book details (página de conversão de doação). Commit `00d32e9` (branch `develop`, sharebook-frontend).

Abordagem escolhida: **`ChangeDetectorRef.markForCheck()`** em cada callback assíncrono que muda estado (subscribe HTTP, `afterClosed()` de dialog, `FileReader.onload`), em vez de reescrever os componentes pra Signals. Justificativa: essas duas páginas são as de maior risco de negócio do app inteiro — a via mais segura (markForCheck explícito, zero mudança de template) venceu a mais idiomática (Signals, que exigiria reescrever leituras no template inteiro). Signals continuam oportunistas pros demais 56 componentes, sem prazo, como o texto original desta tarefa já previa.

Validação: interação real via Playwright contra backend local — home renderiza as 3 prateleiras + 9 meetups vindos de chamada assíncrona; PDP logado como Administrator chega a `state: 'ready'` através da cadeia mais funda de subscribes aninhados (`getBook -> getFreightOptions -> getRequested`) e renderiza os botões de ação; clique em "Compartilhar com amigos" abre o modal. Zero erro de JS. Suíte 93/95 e `build:ssr` limpos.
