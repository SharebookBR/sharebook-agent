# Grava planos editoriais para os 5 itens triados manualmente (ebook_foundation_subjects)
# Sinopses em ingles, conforme prompt editorial da source.
# Categorias: DevOps / Dados / Geral conforme guia de decisao.

from __future__ import annotations

import json
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import psycopg2


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    with open(r"C:\Repos\SHAREBOOK\sharebook-agent\.env", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"')
    return env


def pg_connect(dsn: str):
    prefix = "postgresql://"
    rest = dsn[len(prefix):]
    userpass, hostdb = rest.rsplit("@", 1)
    user, password = userpass.split(":", 1)
    hostport, database = hostdb.split("/", 1)
    host, port = hostport.split(":", 1)
    return psycopg2.connect(
        user=urllib.parse.unquote(user),
        password=urllib.parse.unquote(password),
        host=host,
        port=int(port),
        dbname=database,
    )


# ---------------------------------------------------------------------------
# Planos
# ---------------------------------------------------------------------------

DEVOPS_ID   = "019d636c-640a-7e2f-babd-c22d3b37c226"
DADOS_ID    = "019d636c-62c1-71e9-9a51-099d3304753e"
GERAL_ID    = "019dcbfc-0a09-702e-a0ab-090acb5597b6"

PLANS = [
    {
        "id": 1298,
        "planned_title": "Network Security",
        "planned_author": "OpenLearn",
        "planned_category_id": DEVOPS_ID,
        "planned_synopsis": (
            "Every network carries information worth stealing and systems worth disrupting. "
            "Understanding the principles behind attack and defense matters more than memorizing "
            "today's tools, and this course makes that distinction explicit from the start: "
            "the first chapter is an upfront glossary of 40+ terms, from passive attack and "
            "ciphertext to demilitarised zone and nonce, so readers speak the same language "
            "before the technical argument begins.\n\n"
            "The material moves from passive and active attack taxonomies through the "
            "fundamentals of symmetric and asymmetric encryption, explaining why key length "
            "alone does not guarantee security. It then covers how encryption is implemented "
            "at different network layers before turning to authentication mechanisms, "
            "certification authorities, digital certificates, and the layered world of "
            "firewalls: packet-filtering routers, application-level gateways, and "
            "circuit-level gateways. Self-assessment questions with answers are embedded "
            "throughout, making this a structured learning experience rather than a reference "
            "to skim.\n\n"
            "Produced by The Open University as part of its level-3 Computing & IT curriculum, "
            "this compact 58-page unit delivers the conceptual backbone that practitioners need "
            "to evaluate and compare security solutions on their own terms, without relying on "
            "vendor narratives or chasing the threat of the week."
        ),
        "planned_by": "manual_windows",
    },
    {
        "id": 1297,
        "planned_title": "Information Security Management: An Executive View",
        "planned_author": "Marcos Semola",
        "planned_category_id": DEVOPS_ID,
        "planned_synopsis": (
            "Most executives think information security means buying the right firewall. "
            "This book is written specifically to correct that misunderstanding: the author "
            "opens with a Knowledge Checkpoint chapter that forces consolidation of every "
            "concept before the reader moves forward, a structural choice that signals this "
            "is a framework for decision-making, not a catalog of technologies.\n\n"
            "The core of the book is a six-barrier defense model that sequences protection "
            "from discouragement through detection and diagnosis, paired with a risk equation "
            "and a corporate information security committee structure. Chapters cover the "
            "information lifecycle in four moments (handling, storage, transport, disposal), "
            "the role of the Security Officer, business continuity planning with hot and warm "
            "site strategies, and a full ISO 27002 compliance chapter with a scored testing "
            "instrument. A final chapter addresses cloud, BYOD, and social media as the new "
            "perimeter. Originally a bestselling title in the Brazilian market, this English "
            "translation adds a foreword from UFRJ information security specialists.\n\n"
            "The book gives executives and senior managers the vocabulary and the governance "
            "structures to lead security decisions rather than delegate them entirely to "
            "technical teams. Readers leave with a defensible framework for risk, not just "
            "a checklist."
        ),
        "planned_by": "manual_windows",
    },
    {
        "id": 1295,
        "planned_title": "Search Engines: Information Retrieval in Practice",
        "planned_author": "W. Bruce Croft, Donald Metzler, Trevor Strohman",
        "planned_category_id": DADOS_ID,
        "planned_synopsis": (
            "Search is everywhere, but the internals of a search engine remain opaque to "
            "most of the engineers who rely on them. This textbook from UMass Amherst's "
            "Center for Intelligent Information Retrieval solves that: it walks from raw "
            "document acquisition to final ranking in a single coherent arc, and the last "
            "chapter, Beyond Bag of Words, pushes into term dependence models, XML retrieval, "
            "entity search, and multimodal content, topics that standard IR courses skip.\n\n"
            "The chapters follow the architecture of a real engine: crawling and document "
            "feeds, text processing with statistical laws (Zipf, Heaps), inverted index "
            "construction including MapReduce-scale indexing, query processing and relevance "
            "feedback, retrieval models from Boolean through vector space to language models "
            "and inference networks, evaluation with TREC test collections and clickthrough "
            "data, and classification and clustering using Naive Bayes and Support Vector "
            "Machines. The Galago search engine ships alongside the book so readers can "
            "run experiments against real document collections rather than toy examples.\n\n"
            "Designed for undergraduates and graduate students in computer science and "
            "information science, and freely released by the authors in 2015, this textbook "
            "remains one of the clearest paths from zero to production-ready search "
            "engineering knowledge."
        ),
        "planned_by": "manual_windows",
    },
    {
        "id": 1268,
        "planned_title": "Flexible Operating System Internals: The Design and Implementation of the Anykernel and Rump Kernels",
        "planned_author": "Antti Kantee",
        "planned_category_id": DEVOPS_ID,
        "planned_synopsis": (
            "Testing kernel code without a full machine, virtualizing a single driver without "
            "duplicating the entire kernel, or running a file system in userspace are problems "
            "that monolithic kernels handle poorly. This doctoral dissertation from Aalto "
            "University proposes the anykernel and rump kernel architecture as the answer, "
            "and Chapter 3 alone covers more than 40 subsystems to prove the claim in "
            "production-grade detail: CPU scheduling, interrupt handling, virtual memory, "
            "networking and disk I/O backends, USB pass-through with hub support, and "
            "microkernel file server integration.\n\n"
            "The architecture separates the kernel into a base, orthogonal factions, and "
            "drivers, each runnable in isolation as a rump kernel client: userspace process, "
            "microkernel server, hypervisor guest, or remote client over a network. The "
            "implementation chapter documents the hypercall interface, C symbol namespace "
            "protection, system call overhead measurements, and the page remapping vs. "
            "copying trade-off with benchmarks. The evaluation chapter analyzes implementation "
            "effort, regression catches, portability to non-NetBSD hosts, and a security "
            "case study with file system drivers. Appendix B is a self-contained tutorial "
            "for building distributed kernel services from scratch, including an NFS server "
            "and TCP/IP stack restarts.\n\n"
            "Written to accompany the production NetBSD implementation it describes, this "
            "dissertation gives systems programmers a rare combination: the theoretical "
            "framework for kernel decomposition and the working code to validate every claim. "
            "Readers who study it alongside the NetBSD source gain depth unavailable in any "
            "standard operating systems textbook."
        ),
        "planned_by": "manual_windows",
    },
    {
        "id": 1265,
        "planned_title": "The Art of Community",
        "planned_author": "Jono Bacon",
        "planned_category_id": GERAL_ID,
        "planned_synopsis": (
            "Most communities collapse not for lack of passion but for lack of structure. "
            "Jono Bacon, who managed the Ubuntu community at its largest, built this book "
            "around the hardest parts that most guides ignore: Chapter 10 includes a full "
            "Ubuntu governance case study with real council committee structures, while "
            "Chapter 14 is an interview collection with Linus Torvalds, Tim O'Reilly, "
            "Dries Buytaert, and a dozen other builders who describe what actually broke "
            "their communities and what fixed them.\n\n"
            "The book covers the full lifecycle: planning team structures and community "
            "design, building communication channels, creating sustainable processes, "
            "selecting workflow tools, executing social media strategy, measuring growth "
            "and decline with real metrics, and running events from small local meetups "
            "to large developer summits. Conflict resolution and governance get their own "
            "dedicated chapters. Notably, Chapter 11 addresses burnout, long-term member "
            "absence, and bereavement explicitly, treating the human cost of sustained "
            "collaboration as a first-class operational concern rather than a footnote.\n\n"
            "Released under a Creative Commons license, this second O'Reilly edition "
            "distills Bacon's experience running one of the largest collaborative projects "
            "in technology history into a practical framework that applies equally to "
            "open source, product communities, activism, and any group that wants to "
            "build something together over the long term."
        ),
        "planned_by": "manual_windows",
    },
]


def set_plan(conn, plan: dict) -> None:
    item_id = plan["id"]
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE importer.queue_items
            SET status='waiting_process',
                planned_title=%s,
                planned_author=%s,
                planned_category_id=%s,
                planned_synopsis=%s,
                planned_cover_mode='source',
                planned_by=%s,
                planned_at=%s,
                updated_at=%s
            WHERE id=%s
            """,
            (
                plan["planned_title"],
                plan["planned_author"],
                plan["planned_category_id"],
                plan["planned_synopsis"],
                plan["planned_by"],
                utc_now(),
                utc_now(),
                item_id,
            ),
        )
        rows = cur.rowcount
    print(f"  #{item_id} {plan['planned_title'][:50]} -> waiting_process  ({rows} row updated)")


def main() -> None:
    env = load_env()
    conn = pg_connect(env["IMPORTER_DB_DSN"])

    print(f"\nGravando {len(PLANS)} planos editoriais...\n")
    for plan in PLANS:
        set_plan(conn, plan)

    conn.commit()
    conn.close()
    print("\nFeito.")


if __name__ == "__main__":
    main()
