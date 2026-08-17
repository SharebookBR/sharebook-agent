from prod_env import pg_ro

conn = pg_ro()
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
