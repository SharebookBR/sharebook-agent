import os
from dotenv import load_dotenv
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension, FilterExpression, Filter, OrderBy

load_dotenv('sharebook-agent/.env')
property_id = os.getenv('GA4_PROPERTY_ID')
key_path = os.getenv('GA4_KEY_FILE_PATH')
client = BetaAnalyticsDataClient.from_service_account_json(key_path)


def run(dimensions, metrics, channel, start='30daysAgo', end='today', limit=20):
    filt = FilterExpression(
        filter=Filter(
            field_name='sessionDefaultChannelGroup',
            string_filter=Filter.StringFilter(value=channel)
        )
    )
    req = RunReportRequest(
        property=f'properties/{property_id}',
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimension_filter=filt,
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name=metrics[0]), desc=True)],
        limit=limit,
    )
    return client.run_report(req)

for channel in ['Organic Search', 'Organic Social']:
    print(f'CHANNEL::{channel}')

    summary = run(['sessionSourceMedium'], ['sessions', 'totalUsers', 'engagedSessions'], channel, limit=15)
    print('SOURCE_MEDIUM')
    for row in summary.rows:
        print('|'.join([*(v.value for v in row.dimension_values), *(v.value for v in row.metric_values)]))

    landing = run(['landingPagePlusQueryString'], ['sessions', 'totalUsers', 'engagedSessions'], channel, limit=20)
    print('LANDING_PAGES')
    for row in landing.rows:
        print('|'.join([*(v.value for v in row.dimension_values), *(v.value for v in row.metric_values)]))

    pages = run(['pagePath'], ['screenPageViews', 'activeUsers'], channel, limit=20)
    print('PAGE_VIEWS')
    for row in pages.rows:
        print('|'.join([*(v.value for v in row.dimension_values), *(v.value for v in row.metric_values)]))
