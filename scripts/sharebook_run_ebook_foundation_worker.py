#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sharebook_prod_auth import ApiHttpError, auth_headers, get_token, load_env, request_json  # noqa: E402

API_BASE = "https://api.sharebook.com.br/api"
REPO_ROOT = Path(__file__).resolve().parent.parent
IMPORTER_ROOT = REPO_ROOT.parent / "sharebook-ebook-importer"
IMPORTER_SRC = IMPORTER_ROOT / "src"
IMPORTER_ENV_PATH = IMPORTER_ROOT / ".env"


def load_importer_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def probe_token(token: str) -> None:
    request_json(
        f"{API_BASE}/category",
        headers={**auth_headers(token), "x-requested-with": "web"},
    )


def obtain_valid_token(env_values: dict[str, str]) -> str:
    token = get_token(env_values, repo_root=REPO_ROOT, force_refresh=False)
    try:
        probe_token(token)
        return token
    except ApiHttpError as exc:
        if exc.code != 401:
            raise
    token = get_token(env_values, repo_root=REPO_ROOT, force_refresh=True)
    probe_token(token)
    return token


def main(argv: list[str]) -> int:
    source = argv[1] if len(argv) > 1 else "ebook_foundation"
    agent_env = load_env(REPO_ROOT)
    importer_env = load_importer_env(IMPORTER_ENV_PATH)

    token = obtain_valid_token(agent_env)
    db_dsn = importer_env["IMPORTER_DB_DSN"]

    env = os.environ.copy()
    env["IMPORTER_DB_DSN"] = db_dsn
    env["TOKEN_V2"] = token

    cmd = [sys.executable, "-m", "sharebook_ebook_importer.cli", "run-once", "--source", source]
    result = subprocess.run(cmd, cwd=IMPORTER_SRC, env=env)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
