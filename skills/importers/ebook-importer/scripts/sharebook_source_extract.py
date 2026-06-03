#!/usr/bin/env python
from __future__ import annotations

import argparse
import html
import json
import re
import ssl
import sys
import urllib.request
from pathlib import Path
from typing import Any


USER_AGENT = "CodexSharebookMvp/1.0"
SSL_CONTEXT = ssl._create_unverified_context()


def configure_stdout_utf8() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30, context=SSL_CONTEXT) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_json(url: str) -> Any:
    return json.loads(fetch_text(url))


def strip_html(value: str) -> str:
    no_tags = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(no_tags)).strip()


def extract_post_json_url(page_html: str) -> str:
    match = re.search(r"https://livrosdominiopublico\.com\.br/wp-json/wp/v2/posts/\d+", page_html)
    if not match:
        raise SystemExit("Nao foi possivel localizar o endpoint wp-json do post.")
    return match.group(0)


def extract_author(page_html: str, title: str) -> str | None:
    patterns = [
        rf"{re.escape(title)}\s+De\s+([^<>&]+)",
        r'"author":\{"@type":"Person","name":"([^"]+)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, page_html, re.IGNORECASE)
        if match:
            return html.unescape(match.group(1)).strip()
    return None


def collect_pdf_url(page_html: str) -> str | None:
    match = re.search(r"https://files\.livrosdominiopublico\.com\.br/[^\s\"']+\.pdf", page_html, re.IGNORECASE)
    return match.group(0) if match else None


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60, context=SSL_CONTEXT) as response:
        destination.write_bytes(response.read())


def build_manifest(source_url: str, page_html: str, post: dict[str, Any]) -> dict[str, Any]:
    title = strip_html(post["title"]["rendered"])
    excerpt = strip_html(post["excerpt"]["rendered"])
    content = strip_html(post["content"]["rendered"])
    author = extract_author(page_html, title)
    pdf_url = collect_pdf_url(page_html)
    return {
        "source_url": source_url,
        "title": title,
        "author": author,
        "excerpt": excerpt,
        "content": content,
        "pdf_url": pdf_url,
    }


def main() -> int:
    configure_stdout_utf8()
    parser = argparse.ArgumentParser(description="Extrai metadados de uma pagina do Livros Dominio Publico.")
    parser.add_argument("url", help="URL da pagina do livro.")
    parser.add_argument("--out-dir", help="Diretorio para salvar manifest, PDF e capa de origem.")
    args = parser.parse_args()

    page_html = fetch_text(args.url)
    post_json_url = extract_post_json_url(page_html)
    post = fetch_json(post_json_url)
    manifest = build_manifest(args.url, page_html, post)

    if args.out_dir:
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        manifest["manifest_path"] = str((out_dir / "manifest.json").resolve())

        if manifest["pdf_url"]:
            pdf_path = out_dir / "source.pdf"
            download(manifest["pdf_url"], pdf_path)
            manifest["downloaded_pdf_path"] = str(pdf_path.resolve())

        (out_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    json.dump(manifest, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
