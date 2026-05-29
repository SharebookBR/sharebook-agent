# Publica os 5 itens usando um PDF fake (placeholder).
# Apos a publicacao, substitui os PDFs reais no S3 usando o eBookPdfPath retornado.
#
# Uso: python publish_fake_pdf_1265_1298.py
# Pre-requisito: C:\Temp\fake.pdf existe (PDF valido minimo)

from __future__ import annotations

import json
import subprocess
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import psycopg2

FAKE_PDF = Path(r"C:\Temp\fake.pdf")
COVER_DIR = Path(r"C:\Repos\SHAREBOOK\sharebook-ebook-importer\var\triage\preview-pages")
SYNOPSIS_DIR = Path(r"C:\Temp\synopses")
PROD_BOOK_SCRIPT = Path(r"C:\Repos\SHAREBOOK\sharebook-agent\scripts\production\sharebook_prod_book.py")

ITEM_IDS = [1265, 1268, 1295, 1297, 1298]

COVER_MAP = {
    1265: COVER_DIR / "1265-page-001.png",
    1268: COVER_DIR / "1268-page-001.png",
    1295: COVER_DIR / "1295-page-001.png",
    1297: COVER_DIR / "1297-page-001.png",
    1298: COVER_DIR / "1298-page-01.png",
}

REAL_PDF_MAP = {
    1265: Path(r"C:\Users\raffa\Downloads\1265.pdf"),
    1268: Path(r"C:\Users\raffa\Downloads\1268.pdf"),
    1295: Path(r"C:\Users\raffa\Downloads\1295.pdf"),
    1297: Path(r"C:\Users\raffa\Downloads\1297.pdf"),
    1298: Path(r"C:\Users\raffa\Downloads\1298.pdf"),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    with open(r"C:\Repos\SHAREBOOK\sharebook-agent\.env", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"')
    return env


def pg_connect(dsn: str):
    prefix = "postgresql://"
    rest = dsn[len(prefix):]
    userpass, hostdb = rest.rsplit("@", 1)
    user, password = userpass.split(":", 1)
    hostport, database = hostdb.split("/", 1)
    host, port = hostport.split(":", 1)
    return psycopg2.connect(
        user=urllib.parse.unquote(user),
        password=urllib.parse.unquote(password),
        host=host,
        port=int(port),
        dbname=database,
    )


def fetch_items(conn, ids: list[int]) -> list[dict]:
    with conn.cursor() as cur:
        placeholders = ",".join(["%s"] * len(ids))
        cur.execute(
            f"""
            SELECT id, planned_title, planned_author, planned_category_id,
                   planned_synopsis, metadata_json
            FROM importer.queue_items
            WHERE id IN ({placeholders})
            ORDER BY id
            """,
            ids,
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def write_synopsis(item_id: int, synopsis: str) -> Path:
    SYNOPSIS_DIR.mkdir(parents=True, exist_ok=True)
    p = SYNOPSIS_DIR / f"{item_id}.txt"
    p.write_text(synopsis, encoding="utf-8")
    return p


def publish_item(item: dict) -> dict:
    item_id = item["id"]
    synopsis_path = write_synopsis(item_id, item["planned_synopsis"])
    cover_path = COVER_MAP[item_id]

    cmd = [
        sys.executable,
        str(PROD_BOOK_SCRIPT),
        "create",
        "--title", item["planned_title"],
        "--author", item["planned_author"],
        "--category-id", item["planned_category_id"],
        "--type", "Eletronic",
        "--synopsis-file", str(synopsis_path),
        "--image-path", str(cover_path),
        "--pdf-path", str(FAKE_PDF),
        "--approve",
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=120)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "").strip())
    return json.loads(proc.stdout)


def mark_done(conn, item_id: int, result: dict) -> None:
    book = result.get("book") or {}
    book_id = book.get("id")
    pdf_path = book.get("eBookPdfPath", "")

    with conn.cursor() as cur:
        cur.execute(
            "SELECT metadata_json FROM importer.queue_items WHERE id=%s", (item_id,)
        )
        row = cur.fetchone()
        meta: dict = {}
        if row and row[0]:
            meta = row[0] if isinstance(row[0], dict) else json.loads(row[0])

        meta["publish_result"] = {
            "sharebook_book_id": book_id,
            "ebook_pdf_path": pdf_path,
            "real_pdf": str(REAL_PDF_MAP[item_id]),
            "published_at": utc_now(),
            "note": "published with fake PDF placeholder — real PDF pending S3 upload",
        }

        cur.execute(
            """
            UPDATE importer.queue_items
            SET status='done',
                sharebook_book_id=%s,
                last_error=NULL,
                metadata_json=%s,
                updated_at=%s
            WHERE id=%s
            """,
            (book_id, json.dumps(meta, ensure_ascii=False), utc_now(), item_id),
        )


def main() -> None:
    if not FAKE_PDF.exists():
        print(f"ERRO: fake PDF nao encontrado em {FAKE_PDF}", file=sys.stderr)
        sys.exit(1)

    env = load_env()
    conn = pg_connect(env["IMPORTER_DB_DSN"])

    items = fetch_items(conn, ITEM_IDS)
    print(f"\nPublicando {len(items)} itens com PDF fake...\n")

    results = []
    for item in items:
        item_id = item["id"]
        print(f"  #{item_id} {item['planned_title'][:55]}")
        try:
            result = publish_item(item)
            book = result.get("book") or {}
            book_id = book.get("id", "?")
            pdf_path = book.get("eBookPdfPath", "?")
            print(f"    -> OK  book_id={book_id}")
            print(f"    -> S3 path: {pdf_path}")
            mark_done(conn, item_id, result)
            conn.commit()
            results.append({"item_id": item_id, "book_id": book_id, "s3_pdf_path": pdf_path,
                            "real_pdf": str(REAL_PDF_MAP[item_id])})
        except Exception as exc:
            print(f"    -> ERRO: {exc}", file=sys.stderr)
            conn.rollback()

    conn.close()

    print(f"\n{'='*60}")
    print("S3 replacements needed:")
    for r in results:
        print(f"  item #{r['item_id']}  s3={r['s3_pdf_path']}")
        print(f"    real pdf: {r['real_pdf']}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
