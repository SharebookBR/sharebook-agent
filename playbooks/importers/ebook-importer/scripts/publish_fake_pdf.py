# Publica item do ciclo manual Windows: PDF fake + upload S3 real.
#
# Uso:
#     python publish_fake_pdf.py --id 1186 --pdf-path C:\Temp\1186.pdf \
#       --cover-path C:\Temp\1186-cover.jpg
#
# Pré-requisitos:
#   - PDF real informado por --pdf-path ou em C:\Users\raffa\Downloads\<id>.pdf
#   - Plano editorial completo no banco (author, synopsis, category_id)
#   - Capa final informada por --cover-path ou em metadata_json.triage.preview_pages[0]
#   - C:\Temp\fake.pdf existente (PDF mínimo de ~287 bytes)
#   - Credenciais e token em .env (401/403 dispara renovação automática)
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

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "production"))

import psycopg2
import boto3
from sharebook_prod_auth import (
    API_BASE,
    ApiHttpError,
    auth_headers,
    get_token,
    load_env,
    request_json,
)
from sharebook_prod_book import find_exact_book, approve_book

FAKE_PDF = Path(r"C:\Temp\fake.pdf")
DOWNLOADS_DIR = Path(r"C:\Users\raffa\Downloads")


def publish_one(
    item_id: int,
    env: dict,
    token: str,
    cur,
    *,
    real_pdf: Path,
    explicit_cover: Path | None,
) -> None:
    cur.execute("""
        SELECT id, source_id, status, title, planned_title, planned_author,
               planned_synopsis, planned_category_id, metadata_json
        FROM importer.queue_items WHERE id = %s
    """, (item_id,))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"Item {item_id} não encontrado")

    _, source_id, from_status, raw_title, planned_title, author, synopsis, cat_id, meta = row
    title = planned_title or raw_title

    if not all([title, author, synopsis, cat_id]):
        raise ValueError(f"Plano incompleto — title={title!r} author={author!r} cat={cat_id!r}")

    preview_pages = (meta or {}).get("triage", {}).get("preview_pages", [])
    cover_path = explicit_cover or (Path(preview_pages[0]) if preview_pages else None)
    if not cover_path or not cover_path.is_file():
        raise FileNotFoundError(f"Capa final não encontrada: {cover_path}")
    if not real_pdf.exists():
        raise FileNotFoundError(f"PDF real não encontrado: {real_pdf}")
    cover_bytes = cover_path.read_bytes()
    cover_name = cover_path.name

    print(f"  título:  {title}")
    print(f"  autor:   {author}")
    print(f"  capa:    {cover_path}")
    print(f"  pdf:     {real_pdf}")

    book = find_exact_book(token, title, author, book_type="Eletronic")
    if not book:
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
        resp = request_json(
            f"{API_BASE}/Book",
            method="POST",
            body=payload,
            headers=auth_headers(token),
        )
        print(f"  create:  {resp.get('successMessage') or resp}")
        book = find_exact_book(token, title, author, book_type="Eletronic")
        if not book:
            raise ValueError("Livro não encontrado após criação")
    else:
        print(f"  create:  livro já existente, reutilizando {book['id']}")

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
        SET status = 'done', sharebook_book_id = %s, last_error = NULL,
            retry_after = NULL, updated_at = %s
        WHERE id = %s
    """, (book_id, now, item_id))
    cur.execute("""
        INSERT INTO importer.queue_item_history
            (queue_item_id, source_id, from_status, to_status, changed_by)
        VALUES (%s, %s, %s, 'done', 'agent')
    """, (item_id, source_id, from_status))


def main() -> None:
    parser = argparse.ArgumentParser(description="Publica item via fake PDF + S3 real")
    parser.add_argument("--id", type=int, required=True, dest="item_id")
    parser.add_argument(
        "--pdf-path",
        type=Path,
        help="PDF real a enviar ao S3 (padrão: Downloads/<id>.pdf).",
    )
    parser.add_argument(
        "--cover-path",
        type=Path,
        help="Capa final local; se omitida, tenta preview_pages[0].",
    )
    args = parser.parse_args()

    if not FAKE_PDF.exists():
        print(f"ERRO: {FAKE_PDF} não existe — crie o fake.pdf antes.", file=sys.stderr)
        sys.exit(1)

    env = load_env(REPO_ROOT)
    token = get_token(env, repo_root=REPO_ROOT)
    real_pdf = args.pdf_path or DOWNLOADS_DIR / f"{args.item_id}.pdf"

    importer_dsn = env.get("IMPORTER_DB_DSN")
    if not importer_dsn:
        raise SystemExit("IMPORTER_DB_DSN ausente no .env")
    conn = psycopg2.connect(importer_dsn)
    cur = conn.cursor()

    print(f"Publicando #{args.item_id}...")
    try:
        try:
            publish_one(
                args.item_id,
                env,
                token,
                cur,
                real_pdf=real_pdf,
                explicit_cover=args.cover_path,
            )
        except ApiHttpError as exc:
            if exc.code not in {401, 403}:
                raise
            conn.rollback()
            token = get_token(env, repo_root=REPO_ROOT, force_refresh=True)
            publish_one(
                args.item_id,
                env,
                token,
                cur,
                real_pdf=real_pdf,
                explicit_cover=args.cover_path,
            )
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
