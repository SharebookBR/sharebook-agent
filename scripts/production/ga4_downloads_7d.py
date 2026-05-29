import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, DateRange, Metric, Dimension, FilterExpression,
    Filter, OrderBy
)
from dotenv import load_dotenv

load_dotenv('sharebook-agent/.env')

property_id = os.getenv('GA4_PROPERTY_ID')
key_path = os.getenv('GA4_KEY_FILE_PATH')

client = BetaAnalyticsDataClient.from_service_account_json(key_path)

# Downloads por data + título
req = RunReportRequest(
    property=f"properties/{property_id}",
    dimensions=[Dimension(name="date"), Dimension(name="pageTitle")],
    metrics=[Metric(name="eventCount")],
    date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
    dimension_filter=FilterExpression(
        filter=Filter(
            field_name="eventName",
            string_filter=Filter.StringFilter(value="ebook_download")
        )
    ),
    order_bys=[
        OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date")),
        OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True),
    ],
    limit=200
)

resp = client.run_report(req)

from collections import defaultdict

# agrupa por data
by_date = defaultdict(list)
for row in resp.rows:
    date  = row.dimension_values[0].value
    title = row.dimension_values[1].value.replace(" | ShareBook", "")
    n     = int(row.metric_values[0].value)
    by_date[date].append((title, n))

total = sum(n for rows in by_date.values() for _, n in rows)

print(f"\n=== ebook_download — últimos 7 dias | Total: {total} ===")
for date in sorted(by_date):
    d = f"{date[:4]}-{date[4:6]}-{date[6:]}"
    day_total = sum(n for _, n in by_date[date])
    print(f"\n{d}  ({day_total} downloads)")
    for title, n in by_date[date]:
        print(f"  {n:>3}  {title}")
