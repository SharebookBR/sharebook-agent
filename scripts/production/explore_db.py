from prod_env import pg_ro, pg_rw

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
explore("sharebook", pg_ro())

# sharebook_importer (RW)
explore("sharebook_importer", pg_rw(dbname="sharebook_importer"))
