"""
Uso da busca interna via pagePath /buscar/:criteria — últimos 30 dias
Abordagem canônica para períodos sem evento 'search' registrado.
"""
import sys
from pathlib import Path
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, Dimension, Metric, DateRange,
    FilterExpression, Filter
)

PROPERTY_ID = "386966473"
KEY_PATH = Path(__file__).parent / "ga4-key.json"
START_DATE = "30daysAgo"
END_DATE = "today"


def build_client():
    creds = service_account.Credentials.from_service_account_file(
        str(KEY_PATH),
        scopes=["https://www.googleapis.com/auth/analytics.readonly"]
    )
    return BetaAnalyticsDataClient(credentials=creds)


def query_search_volume(client):
    """Total de page views em /buscar/* por dia"""
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="date")],
        metrics=[
            Metric(name="screenPageViews"),
            Metric(name="totalUsers"),
        ],
        date_ranges=[DateRange(start_date=START_DATE, end_date=END_DATE)],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="pagePath",
                string_filter=Filter.StringFilter(
                    value="/buscar/",
                    match_type=Filter.StringFilter.MatchType.BEGINS_WITH
                )
            )
        )
    )
    return client.run_report(req)


def query_top_terms(client):
    """Top termos buscados (via pagePath) — últimos 30 dias"""
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="pagePath")],
        metrics=[
            Metric(name="screenPageViews"),
            Metric(name="totalUsers"),
        ],
        date_ranges=[DateRange(start_date=START_DATE, end_date=END_DATE)],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="pagePath",
                string_filter=Filter.StringFilter(
                    value="/buscar/",
                    match_type=Filter.StringFilter.MatchType.BEGINS_WITH
                )
            )
        )
    )
    return client.run_report(req)


def extract_term(page_path: str) -> str:
    parts = page_path.split("/buscar/", 1)
    if len(parts) > 1:
        from urllib.parse import unquote
        return unquote(parts[1]).strip("/")
    return page_path


def main():
    if not KEY_PATH.exists():
        print(f"[ERRO] Chave não encontrada: {KEY_PATH}")
        sys.exit(1)

    client = build_client()

    print(f"\n{'='*58}")
    print(f"  Busca interna via /buscar/:criteria — últimos 30 dias")
    print(f"{'='*58}")

    # ── Volume diário
    vol = query_search_volume(client)
    rows = sorted(vol.rows, key=lambda r: r.dimension_values[0].value)
    total_views = sum(int(r.metric_values[0].value) for r in rows)
    total_users = sum(int(r.metric_values[1].value) for r in rows)

    print(f"\n  Total de buscas (page views /buscar/*): {total_views}")
    print(f"  Usuários únicos que buscaram:           {total_users}")

    print(f"\n  Volume diário:")
    print(f"  {'Data':<12} {'Buscas':>8}  {'Usuários':>9}")
    print(f"  {'-'*34}")
    for row in rows:
        d = row.dimension_values[0].value
        date_fmt = f"{d[0:4]}-{d[4:6]}-{d[6:8]}"
        views = row.metric_values[0].value
        users = row.metric_values[1].value
        print(f"  {date_fmt:<12} {views:>8}  {users:>9}")

    # ── Top termos
    terms = query_top_terms(client)
    term_rows = sorted(
        terms.rows,
        key=lambda r: int(r.metric_values[0].value),
        reverse=True
    )

    print(f"\n  Top termos buscados:")
    print(f"  {'Termo':<40} {'Buscas':>7}  {'Usuários':>9}")
    print(f"  {'-'*60}")
    for row in term_rows[:25]:
        term = extract_term(row.dimension_values[0].value)
        views = row.metric_values[0].value
        users = row.metric_values[1].value
        print(f"  {term:<40} {views:>7}  {users:>9}")

    print(f"\n{'='*58}\n")


if __name__ == "__main__":
    main()
