import os
from dotenv import load_dotenv
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension, OrderBy

load_dotenv('sharebook-agent/.env')
property_id = os.getenv('GA4_PROPERTY_ID')
key_path = os.getenv('GA4_KEY_FILE_PATH')
client = BetaAnalyticsDataClient.from_service_account_json(key_path)

request = RunReportRequest(
    property=f'properties/{property_id}',
    dimensions=[Dimension(name='yearWeek')],
    metrics=[Metric(name='sessions'), Metric(name='totalUsers')],
    date_ranges=[DateRange(start_date='90daysAgo', end_date='today')],
    order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name='yearWeek'))]
)

response = client.run_report(request)
for row in response.rows:
    print('|'.join([
        row.dimension_values[0].value,
        row.metric_values[0].value,
        row.metric_values[1].value,
    ]))
