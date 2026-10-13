#!/usr/bin/env python3
import sys
from pathlib import Path

# Resolve shared operational modules after playbook colocation.
_AGENT_ROOT = next((p for p in Path(__file__).resolve().parents if (p / "AGENTS.md").exists()), None)
if _AGENT_ROOT:
    sys.path.insert(0, str(_AGENT_ROOT / "playbooks" / "_shared" / "scripts"))
    sys.path.insert(0, str(_AGENT_ROOT / "playbooks" / "_shared" / "scripts" / "production"))

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sharebook_prod_auth import load_env, get_token  # noqa: E402


def main() -> int:
    repo_root = next((p for p in Path(__file__).resolve().parents if (p / "AGENTS.md").exists()), Path.cwd())
    env_values = load_env(repo_root)
    get_token(env_values, repo_root=repo_root, force_refresh=True)
    print("Token renovado e salvo no .env.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
