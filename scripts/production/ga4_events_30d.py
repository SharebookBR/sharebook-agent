"""
Todos os eventos rastreados — últimos 30 dias
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

EVENTS = [
    "ebook_download",
    "amazon_click",
    "share_modal_open",
    "social_share",
    "search",
    "login",
    "sign_up",
]


def build_client():
    creds = service_account.Credentials.from_service_account_file(
        str(KEY_PATH),
        scopes=["https://www.googleapis.com/auth/analytics.readonly"]
    )
    return BetaAnalyticsDataClient(credentials=creds)


def query_totals(client):
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="eventName")],
        metrics=[
            Metric(name="eventCount"),
            Metric(name="totalUsers"),
        ],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                in_list_filter=Filter.InListFilter(values=EVENTS)
            )
        )
    )
    return client.run_report(req)


def query_top_books(client, event_name):
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="customEvent:book_title")],
        metrics=[Metric(name="eventCount")],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(value=event_name)
            )
        )
    )
    return client.run_report(req)


def query_share_channels(client):
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="customEvent:method")],
        metrics=[Metric(name="eventCount")],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(value="social_share")
            )
        )
    )
    return client.run_report(req)


def sorted_rows(response):
    rows = []
    for row in response.rows:
        dims = [d.value for d in row.dimension_values]
        mets = [m.value for m in row.metric_values]
        rows.append((dims, mets))
    rows.sort(key=lambda x: int(x[1][0]), reverse=True)
    return rows


def print_top(rows, label_col=0, top=10, indent="    "):
    if not rows:
        print(f"{indent}(sem dados)")
        return
    for dims, mets in rows[:top]:
        label = dims[label_col] if dims[label_col] != "(not set)" else "—"
        print(f"{indent}{label:<45} {mets[0]:>5}")


def main():
    if not KEY_PATH.exists():
        print(f"[ERRO] Chave não encontrada: {KEY_PATH}")
        sys.exit(1)

    client = build_client()

    print(f"\n{'='*60}")
    print(f"  Eventos GA4 — últimos 30 dias")
    print(f"{'='*60}")

    # ── Totais
    totals = query_totals(client)
    totals_map = {}
    for row in totals.rows:
        ev = row.dimension_values[0].value
        totals_map[ev] = {
            "count": int(row.metric_values[0].value),
            "users": int(row.metric_values[1].value),
        }

    print(f"\n  {'Evento':<22} {'Ocorrências':>12}  {'Usuários':>9}")
    print(f"  {'-'*48}")
    for ev in EVENTS:
        d = totals_map.get(ev, {"count": 0, "users": 0})
        print(f"  {ev:<22} {d['count']:>12}  {d['users']:>9}")

    # ── Top livros por download (via pagePath — custom dim só retroage de hoje)
    dl_count = totals_map.get("ebook_download", {}).get("count", 0)
    print(f"\n  Top livros — ebook_download ({dl_count} total):")
    print(f"    (book_title disponível via API só a partir de 04/06/2026)")

    # ── Top livros por amazon_click
    az_count = totals_map.get("amazon_click", {}).get("count", 0)
    print(f"\n  Top livros — amazon_click ({az_count} total):")
    print(f"    (book_title disponível via API só a partir de 04/06/2026)")

    # ── Canais de compartilhamento (method não está registrado como custom dim)
    sh_count = totals_map.get("social_share", {}).get("count", 0)
    print(f"\n  social_share ({sh_count} total) — canais indisponíveis via API")
    print(f"    (parâmetro 'method' não registrado como custom dimension)")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
