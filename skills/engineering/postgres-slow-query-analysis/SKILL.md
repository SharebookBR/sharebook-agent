---
name: postgres-slow-query-analysis
description: Analyze PostgreSQL slow queries and report findings without making changes. Use when asked to inspect slow queries, database performance offenders, slow query logs, pg_stat_statements, or weekly read-only performance reviews for the Sharebook backend. This skill is strictly analysis-only and must never alter database settings, schema, data, containers, or application code.
---

# Postgres Slow Query Analysis

Perform a read-only investigation of slow queries in the Sharebook backend and report the findings to Raffa. Do not change anything.

## Hard rules

- Only analyze and report.
- Never execute `INSERT`, `UPDATE`, `DELETE`, `ALTER`, `CREATE`, `DROP`, `TRUNCATE`, `REINDEX`, `VACUUM`, `ANALYZE`, `docker update`, deploy, restart, or config changes.
- Never enable extensions, change Postgres settings, or alter container logging.
- Never propose that a change was already applied when it was not.
- If a useful next step would require mutation, stop at recommendation.

## Goal

Identify the main slow-query offenders, name them clearly, and summarize likely causes in practical language.

## Preferred workflow

1. Confirm available observability without changing anything.
   - Check whether `pg_stat_statements` exists.
   - Check relevant read-only settings such as `log_min_duration_statement`, `track_io_timing`, and `compute_query_id`.
2. Inspect read-only database statistics.
   - Use `pg_stat_user_tables`, `pg_stat_user_indexes`, `pg_stat_database`, `pg_stat_activity`, `pg_stats`, and `information_schema` as needed.
   - Look for high `seq_scan`, high `seq_tup_read`, low `idx_scan`, temp usage, and suspicious table access patterns.
3. Inspect the Postgres container logs through the VPS in read-only mode.
   - Use the canonical VPS helper: `sharebook-agent/scripts/infra/vps_ssh.py`.
   - Discover the application Postgres container with `docker ps` if needed.
   - Read logs only. Do not restart containers or edit retention.
   - Search for entries matching slow statements, typically `duration: ... ms`.
4. Group the offenders.
   - Normalize recurring patterns by table set and query shape.
   - Prefer naming offenders by business meaning, for example:
     - heavy `Books + Users + BookUser` ORM hydration query
     - `JobHistories` search/order query
     - large log/batch write
5. Report only what the evidence supports.
   - Distinguish clearly between confirmed evidence from logs and statistical suspicion from table/index metrics.
   - If retention is too short for a true 7-day view, say so plainly.

## Sharebook-specific heuristics

- A giant query selecting many columns from `Books`, joined with `Users` and `BookUser`, is a likely top offender when container logs show repeated durations above 1 second.
- `JobHistories` with very high sequential reads and text filtering in `Details` is a likely operational offender.
- `MailBounces` or `Meetups` with many sequential scans can indicate waste, but they are lower priority unless logs confirm slow statements.
- `COPY Logs ... FROM STDIN BINARY` above 1 second is worth noting, but usually below the main read-query offenders unless frequency is high.

## Reporting format

Keep the report compact and decision-oriented. Include:

1. Observability status
2. Top offenders
3. Evidence
4. Limitations
5. Recommended next read-only investigation

Use direct language. Name the offenders explicitly. Example style:

- Offender 1: giant `Books` query with `Users` and `BookUser`
- Offender 2: `JobHistories` search/order pattern
- Offender 3: `COPY Logs` batch writes

## WhatsApp delivery

When sending the final weekly report to Raffa on WhatsApp:

- Keep it concise.
- Favor bullets.
- Focus on the top 2 or 3 offenders.
- Explicitly state that this was an analysis-only pass and nothing was changed.
- If there is no meaningful signal, say that no clear offender was identified from the retained logs/statistics.

## Canonical tools and paths

- Read-only DB query skill: `sharebook-agent/skills/engineering/sharebook-postgres-ro/SKILL.md`
- VPS helper: `sharebook-agent/scripts/infra/vps_ssh.py`
- VPS playbook: `sharebook-agent/skills/infra/coolify-vps.md`

## Minimal command patterns

Use these only as patterns, adapting carefully and keeping everything read-only.

```bash
python3 sharebook-agent/scripts/production/sharebook_prod_pg_ro_query_direct.py --csv --sql "SELECT name, setting FROM pg_settings WHERE name IN ('log_min_duration_statement','track_io_timing','compute_query_id','shared_preload_libraries');"
```

```bash
python3 sharebook-agent/scripts/production/sharebook_prod_pg_ro_query_direct.py --csv --sql "SELECT schemaname, relname, seq_scan, seq_tup_read, idx_scan, n_live_tup FROM pg_stat_user_tables ORDER BY seq_tup_read DESC NULLS LAST LIMIT 20;"
```

```bash
python3 sharebook-agent/scripts/infra/vps_ssh.py --cmd "docker logs --since 168h <postgres-container> 2>&1 | grep -E 'duration: .* ms' | tail -n 200"
```

## Stop conditions

Stop and report instead of digging forever when:

- the logs retained are insufficient for the requested time window
- the container cannot be reached read-only
- the evidence is enough to name the main offenders already

The point is not to produce a thesis. The point is to identify the real offenders quickly, safely, and without touching production.
