"""Parseia o free-programming-books-subjects.md (EbookFoundation) e insere
entradas com link direto de PDF como waiting_triage no banco do importer.

Uso:
    python crawl_ebook_foundation_subjects.py [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import urllib.request
from urllib.request import Request, urlopen

import psycopg2

SOURCE_NAME = "ebook_foundation_subjects"
RAW_MD_URL  = "https://raw.githubusercontent.com/EbookFoundation/free-programming-books/main/books/free-programming-books-subjects.md"
USER_AGENT  = "Mozilla/5.0"

ITEM_RE    = re.compile(r"^\* \[(?P<title>.+?)\]\((?P<url>https?://[^)]+)\)(?: - (?P<rest>.*))?$")
HEADING_RE = re.compile(r"^(#{3,4})\s+(?P<name>.+?)\s*$")  # ### subject, #### sub-subject


def fetch_markdown(url: str) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def is_pdf_entry(url: str, rest: str) -> bool:
    if url.lower().endswith(".pdf"):
        return True
    if rest and "(pdf)" in rest.lower():
        return True
    return False


def extract_author(rest: str) -> str | None:
    if not rest:
        return None
    author = rest.split("(", 1)[0].strip().strip("-").strip()
    return author or None


def parse_subjects(text: str) -> list[dict]:
    """Returns list of {title, url, author, subject} — PDF-only entries."""
    entries: list[dict] = []
    current_path: list[str] = []
    in_index = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        # Skip the table-of-contents block (### Index section)
        if line == "### Index":
            in_index = True
            continue
        if in_index:
            # First real section heading exits the index
            if HEADING_RE.match(line):
                in_index = False
            else:
                continue

        heading_match = HEADING_RE.match(line)
        if heading_match:
            level = len(heading_match.group(1))
            name = heading_match.group("name").strip()
            depth = level - 3  # ### → depth 0, #### → depth 1
            current_path = current_path[:depth]
            current_path.append(name)
            continue

        item_match = ITEM_RE.match(line)
        if not item_match:
            continue

        url  = item_match.group("url").strip()
        rest = (item_match.group("rest") or "").strip()
        if not is_pdf_entry(url, rest):
            continue

        entries.append({
            "title":   item_match.group("title").strip(),
            "url":     url,
            "author":  extract_author(rest),
            "subject": " > ".join(current_path) if current_path else None,
        })

    return entries


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Não insere no banco, só imprime")
    args = parser.parse_args()

    print(f"Buscando markdown: {RAW_MD_URL}")
    text = fetch_markdown(RAW_MD_URL)
    entries = parse_subjects(text)
    print(f"Entradas PDF encontradas: {len(entries)}")

    if args.dry_run:
        for e in entries[:20]:
            print(f"  [{e['subject']}] {e['title']} — {e['author']} — {e['url']}")
        if len(entries) > 20:
            print(f"  ... (+{len(entries) - 20} mais)")
        return 0

    conn = psycopg2.connect(
        host="212.85.23.202", port=5432, dbname="sharebook_importer",
        user="sharebook_ai_rw", password="F%Ljy9oxTA3iR#npW%4W9iaSaJKU", sslmode="disable"
    )
    conn.autocommit = False
    cur = conn.cursor()

    cur.execute("SELECT id FROM importer.sources WHERE name = %s", (SOURCE_NAME,))
    row = cur.fetchone()
    if not row:
        raise SystemExit(f"Source '{SOURCE_NAME}' não encontrada. Crie-a no banco primeiro.")
    source_id = row[0]
    print(f"Source ID: {source_id}")

    cur.execute("SELECT source_url FROM importer.queue_items WHERE source_id = %s", (source_id,))
    existing = {r[0] for r in cur.fetchall()}
    print(f"Itens já existentes: {len(existing)}")

    new_entries = [e for e in entries if e["url"] not in existing]
    print(f"Itens novos a inserir: {len(new_entries)}")

    if not new_entries:
        print("Nada a inserir.")
        conn.close()
        return 0

    inserted = 0
    for e in new_entries:
        cur.execute("""
            INSERT INTO importer.queue_items
                (source_id, title, author, source_url, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, 'waiting_triage', NOW(), NOW())
        """, (source_id, e["title"], e["author"], e["url"]))
        inserted += 1

    conn.commit()
    print(f"OK: {inserted} itens inseridos como waiting_triage.")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
