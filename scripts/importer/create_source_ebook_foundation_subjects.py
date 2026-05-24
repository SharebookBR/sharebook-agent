# -*- coding: utf-8 -*-
"""Cria a source ebook_foundation_subjects no banco do importer."""
import psycopg2

EDITORIAL_PROMPT = """\
Source: EbookFoundation free-programming-books (subjects)
Livros técnicos de programação em inglês, organizados por assunto.

TÍTULO: manter em inglês exatamente como está no arquivo original. Não traduzir.
SINOPSE: escrever em português (PT-BR), 2-4 parágrafos, tom técnico-informativo.
  Focar no que o leitor vai aprender/dominar. Mencionar o assunto principal.
  Não inventar informações que não estejam no PDF ou no contexto da entry.
AUTOR: usar o campo author já pré-preenchido. Se vazio, extrair do PDF.
NÍVEL: deduzir pelo título e conteúdo (basico/intermediario/avancado).
CAPA: autoral (não há capa original nesta source).
CATEGORIA: usar sempre uma das subcategorias de Tecnologia abaixo.
  Escolher pelo subject da entry e pelo conteúdo do PDF.

  IA        (019d636c-6365-74c5-9323-14be85d8b0a3) → Machine Learning, Deep Learning, AI, Computer Vision, NLP, Quantum Computing
  Dados     (019d636c-62c1-71e9-9a51-099d3304753e) → Data Science, Database, Statistics, Information Retrieval
  Cloud     (019d636c-6206-7f05-ade0-14ed095dd21c) → Cloud Computing, Containers, Networking
  DevOps    (019d636c-640a-7e2f-babd-c22d3b37c226) → Operating Systems, Linux, Security, Reverse Engineering, Embedded Systems
  Frontend  (019d636c-616a-7dcb-af70-77619c9dbaf5) → Web, JavaScript, HTML, CSS, Graphics, UI
  Backend   (019d636c-5fdd-7505-9c76-e02944d9b618) → Algorithms, Software Architecture, Compiler Design, Programming Languages
  Geral     (019dcbfc-0a09-702e-a0ab-090acb5597b6) → Mathematics, Theoretical CS, Misc, Professional Development, tudo que não se encaixar acima
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
