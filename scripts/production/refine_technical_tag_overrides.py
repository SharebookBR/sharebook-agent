#!/usr/bin/env python3
"""Ajustes editoriais explícitos após completion do backfill técnico."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sharebook_prod_auth import API_BASE, auth_headers, get_token, load_env, request_json  # noqa: E402
from sharebook_prod_book import normalize_match_text  # noqa: E402


EXTRA_TAGS: tuple[dict[str, Any], ...] = (
    {
        "id": "engenharia-de-software",
        "name": "Engenharia de Software",
        "aliases": ["software-engineering"],
        "family": "backend-arquitetura",
        "description": "Livros sobre prática, qualidade, processo e construção profissional de software.",
        "usageNotes": "Use quando o foco é engenharia de software como disciplina, não uma stack específica.",
        "status": "Active",
        "isPublic": True,
    },
)

OVERRIDES: dict[str, list[str]] = {
    "Evidence-based Software Engineering": ["engenharia-de-software"],
    "Programming Languages: Application and Interpretation": ["programacao-funcional", "metodos-formais"],
    "Partial Evaluation and Automatic Program Generation": ["programacao-funcional", "compiladores"],
    "Dive Into Systems": ["sistemas-operacionais", "arquitetura-de-computadores"],
    "Kafka, The definitive Guide": ["event-driven", "sistemas-distribuidos"],
    "Software-Defined Radio for Engineers": ["processamento-de-sinais", "sistemas-embarcados"],
    "The Art of Community": ["software-livre", "gestao-de-tecnologia"],
    "Mathematics for Computer Science": ["matematica-discreta", "fundamentos-da-computacao"],
    "Non-Uniform Random Variate Generation": ["estatistica", "algoritmos"],
    "Computational Mathematics with SageMath": ["metodos-numericos", "fundamentos-da-computacao"],
    "Think Bayes": ["estatistica", "data-science"],
    "Think Stats, 2nd Edition": ["estatistica", "data-science"],
    "Latexação": ["latex"],
    "Academia da Tartaruga": ["logica", "fundamentos-da-computacao"],
    "Structure and Interpretation of Computer Programs": ["programacao-funcional", "fundamentos-da-computacao"],
}


def seed_extra_tags(token: str) -> list[str]:
    headers = auth_headers(token)
    existing = {tag["id"] for tag in request_json(f"{API_BASE}/Tag", headers=headers)}
    created: list[str] = []
    for tag in EXTRA_TAGS:
        if tag["id"] in existing:
            continue
        request_json(f"{API_BASE}/Tag", method="POST", body=tag, headers=headers)
        created.append(tag["id"])
    return created


def find_books(token: str) -> dict[str, dict[str, Any]]:
    books = request_json(f"{API_BASE}/Book/1/9999", headers=auth_headers(token)).get("items") or []
    return {normalize_match_text(book.get("title")): book for book in books}


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    token = get_token(load_env(repo_root), repo_root=repo_root)
    headers = auth_headers(token)
    created = seed_extra_tags(token)
    books_by_title = find_books(token)
    applied: list[dict[str, Any]] = []
    missing: list[str] = []

    for title, tag_ids in OVERRIDES.items():
        book = books_by_title.get(normalize_match_text(title))
        if not book:
            missing.append(title)
            continue
        response = request_json(
            f"{API_BASE}/Tag/Book/{book['id']}",
            method="PUT",
            body={"TagIds": tag_ids},
            headers=headers,
        ) or []
        applied.append({
            "title": title,
            "applied": [tag.get("id") for tag in response],
        })

    print(json.dumps({"createdTags": created, "applied": applied, "missing": missing}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
