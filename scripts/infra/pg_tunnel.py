#!/usr/bin/env python3
"""Tunel SSH do Windows local ate o Postgres de producao dentro da VPS.

Por que existe:
    O Coolify tem um toggle que expoe (ou nao) o Postgres na internet. Quando ele esta
    desligado - que e a postura mais segura e o default depois da migracao de 2026-08-17 -
    a porta 5432 simplesmente nao e publicada no host e qualquer conexao direta do Windows
    morre com "Connection refused". O container continua sadio; o app o alcanca pela rede
    interna do Docker.

    Este script da acesso sem precisar reabrir a porta para a internet: usa o SSH que ja
    temos, descobre o IP interno do container e encaminha uma porta local ate ele. Nao
    altera nada no servidor.

Uso:
    python scripts/infra/pg_tunnel.py                 # 127.0.0.1:15432 -> container:5432
    python scripts/infra/pg_tunnel.py --local-port 25432
    python scripts/infra/pg_tunnel.py --container coolify-db

    Deixe rodando em um terminal. Em outro, aponte o DSN para o tunel. O CLI do importer
    usa os.environ.setdefault, entao a variavel exportada vence o .env:

        export IMPORTER_DB_DSN="postgresql://user:pass@127.0.0.1:15432/sharebook_importer"
        python cli.py publish-once --id <ID>

Ctrl+C encerra. Credenciais vem de sharebook-agent/.env - nunca hardcode.
"""

from __future__ import annotations

import argparse
import select
import socketserver
import sys
from pathlib import Path

import paramiko
from dotenv import load_dotenv
import os

ENV_PATH = Path(r"C:\Repos\SHAREBOOK\sharebook-agent\.env")
# Container do Postgres das aplicacoes (nome-hash gerado pelo Coolify).
DEFAULT_CONTAINER = "fgsgwsckccgk8sccc4gg0gg0"
DEFAULT_PREFIX = "VPS_HOSTGATOR_SSH"


def ssh_credentials(prefix: str) -> tuple[str, int, str, str]:
    load_dotenv(ENV_PATH)
    host = os.getenv(f"{prefix}_HOST")
    user = os.getenv(f"{prefix}_USER")
    password = os.getenv(f"{prefix}_PASSWORD")
    port = int(os.getenv(f"{prefix}_PORT") or 22)
    missing = [k for k, v in (("HOST", host), ("USER", user), ("PASSWORD", password)) if not v]
    if missing:
        raise SystemExit(f"Faltam no .env: {', '.join(f'{prefix}_{m}' for m in missing)}")
    return host, port, user, password


def container_ip(client: paramiko.SSHClient, container: str) -> str:
    cmd = ("docker inspect -f "
           "'{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}' " + container)
    _, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode(errors="replace").split()
    if not out:
        err = stderr.read().decode(errors="replace").strip()
        raise SystemExit(f"Nao achei o IP do container '{container}'. docker inspect disse: {err}")
    return out[0]


class Forwarder(socketserver.BaseRequestHandler):
    transport: paramiko.Transport
    remote: tuple[str, int]

    def handle(self) -> None:
        try:
            channel = self.transport.open_channel(
                "direct-tcpip", self.remote, self.request.getpeername()
            )
        except Exception as exc:
            print(f"  canal recusado: {exc}", file=sys.stderr, flush=True)
            return
        if channel is None:
            return
        try:
            while True:
                readable, _, _ = select.select([self.request, channel], [], [], 5)
                if self.request in readable:
                    data = self.request.recv(65536)
                    if not data:
                        break
                    channel.sendall(data)
                if channel in readable:
                    data = channel.recv(65536)
                    if not data:
                        break
                    self.request.sendall(data)
        finally:
            channel.close()
            self.request.close()


class ThreadedServer(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


def main() -> None:
    parser = argparse.ArgumentParser(description="Tunel SSH ate o Postgres da VPS")
    parser.add_argument("--local-port", type=int, default=15432)
    parser.add_argument("--remote-port", type=int, default=5432)
    parser.add_argument("--container", default=DEFAULT_CONTAINER,
                        help=f"Container do Postgres (default: {DEFAULT_CONTAINER})")
    parser.add_argument("--prefix", default=DEFAULT_PREFIX,
                        help=f"Prefixo das credenciais SSH no .env (default: {DEFAULT_PREFIX})")
    args = parser.parse_args()

    host, port, user, password = ssh_credentials(args.prefix)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port=port, username=user, password=password, timeout=30)

    ip = container_ip(client, args.container)
    Forwarder.transport = client.get_transport()
    Forwarder.remote = (ip, args.remote_port)

    server = ThreadedServer(("127.0.0.1", args.local_port), Forwarder)
    print(f"tunel pronto: 127.0.0.1:{args.local_port} -> {ip}:{args.remote_port} "
          f"(container {args.container} via {host})", flush=True)
    print("Ctrl+C para encerrar.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nencerrando.")
    finally:
        server.shutdown()
        client.close()


if __name__ == "__main__":
    main()
