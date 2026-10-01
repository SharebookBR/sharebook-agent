#!/usr/bin/env python3
"""Gera o HTML do livro a partir de chapters/*.md e imprime o PDF (512x640 pt).

Copiado de `bruxa-por-acaso/` com UMA mudança de mecanismo, explicada em `insert_images`:
o localizador de prancha deixou de depender do rótulo `CAPÍTULO N`.

Capa e ilustrações não passam pelo Chromium: página sem margem no meio do fluxo faz o
Chromium encolher o documento inteiro. Entram depois, via PyMuPDF, como páginas inteiras.

Uso: python3 build_book.py [--version vN]
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
    ROOT, "..", "..", "..", "product-ux", "cover-direction", "assets",
    "sharebook-originals-seal.png"))

HYPH = pyphen.Pyphen(lang="pt_BR", left=3, right=3)
WORD = re.compile(r"[A-Za-zÀ-ÿ]{7,}")

TITULO = "Promessa de Dez Verões"
TITULO_H1 = "Promessa"
TITULO_SPAN = "de Dez Verões"
TAGLINE = "Um pacto de sangue num guardanapo, sete dias para dizer adeus..."

# arquivo de capítulo -> ilustração de página inteira, inserida ANTES da abertura.
# O `05` é o epílogo: ver o comentário em insert_images.
PLATES = {
    "01": "ilus-01-porta-chuva",
    "02": "ilus-02-casa-tempestade",
    "03": "ilus-03-aparador-runas",
    "04": "ilus-05-varanda-escolha",
    "05": "ilus-04-varanda-grimorio",
}
CAPA = "promessa-de-dez-veroes-capa"


def hyphenate(fragment):
    parts = re.split(r"(<[^>]+>)", fragment)
    for i, part in enumerate(parts):
        if not part.startswith("<"):
            parts[i] = WORD.sub(lambda m: HYPH.inserted(m.group(0), hyphen="­"), part)
    return "".join(parts)


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
    seal = (f'<img class="seal" src="file://{SEAL}" alt="Sharebook Originals">'
            if os.path.exists(SEAL) else "")
    if not seal:
        missing.append("selo Sharebook Originals")

    parts = [f"""
<section class="page title-page">
  <h1>{html.escape(TITULO_H1)}<span>{html.escape(TITULO_SPAN)}</span></h1>
  <p class="tagline">{html.escape(TAGLINE)}</p>
  {seal}
</section>
<section class="page imprint">
  <div>
    <p><strong>{html.escape(TITULO)}</strong></p>
    <p>Sharebook Originals · 2026</p>
    <p>Romance paranormal · Conteúdo adulto, recomendado para maiores de 18 anos</p>
    <p class="gap">Esta é uma obra de ficção. Nomes, personagens, lugares e acontecimentos
    são fruto da imaginação ou usados de forma fictícia. Qualquer semelhança com pessoas
    reais — bruxas e ancoradouros incluídos — é mera coincidência.</p>
    <p class="gap">Distribuição gratuita pelo Sharebook — app livre e gratuito para doação
    de livros.<br>sharebook.com.br</p>
  </div>
</section>"""]

    toc, chapters, aberturas = [], [], {}
    for path in sorted(glob.glob(os.path.join(ROOT, "chapters", "*.md"))):
        num = os.path.basename(path)[:2]
        label, name, inner = chapter_html(path)
        aberturas[num] = (label, name)
        toc.append(f'<li><span class="toc-label">{html.escape(label)}</span>'
                   f'{html.escape(name)}</li>')
        label_html = f'<p class="ch-label">{html.escape(label)}</p>' if label else ""
        chapters.append(
            f'<section class="chapter">{label_html}<h2>{html.escape(name)}</h2>{inner}</section>')

    parts.append('<section class="page toc"><h2>Sumário</h2><ol>' + "".join(toc) + "</ol></section>")
    parts.extend(chapters)

    css = open(os.path.join(ROOT, "book.css"), encoding="utf-8").read()
    doc = (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
           f"<title>{html.escape(TITULO)}</title><style>{css}</style></head><body>"
           + "\n".join(parts) + "</body></html>")

    # Anti-padrão da skill: markdown cru no HTML final.
    if "**" in doc:
        missing.append("markdown cru (`**`) sobrou no HTML")
    return doc, aberturas


def _chave(s):
    return re.sub(r"\s+", "", s).upper()


def insert_images(pdf_path, aberturas, missing):
    """Insere capa e pranchas. O localizador NÃO depende do rótulo `CAPÍTULO N`.

    O build original casava a primeira linha da página contra `CAPÍTULO (\\d+)`. Isso
    funciona para capítulo numerado e **falha silenciosamente para o epílogo**, que não tem
    rótulo — a prancha simplesmente não entrava, e o PDF saía sem erro nenhum.

    Aqui a abertura é localizada casando a primeira linha da página contra o rótulo **ou**
    contra o título do capítulo, os dois vindos do próprio `chapters/`. Funciona para
    `CAPÍTULO 4` e para `Epílogo` sem caso especial, e serve a qualquer livro da linha com
    seção sem número (prólogo, interlúdio, posfácio).
    """
    doc = pymupdf.open(pdf_path)
    w, h = doc[0].rect.width, doc[0].rect.height

    candidatos = {}
    for num, (label, name) in aberturas.items():
        for s in (label, name):
            if s:
                candidatos.setdefault(_chave(s), num)

    starts = {}
    for i, page in enumerate(doc):
        txt = page.get_text().strip()
        if not txt:
            continue
        num = candidatos.get(_chave(txt.split("\n", 1)[0]))
        if num:
            starts.setdefault(num, i)

    inserts = []
    for num, stem in PLATES.items():
        img = find_asset(stem)
        if not img:
            missing.append(f"imagem {stem}")
        elif num not in starts:
            missing.append(f"abertura da seção {num} não localizada no PDF")
        else:
            inserts.append((starts[num], img))

    capa = find_asset(CAPA)
    if capa:
        inserts.append((0, capa))
    else:
        missing.append("capa")

    for idx, img in sorted(inserts, reverse=True):
        page = doc.new_page(pno=idx, width=w, height=h)
        # PNG de IA pesa ~2 MB por página; JPEG q85 mantém a qualidade e corta ~90%.
        pix = pymupdf.Pixmap(img)
        if pix.alpha:
            pix = pymupdf.Pixmap(pix, 0)
        page.insert_image(page.rect, stream=pix.tobytes("jpeg", jpg_quality=85),
                          keep_proportion=False)
    tmp = pdf_path + ".tmp"
    doc.save(tmp, garbage=3, deflate=True)
    doc.close()
    os.replace(tmp, pdf_path)
    return len(inserts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v1")
    args = ap.parse_args()
    missing = []

    doc_html, aberturas = build_html(missing)
    out_html = os.path.join(ROOT, "promessa-de-dez-veroes-book.html")
    open(out_html, "w", encoding="utf-8").write(doc_html)

    out_pdf = os.path.join(ROOT, f"promessa-de-dez-veroes-book-{args.version}.pdf")
    subprocess.run(["node", os.path.join(ROOT, "print_pdf.mjs"), out_html, out_pdf], check=True)
    n = insert_images(out_pdf, aberturas, missing)

    print(f"{out_pdf}\n{n} página(s) de imagem inseridas")
    if missing:
        print("PENDENTE:", "; ".join(missing), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
