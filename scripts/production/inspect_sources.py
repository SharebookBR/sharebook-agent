import psycopg2, json

conn = psycopg2.connect(
    host="212.85.23.202", port=5432, dbname="sharebook_importer",
    user="sharebook_ai_rw", password="F%Ljy9oxTA3iR#npW%4W9iaSaJKU", sslmode="disable"
)
cur = conn.cursor()

# colunas da tabela
cur.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_schema = 'importer' AND table_name = 'sources'
    ORDER BY ordinal_position
""")
print("=== COLUNAS: importer.sources ===")
for row in cur.fetchall():
    print(f"  {row[0]} | {row[1]} | nullable={row[2]}")

# dados
cur.execute('SELECT * FROM importer.sources')
rows = cur.fetchall()
print(f"\n=== DADOS ({len(rows)} sources) ===")
for row in rows:
    print(f"  {row}")

conn.close()
