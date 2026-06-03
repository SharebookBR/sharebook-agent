import sys, base64, json
sys.path.insert(0, r"C:\Repos\SHAREBOOK\sharebook-agent\scripts\production")

from pathlib import Path
from dotenv import dotenv_values
import psycopg2, boto3
from datetime import datetime, timezone
from sharebook_prod_auth import API_BASE, auth_headers, get_token, load_env, request_json

REPO_ROOT = Path(r"C:\Repos\SHAREBOOK\sharebook-agent")
env = load_env(REPO_ROOT)
token = get_token(env, repo_root=REPO_ROOT)

FAKE_PDF = Path(r"C:\Temp\fake.pdf")
if not FAKE_PDF.exists():
    FAKE_PDF.write_bytes(
        b"%PDF-1.0\n1 0 obj<</Type /Catalog /Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type /Pages /Kids [3 0 R] /Count 1>>endobj\n"
        b"3 0 obj<</Type /Page /MediaBox [0 0 3 3]>>endobj\n"
        b"xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n"
        b"0000000058 00000 n\n0000000115 00000 n\n"
        b"trailer<</Size 4 /Root 1 0 R>>\nstartxref\n190\n%%EOF"
    )

conn = psycopg2.connect(
    host="212.85.23.202", port=5432, dbname="sharebook_importer",
    user="sharebook_ai_rw", password="F%Ljy9oxTA3iR#npW%4W9iaSaJKU", sslmode="disable"
)
cur = conn.cursor()

cur.execute("""
    SELECT qi.id, qi.planned_title, qi.planned_author, qi.planned_synopsis,
           qi.planned_category_id, qi.metadata_json
    FROM importer.queue_items qi
    WHERE qi.id = 1302 AND qi.status = 'waiting_process'
""")
row = cur.fetchone()
if not row:
    print("Item 1302 não está em waiting_process — abortando.")
    sys.exit(1)

item_id, title, author, synopsis, cat_id, meta = row
preview_pages = meta.get("triage", {}).get("preview_pages", [])
cover_path = Path(preview_pages[0]) if preview_pages else None

print(f"Publicando #{item_id}: {title}")

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
print(f"  create response: {json.dumps(create_resp, ensure_ascii=False)[:200]}")

# Buscar o livro criado pelo título/autor
from sharebook_prod_book import find_exact_book, approve_book
book = find_exact_book(token, title, author, book_type="Eletronic")
if not book:
    print("ERRO: livro não encontrado após criação.")
    sys.exit(1)

book_id = book["id"]
ebook_pdf_path = book.get("eBookPdfPath") or book.get("eBookPDFPath")
print(f"  book_id={book_id}  pdf_path={ebook_pdf_path}")

# Aprovar
approve_book(token, book_id)
print(f"  aprovado ✓")

# Upload PDF real para S3
real_pdf = Path(r"C:\Users\raffa\Downloads") / f"{item_id}.pdf"
s3 = boto3.client("s3",
    aws_access_key_id=env["AWS_S3_ACCESS_KEY"],
    aws_secret_access_key=env["AWS_S3_SECRET_KEY"],
    region_name=env.get("AWS_S3_REGION", "sa-east-1")
)
s3.upload_file(str(real_pdf), env["AWS_S3_BUCKET"], ebook_pdf_path)
print(f"  S3 upload OK → {ebook_pdf_path}")

# Marca done no importer
now = datetime.now(timezone.utc)
cur.execute("""
    UPDATE importer.queue_items
    SET status = 'done', sharebook_book_id = %s, updated_at = %s
    WHERE id = %s
""", (book_id, now, item_id))
conn.commit()
conn.close()
print(f"#{item_id} → done ✓")
