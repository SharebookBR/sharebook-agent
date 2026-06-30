import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

item_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1046

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

conn = psycopg2.connect(
    host=os.environ["SHAREBOOK_PROD_PG_RW_HOST"],
    port=int(os.environ["SHAREBOOK_PROD_PG_RW_PORT"]),
    dbname="sharebook_importer",
    user=os.environ["SHAREBOOK_PROD_PG_RW_USER"],
    password=os.environ["SHAREBOOK_PROD_PG_RW_PASSWORD"],
    sslmode=os.getenv("SHAREBOOK_PROD_PG_RW_SSLMODE", "disable"),
)
cur = conn.cursor()
cur.execute("""
    SELECT qi.id, qi.title, qi.author, qi.status, qi.source_url,
           qi.planned_title, qi.planned_author, qi.planned_synopsis,
           qi.planned_category_id, qi.planned_by,
           qi.triage_attempts, qi.publish_attempts, qi.metadata_json,
           s.name as source_name
    FROM importer.queue_items qi
    JOIN importer.sources s ON s.id = qi.source_id
    WHERE qi.id = %s
""", (item_id,))
row = cur.fetchone()
if not row:
    print(f"Item {item_id} não encontrado.")
    conn.close()
    sys.exit(1)

cols = ["id","title","author","status","source_url","planned_title","planned_author",
        "planned_synopsis","planned_category_id","planned_by","triage_attempts","publish_attempts",
        "metadata_json","source_name"]
data = dict(zip(cols, row))

print(f"=== ITEM {item_id} ===")
for k, v in data.items():
    if k == "metadata_json":
        continue
    print(f"  {k}: {v}")

meta = data.get("metadata_json") or {}
print(f"\n=== METADATA ===")
triage = meta.get("triage", {})
manifest = meta.get("manifest", {})
print(f"  triage.mode:    {triage.get('mode')}")
print(f"  triage.reason:  {triage.get('reason')}")
print(f"  local_pdf:      {meta.get('local_pdf')}")
print(f"  local_cover:    {meta.get('local_cover')}")
print(f"  manifest.pdf_url:   {manifest.get('pdf_url')}")
print(f"  manifest.cover_url: {manifest.get('cover_url')}")
print(f"  manifest.author:    {manifest.get('author')}")
preview = triage.get("preview_pages", [])
print(f"  preview_pages:  {len(preview)} página(s)")
ctx = triage.get("context_text", "")
print(f"\n=== CONTEXT TEXT (primeiros 500 chars) ===")
print(ctx[:500] if ctx else "(vazio)")

conn.close()
