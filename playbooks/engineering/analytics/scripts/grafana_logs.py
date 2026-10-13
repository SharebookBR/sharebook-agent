#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path

# Resolve shared operational modules after playbook colocation.
_AGENT_ROOT = next((p for p in Path(__file__).resolve().parents if (p / "AGENTS.md").exists()), None)
if _AGENT_ROOT:
    sys.path.insert(0, str(_AGENT_ROOT / "playbooks" / "_shared" / "scripts"))
    sys.path.insert(0, str(_AGENT_ROOT / "playbooks" / "_shared" / "scripts" / "production"))


import argparse
import base64
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from ipaddress import ip_address
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
AGENT_DIR = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(AGENT_DIR / "scripts" / "lib"))

from sharebook_env import load_env, require_env  # noqa: E402

DEFAULT_SERVICE = "sharebook-api"
REQUIRED_ENV = (
    "GRAFANA_CLOUD_LOGS_LOKI_URL",
    "GRAFANA_CLOUD_LOGS_READ_USER",
    "GRAFANA_CLOUD_LOGS_READ_TOKEN",
)


def parse_duration(value: str) -> int:
    match = re.fullmatch(r"(\d+)([smhd])", value.strip().lower())
    if not match:
        raise SystemExit("--since deve usar formato como 30s, 15m, 6h ou 1d")
    amount = int(match.group(1))
    unit = match.group(2)
    factor = {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit]
    return amount * factor


def ns_now() -> int:
    return int(datetime.now(tz=timezone.utc).timestamp() * 1_000_000_000)


def iso_from_ns(value: str) -> str:
    try:
        ts = int(value) / 1_000_000_000
    except ValueError:
        return value
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def classify_ip(value: str | None) -> str:
    if not value:
        return "missing"
    raw = value.split(",", 1)[0].strip()
    if not raw:
        return "missing"
    try:
        parsed = ip_address(raw)
    except ValueError:
        return "invalid"
    if parsed.is_private or parsed.is_loopback or parsed.is_link_local:
        return "private/internal"
    return "public"


def short(value: str | None, limit: int = 90) -> str:
    if not value:
        return "-"
    value = " ".join(str(value).split())
    if len(value) <= limit:
        return value
    return value[: limit - 1] + "…"


def redact_ips(value: str | None) -> str:
    if not value:
        return "-"
    value = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "[ip]", value)
    value = re.sub(r"\b(?:[0-9a-fA-F]{0,4}:){2,}[0-9a-fA-F]{0,4}\b", "[ip]", value)
    return value


def maybe_json(line: str) -> dict[str, Any]:
    try:
        parsed = json.loads(line)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def first_value(*values: Any) -> str | None:
    for value in values:
        if value is not None and value != "":
            return str(value)
    return None


def field(data: dict[str, Any], *names: str) -> str | None:
    for name in names:
        current: Any = data
        for part in name.split("."):
            if not isinstance(current, dict) or part not in current:
                current = None
                break
            current = current[part]
        if current is not None and current != "":
            return str(current)
    return None


def build_query(args: argparse.Namespace) -> str:
    if args.query:
        return args.query
    selectors = [f'service_name="{args.service}"']
    if args.level:
        selectors.append(f'level="{args.level}"')
    query = "{" + ",".join(selectors) + "}"
    filters: list[str] = []
    if args.contains:
        filters.append(json.dumps(args.contains))
    for item in filters:
        query += f" |= {item}"
    return query


def loki_get(env: dict[str, str], query: str, since_seconds: int, limit: int) -> dict[str, Any]:
    end = ns_now()
    start = end - since_seconds * 1_000_000_000
    base = env["GRAFANA_CLOUD_LOGS_LOKI_URL"].rstrip("/")
    params = urllib.parse.urlencode(
        {
            "query": query,
            "start": str(start),
            "end": str(end),
            "limit": str(limit),
            "direction": "backward",
        }
    )
    request = urllib.request.Request(f"{base}/loki/api/v1/query_range?{params}")
    login = f"{env['GRAFANA_CLOUD_LOGS_READ_USER']}:{env['GRAFANA_CLOUD_LOGS_READ_TOKEN']}"
    auth = base64.b64encode(login.encode("utf-8")).decode("ascii")
    request.add_header("Authorization", f"Basic {auth}")
    request.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Loki HTTP {exc.code}: {short(detail, 220)}") from exc


def flatten_results(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for stream in payload.get("data", {}).get("result", []):
        labels = stream.get("stream", {})
        for item in stream.get("values", []):
            ts, line = item[0], item[1]
            metadata = item[2] if len(item) > 2 and isinstance(item[2], dict) else {}
            parsed = maybe_json(line)
            data = {**labels, **metadata, **parsed}
            rows.append({"ts": ts, "line": line, "data": data})
    rows.sort(key=lambda row: row["ts"])
    return rows


def summarize(row: dict[str, Any]) -> dict[str, str]:
    data = row["data"]
    line = row["line"]
    method = field(data, "RequestMethod", "request.method", "http_request_method", "http.request.method")
    path = field(data, "RequestPath", "Path", "path", "url.path", "http_route", "http.route")
    status = field(data, "StatusCode", "http_response_status_code", "http.response.status_code")
    level = first_value(
        field(data, "level", "Level", "severity_text", "SeverityText"),
        "info",
    )
    ua = field(data, "UserAgent", "user_agent", "http.user_agent")
    ip = field(data, "ClientIp", "client_ip", "remote_ip")
    message = field(data, "RenderedMessage", "Message", "message", "body")
    if not message:
        message = line
    return {
        "time": iso_from_ns(row["ts"]),
        "level": short(level, 10),
        "status": short(status, 8),
        "method": short(method, 8),
        "path": short(path, 70),
        "ip": classify_ip(ip),
        "ua": short(ua, 70),
        "msg": short(redact_ips(message), 140),
    }


def client_filter(rows: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    for row in rows:
        item = summarize(row)
        if args.user_agent and args.user_agent not in item["ua"]:
            continue
        if args.route and args.route not in item["path"] and args.route not in item["msg"]:
            continue
        if args.errors:
            try:
                if int(item["status"]) < 500:
                    continue
            except ValueError:
                if " 5" not in item["msg"]:
                    continue
        filtered.append(row)
    return filtered


def print_compact(rows: list[dict[str, Any]]) -> None:
    if not rows:
        print("no logs")
        return
    for row in rows:
        item = summarize(row)
        print(
            f"{item['time']} {item['level']:>7} {item['status']:>3} "
            f"{item['method']:<6} {item['path']:<45} "
            f"ip={item['ip']:<16} ua={item['ua']} :: {item['msg']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Consulta Grafana Cloud Logs/Loki usando o .env canonico, com saida compacta e segura."
    )
    parser.add_argument("--since", default="15m", help="janela relativa: 30s, 15m, 6h, 1d")
    parser.add_argument("--service", default=DEFAULT_SERVICE, help="label service_name")
    parser.add_argument("--contains", help="filtro textual LogQL")
    parser.add_argument("--user-agent", help="filtro textual por User-Agent")
    parser.add_argument("--route", help="filtro textual por rota/path")
    parser.add_argument("--level", help="label level quando existir")
    parser.add_argument("--errors", action="store_true", help="atalho textual para respostas 5xx")
    parser.add_argument("--query", help="LogQL completo; ignora filtros gerados")
    parser.add_argument("--limit", type=int, default=50, help="limite de entradas")
    parser.add_argument("--json", action="store_true", help="saida JSON compacta e sanitizada")
    args = parser.parse_args()

    env = load_env()
    require_env(env, REQUIRED_ENV)
    query = build_query(args)
    fetch_limit = args.limit
    if args.user_agent or args.route or args.errors:
        fetch_limit = min(max(args.limit * 5, 100), 1000)
    payload = loki_get(env, query, parse_duration(args.since), fetch_limit)
    rows = client_filter(flatten_results(payload), args)[-args.limit :]
    if args.json:
        print(json.dumps([summarize(row) for row in rows], ensure_ascii=False, indent=2))
    else:
        print_compact(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
