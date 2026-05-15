import pg8000
import argparse
import os
import csv
import sys
from pathlib import Path

def parse_env(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip()
    return data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sql")
    parser.add_argument("--sql-file")
    parser.add_argument("--env-file", default="sharebook-agent/.env")
    args = parser.parse_args()

    env = parse_env(Path(args.env_file))
    
    host = env.get("SHAREBOOK_PROD_PG_RO_HOST")
    port = int(env.get("SHAREBOOK_PROD_PG_RO_PORT", 5432))
    database = env.get("SHAREBOOK_PROD_PG_RO_DATABASE")
    user = env.get("SHAREBOOK_PROD_PG_RO_USER")
    password = env.get("SHAREBOOK_PROD_PG_RO_PASSWORD")

    if not all([host, database, user, password]):
        print("Erro: Credenciais incompletas no .env")
        sys.exit(1)

    sql = args.sql
    if args.sql_file:
        sql = Path(args.sql_file).read_text(encoding="utf-8")

    try:
        conn = pg8000.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        cursor = conn.cursor()
        cursor.execute(sql)
        
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []

        writer = csv.writer(sys.stdout)
        if columns:
            writer.writerow(columns)
        for row in results:
            writer.writerow(row)

        conn.close()
    except Exception as e:
        print(f"Erro ao executar query: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
