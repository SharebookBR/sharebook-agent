"""Cria a source ebook_foundation_subjects no banco do importer."""
import psycopg2

EDITORIAL_PROMPT = """\
Source: EbookFoundation free-programming-books (subjects)
Livros tecnicos de programacao em ingles, organizados por assunto.

TITULO: manter em ingles exatamente como esta no arquivo original. Nao traduzir.
SINOPSE: escrever em portugues (PT-BR), 2-4 paragrafos, tom tecnico-informativo.
  Focar no que o leitor vai aprender/dominar. Mencionar o assunto principal.
  Nao inventar informacoes que nao estejam no PDF ou no contexto da entry.
AUTOR: usar o campo author ja pre-preenchido. Se vazio, extrair do PDF.
NIVEL: deduzir pelo titulo e conteudo (basico/intermediario/avancado).
CAPA: autoral (nao ha capa original nesta source).
CATEGORIA: mapear pelo subject da entry (disponivel no metadata_json.subject):
  Algorithms & Data Structures           -> Programacao > Algoritmos
  Artificial Intelligence / Machine Learning / Deep Learning -> Programacao > Inteligencia Artificial
  Security / Cryptography                -> Programacao > Seguranca
  Web / JavaScript / HTML / CSS / React  -> Programacao > Desenvolvimento Web
  Python                                 -> Programacao > Python
  Java                                   -> Programacao > Java
  C / C++ / C#                           -> Programacao > C/C++
  Go / Rust / Swift / Kotlin             -> Programacao > [linguagem]
  Database / SQL / NoSQL                 -> Programacao > Banco de Dados
  Operating Systems / Linux / Unix       -> Programacao > Sistemas Operacionais
  Software Engineering / Design Patterns -> Programacao > Engenharia de Software
  Cloud / DevOps / Docker / Kubernetes   -> Programacao > DevOps e Cloud
  Data Science / Statistics              -> Programacao > Ciencia de Dados
  Computer Science / Mathematics         -> Programacao
  Demais assuntos                        -> Programacao
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
