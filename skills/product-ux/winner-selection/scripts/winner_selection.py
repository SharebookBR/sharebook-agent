#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[4]
PRODUCTION_SCRIPTS = REPO_ROOT / "scripts" / "production"
sys.path.insert(0, str(PRODUCTION_SCRIPTS))

from sharebook_prod_auth import (  # noqa: E402
    API_BASE,
    SSL_CONTEXT,
    ApiHttpError,
    auth_headers,
    get_token,
    load_env,
    request_json,
)


BOOK_READY_FOR_SELECTION = "AwaitingDonorDecision"
REQUEST_ACTIVE = "WaitingAction"
BOOK_AFTER_SELECTION = "WaitingSend"
REQUEST_WINNER = "Donated"
SAFE_NICKNAME_RE = re.compile(r"(?i)^Interessado\s+\d+$")

EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
URL_RE = re.compile(r"(?i)\b(?:https?://|www\.)\S+")
CEP_RE = re.compile(r"(?i)\bcep\s*[:\-]?\s*\d{5}[\s.-]?\d{3}\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?\d{4,5}[\s.-]?\d{4}(?!\d)")
ADDRESS_LINE_RE = re.compile(
    r"(?im)^.*\b(?:rua|avenida|av\.|travessa|alameda|rodovia)\b.*$"
)
INTRO_NAME_RE = re.compile(
    r"(?i)\b(?:meu nome é|me chamo|me chamou)\s+.{1,80}?"
    r"(?=\s*(?:,|\.|!|\n|\be\s+\d+\s+anos\b|\be\s+sou\b|\bsou\b|"
    r"\btenho\b|\bestou\b|\bgostaria\b|\bquero\b|\bgosto\b|\bentrei\b))"
)
SOU_NAME_RE = re.compile(
    r"(?i)\bSou\s+[A-ZÀ-Ý][\wÀ-ÿ'’-]*(?:\s+[A-ZÀ-Ý][\wÀ-ÿ'’-]*){0,4}"
    r"(?=\s*(?:,\s*(?:tenho|fui|estou|moro|gosto|amo)\b|tenho\b))"
)
CALLED_NAME_RE = re.compile(
    r"(?i:\b(?:chamad[oa]s?|se chama)\s+)"
    r"[A-ZÀ-Ý][\wÀ-ÿ'’-]*(?:\s+[A-ZÀ-Ý][\wÀ-ÿ'’-]*){0,4}"
    r"(?=\s*(?:[,.;!?\n]|$))"
)
ODD_ME_NAME_RE = re.compile(
    r"\bme\s+[A-ZÀ-Ý][\wÀ-ÿ'’-]*(?:\s+[A-ZÀ-Ý][\wÀ-ÿ'’-]*){0,4}(?=\s*[,\.])"
)
NAMED_LOCATION_RE = re.compile(
    r"(?i)\b(?:moro|resido|residente)\s+(?:em|no|na)\s+"
    r"(?!interior\b|zona\s+rural\b)[^,.()\n]{1,80}"
    r"(?:,\s*(?:no|na)\s+[^.()\n]{1,40})?"
)
INSTITUTION_ACRONYM_RE = re.compile(
    r"(?i:\b(?:universidade|faculdade|colégio|escola|instituição)\s+(?:d[aeo]\s+)?)"
    r"[A-Z]{2,}\b"
)
FAMILY_NAME_RE = re.compile(r"\b[A-ZÀ-Ý][\wÀ-ÿ'’-]+\s+(?=de\s+\d{1,3}\b)")
SIGNATURE_RE = re.compile(
    r"(?im)(^\s*(?:Com carinho(?: e gratidão)?|Atenciosamente)[,]?\s*\n)\s*[^\n]+$"
)


def opaque_code(book_id: str, user_id: str) -> str:
    digest = hashlib.sha256(f"{book_id}:{user_id}".encode("utf-8")).hexdigest()
    return f"P-{digest[:8].upper()}"


def safe_requester_nickname(value: Any, selection_code: str) -> str:
    nickname = str(value or "").strip()
    if SAFE_NICKNAME_RE.fullmatch(nickname):
        return nickname
    return f"Solicitação {selection_code}"


def sanitize_request_text(text: str) -> str:
    sanitized = text or ""
    sanitized = EMAIL_RE.sub("[e-mail removido]", sanitized)
    sanitized = URL_RE.sub("[link removido]", sanitized)
    sanitized = CEP_RE.sub("[CEP removido]", sanitized)
    sanitized = PHONE_RE.sub("[telefone removido]", sanitized)
    sanitized = ADDRESS_LINE_RE.sub("[endereço removido]", sanitized)
    sanitized = INTRO_NAME_RE.sub("meu nome é [identidade removida]", sanitized)
    sanitized = SOU_NAME_RE.sub("Sou [identidade removida]", sanitized)
    sanitized = CALLED_NAME_RE.sub("chamado [familiar removido]", sanitized)
    sanitized = ODD_ME_NAME_RE.sub("me [identidade removida]", sanitized)
    sanitized = NAMED_LOCATION_RE.sub("moro em [localidade removida]", sanitized)
    sanitized = INSTITUTION_ACRONYM_RE.sub("[instituição removida]", sanitized)
    sanitized = FAMILY_NAME_RE.sub("[familiar removido] ", sanitized)
    sanitized = SIGNATURE_RE.sub(r"\1[assinatura removida]", sanitized)
    sanitized = re.sub(r"[ \t]+\n", "\n", sanitized)
    sanitized = re.sub(r"\n{3,}", "\n\n", sanitized)
    return sanitized.strip()


def authenticated_json(
    url: str,
    env_values: dict[str, str],
    *,
    force_refresh: bool = False,
) -> Any:
    token = get_token(env_values, repo_root=REPO_ROOT, force_refresh=force_refresh)
    try:
        return request_json(url, headers=auth_headers(token))
    except ApiHttpError as exc:
        if exc.code != 401 or force_refresh:
            raise
        return authenticated_json(url, env_values, force_refresh=True)


def resolve_book(slug: str) -> dict[str, Any]:
    encoded_slug = urllib.parse.quote(slug, safe="")
    book = request_json(f"{API_BASE}/book/Slug/{encoded_slug}")
    if not isinstance(book, dict) or not book.get("id"):
        raise SystemExit("Livro não encontrado ou resposta inválida.")
    return book


def get_requests(book_id: str, env_values: dict[str, str]) -> list[dict[str, Any]]:
    response = authenticated_json(
        f"{API_BASE}/book/RequestersList/{book_id}", env_values
    )
    if not isinstance(response, list):
        raise SystemExit("RequestersList não retornou uma lista.")
    return response


def prepare(slug: str, include_closed: bool) -> int:
    env_values = load_env(REPO_ROOT)
    book = resolve_book(slug)
    requests = get_requests(book["id"], env_values)

    candidates: list[dict[str, Any]] = []
    for request in requests:
        text = str(request.get("requestText") or "")
        status = str(request.get("status") or "")
        if status == "Canceled" or text.strip().lower().startswith("pedido cancelado"):
            continue
        if not include_closed and status != REQUEST_ACTIVE:
            continue

        selection_code = opaque_code(book["id"], str(request["userId"]))
        candidates.append(
            {
                "nickname": safe_requester_nickname(
                    request.get("requesterNickName"), selection_code
                ),
                "selectionCode": selection_code,
                "requestText": sanitize_request_text(text),
                "hasDonated": int(request.get("totalBooksDonated") or 0) > 0,
                "booksReceived": int(request.get("totalBooksWon") or 0),
            }
        )

    output = {
        "book": {
            "id": book["id"],
            "title": book.get("title"),
            "author": book.get("author"),
            "slug": book.get("slug"),
            "status": book.get("status"),
        },
        "candidateCount": len(candidates),
        "candidates": candidates,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


def mutation_once(url: str, token: str, body: dict[str, Any]) -> Any:
    encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json", **auth_headers(token)}
    request = urllib.request.Request(url, data=encoded, headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(request, timeout=120, context=SSL_CONTEXT) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ApiHttpError(exc.code, url, detail) from exc


def selection_state(
    slug: str,
    code: str,
    env_values: dict[str, str],
) -> dict[str, Any]:
    book = resolve_book(slug)
    requests = get_requests(book["id"], env_values)
    candidate = next(
        (
            request
            for request in requests
            if opaque_code(book["id"], str(request["userId"])) == code
        ),
        None,
    )
    return {
        "book": book,
        "requests": requests,
        "candidate": candidate,
    }


def validated_result(state: dict[str, Any], code: str, api_response: Any) -> dict[str, Any]:
    candidate = state["candidate"]
    requests = state["requests"]
    return {
        "code": code,
        "apiSuccess": api_response.get("success") if isinstance(api_response, dict) else None,
        "successMessage": (
            api_response.get("successMessage") if isinstance(api_response, dict) else None
        ),
        "bookStatus": state["book"].get("status"),
        "winnerRequestStatus": candidate.get("status") if candidate else None,
        "remainingWaitingAction": sum(
            1 for request in requests if request.get("status") == REQUEST_ACTIVE
        ),
    }


def is_complete(result: dict[str, Any]) -> bool:
    return (
        result["bookStatus"] == BOOK_AFTER_SELECTION
        and result["winnerRequestStatus"] == REQUEST_WINNER
        and result["remainingWaitingAction"] == 0
    )


def choose(slug: str, code: str, note: str, confirm: bool) -> int:
    if not confirm:
        raise SystemExit("Escolha não executada: use --confirm após autorização explícita.")

    env_values = load_env(REPO_ROOT)
    before = selection_state(slug, code, env_values)
    book = before["book"]
    candidate = before["candidate"]

    if candidate is None:
        raise SystemExit("Código anônimo não pertence às solicitações deste livro.")

    already_complete = validated_result(before, code, None)
    if is_complete(already_complete):
        already_complete["observedIdempotentState"] = True
        print(json.dumps(already_complete, ensure_ascii=False, indent=2))
        return 0

    if book.get("status") != BOOK_READY_FOR_SELECTION:
        raise SystemExit(f"Status inesperado do livro: {book.get('status')}")
    if candidate.get("status") != REQUEST_ACTIVE:
        raise SystemExit(f"Solicitação não está ativa: {candidate.get('status')}")

    token = get_token(env_values, repo_root=REPO_ROOT)
    url = f"{API_BASE}/book/Donate/{book['id']}"
    body = {"userId": candidate["userId"], "note": note}
    api_response: Any = None

    try:
        api_response = mutation_once(url, token, body)
    except ApiHttpError as exc:
        if exc.code != 401:
            raise
        token = get_token(env_values, repo_root=REPO_ROOT, force_refresh=True)
        api_response = mutation_once(url, token, body)
    except (urllib.error.URLError, TimeoutError, socket.timeout):
        # A mutação pode ter concluído. Não repetir sem observar o estado real.
        pass

    after = selection_state(slug, code, env_values)
    result = validated_result(after, code, api_response)
    if not is_complete(result):
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit("Escolha não pôde ser confirmada; nenhuma repetição automática foi feita.")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def self_test() -> int:
    samples = [
        (
            "Meu nome é Maria Silva, tenho 20 anos. Moro em Campinas. "
            "E-mail maria@example.com. CEP 13000-000. Rua das Flores, 10.",
            ["Maria Silva", "Campinas", "maria@example.com", "13000-000", "Rua das Flores"],
        ),
        (
            "Meu nome é Joana e 18 anos e sou leitora.\n\nCom carinho,\nJoana Souza",
            ["Joana", "Joana Souza"],
        ),
        (
            "Agradeço pela oportunidade.\nAtenciosamente,\nPaulo da Silva\nRua das Flores, 10.",
            ["Paulo da Silva", "Rua das Flores"],
        ),
        (
            "Olá, me Carlos. Meus filhos são Alice de 10 e Bento de 8 anos.",
            ["Carlos", "Alice", "Bento"],
        ),
        (
            "Residente no Rio Grande do Sul e moro em Porto Alegre.",
            ["Rio Grande do Sul", "Porto Alegre"],
        ),
        (
            "Tenho um filhinho ainda criança chamado George, e quero ensiná-lo a ler.",
            ["George"],
        ),
        (
            "Sou Igor tenho um filho e gosto de ler para ele.",
            ["Igor"],
        ),
        (
            "Entrei pelo Enem na universidade de UFRN.",
            ["UFRN"],
        ),
    ]
    for sample, forbidden in samples:
        sanitized = sanitize_request_text(sample)
        if any(value in sanitized for value in forbidden):
            raise SystemExit(f"Falha no sanitizador: {sanitized}")
    if opaque_code("book", "user") != opaque_code("book", "user"):
        raise SystemExit("Código opaco não é determinístico.")
    if opaque_code("book", "user") == opaque_code("book", "other"):
        raise SystemExit("Código opaco colidiu no autoteste.")
    if safe_requester_nickname("Interessado 12", "P-TESTE") != "Interessado 12":
        raise SystemExit("Apelido anônimo válido foi alterado.")
    if safe_requester_nickname("Nome Real", "P-TESTE") != "Solicitação P-TESTE":
        raise SystemExit("Fallback de apelido inseguro falhou.")
    print("Autoteste concluído com sucesso.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepara solicitações anônimas e registra ganhador pela API do Sharebook."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--slug", required=True)
    prepare_parser.add_argument("--include-closed", action="store_true")

    choose_parser = subparsers.add_parser("choose")
    choose_parser.add_argument("--slug", required=True)
    choose_parser.add_argument("--code", required=True)
    choose_parser.add_argument("--note", default="")
    choose_parser.add_argument("--confirm", action="store_true")

    subparsers.add_parser("self-test")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "prepare":
        return prepare(args.slug, args.include_closed)
    if args.command == "choose":
        return choose(args.slug, args.code, args.note, args.confirm)
    return self_test()


if __name__ == "__main__":
    raise SystemExit(main())
