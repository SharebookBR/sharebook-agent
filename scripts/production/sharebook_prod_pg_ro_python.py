#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path
import pg8000.native

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
    parser = argparse.ArgumentParser(description="Consulta Postgres via pg8000 (Pure Python).")
    parser.add_argument("--env-file", default="sharebook-agent/.env")
    parser.add_argument("--sql", help="SQL query.")
    parser.add_argument("--sql-file", help="SQL file.")
    args = parser.parse_args()

    env = parse_env(Path(args.env_file))
    
    user = env.get("SHAREBOOK_PROD_PG_RO_USER", "postgres")
    password = env.get("SHAREBOOK_PROD_PG_RO_PASSWORD")
    host = env.get("SHAREBOOK_PROD_PG_RO_HOST", "212.85.23.202")
    port = int(env.get("SHAREBOOK_PROD_PG_RO_PORT", 5432))
    database = env.get("SHAREBOOK_PROD_PG_RO_DATABASE", "postgres")

    if not password:
        print("Erro: SHAREBOOK_PROD_PG_RO_PASSWORD não encontrada no .env", file=sys.stderr)
        return 1

    if args.sql_file:
        sql = Path(args.sql_file).read_text(encoding="utf-8")
    elif args.sql:
        sql = args.sql
    else:
        print("Erro: Forneça --sql ou --sql-file", file=sys.stderr)
        return 1

    try:
        con = pg8000.native.Connection(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        
        for row in con.run(sql):
            print("\t".join(map(str, row)))
            
    except Exception as e:
        print(f"Erro na conexão/query: {e}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
