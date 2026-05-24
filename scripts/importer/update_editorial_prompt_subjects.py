# -*- coding: utf-8 -*-
"""Atualiza o editorial_prompt da source ebook_foundation_subjects."""
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
4. context_text (texto extraído do PDF)
5. local_pdf_path (fallback manual — registrar "preparer-subjects (via manual pdf read)" no planned_by)

## Título
Manter em inglês exatamente como está no arquivo original. Não traduzir.

## Sinopse
- Escrever em inglês.
- 3 parágrafos.
- Parágrafo 1: apresentar o tema central e o escopo do livro.
- Parágrafo 2: principais tópicos cobertos e o que o leitor vai dominar.
- Parágrafo 3: para quem é, pré-requisitos e por que vale ler.
- Não inventar informações que não estejam no PDF ou no contexto da entry.

## Nível
Deduzir pelo título, subject e conteúdo do PDF:
- basico → introduções, "for beginners", "getting started", fundamentos
- intermediario → sem indicação explícita de nível
- avancado → "advanced", papers acadêmicos, teoria formal, matemática densa

## Capa
Autoral — não há capa original nesta source.

## Categorias disponíveis (usar sempre subcategoria de Tecnologia)

| Subcategoria | ID | Subjects que cobre |
|---|---|---|
| IA        | 019d636c-6365-74c5-9323-14be85d8b0a3 | Machine Learning, Artificial Intelligence, Computer Vision, NLP, Quantum Computing |
| Dados     | 019d636c-62c1-71e9-9a51-099d3304753e | Data Science, Database, Statistics, Information Retrieval |
| Cloud     | 019d636c-6206-7f05-ade0-14ed095dd21c | Cloud Computing, Containers, Networking |
| DevOps    | 019d636c-640a-7e2f-babd-c22d3b37c226 | Operating Systems, Linux, Security & Privacy, Reverse Engineering, Embedded Systems |
| Frontend  | 019d636c-616a-7dcb-af70-77619c9dbaf5 | Web, JavaScript, HTML, CSS, Graphics Programming |
| Backend   | 019d636c-5fdd-7505-9c76-e02944d9b618 | Algorithms & Data Structures, Software Architecture, Compiler Design, Programming Languages, OOP |
| Geral     | 019dcbfc-0a09-702e-a0ab-090acb5597b6 | Mathematics, Theoretical Computer Science, Misc, Professional Development, tudo que não se encaixar acima |

## Guia de decisão rápida
- subject contém "Machine Learning" / "AI" / "Computer Vision" → IA
- subject contém "Data" / "Database" / "Statistics" → Dados
- subject contém "Cloud" / "Container" / "Network" → Cloud
- subject contém "Operating System" / "Linux" / "Security" / "Embedded" → DevOps
- subject contém "Web" / "JavaScript" / "CSS" → Frontend
- subject contém "Algorithm" / "Software" / "Compiler" / "Programming" → Backend
- subject contém "Math" / "Theoretical" / "Misc" / "Professional" → Geral
"""

conn = psycopg2.connect(
    host="212.85.23.202", port=5432, dbname="sharebook_importer",
    user="sharebook_ai_rw", password="F%Ljy9oxTA3iR#npW%4W9iaSaJKU", sslmode="disable"
)
cur = conn.cursor()
cur.execute(
    "UPDATE importer.sources SET editorial_prompt = %s, updated_at = NOW() WHERE name = %s",
    (EDITORIAL_PROMPT, "ebook_foundation_subjects")
)
print(f"Linhas afetadas: {cur.rowcount}")
conn.commit()
conn.close()
