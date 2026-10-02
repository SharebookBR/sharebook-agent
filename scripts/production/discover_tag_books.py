#!/usr/bin/env python3
"""Descobre os 5 livros do ciclo manual em produção por título."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sharebook_prod_auth import get_token, load_env  # noqa: E402
from sharebook_prod_book import full_search_books, normalize_match_text  # noqa: E402


BOOKS = [
    "Making Games with Python & Pygame",
    "Kubernetes for Full-Stack Developers",
    "An Introduction to Statistical Learning",
    "Microservices AntiPatterns and Pitfalls",
    "The Art of High Performance Computing",
]


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    env_values = load_env(repo_root)
    token = get_token(env_values, repo_root=repo_root)

    results = {}
    for title in BOOKS:
        items = full_search_books(title, page=1, items=30)
        target = normalize_match_text(title)
        matches = []
        for item in items:
            item_title = normalize_match_text(item.get("title"))
            if target in item_title or item_title in target:
                matches.append(item)
        results[title] = [
            {
                "title": m.get("title"),
                "author": m.get("author"),
                "id": m.get("id"),
                "slug": m.get("slug"),
                "type": m.get("type"),
                "status": m.get("status"),
            }
            for m in matches
        ]

    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
