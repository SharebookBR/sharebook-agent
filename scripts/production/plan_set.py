"""Encaminha o plan-set local para a CLI canônica do ebook importer.

Uso:
    python plan_set.py --id 1046 --category-id <UUID> --synopsis-file <path>
                       [--title <title>] [--author <author>] [--planned-by <who>]
                       [--cover-url <path>] [--cover-path <path>]
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    workspace = Path(__file__).resolve().parents[3]
    cli_path = workspace / "sharebook-ebook-importer" / "cli.py"
    if not cli_path.is_file():
        raise FileNotFoundError(f"CLI canônica não encontrada: {cli_path}")

    completed = subprocess.run(
        [sys.executable, str(cli_path), "plan-set", *sys.argv[1:]],
        cwd=cli_path.parent,
        check=False,
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
