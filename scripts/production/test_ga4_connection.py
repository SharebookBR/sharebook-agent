import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Metric,
    Dimension
)
from dotenv import load_dotenv

# Carrega ambiente
load_dotenv('sharebook-agent/.env')

def test_connection():
    property_id = os.getenv('GA4_PROPERTY_ID')
    key_path = os.getenv('GA4_KEY_FILE_PATH')

    print(f"🚀 Iniciando teste de conexão GA4...")
    print(f"📊 Property ID: {property_id}")
    print(f"🔑 Usando chave: {key_path}")

    try:
        client = BetaAnalyticsDataClient.from_service_account_json(key_path)

        # Request simples: Usuários ativos hoje
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="date")],
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date="today", end_date="today")],
        )

        response = client.run_report(request)

        print("\n✅ CONEXÃO ESTABELECIDA COM SUCESSO!")
        print("-" * 30)
        
        if not response.rows:
            print("ℹ️ Nenhum dado encontrado para hoje ainda (normal se o GA4 for novo).")
        else:
            for row in response.rows:
                print(f"📅 Data: {row.dimension_values[0].value} | 👥 Usuários Ativos: {row.metric_values[0].value}")
        
        print("-" * 30)

    except Exception as e:
        print(f"\n❌ ERRO NA CONEXÃO:")
        print(str(e))

if __name__ == "__main__":
    test_connection()
