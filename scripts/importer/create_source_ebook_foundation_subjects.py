# -*- coding: utf-8 -*-
"""Cria a source ebook_foundation_subjects no banco do importer."""
import psycopg2

EDITORIAL_PROMPT = """\
# Preparo Editorial — ebook_foundation_subjects

## Fonte
URL: https://raw.githubusercontent.com/EbookFoundation/free-programming-books/main/books/free-programming-books-subjects.md
Perfil: livros técnicos de programação em inglês, curados pela comunidade EbookFoundation.
Autor e subject já vêm pré-preenchidos no item — usar como insumo primário de categorização.

## Ordem de uso dos artefatos (obrigatória)
1. metadata_json.subject (subject do markdown — melhor sinal para categoria)
2. metadata_json.author (autor pré-preenchido do markdown)
3. preview_pages (PNGs das primeiras páginas — confirmar nível e conteúdo)
4. context_text (texto extraído do PDF — ler o table of contents antes de qualquer coisa)
5. local_pdf_path (fallback manual — registrar "preparer-subjects (via manual pdf read)" no planned_by)

## Regra absoluta: ler o table of contents antes de escrever
Antes de qualquer parágrafo, extrair e ler o table of contents do PDF.
Responder estas 3 perguntas com base no índice:
1. Estrutura: sequência de capítulos do começo ao fim?
2. Autoria: único autor, coletivo, institucional?
3. Diferencial inesperado: algo que não está no título?

O primeiro parágrafo da sinopse DEVE conter algo específico do table of contents.

## Título
Manter em inglês exatamente como está no arquivo original. Não traduzir.

## Sinopse
- Escrever em inglês.
- 3 parágrafos. Máximo 2000 caracteres. Ideal: 1200–1800.
- Parágrafo 1: gancho com o problema do leitor + algo específico do table of contents.
- Parágrafo 2: conteúdo real (tópicos principais, descobertas inesperadas do índice).
- Parágrafo 3: valor do material, diferencial, o que o leitor leva.
- Proibido: subtítulos nos parágrafos, datas/épocas, "In this book", sinopse genérica.

## Nível
Deduzir pelo título, subject e conteúdo do PDF:
- basico → introduções, "for beginners", "getting started", fundamentos
- intermediario → sem indicação explícita de nível
- avancado → "advanced", papers acadêmicos, teoria formal, matemática densa

## Capa
Autoral — não há capa original nesta source.
Gerar 6 variações com cover_generate.py, analisar visualmente, escolher a melhor.
Paletas: tron, deep-ocean, lava, frost, matrix, sunset, graphite, cyber, forest, platinum.
planned_cover_mode deve ser 'source'. Detalhes da capa em metadata_json.

## Categorias disponíveis (Tecnologia — usar apenas folhas)
| Subcategoria | ID | Subjects que cobre |
|---|---|---|
| IA        | 019d636c-6365-74c5-9323-14be85d8b0a3 | Machine Learning, Artificial Intelligence, Computer Vision, NLP, Quantum Computing |
| Dados     | 019d636c-62c1-71e9-9a51-099d3304753e | Data Science, Database, Statistics, Information Retrieval |
| Cloud     | 019d636c-6206-7f05-ade0-14ed095dd21c | Cloud Computing, Containers, Networking |
| DevOps    | 019d636c-640a-7e2f-babd-c22d3b37c226 | Operating Systems, Linux, Security & Privacy, Reverse Engineering, Embedded Systems |
| Frontend  | 019d636c-616a-7dcb-af70-77619c9dbaf5 | Web, JavaScript, HTML, CSS, Graphics Programming |
| Backend   | 019d636c-5fdd-7505-9c76-e02944d9b618 | Algorithms & Data Structures, Software Architecture, Compiler Design, Programming Languages, OOP |
| Geral     | 019dcbfc-0a09-702e-a0ab-090acb5597b6 | Mathematics, Theoretical Computer Science, Misc, Professional Development |

NUNCA usar "Conhecimento & Carreira" (`019d7e18-3fd3-7434-8033-28750c0881b5`) para livros de tecnologia.

## Guia de decisão rápida
- subject contém "Machine Learning" / "AI" / "Computer Vision" → IA
- subject contém "Data" / "Database" / "Statistics" → Dados
- subject contém "Cloud" / "Container" / "Network" → Cloud
- subject contém "Operating System" / "Linux" / "Security" / "Embedded" → DevOps
- subject contém "Web" / "JavaScript" / "CSS" → Frontend
- subject contém "Algorithm" / "Software" / "Compiler" / "Programming" → Backend
- subject contém "Math" / "Theoretical" / "Misc" / "Professional" → Geral

## Deduplicação semântica
Dois PDFs diferentes podem ser duplicatas se cobrem o mesmo assunto no mesmo nível.
Regra: só é duplicata se mesmo nível + mesma categoria. Caso contrário, convivem.
"""

conn = psycopg2.connect(
    host="212.85.23.202", port=5432, dbname="sharebook_importer",
    user="sharebook_ai_rw", password="F%Ljy9oxTA3iR#npW%4W9iaSaJKU", sslmode="disable"
)
cur = conn.cursor()
cur.execute("""
    INSERT INTO importer.sources (name, url, editorial_prompt, created_at, updated_at)
    VALUES (%s, %s, %s, NOW(), NOW())
    ON CONFLICT (name) DO NOTHING
    RETURNING id
""", (
    "ebook_foundation_subjects",
    "https://raw.githubusercontent.com/EbookFoundation/free-programming-books/main/books/free-programming-books-subjects.md",
    EDITORIAL_PROMPT,
))
row = cur.fetchone()
if row:
    print(f"Source criada com ID: {row[0]}")
else:
    cur.execute("SELECT id FROM importer.sources WHERE name = 'ebook_foundation_subjects'")
    print(f"Source ja existia, ID: {cur.fetchone()[0]}")
conn.commit()
conn.close()
