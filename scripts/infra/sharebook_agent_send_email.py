#!/usr/bin/env python3
from __future__ import annotations

import argparse
import select
import smtplib
import socket
import ssl
import sys
import threading
from contextlib import contextmanager
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from pathlib import Path
from typing import Iterator

SCRIPT_DIR = Path(__file__).resolve().parent
LIB_DIR = SCRIPT_DIR.parent / "lib"
sys.path.insert(0, str(LIB_DIR))

from sharebook_env import load_env, require_env  # noqa: E402


REQUIRED_ENV = [
    "SHAREBOOK_AGENT_SMTP_HOST",
    "SHAREBOOK_AGENT_SMTP_PORT",
    "SHAREBOOK_AGENT_SMTP_USERNAME",
    "SHAREBOOK_AGENT_SMTP_PASSWORD",
    "SHAREBOOK_AGENT_SMTP_FROM",
]

VPS_ENV = [
    "VPS_HOSTGATOR_SSH_HOST",
    "VPS_HOSTGATOR_SSH_USER",
    "VPS_HOSTGATOR_SSH_PASSWORD",
]


def split_addresses(values: list[str] | None) -> list[str]:
    if not values:
        return []
    addresses: list[str] = []
    for value in values:
        addresses.extend(item.strip() for item in value.split(",") if item.strip())
    return addresses


def read_body(args: argparse.Namespace) -> str:
    if args.body_file:
        return Path(args.body_file).read_text(encoding="utf-8")
    if args.body is not None:
        return args.body
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit("Informe o corpo com --body, --body-file ou stdin.")


def bool_env(value: str | None, default: bool = True) -> bool:
    if value is None or value == "":
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


def forward_once(server: socket.socket, transport: object, target_host: str, target_port: int) -> None:
    client = None
    channel = None
    try:
        client, _ = server.accept()
        channel = transport.open_channel("direct-tcpip", (target_host, target_port), client.getsockname())
        while True:
            readable, _, _ = select.select([client, channel], [], [], 30)
            if client in readable:
                data = client.recv(16384)
                if not data:
                    break
                channel.sendall(data)
            if channel in readable:
                data = channel.recv(16384)
                if not data:
                    break
                client.sendall(data)
    finally:
        if channel is not None:
            channel.close()
        if client is not None:
            client.close()
        server.close()


@contextmanager
def smtp_connection(
    host: str,
    port: int,
    timeout: int,
    context: ssl.SSLContext,
    env: dict[str, str],
    via_vps: bool,
) -> Iterator[smtplib.SMTP]:
    if not via_vps:
        with smtplib.SMTP_SSL(host=host, port=port, timeout=timeout, context=context) as smtp:
            yield smtp
        return

    try:
        import paramiko
    except ImportError as exc:
        raise SystemExit("paramiko nao esta instalado; necessario para SHAREBOOK_AGENT_SMTP_VIA_VPS=true.") from exc

    require_env(env, VPS_ENV)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=env["VPS_HOSTGATOR_SSH_HOST"],
        port=int(env.get("VPS_HOSTGATOR_SSH_PORT") or 22),
        username=env["VPS_HOSTGATOR_SSH_USER"],
        password=env["VPS_HOSTGATOR_SSH_PASSWORD"],
        timeout=15,
        banner_timeout=15,
        auth_timeout=15,
    )
    try:
        transport = client.get_transport()
        if transport is None:
            raise SystemExit("Falha ao abrir transporte SSH para a VPS.")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        local_host, local_port = server.getsockname()
        thread = threading.Thread(target=forward_once, args=(server, transport, host, port), daemon=True)
        thread.start()
        with smtplib.SMTP_SSL(host=local_host, port=local_port, timeout=timeout, context=context) as smtp:
            yield smtp
    finally:
        client.close()


def build_message(args: argparse.Namespace, env: dict[str, str]) -> tuple[EmailMessage, list[str]]:
    to_addresses = split_addresses(args.to)
    cc_addresses = split_addresses(args.cc)
    bcc_addresses = split_addresses(args.bcc)
    if not to_addresses:
        raise SystemExit("Informe pelo menos um destinatario.")

    from_email = env["SHAREBOOK_AGENT_SMTP_FROM"]
    from_name = args.from_name or env.get("SHAREBOOK_AGENT_SMTP_FROM_NAME") or ""
    domain = from_email.rsplit("@", 1)[-1] if "@" in from_email else "sharebook.com.br"

    message = EmailMessage()
    message["From"] = formataddr((from_name, from_email)) if from_name else from_email
    message["To"] = ", ".join(to_addresses)
    if cc_addresses:
        message["Cc"] = ", ".join(cc_addresses)
    if args.reply_to:
        message["Reply-To"] = args.reply_to
    message["Subject"] = args.subject
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain=domain)

    body = read_body(args)
    if args.html:
        message.set_content(args.alt_text or "Mensagem em HTML.")
        message.add_alternative(body, subtype="html")
    else:
        message.set_content(body)

    recipients = to_addresses + cc_addresses + bcc_addresses
    return message, recipients


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Envia e-mail pelo SMTP proprio do Sharebook/Stalwart usando SHAREBOOK_AGENT_SMTP_* do .env."
    )
    parser.add_argument("to", nargs="+", help="Destinatario(s). Aceita lista separada por espaco ou virgula.")
    parser.add_argument("--subject", required=True, help="Assunto do e-mail.")
    parser.add_argument("--body", help="Corpo do e-mail em texto ou HTML.")
    parser.add_argument("--body-file", help="Arquivo com o corpo do e-mail.")
    parser.add_argument("--html", action="store_true", help="Envia o corpo como HTML.")
    parser.add_argument("--alt-text", help="Texto alternativo quando --html for usado.")
    parser.add_argument("--cc", action="append", help="CC. Pode repetir ou separar por virgula.")
    parser.add_argument("--bcc", action="append", help="BCC. Pode repetir ou separar por virgula.")
    parser.add_argument("--reply-to", help="Endereco Reply-To.")
    parser.add_argument("--envelope-from", help="Endereco SMTP MAIL FROM/Return-Path.")
    parser.add_argument("--from-name", help="Nome exibido no remetente.")
    parser.add_argument("--env-file", type=Path, help="Caminho alternativo para o .env canonico.")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout SMTP em segundos.")
    parser.add_argument("--via-vps", action="store_true", help="Acessa o SMTP por tunel SSH pela VPS HostGator.")
    parser.add_argument("--dry-run", action="store_true", help="Monta a mensagem sem enviar.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    env = load_env(args.env_file)
    require_env(env, REQUIRED_ENV)

    message, recipients = build_message(args, env)
    host = env["SHAREBOOK_AGENT_SMTP_HOST"]
    port = int(env["SHAREBOOK_AGENT_SMTP_PORT"])
    tls_verify = bool_env(env.get("SHAREBOOK_AGENT_SMTP_TLS_VERIFY"), default=True)
    via_vps = args.via_vps or bool_env(env.get("SHAREBOOK_AGENT_SMTP_VIA_VPS"), default=False)
    envelope_from = args.envelope_from or env.get("SHAREBOOK_AGENT_SMTP_ENVELOPE_FROM") or env["SHAREBOOK_AGENT_SMTP_FROM"]

    print(f"SMTP_FROM={env['SHAREBOOK_AGENT_SMTP_FROM']}")
    print(f"SMTP_ENVELOPE_FROM={envelope_from}")
    print(f"SMTP_TO={', '.join(recipients)}")
    print(f"SMTP_SUBJECT={args.subject}")
    print(f"SMTP_MESSAGE_ID={message['Message-ID']}")
    if args.dry_run:
        print("SMTP_DRY_RUN=1")
        return 0

    context = ssl.create_default_context()
    if not tls_verify:
        context = ssl._create_unverified_context()
        print("SMTP_TLS_VERIFY=false")
    if via_vps:
        print("SMTP_VIA_VPS=true")

    with smtp_connection(host, port, args.timeout, context, env, via_vps) as smtp:
        smtp.login(env["SHAREBOOK_AGENT_SMTP_USERNAME"], env["SHAREBOOK_AGENT_SMTP_PASSWORD"])
        smtp.send_message(message, from_addr=envelope_from, to_addrs=recipients)

    print("SMTP_SEND_OK=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
