# Épico — Simplificação e modernização do código (sharebook-backend)

## Estado

- **Status:** não iniciado. Ainda na fase de diagnóstico — nenhuma refatoração começou.
- **Prioridade:** logo depois de [Simplificação e modernização do código (frontend)](../simplificacao-modernizacao-frontend/index.md), como continuação natural da mesma frente de redução de custo cognitivo, agora do lado do backend.
- **Valor:** alto — mesmo racional do épico do frontend: reduzir custo cognitivo de manutenção e destravar features futuras com menos atrito.
- **Origem:** pedido direto do Raffa em 2026-09-19. O `sharebook-backend` carrega muitos anos de história (.NET, camadas, patterns) que nunca foram revisados com a lente de "isso ainda paga o próprio custo cognitivo?".

## Objetivo

Igual ao do frontend, adaptado para o backend: o objetivo **não é** atualizar tecnologia ou aplicar patterns modernos por si só. A prioridade é **reduzir custo cognitivo e tornar o backend humano-friendly e IA-friendly** — fácil de descobrir, navegar, entender e modificar, tanto por um dev novo quanto por um agente de IA com contexto limitado.

Pergunta central a repetir durante todo o diagnóstico:

> Se estivéssemos construindo este backend hoje, conhecendo o domínio do Sharebook como conhecemos agora, ele teria esta forma?

Sem apego ao passado (pastas, layers, abstrações, interfaces, services, repositories, helpers, DTOs, patterns não sobrevivem só porque já existem e funcionam), mas **sem perder funcionalidade**. Não é troca de arquitetura antiga por arquitetura sofisticada nova — é entregar uma arquitetura que precise de **menos explicação**, não uma mais bonita.

### IA-friendly como requisito arquitetural

Um agente deveria conseguir entrar no repositório e descobrir rapidamente: onde mora uma regra de negócio, onde começa um caso de uso, quais arquivos participam dele, onde estão os contratos de entrada/saída, onde ocorre persistência, onde estão as integrações externas, quais são as fronteiras entre domínios, quais dependências uma mudança pode afetar, e onde criar código novo para uma funcionalidade.

Pergunta a fazer durante o diagnóstico: **quanto contexto um agente precisa carregar para alterar com segurança uma regra de negócio?** O objetivo é reduzir esse custo — sem criar arquivos, comentários ou documentação só para "explicar" o código a uma IA. A melhor documentação arquitetural é uma estrutura óbvia por si mesma.

## Não partir de arquitetura pronta

Não assumir de antemão que a solução é Clean Architecture, Hexagonal, Vertical Slice, DDD, CQRS, MediatR, Repository Pattern, Unit of Work ou qualquer outro pattern. São ferramentas, não objetivos. Se algo disso já existe no backend hoje, questionar se está pagando o próprio custo cognitivo. Se alguma dessas ideias simplificar concretamente o Sharebook, propor; se aumentar arquivos/indireções/conceitos sem benefício proporcional, não propor. Também não copiar automaticamente a organização adotada no frontend — o backend deve encontrar suas próprias fronteiras naturais.

## Primeira entrega: diagnóstico, não implementação

Igual ao combinado com o Raffa: **nenhuma refatoração começa antes do diagnóstico**. A Tarefa 1 é a única tarefa aberta deste épico por enquanto — ela produz o diagnóstico completo (mapa da arquitetura, fontes de custo cognitivo, análise IA-friendly, o que eliminar/unir/dividir/mover/renomear, arquitetura recomendada, comparação antes/depois em fluxos reais, plano incremental de migração). As tarefas de execução (2, 3, 4...) só existem depois que o diagnóstico está pronto e revisado pelo Raffa — igual ao frontend, onde o diagnóstico completo (números concretos da auditoria de código) veio antes de fatiar as tarefas 1-9.

## Princípios (herdados do épico do frontend, válidos aqui também)

- Modernização incremental e verificável, não reescrita. Preservar comportamento antes de melhorar implementação.
- Nenhuma tarefa deste épico muda comportamento visível do usuário ou contrato de API sem que isso vire decisão de produto à parte.
- Cada tarefa de execução (quando existirem) termina com build limpo, suíte de teste verde e commit isolado — nunca lote misturado de tarefas diferentes.
- Nada de "modernização por checklist": se um padrão atual já é a solução mais simples, ele fica como está.

## Fora de escopo agora

- Reescrever o backend do zero ou trocar de framework/tecnologia de base.
- Mudar comportamento de negócio, UX visível ou contrato de API.
- Adotar arquitetura sofisticada só por ser mais moderna — a métrica de sucesso é custo cognitivo, não quantidade de patterns aplicados.

## Tarefas

| # | Tarefa | Benefício | Risco | Esforço | Status |
|---|---|---|---|---|---|
| 1 | [Diagnóstico de arquitetura e custo cognitivo](tarefa01-diagnostico.md) | Alto — base de evidência para todo o resto do épico | Baixo (é investigação, não muda código) | Médio | Pendente |
