# Missão — Automação BaixeLivros Worker (SQLite + Cron)

## Objetivo
Automatizar a ingestão de ebooks do BaixeLivros para o Sharebook com segurança operacional, evitando duplicações e mantendo throughput constante.

## Escopo inicial (MVP)
- 1 execução por hora
- 1 livro processado por execução
- Fonte inicial: `Literatura Estrangeira`
- Controle de fila em SQLite
- Worker Python rodando em container dedicado
- Agendamento via cron

---

## Entregáveis
1. **Worker Python** com fluxo sequencial e idempotente
2. **Banco SQLite** com estado da fila e histórico de tentativas
3. **Container dedicado** (`sharebook-importer-worker`)
4. **Cron job** com lock para impedir concorrência
5. **Logs estruturados** (JSON) + resumo de execução
6. **Playbook operacional** (start/stop/debug/retry)

---

## Arquitetura proposta
- Código: repositório `sharebook-agent`
- Runtime: container isolado
- Persistência: volume Docker para `sqlite.db` + diretório de logs
- Scheduler: cron no host chamando worker

### Tabelas SQLite (mínimo)
- `sources` (id, name, url, enabled)
- `queue_items` (id, source_id, position, title, author, source_url, status, attempts, last_error, sharebook_book_id, updated_at)
- `runs` (id, started_at, finished_at, status, processed_item_id, message)

Status de `queue_items`:
- `pending`
- `in_progress`
- `done`
- `source_blocked`
- `retry_later`

---

## Fluxo do worker (por execução)
1. Adquirir lock global
2. Selecionar primeiro item `pending`
3. Extrair metadados + capa + PDF da fonte
4. Validar licença/bloqueio óbvio
5. Dedupe no Sharebook (título + autor + variações)
6. Se já existir: marcar `done` com referência
7. Se não existir: criar ebook e aprovar
8. Persistir resultado em `queue_items` + `runs`
9. Liberar lock

---

## Regras de segurança operacional
- Sem execução paralela do mesmo worker
- Timeout por execução
- Retry com limite (ex.: 3) antes de `retry_later`
- Falha permanente de fonte -> `source_blocked`
- Nunca reordenar fila automaticamente

---

## Fases

## Fase 1 — MVP funcional
- Schema SQLite
- Worker `run-once`
- Dockerfile + compose service
- Cron horário
- Teste real com 2 itens em ambiente controlado

## Fase 2 — Hardening
- Backoff e classificação de erros
- Logs JSON e sumário por execução
- Comando de inspeção de fila (`status`)
- Script de recuperação de item travado (`in_progress` antigo)

## Fase 3 — Escala segura
- Multi-categoria por `source_id`
- Cadência ajustável por fonte
- Alertas em falha recorrente
- Painel simples de progresso

---

## Critérios de sucesso
- 7 dias sem duplicação
- >95% de execuções concluídas sem intervenção manual
- Throughput estável (>= 1 livro/h no horário ativo)
- Reprocessamento seguro após falha (idempotência comprovada)

---

## Critérios de rollback
- Duplicações detectadas em produção
- Falha repetida de aprovação/publicação
- Crescimento de `retry_later` acima do limite definido

Ação de rollback:
- pausar cron
- manter banco e logs para análise
- retomar fluxo manual temporariamente

---

## Próximo passo imediato
Implementar **Fase 1** em modo conservador (1 item/h), com validação em produção assistida nas primeiras execuções.
