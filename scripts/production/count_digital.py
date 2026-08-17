from prod_env import pg_ro

conn = pg_ro()
cur = conn.cursor()

cur.execute('SELECT COUNT(*) FROM "Books" WHERE "Type" = 1')
digital = cur.fetchone()[0]

cur.execute('SELECT COUNT(*) FROM "Books" WHERE "Type" = 0')
physical = cur.fetchone()[0]

cur.execute('SELECT COUNT(*) FROM "Books"')
total = cur.fetchone()[0]

print(f"Digital:  {digital}")
print(f"Físico:   {physical}")
print(f"Total:    {total}")

conn.close()
