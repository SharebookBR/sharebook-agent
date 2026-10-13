#!/usr/bin/env python3
"""Sonda os endpoints públicos de Tag na API de produção e lista tags existentes."""
from __future__ import annotations
import sys
from pathlib import Path

# Resolve shared operational modules after playbook colocation.
_AGENT_ROOT = next((p for p in Path(__file__).resolve().parents if (p / "AGENTS.md").exists()), None)
if _AGENT_ROOT:
    sys.path.insert(0, str(_AGENT_ROOT / "playbooks" / "_shared" / "scripts"))
    sys.path.insert(0, str(_AGENT_ROOT / "playbooks" / "_shared" / "scripts" / "production"))


import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sharebook_prod_auth import API_BASE, get_token, load_env, request_json  # noqa: E402


def main() -> int:
    repo_root = next((p for p in Path(__file__).resolve().parents if (p / "AGENTS.md").exists()), Path.cwd())
    env_values = load_env(repo_root)
    token = get_token(env_values, repo_root=repo_root)

    # GET /api/Tag (público)
    try:
        tags = request_json(f"{API_BASE}/Tag")
        print("GET /Tag OK")
        print(json.dumps(tags, ensure_ascii=False, indent=2))
    except Exception as exc:  # noqa: BLE001
        print(f"GET /Tag FALHOU: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
