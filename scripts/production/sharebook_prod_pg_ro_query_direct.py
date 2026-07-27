#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
from pathlib import Path


def parse_env(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip()
    return data


def req(env: dict[str, str], key: str) -> str:
    val = env.get(key, "").strip()
    if not val:
        raise SystemExit(f"Variável obrigatória ausente no .env: {key}")
    return val


def run_with_psycopg(
    *,
    host: str,
    port: str,
    db: str,
    user: str,
    password: str,
    sslmode: str,
    sql: str,
    csv_output: bool,
    tuples_only: bool,
) -> int:
    try:
        import psycopg2
    except ImportError:
        print(
            "psql não foi encontrado e psycopg2 não está instalado. "
            "Instale um dos dois para consultar o Postgres.",
            file=sys.stderr,
        )
        return 2

    try:
        with psycopg2.connect(
            host=host,
            port=port,
            dbname=db,
            user=user,
            password=password,
            sslmode=sslmode,
        ) as connection:
            connection.set_session(readonly=True, autocommit=True)
            with connection.cursor() as cursor:
                cursor.execute(sql)
                if cursor.description is None:
                    return 0

                headers = [column.name for column in cursor.description]
                rows = cursor.fetchall()
                delimiter = "," if csv_output else "\t"
                writer = csv.writer(sys.stdout, delimiter=delimiter, lineterminator="\n")
                if not tuples_only:
                    writer.writerow(headers)
                writer.writerows(rows)
        return 0
    except psycopg2.Error as exc:
        print(f"Falha na consulta read-only: {exc}", file=sys.stderr)
        return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Query read-only direta no Postgres de produção (sem SSH).")
    ap.add_argument("--env-file", default="/data/workspace/sharebook-agent/.env")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--sql")
    src.add_argument("--sql-file")
    ap.add_argument("--csv", action="store_true")
    ap.add_argument("--tuples-only", action="store_true")
    args = ap.parse_args()

    env_path = Path(args.env_file)
    if not env_path.exists():
        raise SystemExit(f"Arquivo .env não encontrado: {env_path}")

    envf = parse_env(env_path)
    host = req(envf, "SHAREBOOK_PROD_PG_RO_HOST")
    port = req(envf, "SHAREBOOK_PROD_PG_RO_PORT")
    db = req(envf, "SHAREBOOK_PROD_PG_RO_DATABASE")
    user = req(envf, "SHAREBOOK_PROD_PG_RO_USER")
    password = req(envf, "SHAREBOOK_PROD_PG_RO_PASSWORD")
    sslmode = envf.get("SHAREBOOK_PROD_PG_RO_SSLMODE", "disable").strip() or "disable"

    if args.sql_file:
        sql = Path(args.sql_file).read_text(encoding="utf-8")
    else:
        sql = args.sql or ""

    psql = shutil.which("psql")
    if psql is None:
        return run_with_psycopg(
            host=host,
            port=port,
            db=db,
            user=user,
            password=password,
            sslmode=sslmode,
            sql=sql,
            csv_output=args.csv,
            tuples_only=args.tuples_only,
        )

    cmd = [
        psql,
        "-h", host,
        "-p", port,
        "-d", db,
        "-U", user,
        "-v", "ON_ERROR_STOP=1",
        "-P", "pager=off",
    ]
    if args.csv:
        cmd.append("--csv")
    if args.tuples_only:
        cmd.append("-t")
    cmd += ["-c", sql]

    proc_env = os.environ.copy()
    proc_env["PGPASSWORD"] = password

    completed = subprocess.run(cmd, env=proc_env)
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main())
