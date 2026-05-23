"""Aplica plan-set num item da fila do importer diretamente no banco.

Uso:
    python plan_set.py --id 1046 --category-id <UUID> --synopsis-file <path>
                       [--title <title>] [--author <author>] [--planned-by <who>]
                       [--cover-url <url>]
"""
from __future__ import annotations
import argparse
from pathlib import Path
import psycopg2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=int, required=True)
    parser.add_argument("--category-id", required=True)
    parser.add_argument("--synopsis-file", required=True)
    parser.add_argument("--title")
    parser.add_argument("--author")
    parser.add_argument("--planned-by", default="claude-windows-local")
    parser.add_argument("--cover-url")
    args = parser.parse_args()

    synopsis = Path(args.synopsis_file).read_text(encoding="utf-8-sig").strip()

    conn = psycopg2.connect(
        host="212.85.23.202", port=5432, dbname="sharebook_importer",
        user="sharebook_ai_rw", password="F%Ljy9oxTA3iR#npW%4W9iaSaJKU", sslmode="disable"
    )
    cur = conn.cursor()

    cur.execute("""
        UPDATE importer.queue_items SET
            planned_title       = COALESCE(%s, title),
            planned_author      = COALESCE(%s, author),
            planned_category_id = %s,
            planned_synopsis    = %s,
            planned_by          = %s,
            planned_cover_url   = %s,
            status              = 'waiting_process',
            updated_at          = NOW()
        WHERE id = %s
    """, (
        args.title,
        args.author,
        args.category_id,
        synopsis,
        args.planned_by,
        args.cover_url,
        args.id,
    ))

    if cur.rowcount != 1:
        conn.rollback()
        print(f"ERRO: item {args.id} não encontrado ou não atualizado.")
        return 1

    conn.commit()
    print(f"✓ Item {args.id} → waiting_process")
    print(f"  category_id: {args.category_id}")
    print(f"  planned_by:  {args.planned_by}")
    print(f"  synopsis:    {synopsis[:80]}...")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
