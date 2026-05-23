import psycopg2

def query(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()

def explore(label, conn):
    print(f"\n{'='*50}")
    print(f"BANCO: {label}")
    print('='*50)
    tables = query(conn, "SELECT schemaname, tablename FROM pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema') ORDER BY schemaname, tablename")
    print(f"Tabelas ({len(tables)}):\n")
    for schema, t in tables:
        try:
            cnt = query(conn, f'SELECT COUNT(*) FROM "{schema}"."{t}"')[0][0]
            print(f"  {schema}.{t}: {cnt} rows")
        except Exception as e:
            conn.rollback()
            print(f"  {schema}.{t}: erro - {e}")
    conn.close()

# sharebook principal (RO)
c1 = psycopg2.connect(
    host="212.85.23.202", port=5432, dbname="sharebook",
    user="sharebook_ai_ro", password="3-nbj0bw3STVkxlcCeEO2ZFwtvyn", sslmode="disable"
)
explore("sharebook", c1)

# sharebook_importer (RW — mesmo user)
c2 = psycopg2.connect(
    host="212.85.23.202", port=5432, dbname="sharebook_importer",
    user="sharebook_ai_rw", password="F%Ljy9oxTA3iR#npW%4W9iaSaJKU", sslmode="disable"
)
explore("sharebook_importer", c2)
