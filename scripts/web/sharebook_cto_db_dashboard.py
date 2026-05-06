#!/usr/bin/env python3
from __future__ import annotations

import io
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ENV_PATH = Path('/data/workspace/sharebook-agent/.env')
OUT_DIR = Path('/data/workspace/sharebook-agent/reports/cto-db-dashboard')
OUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_env(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        data[k.strip()] = v.strip()
    return data


def q(sql: str, env: dict[str, str]) -> pd.DataFrame:
    cmd = [
        'psql',
        '-h', env['SHAREBOOK_PROD_PG_RO_HOST'],
        '-p', env['SHAREBOOK_PROD_PG_RO_PORT'],
        '-d', env['SHAREBOOK_PROD_PG_RO_DATABASE'],
        '-U', env['SHAREBOOK_PROD_PG_RO_USER'],
        '--csv',
        '-v', 'ON_ERROR_STOP=1',
        '-P', 'pager=off',
        '-c', sql,
    ]
    e = os.environ.copy()
    e['PGPASSWORD'] = env['SHAREBOOK_PROD_PG_RO_PASSWORD']
    out = subprocess.check_output(cmd, env=e, text=True)
    return pd.read_csv(io.StringIO(out))


def savefig(name: str):
    path = OUT_DIR / name
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def main():
    env = parse_env(ENV_PATH)

    # 1) Crescimento de usuários (24 meses)
    users = q(
        """
        SELECT date_trunc('month', "CreationDate")::date AS month,
               count(*) AS new_users
        FROM "Users"
        WHERE "CreationDate" >= date_trunc('month', now()) - interval '23 months'
        GROUP BY 1
        ORDER BY 1;
        """,
        env,
    )
    users['month'] = pd.to_datetime(users['month'])
    users['new_users'] = users['new_users'].fillna(0)
    users['cum_users_24m'] = users['new_users'].cumsum()

    plt.figure(figsize=(10, 4.8))
    plt.bar(users['month'].dt.strftime('%Y-%m'), users['new_users'], color='#3b82f6', label='Novos usuários/mês')
    plt.plot(users['month'].dt.strftime('%Y-%m'), users['cum_users_24m'], color='#111827', marker='o', label='Acumulado 24m')
    plt.xticks(rotation=55, ha='right')
    plt.title('Crescimento de usuários (24 meses)')
    plt.ylabel('Usuários')
    plt.legend()
    savefig('01_users_growth_24m.png')

    # 2) Aprovações de livros por semana (físico x digital)
    approvals = q(
        """
        SELECT date_trunc('week', "ApprovedAt")::date AS week,
               "Type" AS book_type,
               count(*) AS approved_books
        FROM "Books"
        WHERE "ApprovedAt" >= now() - interval '26 weeks'
        GROUP BY 1,2
        ORDER BY 1,2;
        """,
        env,
    )
    approvals['week'] = pd.to_datetime(approvals['week'])
    piv = approvals.pivot(index='week', columns='book_type', values='approved_books').fillna(0)
    piv = piv.rename(columns={0: 'Físico', 1: 'Digital'})

    plt.figure(figsize=(10, 4.8))
    plt.plot(piv.index, piv.get('Físico', 0), marker='o', label='Físico')
    plt.plot(piv.index, piv.get('Digital', 0), marker='o', label='Digital')
    plt.title('Aprovações por semana (últimas 26 semanas)')
    plt.ylabel('Livros aprovados')
    plt.xlabel('Semana')
    plt.legend()
    savefig('02_approvals_by_week_type.png')

    # 3) Marketplace demand: interessados por semana + ratio por livro criado
    demand = q(
        """
        WITH b AS (
          SELECT date_trunc('week', "CreationDate")::date AS week, count(*) AS books_created
          FROM "Books"
          WHERE "CreationDate" >= now() - interval '26 weeks'
          GROUP BY 1
        ),
        bu AS (
          SELECT date_trunc('week', "CreationDate")::date AS week, count(*) AS interests
          FROM "BookUser"
          WHERE "CreationDate" >= now() - interval '26 weeks'
          GROUP BY 1
        )
        SELECT COALESCE(b.week, bu.week) AS week,
               COALESCE(b.books_created, 0) AS books_created,
               COALESCE(bu.interests, 0) AS interests
        FROM b FULL OUTER JOIN bu ON b.week = bu.week
        ORDER BY 1;
        """,
        env,
    )
    demand['week'] = pd.to_datetime(demand['week'])
    demand['interests_per_book'] = demand.apply(
        lambda r: (r['interests'] / r['books_created']) if r['books_created'] else None,
        axis=1,
    )

    fig, ax1 = plt.subplots(figsize=(10, 4.8))
    ax1.bar(demand['week'], demand['interests'], color='#10b981', alpha=0.75, label='Interesses (BookUser)')
    ax1.set_ylabel('Interesses/semana')
    ax1.set_xlabel('Semana')
    ax2 = ax1.twinx()
    ax2.plot(demand['week'], demand['interests_per_book'], color='#ef4444', marker='o', label='Interesses por livro criado')
    ax2.set_ylabel('Interesses por livro')
    ax1.set_title('Demanda do marketplace (últimas 26 semanas)')
    savefig('03_marketplace_demand.png')

    # 4) Confiabilidade e custo operacional dos jobs
    jobs = q(
        """
        SELECT date_trunc('day', "CreationDate")::date AS day,
               "JobName",
               count(*) AS runs,
               sum(CASE WHEN "IsSuccess" THEN 1 ELSE 0 END) AS success_runs,
               percentile_cont(0.95) WITHIN GROUP (ORDER BY "TimeSpentSeconds") AS p95_sec
        FROM "JobHistories"
        WHERE "CreationDate" >= now() - interval '30 days'
          AND "JobName" IN ('JobExecutor','MailSender')
        GROUP BY 1,2
        ORDER BY 1,2;
        """,
        env,
    )
    jobs['day'] = pd.to_datetime(jobs['day'])
    jobs['success_rate'] = (jobs['success_runs'] / jobs['runs']) * 100.0

    fig, axes = plt.subplots(2, 1, figsize=(10, 7.2), sharex=True)
    for name, grp in jobs.groupby('JobName'):
        axes[0].plot(grp['day'], grp['success_rate'], marker='o', label=name)
        axes[1].plot(grp['day'], grp['p95_sec'], marker='o', label=name)
    axes[0].set_title('Confiabilidade diária (últimos 30 dias)')
    axes[0].set_ylabel('Success rate (%)')
    axes[0].set_ylim(90, 101)
    axes[0].legend()
    axes[1].set_title('Custo operacional (p95 de duração por dia)')
    axes[1].set_ylabel('p95 (segundos)')
    axes[1].set_xlabel('Dia')
    axes[1].legend()
    savefig('04_job_reliability_and_latency.png')

    # 5) Peso de armazenamento por tabela
    storage = q(
        """
        SELECT relname AS table_name,
               pg_total_relation_size(c.oid) AS bytes
        FROM pg_class c
        JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname='public' AND relkind='r'
        ORDER BY pg_total_relation_size(c.oid) DESC
        LIMIT 8;
        """,
        env,
    )
    storage['mb'] = storage['bytes'] / 1024 / 1024

    plt.figure(figsize=(10, 4.8))
    plt.barh(storage['table_name'][::-1], storage['mb'][::-1], color='#6366f1')
    plt.title('Top tabelas por armazenamento')
    plt.xlabel('MB')
    savefig('05_storage_top_tables.png')

    # Executive summary (markdown)
    latest_users = int(users['new_users'].iloc[-1]) if not users.empty else 0
    prev_users = int(users['new_users'].iloc[-2]) if len(users) > 1 else 0
    users_mom = ((latest_users - prev_users) / prev_users * 100.0) if prev_users else None

    ebook_ratio = None
    if not piv.empty and 'Digital' in piv.columns and 'Físico' in piv.columns:
        tot_d = float(piv['Digital'].sum())
        tot_f = float(piv['Físico'].sum())
        ebook_ratio = (tot_d / (tot_d + tot_f) * 100.0) if (tot_d + tot_f) else None

    avg_interest_per_book = float(pd.Series(demand['interests_per_book']).dropna().mean()) if not demand.empty else 0.0

    jexec = jobs[jobs['JobName'] == 'JobExecutor']
    mail = jobs[jobs['JobName'] == 'MailSender']
    jexec_sr = float(jexec['success_rate'].mean()) if not jexec.empty else 0.0
    mail_sr = float(mail['success_rate'].mean()) if not mail.empty else 0.0
    jexec_p95 = float(jexec['p95_sec'].median()) if not jexec.empty else 0.0
    mail_p95 = float(mail['p95_sec'].median()) if not mail.empty else 0.0

    md = OUT_DIR / 'README.md'
    md.write_text(
        f"""# CTO Dashboard — Sharebook (DB)

Gerado em: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}

## Highlights executivos
- Novos usuários no último mês: **{latest_users}**""" + (f""" (**{users_mom:+.1f}% MoM**)""" if users_mom is not None else "") + f"""
- Participação digital nas aprovações (26 semanas): **{ebook_ratio:.1f}%**""" + ("" if ebook_ratio is not None else " n/a") + f"""
- Média de interesse por livro criado (26 semanas): **{avg_interest_per_book:.1f}**
- JobExecutor — sucesso médio 30d: **{jexec_sr:.2f}%**, p95 mediano: **{jexec_p95:.1f}s**
- MailSender — sucesso médio 30d: **{mail_sr:.2f}%**, p95 mediano: **{mail_p95:.1f}s**

## Gráficos
1. `01_users_growth_24m.png` — crescimento de usuários
2. `02_approvals_by_week_type.png` — aprovações semanais (físico x digital)
3. `03_marketplace_demand.png` — interesses e interesse por livro criado
4. `04_job_reliability_and_latency.png` — confiabilidade e latência operacional
5. `05_storage_top_tables.png` — peso de armazenamento
""",
        encoding='utf-8',
    )

    print(f"Dashboard gerado em: {OUT_DIR}")


if __name__ == '__main__':
    main()
