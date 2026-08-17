from prod_env import pg_rw

conn = pg_rw(dbname="sharebook_importer")
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
