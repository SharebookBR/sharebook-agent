"""
GA4 Dashboard Generator — Sharebook
Gera um HTML estático com métricas das últimas 12 semanas.
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    Dimension,
    Metric,
    DateRange,
    FilterExpression,
    Filter,
    OrderBy,
)
from google.oauth2 import service_account

KEY_PATH = Path(__file__).parent / "ga4-key.json"
PROPERTY_ID = "386966473"
OUTPUT_PATH = Path(__file__).parent.parent.parent / "ga4_dashboard.html"


def get_client():
    creds = service_account.Credentials.from_service_account_file(
        str(KEY_PATH),
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )
    return BetaAnalyticsDataClient(credentials=creds)


def date_range_12_weeks():
    end = datetime.today()
    start = end - timedelta(weeks=12)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def fetch_sessions_weekly(client):
    start, end = date_range_12_weeks()
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name="year"), Dimension(name="week")],
        metrics=[Metric(name="sessions")],
        order_bys=[
            OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="year"), desc=False),
            OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="week"), desc=False),
        ],
    )
    resp = client.run_report(req)
    rows = []
    for row in resp.rows:
        year = row.dimension_values[0].value
        week = row.dimension_values[1].value.zfill(2)
        sessions = int(row.metric_values[0].value)
        rows.append({"label": f"{year}-W{week}", "value": sessions})
    return rows


def fetch_event_total(client, event_name):
    start, end = date_range_12_weeks()
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(value=event_name, match_type="EXACT"),
            )
        ),
    )
    resp = client.run_report(req)
    if resp.rows:
        return int(resp.rows[0].metric_values[0].value)
    return 0


def fetch_top_books(client, limit=10):
    start, end = date_range_12_weeks()
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name="pagePath"), Dimension(name="pageTitle")],
        metrics=[Metric(name="screenPageViews")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="pagePath",
                string_filter=Filter.StringFilter(value="/livros/", match_type="BEGINS_WITH"),
            )
        ),
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
        limit=limit,
    )
    resp = client.run_report(req)
    rows = []
    for row in resp.rows:
        path = row.dimension_values[0].value
        # Extrai slug do path: /livros/meu-livro-aqui → Meu Livro Aqui
        slug = path.rstrip("/").split("/")[-1]
        title = slug.replace("-", " ").title() if slug else path
        views = int(row.metric_values[0].value)
        rows.append({"path": path, "title": title, "views": views})
    return rows


def fetch_top_downloads(client, limit=10):
    start, end = date_range_12_weeks()
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name="pagePath")],
        metrics=[Metric(name="eventCount")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(value="ebook_download", match_type="EXACT"),
            )
        ),
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)],
        limit=limit,
    )
    resp = client.run_report(req)
    rows = []
    for row in resp.rows:
        path = row.dimension_values[0].value
        slug = path.rstrip("/").split("/")[-1]
        title = slug.replace("-", " ").title() if slug else path
        count = int(row.metric_values[0].value)
        rows.append({"path": path, "title": title, "count": count})
    return rows


def fetch_downloads_weekly(client):
    start, end = date_range_12_weeks()
    req = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name="year"), Dimension(name="week")],
        metrics=[Metric(name="eventCount")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(value="ebook_download", match_type="EXACT"),
            )
        ),
        order_bys=[
            OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="year"), desc=False),
            OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="week"), desc=False),
        ],
    )
    resp = client.run_report(req)
    rows = []
    for row in resp.rows:
        year = row.dimension_values[0].value
        week = row.dimension_values[1].value.zfill(2)
        count = int(row.metric_values[0].value)
        rows.append({"label": f"{year}-W{week}", "value": count})
    return rows


def build_html(sessions, downloads_weekly, downloads_total, logins, signups, top_books, top_downloads):
    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Align weekly labels (sessions + downloads may have different weeks)
    all_labels = sorted(set([r["label"] for r in sessions] + [r["label"] for r in downloads_weekly]))
    sessions_map = {r["label"]: r["value"] for r in sessions}
    downloads_map = {r["label"]: r["value"] for r in downloads_weekly}

    # Current week label to highlight incomplete data (ISO week, same que GA4 usa)
    now = datetime.today()
    iso_year, iso_week, _ = now.isocalendar()
    current_week_key = f"{iso_year}-W{iso_week:02d}"

    def iso_to_friendly(label):
        # "2026-W23" → "2026-06-W1"
        year, week = label.split("-W")
        from datetime import date
        monday = date.fromisocalendar(int(year), int(week), 1)
        week_in_month = (monday.day - 1) // 7 + 1
        return f"{monday.year}-{monday.month:02d}-W{week_in_month}"

    display_labels = [iso_to_friendly(l) for l in all_labels]
    current_display_label = iso_to_friendly(current_week_key)

    labels_js = json.dumps(display_labels)
    all_sessions_js = json.dumps([sessions_map.get(l, 0) for l in all_labels])
    all_downloads_js = json.dumps([downloads_map.get(l, 0) for l in all_labels])
    current_week_display_js = json.dumps(current_display_label)
    total_sessions_js = sum(sessions_map.values())
    total_downloads_js = sum(downloads_map.values())

    base_url = "https://sharebook.com.br"

    books_rows = ""
    for i, b in enumerate(top_books, 1):
        books_rows += f"""
        <tr>
          <td class="rank">{i}</td>
          <td class="title"><a href="{base_url}{b['path']}" target="_blank">{b['title']}</a></td>
          <td class="views">{b['views']:,}</td>
        </tr>"""

    downloads_rows = ""
    for i, b in enumerate(top_downloads, 1):
        downloads_rows += f"""
        <tr>
          <td class="rank">{i}</td>
          <td class="title"><a href="{base_url}{b['path']}" target="_blank">{b['title']}</a></td>
          <td class="views">{b['count']:,}</td>
        </tr>"""

    total_sessions = sum(r["value"] for r in sessions)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sharebook — Analytics Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f4f6f9;
      color: #333;
      padding: 24px;
    }}

    header {{
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 32px;
    }}

    header .logo {{
      font-size: 22px;
      font-weight: 700;
      color: #29abe2;
      letter-spacing: -0.5px;
    }}

    header .logo span {{ color: #555; font-weight: 400; font-size: 14px; }}

    .header-right {{
      margin-left: auto;
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    header .generated {{
      font-size: 12px;
      color: #888;
    }}

    #weekSelect {{
      font-size: 13px;
      padding: 6px 10px;
      border: 1px solid #d0e8f5;
      border-radius: 6px;
      color: #29abe2;
      background: #fff;
      cursor: pointer;
      outline: none;
    }}

    #weekSelect:focus {{
      border-color: #29abe2;
      box-shadow: 0 0 0 2px rgba(41,171,226,0.15);
    }}

    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      margin-bottom: 32px;
    }}

    .kpi-card {{
      background: #fff;
      border-radius: 10px;
      padding: 20px 24px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.07);
      border-top: 3px solid #29abe2;
    }}

    .kpi-card .label {{
      font-size: 12px;
      color: #888;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 8px;
    }}

    .kpi-card .value {{
      font-size: 32px;
      font-weight: 700;
      color: #29abe2;
    }}

    .kpi-card .sub {{
      font-size: 11px;
      color: #aaa;
      margin-top: 4px;
    }}

    .charts-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 32px;
    }}

    @media (max-width: 768px) {{
      .charts-grid {{ grid-template-columns: 1fr; }}
    }}

    .card {{
      background: #fff;
      border-radius: 10px;
      padding: 20px 24px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.07);
      border: 1px solid #d0d0d0;
    }}

    .card h3 {{
      font-size: 13px;
      font-weight: 600;
      color: #fff;
      background: #29abe2;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin: -20px -24px 16px -24px;
      padding: 12px 24px;
      border-radius: 10px 10px 0 0;
    }}

    .card canvas {{ max-height: 220px; }}

    .books-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}

    .books-table td {{
      padding: 9px 12px;
      border-bottom: 1px solid #d0d0d0;
    }}

    .books-table tr:last-child td {{ border-bottom: none; }}

    .books-table .rank {{
      color: #bbb;
      font-weight: 600;
      width: 28px;
    }}

    .books-table .title a {{
      color: #333;
      text-decoration: none;
    }}

    .books-table .title a:hover {{
      color: #29abe2;
      text-decoration: underline;
    }}

    .books-table .views {{
      text-align: right;
      font-weight: 600;
      color: #29abe2;
      white-space: nowrap;
    }}

    footer {{
      text-align: center;
      font-size: 11px;
      color: #bbb;
      margin-top: 16px;
    }}
  </style>
</head>
<body>

  <header>
    <div class="logo">sharebook <span>/ analytics</span></div>
    <div class="header-right">
      <select id="weekSelect">
        <option value="all">Todas as semanas</option>
      </select>
    </div>
  </header>

  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="label">Sessões</div>
      <div class="value" id="kpiSessions">{total_sessions_js:,}</div>
      <div class="sub" id="kpiSessionsSub">últimas 12 semanas</div>
    </div>
    <div class="kpi-card">
      <div class="label">Downloads</div>
      <div class="value" id="kpiDownloads">{total_downloads_js:,}</div>
      <div class="sub" id="kpiDownloadsSub">últimas 12 semanas</div>
    </div>
    <div class="kpi-card">
      <div class="label">Logins</div>
      <div class="value">{logins:,}</div>
      <div class="sub">evento login</div>
    </div>
    <div class="kpi-card">
      <div class="label">Cadastros</div>
      <div class="value">{signups:,}</div>
      <div class="sub">evento sign_up</div>
    </div>
  </div>

  <div class="charts-grid">
    <div class="card">
      <h3>Sessões por semana</h3>
      <canvas id="chartSessions"></canvas>
    </div>
    <div class="card">
      <h3>Downloads por semana</h3>
      <canvas id="chartDownloads"></canvas>
    </div>
  </div>

  <div class="charts-grid">
    <div class="card">
      <h3>Top {len(top_books)} livros por visualizações</h3>
      <table class="books-table">
        {books_rows}
      </table>
    </div>
    <div class="card">
      <h3>Top {len(top_downloads)} livros por downloads</h3>
      <table class="books-table">
        {downloads_rows}
      </table>
    </div>
  </div>

  <footer>sharebook.com.br · dados via Google Analytics 4</footer>

  <script>
    const labels = {labels_js};
    const allSessions = {all_sessions_js};
    const allDownloads = {all_downloads_js};
    const currentWeek = {current_week_display_js};
    const totalSessions = {total_sessions_js};
    const totalDownloads = {total_downloads_js};

    // Populate select — newest first
    const sel = document.getElementById("weekSelect");
    [...labels].reverse().forEach(lbl => {{
      const opt = document.createElement("option");
      opt.value = lbl;
      opt.textContent = lbl;
      if (lbl === currentWeek) opt.selected = true;
      sel.appendChild(opt);
    }});

    const BLUE      = "rgba(41,171,226,0.7)";
    const BLUE_DIM  = "rgba(41,171,226,0.2)";
    const BLUE_DL   = "rgba(41,171,226,0.35)";
    const BLUE_DIM2 = "rgba(41,171,226,0.1)";
    const ORANGE    = "rgba(255,165,0,0.8)";
    const ORANGE_DL = "rgba(255,165,0,0.5)";
    const BORDER    = "#29abe2";
    const BORDER_OR = "#f0a000";

    function makeColors(selectedLabel, normalBg, dimBg, selBg, normalBorder, selBorder) {{
      return labels.map(l => ({{
        bg:     selectedLabel === "all" ? normalBg  : (l === selectedLabel ? selBg  : dimBg),
        border: selectedLabel === "all" ? normalBorder : (l === selectedLabel ? selBorder : normalBorder),
      }}));
    }}

    const commonOptions = {{
      responsive: true,
      maintainAspectRatio: true,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        x: {{ ticks: {{ font: {{ size: 10 }}, maxRotation: 45 }}, grid: {{ display: false }} }},
        y: {{ beginAtZero: true, ticks: {{ font: {{ size: 10 }} }}, grid: {{ color: "#f0f0f0" }} }},
      }},
    }};

    function buildDataset(data, bgColors, borderColors) {{
      return {{
        data,
        backgroundColor: bgColors,
        borderColor: borderColors,
        borderWidth: 1,
        borderRadius: 4,
      }};
    }}

    function getColors(selectedLabel) {{
      const s = makeColors(selectedLabel, BLUE,    BLUE_DIM,  ORANGE,    BORDER, BORDER_OR);
      const d = makeColors(selectedLabel, BLUE_DL, BLUE_DIM2, ORANGE_DL, BORDER, BORDER_OR);
      return {{ s, d }};
    }}

    const initColors = getColors(currentWeek);

    const chartSessions = new Chart(document.getElementById("chartSessions"), {{
      type: "bar",
      data: {{ labels, datasets: [buildDataset(allSessions, initColors.s.map(c=>c.bg), initColors.s.map(c=>c.border))] }},
      options: commonOptions,
    }});

    const chartDownloads = new Chart(document.getElementById("chartDownloads"), {{
      type: "bar",
      data: {{ labels, datasets: [buildDataset(allDownloads, initColors.d.map(c=>c.bg), initColors.d.map(c=>c.border))] }},
      options: commonOptions,
    }});

    function updateKpis(selectedLabel) {{
      const kpiS   = document.getElementById("kpiSessions");
      const kpiD   = document.getElementById("kpiDownloads");
      const subS   = document.getElementById("kpiSessionsSub");
      const subD   = document.getElementById("kpiDownloadsSub");
      if (selectedLabel === "all") {{
        kpiS.textContent = totalSessions.toLocaleString("pt-BR");
        kpiD.textContent = totalDownloads.toLocaleString("pt-BR");
        subS.textContent = "últimas 12 semanas";
        subD.textContent = "últimas 12 semanas";
      }} else {{
        const idx = labels.indexOf(selectedLabel);
        kpiS.textContent = (allSessions[idx] || 0).toLocaleString("pt-BR");
        kpiD.textContent = (allDownloads[idx] || 0).toLocaleString("pt-BR");
        subS.textContent = selectedLabel;
        subD.textContent = selectedLabel;
      }}
    }}

    // Init KPIs with current week
    updateKpis(currentWeek);

    sel.addEventListener("change", () => {{
      const v = sel.value;
      const c = getColors(v);
      chartSessions.data.datasets[0].backgroundColor = c.s.map(x=>x.bg);
      chartSessions.data.datasets[0].borderColor = c.s.map(x=>x.border);
      chartSessions.update();
      chartDownloads.data.datasets[0].backgroundColor = c.d.map(x=>x.bg);
      chartDownloads.data.datasets[0].borderColor = c.d.map(x=>x.border);
      chartDownloads.update();
      updateKpis(v);
    }});
  </script>

</body>
</html>"""
    return html


def main():
    print("Conectando ao GA4...")
    client = get_client()

    print("Buscando sessões semanais...")
    sessions = fetch_sessions_weekly(client)

    print("Buscando downloads semanais...")
    downloads_weekly = fetch_downloads_weekly(client)

    print("Buscando totais de eventos...")
    downloads_total = fetch_event_total(client, "ebook_download")
    logins = fetch_event_total(client, "login")
    signups = fetch_event_total(client, "sign_up")

    print("Buscando top livros por views...")
    top_books = fetch_top_books(client)

    print("Buscando top livros por downloads...")
    top_downloads = fetch_top_downloads(client)

    print("Gerando HTML...")
    html = build_html(sessions, downloads_weekly, downloads_total, logins, signups, top_books, top_downloads)

    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"\nDashboard gerado: {OUTPUT_PATH}")
    print(f"  Sessões totais : {sum(r['value'] for r in sessions):,}")
    print(f"  Downloads      : {downloads_total:,}")
    print(f"  Logins         : {logins:,}")
    print(f"  Cadastros      : {signups:,}")
    print(f"  Top livros     : {len(top_books)}")


if __name__ == "__main__":
    main()
