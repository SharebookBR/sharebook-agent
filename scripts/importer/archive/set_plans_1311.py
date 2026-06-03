import psycopg2
from datetime import datetime, timezone

GERAL_ID = "019dcbfc-0a09-702e-a0ab-090acb5597b6"

SYNOPSIS = """\
Composition is not just a programming technique — it is the central idea of an entire branch of mathematics. Category Theory for Programmers starts there, with Chapter 1 literally titled "Category: The Essence of Composition," and builds from arrows and objects all the way through functors, natural transformations, monads, Kleisli categories, adjunctions, and F-algebras across 498 pages.

The book covers two major tracks in parallel: the abstract mathematical theory and its direct translation to Haskell (and, in places, C++ and Scala). Readers encounter the Maybe functor, the Reader functor, the Curry-Howard isomorphism, Cartesian closed categories, and exponentials of algebraic data types — each introduced first as a mathematical object, then grounded in code. Every chapter ends with challenges that force the reader to prove or implement what they just read.

Originally a series of blog posts by Bartosz Milewski, one of the most respected voices in functional programming, this compiled edition (assembled by Igal Tabachnik) is the definitive free resource for programmers who want to understand why Haskell looks the way it does, why monads keep showing up everywhere, and what the mathematicians were actually thinking when they invented all of this. Dense, rewarding, and honest about its difficulty.\
"""

PLANS = [
    {
        "id": 1311,
        "planned_title": "Category Theory for Programmers",
        "planned_author": "Bartosz Milewski",
        "planned_category_id": GERAL_ID,
        "planned_synopsis": SYNOPSIS,
        "planned_by": "manual_windows",
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
            planned_title = %s, planned_author = %s, planned_category_id = %s,
            planned_synopsis = %s, planned_by = %s, planned_at = %s,
            status = 'waiting_process', updated_at = %s
        WHERE id = %s AND status = 'waiting_editor'
    """, (p["planned_title"], p["planned_author"], p["planned_category_id"],
          p["planned_synopsis"], p["planned_by"], now, now, p["id"]))
    print(f"#{p['id']} {p['planned_title']} → waiting_process  (rows={cur.rowcount})")

conn.commit()
conn.close()
