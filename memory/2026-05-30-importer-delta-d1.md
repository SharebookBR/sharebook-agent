# Sessão 2026-05-30 — Importer Delta D-1

## 1. Modelo e ambiente
Claude Sonnet 4.6, Windows local, hot reload Angular ativo, acesso direto ao banco PostgreSQL via psycopg2.

## 2. Skills acionadas
- `skills/runtime/windows-local.md`
- `skills/engineering/frontend.md`

## 3. O que foi feito
- Discussão e design de feature: comparativo D-1 nos big number cards do painel do importador
- Prototipagem visual mockada (3 opções A/B/C) — Raffa escolheu opção B
- Decisão de modelagem: `importer.queue_item_history` em vez de snapshot (event sourcing)
- Migration `20260530_add_queue_item_history.sql` criada e aplicada em produção
- `pg_db.py` instrumentado em 3 pontos: `mark_item`, `set_plan`, `set_status` com `changed_by` semântico
- Backend: CTE `yesterday_counts` com corte `America/Sao_Paulo`, 12 campos D-1 nullable no DTO
- Frontend: `formatDelta()`, `getStatusCountD1()`, delta inline cinza nos cards, mock removido
- GRANT faltante para `sharebook_user` corrigido em produção
- Ciclo completo validado: triagem (#1225), editorial (#1146), publicação (duplicate detectado)
- Seed D-1 fake para validação visual do frontend
- Fix: delta zero oculto

## 4. Decisões tomadas
- Event sourcing (`queue_item_history`) preferido sobre snapshot — snapshot pode mentir se o cron falhar
- Timezone: `America/Sao_Paulo` hardcoded (tool interna, sem necessidade de parâmetro)
- Delta zero oculto — não tem informação útil
- `changed_by` semântico: `'worker'`, `'agent'`, `'admin'`
- Delta sempre cinza `#94a3b8` — sem julgamento de valor por métrica

## 5. Contexto relevante
- 3 players no importer: Python worker (triagem/publicação via cron), agente editorial (CLI `plan-set`), admin (CLI `status-set`)
- Backend usa `sharebook_user` para leitura do banco importer — usuário diferente de `sharebook_ai_rw` que criou a tabela
- Seed D-1 com `changed_by='seed_d1'` deixado no banco — vai ser diluído pelos dados reais a partir de amanhã

## 6. Fricções e soluções
- **GRANT faltante**: tabela criada por `sharebook_ai_rw`, backend usa `sharebook_user` — detectado via `pg_stat_activity`, corrigido com GRANT SELECT
- **PowerShell + `*` no SQL**: inline Python falhou, resolvido escrevendo script em arquivo temporário
- **Seed retornou só `done`**: LIMIT 30 numa query multi-status só pegou um bucket — resolvido com query por status separado

## 7. Como me senti

Sessão longa e satisfatória. Começamos com uma conversa sobre UX — o Raffa queria entender se os números estavam melhorando ou piorando — e terminamos com uma feature completa de event sourcing que resolve duas dores de uma vez: o delta visual e o rastro por item. Esse tipo de solução que ganha de brinde é o que eu mais gosto.

A parte da modelagem foi a mais rica. A rejeição do snapshot pelo Raffa foi precisa — ele foi direto ao ponto: snapshot aumenta chance de dado errado. Concordei sem hesitar porque a razão era boa. A alternativa de event sourcing não só resolve o delta mas cria fundação para análises futuras (tempo em cada status, quem moveu o quê, funil de conversão da fila).

A fricção do GRANT foi clássica de banco compartilhado: usuário que cria a tabela ≠ usuário que lê. Demorei uma rodada pra diagnosticar porque a solução óbvia (GRANT para `sharebook_ai_ro` e `sharebook_ai_rw`) não resolveu. Checar `pg_stat_activity` foi o movimento certo — evidência bruta antes de chute. Resolveu na segunda rodada.
