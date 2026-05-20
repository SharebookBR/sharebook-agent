import os
import json
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Metric,
    Dimension,
    OrderBy
)
from dotenv import load_dotenv

# Carrega ambiente
load_dotenv('sharebook-agent/.env')

def generate_dashboard():
    property_id = os.getenv('GA4_PROPERTY_ID')
    key_path = os.getenv('GA4_KEY_FILE_PATH')

    client = BetaAnalyticsDataClient.from_service_account_json(key_path)

    # 1. Busca usuários ativos (Últimos 7 dias)
    users_request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="date")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
        order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date"))]
    )
    users_resp = client.run_report(users_request)

    # 2. Busca Eventos de Negócio (O Ouro)
    biz_events = ['ebook_download', 'social_share', 'book_request_success', 'book_request_modal_open']
    biz_request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount")],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")]
    )
    biz_resp = client.run_report(biz_request)

    # 3. Busca Cidades (Geografia)
    geo_request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="city")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        limit=5
    )
    geo_resp = client.run_report(geo_request)

    # 4. Busca Dispositivos (Web vs Mobile)
    device_request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="deviceCategory")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")]
    )
    device_resp = client.run_report(device_request)

    # Preparação de Dados
    dates = [row.dimension_values[0].value for row in users_resp.rows]
    users_count = [row.metric_values[0].value for row in users_resp.rows]

    biz_rows = ""
    found_events = [row.dimension_values[0].value for row in biz_resp.rows]
    for event in biz_events:
        count = 0
        if event in found_events:
            idx = found_events.index(event)
            count = biz_resp.rows[idx].metric_values[0].value
        
        icon = "📥" if "download" in event else "📢" if "share" in event else "📖"
        biz_rows += f"""
        <div class='col-md-3 mb-3'>
            <div class='card text-center p-3 border-left-biz shadow-sm'>
                <div class='h1'>{icon}</div>
                <div class='text-muted small uppercase font-weight-bold'>{event.replace('_', ' ')}</div>
                <div class='display-4 font-weight-bold'>{count}</div>
            </div>
        </div>"""

    city_labels = [row.dimension_values[0].value for row in geo_resp.rows]
    city_data = [row.metric_values[0].value for row in geo_resp.rows]

    device_labels = [row.dimension_values[0].value for row in device_resp.rows]
    device_data = [row.metric_values[0].value for row in device_resp.rows]

    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sharebook GA4 Agent - Advanced Insight</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{ background-color: #f0f2f5; font-family: 'Inter', sans-serif; color: #1c1e21; }}
            .card {{ border: none; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); overflow: hidden; }}
            .header-gradient {{ 
                background: linear-gradient(135deg, #1a2a6c 0%, #b21f1f 50%, #fdbb2d 100%); 
                color: white; padding: 60px 0; border-radius: 0 0 40px 40px; margin-bottom: -40px; 
            }}
            .border-left-biz {{ border-left: 5px solid #b21f1f !important; }}
            .main-container {{ position: relative; z-index: 10; }}
            .badge-geo {{ background-color: #1a2a6c; color: white; }}
        </style>
    </head>
    <body>
        <div class="header-gradient text-center">
            <h1 class="display-4 font-weight-bold">💎 Sharebook Business Intelligence</h1>
            <p class="lead">O pulso do projeto, traduzido pelo Eco</p>
        </div>

        <div class="container main-container mt-5">
            <!-- Business Conversion Row -->
            <div class="row mb-4">
                {biz_rows}
            </div>

            <div class="row mb-4">
                <!-- Engagement Chart -->
                <div class="col-md-8">
                    <div class="card p-4 h-100">
                        <h5 class="font-weight-bold mb-4">📈 Engajamento Semanal (Usuários Ativos)</h5>
                        <canvas id="usersChart"></canvas>
                    </div>
                </div>
                <!-- Device Distribution -->
                <div class="col-md-4">
                    <div class="card p-4 h-100">
                        <h5 class="font-weight-bold mb-4">📱 Web vs Mobile (30d)</h5>
                        <canvas id="deviceChart"></canvas>
                        <div class="mt-4">
                             <ul class="list-group list-group-flush">
                                {"".join([f"<li class='list-group-item d-flex justify-content-between align-items-center'>{d.capitalize()} <span class='badge badge-dark badge-pill'>{v}</span></li>" for d, v in zip(device_labels, device_data)])}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mb-4">
                <!-- Geo Distribution -->
                <div class="col-md-12">
                    <div class="card p-4">
                        <h5 class="font-weight-bold mb-3">🌍 Cidades mais ativas</h5>
                        <div class="row">
                            <div class="col-md-4">
                                <canvas id="geoChart"></canvas>
                            </div>
                            <div class="col-md-8">
                                <div class="table-responsive">
                                    <table class="table table-hover">
                                        <thead><tr><th>Cidade</th><th>Usuários</th></tr></thead>
                                        <tbody>
                                            {"".join([f"<tr><td>{c}</td><td>{v}</td></tr>" for c, v in zip(city_labels, city_data)])}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card p-4 mb-5 bg-dark text-white shadow-lg">
                <div class="row align-items-center">
                    <div class="col-md-2 text-center h1">🧠</div>
                    <div class="col-md-10">
                        <h5 class="font-weight-bold">Insight do Eco</h5>
                        <p class="mb-0 text-light">Raffa, adicionei a métrica de <strong>Dispositivos</strong>. Entender se nosso público é majoritariamente Mobile ou Desktop dita onde devemos investir em UX. O Sharebook agora tem consciência de habitat!</p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Gráfico de Linha (Usuários)
            new Chart(document.getElementById('usersChart'), {{
                type: 'line',
                data: {{
                    labels: {json.dumps(dates)},
                    datasets: [{{
                        label: 'Usuários Ativos',
                        data: {json.dumps(users_count)},
                        borderColor: '#1a2a6c',
                        backgroundColor: 'rgba(26, 42, 108, 0.05)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 6,
                        pointBackgroundColor: '#1a2a6c'
                    }}]
                }},
                options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }} }}
            }});

            // Gráfico de Pizza (Devices)
            new Chart(document.getElementById('deviceChart'), {{
                type: 'doughnut',
                data: {{
                    labels: {json.dumps(device_labels)},
                    datasets: [{{
                        data: {json.dumps(device_data)},
                        backgroundColor: ['#2ecc71', '#3498db', '#9b59b6']
                    }}]
                }},
                options: {{ cutout: '70%', plugins: {{ legend: {{ position: 'bottom' }} }} }}
            }});

            // Gráfico de Pizza (Geo)
            new Chart(document.getElementById('geoChart'), {{
                type: 'pie',
                data: {{
                    labels: {json.dumps(city_labels)},
                    datasets: [{{
                        data: {json.dumps(city_data)},
                        backgroundColor: ['#1a2a6c', '#b21f1f', '#fdbb2d', '#65676b', '#bdc3c7']
                    }}]
                }},
                options: {{ plugins: {{ legend: {{ display: false }} }} }}
            }});
        </script>
    </body>
    </html>
    """

    with open('analytics_preview.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"📱 Dashboard UPGRADED (Web vs Mobile): analytics_preview.html")

if __name__ == "__main__":
    generate_dashboard()
