# Credenciais de produção lidas do .env — nunca hardcode.
#
# Uso:
#     from prod_env import pg_ro, pg_rw, ssh_credentials
#
#     conn = pg_ro()                              # banco sharebook (leitura)
#     conn = pg_rw(dbname="sharebook_importer")   # fila do importer (escrita)
#     user, host, port, password = ssh_credentials()
#
# O .env fica na raiz do sharebook-agent e está no .gitignore.
# Mesmo padrão de build_dsn() em skills/importers/ebook-importer/scripts/render_covers.py.

from __future__ import annotations

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"


def load_env() -> None:
    if not ENV_PATH.exists():
        raise SystemExit(f".env não encontrado: {ENV_PATH}")
    load_dotenv(ENV_PATH)


def _required(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise SystemExit(f"Variável obrigatória ausente no .env: {key}")
    return value


def _connect(prefix: str, dbname: str | None):
    load_env()
    return psycopg2.connect(
        host=_required(f"{prefix}_HOST"),
        port=int(_required(f"{prefix}_PORT")),
        dbname=dbname or _required(f"{prefix}_DATABASE"),
        user=_required(f"{prefix}_USER"),
        password=_required(f"{prefix}_PASSWORD"),
        sslmode=os.getenv(f"{prefix}_SSLMODE", "disable"),
    )


def pg_ro(dbname: str | None = None):
    """Conexão de leitura. Sem dbname, usa SHAREBOOK_PROD_PG_RO_DATABASE."""
    return _connect("SHAREBOOK_PROD_PG_RO", dbname)


def pg_rw(dbname: str | None = None):
    """Conexão de escrita. Sem dbname, usa SHAREBOOK_PROD_PG_RW_DATABASE."""
    return _connect("SHAREBOOK_PROD_PG_RW", dbname)


def ssh_credentials(prefix: str = "VPS_HOSTGATOR_SSH") -> tuple[str, str, int, str]:
    """Credenciais SSH da VPS. Padrão: HostGator (produção desde 2026-08-17).

    Use prefix="VPS_SSH" para a caixa antiga da Hostinger, mantida como rollback.
    """
    load_env()
    return (
        _required(f"{prefix}_USER"),
        _required(f"{prefix}_HOST"),
        int(os.getenv(f"{prefix}_PORT", "22")),
        _required(f"{prefix}_PASSWORD"),
    )
