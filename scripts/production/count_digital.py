import psycopg2

conn = psycopg2.connect(
    host="212.85.23.202", port=5432, dbname="sharebook",
    user="sharebook_ai_ro", password="3-nbj0bw3STVkxlcCeEO2ZFwtvyn", sslmode="disable"
)
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
