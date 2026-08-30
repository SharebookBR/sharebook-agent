#!/usr/bin/env python3
"""Send a Telegram message through the configured OpenClaw channel."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Any


TELEGRAM_DIRECT_RE = re.compile(r"^agent:[^:]+:telegram:direct:(?P<target>.+)$")


def run_openclaw(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["openclaw", *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def find_recent_telegram_target(limit: int) -> str:
    result = run_openclaw(["sessions", "--json", "--limit", str(limit)])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())

    try:
        payload: dict[str, Any] = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Could not parse OpenClaw sessions JSON: {exc}") from exc

    for session in payload.get("sessions", []):
        key = str(session.get("key", ""))
        match = TELEGRAM_DIRECT_RE.match(key)
        if match:
            return match.group("target")

    raise RuntimeError(
        "No Telegram direct session found. Pass --target or set OPENCLAW_TELEGRAM_TARGET."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Send a Telegram message using OpenClaw's configured Telegram channel.",
    )
    parser.add_argument("message", help="Message text to send.")
    parser.add_argument(
        "-t",
        "--target",
        default=os.environ.get("OPENCLAW_TELEGRAM_TARGET"),
        help="Telegram chat id or @username. Defaults to OPENCLAW_TELEGRAM_TARGET, then latest direct Telegram session.",
    )
    parser.add_argument(
        "--account",
        help="Optional OpenClaw channel account id.",
    )
    parser.add_argument(
        "--limit",
        default=100,
        type=int,
        help="How many recent sessions to inspect when auto-detecting target.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the OpenClaw payload without sending.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    target = args.target or find_recent_telegram_target(args.limit)

    command = [
        "message",
        "send",
        "--channel",
        "telegram",
        "--target",
        target,
        "--message",
        args.message,
        "--json",
    ]
    if args.account:
        command.extend(["--account", args.account])
    if args.dry_run:
        command.append("--dry-run")

    result = run_openclaw(command)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
