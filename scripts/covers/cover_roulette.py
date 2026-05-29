#!/usr/bin/env python3
"""
Roleta de direção visual para capas de livros.

Objetivo:
- aumentar a diversidade real do catálogo
- sortear cor principal com personalidade
- escolher cor secundária por afinidade
- fixar uma cor neutra de apoio
- sortear um modo conceitual: bom vs ruim_bom
- entregar direção visual, não prompt engessado

Uso:
    python3 cover_roulette.py
    python3 cover_roulette.py --pretty
"""

import argparse
import json
import random

MAIN_COLORS = [
    {
        "name": "verde total",
        "hex": "#16A34A",
        "family": "ousado_chapado",
        "affinities": ["rosa chiclete", "amarelo gema", "creme editorial", "preto absoluto", "azul royal"],
    },
    {
        "name": "azul elétrico",
        "hex": "#2563EB",
        "family": "tech_vivo",
        "affinities": ["laranja cartaz", "amarelo gema", "branco duro", "rosa chiclete", "grafite"],
    },
    {
        "name": "vermelho cartaz",
        "hex": "#DC2626",
        "family": "poster",
        "affinities": ["ciano vivo", "creme editorial", "preto absoluto", "rosa pálido"],
    },
    {
        "name": "roxo sintético",
        "hex": "#7C3AED",
        "family": "estranho_bom",
        "affinities": ["amarelo gema", "verde ácido", "branco duro", "rosa chiclete"],
    },
    {
        "name": "amarelo total",
        "hex": "#FACC15",
        "family": "ousado_chapado",
        "affinities": ["azul royal", "preto absoluto", "vermelho cartaz", "grafite"],
    },
    {
        "name": "laranja brutal",
        "hex": "#EA580C",
        "family": "poster",
        "affinities": ["azul royal", "creme editorial", "preto absoluto", "rosa pálido"],
    },
    {
        "name": "rosa chiclete",
        "hex": "#EC4899",
        "family": "cafona_charmoso",
        "affinities": ["verde total", "preto absoluto", "creme editorial", "azul royal"],
    },
    {
        "name": "ciano vivo",
        "hex": "#06B6D4",
        "family": "tech_vivo",
        "affinities": ["vermelho cartaz", "grafite", "branco duro", "amarelo gema"],
    },
    {
        "name": "verde ácido",
        "hex": "#84CC16",
        "family": "estranho_bom",
        "affinities": ["roxo sintético", "preto absoluto", "rosa chiclete", "grafite"],
    },
    {
        "name": "bordô seco",
        "hex": "#7F1D1D",
        "family": "editorial_sobrio",
        "affinities": ["creme editorial", "ouro sujo", "rosa pálido", "grafite"],
    },
]

SECONDARY_COLORS = {
    "rosa chiclete": "#EC4899",
    "amarelo gema": "#F59E0B",
    "creme editorial": "#F5E9D4",
    "preto absoluto": "#111111",
    "azul royal": "#1D4ED8",
    "laranja cartaz": "#F97316",
    "branco duro": "#FFFFFF",
    "grafite": "#374151",
    "ciano vivo": "#06B6D4",
    "rosa pálido": "#F9A8D4",
    "ouro sujo": "#C08A00",
    "verde ácido": "#84CC16",
}

NEUTRALS = [
    {"name": "branco duro", "hex": "#FFFFFF"},
    {"name": "preto absoluto", "hex": "#111111"},
    {"name": "creme editorial", "hex": "#F5E9D4"},
    {"name": "grafite", "hex": "#374151"},
]

STYLE_BUCKETS = {
    "bom": [
        {"name": "tipografia brutalista", "direction": "tipografia enorme, composição seca, impacto editorial"},
        {"name": "blueprint técnico", "direction": "grade fina, linhas técnicas, sensação de manual de engenharia"},
        {"name": "poster geométrico", "direction": "formas geométricas grandes, composição limpa e decidida"},
        {"name": "faixa editorial", "direction": "grande faixa estrutural, hierarquia tipográfica clara, cara de livro sério"},
        {"name": "diagonal cartaz", "direction": "corte diagonal forte, sensação de movimento e energia"},
        {"name": "grid modernista", "direction": "alinhamento rígido, respiro, composição de revista de design"},
        {"name": "circuito elegante", "direction": "linhas e nós discretos, tecnologia sem exagero neon"},
    ],
    "ruim_bom": [
        {"name": "apostila premium duvidosa", "direction": "conceito de apostila corporativa meio brega, mas acabamento impecável"},
        {"name": "flyer de curso de informática 2004", "direction": "energia de panfleto antigo de tecnologia, porém super bem resolvido"},
        {"name": "cd-rom educacional charmoso", "direction": "estética de software educativo antigo com execução elegante"},
        {"name": "manual técnico cafona adorável", "direction": "visual meio errado de manual técnico, mas irresistível e memorável"},
        {"name": "powerpoint impecável", "direction": "cara de slide corporativo ousado, com composição surpreendentemente bonita"},
        {"name": "folder de evento tech estranho", "direction": "conceito de evento de tecnologia meio datado, final adorável"},
    ],
}


def pick_direction():
    mode = random.choice(["bom", "ruim_bom"])
    main = random.choice(MAIN_COLORS)
    secondary_name = random.choice(main["affinities"])
    neutral = random.choice(NEUTRALS)
    style = random.choice(STYLE_BUCKETS[mode])

    return {
        "mode": mode,
        "palette": {
            "main": {
                "name": main["name"],
                "hex": main["hex"],
                "family": main["family"],
            },
            "secondary": {
                "name": secondary_name,
                "hex": SECONDARY_COLORS[secondary_name],
            },
            "neutral": neutral,
        },
        "style": style,
        "notes": [
            "usar a cor principal com coragem real",
            "a secundária deve criar tensão ou charme, não só combinar",
            "a neutra existe para segurar legibilidade e composição",
            "não deixar a IA cair no default tech-clean genérico",
        ],
    }


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--pretty", action="store_true", help="saída legível")
    args = parser.parse_args()

    result = pick_direction()

    if args.pretty:
        print(f"🎲 Modo: {result['mode']}")
        print(f"🎨 Principal: {result['palette']['main']['name']} ({result['palette']['main']['hex']})")
        print(f"   Família: {result['palette']['main']['family']}")
        print(f"🎨 Secundária: {result['palette']['secondary']['name']} ({result['palette']['secondary']['hex']})")
        print(f"🎨 Neutra: {result['palette']['neutral']['name']} ({result['palette']['neutral']['hex']})")
        print(f"🖼️  Estilo: {result['style']['name']}")
        print(f"   Direção: {result['style']['direction']}")
        print("\n📌 Notas:")
        for note in result['notes']:
            print(f"- {note}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
