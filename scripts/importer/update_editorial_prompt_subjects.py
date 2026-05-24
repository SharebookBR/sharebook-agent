# -*- coding: utf-8 -*-
"""Atualiza o editorial_prompt da source ebook_foundation_subjects."""
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
CATEGORIA: usar sempre a categoria Tecnologia. Subcategorias disponíveis:
  - IA        → Machine Learning, Deep Learning, AI, Computer Vision, NLP
  - Dados     → Data Science, Database, Statistics, Information Retrieval
  - Cloud     → Cloud Computing, DevOps, Containers, Docker, Kubernetes
  - DevOps    → Operating Systems, Linux, Networking, Security
  - Frontend  → Web, JavaScript, HTML, CSS, Graphics, UI
  - Backend   → Algorithms, Software Engineering, Programming, Compiler Design
  - Geral     → tudo que não se encaixar claramente nas anteriores
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
