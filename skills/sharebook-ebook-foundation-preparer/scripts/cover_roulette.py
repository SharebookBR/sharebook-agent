#!/usr/bin/env python3
"""
Sorteio de paleta + estilo para capas de livros da ebook_foundation.
Cada chamada gera uma combinação aleatória que alimenta o prompt de geração de imagem.

Uso:
    python3 cover_roulette.py                    # output JSON
    python3 cover_roulette.py --pretty           # output legível

Saída: JSON com paleta e estilo sorteados + prompt base para o gerador de imagem.
"""

import random
import json
import sys

# ── Paletas ──────────────────────────────────────────────────────────────
# Cada entrada: (nome, bg_hex, fg_hex, accent_hex)
PALETTES = [
    ("Tron",          "#0D1117", "#00FF41", "#FFFFFF"),
    ("Deep Ocean",    "#0B1D3A", "#3B82F6", "#FACC15"),
    ("Lava",          "#1A0A00", "#FF4500", "#FFD700"),
    ("Frost",         "#0F172A", "#38BDF8", "#E2E8F0"),
    ("Matrix",        "#0A0A0A", "#00FF88", "#BBFFBB"),
    ("Sunset",        "#1A0A2E", "#E94560", "#FFD700"),
    ("Graphite",      "#1E1E1E", "#A0A0A0", "#FFFFFF"),
    ("Cyber",         "#120458", "#FF6B6B", "#00D2FF"),
    ("Forest",        "#0D2818", "#4ADE80", "#FBBF24"),
    ("Platinum",      "#1A1A2E", "#E2E8F0", "#F59E0B"),
]

# ── Estilos ──────────────────────────────────────────────────────────────
# Cada entrada: (nome, descrição_prompt)
STYLES = [
    ("terminal",
     "terminal screen with green-on-black monospace text, glowing cursor, dark background, command-line aesthetic, retro-futuristic vibe"),
    ("block",
     "large solid color block on lower half, title in bold sans-serif above, minimal and clean, editorial design"),
    ("geometric",
     "overlapping geometric shapes (triangles, circles) in contrasting colors, modern tech feel, abstract composition"),
    ("grid",
     "subtle grid pattern background, title in bold monospace, small accent line, blueprint aesthetic"),
    ("typography",
     "big bold typography as the main visual element, no imagery, clean sans-serif, high contrast, magazine-style"),
    ("diagonal",
     "diagonal color split background, title on the lighter side, accent stripe, dynamic and bold"),
    ("circuit",
     "abstract circuit board / node lines pattern, tech vibe, glowing accent details, dark base"),
    ("gradient",
     "smooth gradient from dark to accent color, title centered, subtle light particles, modern digital product feel"),
]

def pick():
    pal = random.choice(PALETTES)
    sty = random.choice(STYLES)
    return {
        "palette": {
            "name": pal[0],
            "bg": pal[1],
            "fg": pal[2],
            "accent": pal[3],
        },
        "style": {
            "name": sty[0],
            "prompt_description": sty[1],
        },
    }

def build_prompt(result, title="", author=""):
    """Monta o prompt final para o gerador de imagem."""
    p = result["palette"]
    s = result["style"]
    return (
        f"Book cover design, 2:3 ratio, {s['prompt_description']}. "
        f"Color palette: background {p['bg']}, "
        f"primary text {p['fg']}, "
        f"accent {p['accent']}. "
        f"Title: '{title}' in bold prominent text. "
        f"Author: '{author}' in smaller text. "
        f"No illustration, no photo, keep it clean and professional."
    )

if __name__ == "__main__":
    title = sys.argv[1] if len(sys.argv) > 1 else ""
    author = sys.argv[2] if len(sys.argv) > 2 else ""

    result = pick()
    result["image_prompt"] = build_prompt(result, title, author)

    if "--pretty" in sys.argv:
        print(f"🎨 Paleta: {result['palette']['name']}")
        print(f"   BG: {result['palette']['bg']}")
        print(f"   FG: {result['palette']['fg']}")
        print(f"   Accent: {result['palette']['accent']}")
        print(f"🖼️  Estilo: {result['style']['name']}")
        print(f"   {result['style']['prompt_description']}")
        print(f"\n📝 Prompt:\n{result['image_prompt']}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
