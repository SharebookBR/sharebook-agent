#!/usr/bin/env python3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sharebook_prod_auth import load_env, get_token  # noqa: E402


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    env_values = load_env(repo_root)
    token = get_token(env_values, repo_root=repo_root, force_refresh=True)
    print(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
