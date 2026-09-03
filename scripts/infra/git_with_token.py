#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
LIB_DIR = SCRIPT_DIR.parent / "lib"
sys.path.insert(0, str(LIB_DIR))

from sharebook_env import github_extra_header, load_env, resolve_env_file


def run_git(repo: Path, header: str, args: list[str]) -> None:
    command = ["git", "-C", str(repo), "-c", f"http.extraHeader={header}", *args]
    completed = subprocess.run(command)
    if completed.returncode:
        raise SystemExit(completed.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Executa git HTTPS usando GITHUB_PERSONAL_ACCESS_TOKEN do .env, sem persistir nem imprimir o token."
    )
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--env-file", type=Path, default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    sync = sub.add_parser("sync", help="fetch origin <branch>, rebase e push")
    sync.add_argument("--branch", default="master")

    raw = sub.add_parser("run", help="executa um comando git arbitrário")
    raw.add_argument("git_args", nargs=argparse.REMAINDER)

    args = parser.parse_args()
    values = load_env(resolve_env_file(args.env_file))
    header = github_extra_header(values)

    if args.command == "sync":
        run_git(args.repo, header, ["fetch", "origin", args.branch])
        run_git(args.repo, header, ["rebase", f"origin/{args.branch}"])
        run_git(args.repo, header, ["push", "origin", args.branch])
        return 0

    if not args.git_args:
        raise SystemExit("Informe argumentos após `run`, por exemplo: run status --short")
    run_git(args.repo, header, args.git_args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
