import psycopg2
from dotenv import load_dotenv
import os

load_dotenv(r'C:\Repos\SHAREBOOK\sharebook-agent\.env')

conn = psycopg2.connect(
    host='212.85.23.202', port=5432, dbname='sharebook',
    user='sharebook_ai_ro', password='3-nbj0bw3STVkxlcCeEO2ZFwtvyn', sslmode='disable'
)
cur = conn.cursor()

print('=== Job Histories (NewEbookWeeklyDigest) ===')
cur.execute("""
    SELECT "JobName", "IsSuccess", "Details", "CreationDate"
    FROM "JobHistories"
    WHERE "JobName" = 'NewEbookWeeklyDigest'
    ORDER BY "CreationDate" DESC
    LIMIT 5
""")
rows = cur.fetchall()
for r in rows:
    print(f'Data: {r[3]}')
    print(f'IsSuccess: {r[1]}')
    print(f'Details:')
    for line in str(r[2]).split('\n'):
        print(f'  {line}')
    print()

print()
print('=== Ebooks aprovados nos ultimos 7 dias ===')
cur.execute("""
    SELECT b."Id", b."Title", b."Author", b."ApprovedAt", c."Name" as category
    FROM "Books" b
    LEFT JOIN "Categories" c ON b."CategoryId" = c."Id"
    WHERE b."Type" = 1
      AND b."Status" = 1
      AND b."ApprovedAt" >= NOW() - INTERVAL '7 days'
    ORDER BY b."ApprovedAt" DESC
""")
ebooks = cur.fetchall()
print(f'Total: {len(ebooks)} ebook(s)')
for e in ebooks:
    print(f'  [{e[4]}] {e[1]} — {e[2]} (ApprovedAt: {e[3]})')

conn.close()
