#!/usr/bin/env python3
"""
Gera um prompt completo de capa a partir da URL de um livro do Sharebook.

Uso:
    python3 cover_prompt_from_url.py "https://www.sharebook.com.br/livros/..."
"""

import argparse
import json
import re
import subprocess
import sys
import urllib.request
from html import unescape
from pathlib import Path


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", "replace")


def clean_text(value: str) -> str:
    value = unescape(value)
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def extract_book_data(html: str) -> dict:
    title = None
    author = None
    synopsis = None

    title_patterns = [
        r'Título:\s*</strong>\s*<br[^>]*>\s*([^<]+)',
        r'Título:([^<\n]+)',
        r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',
        r'<title>([^<]+)</title>',
    ]
    author_patterns = [
        r'Autor:\s*</strong>\s*<br[^>]*>(.*?)</p>',
        r'Autor:\s*</strong>(.*?)</p>',
        r'Autor:([^<\n]+)',
    ]
    synopsis_patterns = [
        r'Sinopse:\s*</[^>]+>\s*(.*?)\s*Livro digital disponível gratuitamente!',
        r'Sinopse:(.*?)Livro digital disponível gratuitamente!',
        r'Sinopse:(.*)',
    ]

    for pattern in title_patterns:
        m = re.search(pattern, html, re.I | re.S)
        if m:
            title = clean_text(m.group(1))
            break

    for pattern in author_patterns:
        m = re.search(pattern, html, re.I | re.S)
        if m:
            names = re.findall(r'<a[^>]*>([^<]+)</a>', m.group(1))
            if names:
                author = ', '.join(clean_text(n) for n in names)
            else:
                author = clean_text(m.group(1))
            break

    for pattern in synopsis_patterns:
        m = re.search(pattern, html, re.I | re.S)
        if m:
            synopsis = clean_text(m.group(1))
            break

    if title and title.lower().startswith('livro digital'):
        title = title.replace('Livro digital', '').strip(' :-')
    if title and title.endswith('| ShareBook'):
        title = title[:-11].strip()

    return {
        'title': title,
        'author': author,
        'synopsis': synopsis,
    }


def run_roulette() -> dict:
    roulette_script = Path(__file__).parent / 'cover_roulette.py'
    out = subprocess.check_output(
        [sys.executable, str(roulette_script)],
        text=True,
    )
    return json.loads(out)


def build_prompt(book: dict, palette: dict) -> str:
    return f"""Me ajuda a criar uma arte de capa no formato 4:5? Não gere a imagem ainda. Primeiro, proponha 3 opções diferentes de conceito para a capa, com abordagens visuais bem distintas entre si, já levando em conta as diretrizes abaixo.

Direção:
- mode: {palette['mode']}

Paleta:
- background: {palette['colors']['background']['name']} ({palette['colors']['background']['hex']})
- primary: {palette['colors']['primary']['name']} ({palette['colors']['primary']['hex']})
- secondary: {palette['colors']['secondary']['name']} ({palette['colors']['secondary']['hex']})
- accent: {palette['colors']['accent']['name']} ({palette['colors']['accent']['hex']})

Livro:
- título: {book['title'] or '[não encontrado]'}
- autor: {book['author'] or '[não encontrado]'}
- sinopse: {book['synopsis'] or '[não encontrada]'}"""


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('url')
    args = parser.parse_args()

    html = fetch_html(args.url)
    book = extract_book_data(html)
    if not book['title']:
        print('Erro: não consegui extrair o título da página.', file=sys.stderr)
        sys.exit(1)

    palette = run_roulette()
    print(build_prompt(book, palette))


if __name__ == '__main__':
    main()
