import psycopg2
from datetime import datetime, timezone

DEVOPS_ID = "019d636c-640a-7e2f-babd-c22d3b37c226"

SYNOPSIS = """\
Most explanations of SELinux start with access control policies and end with the reader more confused than before. This coloring book takes a different approach: using cats, dogs, and bowls of food as its teaching metaphor, it walks through Type Enforcement — the core model behind SELinux — by showing how process types and object types interact through explicit policy rules like ALLOW CAT CAT_CHOW:FOOD EAT.

Across its 16 illustrated pages, the book covers the fundamental concepts that make SELinux tick: process types, object types, policy rules, and how labels are applied to both. By mapping each concept to a simple animal analogy, it builds intuition for why mandatory access control exists and how it constrains what processes can and cannot do on a Linux system — without relying on jargon as a crutch.

Written by Dan Walsh, one of the key engineers behind SELinux in Fedora and RHEL, and illustrated by Máirín Duffy, this is the rare security document that is genuinely approachable. It won't replace a full SELinux reference, but it will give any Linux user or sysadmin a mental model they can actually hold onto before diving into the deeper material.\
"""

PLANS = [
    {
        "id": 1302,
        "planned_title": "The SELinux Coloring Book",
        "planned_author": "Dan Walsh, Máirín Duffy",
        "planned_category_id": DEVOPS_ID,
        "planned_synopsis": SYNOPSIS,
        "planned_by": "manual_windows",
        "planned_level": "basico",
    }
]

conn = psycopg2.connect(
    host="212.85.23.202", port=5432, dbname="sharebook_importer",
    user="sharebook_ai_rw", password="F%Ljy9oxTA3iR#npW%4W9iaSaJKU", sslmode="disable"
)
cur = conn.cursor()
now = datetime.now(timezone.utc)

for p in PLANS:
    cur.execute("""
        UPDATE importer.queue_items SET
            planned_title = %s,
            planned_author = %s,
            planned_category_id = %s,
            planned_synopsis = %s,
            planned_by = %s,
            planned_at = %s,
            status = 'waiting_process',
            updated_at = %s
        WHERE id = %s AND status = 'waiting_editor'
    """, (
        p["planned_title"], p["planned_author"], p["planned_category_id"],
        p["planned_synopsis"], p["planned_by"], now, now, p["id"]
    ))
    print(f"#{p['id']} {p['planned_title']} → waiting_process  (rows={cur.rowcount})")

conn.commit()
conn.close()
