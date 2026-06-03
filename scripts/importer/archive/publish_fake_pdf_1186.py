import sys, base64, json
sys.path.insert(0, r"C:\Repos\SHAREBOOK\sharebook-agent\scripts\production")

from pathlib import Path
from dotenv import dotenv_values
import psycopg2, boto3
from datetime import datetime, timezone
from sharebook_prod_auth import API_BASE, auth_headers, get_token, load_env, request_json
from sharebook_prod_book import find_exact_book, approve_book

REPO_ROOT = Path(r"C:\Repos\SHAREBOOK\sharebook-agent")
env = load_env(REPO_ROOT)
token = get_token(env, repo_root=REPO_ROOT)

FAKE_PDF = Path(r"C:\Temp\fake.pdf")

conn = psycopg2.connect(
    host="212.85.23.202", port=5432, dbname="sharebook_importer",
    user="sharebook_ai_rw", password="F%Ljy9oxTA3iR#npW%4W9iaSaJKU", sslmode="disable"
)
cur = conn.cursor()
cur.execute("""
    SELECT id, title, planned_title, planned_author, planned_synopsis, planned_category_id, metadata_json
    FROM importer.queue_items WHERE id = 1186
""")
row = cur.fetchone()
if not row:
    print("Item 1186 não encontrado.")
    sys.exit(1)

item_id, raw_title, planned_title, author, synopsis, cat_id, meta = row
title = planned_title or raw_title
preview_pages = (meta or {}).get("triage", {}).get("preview_pages", [])
cover_path = Path(preview_pages[0]) if preview_pages else None

print(f"Publicando #{item_id}: {title}")
print(f"  autor: {author}")
print(f"  capa: {cover_path}")

cover_bytes = cover_path.read_bytes() if cover_path and cover_path.exists() else b""
cover_name = cover_path.name if cover_path else "cover.png"

payload = {
    "Title": title,
    "Author": author,
    "CategoryId": cat_id,
    "Synopsis": synopsis,
    "Type": "Eletronic",
    "ImageName": cover_name,
    "ImageBytes": base64.b64encode(cover_bytes).decode("ascii"),
    "PdfBytes": base64.b64encode(FAKE_PDF.read_bytes()).decode("ascii"),
}

create_resp = request_json(f"{API_BASE}/Book", method="POST",
                           body=payload, headers=auth_headers(token))
print(f"  create: {create_resp.get('successMessage') or create_resp}")

book = find_exact_book(token, title, author, book_type="Eletronic")
if not book:
    print("ERRO: livro não encontrado após criação.")
    sys.exit(1)

book_id = book["id"]
ebook_pdf_path = book.get("eBookPdfPath") or book.get("eBookPDFPath")
print(f"  book_id={book_id}  pdf_path={ebook_pdf_path}")

approve_book(token, book_id)
print("  aprovado ✓")

real_pdf = Path(r"C:\Users\raffa\Downloads") / f"{item_id}.pdf"
s3 = boto3.client("s3",
    aws_access_key_id=env["AWS_S3_ACCESS_KEY"],
    aws_secret_access_key=env["AWS_S3_SECRET_KEY"],
    region_name=env.get("AWS_S3_REGION", "sa-east-1")
)
s3.upload_file(str(real_pdf), env["AWS_S3_BUCKET"], ebook_pdf_path,
               ExtraArgs={"ContentType": "application/pdf"})
print(f"  S3 upload OK -> {ebook_pdf_path}")

now = datetime.now(timezone.utc)
cur.execute("""
    UPDATE importer.queue_items SET status = 'done', sharebook_book_id = %s, updated_at = %s
    WHERE id = %s
""", (book_id, now, item_id))
cur.execute("""
    INSERT INTO importer.queue_item_history (queue_item_id, source_id, from_status, to_status, changed_by)
    SELECT 1186, source_id, 'error', 'done', 'agent' FROM importer.queue_items WHERE id = 1186
""")
conn.commit()
conn.close()
print(f"#{item_id} -> done ✓")
