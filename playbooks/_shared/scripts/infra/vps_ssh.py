#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import paramiko
except ImportError as exc:  # pragma: no cover - runtime guidance
    raise SystemExit(
        "paramiko não está instalado. Rode: python -m pip install --user paramiko"
    ) from exc


def parse_env(env_path: Path, prefix: str = "VPS_SSH") -> tuple[str, str, int, str]:
    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise SystemExit(f"Linha inválida no .env: {line}")
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()

    host_key = f"{prefix}_HOST"
    user_key = f"{prefix}_USER"
    password_key = f"{prefix}_PASSWORD"
    port_key = f"{prefix}_PORT"

    required_keys = [host_key, user_key, password_key]
    missing_keys = [key for key in required_keys if not values.get(key)]
    if missing_keys:
        missing = ", ".join(missing_keys)
        raise SystemExit(f"Variáveis obrigatórias ausentes no .env: {missing}")

    host = values[host_key]
    user = values[user_key]
    password = values[password_key]

    try:
        port = int(values.get(port_key, "22"))
    except ValueError as exc:
        raise SystemExit(f"{port_key} inválida no .env.") from exc

    return user, host, port, password


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Executa comandos SSH no VPS usando credenciais lidas do .env."
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Caminho para o arquivo .env com <PREFIX>_HOST, <PREFIX>_PORT, <PREFIX>_USER e <PREFIX>_PASSWORD.",
    )
    parser.add_argument(
        "--prefix",
        default="VPS_SSH",
        help="Prefixo das variáveis de conexão no .env. Padrão: VPS_SSH (Hostinger). "
        "Use VPS_HOSTGATOR_SSH para a caixa da HostGator.",
    )
    parser.add_argument(
        "--cmd",
        action="append",
        dest="commands",
        help="Comando remoto a executar. Pode ser informado várias vezes.",
    )
    parser.add_argument(
        "--script-file",
        help="Arquivo texto com um comando remoto por linha. Linhas vazias e comentários são ignorados.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout em segundos para cada comando remoto.",
    )
    return parser


def load_commands(args: argparse.Namespace) -> list[str]:
    commands: list[str] = []

    if args.script_file:
        script_path = Path(args.script_file)
        commands.extend(
            line.strip()
            for line in script_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        )

    if args.commands:
        commands.extend(args.commands)

    if not commands:
        raise SystemExit("Informe pelo menos um comando com --cmd ou --script-file.")

    return commands


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    env_path = Path(args.env_file)
    if not env_path.exists():
        raise SystemExit(f"Arquivo .env não encontrado: {env_path}")

    commands = load_commands(args)
    user, host, port, password = parse_env(env_path, args.prefix)

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
        for command in commands:
            print(f"===== CMD: {command} =====")
            stdin, stdout, stderr = client.exec_command(command, timeout=args.timeout)
            output = stdout.read().decode("utf-8", errors="replace")
            error_output = stderr.read().decode("utf-8", errors="replace")
            if output.strip():
                print(output.rstrip())
            if error_output.strip():
                print("--- STDERR ---")
                print(error_output.rstrip())
            print()
    finally:
        client.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
