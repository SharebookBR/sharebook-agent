---
name: daily-triage-recovery
description: Analyze and recover the Sharebook ebook importer triage batch from today. Use when the user asks to inspect today's import queue, source_blocked items, the overnight triage worker run, items that ran after midnight, daily triage failures, or to save/importer items from the current day's triage window while deciding whether to harden the worker.
---

# Daily Triage Recovery

Use this skill for the daily review of the ebook importer triage worker output. It is not a full backlog sweep. The default scope is the current day in `America/Sao_Paulo` (GMT-3), starting at local midnight.

Also use `../ebook-importer/SKILL.md` for importer status names, commands, database guardrails, manual Windows flow, and hardening patterns.

## Core Rule

Look at what the triage worker processed today, not every old item in the queue.

The worker normally runs from `00:00` to `08:00` every 15 minutes. "Today" means local date in `America/Sao_Paulo`; always convert from UTC when querying `created_at`, `updated_at`, `changed_at`, `started_at`, or `finished_at`.

## Default Scope

Start from items that transitioned to `source_blocked` today:

```sql
SELECT DISTINCT qi.id, qi.title, qi.author, qi.source_url, qi.status, qi.last_error,
       h.changed_at AT TIME ZONE 'America/Sao_Paulo' AS local_changed_at
FROM importer.queue_item_history h
JOIN importer.queue_items qi ON qi.id = h.queue_item_id
WHERE h.to_status = 'source_blocked'
  AND h.changed_at >= (date_trunc('day', now() AT TIME ZONE 'America/Sao_Paulo') AT TIME ZONE 'America/Sao_Paulo')
ORDER BY qi.id;
```

If the user asks "from item N onward", combine the daily window with `qi.id >= N` unless they explicitly ask for the whole backlog.

## Triage Decision

For each item, classify it before touching the database:

- `recoverable`: official/public PDF exists or the source URL can be corrected.
- `hardening_candidate`: the fix is likely to repeat and belongs in extractor/worker/crawler logic.
- `triage_rejected`: source is HTML-only, video, platform page, paywall, non-ebook, pirated source, or no redistributable PDF.
- `true_blocked`: WAF, signed download, browser-only flow, broken host, or access restriction that is not worth automating now.
- `new_source_candidate`: the item itself is not a book, but reveals a reusable source worth adding later.

Prefer transforming manual recovery into worker hardening when the pattern is repeatable. Do not force automation for rare, expensive, or impossible cases.

**Before marking anything `true_blocked` due to WAF or browser-only flow**: ask Raffa if he can download the PDF manually. WAF blocks the worker but not a human browser. A manual download + windows-manual.md flow can still save the item. Only give up after he confirms he cannot or does not want to.

## Workflow

1. Query the item, source, status, `last_error`, history, and recent runs.
2. Inspect the source URL and any official alternatives. Prefer primary/official sources over random mirrors.
3. Validate candidate PDFs with status, content type, content length, and `%PDF` magic bytes.
4. Check license/redistribution enough to avoid pirated or restricted material.
5. Discuss the intended action with Raffa before changing production state, unless he explicitly asked to execute.
6. If hardening is worthwhile, patch the worker/extractor first and validate locally.
7. Return the item to `waiting_triage`, run `triage-once --id <ID>`, and collect feedback.
8. Report final item status, run status/id, history transition, manifest PDF URL, and any commit hash.

## Database Guardrails

- PostgreSQL is source of truth: `sharebook_importer`, schema `importer`.
- Use IDs, never queue position.
- Preserve `metadata_json`; merge rather than overwrite when doing direct DB work.
- Do not mark a manually rescued item `done`; let the worker flow advance it.
- For source URL corrections, set `status='waiting_triage'`, clear `last_error`, clear `retry_after`, reset `retry_count=0`, and insert history.
- If changing code, commit and push after validation.

## Common Outcomes

### Correct Source URL

Use when the item points to HTML but an official direct PDF exists.

Result: update `source_url`, optionally title/author, reset to `waiting_triage`, run worker, confirm `waiting_editorial`.

### Worker Hardening

Use when an extractor can learn a repeatable pattern: URL family handler, redirect/cookie session, release asset discovery, Wayback raw link, platform-specific API, or clean rejection.

Result: patch code, run local focused test, reset item, run worker, collect feedback, commit and push.

### Clean Rejection

Use when there is no public/redistributable PDF or the item is not a book.

Result: prefer worker-based `triage_rejected` with readable `last_error` / `triage.detail`; avoid leaving semantic failures as `source_blocked`.

### Leave Quiet

Use when the item is not worth energy today. Say why, and move on without mutating state.

## Reporting Style

Keep the report operational:

- what the item is;
- why the worker failed;
- whether it is recoverable;
- what action you intend or performed;
- feedback from the rerun;
- code commit if any.

Avoid broad backlog analysis unless requested. The daily harvest is valuable because it is narrow.
