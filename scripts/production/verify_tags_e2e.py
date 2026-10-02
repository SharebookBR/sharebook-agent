#!/usr/bin/env python3
"""Verifica de ponta a ponta: tag -> livros, e PDP (slug) -> tags."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sharebook_prod_auth import API_BASE, get_token, load_env, request_json  # noqa: E402


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    env_values = load_env(repo_root)
    token = get_token(env_values, repo_root=repo_root)

    print("=== GET /Tag/kubernetes/Books/1/10 ===")
    books = request_json(f"{API_BASE}/Tag/kubernetes/Books/1/10")
    print(json.dumps({
        "totalItems": books.get("totalItems"),
        "titles": [b.get("title") for b in books.get("items") or []],
        "tagsOnFirst": [t.get("id") for t in (books.get("items") or [{}])[0].get("tags") or []],
    }, ensure_ascii=False, indent=2))

    print("\n=== GET /Book/Slug/kubernetes-for-full-stack-developers ===")
    book = request_json(f"{API_BASE}/Book/Slug/kubernetes-for-full-stack-developers")
    print(json.dumps({
        "title": book.get("title"),
        "tags": [t.get("id") for t in book.get("tags") or []],
    }, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
