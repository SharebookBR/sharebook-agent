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
    "c": ("C", "linguagens-frameworks", ["linguagem-c", "c-language"],
          "Livros sobre a linguagem C e seu ecossistema."),
    "c-plus-plus": ("C++", "linguagens-frameworks", ["cplusplus", "cpp"],
                    "Livros sobre C++ como linguagem e ecossistema."),
    "csharp": ("C#", "linguagens-frameworks", ["c-sharp", "c-sharp-language"],
               "Livros sobre C# e desenvolvimento no ecossistema Microsoft."),
    "dotnet": (".NET", "linguagens-frameworks", ["asp-net", "net"],
               "Livros sobre .NET, ASP.NET e a plataforma relacionada."),
    "go": ("Go", "linguagens-frameworks", ["golang", "go-lang"],
           "Livros sobre a linguagem Go."),
    "java": ("Java", "linguagens-frameworks", [],
             "Livros sobre Java e seu ecossistema."),
    "javascript": ("JavaScript", "linguagens-frameworks", ["js", "java-script", "nodejs", "node-js"],
                   "Livros sobre JavaScript no navegador, backend e ecossistema web."),
    "php": ("PHP", "linguagens-frameworks", [],
            "Livros sobre PHP e desenvolvimento web/backend."),
    "python": ("Python", "linguagens-frameworks", ["py"],
               "Livros sobre a linguagem Python e seu ecossistema."),
    "r": ("R", "linguagens-frameworks", ["linguagem-r", "r-language"],
          "Livros sobre a linguagem R, análise estatística e visualização de dados."),
    "scala": ("Scala", "linguagens-frameworks", [],
              "Livros sobre Scala, JVM e programação funcional."),
    "spring-boot": ("Spring Boot", "linguagens-frameworks", ["spring", "spring-framework"],
                    "Livros sobre Spring Boot e backend Java."),
    "typescript": ("TypeScript", "linguagens-frameworks", ["ts", "type-script"],
                   "Livros sobre TypeScript no frontend e backend moderno."),
    "sql": ("SQL", "linguagens-frameworks", [],
            "Livros sobre SQL, consultas e bancos relacionais."),
    "apis": ("APIs", "backend-arquitetura", ["api", "rest", "graphql"],
             "Livros sobre desenho, consumo e contrato de APIs."),
    "backend": ("Backend", "backend-arquitetura", ["back-end", "server-side"],
                "Livros sobre desenvolvimento server-side e serviços de aplicação."),
    "clean-code": ("Clean Code", "backend-arquitetura", ["codigo-limpo", "code-quality", "qualidade-de-codigo"],
                   "Livros sobre legibilidade, manutenção e qualidade de código."),
    "design-patterns": ("Design Patterns", "backend-arquitetura", ["padroes-de-projeto", "patterns"],
                        "Livros sobre padrões de projeto e design de código."),
    "event-driven": ("Event-Driven", "backend-arquitetura", ["arquitetura-orientada-a-eventos", "event-sourcing", "stream-processing"],
                     "Livros sobre eventos, streaming, pub/sub e padrões assíncronos."),
    "sistemas-distribuidos": ("Sistemas Distribuídos", "backend-arquitetura", ["distributed-systems"],
                              "Livros sobre comunicação, consenso, replicação e escala."),
    "testes": ("Testes", "backend-arquitetura", ["testing", "unit-testing", "testes-automatizados"],
               "Livros sobre testes automatizados, TDD e qualidade verificável."),
    "aws": ("AWS", "infra-cloud-seguranca", ["amazon-web-services", "amazon-s3"],
            "Livros sobre Amazon Web Services e serviços AWS."),
    "ci-cd": ("CI/CD", "infra-cloud-seguranca", ["continuous-integration", "continuous-delivery", "pipeline"],
              "Livros sobre build, testes, deploy e automação de entrega."),
    "cloud": ("Cloud", "infra-cloud-seguranca", ["computacao-em-nuvem", "cloud-computing"],
              "Livros sobre fundamentos e estratégia de computação em nuvem."),
    "docker": ("Docker", "infra-cloud-seguranca", ["containers", "conteineres"],
               "Contêineres, Docker e empacotamento de aplicações."),
    "kubernetes": ("Kubernetes", "infra-cloud-seguranca", ["k8s"],
                   "Orquestração de contêineres com Kubernetes."),
    "devops": ("DevOps", "infra-cloud-seguranca", ["operacoes", "infra"],
               "Cultura, automação e operação de software."),
    "git": ("Git", "infra-cloud-seguranca", ["controle-de-versao", "version-control"],
            "Livros sobre Git e controle de versão."),
    "linux": ("Linux", "infra-cloud-seguranca", ["unix", "shell", "linha-de-comando"],
              "Livros sobre Linux, Unix, shell e fundamentos operacionais."),
    "networking": ("Networking", "infra-cloud-seguranca", ["redes", "tcp-ip", "ipv6"],
                   "Livros sobre redes de computadores e protocolos."),
    "observabilidade": ("Observabilidade", "infra-cloud-seguranca", ["monitoramento", "logging", "metrics", "tracing"],
                        "Livros sobre logs, métricas, tracing e diagnóstico operacional."),
    "seguranca": ("Segurança", "infra-cloud-seguranca", ["security", "hardening", "appsec"],
                  "Livros sobre segurança aplicada e proteção de sistemas."),
    "criptografia": ("Criptografia", "infra-cloud-seguranca", ["cryptography", "crypto"],
                     "Livros sobre primitivos, protocolos e teoria criptográfica."),
    "bancos-de-dados": ("Bancos de Dados", "dados-ia", ["databases", "database", "banco-de-dados"],
                        "Livros sobre modelagem, projeto e sistemas de banco de dados."),
    "data-science": ("Data Science", "dados-ia", ["ciencia-de-dados"],
                     "Livros sobre ciclo de dados, análise e ciência de dados."),
    "deep-learning": ("Deep Learning", "dados-ia", ["redes-neurais", "neural-networks"],
                      "Livros sobre redes neurais e aprendizado profundo."),
    "machine-learning": ("Machine Learning", "dados-ia", ["ml", "aprendizado-de-maquina"],
                         "Aprendizado de máquina: modelos, treinamento e avaliação."),
    "estatistica": ("Estatística", "dados-ia", ["statistics", "statistical-learning"],
                    "Estatística e aprendizado estatístico aplicado."),
    "information-retrieval": ("Information Retrieval", "dados-ia", ["busca", "search-engines", "recuperacao-de-informacao"],
                              "Livros sobre motores de busca, indexação, ranking e avaliação de busca."),
    "computer-vision": ("Computer Vision", "dados-ia", ["visao-computacional", "image-processing"],
                        "Livros sobre visão computacional e processamento de imagem."),
    "algoritmos": ("Algoritmos", "fundamentos-computacao", ["algorithms"],
                   "Livros sobre análise, projeto e repertório algorítmico."),
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
    "compiladores": ("Compiladores", "fundamentos-computacao", ["compilers", "compiler-design"],
                     "Livros sobre parsing, análise, geração de código e runtimes."),
    "estruturas-de-dados": ("Estruturas de Dados", "fundamentos-computacao", ["data-structures"],
                            "Livros sobre listas, árvores, heaps, hashing, grafos e estruturas relacionadas."),
    "matematica-discreta": ("Matemática Discreta", "fundamentos-computacao", ["discrete-mathematics"],
                            "Livros sobre matemática discreta aplicada à computação."),
    "metodos-numericos": ("Métodos Numéricos", "fundamentos-computacao",
                          ["numerical-methods", "analise-numerica"],
                          "Algoritmos numéricos, solvers e cálculo científico."),
    "sistemas-operacionais": ("Sistemas Operacionais", "fundamentos-computacao", ["operating-systems", "kernel"],
                              "Livros sobre kernel, processos, memória, concorrência e sistemas de arquivos."),
    "teoria-da-computacao": ("Teoria da Computação", "fundamentos-computacao", ["theory-of-computation", "automatos", "turing"],
                             "Livros sobre computabilidade, autômatos, linguagens formais e complexidade."),
    "frontend": ("Frontend", "frontend-graficos-jogos", ["front-end", "web-frontend"],
                 "Livros sobre interface web, client-side e frontend."),
    "html-css": ("HTML/CSS", "frontend-graficos-jogos", ["html", "css"],
                 "Livros sobre marcação, estilo e fundamentos web."),
    "web-design": ("Web Design", "frontend-graficos-jogos", ["design-web"],
                   "Livros sobre composição, semântica, UX visual e construção de páginas."),
    "computacao-grafica": ("Computação Gráfica", "frontend-graficos-jogos",
                           ["computer-graphics", "opengl", "rendering", "ray-tracing"],
                           "Livros sobre computação gráfica, renderização e aplicações visuais."),
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
