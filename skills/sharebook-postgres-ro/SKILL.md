---
name: sharebook-postgres-ro
description: Consultas read-only no Postgres de produção do Sharebook usando scripts oficiais (direto sem SSH e fallback via SSH). Use quando precisar responder métricas, top lists, auditoria de jobs, inspeção de schema/tabelas/colunas e diagnósticos de dados sem alterar produção.
---

# Sharebook Postgres RO

Executar consulta de banco com segurança e velocidade, sem improvisar SQL de risco.

## Workflow

1. Preferir caminho direto (sem SSH):
   - `sharebook-agent/scripts/sharebook_prod_pg_ro_query_direct.py`
2. Se o direto falhar por rede, usar fallback SSH:
   - `sharebook-agent/scripts/sharebook_prod_pg_ro_query.py`
3. Começar por descoberta mínima quando houver dúvida de schema:
   - tabelas (`information_schema.tables`)
   - colunas (`information_schema.columns`)
4. Rodar query final com projeção explícita (sem `SELECT *`) e `LIMIT` quando fizer sentido.
5. Entregar resultado em formato útil ao pedido (tabela curta, CSV, resumo executivo).

## Guardrails (hard)

- Apenas `SELECT`/CTE read-only.
- Nunca executar `INSERT`, `UPDATE`, `DELETE`, `ALTER`, `DROP`, `TRUNCATE`, `CREATE`.
- Não expor dado sensível bruto; resumir/mascarar quando necessário.
- Em dúvida de tabela/coluna, descobrir antes de consultar.

## Comandos canônicos

```bash
python3 sharebook-agent/scripts/sharebook_prod_pg_ro_query_direct.py --csv --sql "SELECT now();"
```

```bash
python3 sharebook-agent/scripts/sharebook_prod_pg_ro_query_direct.py --csv --sql "SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY 2;"
```

```bash
python3 sharebook-agent/scripts/sharebook_prod_pg_ro_query_direct.py --csv --sql "SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='Books' ORDER BY ordinal_position;"
```

## Receitas prontas

Para consultas recorrentes, ler: `references/queries.md`.
