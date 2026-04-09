#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path

try:
    import paramiko
except ImportError as exc:  # pragma: no cover
    raise SystemExit("paramiko não está instalado. Rode: python -m pip install --user paramiko") from exc


def parse_env(env_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def required(values: dict[str, str], key: str) -> str:
    value = values.get(key, "").strip()
    if not value:
        raise SystemExit(f"Variável obrigatória ausente no .env: {key}")
    return value


def build_psql_command(values: dict[str, str], sql: str, csv: bool, tuples_only: bool) -> str:
    pg_host_container = required(values, "SHAREBOOK_PROD_PG_RO_HOST")
    pg_port = required(values, "SHAREBOOK_PROD_PG_RO_PORT")
    pg_db = required(values, "SHAREBOOK_PROD_PG_RO_DATABASE")
    pg_user = required(values, "SHAREBOOK_PROD_PG_RO_USER")
    pg_password = required(values, "SHAREBOOK_PROD_PG_RO_PASSWORD")

    psql_parts = [
        "docker", "exec", "-e", f"PGPASSWORD={pg_password}", "-i", pg_host_container,
        "psql", "-U", pg_user, "-d", pg_db, "-p", pg_port,
        "-v", "ON_ERROR_STOP=1",
        "-P", "pager=off",
    ]

    if csv:
        psql_parts += ["--csv"]
    if tuples_only:
        psql_parts += ["-t"]

    psql_parts += ["-c", sql]
    return " ".join(shlex.quote(part) for part in psql_parts)


def run_ssh_command(host: str, port: int, user: str, password: str, command: str, timeout: int) -> int:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=host,
        port=port,
        username=user,
        password=password,
        timeout=15,
        banner_timeout=15,
        auth_timeout=15,
    )

    try:
        _, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")

        if out:
            print(out.rstrip())
        if err:
            print(err.rstrip(), file=sys.stderr)

        return stdout.channel.recv_exit_status()
    finally:
        client.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Executa SQL read-only no Postgres de produção via SSH + docker exec (atalho enxuto)."
    )
    parser.add_argument(
        "--env-file",
        default="/data/workspace/sharebook-agent/.env",
        help="Caminho do .env com credenciais SSH e PG read-only.",
    )

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--sql", help="SQL inline para executar.")
    source.add_argument("--sql-file", help="Arquivo .sql para executar.")

    parser.add_argument("--csv", action="store_true", help="Saída CSV (psql --csv).")
    parser.add_argument("--tuples-only", action="store_true", help="Tuplas apenas (psql -t).")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout em segundos.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    env_path = Path(args.env_file)
    if not env_path.exists():
        raise SystemExit(f"Arquivo .env não encontrado: {env_path}")

    values = parse_env(env_path)

    ssh_host = required(values, "VPS_SSH_HOST")
    ssh_user = required(values, "VPS_SSH_USER")
    ssh_password = required(values, "VPS_SSH_PASSWORD")
    ssh_port = int(values.get("VPS_SSH_PORT", "22"))

    if args.sql_file:
        sql = Path(args.sql_file).read_text(encoding="utf-8")
    else:
        sql = args.sql or ""

    command = build_psql_command(values, sql, csv=args.csv, tuples_only=args.tuples_only)
    return run_ssh_command(ssh_host, ssh_port, ssh_user, ssh_password, command, timeout=args.timeout)


if __name__ == "__main__":
    sys.exit(main())
