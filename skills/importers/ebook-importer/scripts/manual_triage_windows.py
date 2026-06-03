# Triagem manual de itens source_blocked -- replica TriageWorker.run_once() no Windows.
#
# Uso:
#     python manual_triage_windows.py --ids 1265 1268 1295 1297 1298
#
# Comportamento:
# - Le o PDF de Downloads/<id>.pdf
# - Valida magic bytes (%PDF-)
# - Extrai texto das primeiras 15 paginas (pypdf, fallback fitz)
# - Checa duplicata em producao pelo titulo exato
# - Monta metadata_json no formato canonico do worker
# - Cria run, marca triaging -> waiting_editor, fecha run
# - Em caso de falha: marca source_blocked com last_error

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg2


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DOWNLOADS_DIR = Path(r"C:\Users\raffa\Downloads")
ENV_PATH = Path(r"C:\Repos\SHAREBOOK\sharebook-agent\.env")


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    with open(ENV_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"')
    return env


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# PDF utils  (replicam _looks_like_pdf, _extract_pdf_text, _is_probably_invalid_pdf)
# ---------------------------------------------------------------------------

def looks_like_pdf(pdf_path: Path) -> bool:
    try:
        return pdf_path.read_bytes()[:8].startswith(b"%PDF-")
    except OSError:
        return False


def extract_pdf_text(pdf_path: Path) -> str:
    try:
        try:
            from pypdf import PdfReader
            reader = PdfReader(pdf_path)
            parts = []
            for i in range(min(15, len(reader.pages))):
                t = reader.pages[i].extract_text()
                if t:
                    parts.append(t)
            return " ".join(" ".join(parts).split()[:2000])
        except ModuleNotFoundError:
            import fitz
            doc = fitz.open(pdf_path)
            parts = []
            for i in range(min(15, doc.page_count)):
                t = doc.load_page(i).get_text("text")
                if t:
                    parts.append(t)
            return " ".join(" ".join(parts).split()[:2000])
    except Exception as exc:
        print(f"  [WARN] extração de texto falhou: {exc}", file=sys.stderr)
        return ""


def is_probably_invalid_pdf(pdf_path: Path, pdf_text: str) -> bool:
    # pdftoppm não disponível no Windows na maioria dos casos → preview_pages = []
    # Regra: inválido apenas se < 50 KB E sem texto (sem preview disponível)
    size = pdf_path.stat().st_size
    if size >= 50_000:
        return False
    return not bool((pdf_text or "").strip())


# ---------------------------------------------------------------------------
# Prod duplicate check  (replica _check_prod_duplicate)
# ---------------------------------------------------------------------------

def check_prod_duplicate(title: str, env: dict[str, str]) -> bool:
    host = env.get("SHAREBOOK_PROD_PG_RO_HOST")
    if not host:
        print("  [WARN] SHAREBOOK_PROD_PG_RO_HOST ausente — pulando checagem de duplicata", file=sys.stderr)
        return False
    try:
        conn = psycopg2.connect(
            host=host,
            port=env.get("SHAREBOOK_PROD_PG_RO_PORT", "5432"),
            database=env.get("SHAREBOOK_PROD_PG_RO_DATABASE", "sharebook"),
            user=env.get("SHAREBOOK_PROD_PG_RO_USER"),
            password=env.get("SHAREBOOK_PROD_PG_RO_PASSWORD"),
            connect_timeout=5,
        )
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT 1 FROM "Books" WHERE "Title" = %s LIMIT 1', (title,))
                return cur.fetchone() is not None
    except Exception as exc:
        print(f"  [WARN] checagem de duplicata falhou: {exc}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# DB helpers  (replicam pg_db.PostgresDatabase)
# ---------------------------------------------------------------------------

def pg_connect(dsn: str):
    import urllib.parse
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


def db_create_run(conn, item_id: int, message: str) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO importer.runs (started_at, status, processed_item_id, message)
            VALUES (%s, 'running', %s, %s) RETURNING id
            """,
            (utc_now(), item_id, message),
        )
        return int(cur.fetchone()[0])


def db_finish_run(conn, run_id: int, status: str, message: str, details_json: str | None = None) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE importer.runs
            SET finished_at=%s, status=%s, message=%s, details_json=%s
            WHERE id=%s
            """,
            (utc_now(), status, message, details_json, run_id),
        )


def db_mark_item(conn, item_id: int, status: str, *,
                 attempts_delta: int = 0,
                 last_error: str | None = None,
                 metadata_json: str | None = None) -> None:
    with conn.cursor() as cur:
        # Lê estado atual para fazer merge de metadata (igual pg_db.mark_item)
        cur.execute(
            "SELECT metadata_json, retry_count, max_retries FROM importer.queue_items WHERE id=%s",
            (item_id,),
        )
        current = cur.fetchone()
        current_meta = current[0] if current else None

        if metadata_json is not None and current_meta is not None:
            existing = current_meta if isinstance(current_meta, dict) else json.loads(current_meta)
            incoming = metadata_json if isinstance(metadata_json, dict) else json.loads(metadata_json)
            effective_metadata: str | None = json.dumps({**existing, **incoming}, ensure_ascii=False)
        elif metadata_json is not None:
            effective_metadata = metadata_json
        else:
            effective_metadata = current_meta if isinstance(current_meta, str) else (
                json.dumps(current_meta, ensure_ascii=False) if current_meta else None
            )

        cur.execute(
            """
            UPDATE importer.queue_items
            SET status=%s,
                attempts=attempts + %s,
                last_error=%s,
                metadata_json=%s,
                updated_at=%s
            WHERE id=%s
            """,
            (status, attempts_delta, last_error, effective_metadata, utc_now(), item_id),
        )


def db_set_author_if_missing(conn, item_id: int, author: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE importer.queue_items
            SET author = COALESCE(NULLIF(author, ''), %s),
                planned_author = COALESCE(NULLIF(planned_author, ''), %s),
                updated_at=%s
            WHERE id=%s
            """,
            (author.strip(), author.strip(), utc_now(), item_id),
        )


def db_update_title(conn, item_id: int, title: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE importer.queue_items
            SET title=%s, updated_at=%s
            WHERE id=%s AND title != %s
            """,
            (title.strip(), utc_now(), item_id, title.strip()),
        )


# ---------------------------------------------------------------------------
# Triage de um item
# ---------------------------------------------------------------------------

def triage_item(conn, env: dict[str, str], item: dict) -> bool:
    item_id = item["id"]
    title = str(item["title"] or "").strip()
    author = str(item["author"] or "").strip()
    source_url = str(item["source_url"] or "").strip()
    item_label = f"#{item_id:04d} {title}"

    print(f"\n{'='*60}")
    print(f"  Triando: {item_label}")
    print(f"{'='*60}")

    run_id = db_create_run(conn, item_id, "manual triage running")
    conn.commit()

    try:
        # 1. Marca triaging
        db_mark_item(conn, item_id, "triaging", attempts_delta=1)
        conn.commit()

        # 2. Localiza PDF
        pdf_path = DOWNLOADS_DIR / f"{item_id}.pdf"
        if not pdf_path.exists():
            raise ValueError(f"PDF não encontrado em {pdf_path}")

        # 3. Valida magic bytes
        if not looks_like_pdf(pdf_path):
            raise ValueError(f"conteúdo inválido: sem cabeçalho PDF válido em {pdf_path.name}")

        print(f"  PDF: {pdf_path.name}  ({pdf_path.stat().st_size:,} bytes)  [OK]")

        # 4. Extrai texto
        pdf_text = extract_pdf_text(pdf_path)
        word_count = len(pdf_text.split()) if pdf_text else 0
        print(f"  Texto extraído: {word_count} palavras")

        # 5. Valida conteúdo mínimo
        if is_probably_invalid_pdf(pdf_path, pdf_text):
            raise ValueError("conteúdo inválido: pdf sem texto útil (< 50 KB e sem texto extraível)")

        # 6. Checa duplicata em produção
        is_dup = check_prod_duplicate(title, env)
        if is_dup:
            print(f"  [DUPLICATA] '{title}' já existe em produção")
            metadata = {
                "local_pdf": pdf_path.name,
                "manifest": {
                    "source_name": "ebook_foundation_subjects",
                    "source_url": source_url,
                    "downloaded_pdf_path": str(pdf_path),
                },
                "triage": {"mode": "manual_windows", "reason": "exact_title_match_in_production"},
            }
            db_mark_item(conn, item_id, "duplicate",
                         last_error="duplicata detectada em produção (título exato)",
                         metadata_json=json.dumps(metadata, ensure_ascii=False))
            db_finish_run(conn, run_id, "ok", f"triage duplicate: {item_label}",
                          details_json=json.dumps(metadata, ensure_ascii=False))
            conn.commit()
            print(f"  → duplicate")
            return True

        # 7. Monta context_text (mesmo formato do worker)
        context_parts = [f"PDF TEXT (FIRST 2000 WORDS):\n{pdf_text}"]
        context_text = "\n\n".join(context_parts)

        # 8. Monta metadata_json (formato canônico)
        metadata = {
            "local_pdf": pdf_path.name,
            "manifest": {
                "source_name": "ebook_foundation_subjects",
                "source_url": source_url,
                "downloaded_pdf_path": str(pdf_path),
                "title": title,
                "author": author,
            },
            "triage": {
                "mode": "manual_windows",
                "reason": "passed_mechanical_triage",
                "context_text": context_text,
                "preview_pages": [],
            },
        }

        # 9. Marca waiting_editor
        db_mark_item(conn, item_id, "waiting_editor",
                     last_error=None,
                     metadata_json=json.dumps(metadata, ensure_ascii=False))
        if author:
            db_set_author_if_missing(conn, item_id, author)
        if title:
            db_update_title(conn, item_id, title)

        db_finish_run(conn, run_id, "ok", f"triage ok: {item_label}",
                      details_json=json.dumps(metadata, ensure_ascii=False))
        conn.commit()
        print(f"  → waiting_editor  ✓")
        return True

    except Exception as exc:
        message = str(exc)
        print(f"  [ERRO] {message}", file=sys.stderr)
        try:
            db_mark_item(conn, item_id, "source_blocked", last_error=message)
            db_finish_run(conn, run_id, "error", message)
            conn.commit()
        except Exception as db_exc:
            print(f"  [ERRO DB] {db_exc}", file=sys.stderr)
            conn.rollback()
        print(f"  → source_blocked")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Triagem manual de itens no Windows")
    parser.add_argument("--ids", nargs="+", type=int, required=True, help="IDs da fila")
    parser.add_argument("--dry-run", action="store_true", help="Simula sem gravar no banco")
    args = parser.parse_args()

    env = load_env()
    dsn = env.get("IMPORTER_DB_DSN", "")
    if not dsn:
        print("ERRO: IMPORTER_DB_DSN não encontrado no .env", file=sys.stderr)
        sys.exit(1)

    conn = pg_connect(dsn)

    # Busca os itens
    with conn.cursor() as cur:
        placeholders = ",".join(["%s"] * len(args.ids))
        cur.execute(
            f"""
            SELECT id, source_id, title, author, status, source_url
            FROM importer.queue_items
            WHERE id IN ({placeholders})
            ORDER BY id DESC
            """,
            args.ids,
        )
        cols = [d[0] for d in cur.description]
        items = [dict(zip(cols, row)) for row in cur.fetchall()]

    if not items:
        print("Nenhum item encontrado para os IDs informados.", file=sys.stderr)
        sys.exit(1)

    print(f"\nItens encontrados: {len(items)}")
    for item in items:
        print(f"  #{item['id']}  {item['title']}  [{item['status']}]")

    if args.dry_run:
        print("\n[DRY-RUN] Nenhuma alteração gravada.")
        sys.exit(0)

    ok = 0
    fail = 0
    for item in items:
        success = triage_item(conn, env, item)
        if success:
            ok += 1
        else:
            fail += 1

    conn.close()
    print(f"\n{'='*60}")
    print(f"  Resultado: {ok} ok  |  {fail} falhou")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
