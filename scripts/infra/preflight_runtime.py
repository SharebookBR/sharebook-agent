#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
LIB_DIR = SCRIPT_DIR.parent / "lib"
sys.path.insert(0, str(LIB_DIR))

from sharebook_env import load_env, require_env, resolve_agent_dir, resolve_env_file, sibling_repo


def run(command: list[str], *, cwd: Path | None = None) -> bool:
    completed = subprocess.run(command, cwd=str(cwd) if cwd else None)
    return completed.returncode == 0


def has_module(python: Path, module: str) -> bool:
    return subprocess.run(
        [str(python), "-c", f"import {module}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def ensure_debian_packages(packages: list[str], fix: bool) -> None:
    if not fix:
        return
    if os.name != "posix" or not Path("/usr/bin/apt-get").exists():
        return
    run(["apt-get", "update"])
    run(["apt-get", "install", "-y", *packages])


def ensure_importer_venv(importer_dir: Path, fix: bool) -> Path:
    venv_python = importer_dir / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if venv_python.exists():
        return venv_python
    if not fix:
        raise SystemExit(f"venv ausente: {venv_python}")
    if os.name == "posix":
        ensure_debian_packages(["python3.11-venv"], fix=True)
    if not run([sys.executable, "-m", "venv", ".venv"], cwd=importer_dir):
        raise SystemExit("falha ao criar .venv do importer")
    if not run([str(venv_python), "-m", "pip", "install", "-e", "."], cwd=importer_dir):
        raise SystemExit("falha ao instalar dependências do importer")
    return venv_python


def preflight_importer(env_file: Path, fix: bool) -> None:
    values = load_env(env_file)
    require_env(values, ["SHAREBOOK_AGENT_DIR", "IMPORTER_DB_DSN", "GITHUB_PERSONAL_ACCESS_TOKEN"])

    agent_dir = resolve_agent_dir(env_file)
    importer_dir = Path(values.get("SHAREBOOK_EBOOK_IMPORTER_DIR") or sibling_repo(agent_dir, "sharebook-ebook-importer"))
    if not importer_dir.exists():
        raise SystemExit(f"repo do importer não encontrado: {importer_dir}")

    if not shutil.which("pdftoppm"):
        ensure_debian_packages(["poppler-utils"], fix=fix)
    if not shutil.which("pdftoppm"):
        raise SystemExit("pdftoppm ausente; instale poppler-utils/Poppler")

    python = ensure_importer_venv(importer_dir, fix=fix)
    missing_modules = [module for module in ("psycopg2", "PIL", "pypdf") if not has_module(python, module)]
    if missing_modules:
        if not fix:
            raise SystemExit("dependências Python ausentes: " + ", ".join(missing_modules))
        if not run([str(python), "-m", "pip", "install", "-e", "."], cwd=importer_dir):
            raise SystemExit("falha ao reinstalar dependências do importer")

    print("preflight importer: ok")
    print(f"agent_dir={agent_dir}")
    print(f"importer_dir={importer_dir}")
    print(f"python={python}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight autocorretivo do runtime Sharebook.")
    parser.add_argument("--env-file", type=Path, default=None)
    parser.add_argument("--task", choices=["importer"], required=True)
    parser.add_argument("--no-fix", action="store_true", help="Somente diagnostica; não instala/corrige.")
    args = parser.parse_args()

    env_file = resolve_env_file(args.env_file)
    if args.task == "importer":
        preflight_importer(env_file, fix=not args.no_fix)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
