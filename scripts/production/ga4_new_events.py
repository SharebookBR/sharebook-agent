"""
Métricas dos novos eventos GA4: search e amazon_click
Período: ontem (2026-06-03) e hoje (2026-06-04)
"""
import sys
from pathlib import Path
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, Dimension, Metric, DateRange, FilterExpression, Filter
)

PROPERTY_ID = "386966473"
KEY_PATH = Path(__file__).parent / "ga4-key.json"


def build_client():
    creds = service_account.Credentials.from_service_account_file(
        str(KEY_PATH),
        scopes=["https://www.googleapis.com/auth/analytics.readonly"]
    )
    return BetaAnalyticsDataClient(credentials=creds)


def query_totals(client, start, end):
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="eventName")],
        metrics=[
            Metric(name="eventCount"),
            Metric(name="totalUsers"),
        ],
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                in_list_filter=Filter.InListFilter(values=["search", "amazon_click"])
            )
        )
    )
    return client.run_report(req)


def query_search_terms(client, start, end):
    """searchTerm é dimensão built-in do evento search padrão do GA4"""
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="searchTerm")],
        metrics=[Metric(name="eventCount")],
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(value="search")
            )
        )
    )
    return client.run_report(req)


def query_amazon_by_session_source(client, start, end):
    """Origem das sessões que converteram em amazon_click"""
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[
            Dimension(name="sessionDefaultChannelGroup"),
            Dimension(name="sessionSourceMedium"),
        ],
        metrics=[
            Metric(name="eventCount"),
            Metric(name="totalUsers"),
        ],
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(value="amazon_click")
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


def print_period(client, label, start, end):
    print(f"\n{'─'*55}")
    print(f"  {label}  ({start})")
    print(f"{'─'*55}")

    totals = query_totals(client, start, end)
    if not totals.rows:
        print("  Nenhum evento nos dois tipos.")
    else:
        print("  Evento             Ocorrências   Usuários")
        for row in totals.rows:
            ev = row.dimension_values[0].value
            cnt = row.metric_values[0].value
            usr = row.metric_values[1].value
            print(f"  {ev:<20} {cnt:>8}      {usr:>6}")

    # Busca interna
    terms = query_search_terms(client, start, end)
    term_rows = sorted_rows(terms)
    print("\n  Termos buscados (search):")
    if not term_rows:
        print("    Nenhum evento search registrado.")
    else:
        for dims, mets in term_rows[:15]:
            term = dims[0] if dims else "(not set)"
            print(f"    {term:<38} {mets[0]:>4}")

    # Origem dos cliques Amazon
    src = query_amazon_by_session_source(client, start, end)
    src_rows = sorted_rows(src)
    print("\n  Origem das sessões → amazon_click:")
    if not src_rows:
        print("    Nenhum dado.")
    else:
        for dims, mets in src_rows:
            channel = dims[0]
            source = dims[1]
            cnt = mets[0]
            usr = mets[1]
            print(f"    {channel:<25} {source:<25} {cnt:>3} cliques  {usr:>2} users")


def main():
    if not KEY_PATH.exists():
        print(f"[ERRO] Chave não encontrada: {KEY_PATH}")
        sys.exit(1)

    client = build_client()
    print(f"\n{'='*55}")
    print(f"  GA4 — search + amazon_click")
    print(f"{'='*55}")

    print_period(client, "Ontem", "2026-06-03", "2026-06-03")
    print_period(client, "Hoje (parcial)", "2026-06-04", "2026-06-04")

    print(f"\n{'='*55}")
    print("  NOTA: book_title e search_term NÃO estão registrados")
    print("  como custom dimensions no GA4 — dados de livro indisponíveis.")
    print("  Registrar em: GA4 Admin > Custom Definitions > Create.")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
