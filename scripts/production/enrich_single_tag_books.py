#!/usr/bin/env python3
"""Enriquecimento fino: adiciona tags a ebooks técnicos com exatamente 1 tag.

Curadoria editorial manual (cada sinopse completa foi lida). Nunca remove tags;
apenas adiciona até o limite de 3 por livro. Reusa o vocabulário existente e
cria tag nova somente para lacuna recorrente real (ver NEW_TAGS).

Por padrão roda em dry-run e grava relatório em var/reports/. Use --apply para
aplicar em produção.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from backfill_technical_tags import (  # noqa: E402
    collect_tech_category_ids,
    flatten_categories,
    get_existing_book_tags,
)
from sharebook_prod_auth import (  # noqa: E402
    API_BASE,
    ApiHttpError,
    auth_headers,
    get_token,
    load_env,
    request_json,
)

MAX_TAGS_PER_BOOK = 3
REPORT_DIR = Path("/data/workspace/sharebook-agent/var/reports")

# --- Tag nova (lacuna recorrente: ética/segurança/governança/impacto social de IA) ---
NEW_TAGS: tuple[dict[str, Any], ...] = (
    {
        "id": "ia-e-sociedade",
        "name": "IA e Sociedade",
        "aliases": ["ai-ethics", "ai-safety", "ai-and-society", "etica-em-ia", "ai-governance"],
        "family": "dados-ia",
        "description": "Livros sobre ética, segurança, governança, direito e impactos sociais da inteligência artificial.",
        "usageNotes": "Use quando o foco é a dimensão social, ética, regulatória ou de segurança da IA — não o algoritmo em si.",
        "status": "Active",
        "isPublic": True,
    },
)

# --- Curadoria: slug -> tags adicionais + evidência + rationale ---
# Cada sinopse completa foi lida; a evidência cita o trecho que sustenta a tag.
ENRICHMENTS: dict[str, dict[str, Any]] = {
    # Backend
    "algorithms-notes-for-professionals": {
        "add": ["estruturas-de-dados"],
        "evidence": "árvores, grafos, estruturas de dados e travessias no sumário",
        "rationale": "Além de algoritmos, é um survey de estruturas de dados (trees/graphs).",
    },
    "apostila-linguagem-c": {
        "add": ["programacao-orientada-a-objetos"],
        "evidence": "classes, encapsulamento, herança múltipla, polimorfismo",
        "rationale": "Assume C e avança direto para OOP com C++.",
    },
    "c-para-iniciantes": {
        "add": ["programacao-orientada-a-objetos"],
        "evidence": "orientação a objetos com herança e polimorfismo",
        "rationale": "OOP é um dos pilares ensinados de forma explícita.",
    },
    "compiler-design-in-c-1990": {
        "add": ["c"],
        "evidence": "compiler construction in C, C-code como linguagem intermediária",
        "rationale": "A implementação inteira é em C (título + pipeline).",
    },
    "construindo-aplicacoes-web-em-golang": {
        "add": ["backend"],
        "evidence": "aplicação web real: banco, sessões, REST, WebSockets, framework MVC",
        "rationale": "Foco em backend web com Go, não só na linguagem.",
    },
    "designing-event-driven-systems-concepts-and-p": {
        "add": ["sistemas-distribuidos"],
        "evidence": "eventual consistency, escalonamento concorrente, streaming como fonte de verdade",
        "rationale": "Kafka/streaming como arquitetura distribuída (mesma decisão de 'Kafka, The definitive Guide').",
    },
    "java-basico-e-orientacao-a-objeto": {
        "add": ["programacao-orientada-a-objetos"],
        "evidence": "encapsulamento, herança, polimorfismo (título cita orientação a objeto)",
        "rationale": "OOP é o eixo do curso.",
    },
    "linguagem-de-programacao-c-avancado": {
        "add": ["programacao-orientada-a-objetos"],
        "evidence": "herança, polimorfismo, abstração, delegates",
        "rationale": "OOP avançada é a espinha dorsal do material.",
    },
    "making-sense-of-stream-processing": {
        "add": ["sistemas-distribuidos"],
        "evidence": "change data capture, logs append-only, sistemas distribuídos composáveis",
        "rationale": "Stream processing como infraestrutura distribuída (Kleppmann).",
    },
    "open-data-structures-an-introduction": {
        "add": ["algoritmos"],
        "evidence": "análise de tempo de execução, sorting algorithms, grafos",
        "rationale": "Cada estrutura é analisada por corretude e complexidade (análise de algoritmos).",
    },
    "programacao-orientada-a-objetos-uma-abordagem": {
        "add": ["programacao-orientada-a-objetos"],
        "evidence": "classes, objetos, herança, polimorfismo (título)",
        "rationale": "OOP é o assunto central.",
    },
    "purely-functional-data-structures": {
        "add": ["programacao-funcional"],
        "evidence": "purely functional, lazy evaluation, persistência",
        "rationale": "Estruturas de dados em linguagens funcionais puras.",
    },
    "python-para-matematicos": {
        "add": ["metodos-numericos"],
        "evidence": "cálculo de integrais e solução de sistemas lineares com NumPy",
        "rationale": "Aplicação de Python a métodos numéricos (integrais, sistemas lineares).",
    },
    "text-algorithms": {
        "add": ["estruturas-de-dados"],
        "evidence": "suffix trees, suffix arrays, factor automata, índices",
        "rationale": "A espinha dorsal são estruturas de dados para texto.",
    },
    # Cloud
    "cloud-para-devs-fundamentos-sem-enrolacao-v2": {
        "add": ["devops", "observabilidade"],
        "evidence": "CI/CD, observabilidade (logs, métricas, tracing), deploy sem derrubar",
        "rationale": "Cinco perguntas centrais: compute, dados, acesso, deploy e observabilidade.",
    },
    # Dados
    "a-programmers-guide-to-data-mining": {
        "add": ["machine-learning"],
        "evidence": "kNN, Naive Bayes, classificação, clustering",
        "rationale": "Data mining com algoritmos de ML implementados do zero.",
    },
    "analise-exploratoria-de-dados-usando-o-r": {
        "add": ["estatistica"],
        "evidence": "tendência central, dispersão, correlação, análise multivariada",
        "rationale": "É análise exploratória/estatística (R é a ferramenta).",
    },
    "data-mining-concepts-and-techniques": {
        "add": ["machine-learning"],
        "evidence": "classificação, clustering, associação, mineração",
        "rationale": "Data mining = aprendizado de máquina aplicado.",
    },
    "database-design-2nd-edition": {
        "add": ["sql"],
        "evidence": "SQL lab completo com soluções, data manipulation",
        "rationale": "Modelagem + prática SQL em um único volume.",
    },
    "database-fundamentals": {
        "add": ["sql"],
        "evidence": "schema definition, joins, subqueries, stored procedures, JDBC",
        "rationale": "Metade do livro é SQL e acesso via aplicação.",
    },
    "foundations-of-data-science": {
        "add": ["machine-learning"],
        "evidence": "perceptrons, kernel, SVM, online learning, VC-dimension",
        "rationale": "Arco completo de ML como núcleo do livro.",
    },
    "introduction-to-data-science": {
        "add": ["r"],
        "evidence": "introduz R e RStudio; análise com R ao longo do livro",
        "rationale": "R é a ferramenta central de trabalho.",
    },
    "introducao-a-banco-de-dados_copy2": {
        "add": ["sql"],
        "evidence": "SQL com subconsultas, visões, DDL, álgebra relacional",
        "rationale": "SQL é ensinado em profundidade junto à modelagem.",
    },
    "julia-data-science": {
        "add": ["julia"],
        "evidence": "ecossistema Julia, DataFrames, ML com Julia",
        "rationale": "Julia é a linguagem e o diferencial do título.",
    },
    "mining-of-massive-datasets": {
        "add": ["machine-learning"],
        "evidence": "clustering, recomendação, ML methods para dados massivos",
        "rationale": "Métodos de ML em escala são o cerne do livro.",
    },
    "principles-of-data-science": {
        "add": ["machine-learning", "estatistica"],
        "evidence": "unidades de análise estatística e de predição/modelagem (ML, redes neurais)",
        "rationale": "Estatística e ML são unidades inteiras do OpenStax.",
    },
    "projeto-de-algoritmos-em-c": {
        "add": ["c", "estruturas-de-dados"],
        "evidence": "código C limpo; vetores, listas, filas, pilhas, árvores binárias de busca",
        "rationale": "Algoritmos em C, com estruturas de dados como espinha dorsal.",
    },
    "think-data-structures": {
        "add": ["python"],
        "evidence": "implementação em Python",
        "rationale": "Estruturas de dados implementadas em Python (Downey).",
    },
    "think-stats-probability-and-statistics-for-pr": {
        "add": ["python"],
        "evidence": "usa Python para desenvolver intuição estatística",
        "rationale": "Estatística computacional em Python.",
    },
    # DevOps
    "basic-computer-architecture": {
        "add": ["assembly"],
        "evidence": "assembly para ARM, x86 e RISC-V",
        "rationale": "Assembly é ensinado explicitamente para três ISAs.",
    },
    "casamento-de-padroes-no-shell-do-gnulinux": {
        "add": ["bash"],
        "evidence": "Bash (shopt, GLOBIGNORE), globs, expressões regulares no shell",
        "rationale": "Livro de Bash/shell pattern matching.",
    },
    "information-security-management-an-executive": {
        "add": ["gestao-de-tecnologia"],
        "evidence": "visão executiva, governança, comitê de segurança, ISO 27002",
        "rationale": "Segurança sob a ótica de gestão e decisão executiva.",
    },
    "introducao-ao-shell-script": {
        "add": ["bash"],
        "evidence": "shell script, variáveis, test, estruturas de controle",
        "rationale": "Curso de shell script (Bash) do Aurélio Jargas.",
    },
    "microsoft-technologies-3-devops-for-aspnet-co": {
        "add": ["dotnet"],
        "evidence": "ASP.NET Core, App Service, Azure DevOps",
        "rationale": "DevOps aplicado à plataforma .NET/ASP.NET Core.",
    },
    "operating-systems-from-0-to-1": {
        "add": ["assembly", "arquitetura-de-computadores"],
        "evidence": "x86 assembly, portas lógicas, bootloader, ELF em bare metal",
        "rationale": "Vai das portas lógicas ao kernel, ensinando assembly e arquitetura no caminho.",
    },
    "the-linux-command-line": {
        "add": ["bash"],
        "evidence": "programas completos em Bash, redirecionamento, pipelines",
        "rationale": "Do terminal ao script Bash.",
    },
    "unix-application-and-system-programming-lectu": {
        "add": ["c"],
        "evidence": "exemplos compiláveis, código C até o hardware",
        "rationale": "Programação de sistemas UNIX em C.",
    },
    # Geral
    "algorithms-and-complexity": {
        "add": ["teoria-da-computacao"],
        "evidence": "NP-completude, máquinas de Turing, teorema de Cook",
        "rationale": "Metade final é complexidade e teoria da computação.",
    },
    "an-introduction-to-cellular-automata": {
        "add": ["sistemas-complexos"],
        "evidence": "regras locais gerando comportamento coordenado",
        "rationale": "Autômatos celulares como sistemas complexos.",
    },
    "cellular-automata-machines": {
        "add": ["sistemas-complexos"],
        "evidence": "modelagem física, fenômenos coletivos, difusão, fluidos",
        "rationale": "Autômatos celulares aplicados a sistemas complexos/físicos.",
    },
    "compiler-construction-using-c-slangfornet": {
        "add": ["compiladores"],
        "evidence": "AST, fases do compilador, recursive descent parsing",
        "rationale": "Construção de compilador (título).",
    },
    "computer-science-class-xi": {
        "add": ["python"],
        "evidence": "Python: funções, condicionais, loops, strings, listas, dicionários",
        "rationale": "Python é a linguagem de programação do currículo.",
    },
    "computer-science-class-xii": {
        "add": ["python"],
        "evidence": "prática baseada em Python",
        "rationale": "Python é a linguagem do currículo.",
    },
    "computer-science-ii": {
        "add": ["programacao-orientada-a-objetos", "bancos-de-dados"],
        "evidence": "quatro pilares de OOP, SOLID; tabelas, SQL, normalização",
        "rationale": "CS2 cobre OOP e banco de dados como unidades centrais.",
    },
    "elementary-algorithms": {
        "add": ["estruturas-de-dados"],
        "evidence": "listas, BSTs, heaps, priority queues",
        "rationale": "Construído a partir de estruturas de dados.",
    },
    "foundations-of-computer-science": {
        "add": ["matematica-discreta", "teoria-da-computacao"],
        "evidence": "combinatória, probabilidade discreta, lógica; autômatos, gramáticas",
        "rationale": "Aho/Ullman entrelaçam matemática discreta e teoria da computação.",
    },
    "foundations-of-programming": {
        "add": ["engenharia-de-software", "dotnet"],
        "evidence": "DDD, DI, testes, princípios de manutenibilidade; ecossistema .NET",
        "rationale": "Princípios de engenharia de software aplicados em .NET.",
    },
    "introduction-to-computer-science": {
        "add": ["algoritmos"],
        "evidence": "estruturas de dados, propriedades formais de algoritmos, paradigmas algorítmicos",
        "rationale": "Algoritmos é um dos eixos centrais do survey.",
    },
    "the-art-of-high-performance-computing-volume-2": {
        "add": ["concorrencia"],
        "evidence": "MPI, OpenMP, programação paralela",
        "rationale": "Programação paralela/concorrente para ciência.",
    },
    "the-art-of-high-performance-computing-volume-3": {
        "add": ["c-plus-plus", "fortran"],
        "evidence": "metade C++ e trilha paralela Fortran2008",
        "rationale": "Ensina as duas linguagens lado a lado.",
    },
    "the-art-of-high-performance-computing---volume-4": {
        "add": ["bash"],
        "evidence": "linha de comando Unix: pipes, redirecionamento, sed, awk, shell script",
        "rationale": "CLI/shell é habilidade de primeira classe no 'carpentry'.",
    },
    "the-design-of-approximation-algorithms": {
        "add": ["otimizacao"],
        "evidence": "problemas de otimização, programação linear/inteira",
        "rationale": "Algoritmos de aproximação para otimização.",
    },
    # IA
    "a-brief-introduction-to-machine-learning-for": {
        "add": ["estatistica"],
        "evidence": "pensamento Bayesiano e frequentista, modelos probabilísticos",
        "rationale": "ML com base estatística/probabilística explícita.",
    },
    "ai-safety-for-fleshy-humans": {
        "add": ["ia-e-sociedade"],
        "evidence": "alignment, viés, interpretabilidade, governança, uso indevido",
        "rationale": "Segurança e impacto social da IA.",
    },
    "algorithms-for-decision-making": {
        "add": ["inteligencia-artificial", "aprendizado-por-reforco"],
        "evidence": "MDPs, planejamento, actor-critic, multiagente",
        "rationale": "Decisão sob incerteza: IA + aprendizado por reforço.",
    },
    "algorithms-for-reinforcement-learning": {
        "add": ["aprendizado-por-reforco"],
        "evidence": "TD learning, Q-learning, actor-critic, MDPs",
        "rationale": "Aprendizado por reforço (título).",
    },
    "artificial-intelligence-and-the-future-for-te": {
        "add": ["ia-e-sociedade"],
        "evidence": "política educacional, privacidade, vigilância, equidade",
        "rationale": "IA na educação: dimensão social e de governança.",
    },
    "artificial-intelligence-for-a-better-future-a": {
        "add": ["ia-e-sociedade"],
        "evidence": "ética da IA, privacidade, viés, trabalho, democracia",
        "rationale": "Ética e impactos sociais da IA.",
    },
    "artificial-intelligence-foundations-of-comput": {
        "add": ["machine-learning"],
        "evidence": "aprendizado supervisionado/não supervisionado, redes neurais, deep learning, RL",
        "rationale": "ML é uma das grandes áreas cobertas pelo livro de agentes.",
    },
    "bayesian-reasoning-and-machine-learning": {
        "add": ["estatistica"],
        "evidence": "inferência probabilística, modelos gráficos, Gaussian processes",
        "rationale": "ML bayesiano/probabilístico.",
    },
    "graph-representational-learning-book": {
        "add": ["machine-learning"],
        "evidence": "node embeddings, GNNs, message passing",
        "rationale": "Aprendizado de máquina sobre grafos.",
    },
    "inteligencia-artificial-avancos-e-tendencias": {
        "add": ["ia-e-sociedade"],
        "evidence": "vieses, direito, sociologia, artes, finanças",
        "rationale": "IA como fenômeno social e cultural (coletânea C4AI-USP).",
    },
    "kalman-and-bayesian-filters-in-python": {
        "add": ["processamento-de-sinais"],
        "evidence": "filtros (g-h, Kalman, partículas), estimação de estado",
        "rationale": "Filtragem e estimação de sinais/estado.",
    },
    "on-the-path-to-ai-laws-prophecies-and-the-con": {
        "add": ["ia-e-sociedade"],
        "evidence": "direito, accountability, viés, regulação",
        "rationale": "ML sob a lente do direito e da sociedade.",
    },
    "pattern-recognition-and-machine-learning": {
        "add": ["estatistica"],
        "evidence": "teoria de probabilidade, inferência aproximada, modelos gráficos",
        "rationale": "Bishop: abordagem probabilística/estatística de ML.",
    },
    "probabilistic-machine-learning---an-introduct": {
        "add": ["estatistica"],
        "evidence": "probabilidade, estatística, decisão bayesiana, inferência",
        "rationale": "ML probabilístico (Murphy).",
    },
    "probabilistic-machine-learning-advanced-topic": {
        "add": ["estatistica", "deep-learning"],
        "evidence": "inferência variacional, Monte Carlo; VAEs, diffusion, GANs",
        "rationale": "ML probabilístico avançado + modelos generativos profundos.",
    },
    "quantum-algorithms": {
        "add": ["computacao-quantica"],
        "evidence": "quantum Fourier transform, Shor, quantum walks",
        "rationale": "Algoritmos quânticos (título).",
    },
    "the-lion-way-machine-learning-plus-intelligen": {
        "add": ["otimizacao"],
        "evidence": "machine learning + otimização inteligente (título), LSH, LASSO",
        "rationale": "ML fundado em otimização.",
    },
}

# Notas de "deixar como está" para casos relevantes (o resto usa DEFAULT_LEAVE).
LEAVE_NOTES: dict[str, str] = {
    "evidence-based-software-engineering": "Decisão editorial prévia (override) deixou apenas 'engenharia-de-software'; mantida.",
    "latexacao": "Override prévio fixou apenas 'latex'; mantida.",
    "ray-tracing-gems": "Regra explícita: não leva 'observabilidade'; 'computação-gráfica' basta.",
    "the-joy-of-cryptography": "'criptografia' é o eixo preciso; nenhum eixo secundário sustentado.",
    "culture-empire-digital-revolution": "Memória/memoir; a tag atual não pede eixo adicional (evitar ruído editorial).",
    "the-quest-for-artificial-intelligence-a-histo": "História da IA; 'inteligência-artificial' é honesto e suficiente.",
}

DEFAULT_LEAVE = "Tag atual é honesta e suficiente; a sinopse não sustenta eixo transversal adicional sem forçar cobertura."


def request_json_retry(url: str, *, method: str = "GET", body: dict[str, Any] | None = None,
                       headers: dict[str, str] | None = None, attempts: int = 4) -> Any:
    """request_json com retry em 503/429 transitórios (sleep de 10s entre tentativas)."""
    import time
    for attempt in range(attempts):
        try:
            return request_json(url, method=method, body=body, headers=headers)
        except ApiHttpError as exc:
            if exc.code not in {503, 429} or attempt >= attempts - 1:
                raise
            time.sleep(10)
    return None



def seed_new_tags(token: str) -> list[str]:
    headers = auth_headers(token)
    existing = {tag["id"] for tag in request_json(f"{API_BASE}/Tag", headers=headers)}
    created: list[str] = []
    for tag in NEW_TAGS:
        if tag["id"] in existing:
            continue
        request_json_retry(f"{API_BASE}/Tag", method="POST", body=tag, headers=headers)
        created.append(tag["id"])
    return created


def build_plan(token: str) -> dict[str, Any]:
    headers = auth_headers(token)
    categories = request_json(f"{API_BASE}/Category", headers=headers)["items"]
    tech_ids = collect_tech_category_ids(categories)
    cat_by_id = {c["id"]: c for c in flatten_categories(categories)}

    books = request_json(f"{API_BASE}/Book/1/9999", headers=headers).get("items") or []
    tags = request_json(f"{API_BASE}/Tag", headers=headers) or []
    tag_by_id = {t["id"]: t for t in tags}

    enriched: list[dict[str, Any]] = []
    left_as_is: list[dict[str, Any]] = []
    missing: list[str] = []

    for book in books:
        if not (
            book.get("type") == "Eletronic"
            and book.get("status") == "Available"
            and book.get("categoryId") in tech_ids
        ):
            continue

        existing = [t.get("id") for t in (book.get("tags") or []) if t.get("id")]
        if not existing:
            existing = get_existing_book_tags(token, book["id"])
        if len(existing) != 1:
            continue  # alvo: exatamente 1 tag

        slug = book.get("slug") or ""
        entry = ENRICHMENTS.get(slug)
        if not entry:
            reason = LEAVE_NOTES.get(slug, DEFAULT_LEAVE)
            left_as_is.append({
                "bookId": book["id"],
                "slug": slug,
                "title": book.get("title"),
                "author": book.get("author"),
                "categoryPath": cat_by_id.get(book.get("categoryId"), {}).get("path"),
                "existingTags": existing,
                "existingTagNames": [tag_by_id.get(t, {}).get("name") for t in existing],
                "reason": reason,
            })
            continue

        added = [t for t in entry["add"] if t not in existing]
        final = (existing + added)[:MAX_TAGS_PER_BOOK]
        enriched.append({
            "bookId": book["id"],
            "slug": slug,
            "title": book.get("title"),
            "author": book.get("author"),
            "categoryPath": cat_by_id.get(book.get("categoryId"), {}).get("path"),
            "existingTags": existing,
            "addedTags": added,
            "finalTags": final,
            "evidence": entry["evidence"],
            "rationale": entry["rationale"],
        })

    enriched.sort(key=lambda x: x["title"] or "")
    left_as_is.sort(key=lambda x: x["title"] or "")

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "oneTagBooksSeen": len(enriched) + len(left_as_is),
        "enrichedTotal": len(enriched),
        "leftAsIsTotal": len(left_as_is),
        "missingFromCatalog": missing,
        "newTags": [{"id": t["id"], "name": t["name"], "rationale": t["description"]} for t in NEW_TAGS],
        "enriched": enriched,
        "leftAsIs": left_as_is,
    }


def apply_plan(token: str, plan: dict[str, Any]) -> list[dict[str, Any]]:
    headers = auth_headers(token)
    applied: list[dict[str, Any]] = []
    for item in plan["enriched"]:
        response = request_json_retry(
            f"{API_BASE}/Tag/Book/{item['bookId']}",
            method="PUT",
            headers=headers,
            body={"TagIds": item["finalTags"]},
        ) or []
        applied.append({
            "bookId": item["bookId"],
            "title": item["title"],
            "applied": [tag.get("id") for tag in response],
        })
    return applied


def recount_distribution(token: str) -> dict[str, int]:
    headers = auth_headers(token)
    categories = request_json(f"{API_BASE}/Category", headers=headers)["items"]
    tech_ids = collect_tech_category_ids(categories)
    books = request_json(f"{API_BASE}/Book/1/9999", headers=headers).get("items") or []
    dist: dict[str, int] = {}
    for book in books:
        if not (
            book.get("type") == "Eletronic"
            and book.get("status") == "Available"
            and book.get("categoryId") in tech_ids
        ):
            continue
        existing = [t.get("id") for t in (book.get("tags") or []) if t.get("id")]
        if not existing:
            existing = get_existing_book_tags(token, book["id"])
        n = len(existing)
        dist[str(n)] = dist.get(str(n), 0) + 1
    return dist


def write_report(plan: dict[str, Any], suffix: str) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / f"enrich-single-tag-{suffix}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Enriquece ebooks técnicos com exatamente 1 tag.")
    parser.add_argument("--apply", action="store_true", help="Aplica as tags em produção.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    env_values = load_env(repo_root)

    def run(token: str) -> dict[str, Any]:
        created = seed_new_tags(token) if args.apply else []
        plan = build_plan(token)
        plan["mode"] = "apply" if args.apply else "dry-run"
        plan["createdTags"] = created
        report = write_report(plan, "apply" if args.apply else "dry-run")
        result: dict[str, Any] = {
            "mode": plan["mode"],
            "createdTags": created,
            "enrichedTotal": plan["enrichedTotal"],
            "leftAsIsTotal": plan["leftAsIsTotal"],
            "report": str(report),
        }
        if args.apply:
            result["applied"] = apply_plan(token, plan)
            result["distributionAfter"] = recount_distribution(token)
        return result

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
