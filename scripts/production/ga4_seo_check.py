import os
from collections import defaultdict
from dotenv import load_dotenv
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension, FilterExpression, Filter, OrderBy

load_dotenv('sharebook-agent/.env')

property_id = os.getenv('GA4_PROPERTY_ID')
key_path = os.getenv('GA4_KEY_FILE_PATH')
client = BetaAnalyticsDataClient.from_service_account_json(key_path)


def run_report(dimensions, metrics, start_date='30daysAgo', end_date='today', dimension_filter=None, order_bys=None, limit=100):
    request = RunReportRequest(
        property=f'properties/{property_id}',
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimension_filter=dimension_filter,
        order_bys=order_bys or [],
        limit=limit,
    )
    return client.run_report(request)

# 1) Organic search vs all session default channels
channels = run_report(
    dimensions=['sessionDefaultChannelGroup'],
    metrics=['sessions', 'totalUsers', 'engagedSessions'],
    limit=20,
)

print('CHANNELS')
for row in channels.rows:
    print('|'.join([
        row.dimension_values[0].value,
        row.metric_values[0].value,
        row.metric_values[1].value,
        row.metric_values[2].value,
    ]))

# 2) Landing pages from Organic Search
organic_filter = FilterExpression(
    filter=Filter(
        field_name='sessionDefaultChannelGroup',
        string_filter=Filter.StringFilter(value='Organic Search')
    )
)
landing = run_report(
    dimensions=['landingPagePlusQueryString'],
    metrics=['sessions', 'totalUsers', 'engagedSessions'],
    dimension_filter=organic_filter,
    order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name='sessions'), desc=True)],
    limit=25,
)

print('LANDING_PAGES_ORGANIC')
for row in landing.rows:
    print('|'.join([
        row.dimension_values[0].value,
        row.metric_values[0].value,
        row.metric_values[1].value,
        row.metric_values[2].value,
    ]))

# 3) Search engine breakdown
source_medium = run_report(
    dimensions=['sessionSourceMedium'],
    metrics=['sessions', 'totalUsers'],
    dimension_filter=organic_filter,
    order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name='sessions'), desc=True)],
    limit=15,
)

print('SOURCE_MEDIUM_ORGANIC')
for row in source_medium.rows:
    print('|'.join([
        row.dimension_values[0].value,
        row.metric_values[0].value,
        row.metric_values[1].value,
    ]))
