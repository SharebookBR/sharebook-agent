# -*- coding: utf-8 -*-
"""Popula metadata_json.subject nos queue_items de ebook_foundation_subjects.

Funciona retroativamente (itens já inseridos) e serve de referência para
entender como o crawler passa o subject nos itens futuros.
"""
from __future__ import annotations

import json
import re
import urllib.request

import psycopg2

SOURCE_NAME = "ebook_foundation_subjects"
RAW_MD_URL  = "https://raw.githubusercontent.com/EbookFoundation/free-programming-books/main/books/free-programming-books-subjects.md"
USER_AGENT  = "Mozilla/5.0"

ITEM_RE    = re.compile(r"^\* \[(?P<title>.+?)\]\((?P<url>https?://[^)]+)\)(?: - (?P<rest>.*))?$")
HEADING_RE = re.compile(r"^(#{3,4})\s+(?P<name>.+?)\s*$")


def fetch_markdown(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def is_pdf_entry(url: str, rest: str) -> bool:
    if url.lower().endswith(".pdf"):
        return True
    if rest and "(pdf)" in rest.lower():
        return True
    return False


def build_url_to_subject(text: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    current_path: list[str] = []
    in_index = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line == "### Index":
            in_index = True
            continue
        if in_index:
            if HEADING_RE.match(line):
                in_index = False
            else:
                continue

        heading_match = HEADING_RE.match(line)
        if heading_match:
            level = len(heading_match.group(1))
            name = heading_match.group("name").strip()
            depth = level - 3
            current_path = current_path[:depth]
            current_path.append(name)
            continue

        item_match = ITEM_RE.match(line)
        if not item_match:
            continue
        url = item_match.group("url").strip()
        rest = (item_match.group("rest") or "").strip()
        if not is_pdf_entry(url, rest):
            continue
        mapping[url] = current_path[0] if current_path else "Unknown"

    return mapping


def main() -> None:
    print("Buscando markdown...")
    text = fetch_markdown(RAW_MD_URL)
    url_to_subject = build_url_to_subject(text)
    print(f"URLs mapeadas: {len(url_to_subject)}")

    conn = psycopg2.connect(
        host="212.85.23.202", port=5432, dbname="sharebook_importer",
        user="sharebook_ai_rw", password="F%Ljy9oxTA3iR#npW%4W9iaSaJKU", sslmode="disable"
    )
    cur = conn.cursor()

    cur.execute("SELECT id FROM importer.sources WHERE name = %s", (SOURCE_NAME,))
    source_id = cur.fetchone()[0]

    cur.execute("SELECT id, source_url, metadata_json FROM importer.queue_items WHERE source_id = %s", (source_id,))
    rows = cur.fetchall()
    print(f"Itens no banco: {len(rows)}")

    updated = 0
    not_found = 0
    for item_id, source_url, metadata_raw in rows:
        subject = url_to_subject.get(source_url)
        if not subject:
            not_found += 1
            continue
        metadata = json.loads(metadata_raw) if metadata_raw else {}
        metadata["subject"] = subject
        cur.execute(
            "UPDATE importer.queue_items SET metadata_json = %s, updated_at = NOW() WHERE id = %s",
            (json.dumps(metadata, ensure_ascii=False), item_id)
        )
        updated += 1

    conn.commit()
    conn.close()
    print(f"Atualizados: {updated} | Sem match: {not_found}")


if __name__ == "__main__":
    main()
