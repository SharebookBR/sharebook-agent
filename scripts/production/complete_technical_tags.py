#!/usr/bin/env python3
"""Completa cobertura de tags em ebooks técnicos sem sobrescrever curadoria.

Esta fase é deliberadamente editorial: cria lacunas reais do vocabulário técnico
e tagueia apenas livros de Tecnologia que ainda não têm tag pública aprovada.
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

from backfill_technical_tags import (  # noqa: E402
    API_BASE,
    REPORT_DIR,
    auth_headers,
    fetch_context,
    flatten_categories,
    get_existing_book_tags,
    get_token,
    load_env,
    request_json,
)

MAX_TAGS_PER_BOOK = 3


@dataclass(frozen=True)
class TagSeed:
    id: str
    name: str
    family: str
    aliases: tuple[str, ...] = ()
    description: str = ""
    usage_notes: str = ""


@dataclass(frozen=True)
class CompletionRule:
    tag: str
    patterns: tuple[str, ...]
    reason: str


NEW_TAGS: tuple[TagSeed, ...] = (
    TagSeed("inteligencia-artificial", "Inteligência Artificial", "dados-ia", ("ai", "ia", "artificial-intelligence"), "Livros sobre fundamentos, aplicações e impactos de IA."),
    TagSeed("ia-generativa", "IA Generativa", "dados-ia", ("generative-ai", "chatgpt", "dall-e"), "Livros sobre modelos generativos, prompts e aplicações modernas de IA."),
    TagSeed("prompt-engineering", "Prompt Engineering", "dados-ia", ("engenharia-de-prompt", "prompts"), "Livros sobre criação e refinamento de prompts para modelos generativos."),
    TagSeed("processamento-de-linguagem-natural", "Processamento de Linguagem Natural", "dados-ia", ("nlp", "natural-language-processing"), "Livros sobre linguagem natural, fala, texto e aplicações linguísticas."),
    TagSeed("aprendizado-por-reforco", "Aprendizado por Reforço", "dados-ia", ("reinforcement-learning",), "Livros sobre agentes, políticas, recompensas e aprendizado por reforço."),
    TagSeed("mlops", "MLOps", "dados-ia", ("machine-learning-operations",), "Livros sobre operação, deploy e governança de modelos de machine learning."),
    TagSeed("programacao-funcional", "Programação Funcional", "backend-arquitetura", ("functional-programming",), "Livros sobre linguagens, técnicas e modelos funcionais."),
    TagSeed("programacao-orientada-a-objetos", "Programação Orientada a Objetos", "backend-arquitetura", ("oop", "object-oriented-programming"), "Livros sobre objetos, classes, encapsulamento e design orientado a objetos."),
    TagSeed("metodos-formais", "Métodos Formais", "fundamentos-computacao", ("formal-methods", "z-notation"), "Livros sobre especificação, prova, semântica formal e verificação."),
    TagSeed("concorrencia", "Concorrência", "fundamentos-computacao", ("concurrency", "parallelism"), "Livros sobre concorrência, paralelismo, semáforos e processos."),
    TagSeed("processamento-de-imagens", "Processamento de Imagens", "frontend-graficos-jogos", ("jpeg",), "Livros sobre imagens digitais, compressão, visão e formatos."),
    TagSeed("realidade-virtual", "Realidade Virtual", "frontend-graficos-jogos", ("virtual-reality", "vr"), "Livros sobre ambientes virtuais, interação e mundos 3D."),
    TagSeed("editores-de-texto", "Editores de Texto", "infra-cloud-operacao-seguranca", ("vim", "emacs", "text-editors"), "Livros sobre editores usados por devs, como Vim e Emacs."),
    TagSeed("escrita-tecnica", "Escrita Técnica", "uso-editorial", ("technical-writing",), "Livros sobre documentação, escrita e comunicação técnica."),
    TagSeed("software-livre", "Software Livre", "uso-editorial", ("open-source", "free-software", "creative-commons"), "Livros sobre software livre, domínio público, licenças e comunidades abertas."),
    TagSeed("gestao-de-tecnologia", "Gestão de Tecnologia", "uso-editorial", ("it-management", "tech-management"), "Livros sobre gestão, carreira, produto e decisões em tecnologia."),
    TagSeed("internet-das-coisas", "Internet das Coisas", "infra-cloud-operacao-seguranca", ("iot",), "Livros sobre IoT, dispositivos conectados e aplicações embarcadas."),
    TagSeed("sistemas-embarcados", "Sistemas Embarcados", "fundamentos-computacao", ("embedded-systems", "arduino"), "Livros sobre hardware, firmware, microcontroladores e sistemas embarcados."),
    TagSeed("blockchain", "Blockchain", "infra-cloud-operacao-seguranca", ("distributed-ledger",), "Livros sobre blockchain, smart contracts e aplicações descentralizadas."),
    TagSeed("criptomoedas", "Criptomoedas", "infra-cloud-operacao-seguranca", ("bitcoin", "cryptocurrency"), "Livros sobre Bitcoin, moedas digitais e protocolos criptoeconômicos."),
    TagSeed("computacao-quantica", "Computação Quântica", "fundamentos-computacao", ("quantum-computing", "quantum-information"), "Livros sobre computação quântica, informação quântica e algoritmos quânticos."),
    TagSeed("versionamento-de-codigo", "Controle de Versão", "infra-cloud-operacao-seguranca", ("subversion", "svn"), "Livros sobre ferramentas e práticas de controle de versão."),
    TagSeed("teoria-das-categorias", "Teoria das Categorias", "fundamentos-computacao", ("category-theory",), "Livros sobre teoria das categorias aplicada à programação."),
    TagSeed("pensamento-computacional", "Pensamento Computacional", "fundamentos-computacao", ("computational-thinking",), "Livros introdutórios sobre raciocínio computacional."),
    TagSeed("fundamentos-da-computacao", "Fundamentos da Computação", "fundamentos-computacao", ("computer-science", "ciencia-da-computacao"), "Livros gerais de ciência da computação e programação de base."),
    TagSeed("logica", "Lógica", "fundamentos-computacao", ("logic", "logica-computacional"), "Livros sobre lógica aplicada à computação."),
    TagSeed("circuitos-digitais", "Circuitos Digitais", "fundamentos-computacao", ("digital-circuits",), "Livros sobre circuitos digitais, eletrônica básica e organização de hardware."),
    TagSeed("otimizacao", "Otimização", "dados-ia", ("optimization", "otimizacao-combinatoria"), "Livros sobre otimização, busca e métodos computacionais de decisão."),
    TagSeed("processamento-de-sinais", "Processamento de Sinais", "dados-ia", ("signal-processing", "dsp"), "Livros sobre sinais digitais e computação de sinais."),
    TagSeed("sistemas-complexos", "Sistemas Complexos", "dados-ia", ("complex-systems",), "Livros sobre modelagem e análise de sistemas complexos."),
    TagSeed("modelagem", "Modelagem", "fundamentos-computacao", ("modeling", "modelagem-computacional"), "Livros sobre modelagem de sistemas, dados e fenômenos computacionais."),
    TagSeed("carreira-dev", "Carreira Dev", "uso-editorial", ("software-engineer-career", "carreira-em-tecnologia"), "Livros sobre carreira, posicionamento e evolução profissional em software."),
    TagSeed("bash", "Bash", "linguagens-plataformas-frameworks", ("gnu-bash", "shell-script"), "Livros sobre Bash, shell e linha de comando."),
    TagSeed("lisp", "Lisp", "linguagens-plataformas-frameworks", ("common-lisp", "cl"), "Livros sobre Lisp e Common Lisp."),
    TagSeed("latex", "LaTeX", "linguagens-plataformas-frameworks", ("tex", "latex2e"), "Livros sobre LaTeX, Beamer e produção técnica em TeX."),
    TagSeed("pascal", "Pascal", "linguagens-plataformas-frameworks", (), "Livros sobre Pascal."),
    TagSeed("julia", "Julia", "linguagens-plataformas-frameworks", (), "Livros sobre Julia."),
    TagSeed("fortran", "Fortran", "linguagens-plataformas-frameworks", ("fortran90",), "Livros sobre Fortran."),
    TagSeed("assembly", "Assembly", "linguagens-plataformas-frameworks", ("asm", "intel-8086"), "Livros sobre Assembly e arquitetura de baixo nível."),
    TagSeed("small-basic", "Small Basic", "linguagens-plataformas-frameworks", ("basic",), "Livros introdutórios com Small Basic."),
    TagSeed("tkinter", "Tkinter", "linguagens-plataformas-frameworks", (), "Livros sobre interfaces gráficas com Tkinter."),
    TagSeed("yii", "Yii", "linguagens-plataformas-frameworks", ("yii2",), "Livros sobre o framework PHP Yii."),
)

RULES: tuple[CompletionRule, ...] = (
    CompletionRule("editores-de-texto", (r"\bemacs\b", r"\bvim\b", r"\btext editing\b", r"\beditor de texto\b"), "editor de texto explícito"),
    CompletionRule("programacao-funcional", (r"\bfunctional languages?\b", r"\bfunctional programming\b", r"\bprogramacao funcional\b", r"\bcategory theory\b"), "programação funcional"),
    CompletionRule("metodos-formais", (r"\bz specification\b", r"\bformal methods?\b", r"\bsemantics\b", r"\brefinement\b", r"\bproof\b"), "métodos formais/especificação"),
    CompletionRule("concorrencia", (r"\bcommunicating sequential processes\b", r"\bcsp\b", r"\bsemaphores?\b", r"\bconcorrencia\b", r"\bconcurrency\b"), "concorrência/processos"),
    CompletionRule("processamento-de-imagens", (r"\bjpeg\b", r"\bimage processing\b", r"\bprocessamento de imagens\b"), "processamento de imagens"),
    CompletionRule("desenvolvimento-de-jogos", (r"\bgame programming\b", r"\bgame development\b", r"\bpygame\b"), "jogos"),
    CompletionRule("design-patterns", (r"\bdesign patterns?\b", r"\bpadroes de projeto\b"), "padrões de projeto"),
    CompletionRule("realidade-virtual", (r"\bvirtual reality\b", r"\bvirtual worlds?\b", r"\brealidade virtual\b"), "realidade virtual"),
    CompletionRule("computacao-grafica", (r"\b3d graphics\b", r"\bcomputer graphics\b", r"\bopengl\b", r"\brendering\b"), "computação gráfica"),
    CompletionRule("software-livre", (r"\bpublic domain\b", r"\bcreative commons\b", r"\bopen source\b", r"\bfree software\b", r"\brichard stallman\b"), "software livre/licenciamento"),
    CompletionRule("lisp", (r"\bcommon lisp\b", r"\blisp\b"), "Lisp"),
    CompletionRule("inteligencia-artificial", (r"\bartificial intelligence\b", r"\binteligencia artificial\b", r"\bfoundations of computational agents\b"), "IA"),
    CompletionRule("ia-generativa", (r"\bgenerative ai\b", r"\bchatgpt\b", r"\bdall e\b"), "IA generativa"),
    CompletionRule("prompt-engineering", (r"\bprompt engineering\b", r"\bprompt book\b", r"\bprompts?\b"), "prompt engineering"),
    CompletionRule("processamento-de-linguagem-natural", (r"\bnatural language processing\b", r"\bspeech and language\b", r"\bnlp\b", r"\bprocessamento de linguagem natural\b"), "NLP"),
    CompletionRule("aprendizado-por-reforco", (r"\breinforcement learning\b", r"\baprendizado por reforco\b"), "aprendizado por reforço"),
    CompletionRule("mlops", (r"\bmlops\b", r"\bmachine learning operations\b"), "MLOps"),
    CompletionRule("deep-learning", (r"\bneural network\b", r"\bdeep learning\b", r"\bredes neurais\b"), "deep learning"),
    CompletionRule("data-science", (r"\bdata mining\b", r"\bmassive datasets\b", r"\bdata analysis\b", r"\bciencia de dados\b"), "dados"),
    CompletionRule("estatistica", (r"\bbayesian\b", r"\bprobabilistic\b", r"\bprobability\b", r"\bstatistics\b"), "estatística/probabilidade"),
    CompletionRule("bancos-de-dados", (r"\bdatabase\b", r"\bdatabases\b", r"\bbanco de dados\b"), "bancos de dados"),
    CompletionRule("teoria-da-computacao", (r"\btheoretical computer science\b", r"\btheory of computation\b", r"\bformal languages?\b"), "teoria da computação"),
    CompletionRule("fundamentos-da-computacao", (r"\bintroduction to computer science\b", r"\bfoundations of computer science\b", r"\bcomputer science\b", r"\bfoundations of programming\b"), "fundamentos de computação"),
    CompletionRule("compiladores", (r"\bgcc\b", r"\bcompiler\b", r"\bcompilers\b", r"\boberon\b"), "compiladores"),
    CompletionRule("sistemas-operacionais", (r"\boperating system\b", r"\boperating systems\b", r"\bfile system\b", r"\bkernel\b", r"\banykernel\b", r"\brump kernels?\b"), "sistemas operacionais"),
    CompletionRule("arquitetura-de-computadores", (r"\bcomputer organization\b", r"\bcomputer architecture\b", r"\bbottom up\b"), "arquitetura de computadores"),
    CompletionRule("computacao-quantica", (r"\bquantum computing\b", r"\bquantum information\b", r"\bquantum shannon\b"), "computação quântica"),
    CompletionRule("clean-code", (r"\bcode simplicity\b", r"\bcode quality\b", r"\bsimplicity\b"), "qualidade/simplicidade de código"),
    CompletionRule("gestao-de-tecnologia", (r"\bit manager\b", r"\bmanagement\b", r"\bdon t just roll the dice\b", r"\bnetworked economy\b"), "gestão de tecnologia"),
    CompletionRule("carreira-dev", (r"\bstand out as a software engineer\b", r"\bsoftware engineer\b"), "carreira dev"),
    CompletionRule("escrita-tecnica", (r"\btechnical writing\b", r"\bguidebook\b"), "escrita técnica"),
    CompletionRule("processamento-de-sinais", (r"\bsignal computing\b", r"\bdigital signals\b", r"\bdsp\b"), "processamento de sinais"),
    CompletionRule("sistemas-embarcados", (r"\bembedded systems?\b", r"\barduino\b", r"\bdigital circuit\b"), "sistemas embarcados"),
    CompletionRule("internet-das-coisas", (r"\binternet das coisas\b", r"\biot\b"), "IoT"),
    CompletionRule("blockchain", (r"\bblockchain\b",), "blockchain"),
    CompletionRule("criptomoedas", (r"\bbitcoin\b", r"\bcryptocurrency\b", r"\bcryptocurrencies\b"), "criptomoedas"),
    CompletionRule("versionamento-de-codigo", (r"\bsubversion\b", r"\bversion control\b", r"\bsvn\b"), "controle de versão"),
    CompletionRule("teoria-das-categorias", (r"\bcategory theory\b",), "teoria das categorias"),
    CompletionRule("pensamento-computacional", (r"\bcomputational thinking\b",), "pensamento computacional"),
    CompletionRule("logica", (r"\bcomputational logic\b", r"\blogica\b", r"\blogic\b"), "lógica"),
    CompletionRule("circuitos-digitais", (r"\bdigital circuits?\b",), "circuitos digitais"),
    CompletionRule("otimizacao", (r"\boptimization\b", r"\botimizacao\b", r"\bgenetic programming\b"), "otimização"),
    CompletionRule("sistemas-complexos", (r"\bcomplex systems?\b", r"\bcomplexity\b"), "sistemas complexos"),
    CompletionRule("modelagem", (r"\bmodeling\b", r"\bmodelagem\b"), "modelagem"),
    CompletionRule("programacao-orientada-a-objetos", (r"\bobject oriented\b", r"\boop\b", r"\bnaked objects\b"), "orientação a objetos"),
    CompletionRule("bash", (r"\bbash\b", r"\bshell\b"), "Bash/shell"),
    CompletionRule("latex", (r"\blatex\b", r"\blatex2e\b", r"\bbeamer\b"), "LaTeX"),
    CompletionRule("pascal", (r"\bpascal\b",), "Pascal"),
    CompletionRule("julia", (r"\bjulia\b",), "Julia"),
    CompletionRule("fortran", (r"\bfortran\b", r"\bfortran90\b"), "Fortran"),
    CompletionRule("assembly", (r"\bassembly\b", r"\b8086\b"), "Assembly"),
    CompletionRule("small-basic", (r"\bsmall basic\b",), "Small Basic"),
    CompletionRule("tkinter", (r"\btkinter\b",), "Tkinter"),
    CompletionRule("yii", (r"\byii\b", r"\byii2\b"), "Yii"),
    CompletionRule("go", (r"\bgo por exemplo\b", r"\bgolang\b", r"\bgo lang\b", r"\baprenda go\b"), "Go"),
    CompletionRule("c", (r"\blinguagem c\b", r"\bapostila linguagem c\b", r"\bpointers and memory\b"), "C"),
    CompletionRule("r", (r"\br para cientistas sociais\b", r"\busing r\b", r"\busando o r\b"), "R"),
    CompletionRule("networking", (r"\bsockets?\b", r"\bprogramacao em rede\b", r"\bnetworking\b"), "redes"),
    CompletionRule("event-driven", (r"\bkafka\b", r"\bevent streaming\b", r"\bevent driven\b"), "eventos/streaming"),
    CompletionRule("seguranca", (r"\bselinux\b", r"\bsecurity\b", r"\bseguranca\b"), "segurança"),
    CompletionRule("algoritmos", (r"\balgorithmic\b", r"\balgorithms?\b", r"\balgoritmos?\b", r"\bbinary trees?\b", r"\blinked list\b", r"\blist recursion\b"), "algoritmos"),
    CompletionRule("algoritmos", (r"\bcompetitive programming\b", r"\bcompetitive programmer\b"), "programação competitiva"),
    CompletionRule("programacao-funcional", (r"\bstructure and interpretation of computer programs\b", r"\bsicp\b"), "SICP/programação funcional"),
    CompletionRule("estruturas-de-dados", (r"\blinked list\b", r"\bbinary trees?\b", r"\bdata structures?\b"), "estruturas de dados"),
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


def seed_missing_tags(token: str) -> list[str]:
    headers = auth_headers(token)
    existing = {tag["id"] for tag in request_json(f"{API_BASE}/Tag", headers=headers)}
    created: list[str] = []
    for tag in NEW_TAGS:
        if tag.id in existing:
            continue
        request_json(
            f"{API_BASE}/Tag",
            method="POST",
            headers=headers,
            body={
                "id": tag.id,
                "name": tag.name,
                "aliases": list(tag.aliases),
                "family": tag.family,
                "description": tag.description,
                "usageNotes": tag.usage_notes,
                "status": "Active",
                "isPublic": True,
            },
        )
        created.append(tag.id)
    return created


def score_rule(rule: CompletionRule, title: str, synopsis: str) -> int:
    score = 0
    for pattern in rule.patterns:
        if re.search(pattern, title):
            score += 3
            break
    for pattern in rule.patterns:
        if re.search(pattern, synopsis):
            score += 1
            break
    return score


def category_fallback(category_path: str) -> list[str]:
    if category_path.endswith("> IA"):
        return ["inteligencia-artificial"]
    if category_path.endswith("> Dados"):
        return ["data-science"]
    if category_path.endswith("> Frontend"):
        return ["frontend"]
    if category_path.endswith("> Backend"):
        return ["backend"]
    if category_path.endswith("> DevOps"):
        return ["devops"]
    return ["fundamentos-da-computacao"]


def suggest_book_tags(book: dict[str, Any], category_path: str, valid_tags: set[str]) -> tuple[list[str], list[str]]:
    title = normalize_text(book.get("title"))
    synopsis = normalize_text(book.get("synopsis"))
    matches: list[dict[str, Any]] = []
    for index, rule in enumerate(RULES):
        score = score_rule(rule, title, synopsis)
        if score >= 2 and rule.tag in valid_tags:
            matches.append({"tag": rule.tag, "score": score, "index": index, "reason": rule.reason})

    matches.sort(key=lambda item: (-item["score"], item["index"]))
    tags: list[str] = []
    reasons: list[str] = []
    for match in matches:
        if match["tag"] not in tags:
            tags.append(match["tag"])
            reasons.append(match["reason"])
        if len(tags) == MAX_TAGS_PER_BOOK:
            return tags, reasons

    for tag in category_fallback(category_path):
        if tag in valid_tags and tag not in tags:
            tags.append(tag)
            reasons.append(f"fallback editorial por categoria {category_path}")
        if len(tags) == MAX_TAGS_PER_BOOK:
            break

    return tags, reasons


def build_plan(token: str) -> dict[str, Any]:
    books, categories, tech_category_ids, valid_tags = fetch_context(token)
    valid_tags = set(valid_tags) | {tag.id for tag in NEW_TAGS}
    category_by_id = {category["id"]: category for category in flatten_categories(categories)}
    selected: list[dict[str, Any]] = []
    skipped_with_tags = 0
    skipped_without_tags = 0

    for book in books:
        if not (
            book.get("type") == "Eletronic"
            and book.get("status") == "Available"
            and book.get("categoryId") in tech_category_ids
        ):
            continue

        existing = [tag.get("id") for tag in (book.get("tags") or []) if tag.get("id")]
        if not existing:
            existing = get_existing_book_tags(token, book["id"])
        if existing:
            skipped_with_tags += 1
            continue

        category_path = category_by_id.get(book.get("categoryId"), {}).get("path") or ""
        tags, reasons = suggest_book_tags(book, category_path, valid_tags)
        if not tags:
            skipped_without_tags += 1
            continue

        selected.append({
            "bookId": book["id"],
            "slug": book.get("slug"),
            "title": book.get("title"),
            "author": book.get("author"),
            "categoryPath": category_path,
            "suggestedTags": tags,
            "reasons": reasons,
        })

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "selectedTotal": len(selected),
        "skippedAlreadyTagged": skipped_with_tags,
        "skippedWithoutTags": skipped_without_tags,
        "selected": selected,
    }


def write_report(plan: dict[str, Any], suffix: str) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / f"technical-tags-completion-{suffix}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def apply_plan(token: str, plan: dict[str, Any]) -> list[dict[str, Any]]:
    headers = auth_headers(token)
    applied: list[dict[str, Any]] = []
    for item in plan["selected"]:
        response = request_json(
            f"{API_BASE}/Tag/Book/{item['bookId']}",
            method="PUT",
            headers=headers,
            body={"TagIds": item["suggestedTags"]},
        ) or []
        applied.append({
            "bookId": item["bookId"],
            "title": item["title"],
            "applied": [tag.get("id") for tag in response],
        })
    return applied


def main() -> int:
    parser = argparse.ArgumentParser(description="Completa tags dos ebooks técnicos ainda sem tag.")
    parser.add_argument("--apply", action="store_true", help="Aplica as tags em produção.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    token = get_token(load_env(repo_root), repo_root=repo_root)

    created = seed_missing_tags(token) if args.apply else []
    plan = build_plan(token)
    plan["mode"] = "apply" if args.apply else "dry-run"
    plan["createdTags"] = created
    report = write_report(plan, "apply" if args.apply else "dry-run")

    result: dict[str, Any] = {
        "mode": plan["mode"],
        "createdTags": created,
        "selectedTotal": plan["selectedTotal"],
        "skippedAlreadyTagged": plan["skippedAlreadyTagged"],
        "skippedWithoutTags": plan["skippedWithoutTags"],
        "report": str(report),
    }
    if args.apply:
        result["applied"] = apply_plan(token, plan)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
