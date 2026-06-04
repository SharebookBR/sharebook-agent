"""Lista metadata da property GA4: custom dimensions registradas e top event params"""
from pathlib import Path
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import GetMetadataRequest

PROPERTY_ID = "386966473"
KEY_PATH = Path(__file__).parent / "ga4-key.json"

creds = service_account.Credentials.from_service_account_file(
    str(KEY_PATH),
    scopes=["https://www.googleapis.com/auth/analytics.readonly"]
)
client = BetaAnalyticsDataClient(credentials=creds)

resp = client.get_metadata(GetMetadataRequest(name=f"properties/{PROPERTY_ID}/metadata"))

print("\n### Custom Dimensions disponíveis:")
for d in resp.dimensions:
    if d.api_name.startswith("customEvent") or "event" in d.api_name.lower():
        print(f"  {d.api_name:<45} {d.ui_name}")

print("\n### Todas as dimensions (filtro: não built-in padrão):")
for d in resp.dimensions:
    if not any(d.api_name.startswith(p) for p in ["age", "city", "country", "gender", "language"]):
        cat = getattr(d, 'category', '?')
        print(f"  {d.api_name:<45} [{cat}] {d.ui_name}")
