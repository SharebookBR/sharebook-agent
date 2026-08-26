#!/usr/bin/env python3
"""Read-only Search Console exploration for the Sharebook domain property."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


DEFAULT_SITE_URL = "sc-domain:sharebook.com.br"
READONLY_SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"
API_BASE_URL = "https://www.googleapis.com/webmasters/v3"
MAX_PAGE_SIZE = 25_000

ALLOWED_DIMENSIONS = {
    "country",
    "date",
    "device",
    "hour",
    "page",
    "query",
    "searchAppearance",
}
ALLOWED_FILTER_OPERATORS = {
    "contains",
    "equals",
    "notContains",
    "notEquals",
    "includingRegex",
    "excludingRegex",
}
ALLOWED_SEARCH_TYPES = {"web", "image", "video", "news", "discover", "googleNews"}


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def default_key_file() -> Path:
    configured = os.environ.get("GA4_KEY_FILE_PATH")
    if configured:
        return Path(configured).expanduser().resolve()
    return repository_root() / "scripts" / "production" / "ga4-key.json"


def authorized_session(key_file: Path) -> AuthorizedSession:
    if not key_file.is_file():
        raise RuntimeError(
            f"Credencial não encontrada em {key_file}. "
            "Use --key-file ou configure GA4_KEY_FILE_PATH."
        )
    credentials = service_account.Credentials.from_service_account_file(
        str(key_file), scopes=[READONLY_SCOPE]
    )
    return AuthorizedSession(credentials)


def api_json(
    session: AuthorizedSession,
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    response = session.request(method, url, json=payload, timeout=60)
    if response.ok:
        return response.json()

    detail = response.text[:500]
    try:
        detail = response.json().get("error", {}).get("message", detail)
    except ValueError:
        pass
    raise RuntimeError(f"Search Console API respondeu HTTP {response.status_code}: {detail}")


def parse_iso_date(raw: str) -> date:
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use datas no formato YYYY-MM-DD.") from exc


def parse_dimensions(raw: str) -> list[str]:
    dimensions = [item.strip() for item in raw.split(",") if item.strip()]
    invalid = [item for item in dimensions if item not in ALLOWED_DIMENSIONS]
    if invalid:
        allowed = ", ".join(sorted(ALLOWED_DIMENSIONS))
        raise argparse.ArgumentTypeError(
            f"Dimensão inválida: {', '.join(invalid)}. Permitidas: {allowed}."
        )
    if len(dimensions) != len(set(dimensions)):
        raise argparse.ArgumentTypeError("Não repita a mesma dimensão.")
    return dimensions


def nth_weekday(year: int, month: int, weekday: int, occurrence: int) -> date:
    first = date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    return first + timedelta(days=offset + 7 * (occurrence - 1))


def pacific_today() -> date:
    """Return the current Pacific date without requiring the tzdata package."""
    now_utc = datetime.now(timezone.utc)
    dst_start_day = nth_weekday(now_utc.year, 3, 6, 2)
    dst_end_day = nth_weekday(now_utc.year, 11, 6, 1)
    dst_start_utc = datetime.combine(
        dst_start_day, datetime.min.time(), timezone.utc
    ) + timedelta(hours=10)
    dst_end_utc = datetime.combine(
        dst_end_day, datetime.min.time(), timezone.utc
    ) + timedelta(hours=9)
    offset_hours = -7 if dst_start_utc <= now_utc < dst_end_utc else -8
    return now_utc.astimezone(timezone(timedelta(hours=offset_hours))).date()


def resolve_period(args: argparse.Namespace) -> tuple[date, date]:
    if bool(args.start_date) != bool(args.end_date):
        raise RuntimeError("Informe --start-date e --end-date juntos.")
    if args.start_date and args.end_date:
        if args.start_date > args.end_date:
            raise RuntimeError("--start-date deve ser anterior ou igual a --end-date.")
        return args.start_date, args.end_date
    if args.days < 1:
        raise RuntimeError("--days deve ser maior que zero.")
    if args.lag_days < 0:
        raise RuntimeError("--lag-days não pode ser negativo.")

    today_pacific = pacific_today()
    end = today_pacific - timedelta(days=args.lag_days)
    start = end - timedelta(days=args.days - 1)
    return start, end


def previous_period(start: date, end: date) -> tuple[date, date]:
    length = (end - start).days + 1
    previous_end = start - timedelta(days=1)
    return previous_end - timedelta(days=length - 1), previous_end


def dimension_filters(raw_filters: list[list[str]] | None) -> list[dict[str, str]]:
    filters: list[dict[str, str]] = []
    for dimension, operator, expression in raw_filters or []:
        if dimension not in ALLOWED_DIMENSIONS - {"date", "hour"}:
            raise RuntimeError(f"Dimensão de filtro inválida: {dimension}.")
        if operator not in ALLOWED_FILTER_OPERATORS:
            raise RuntimeError(f"Operador de filtro inválido: {operator}.")
        filters.append(
            {"dimension": dimension, "operator": operator, "expression": expression}
        )
    return filters


def query_payload(
    start: date,
    end: date,
    dimensions: list[str],
    args: argparse.Namespace,
    start_row: int,
    row_limit: int,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "dimensions": dimensions,
        "type": args.search_type,
        "aggregationType": args.aggregation_type,
        "dataState": args.data_state,
        "startRow": start_row,
        "rowLimit": row_limit,
    }
    filters = dimension_filters(args.filter)
    if filters:
        payload["dimensionFilterGroups"] = [{"groupType": "and", "filters": filters}]
    return payload


def normalized_row(row: dict[str, Any], dimensions: list[str]) -> dict[str, Any]:
    result = dict(zip(dimensions, row.get("keys", [])))
    result.update(
        {
            "clicks": float(row.get("clicks", 0)),
            "impressions": float(row.get("impressions", 0)),
            "ctr": float(row.get("ctr", 0)),
            "position": float(row.get("position", 0)),
        }
    )
    return result


def fetch_rows(
    session: AuthorizedSession,
    site_url: str,
    start: date,
    end: date,
    dimensions: list[str],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    encoded_site = quote(site_url, safe="")
    url = f"{API_BASE_URL}/sites/{encoded_site}/searchAnalytics/query"
    rows: list[dict[str, Any]] = []
    start_row = 0

    while len(rows) < args.max_rows:
        page_size = min(MAX_PAGE_SIZE, args.max_rows - len(rows))
        payload = query_payload(start, end, dimensions, args, start_row, page_size)
        response = api_json(session, "POST", url, payload)
        page = response.get("rows", [])
        if not page:
            break
        rows.extend(normalized_row(row, dimensions) for row in page)
        start_row += len(page)
        if len(page) < page_size:
            break

    return rows


def percentage_change(current: float, previous: float) -> float | None:
    if previous == 0:
        return None
    return (current - previous) / previous * 100


def comparison_rows(
    current: list[dict[str, Any]],
    previous: list[dict[str, Any]],
    dimensions: list[str],
) -> list[dict[str, Any]]:
    def key_for(row: dict[str, Any]) -> tuple[Any, ...]:
        return tuple(row.get(dimension) for dimension in dimensions)

    current_by_key = {key_for(row): row for row in current}
    previous_by_key = {key_for(row): row for row in previous}
    compared: list[dict[str, Any]] = []

    for key in current_by_key.keys() | previous_by_key.keys():
        current_row = current_by_key.get(key, {})
        previous_row = previous_by_key.get(key, {})
        current_clicks = float(current_row.get("clicks", 0))
        previous_clicks = float(previous_row.get("clicks", 0))
        current_impressions = float(current_row.get("impressions", 0))
        previous_impressions = float(previous_row.get("impressions", 0))
        current_ctr = float(current_row.get("ctr", 0))
        previous_ctr = float(previous_row.get("ctr", 0))
        current_position = current_row.get("position")
        previous_position = previous_row.get("position")

        item = {dimension: key[index] for index, dimension in enumerate(dimensions)}
        item.update(
            {
                "currentClicks": current_clicks,
                "previousClicks": previous_clicks,
                "clickDelta": current_clicks - previous_clicks,
                "clickChangePercent": percentage_change(current_clicks, previous_clicks),
                "currentImpressions": current_impressions,
                "previousImpressions": previous_impressions,
                "impressionDelta": current_impressions - previous_impressions,
                "impressionChangePercent": percentage_change(
                    current_impressions, previous_impressions
                ),
                "currentCtr": current_ctr,
                "previousCtr": previous_ctr,
                "ctrChangePercentagePoints": (current_ctr - previous_ctr) * 100,
                "currentPosition": current_position,
                "previousPosition": previous_position,
                "positionChange": (
                    float(previous_position) - float(current_position)
                    if current_position is not None and previous_position is not None
                    else None
                ),
            }
        )
        compared.append(item)

    return compared


def sort_comparison(rows: list[dict[str, Any]], sort_by: str) -> None:
    rows.sort(key=lambda row: abs(float(row.get(sort_by) or 0)), reverse=True)


def emit_rows(rows: list[dict[str, Any]], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return
    if not rows:
        print("Nenhuma linha encontrada.")
        return

    fieldnames = list(rows[0].keys())
    if output_format == "csv":
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        return

    widths = {
        field: min(60, max(len(field), *(len(str(row.get(field, ""))) for row in rows)))
        for field in fieldnames
    }
    print(" | ".join(field.ljust(widths[field]) for field in fieldnames))
    print("-+-".join("-" * widths[field] for field in fieldnames))
    for row in rows:
        values = []
        for field in fieldnames:
            value = str(row.get(field, ""))
            if len(value) > widths[field]:
                value = value[: widths[field] - 1] + "…"
            values.append(value.ljust(widths[field]))
        print(" | ".join(values))


def emit_document(document: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(document, ensure_ascii=False, indent=2))
        return
    emit_rows(document.get("rows", []), output_format)


def common_query_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--site-url", default=DEFAULT_SITE_URL)
    parser.add_argument("--key-file", type=Path, default=default_key_file())
    parser.add_argument("--start-date", type=parse_iso_date)
    parser.add_argument("--end-date", type=parse_iso_date)
    parser.add_argument("--days", type=int, default=28)
    parser.add_argument("--lag-days", type=int, default=3)
    parser.add_argument("--search-type", choices=sorted(ALLOWED_SEARCH_TYPES), default="web")
    parser.add_argument(
        "--aggregation-type",
        choices=["auto", "byPage", "byProperty"],
        default="auto",
    )
    parser.add_argument("--data-state", choices=["final", "all"], default="final")
    parser.add_argument("--max-rows", type=int, default=25_000)
    parser.add_argument(
        "--filter",
        action="append",
        nargs=3,
        metavar=("DIMENSION", "OPERATOR", "EXPRESSION"),
        help="Filtro AND repetível, por exemplo: --filter page contains /livros/",
    )
    parser.add_argument("--format", choices=["json", "csv", "table"], default="json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Exploração read-only do Google Search Console do Sharebook."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sites = subparsers.add_parser("sites", help="Lista propriedades visíveis à service account.")
    sites.add_argument("--key-file", type=Path, default=default_key_file())
    sites.add_argument("--format", choices=["json", "csv", "table"], default="json")

    overview = subparsers.add_parser("overview", help="Compara o agregado com a janela anterior.")
    common_query_arguments(overview)

    query = subparsers.add_parser("query", help="Consulta dimensões arbitrárias.")
    common_query_arguments(query)
    query.add_argument("--dimensions", type=parse_dimensions, required=True)
    query.add_argument("--compare", action="store_true")
    query.add_argument(
        "--sort",
        choices=["currentImpressions", "clickDelta", "impressionDelta", "positionChange"],
        default="currentImpressions",
    )

    opportunities = subparsers.add_parser(
        "opportunities", help="Prioriza combinações query + página com CTR baixo."
    )
    common_query_arguments(opportunities)
    opportunities.set_defaults(max_rows=25_000)
    opportunities.add_argument("--min-impressions", type=float, default=20)
    opportunities.add_argument("--target-ctr", type=float, default=0.05)
    opportunities.add_argument("--min-position", type=float, default=1)
    opportunities.add_argument("--max-position", type=float, default=20)
    opportunities.add_argument("--top", type=int, default=10)

    return parser


def run_sites(args: argparse.Namespace) -> None:
    session = authorized_session(args.key_file)
    response = api_json(session, "GET", f"{API_BASE_URL}/sites")
    rows = [
        {
            "siteUrl": item.get("siteUrl"),
            "permissionLevel": item.get("permissionLevel"),
        }
        for item in response.get("siteEntry", [])
    ]
    emit_rows(rows, args.format)


def run_overview(args: argparse.Namespace) -> None:
    if args.max_rows < 1:
        raise RuntimeError("--max-rows deve ser maior que zero.")
    start, end = resolve_period(args)
    previous_start, previous_end = previous_period(start, end)
    session = authorized_session(args.key_file)
    current = fetch_rows(session, args.site_url, start, end, [], args)
    previous = fetch_rows(session, args.site_url, previous_start, previous_end, [], args)
    rows = comparison_rows(current, previous, [])
    emit_document(
        {
            "siteUrl": args.site_url,
            "currentPeriod": {"start": start.isoformat(), "end": end.isoformat()},
            "previousPeriod": {
                "start": previous_start.isoformat(),
                "end": previous_end.isoformat(),
            },
            "rows": rows,
        },
        args.format,
    )


def run_query(args: argparse.Namespace) -> None:
    if args.max_rows < 1:
        raise RuntimeError("--max-rows deve ser maior que zero.")
    start, end = resolve_period(args)
    session = authorized_session(args.key_file)
    current = fetch_rows(session, args.site_url, start, end, args.dimensions, args)

    if not args.compare:
        emit_document(
            {
                "siteUrl": args.site_url,
                "period": {"start": start.isoformat(), "end": end.isoformat()},
                "dimensions": args.dimensions,
                "rows": current,
            },
            args.format,
        )
        return

    previous_start, previous_end = previous_period(start, end)
    previous = fetch_rows(
        session, args.site_url, previous_start, previous_end, args.dimensions, args
    )
    rows = comparison_rows(current, previous, args.dimensions)
    sort_comparison(rows, args.sort)
    emit_document(
        {
            "siteUrl": args.site_url,
            "currentPeriod": {"start": start.isoformat(), "end": end.isoformat()},
            "previousPeriod": {
                "start": previous_start.isoformat(),
                "end": previous_end.isoformat(),
            },
            "dimensions": args.dimensions,
            "rows": rows,
        },
        args.format,
    )


def run_opportunities(args: argparse.Namespace) -> None:
    if args.max_rows < 1 or args.top < 1:
        raise RuntimeError("--max-rows e --top devem ser maiores que zero.")
    if not 0 < args.target_ctr <= 1:
        raise RuntimeError("--target-ctr deve ser uma fração entre 0 e 1.")
    if args.min_position > args.max_position:
        raise RuntimeError("--min-position não pode superar --max-position.")

    start, end = resolve_period(args)
    session = authorized_session(args.key_file)
    rows = fetch_rows(session, args.site_url, start, end, ["query", "page"], args)
    opportunities = []
    for row in rows:
        if row["impressions"] < args.min_impressions:
            continue
        if row["ctr"] >= args.target_ctr:
            continue
        if not args.min_position <= row["position"] <= args.max_position:
            continue
        opportunities.append(
            {
                **row,
                "missedClicksAtTargetCtr": round(
                    row["impressions"] * (args.target_ctr - row["ctr"]), 2
                ),
            }
        )

    opportunities.sort(key=lambda row: row["missedClicksAtTargetCtr"], reverse=True)
    emit_document(
        {
            "siteUrl": args.site_url,
            "period": {"start": start.isoformat(), "end": end.isoformat()},
            "criteria": {
                "minImpressions": args.min_impressions,
                "targetCtr": args.target_ctr,
                "minPosition": args.min_position,
                "maxPosition": args.max_position,
            },
            "rows": opportunities[: args.top],
        },
        args.format,
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "sites":
            run_sites(args)
        elif args.command == "overview":
            run_overview(args)
        elif args.command == "query":
            run_query(args)
        elif args.command == "opportunities":
            run_opportunities(args)
        return 0
    except (RuntimeError, OSError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
