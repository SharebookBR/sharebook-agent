#!/usr/bin/env python
from __future__ import annotations

import argparse
import base64
import json
import re
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import quote

from sharebook_prod_auth import (
    API_BASE,
    ApiHttpError,
    auth_headers,
    get_token,
    load_env,
    request_json,
)


def read_utf8_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8-sig")


def infer_image_url(book: dict[str, Any] | None) -> dict[str, Any] | None:
    if not book:
        return book
    if book.get("imageUrl") or not book.get("imageSlug"):
        return book

    enriched = dict(book)
    public_api_base = API_BASE.removesuffix("/api")
    enriched["imageUrl"] = f"{public_api_base}/Images/Books/{book['imageSlug']}"
    return enriched


def get_categories(token: str) -> list[dict[str, Any]]:
    payload = request_json(f"{API_BASE}/Category", headers=auth_headers(token))
    return payload["items"]


def normalize_category_alias(category_name: str) -> str:
    normalized = category_name.strip().lower()
    aliases = {
        "poesia": "artes",
        "poema": "artes",
        "poemas": "artes",
        "romance": "amor",
        "amor": "amor",
        "informática": "tecnologia",
        "informatica": "tecnologia",
        "tecnologia": "tecnologia",
    }
    return aliases.get(normalized, normalized)


def resolve_category_id(token: str, category_name: str | None, category_id: str | None) -> str:
    if category_id:
        return category_id
    if not category_name:
        raise SystemExit("Informe --category-id ou --category-name.")
    categories = get_categories(token)
    normalized = normalize_category_alias(category_name)
    for item in categories:
        if item["name"].strip().lower() == normalized:
            return item["id"]
    available = ", ".join(sorted(item["name"] for item in categories))
    raise SystemExit(f"Categoria nao encontrada: {category_name}. Disponiveis: {available}")


def get_books(token: str) -> list[dict[str, Any]]:
    payload = request_json(f"{API_BASE}/Book/1/9999", headers=auth_headers(token))
    return payload["items"]


def get_book_by_id(token: str, book_id: str) -> dict[str, Any] | None:
    match = next((item for item in get_books(token) if item.get("id") == book_id), None)
    return infer_image_url(match)


def normalize_match_text(value: str | None) -> str:
    return " ".join((value or "").strip().casefold().split())


def normalize_loose_title(value: str | None) -> str:
    text = normalize_match_text(value)
    text = re.sub(r"\([^)]*\)", " ", text)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def full_search_books(criteria: str, page: int = 1, items: int = 100) -> list[dict[str, Any]]:
    encoded_criteria = quote(criteria, safe="")
    payload = request_json(f"{API_BASE}/Book/FullSearch/{encoded_criteria}/{page}/{items}")
    return payload.get("items") or []


def _is_title_variant(title_a: str | None, title_b: str | None) -> bool:
    loose_a = normalize_loose_title(title_a)
    loose_b = normalize_loose_title(title_b)
    if not loose_a or not loose_b:
        return False
    if loose_a == loose_b:
        return True
    if len(loose_a) >= 8 and len(loose_b) >= 8 and (loose_a in loose_b or loose_b in loose_a):
        return True
    return False


def find_exact_book(
    token: str, title: str, author: str, book_type: str | None = None
) -> dict[str, Any] | None:
    del token  # token mantido na assinatura por compatibilidade com chamadas existentes.
    normalized_title = normalize_match_text(title)
    normalized_author = normalize_match_text(author)

    candidates = full_search_books(title, page=1, items=100)
    if not candidates:
        candidates = full_search_books(author, page=1, items=100)

    exact_matches = [
        item
        for item in candidates
        if normalize_match_text(item.get("title")) == normalized_title
        and normalize_match_text(item.get("author")) == normalized_author
        and (book_type is None or item.get("type") == book_type)
    ]
    if exact_matches:
        exact_matches.sort(key=lambda item: item["creationDate"], reverse=True)
        return infer_image_url(exact_matches[0])

    similar_matches = [
        item
        for item in candidates
        if normalize_match_text(item.get("author")) == normalized_author
        and (book_type is None or item.get("type") == book_type)
        and _is_title_variant(item.get("title"), title)
    ]
    if not similar_matches:
        return None

    similar_matches.sort(key=lambda item: item["creationDate"], reverse=True)
    match = infer_image_url(similar_matches[0])
    if match is None:
        return None
    enriched = dict(match)
    enriched["matchKind"] = "similar"
    return enriched


def delete_book(token: str, book_id: str) -> Any:
    return request_json(f"{API_BASE}/Book/{book_id}", method="DELETE", headers=auth_headers(token))


def approve_book(token: str, book_id: str) -> Any:
    return request_json(
        f"{API_BASE}/Book/Approve/{book_id}",
        method="POST",
        body={"ChooseDate": None},
        headers=auth_headers(token),
    )


def _read_synopsis_arg(args: argparse.Namespace, current_synopsis: str) -> str:
    synopsis = getattr(args, "synopsis", None)
    if getattr(args, "synopsis_file", None):
        synopsis = read_utf8_text(args.synopsis_file).strip()
    return current_synopsis if synopsis is None else synopsis


def _read_optional_bytes(path: str | None) -> bytes:
    if not path:
        return b""
    return Path(path).read_bytes()


def create_book(args: argparse.Namespace, token: str) -> dict[str, Any]:
    title = args.title
    author = args.author
    synopsis = _read_synopsis_arg(args, "")

    existing = find_exact_book(token, title, author, book_type=args.type)
    if existing and args.delete_existing:
        delete_book(token, existing["id"])
        existing = None

    if existing:
        match_kind = existing.get("matchKind")
        reason = "titulo/autor e tipo" if match_kind != "similar" else "titulo similar + mesmo autor e tipo"
        raise SystemExit(
            f"Livro ja existe com {reason}. "
            f"Use --delete-existing para recriar. ID: {existing['id']}"
        )

    category_id = resolve_category_id(token, args.category_name, args.category_id)
    book_type = args.type
    payload = {
        "Title": title,
        "Author": author,
        "CategoryId": category_id,
        "ImageName": Path(args.image_path).name,
        "ImageBytes": base64.b64encode(Path(args.image_path).read_bytes()).decode("ascii"),
        "Synopsis": synopsis,
        "Type": book_type,
    }

    if book_type == "Eletronic":
        if not args.pdf_path:
            raise SystemExit("Informe --pdf-path para livros digitais.")
        payload["PdfBytes"] = base64.b64encode(Path(args.pdf_path).read_bytes()).decode("ascii")
    else:
        if not args.freight_option:
            raise SystemExit("Informe --freight-option para livros físicos.")
        payload["FreightOption"] = args.freight_option

    create_response = request_json(
        f"{API_BASE}/Book",
        method="POST",
        body=payload,
        headers=auth_headers(token),
    )

    created = find_exact_book(token, title, author, book_type=book_type)
    if not created:
        raise SystemExit("Livro nao encontrado apos o cadastro.")

    result: dict[str, Any] = {"create_response": create_response, "book": infer_image_url(created)}
    if args.approve:
        result["approve_response"] = approve_book(token, created["id"])
        result["book"] = find_exact_book(token, title, author, book_type=book_type)
    return result


def update_book(args: argparse.Namespace, token: str) -> dict[str, Any]:
    current = get_book_by_id(token, args.id)
    if not current:
        raise SystemExit(f"Livro nao encontrado para update. ID: {args.id}")

    title = args.title or current["title"]
    author = args.author or current["author"]
    book_type = args.type or current["type"]
    category_id = (
        resolve_category_id(token, args.category_name, args.category_id)
        if (args.category_name or args.category_id)
        else current["categoryId"]
    )
    synopsis = _read_synopsis_arg(args, current.get("synopsis") or "")
    image_bytes = _read_optional_bytes(getattr(args, "image_path", None))
    pdf_bytes = _read_optional_bytes(getattr(args, "pdf_path", None))
    user_id = current.get("userId") or "00000000-0000-0000-0000-000000000000"
    facilitator_id = current.get("userIdFacilitator") or "00000000-0000-0000-0000-000000000000"

    payload: dict[str, Any] = {
        "Id": args.id,
        "Title": title,
        "Author": author,
        "CategoryId": category_id,
        "UserId": user_id,
        "UserIdFacilitator": facilitator_id,
        "Approved": current.get("status") == "Available",
        "ImageName": Path(args.image_path).name if getattr(args, "image_path", None) else "",
        "ImageBytes": base64.b64encode(image_bytes).decode("ascii") if image_bytes else [],
        "Synopsis": synopsis,
        "ChooseDate": current.get("chooseDate"),
        "FreightOption": args.freight_option if args.freight_option is not None else current.get("freightOption"),
        "Type": book_type,
        "PdfBytes": base64.b64encode(pdf_bytes).decode("ascii") if pdf_bytes else [],
    }

    update_response = request_json(
        f"{API_BASE}/Book/{args.id}",
        method="PUT",
        body=payload,
        headers=auth_headers(token),
    )

    updated = get_book_by_id(token, args.id)
    if not updated:
        raise SystemExit(f"Livro nao encontrado apos update. ID: {args.id}")

    result: dict[str, Any] = {"update_response": update_response, "book": updated}
    if args.approve:
        result["approve_response"] = approve_book(token, args.id)
        result["book"] = get_book_by_id(token, args.id)
    return result


def find_many_books(token: str, pairs: list[dict[str, str]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for pair in pairs:
        title = (pair.get("title") or "").strip()
        author = (pair.get("author") or "").strip()
        match = find_exact_book(token, title, author)
        results.append({"title": title, "author": author, "book": infer_image_url(match)})
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Opera livros do Sharebook em producao.")
    sub = parser.add_subparsers(dest="command", required=True)

    find_parser = sub.add_parser("find", help="Buscar livro por titulo e autor.")
    find_parser.add_argument("--title", required=True)
    find_parser.add_argument("--author", required=True)
    find_parser.add_argument("--type", choices=["Printed", "Eletronic"])

    find_many_parser = sub.add_parser("find-many", help="Buscar varios livros com um unico login.")
    find_many_parser.add_argument(
        "--pairs-file",
        required=True,
        help="Arquivo JSON UTF-8 com uma lista de objetos {\"title\":...,\"author\":...}.",
    )

    sub.add_parser("categories", help="Listar categorias disponiveis.")

    delete_parser = sub.add_parser("delete", help="Deletar livro por id.")
    delete_parser.add_argument("--id", required=True)

    approve_parser = sub.add_parser("approve", help="Aprovar livro por id.")
    approve_parser.add_argument("--id", required=True)

    create_parser = sub.add_parser("create", help="Cadastrar livro fisico ou digital.")
    create_parser.add_argument("--title", required=True)
    create_parser.add_argument("--author", required=True)
    create_parser.add_argument("--category-name")
    create_parser.add_argument("--category-id")
    create_parser.add_argument("--type", choices=["Printed", "Eletronic"], default="Eletronic")
    synopsis_group = create_parser.add_mutually_exclusive_group(required=True)
    synopsis_group.add_argument("--synopsis")
    synopsis_group.add_argument("--synopsis-file")
    create_parser.add_argument("--image-path", required=True)
    create_parser.add_argument("--pdf-path")
    create_parser.add_argument(
        "--freight-option",
        choices=["City", "State", "Country", "World", "WithoutFreight"],
        help="Obrigatorio para livro fisico.",
    )
    create_parser.add_argument("--approve", action="store_true")
    create_parser.add_argument("--delete-existing", action="store_true")

    update_parser = sub.add_parser("update", help="Atualizar livro existente por id.")
    update_parser.add_argument("--id", required=True)
    update_parser.add_argument("--title")
    update_parser.add_argument("--author")
    update_parser.add_argument("--category-name")
    update_parser.add_argument("--category-id")
    update_parser.add_argument("--type", choices=["Printed", "Eletronic"])
    update_synopsis_group = update_parser.add_mutually_exclusive_group()
    update_synopsis_group.add_argument("--synopsis")
    update_synopsis_group.add_argument("--synopsis-file")
    update_parser.add_argument("--image-path")
    update_parser.add_argument("--pdf-path")
    update_parser.add_argument(
        "--freight-option",
        choices=["City", "State", "Country", "World", "WithoutFreight"],
        help="Opcional para atualizar livro fisico.",
    )
    update_parser.add_argument("--approve", action="store_true")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    env_values = load_env(repo_root)

    def execute_with_token(token: str) -> Any:
        if args.command == "find":
            return find_exact_book(token, args.title, args.author, book_type=args.type)
        if args.command == "find-many":
            pairs = json.loads(read_utf8_text(args.pairs_file))
            if not isinstance(pairs, list):
                raise SystemExit("--pairs-file deve conter uma lista JSON.")
            return find_many_books(token, pairs)
        if args.command == "categories":
            return get_categories(token)
        if args.command == "delete":
            return delete_book(token, args.id)
        if args.command == "approve":
            return approve_book(token, args.id)
        if args.command == "create":
            return create_book(args, token)
        if args.command == "update":
            return update_book(args, token)
        raise SystemExit(f"Comando desconhecido: {args.command}")

    token = get_token(env_values, repo_root=repo_root)
    try:
        result = execute_with_token(token)
    except ApiHttpError as exc:
        if exc.code not in {401, 403}:
            raise SystemExit(str(exc)) from exc

        token = get_token(env_values, repo_root=repo_root, force_refresh=True)
        result = execute_with_token(token)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
