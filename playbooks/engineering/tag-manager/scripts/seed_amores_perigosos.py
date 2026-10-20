#!/usr/bin/env python3
"""Cria a tag editorial Amores Perigosos e revisa seu catálogo inicial.

Idempotente: preserva tags aprovadas existentes, acrescenta a tag quando há
espaço e recusa silenciosamente destruir uma terceira tag já curada.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


_AGENT_ROOT = next((p for p in Path(__file__).resolve().parents if (p / "AGENTS.md").exists()), None)
if _AGENT_ROOT:
    sys.path.insert(0, str(_AGENT_ROOT / "playbooks" / "_shared" / "scripts"))
    sys.path.insert(0, str(_AGENT_ROOT / "playbooks" / "_shared" / "scripts" / "production"))

from sharebook_prod_auth import (  # noqa: E402
    API_BASE,
    ApiHttpError,
    auth_headers,
    get_token,
    load_env,
    request_json,
)


TAG = {
    "Id": "amores-perigosos",
    "Name": "Amores Perigosos",
    "Aliases": ["amor-perigoso", "paixoes-perigosas", "romances-perigosos"],
    "Family": "literatura-temas",
    "Description": "Histórias em que amar envolve obsessão, pactos, ciúme, poder, transgressão ou consequências fatais.",
    "UsageNotes": "Use quando o romance é central e existe risco sobrenatural, psicológico, social, criminoso ou mortal. Conflito romântico comum não basta.",
    "Status": "Active",
    "IsPublic": True,
}

BOOK_TITLES = (
    "Zanoni",
    "Pacto de Sangue & Seda",
    "Promessa de Dez Verões",
    "Legado de Sangue",
    "Senhora",
    "O Primo Basílio",
    "Dom Casmurro",
    "Amor de Perdição",
    "A Dama das Camélias",
    "Bom Crioulo",
    "Inocência",
    "Romeu e Julieta",
    "Lucíola",
    "A Condessa Vésper",
    "Iracema",
    "Bruxa por Acaso & o Galã de Milhões",
)


def normalize(value: str | None) -> str:
    return " ".join((value or "").strip().casefold().split())


def run(token: str) -> dict[str, Any]:
    headers = auth_headers(token)
    existing_tags = request_json(f"{API_BASE}/Tag/Admin", headers=headers) or []
    existing_ids = {tag.get("id") for tag in existing_tags}

    created = False
    if TAG["Id"] not in existing_ids:
        request_json(f"{API_BASE}/Tag", method="POST", body=TAG, headers=headers)
        created = True

    books_page = request_json(f"{API_BASE}/Book/1/9999", headers=headers) or {}
    books_by_title: dict[str, list[dict[str, Any]]] = {}
    for book in books_page.get("items") or []:
        books_by_title.setdefault(normalize(book.get("title")), []).append(book)

    applied: list[dict[str, Any]] = []
    already_tagged: list[str] = []
    missing: list[str] = []
    blocked_at_limit: list[dict[str, Any]] = []

    for title in BOOK_TITLES:
        candidates = books_by_title.get(normalize(title)) or []
        if not candidates:
            missing.append(title)
            continue

        # A vitrine precisa de um núcleo digital estável. Títulos clássicos
        # frequentemente também existem como doações físicas já encerradas;
        # nunca deixar a ordem incidental da API escolher esse exemplar.
        book = max(
            candidates,
            key=lambda candidate: (
                candidate.get("type") == "Eletronic",
                candidate.get("status") == "Available",
                bool(candidate.get("eBookPdfPath")),
            ),
        )

        current = request_json(f"{API_BASE}/Tag/Book/{book['id']}", headers=headers) or []
        current_ids = [tag.get("id") for tag in current if tag.get("id")]
        if TAG["Id"] in current_ids:
            already_tagged.append(title)
            continue
        if len(current_ids) >= 3:
            blocked_at_limit.append({"title": title, "tags": current_ids})
            continue

        desired = [*current_ids, TAG["Id"]]
        response = request_json(
            f"{API_BASE}/Tag/Book/{book['id']}",
            method="PUT",
            body={"TagIds": desired},
            headers=headers,
        ) or []
        applied.append({
            "title": title,
            "bookId": book["id"],
            "tags": [tag.get("id") for tag in response],
        })

    return {
        "tag": TAG["Id"],
        "created": created,
        "applied": applied,
        "alreadyTagged": already_tagged,
        "missing": missing,
        "blockedAtThreeTags": blocked_at_limit,
    }


def main() -> int:
    repo_root = _AGENT_ROOT or Path.cwd()
    env_values = load_env(repo_root)
    token = get_token(env_values, repo_root=repo_root)
    try:
        result = run(token)
    except ApiHttpError as exc:
        if exc.code not in {401, 403}:
            raise
        token = get_token(env_values, repo_root=repo_root, force_refresh=True)
        result = run(token)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
