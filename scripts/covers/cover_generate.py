#!/usr/bin/env python3
"""
Gera capa de livro localmente usando Pillow, sem API externa.
Usa paleta e estilo do cover_roulette.py para consistência.

Uso:
    python3 cover_generate.py "Título do Livro" "Autor" [--paleta Tron] [--estilo terminal]

Se paleta/estilo não forem informados, sorteia automaticamente.
"""

import argparse
import json
import math
import random
import textwrap
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ── Paletas ──────────────────────────────────────────────────────────────
PALETTES = {
    "tron":       {"bg": "#0D1117", "fg": "#00FF41", "accent": "#FFFFFF"},
    "deep-ocean": {"bg": "#0B1D3A", "fg": "#3B82F6", "accent": "#FACC15"},
    "lava":       {"bg": "#1A0A00", "fg": "#FF4500", "accent": "#FFD700"},
    "frost":      {"bg": "#0F172A", "fg": "#38BDF8", "accent": "#E2E8F0"},
    "matrix":     {"bg": "#0A0A0A", "fg": "#00FF88", "accent": "#BBFFBB"},
    "sunset":     {"bg": "#1A0A2E", "fg": "#E94560", "accent": "#FFD700"},
    "graphite":   {"bg": "#1E1E1E", "fg": "#A0A0A0", "accent": "#FFFFFF"},
    "cyber":      {"bg": "#120458", "fg": "#FF6B6B", "accent": "#00D2FF"},
    "forest":     {"bg": "#0D2818", "fg": "#4ADE80", "accent": "#FBBF24"},
    "platinum":   {"bg": "#1A1A2E", "fg": "#E2E8F0", "accent": "#F59E0B"},
}

# ── Font paths (tentar fonts comuns do sistema) ─────────────────────────
FONT_BOLD_MAP = [
    ("Arial", "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"),
    ("Calibri", "C:/Windows/Fonts/calibrib.ttf", "C:/Windows/Fonts/calibri.ttf"),
    ("Georgia", "C:/Windows/Fonts/georgiab.ttf", "C:/Windows/Fonts/georgia.ttf"),
    ("Consolas", "C:/Windows/Fonts/consolab.ttf", "C:/Windows/Fonts/consola.ttf"),
    # (nome, bold_path, regular_path)
    ("Cantarell",
     "/usr/share/fonts/opentype/cantarell/Cantarell-ExtraBold.otf",
     "/usr/share/fonts/opentype/cantarell/Cantarell-Regular.otf"),
    ("Dosis",
     "/usr/share/fonts/opentype/dosis/Dosis-Bold.otf",
     "/usr/share/fonts/opentype/dosis/Dosis-Book.otf"),
    ("Cabin",
     "/usr/share/fonts/opentype/cabin/Cabin-Bold.otf",
     "/usr/share/fonts/opentype/cabin/Cabin-Regular.otf"),
    ("EB Garamond",
     "/usr/share/fonts/opentype/ebgaramond/EBGaramond12-Bold.otf",
     "/usr/share/fonts/opentype/ebgaramond/EBGaramond12-Regular.otf"),
    ("Roboto",
     "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Bold.ttf",
     "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Regular.ttf"),
    ("DejaVu Serif",
     "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
    ("Liberation Sans",
     "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
     "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),

    # ── Ousadas ───────────────────────────────────────────────────────
    ("KaushanScript",
     "/usr/share/fonts/opentype/kaushanscript/KaushanScript-Regular.otf",
     "/usr/share/fonts/opentype/kaushanscript/KaushanScript-Regular.otf"),
    ("CabinSketch",
     "/usr/share/fonts/truetype/cabinsketch/CabinSketch-Bold.ttf",
     "/usr/share/fonts/truetype/cabinsketch/CabinSketch-Regular.ttf"),
    ("Humor Sans",
     "/usr/share/fonts/truetype/humor-sans/Humor-Sans.ttf",
     "/usr/share/fonts/truetype/humor-sans/Humor-Sans.ttf"),
]


def pick_font_pair() -> tuple:
    """Retorna (nome, bold_font, regular_font) sorteado."""
    available = [
        entry for entry in FONT_BOLD_MAP
        if Path(entry[1]).exists() and Path(entry[2]).exists()
    ]
    if not available:
        raise FileNotFoundError("Nenhum par de fontes compatível foi encontrado no sistema")
    entry = random.choice(available)
    name, bold_path, regular_path = entry
    return name, bold_path, regular_path


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def find_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    p = Path(path)
    if p.exists():
        return ImageFont.truetype(str(p), size)
    raise FileNotFoundError(f"Fonte não encontrada: {path}")


def lerp_color(c1: tuple, c2: tuple, t: float) -> tuple:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_gradient(draw: ImageDraw, size: tuple, color1: tuple, color2: tuple,
                  direction: str = "vertical") -> None:
    """Desenha gradiente no fundo."""
    w, h = size
    for i in range(max(w, h) if direction == "vertical" else w):
        t = i / (h if direction == "vertical" else w)
        color = lerp_color(color1, color2, t)
        if direction == "vertical":
            draw.line([(0, i), (w, i)], fill=color, width=1)
        else:
            draw.line([(i, 0), (i, h)], fill=color, width=1)


def draw_decorative_element(draw: ImageDraw, W: int, H: int, bg_rgb: tuple, palette_name: str) -> None:
    """Desenha elemento geométrico grande, metade fora da capa, cor próxima ao fundo."""
    # Cor derivada do bg: mais clara mas próximo o suficiente pra não competir com o texto
    element_color = tuple(min(255, c + 40) for c in bg_rgb)
    # Sorteia posição (canto) baseado no nome da paleta
    corners = ["top-right", "bottom-left", "top-left", "bottom-right"]
    corner = corners[hash(palette_name) % 4]
    size = 400  # Grande, metade vai aparecer

    if corner == "top-right":
        cx, cy = W, 0
    elif corner == "bottom-left":
        cx, cy = 0, H
    elif corner == "top-left":
        cx, cy = 0, 0
    else:
        cx, cy = W, H

    elem_type = hash(palette_name + "_type") % 3

    if elem_type == 0:
        # Círculo gigante
        draw.ellipse([cx - size, cy - size, cx + size, cy + size],
                     fill=element_color + (60,), outline=None)
        # Anel interno sutil
        draw.ellipse([cx - size//2, cy - size//2, cx + size//2, cy + size//2],
                     outline=element_color + (40,), width=2)
    elif elem_type == 1:
        # Triângulo gigante
        points = [(cx, cy), (cx + size, cy - size), (cx + size, cy + size)]
        if cx > W // 2:
            points = [(cx, cy), (cx - size, cy - size), (cx - size, cy + size)]
        if cy > H // 2:
            points = [(p[0], p[1] - 2*size) if p == points[0] else (p[0], p[1] - size) for p in points]
        draw.polygon(points, fill=element_color + (50,), outline=None)
    else:
        # Quadrado rotacionado (losango)
        offset = size // 2
        points = [(cx, cy - offset), (cx + offset, cy),
                  (cx, cy + offset), (cx - offset, cy)]
        draw.polygon(points, fill=element_color + (55,), outline=None)


def generate_cover(title: str, author: str, palette_name: str | None = None,
                   output_path: str = "cover.png", text_effect: str | None = None) -> dict:
    """Gera capa 600x900 e salva como JPEG."""

    # Sortear paleta se não especificada
    if not palette_name or palette_name.lower() not in PALETTES:
        palette_name = random.choice(list(PALETTES.keys()))
    palette = PALETTES[palette_name.lower()]

    bg_rgb = hex_to_rgb(palette["bg"])
    fg_rgb = hex_to_rgb(palette["fg"])
    accent_rgb = hex_to_rgb(palette["accent"])

    W, H = 600, 900
    img = Image.new("RGB", (W, H), bg_rgb)
    draw = ImageDraw.Draw(img)

    # ── Fundo: gradiente com direção aleatória (bem visível) ────────────
    grad_directions = ["vertical", "horizontal", "diagonal"]
    grad_dir = random.choice(grad_directions)
    # Escurecer/clarear mais pra gradiente ser visível
    lighter = tuple(min(255, c + 60) for c in bg_rgb)
    darker = tuple(max(0, c - 60) for c in bg_rgb)
    if grad_dir == "vertical":
        draw_gradient(draw, (W, H), darker, bg_rgb, "vertical")
    elif grad_dir == "horizontal":
        draw_gradient(draw, (W, H), darker, bg_rgb, "horizontal")
    else:  # diagonal — gradiente manual
        for y in range(H):
            t = y / H
            for x in range(W):
                t2 = x / W
                mix = (t + t2) / 2
                color = lerp_color(darker, lighter, mix)
                draw.point((x, y), fill=color)

    # ── Elemento geométrico por paleta (nunca repete) ────────────────────
    draw_decorative_element(draw, W, H, bg_rgb, palette_name.lower())

    # ── Sortear fonte ────────────────────────────────────────────────────
    font_name, font_bold_path, font_regular_path = pick_font_pair()

    # ── Título ───────────────────────────────────────────────────────────
    # Achar fontes
    font_bold = find_font(font_bold_path, 42)
    font_author = find_font(font_regular_path, 28)
    font_light = find_font(font_regular_path, 20)

    # Quebrar título em até 3 linhas
    words = title.split()
    lines = []
    current_line = ""
    for word in words:
        test = current_line + (" " if current_line else "") + word
        bbox = draw.textbbox((0, 0), test, font=font_bold)
        if bbox[2] - bbox[0] < W - 100:
            current_line = test
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    # Ajustar tamanho da fonte se muitas linhas
    font_size = 42
    if len(lines) > 2:
        font_size = 36
    elif len(lines) > 3:
        font_size = 30
    font_bold = find_font(font_bold_path, font_size)

    # Sortear layout (1-4) baseado no hash do título pra ser determinístico
    layout_id = (hash(title) % 4) + 1 if title else 1

    line_height = font_size + 8
    total_text_height = len(lines) * line_height
    author_bbox = draw.textbbox((0, 0), author, font=font_author) if author else (0, 0, 0, 0)
    author_tw = author_bbox[2] - author_bbox[0]

    # Título SEMPRE acima do autor. Todos os layouts respeitam isso.

    # Sorteio de efeito especial (ou usa o passado)
    text_effects = ["glow", "outline", "shadow", "glow+outline"]
    if text_effect is None:
        text_effect = random.choice(text_effects)

    def render_text(font, texto, x, y, fill_color):
        # Sombra base (sempre)
        draw.text((x + 2, y + 2), texto, fill=(0, 0, 0, 120), font=font)
        if text_effect == "glow":
            # Glow branco com alpha pra destacar do fundo escuro
            for dx, dy, alpha in [(-2, 0, 60), (2, 0, 60), (0, -2, 60), (0, 2, 60),
                                   (-3, -3, 35), (3, -3, 35), (-3, 3, 35), (3, 3, 35)]:
                draw.text((x + dx, y + dy), texto, fill=(255, 255, 255, alpha), font=font)
            draw.text((x, y), texto, fill=fill_color, font=font)
        elif text_effect == "outline":
            for dx, dy in [(-2,-2),(2,-2),(-2,2),(2,2),(0,-2),(0,2),(-2,0),(2,0)]:
                draw.text((x+dx, y+dy), texto, fill=(0, 0, 0, 180), font=font)
            draw.text((x, y), texto, fill=fill_color, font=font)
        elif text_effect == "shadow":
            draw.text((x, y), texto, fill=fill_color, font=font)
        elif text_effect == "glow+outline":
            # Outline preto + glow branco por cima
            for dx, dy in [(-2,-2),(2,-2),(-2,2),(2,2),(0,-2),(0,2),(-2,0),(2,0)]:
                draw.text((x+dx, y+dy), texto, fill=(0,0,0,180), font=font)
            for dx, dy, alpha in [(-2,0,60),(2,0,60),(0,-2,60),(0,2,60)]:
                draw.text((x+dx, y+dy), texto, fill=(255,255,255,alpha), font=font)
            draw.text((x, y), texto, fill=fill_color, font=font)

    def draw_title_at(start_y, align="center", margin=60):
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font_bold)
            tw = bbox[2] - bbox[0]
            if align == "center":
                x = (W - tw) // 2
            else:
                x = margin
            y = start_y + i * line_height
            render_text(font_bold, line, x, y, fg_rgb)

    def draw_author_at(y, align="center", margin=60):
        if not author:
            return
        # Quebrar autor em linhas se for longo demais
        max_author_chars = 30
        author_lines = textwrap.wrap(author, width=max_author_chars) if len(author) > max_author_chars else [author]
        for i, line in enumerate(author_lines):
            bbox = draw.textbbox((0, 0), line, font=font_author)
            tw = bbox[2] - bbox[0]
            if align == "center":
                x = (W - tw) // 2
            else:
                x = margin
            render_text(font_author, line, x, y + i * 28, accent_rgb)

    def draw_bar_at(y, width=80):
        draw.rectangle([(W // 2 - width // 2, y), (W // 2 + width // 2, y + 3)], fill=accent_rgb)

    title_center_y = H * 3 // 10

    if layout_id == 1:
        # Clássico: título no centro-superior, barra, autor abaixo
        start_y = title_center_y - total_text_height // 2
        draw_title_at(start_y, "center")
        bar_y = start_y + len(lines) * line_height + 20
        draw_bar_at(bar_y)
        draw_author_at(bar_y + 35, "center")

    elif layout_id == 2:
        # Título mais ao centro, autor mais abaixo, barra entre eles
        start_y = H * 2 // 5 - total_text_height // 2
        draw_title_at(start_y, "center")
        bar_y = start_y + len(lines) * line_height + 25
        draw_bar_at(bar_y, 60)
        draw_author_at(bar_y + 40, "center")

    elif layout_id == 3:
        # Título alinhado à esquerda, autor abaixo à esquerda
        margin = 60
        start_y = H * 2 // 5 - total_text_height // 2
        draw_title_at(start_y, "left", margin)
        bar_y = start_y + len(lines) * line_height + 20
        draw.rectangle([(margin, bar_y), (margin + 50, bar_y + 3)], fill=accent_rgb)
        draw_author_at(bar_y + 35, "left", margin)

    elif layout_id == 4:
        # Título centralizado no terço médio-superior, autor centralizado abaixo
        start_y = H * 3 // 10 - total_text_height // 2
        draw_title_at(start_y, "center")
        bar_y = start_y + len(lines) * line_height + 20
        draw_bar_at(bar_y)
        draw_author_at(bar_y + 35, "center")

    # ── Salvar ───────────────────────────────────────────────────────────
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output, "JPEG", quality=92)

    return {
        "palette": palette_name.lower(),
        "bg": palette["bg"],
        "fg": palette["fg"],
        "accent": palette["accent"],
        "output": str(output),
        "width": W,
        "height": H,
    }


def main():
    parser = argparse.ArgumentParser(description="Gera capa de livro localmente (Pillow)")
    parser.add_argument("title", help="Título do livro")
    parser.add_argument("author", nargs="?", default="", help="Autor do livro")
    parser.add_argument("--paleta", "-p", choices=list(PALETTES.keys()),
                        help="Nome da paleta (opcional, sorteia se omitido)")
    parser.add_argument("--output", "-o", default="cover.jpg", help="Arquivo de saída")
    parser.add_argument("--efeito", choices=["glow","outline","shadow","glow+outline"],
                        help="Efeito de texto (sorteia se omitido)")
    parser.add_argument("--json", action="store_true", help="Saída JSON")
    args = parser.parse_args()

    result = generate_cover(args.title, args.author, args.paleta, args.output, args.efeito)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"🎨 Capa gerada: {result['output']}")
        print(f"   Paleta: {result['palette']}")
        print(f"   Tamanho: {result['width']}x{result['height']}")
        print(f"   Cores: bg={result['bg']} fg={result['fg']} accent={result['accent']}")


if __name__ == "__main__":
    main()
