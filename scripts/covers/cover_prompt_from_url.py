#!/usr/bin/env python3
"""
Gera um prompt completo de capa a partir da URL de um livro do Sharebook.

Uso:
    python3 cover_prompt_from_url.py "https://www.sharebook.com.br/livros/..."
    python3 cover_prompt_from_url.py "https://..." --avoid-style serigrafia-editorial
    python3 cover_prompt_from_url.py "https://..." --avoid-group impresso-colagem
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


def run_roulette(
    style_count: int = 3,
    avoid_styles: list[str] | None = None,
    avoid_groups: list[str] | None = None,
    seed: int | None = None,
) -> dict:
    roulette_script = Path(__file__).parent / 'cover_roulette.py'
    command = [
        sys.executable,
        str(roulette_script),
        '--styles',
        str(style_count),
    ]
    for style_id in avoid_styles or []:
        command.extend(['--avoid-style', style_id])
    for group_id in avoid_groups or []:
        command.extend(['--avoid-group', group_id])
    if seed is not None:
        command.extend(['--seed', str(seed)])

    out = subprocess.check_output(
        command,
        text=True,
        encoding='utf-8',
    )
    return json.loads(out)


def format_styles(direction: dict) -> str:
    blocks = []
    for index, style in enumerate(direction['styles'], start=1):
        blocks.append(
            f"""Conceito {index} — {style['name']} (`{style['id']}`)
- macrogrupo: {style['group']}
- meio: {style['medium']}
- materialidade: {style['materiality']}
- iluminação: {style['lighting']}
- profundidade: {style['depth']}
- sujeito: {style['subject']}
- comportamento cromático: {style['palette_behavior']}
- direção: {style['guidance']}
- evitar: {style['avoid']}"""
        )
    return '\n\n'.join(blocks)


def build_prompt(book: dict, direction: dict) -> str:
    return f"""Me ajuda a criar uma arte de capa no formato 4:5? Não gere a imagem ainda. Primeiro, proponha {len(direction['styles'])} opções diferentes de conceito, usando exatamente uma família visual sorteada por opção.

Direção geral:
- mode: {direction['mode']}
- tratamento: {direction['mode_guidance']}

Paleta-base — {direction['palette']}:
- background: {direction['colors']['background']['name']} ({direction['colors']['background']['hex']})
- primary: {direction['colors']['primary']['name']} ({direction['colors']['primary']['hex']})
- secondary: {direction['colors']['secondary']['name']} ({direction['colors']['secondary']['hex']})
- accent: {direction['colors']['accent']['name']} ({direction['colors']['accent']['hex']})

Famílias visuais sorteadas:

{format_styles(direction)}

Livro:
- título: {book['title'] or '[não encontrado]'}
- autor: {book['author'] or '[não encontrado]'}
- sinopse: {book['synopsis'] or '[não encontrada]'}

Regras:
- criar um conceito estruturalmente distinto para cada família; os macrogrupos já são distintos
- não misturar as famílias
- tratar as quatro cores como âncoras, seguindo o comportamento cromático de cada conceito
- preservar literalmente título e autoria
- evitar repetição gratuita de estilos vistos nas capas recentes
- não cair no default tech-clean genérico"""


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('url')
    parser.add_argument(
        '--avoid-style',
        action='append',
        default=[],
        help='família visual recente a excluir; pode repetir a opção',
    )
    parser.add_argument(
        '--avoid-group',
        action='append',
        default=[],
        help='macrogrupo visual recente a excluir; pode repetir a opção',
    )
    parser.add_argument('--styles', type=int, default=3)
    parser.add_argument('--seed', type=int)
    args = parser.parse_args()

    html = fetch_html(args.url)
    book = extract_book_data(html)
    if not book['title']:
        print('Erro: não consegui extrair o título da página.', file=sys.stderr)
        sys.exit(1)

    direction = run_roulette(
        style_count=args.styles,
        avoid_styles=args.avoid_style,
        avoid_groups=args.avoid_group,
        seed=args.seed,
    )
    print(build_prompt(book, direction))


if __name__ == '__main__':
    main()
