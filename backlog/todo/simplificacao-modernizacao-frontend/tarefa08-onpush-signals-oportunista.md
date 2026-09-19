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
