#!/usr/bin/env python3
"""Semeia o vocabulário v0 de tags e associa aos 5 livros do ciclo manual.

Idempotente: cria apenas tags que ainda não existem e reaplica as associações.
Fonte editorial: backlog/todo/tags-e-conhecimento-estruturado/tarefa02 + tarefa01-resultado.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sharebook_prod_auth import (  # noqa: E402
    API_BASE,
    ApiHttpError,
    auth_headers,
    get_token,
    load_env,
    request_json,
)

# slug -> (name, family, aliases, description)
TAGS = {
    "python": ("Python", "linguagens-frameworks", ["py"],
               "Livros sobre a linguagem Python e seu ecossistema."),
    "r": ("R", "linguagens-frameworks", ["linguagem-r", "r-language"],
          "Livros sobre a linguagem R, análise estatística e visualização de dados."),
    "docker": ("Docker", "infra-cloud-seguranca", ["containers", "conteineres"],
               "Contêineres, Docker e empacotamento de aplicações."),
    "kubernetes": ("Kubernetes", "infra-cloud-seguranca", ["k8s"],
                   "Orquestração de contêineres com Kubernetes."),
    "devops": ("DevOps", "infra-cloud-seguranca", ["operacoes", "infra"],
               "Cultura, automação e operação de software."),
    "machine-learning": ("Machine Learning", "dados-ia", ["ml", "aprendizado-de-maquina"],
                         "Aprendizado de máquina: modelos, treinamento e avaliação."),
    "estatistica": ("Estatística", "dados-ia", ["statistics", "statistical-learning"],
                    "Estatística e aprendizado estatístico aplicado."),
    "microsservicos": ("Microsserviços", "backend-arquitetura", ["microservices", "micro-services"],
                       "Arquitetura, comunicação e operação de microsserviços."),
    "arquitetura": ("Arquitetura", "backend-arquitetura", ["arquitetura-de-software", "software-architecture"],
                    "Decisão estrutural e design de sistemas de software."),
    "computacao-de-alto-desempenho": ("Computação de Alto Desempenho", "fundamentos-computacao",
                                      ["hpc", "high-performance-computing"],
                                      "Performance científica, paralelismo e gargalos de execução."),
    "arquitetura-de-computadores": ("Arquitetura de Computadores", "fundamentos-computacao",
                                    ["computer-architecture", "organizacao-de-computadores"],
                                    "Hardware, memória, CPU e hierarquias."),
    "metodos-numericos": ("Métodos Numéricos", "fundamentos-computacao",
                          ["numerical-methods", "analise-numerica"],
                          "Algoritmos numéricos, solvers e cálculo científico."),
    "desenvolvimento-de-jogos": ("Desenvolvimento de Jogos", "frontend-graficos-jogos",
                                 ["game-dev", "game-development", "programacao-de-jogos"],
                                 "Construção de jogos, engines e programação de jogos."),
    "pratico": ("Prático", "uso-editorial", ["hands-on", "guia-pratico", "projetos"],
                "Livro aplicado: projetos, laboratório, checklist ou passo a passo."),
}

# book_id -> [tag slugs] (ordem = Position)
BOOK_TAGS = {
    "019f492b-6baa-7394-bc2a-fccdf2b33eaa": ["python", "desenvolvimento-de-jogos", "pratico"],
    "019f7ff2-6abc-7182-b87b-7fd81d903256": ["kubernetes", "docker", "devops"],
    "01a06473-7b51-7606-afe6-2c8e74e50964": ["machine-learning", "estatistica", "r"],
    "019f1a38-b3bc-74c1-b7ff-2a893c2b0ee8": ["microsservicos", "arquitetura", "pratico"],
    "019ebe0f-afa8-7a7d-a0c6-b53fbaaabca3": ["computacao-de-alto-desempenho",
                                            "arquitetura-de-computadores",
                                            "metodos-numericos"],
}


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    env_values = load_env(repo_root)
    token = get_token(env_values, repo_root=repo_root)

    def run():
        return _run(token)

    try:
        summary = run()
    except ApiHttpError as exc:
        if exc.code not in {401, 403}:
            raise
        token = get_token(env_values, repo_root=repo_root, force_refresh=True)
        summary = run()

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def _run(token: str) -> dict:
    headers = auth_headers(token)

    # 1. Lista tags admin existentes
    existing = request_json(f"{API_BASE}/Tag/Admin", headers=headers)
    existing_ids = {t.get("id") for t in (existing or [])}

    created = []
    skipped = []
    for slug, (name, family, aliases, description) in TAGS.items():
        if slug in existing_ids:
            skipped.append(slug)
            continue
        body = {
            "Id": slug,
            "Name": name,
            "Aliases": aliases,
            "Family": family,
            "Description": description,
            "UsageNotes": None,
            "Status": "Active",
            "IsPublic": True,
        }
        request_json(f"{API_BASE}/Tag", method="POST", body=body, headers=headers)
        created.append(slug)

    # 2. Associa tags aos livros (reaplica)
    book_results = []
    for book_id, tag_slugs in BOOK_TAGS.items():
        body = {"TagIds": tag_slugs}
        resp = request_json(
            f"{API_BASE}/Tag/Book/{book_id}", method="PUT", body=body, headers=headers
        )
        book_results.append({
            "bookId": book_id,
            "applied": [t.get("id") for t in (resp or [])],
        })

    return {"createdTags": created, "skippedExisting": skipped, "books": book_results}


if __name__ == "__main__":
    raise SystemExit(main())
