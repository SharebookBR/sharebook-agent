# Publica item do ciclo manual Windows: PDF fake + upload S3 real.
#
# Uso:
#     python publish_fake_pdf.py --id 1186
#
# Pré-requisitos:
#   - PDF real em C:\Users\raffa\Downloads\<id>.pdf
#   - Plano editorial completo no banco (author, synopsis, category_id)
#   - Capa em metadata_json.triage.preview_pages[0] (rodar render_covers.py antes)
#   - C:\Temp\fake.pdf existente (PDF mínimo de ~287 bytes)
#   - Token válido em .env (rodar sharebook_refresh_token.py se necessário)
#
# Fluxo:
#   1. Publica com fake.pdf → livro criado, slug e S3 key retornados
#   2. Aprova o livro
#   3. Upload do PDF real para o S3 key retornado
#   4. Marca item como done no banco

from __future__ import annotations

import argparse
import base64
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, r"C:\Repos\SHAREBOOK\sharebook-agent\scripts\production")

import psycopg2
import boto3
from sharebook_prod_auth import API_BASE, auth_headers, get_token, load_env, request_json
from sharebook_prod_book import find_exact_book, approve_book

REPO_ROOT = Path(r"C:\Repos\SHAREBOOK\sharebook-agent")
FAKE_PDF = Path(r"C:\Temp\fake.pdf")
DOWNLOADS_DIR = Path(r"C:\Users\raffa\Downloads")


def publish_one(item_id: int, env: dict, token: str, cur) -> None:
    cur.execute("""
        SELECT id, title, planned_title, planned_author, planned_synopsis,
               planned_category_id, metadata_json
        FROM importer.queue_items WHERE id = %s
    """, (item_id,))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"Item {item_id} não encontrado")

    _, raw_title, planned_title, author, synopsis, cat_id, meta = row
    title = planned_title or raw_title

    if not all([title, author, synopsis, cat_id]):
        raise ValueError(f"Plano incompleto — title={title!r} author={author!r} cat={cat_id!r}")

    preview_pages = (meta or {}).get("triage", {}).get("preview_pages", [])
    cover_path = Path(preview_pages[0]) if preview_pages else None
    cover_bytes = cover_path.read_bytes() if cover_path and cover_path.exists() else b""
    cover_name = cover_path.name if cover_path else "cover.png"

    real_pdf = DOWNLOADS_DIR / f"{item_id}.pdf"
    if not real_pdf.exists():
        raise FileNotFoundError(f"PDF real não encontrado: {real_pdf}")

    print(f"  título:  {title}")
    print(f"  autor:   {author}")
    print(f"  capa:    {cover_path}")

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

    resp = request_json(f"{API_BASE}/Book", method="POST",
                        body=payload, headers=auth_headers(token))
    print(f"  create:  {resp.get('successMessage') or resp}")

    book = find_exact_book(token, title, author, book_type="Eletronic")
    if not book:
        raise ValueError("Livro não encontrado após criação")

    book_id = book["id"]
    ebook_pdf_path = book.get("eBookPdfPath") or book.get("eBookPDFPath")
    print(f"  book_id: {book_id}")
    print(f"  s3_key:  {ebook_pdf_path}")

    approve_book(token, book_id)
    print("  aprovado ✓")

    s3 = boto3.client("s3",
        aws_access_key_id=env["AWS_S3_ACCESS_KEY"],
        aws_secret_access_key=env["AWS_S3_SECRET_KEY"],
        region_name=env.get("AWS_S3_REGION", "sa-east-1")
    )
    s3.upload_file(str(real_pdf), env["AWS_S3_BUCKET"], ebook_pdf_path,
                   ExtraArgs={"ContentType": "application/pdf"})
    print(f"  S3 upload OK")

    now = datetime.now(timezone.utc)
    cur.execute("""
        UPDATE importer.queue_items
        SET status = 'done', sharebook_book_id = %s, updated_at = %s
        WHERE id = %s
    """, (book_id, now, item_id))
    cur.execute("""
        INSERT INTO importer.queue_item_history
            (queue_item_id, source_id, from_status, to_status, changed_by)
        SELECT %s, source_id, status, 'done', 'agent'
        FROM importer.queue_items WHERE id = %s
    """, (item_id, item_id))


def main() -> None:
    parser = argparse.ArgumentParser(description="Publica item via fake PDF + S3 real")
    parser.add_argument("--id", type=int, required=True, dest="item_id")
    args = parser.parse_args()

    if not FAKE_PDF.exists():
        print(f"ERRO: {FAKE_PDF} não existe — crie o fake.pdf antes.", file=sys.stderr)
        sys.exit(1)

    env = load_env(REPO_ROOT)
    token = get_token(env, repo_root=REPO_ROOT)

    conn = psycopg2.connect(
        host="212.85.23.202", port=5432, dbname="sharebook_importer",
        user="sharebook_ai_rw", password="F%Ljy9oxTA3iR#npW%4W9iaSaJKU", sslmode="disable"
    )
    cur = conn.cursor()

    print(f"Publicando #{args.item_id}...")
    try:
        publish_one(args.item_id, env, token, cur)
        conn.commit()
        print(f"#{args.item_id} -> done ✓")
    except Exception as exc:
        conn.rollback()
        print(f"ERRO: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
