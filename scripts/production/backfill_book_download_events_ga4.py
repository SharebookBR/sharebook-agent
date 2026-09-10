#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Filter, FilterExpression, Metric, RunReportRequest
from google.api_core.exceptions import InvalidArgument
from google.oauth2 import service_account
from psycopg2.extras import execute_values

sys.path.append(str(Path(__file__).resolve().parent))
from prod_env import load_env, pg_rw  # noqa: E402

SOURCE_GA4_BACKFILL = 2


def build_ga4_client() -> BetaAnalyticsDataClient:
    load_env()

    key_path = os.getenv("GA4_KEY_FILE_PATH")
    if key_path and Path(key_path).exists():
        return BetaAnalyticsDataClient.from_service_account_json(key_path)

    credentials_base64 = os.getenv("GA4__CredentialsBase64")
    if not credentials_base64:
        raise SystemExit("Configure GA4_KEY_FILE_PATH ou GA4__CredentialsBase64 no .env.")

    info = json.loads(base64.b64decode(credentials_base64).decode("utf-8"))
    credentials = service_account.Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )
    return BetaAnalyticsDataClient(credentials=credentials)


def fetch_downloads(
    client: BetaAnalyticsDataClient,
    property_id: str,
    start: date,
    end: date,
    slug_dimension: str,
) -> dict[tuple[date, str], int]:
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start.isoformat(), end_date=end.isoformat())],
        dimensions=[
            Dimension(name="date"),
            Dimension(name=slug_dimension),
        ],
        metrics=[Metric(name="eventCount")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(value="ebook_download"),
            )
        ),
        limit=10000,
    )

    response = client.run_report(request)
    downloads: dict[tuple[date, str], int] = defaultdict(int)

    for row in response.rows:
        raw_date = row.dimension_values[0].value
        slug = row.dimension_values[1].value.strip()
        if slug_dimension == "pagePath":
            slug = slug.rstrip("/").split("/")[-1]
        if not slug or slug == "(not set)":
            continue

        day = date(int(raw_date[0:4]), int(raw_date[4:6]), int(raw_date[6:8]))
        downloads[(day, slug)] += int(row.metric_values[0].value)

    return dict(downloads)


def fetch_downloads_with_fallback(
    client: BetaAnalyticsDataClient,
    property_id: str,
    start: date,
    end: date,
) -> tuple[dict[tuple[date, str], int], str]:
    try:
        return fetch_downloads(client, property_id, start, end, "customEvent:book_slug"), "customEvent:book_slug"
    except InvalidArgument:
        return fetch_downloads(client, property_id, start, end, "pagePath"), "pagePath"


def resolve_books(conn, slugs: set[str]) -> dict[str, str]:
    if not slugs:
        return {}

    with conn.cursor() as cur:
        cur.execute(
            'select "Slug", "Id" from "Books" where "Slug" = any(%s)',
            (list(slugs),),
        )
        return {slug: str(book_id) for slug, book_id in cur.fetchall()}


def distributed_timestamp(day: date, index: int, total: int) -> datetime:
    if total <= 1:
        return datetime.combine(day, time(hour=12), timezone.utc)

    seconds = int(((index + 1) / (total + 1)) * 86400)
    return datetime.combine(day, time.min, timezone.utc) + timedelta(seconds=seconds)


def build_rows(downloads: dict[tuple[date, str], int], books_by_slug: dict[str, str]) -> tuple[list[tuple], dict[str, int]]:
    rows: list[tuple] = []
    missing: dict[str, int] = defaultdict(int)

    for (day, slug), count in sorted(downloads.items()):
        book_id = books_by_slug.get(slug)
        if not book_id:
            missing[slug] += count
            continue

        for index in range(count):
            downloaded_at = distributed_timestamp(day, index, count)
            rows.append((str(uuid4()), book_id, None, downloaded_at, SOURCE_GA4_BACKFILL, downloaded_at))

    return rows, dict(missing)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Backfill idempotente de BookDownloadEvents a partir do GA4 ebook_download."
    )
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--yes", action="store_true", help="Confirma escrita em produção.")
    args = parser.parse_args()

    if args.days <= 0:
        raise SystemExit("--days deve ser maior que zero.")

    end = date.today()
    start = end - timedelta(days=args.days - 1)

    load_env()
    property_id = os.getenv("GA4_PROPERTY_ID")
    if not property_id:
        raise SystemExit("Variável obrigatória ausente no .env: GA4_PROPERTY_ID")

    client = build_ga4_client()
    downloads, dimension = fetch_downloads_with_fallback(client, property_id, start, end)

    with pg_rw() as conn:
        books_by_slug = resolve_books(conn, {slug for _, slug in downloads})
        rows, missing = build_rows(downloads, books_by_slug)

        print(f"Período: {start.isoformat()} até {end.isoformat()} UTC")
        print(f"Dimensão usada: {dimension}")
        print(f"Slugs GA4: {len({slug for _, slug in downloads})}")
        print(f"Eventos a inserir: {len(rows)}")
        if missing:
            print(f"Downloads ignorados por slug ausente no banco: {sum(missing.values())}")
            for slug, count in sorted(missing.items(), key=lambda item: item[1], reverse=True)[:20]:
                print(f"  {count:>4} {slug}")

        if args.dry_run:
            return 0

        if not args.yes:
            raise SystemExit("Use --yes para escrever em produção, ou --dry-run para simular.")

        start_at = datetime.combine(start, time.min, timezone.utc)
        end_exclusive = datetime.combine(end + timedelta(days=1), time.min, timezone.utc)

        with conn.cursor() as cur:
            cur.execute(
                '''
                delete from "BookDownloadEvents"
                 where "Source" = %s
                   and "DownloadedAtUtc" >= %s
                   and "DownloadedAtUtc" < %s
                ''',
                (SOURCE_GA4_BACKFILL, start_at, end_exclusive),
            )
            deleted = cur.rowcount

            if rows:
                execute_values(
                    cur,
                    '''
                    insert into "BookDownloadEvents"
                        ("Id", "BookId", "UserId", "DownloadedAtUtc", "Source", "CreationDate")
                    values %s
                    ''',
                    rows,
                    page_size=1000,
                )

        conn.commit()
        print(f"Eventos Ga4Backfill removidos no intervalo: {deleted}")
        print(f"Eventos Ga4Backfill inseridos: {len(rows)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
