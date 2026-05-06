#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
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

    if args.sql_file:
        sql = Path(args.sql_file).read_text(encoding="utf-8")
    else:
        sql = args.sql or ""

    cmd = [
        "psql",
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
