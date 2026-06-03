#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
from pathlib import Path

import psycopg2

IMPORTER_ENV_PATH = Path("/data/workspace/sharebook-ebook-importer/.env")


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description="Register curated ebook_foundation item in importer queue")
    parser.add_argument("--item-id", type=int, required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--author", required=True)
    parser.add_argument("--category-id", required=True)
    parser.add_argument("--synopsis-file", required=True)
    parser.add_argument("--cover-url", required=True, help="Relative path from project root, e.g. triage-downloads/foo-cover.jpg")
    parser.add_argument("--cover-path", required=True, help="Absolute cover path in workspace")
    parser.add_argument("--pdf-md5", required=True)
    parser.add_argument("--cover-palette", default="unknown")
    parser.add_argument("--level", choices=["basico", "intermediario", "avancado"], required=True)
    parser.add_argument("--cover-style", default="pillow")
    parser.add_argument("--synopsis-source", default="pdf_toc")
    args = parser.parse_args()

    synopsis = Path(args.synopsis_file).read_text(encoding="utf-8").strip()
    env = load_env(IMPORTER_ENV_PATH)
    dsn = env["IMPORTER_DB_DSN"]
    parsed = urllib.parse.urlparse(dsn)
    password = urllib.parse.unquote(parsed.password or "")

    metadata_patch = {
        "cover_palette": args.cover_palette,
        "cover_style": args.cover_style,
        "synopsis_source": args.synopsis_source,
        "cover_path": args.cover_path,
        "pdf_md5": args.pdf_md5,
        "current_level": args.level,
    }

    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        dbname=parsed.path.lstrip("/"),
        user=parsed.username,
        password=password,
    )
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE importer.queue_items SET
          planned_title = %s,
          planned_author = %s,
          planned_category_id = %s,
          planned_synopsis = %s,
          planned_cover_mode = 'source',
          planned_cover_url = %s,
          metadata_json = metadata_json || %s::jsonb,
          status = 'waiting_process',
          last_error = NULL,
          updated_at = NOW()
        WHERE id = %s
        """,
        (
            args.title,
            args.author,
            args.category_id,
            synopsis,
            args.cover_url,
            json.dumps(metadata_patch, ensure_ascii=False),
            args.item_id,
        ),
    )
    conn.commit()
    cur.close()
    conn.close()
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
