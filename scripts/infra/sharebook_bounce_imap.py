#!/usr/bin/env python3
from __future__ import annotations

import argparse
import email
import imaplib
import re
import select
import socket
import ssl
import sys
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from email.message import Message
from pathlib import Path
from typing import Iterator

SCRIPT_DIR = Path(__file__).resolve().parent
LIB_DIR = SCRIPT_DIR.parent / "lib"
PRODUCTION_DIR = SCRIPT_DIR.parent / "production"
sys.path.insert(0, str(LIB_DIR))
sys.path.insert(0, str(PRODUCTION_DIR))

from prod_env import pg_rw  # noqa: E402
from sharebook_env import load_env, require_env  # noqa: E402


REQUIRED_IMAP_ENV = [
    "SHAREBOOK_BOUNCE_IMAP_HOST",
    "SHAREBOOK_BOUNCE_IMAP_PORT",
    "SHAREBOOK_BOUNCE_IMAP_USERNAME",
    "SHAREBOOK_BOUNCE_IMAP_PASSWORD",
    "SHAREBOOK_BOUNCE_IMAP_FOLDER",
]

VPS_ENV = [
    "VPS_HOSTGATOR_SSH_HOST",
    "VPS_HOSTGATOR_SSH_USER",
    "VPS_HOSTGATOR_SSH_PASSWORD",
]


@dataclass(frozen=True)
class BounceCandidate:
    uid: str
    subject: str
    email: str
    error_code: str
    is_soft: bool
    is_bounce: bool
    body: str


def bool_env(value: str | None, default: bool = True) -> bool:
    if value is None or value == "":
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


def mask_email(value: str) -> str:
    if "@" not in value:
        return value
    local, domain = value.split("@", 1)
    if len(local) <= 2:
        local_mask = local[:1] + "*"
    else:
        local_mask = local[:2] + "*" * min(6, len(local) - 2)
    return f"{local_mask}@{domain}"


def forward_until_close(server: socket.socket, transport: object, target_host: str, target_port: int) -> None:
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
def imap_connection(env: dict[str, str], timeout: int) -> Iterator[imaplib.IMAP4_SSL]:
    host = env["SHAREBOOK_BOUNCE_IMAP_HOST"]
    port = int(env["SHAREBOOK_BOUNCE_IMAP_PORT"])
    tls_verify = bool_env(env.get("SHAREBOOK_BOUNCE_IMAP_TLS_VERIFY"), default=True)
    via_vps = bool_env(env.get("SHAREBOOK_BOUNCE_IMAP_VIA_VPS"), default=False)

    context = ssl.create_default_context()
    if not tls_verify:
        context = ssl._create_unverified_context()

    if not via_vps:
        with imaplib.IMAP4_SSL(host=host, port=port, ssl_context=context, timeout=timeout) as client:
            yield client
        return

    try:
        import paramiko
    except ImportError as exc:
        raise SystemExit("paramiko nao esta instalado; necessario para SHAREBOOK_BOUNCE_IMAP_VIA_VPS=true.") from exc

    require_env(env, VPS_ENV)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=env["VPS_HOSTGATOR_SSH_HOST"],
        port=int(env.get("VPS_HOSTGATOR_SSH_PORT") or 22),
        username=env["VPS_HOSTGATOR_SSH_USER"],
        password=env["VPS_HOSTGATOR_SSH_PASSWORD"],
        timeout=15,
        banner_timeout=15,
        auth_timeout=15,
    )
    try:
        transport = ssh.get_transport()
        if transport is None:
            raise SystemExit("Falha ao abrir transporte SSH para a VPS.")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        local_host, local_port = server.getsockname()
        thread = threading.Thread(
            target=forward_until_close,
            args=(server, transport, host, port),
            daemon=True,
        )
        thread.start()
        with imaplib.IMAP4_SSL(host=local_host, port=local_port, ssl_context=context, timeout=timeout) as client:
            yield client
    finally:
        ssh.close()


def message_text(message: Message) -> str:
    if message.is_multipart():
        parts: list[str] = []
        for part in message.walk():
            if part.get_content_maintype() == "multipart":
                continue
            content_type = part.get_content_type()
            if content_type not in {"text/plain", "text/html", "message/delivery-status"}:
                continue
            payload = part.get_payload(decode=True)
            if payload is None:
                raw = part.get_payload()
                if isinstance(raw, str):
                    parts.append(raw)
                continue
            charset = part.get_content_charset() or "utf-8"
            parts.append(payload.decode(charset, errors="replace"))
        return "\n".join(parts)

    payload = message.get_payload(decode=True)
    if payload is None:
        raw = message.get_payload()
        return raw if isinstance(raw, str) else ""
    charset = message.get_content_charset() or "utf-8"
    return payload.decode(charset, errors="replace")


def parse_bounce(uid: str, raw_message: bytes) -> BounceCandidate:
    message = email.message_from_bytes(raw_message)
    subject = str(email.header.make_header(email.header.decode_header(message.get("Subject", ""))))
    body = message_text(message)

    email_match = re.search(r"\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*", body)
    original_email = email_match.group(0) if email_match else ""

    code_match = re.search(r"Remote\s+Server\s+returned\s*:?\s*'?(?P<code>[45]\d{2})", body, re.IGNORECASE)
    if not code_match:
        code_match = re.search(r"\bwith code (?P<code>[45]\d{2})\b", body, re.IGNORECASE)

    error_code = code_match.group("code") if code_match else ""
    if not error_code and re.search(r"\bno MX record found\b", body, re.IGNORECASE):
        error_code = "550"
    if not error_code and re.search(r"\b(connection timed out|I/O error)\b", body, re.IGNORECASE):
        error_code = "421"

    is_bounce = bool(error_code)
    return BounceCandidate(
        uid=uid,
        subject=subject,
        email=original_email,
        error_code=error_code,
        is_soft=error_code.startswith("4"),
        is_bounce=is_bounce,
        body=body,
    )


def fetch_candidates(client: imaplib.IMAP4_SSL, folder: str, limit: int | None) -> list[BounceCandidate]:
    status, _ = client.select(folder, readonly=True)
    if status != "OK":
        raise SystemExit(f"Nao foi possivel selecionar a pasta IMAP: {folder}")

    status, data = client.uid("search", None, "ALL")
    if status != "OK":
        raise SystemExit("Falha ao listar UIDs da caixa de bounce.")

    uids = data[0].decode("ascii").split() if data and data[0] else []
    if limit is not None:
        uids = uids[:limit]

    candidates: list[BounceCandidate] = []
    for uid in uids:
        status, fetch_data = client.uid("fetch", uid, "(RFC822)")
        if status != "OK":
            raise SystemExit(f"Falha ao buscar UID {uid}.")
        raw_message = b""
        for item in fetch_data:
            if isinstance(item, tuple) and item[1]:
                raw_message = item[1]
                break
        if not raw_message:
            continue
        candidates.append(parse_bounce(uid, raw_message))
    return candidates


def insert_bounces(candidates: list[BounceCandidate]) -> int:
    rows = [candidate for candidate in candidates if candidate.is_bounce]
    if not rows:
        return 0

    with pg_rw() as conn:
        with conn.cursor() as cur:
            for candidate in rows:
                cur.execute(
                    """
                    insert into "MailBounces"
                        ("Id", "Subject", "Body", "ErrorCode", "IsSoft", "IsBounce", "Email", "CreationDate")
                    values
                        (%s, %s, %s, %s, %s, %s, %s, now())
                    """,
                    (
                        str(uuid.uuid4()),
                        candidate.subject,
                        candidate.body,
                        candidate.error_code,
                        candidate.is_soft,
                        candidate.is_bounce,
                        candidate.email,
                    ),
                )
        conn.commit()
    return len(rows)


def delete_uids(env: dict[str, str], uids: list[str], timeout: int) -> None:
    if not uids:
        return
    folder = env["SHAREBOOK_BOUNCE_IMAP_FOLDER"]
    with imap_connection(env, timeout) as client:
        client.login(env["SHAREBOOK_BOUNCE_IMAP_USERNAME"], env["SHAREBOOK_BOUNCE_IMAP_PASSWORD"])
        status, _ = client.select(folder, readonly=False)
        if status != "OK":
            raise SystemExit(f"Nao foi possivel selecionar a pasta IMAP para escrita: {folder}")
        for uid in uids:
            status, _ = client.uid("store", uid, "+FLAGS", r"(\Deleted)")
            if status != "OK":
                raise SystemExit(f"Falha ao marcar UID {uid} como Deleted.")
        status, _ = client.expunge()
        if status != "OK":
            raise SystemExit("Falha ao executar EXPUNGE na caixa de bounce.")


def print_summary(candidates: list[BounceCandidate], show_emails: bool) -> None:
    total = len(candidates)
    bounces = [candidate for candidate in candidates if candidate.is_bounce]
    non_bounces = [candidate for candidate in candidates if not candidate.is_bounce]
    hard = [candidate for candidate in bounces if not candidate.is_soft]
    soft = [candidate for candidate in bounces if candidate.is_soft]

    print(f"IMAP_MESSAGES={total}")
    print(f"BOUNCE_CANDIDATES={len(bounces)}")
    print(f"HARD_BOUNCES={len(hard)}")
    print(f"SOFT_BOUNCES={len(soft)}")
    print(f"NON_BOUNCES={len(non_bounces)}")

    by_code: dict[str, int] = {}
    for candidate in bounces:
        by_code[candidate.error_code] = by_code.get(candidate.error_code, 0) + 1
    if by_code:
        print("ERROR_CODES=" + ",".join(f"{code}:{count}" for code, count in sorted(by_code.items())))

    for candidate in candidates:
        email_value = candidate.email if show_emails else mask_email(candidate.email)
        print(
            "UID={uid} BOUNCE={bounce} SOFT={soft} CODE={code} EMAIL={email} SUBJECT={subject}".format(
                uid=candidate.uid,
                bounce=str(candidate.is_bounce).lower(),
                soft=str(candidate.is_soft).lower(),
                code=candidate.error_code or "-",
                email=email_value or "-",
                subject=candidate.subject.replace("\n", " ")[:120],
            )
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inventaria e processa bounces IMAP do Stalwart usando SHAREBOOK_BOUNCE_IMAP_* do .env."
    )
    parser.add_argument("--env-file", type=Path, help="Caminho alternativo para o .env canonico.")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout IMAP em segundos.")
    parser.add_argument("--limit", type=int, help="Limita a quantidade de UIDs lidos.")
    parser.add_argument("--show-emails", action="store_true", help="Mostra emails completos na saida.")
    parser.add_argument(
        "--process",
        action="store_true",
        help="Grava bounces no banco e apaga da caixa IMAP apenas os UIDs processados como bounce.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    env = load_env(args.env_file)
    require_env(env, REQUIRED_IMAP_ENV)

    folder = env["SHAREBOOK_BOUNCE_IMAP_FOLDER"]
    with imap_connection(env, args.timeout) as client:
        client.login(env["SHAREBOOK_BOUNCE_IMAP_USERNAME"], env["SHAREBOOK_BOUNCE_IMAP_PASSWORD"])
        candidates = fetch_candidates(client, folder, args.limit)

    print_summary(candidates, show_emails=args.show_emails)

    if not args.process:
        print("DRY_RUN=1")
        return 0

    inserted = insert_bounces(candidates)
    processed_uids = [candidate.uid for candidate in candidates if candidate.is_bounce]
    delete_uids(env, processed_uids, args.timeout)
    print(f"INSERTED_MAIL_BOUNCES={inserted}")
    print(f"DELETED_IMAP_UIDS={len(processed_uids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
