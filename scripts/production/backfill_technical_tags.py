#!/usr/bin/env python3
"""Backfill controlado de tags para ebooks técnicos em produção.

Por padrão roda em dry-run e grava relatório em var/reports/. Use --apply para
aplicar apenas sugestões de alta confiança em livros ainda sem tags.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sharebook_prod_auth import (  # noqa: E402
    API_BASE,
    ApiHttpError,
    auth_headers,
    get_token,
    load_env,
    request_json,
)


TECH_ROOT_NAME = "Tecnologia"
DEFAULT_LIMIT = 50
MAX_TAGS_PER_BOOK = 3
REPORT_DIR = Path("/data/workspace/sharebook-agent/var/reports")


@dataclass(frozen=True)
class Rule:
    tag: str
    patterns: tuple[str, ...]
    reason: str


RULES: tuple[Rule, ...] = (
    Rule("kubernetes", (r"\bkubernetes\b", r"\bk8s\b"), "menciona Kubernetes/K8s"),
    Rule("docker", (r"\bdocker\b", r"\bcontainers?\b", r"\bconteineres?\b"), "menciona Docker/containers"),
    Rule("devops", (r"\bdevops\b", r"\bci cd\b", r"\bpipeline\b", r"\bdeployment\b"), "menciona operação, deploy ou CI/CD"),
    Rule("aws", (r"\baws\b", r"\bamazon web services\b", r"\bamazon s3\b"), "menciona AWS"),
    Rule("cloud", (r"\bcloud\b", r"\bcomputacao em nuvem\b", r"\bcloud computing\b"), "menciona cloud"),
    Rule("linux", (r"\blinux\b", r"\bunix\b", r"\bshell\b", r"\bcommand line\b"), "menciona Linux/Unix/shell"),
    Rule("git", (r"\bgit\b", r"\bgithub\b"), "menciona Git/GitHub"),
    Rule("networking", (r"\bnetworking\b", r"\btcp ip\b", r"\bipv6\b", r"\bredes de computadores\b"), "menciona redes/protocolos"),
    Rule("observabilidade", (r"\bobservability\b", r"\bobservabilidade\b", r"\bmonitoring\b", r"\blogging\b", r"\bmetrics\b", r"\bdistributed tracing\b"), "menciona observabilidade"),
    Rule("seguranca", (r"\bsecurity\b", r"\bseguranca\b", r"\bhacking\b", r"\bhardening\b", r"\bappsec\b"), "menciona segurança aplicada"),
    Rule("criptografia", (r"\bcryptography\b", r"\bcriptografia\b", r"\bcrypto\b"), "menciona criptografia"),
    Rule("python", (r"\bpython\b",), "menciona Python"),
    Rule("r", (r"\blanguage r\b", r"\blinguagem r\b", r"\busing r\b", r"\busando o r\b", r"\bcom r\b"), "menciona R como linguagem/ferramenta"),
    Rule("java", (r"\bjava\b",), "menciona Java"),
    Rule("javascript", (r"\bjavascript\b", r"\bnode js\b", r"\bnodejs\b"), "menciona JavaScript/Node.js"),
    Rule("typescript", (r"\btypescript\b", r"\btype script\b"), "menciona TypeScript"),
    Rule("csharp", (r"\bcsharp\b", r"\bc sharp\b"), "menciona C#"),
    Rule("dotnet", (r"\bdotnet\b", r"\basp net\b"), "menciona .NET/ASP.NET"),
    Rule("c-plus-plus", (r"\bcplusplus\b", r"\bcpp\b", r"\bc plus plus\b"), "menciona C++"),
    Rule("go", (r"\bgolang\b", r"\bgo programming\b", r"\blanguage go\b"), "menciona Go"),
    Rule("php", (r"\bphp\b",), "menciona PHP"),
    Rule("scala", (r"\bscala\b",), "menciona Scala"),
    Rule("spring-boot", (r"\bspring boot\b", r"\bspring framework\b"), "menciona Spring Boot/Spring"),
    Rule("sql", (r"\bsql\b",), "menciona SQL"),
    Rule("bancos-de-dados", (r"\bdatabase\b", r"\bdatabases\b", r"\bbanco de dados\b", r"\bbancos de dados\b"), "menciona bancos de dados"),
    Rule("data-science", (r"\bdata science\b", r"\bciencia de dados\b"), "menciona Data Science"),
    Rule("machine-learning", (r"\bmachine learning\b", r"\baprendizado de maquina\b", r"\bstatistical learning\b"), "menciona Machine Learning"),
    Rule("deep-learning", (r"\bdeep learning\b", r"\bneural networks\b", r"\bredes neurais\b"), "menciona Deep Learning/redes neurais"),
    Rule("computer-vision", (r"\bcomputer vision\b", r"\bvisao computacional\b", r"\bimage processing\b"), "menciona visão computacional"),
    Rule("estatistica", (r"\bstatistics\b", r"\bestatistica\b", r"\bprobability\b", r"\bprobabilidade\b"), "menciona estatística/probabilidade"),
    Rule("information-retrieval", (r"\binformation retrieval\b", r"\bsearch engines\b", r"\brecuperacao de informacao\b"), "menciona busca/recuperação de informação"),
    Rule("algoritmos", (r"\balgorithms\b", r"\balgoritmos\b"), "menciona algoritmos"),
    Rule("estruturas-de-dados", (r"\bdata structures\b", r"\bestruturas de dados\b"), "menciona estruturas de dados"),
    Rule("sistemas-operacionais", (r"\boperating systems\b", r"\bsistemas operacionais\b", r"\bkernel\b"), "menciona sistemas operacionais/kernel"),
    Rule("arquitetura-de-computadores", (r"\bcomputer architecture\b", r"\barquitetura de computadores\b", r"\borganizacao de computadores\b"), "menciona arquitetura de computadores"),
    Rule("computacao-de-alto-desempenho", (r"\bhpc\b", r"\bhigh performance computing\b", r"\bcomputacao de alto desempenho\b"), "menciona HPC"),
    Rule("metodos-numericos", (r"\bnumerical methods\b", r"\bmetodos numericos\b", r"\banalise numerica\b"), "menciona métodos numéricos"),
    Rule("compiladores", (r"\bcompilers\b", r"\bcompiladores\b", r"\bcompiler design\b"), "menciona compiladores"),
    Rule("matematica-discreta", (r"\bdiscrete mathematics\b", r"\bmatematica discreta\b"), "menciona matemática discreta"),
    Rule("teoria-da-computacao", (r"\btheory of computation\b", r"\bteoria da computacao\b", r"\bautomata\b", r"\bautomatos\b"), "menciona teoria da computação"),
    Rule("microsservicos", (r"\bmicroservices\b", r"\bmicrosservicos\b"), "menciona microsserviços"),
    Rule("arquitetura", (r"\bsoftware architecture\b", r"\barquitetura de software\b", r"\barquitetura\b"), "menciona arquitetura de software"),
    Rule("apis", (r"\bapi\b", r"\bapis\b", r"\brest\b", r"\bgraphql\b"), "menciona APIs/REST/GraphQL"),
    Rule("backend", (r"\bbackend\b", r"\bback end\b", r"\bserver side\b"), "menciona backend/server-side"),
    Rule("clean-code", (r"\bclean code\b", r"\bcodigo limpo\b", r"\bcode quality\b"), "menciona Clean Code/qualidade de código"),
    Rule("design-patterns", (r"\bdesign patterns\b", r"\bpadroes de projeto\b"), "menciona Design Patterns"),
    Rule("event-driven", (r"\bevent driven\b", r"\bevent sourcing\b", r"\bstream processing\b", r"\bpub sub\b"), "menciona arquitetura orientada a eventos"),
    Rule("sistemas-distribuidos", (r"\bdistributed systems\b", r"\bsistemas distribuidos\b"), "menciona sistemas distribuídos"),
    Rule("testes", (r"\btesting\b", r"\bunit testing\b", r"\btestes automatizados\b", r"\btdd\b"), "menciona testes"),
    Rule("frontend", (r"\bfrontend\b", r"\bfront end\b", r"\bclient side\b"), "menciona frontend/client-side"),
    Rule("html-css", (r"\bhtml\b", r"\bcss\b"), "menciona HTML/CSS"),
    Rule("web-design", (r"\bweb design\b", r"\bdesign web\b"), "menciona Web Design"),
    Rule("computacao-grafica", (r"\bcomputer graphics\b", r"\bcomputacao grafica\b", r"\bopengl\b", r"\bray tracing\b", r"\brendering\b"), "menciona computação gráfica"),
    Rule("desenvolvimento-de-jogos", (r"\bgame development\b", r"\bgame dev\b", r"\bdesenvolvimento de jogos\b", r"\bpygame\b", r"\bgames\b"), "menciona desenvolvimento de jogos"),
)


def normalize_text(value: str | None) -> str:
    text = value or ""
    text = re.sub(r"(?i)c\+\+", "cplusplus", text)
    text = re.sub(r"(?i)c#", "csharp", text)
    text = re.sub(r"(?i)\.net", "dotnet", text)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def flatten_categories(categories: list[dict[str, Any]], path: str = "") -> list[dict[str, str]]:
    flattened: list[dict[str, str]] = []
    for category in categories:
        current_path = f"{path} > {category['name']}" if path else category["name"]
        flattened.append({"id": category["id"], "name": category["name"], "path": current_path})
        flattened.extend(flatten_categories(category.get("children") or [], current_path))
    return flattened


def collect_tech_category_ids(categories: list[dict[str, Any]]) -> set[str]:
    flattened = flatten_categories(categories)
    tech_root = next(item for item in flattened if item["path"] == TECH_ROOT_NAME)
    tech_prefix = f"{tech_root['path']} > "
    return {
        item["id"]
        for item in flattened
        if item["path"] == tech_root["path"] or item["path"].startswith(tech_prefix)
    }


def score_rule(rule: Rule, title_text: str, synopsis_text: str) -> int:
    score = 0
    for pattern in rule.patterns:
        if re.search(pattern, title_text):
            score += 3
            break
    for pattern in rule.patterns:
        if re.search(pattern, synopsis_text):
            score += 1
            break
    return score


def suggest_tags(book: dict[str, Any]) -> list[dict[str, Any]]:
    title_text = normalize_text(book.get("title"))
    synopsis_text = normalize_text(book.get("synopsis"))
    matches: list[dict[str, Any]] = []

    for rule in RULES:
        score = score_rule(rule, title_text, synopsis_text)
        if score >= 2:
            matches.append({"tag": rule.tag, "score": score, "reason": rule.reason})

    matches.sort(key=lambda item: (-item["score"], item["tag"]))
    return matches[:MAX_TAGS_PER_BOOK]


def fetch_context(token: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], set[str]]:
    headers = auth_headers(token)
    categories_response = request_json(f"{API_BASE}/Category", headers=headers)
    categories = categories_response["items"]
    tech_category_ids = collect_tech_category_ids(categories)

    books_response = request_json(f"{API_BASE}/Book/1/9999", headers=headers)
    books = books_response.get("items") or []

    tags = request_json(f"{API_BASE}/Tag", headers=headers) or []
    valid_tag_ids = {tag["id"] for tag in tags}

    return books, categories, tech_category_ids & {category["id"] for category in flatten_categories(categories)}, valid_tag_ids


def get_existing_book_tags(token: str, book_id: str) -> list[str]:
    tags = request_json(f"{API_BASE}/Tag/Book/{book_id}", headers=auth_headers(token)) or []
    return [tag.get("id") for tag in tags if tag.get("id")]


def build_plan(token: str, *, include_tagged: bool, limit: int) -> dict[str, Any]:
    books, _categories, tech_category_ids, valid_tag_ids = fetch_context(token)
    candidates = [
        book
        for book in books
        if book.get("type") == "Eletronic"
        and book.get("status") == "Available"
        and book.get("categoryId") in tech_category_ids
    ]

    suggestions: list[dict[str, Any]] = []
    skipped_with_tags = 0
    skipped_without_suggestion = 0

    for book in candidates:
        existing_tags = [tag.get("id") for tag in (book.get("tags") or []) if tag.get("id")]
        if not existing_tags:
            existing_tags = get_existing_book_tags(token, book["id"])
        if existing_tags and not include_tagged:
            skipped_with_tags += 1
            continue

        matches = [match for match in suggest_tags(book) if match["tag"] in valid_tag_ids]
        if not matches:
            skipped_without_suggestion += 1
            continue

        suggestions.append({
            "bookId": book["id"],
            "slug": book.get("slug"),
            "title": book.get("title"),
            "author": book.get("author"),
            "categoryId": book.get("categoryId"),
            "existingTags": existing_tags,
            "suggestedTags": [match["tag"] for match in matches],
            "evidence": matches,
        })

    suggestions.sort(key=lambda item: (
        -sum(match["score"] for match in item["evidence"]),
        item["title"] or "",
    ))

    selected = suggestions[:limit]
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "mode": "dry-run",
        "limit": limit,
        "totalBooksFetched": len(books),
        "technicalCandidates": len(candidates),
        "skippedAlreadyTagged": skipped_with_tags,
        "skippedWithoutSuggestion": skipped_without_suggestion,
        "suggestionsTotal": len(suggestions),
        "selectedTotal": len(selected),
        "selected": selected,
        "notSelected": suggestions[limit:],
    }


def apply_plan(token: str, plan: dict[str, Any]) -> list[dict[str, Any]]:
    headers = auth_headers(token)
    results: list[dict[str, Any]] = []
    for item in plan["selected"]:
        response = request_json(
            f"{API_BASE}/Tag/Book/{item['bookId']}",
            method="PUT",
            body={"TagIds": item["suggestedTags"]},
            headers=headers,
        )
        results.append({
            "bookId": item["bookId"],
            "title": item["title"],
            "applied": [tag.get("id") for tag in (response or [])],
        })
    return results


def write_report(plan: dict[str, Any], report_path: Path | None) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    final_path = report_path or REPORT_DIR / f"technical-tags-backfill-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
    final_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return final_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Backfill controlado de tags técnicas.")
    parser.add_argument("--apply", action="store_true", help="Aplica o lote selecionado.")
    parser.add_argument("--include-tagged", action="store_true", help="Inclui livros que já possuem tags.")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help=f"Limite de livros selecionados (padrão: {DEFAULT_LIMIT}).")
    parser.add_argument("--report", type=Path, help="Caminho do relatório JSON.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    env_values = load_env(repo_root)
    token = get_token(env_values, repo_root=repo_root)

    try:
        plan = build_plan(token, include_tagged=args.include_tagged, limit=args.limit)
        if args.apply:
            plan["mode"] = "apply"
            plan["applied"] = apply_plan(token, plan)
    except ApiHttpError as exc:
        if exc.code not in {401, 403}:
            raise
        token = get_token(env_values, repo_root=repo_root, force_refresh=True)
        plan = build_plan(token, include_tagged=args.include_tagged, limit=args.limit)
        if args.apply:
            plan["mode"] = "apply"
            plan["applied"] = apply_plan(token, plan)

    report_path = write_report(plan, args.report)
    summary = {
        "mode": plan["mode"],
        "report": str(report_path),
        "technicalCandidates": plan["technicalCandidates"],
        "skippedAlreadyTagged": plan["skippedAlreadyTagged"],
        "skippedWithoutSuggestion": plan["skippedWithoutSuggestion"],
        "suggestionsTotal": plan["suggestionsTotal"],
        "selectedTotal": plan["selectedTotal"],
        "appliedTotal": len(plan.get("applied") or []),
        "selectedPreview": [
            {
                "title": item["title"],
                "tags": item["suggestedTags"],
                "evidence": item["evidence"],
            }
            for item in plan["selected"][:10]
        ],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
