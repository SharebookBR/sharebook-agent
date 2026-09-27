#!/usr/bin/env python3
"""Gera o HTML do livro a partir de chapters/*.md e imprime o PDF (512x640 pt).

Capa e ilustrações não passam pelo Chromium: página sem margem no meio do fluxo
faz o Chromium encolher o documento inteiro. Elas entram depois, via PyMuPDF,
como páginas inteiras (capa na 1, cada ilustração antes da abertura do capítulo).

Uso: python3 build_book.py [--version vN]
Requer: pip install markdown pyphen; node com playwright (global) e Chromium do ambiente.
"""
import argparse
import glob
import html
import os
import re
import subprocess
import sys

import markdown
import pymupdf
import pyphen

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
SEAL = os.path.normpath(os.path.join(
    ROOT, "..", "..", "..", "product-ux", "cover-direction", "assets", "sharebook-originals-seal.png"))

# Chromium do habitat não baixa dicionário de hifenização pt-BR: inserimos &shy; aqui.
HYPH = pyphen.Pyphen(lang="pt_BR", left=3, right=3)
WORD = re.compile(r"[A-Za-zÀ-ÿ]{7,}")


def hyphenate(fragment):
    parts = re.split(r"(<[^>]+>)", fragment)
    for i, part in enumerate(parts):
        if not part.startswith("<"):
            parts[i] = WORD.sub(lambda m: HYPH.inserted(m.group(0), hyphen="\u00ad"), part)
    return "".join(parts)


TITLE = "Lumi, a Bruxinha"
TAGLINE = "Uma bruxinha que não sabia mandar. Uma floresta que só queria ser escutada."

# capítulo -> ilustração (página inteira antes da abertura do capítulo)
PLATES = {
    "01": "ilus-01-flor-espirro",
    "02": "ilus-02-fotografia",
    "03": "ilus-03-sala-secreta",
    "04": "ilus-04-festival",
    "05": "ilus-05-abraco",
    "06": "ilus-06-amelia",
    "07": "ilus-07-arvore-mae",
    "08": "ilus-08-pergunte",
    "09": "ilus-09-rosa-azul",
}


def find_asset(stem):
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        p = os.path.join(ASSETS, stem + ext)
        if os.path.exists(p):
            return p
    return None


def chapter_html(path):
    text = open(path, encoding="utf-8").read().strip()
    first, body = text.split("\n", 1)
    heading = first.lstrip("#").strip()
    if " — " in heading:
        label, name = heading.split(" — ", 1)
    else:
        label, name = "", heading
    body = re.sub(r"^---\s*$", '<p class="scene-break">* * *</p>', body, flags=re.M)
    body = body.replace("**FIM**", '<p class="fim">FIM</p>')
    inner = hyphenate(markdown.markdown(body, extensions=["sane_lists"]))
    return label, name, inner


def build_html(missing):
    parts = []
    seal = f'<img class="seal" src="file://{SEAL}" alt="Sharebook Originals">' if os.path.exists(SEAL) else ""
    parts.append(f"""
<section class="page title-page">
  <h1>Lumi,<span>a Bruxinha</span></h1>
  <p class="tagline">{html.escape(TAGLINE)}</p>
  {seal}
</section>
<section class="page imprint">
  <div>
    <p><strong>{html.escape(TITLE)}</strong></p>
    <p>Sharebook Originals · 2026</p>
    <p>Fantasia · Infantojuvenil</p>
    <p class="gap">Esta é uma obra de ficção. Nomes, personagens, lugares e acontecimentos
    são fruto da imaginação ou usados de forma fictícia. Qualquer semelhança com pessoas
    reais — ou com plantas que espirram — é mera coincidência.</p>
    <p class="gap">Distribuição gratuita pelo Sharebook — app livre e gratuito para doação de livros.<br>
    sharebook.com.br</p>
  </div>
</section>""")

    toc, chapters = [], []
    for path in sorted(glob.glob(os.path.join(ROOT, "chapters", "*.md"))):
        num = os.path.basename(path)[:2]
        label, name, inner = chapter_html(path)
        toc.append(f'<li><span class="toc-label">{html.escape(label)}</span>{html.escape(name)}</li>')
        label_html = f'<p class="ch-label">{html.escape(label)}</p>' if label else ""
        chapters.append(
            f'<section class="chapter">{label_html}<h2>{html.escape(name)}</h2>{inner}</section>')

    parts.append('<section class="page toc"><h2>Sumário</h2><ol>' + "".join(toc) + "</ol></section>")
    parts.extend(chapters)

    css = open(os.path.join(ROOT, "book.css"), encoding="utf-8").read()
    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
            f"<title>{html.escape(TITLE)}</title><style>{css}</style></head><body>"
            + "\n".join(parts) + "</body></html>")


def insert_images(pdf_path, missing):
    doc = pymupdf.open(pdf_path)
    w, h = doc[0].rect.width, doc[0].rect.height
    # página de abertura de cada capítulo, pelo rótulo "CAPÍTULO N"
    starts = {}
    for i, page in enumerate(doc):
        first = page.get_text().strip().split("\n", 1)[0].replace(" ", "")  # rótulo tem letter-spacing
        m = re.fullmatch(r"CAPÍTULO(\d+)", first)
        if m:
            starts.setdefault(f"{int(m.group(1)):02d}", i)
    inserts = []
    for num, stem in PLATES.items():
        img = find_asset(stem)
        if not img:
            missing.append(stem)
        elif num not in starts:
            missing.append(f"abertura do cap. {num}")
        else:
            inserts.append((starts[num], img))
    cover = find_asset("lumi-a-bruxinha-capa")
    if cover:
        inserts.append((0, cover))
    else:
        missing.append("capa")
    for idx, img in sorted(inserts, reverse=True):
        page = doc.new_page(pno=idx, width=w, height=h)
        page.insert_image(page.rect, filename=img, keep_proportion=False)
    tmp = pdf_path + ".tmp"
    doc.save(tmp, garbage=3, deflate=True)
    doc.close()
    os.replace(tmp, pdf_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v1")
    args = ap.parse_args()
    missing = []
    out_html = os.path.join(ROOT, "lumi-a-bruxinha-book.html")
    open(out_html, "w", encoding="utf-8").write(build_html(missing))
    out_pdf = os.path.join(ROOT, f"lumi-a-bruxinha-book-{args.version}.pdf")
    subprocess.run(["node", os.path.join(ROOT, "print_pdf.mjs"), out_html, out_pdf], check=True)
    insert_images(out_pdf, missing)
    print(out_pdf)
    if missing:
        print("PENDENTE:", ", ".join(missing), file=sys.stderr)


if __name__ == "__main__":
    main()
