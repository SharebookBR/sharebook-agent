#!/usr/bin/env python3
from __future__ import annotations

import base64
import os
import re
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse, urlunparse

DEFAULT_OPENCLAW_AGENT_DIR = Path("/data/workspace/sharebook-agent")
DEFAULT_WINDOWS_AGENT_DIR = Path(r"C:\Repos\SHAREBOOK\sharebook-agent")


def default_agent_dir() -> Path:
    if DEFAULT_OPENCLAW_AGENT_DIR.exists():
        return DEFAULT_OPENCLAW_AGENT_DIR
    return DEFAULT_WINDOWS_AGENT_DIR


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def resolve_agent_dir(env_file: Path | None = None) -> Path:
    candidate_env = env_file or default_agent_dir() / ".env"
    if candidate_env.exists():
        configured = parse_env_file(candidate_env).get("SHAREBOOK_AGENT_DIR")
        if configured:
            return Path(configured)
    return default_agent_dir()


def resolve_env_file(env_file: Path | None = None) -> Path:
    if env_file is not None:
        return env_file
    configured = os.getenv("SHAREBOOK_AGENT_ENV_FILE")
    if configured:
        return Path(configured)
    return resolve_agent_dir() / ".env"


def load_env(env_file: Path | None = None) -> dict[str, str]:
    path = resolve_env_file(env_file)
    if not path.exists():
        raise SystemExit(f".env não encontrado: {path}")
    return parse_env_file(path)


def require_env(values: dict[str, str], keys: Iterable[str]) -> None:
    missing = [key for key in keys if not values.get(key)]
    if missing:
        raise SystemExit("Variáveis obrigatórias ausentes no .env: " + ", ".join(missing))


def sibling_repo(agent_dir: Path, repo_name: str) -> Path:
    return agent_dir.parent / repo_name


def is_windows_path(value: str) -> bool:
    return bool(re.match(r"^[A-Za-z]:[\\/]", value)) or "\\" in value


def resolve_runtime_path(value: str | None, default: Path) -> Path:
    """Resolve um path do .env respeitando o habitat (Windows x POSIX).

    Ignora paths de outro SO (ex.: C:\\... dentro de container Linux) e cai no
    default derivado, evitando diretórios-lixo e quebra de publish/materialize.
    """
    if not value:
        return default
    if os.name == "nt":
        if value.startswith("/") and not is_windows_path(value):
            return default
    else:
        if is_windows_path(value):
            return default
    return Path(value)


def github_extra_header(values: dict[str, str]) -> str:
    token = values.get("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        raise SystemExit("GITHUB_PERSONAL_ACCESS_TOKEN ausente no .env")
    encoded = base64.b64encode(f"x-access-token:{token}".encode("utf-8")).decode("ascii")
    return "AUTHORIZATION: basic " + encoded


def dsn_with_host_port(dsn: str, host: str, port: int) -> str:
    parsed = urlparse(dsn)
    if not parsed.scheme or "@" not in parsed.netloc:
        raise SystemExit("IMPORTER_DB_DSN precisa estar no formato postgresql://user:pass@host:port/db")
    userpass = parsed.netloc.rsplit("@", 1)[0]
    return urlunparse((parsed.scheme, f"{userpass}@{host}:{port}", parsed.path, "", "", ""))


def print_env_keys(values: dict[str, str]) -> None:
    for key in sorted(values):
        print(key)
