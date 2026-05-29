import psycopg2

conn = psycopg2.connect(
    host='212.85.23.202', port=5432, dbname='sharebook',
    user='sharebook_ai_ro', password='3-nbj0bw3STVkxlcCeEO2ZFwtvyn', sslmode='disable'
)
cur = conn.cursor()
cur.execute("""
    SELECT "Id", "JobName", "IsSuccess", "CreationDate", "Details"
    FROM "JobHistories"
    WHERE "JobName" = 'MailSender'
    ORDER BY "CreationDate" DESC
    LIMIT 5
""")
for row in cur.fetchall():
    print(f"--- {row[2]} | {row[3]} ---")
    print(row[4])
    print()
conn.close()
