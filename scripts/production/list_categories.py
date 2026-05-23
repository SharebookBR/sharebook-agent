import psycopg2

conn = psycopg2.connect(
    host="212.85.23.202", port=5432, dbname="sharebook",
    user="sharebook_ai_ro", password="3-nbj0bw3STVkxlcCeEO2ZFwtvyn", sslmode="disable"
)
cur = conn.cursor()
cur.execute('SELECT "Id", "Name", "ParentCategoryId" FROM "Categories" ORDER BY "ParentCategoryId" NULLS FIRST, "Name"')
rows = cur.fetchall()

print("=== CATEGORIAS ===")
roots = [(r[0], r[1]) for r in rows if r[2] is None]
children = [(r[0], r[1], r[2]) for r in rows if r[2] is not None]

for rid, rname in roots:
    print(f"\n[ROOT] {rname} ({rid})")
    for cid, cname, pid in children:
        if str(pid) == str(rid):
            print(f"  └ {cname} ({cid})")

conn.close()
