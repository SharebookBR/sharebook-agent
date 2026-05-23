"""Crawla a listagem do BaixeLivros Quadrinhos e insere itens como
waiting_triage na tabela importer.queue_items.

Uso:
    python crawl_baixelivros_quadrinhos.py [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import ssl
import sys
import urllib.request
from html import unescape
from urllib.parse import urljoin

import psycopg2

SOURCE_NAME = "baixelivros_quadrinhos"
SOURCE_URL  = "https://www.baixelivros.com.br/biblioteca/quadrinhos"
BASE_URL    = "https://www.baixelivros.com.br"
BOOK_PREFIX = f"{BASE_URL}/quadrinhos/"
PAGE_TPL    = f"{SOURCE_URL}/page/{{n}}"
UA          = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

ssl_ctx = ssl._create_unverified_context()


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30, context=ssl_ctx) as r:
        return r.read().decode("utf-8", errors="replace")


def extract_book_urls(html: str) -> list[str]:
    links = re.findall(r'href="(https://www\.baixelivros\.com\.br/quadrinhos/[^"]+)"', html)
    # Filtrar links que claramente não são livros
    return sorted({
        l for l in links
        if not l.endswith("/feed")
        and "/page/" not in l
        and "?" not in l
    })


def extract_title(html: str) -> str:
    m = re.search(r'<meta property="og:title" content="([^"]+)"', html)
    if m:
        title = unescape(m.group(1)).strip()
        # Remove sufixo " PDF Grátis | ..."
        title = re.sub(r"\s+PDF\s+Grátis\s*\|.*$", "", title, flags=re.IGNORECASE)
        return title.strip()
    return ""


def crawl_all_pages() -> list[str]:
    all_urls: list[str] = []
    page = 1
    while True:
        url = SOURCE_URL if page == 1 else PAGE_TPL.format(n=page)
        print(f"  Crawlando página {page}: {url}")
        try:
            html = fetch(url)
        except Exception as e:
            print(f"  Parou na página {page}: {e}")
            break
        found = extract_book_urls(html)
        if not found:
            print(f"  Nenhum livro na página {page} — fim da paginação.")
            break
        new = [u for u in found if u not in all_urls]
        all_urls.extend(new)
        print(f"  Encontrados: {len(found)} links ({len(new)} novos)")
        page += 1
    return all_urls


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Não insere no banco, só imprime")
    args = parser.parse_args()

    print(f"=== Crawlando {SOURCE_URL} ===")
    book_urls = crawl_all_pages()
    print(f"\nTotal de livros encontrados: {len(book_urls)}")

    if args.dry_run:
        print("\n[DRY RUN] URLs que seriam inseridas:")
        for u in book_urls:
            print(" ", u)
        return 0

    # Conectar ao banco
    conn = psycopg2.connect(
        host="212.85.23.202", port=5432, dbname="sharebook_importer",
        user="sharebook_ai_rw", password="F%Ljy9oxTA3iR#npW%4W9iaSaJKU", sslmode="disable"
    )
    conn.autocommit = False
    cur = conn.cursor()

    # Garantir que a source existe e pegar o ID
    cur.execute("SELECT id FROM importer.sources WHERE name = %s", (SOURCE_NAME,))
    row = cur.fetchone()
    if not row:
        raise SystemExit(f"Source '{SOURCE_NAME}' não encontrada no banco. Rode a migration primeiro.")
    source_id = row[0]
    print(f"\nSource ID: {source_id}")

    # Buscar URLs já existentes para não duplicar
    cur.execute("SELECT source_url FROM importer.queue_items WHERE source_id = %s", (source_id,))
    existing = {r[0] for r in cur.fetchall()}
    print(f"Itens já existentes na fila: {len(existing)}")

    new_urls = [u for u in book_urls if u not in existing]
    print(f"Itens novos a inserir: {len(new_urls)}")

    if not new_urls:
        print("Nada a inserir.")
        conn.close()
        return 0

    # Inserir como waiting_triage (título provisório — triage_worker extrai o real)
    inserted = 0
    for url in new_urls:
        # Título provisório a partir do slug
        slug = url.rstrip("/").rsplit("/", 1)[-1]
        title = slug.replace("-", " ").title()
        cur.execute("""
            INSERT INTO importer.queue_items
                (source_id, title, source_url, status, created_at, updated_at)
            VALUES (%s, %s, %s, 'waiting_triage', NOW(), NOW())
        """, (source_id, title, url))
        inserted += 1

    conn.commit()
    print(f"\n✓ {inserted} itens inseridos como waiting_triage.")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
