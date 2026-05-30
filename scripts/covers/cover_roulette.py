#!/usr/bin/env python3
"""
Roleta de direção visual para capas de livros.

Objetivo:
- aumentar a diversidade real do catálogo
- sortear a partir de paletas-mãe coerentes
- distribuir background, primary, secondary e accent sem perder harmonia
- sortear um modo conceitual: bom vs ruim_bom
- entregar direção visual, não prompt engessado
"""

import argparse
import json
import random

PALETTES = [
    {
        "name": "verde pop",
        "colors": {
            "verde total": "#16A34A",
            "rosa chiclete": "#EC4899",
            "preto absoluto": "#111111",
            "creme editorial": "#F5E9D4",
        },
        "schemes": [
            {"background": "verde total", "primary": "preto absoluto", "secondary": "creme editorial", "accent": "rosa chiclete"},
            {"background": "preto absoluto", "primary": "verde total", "secondary": "creme editorial", "accent": "rosa chiclete"},
            {"background": "creme editorial", "primary": "verde total", "secondary": "preto absoluto", "accent": "rosa chiclete"},
            {"background": "rosa chiclete", "primary": "preto absoluto", "secondary": "creme editorial", "accent": "verde total"},
        ],
    },
    {
        "name": "poster soviético tropical",
        "colors": {
            "vermelho cartaz": "#DC2626",
            "ciano vivo": "#06B6D4",
            "creme editorial": "#F5E9D4",
            "preto absoluto": "#111111",
        },
        "schemes": [
            {"background": "vermelho cartaz", "primary": "creme editorial", "secondary": "preto absoluto", "accent": "ciano vivo"},
            {"background": "creme editorial", "primary": "vermelho cartaz", "secondary": "preto absoluto", "accent": "ciano vivo"},
            {"background": "preto absoluto", "primary": "vermelho cartaz", "secondary": "creme editorial", "accent": "ciano vivo"},
            {"background": "ciano vivo", "primary": "preto absoluto", "secondary": "creme editorial", "accent": "vermelho cartaz"},
        ],
    },
    {
        "name": "roxo sintético",
        "colors": {
            "roxo sintético": "#7C3AED",
            "amarelo gema": "#F59E0B",
            "grafite": "#374151",
            "rosa pálido": "#F9A8D4",
        },
        "schemes": [
            {"background": "roxo sintético", "primary": "amarelo gema", "secondary": "grafite", "accent": "rosa pálido"},
            {"background": "grafite", "primary": "roxo sintético", "secondary": "amarelo gema", "accent": "rosa pálido"},
            {"background": "amarelo gema", "primary": "roxo sintético", "secondary": "grafite", "accent": "rosa pálido"},
            {"background": "rosa pálido", "primary": "grafite", "secondary": "roxo sintético", "accent": "amarelo gema"},
        ],
    },
    {
        "name": "manual industrial",
        "colors": {
            "azul royal": "#1D4ED8",
            "amarelo total": "#FACC15",
            "grafite": "#374151",
            "branco duro": "#FFFFFF",
        },
        "schemes": [
            {"background": "azul royal", "primary": "branco duro", "secondary": "amarelo total", "accent": "grafite"},
            {"background": "branco duro", "primary": "azul royal", "secondary": "grafite", "accent": "amarelo total"},
            {"background": "grafite", "primary": "amarelo total", "secondary": "branco duro", "accent": "azul royal"},
            {"background": "amarelo total", "primary": "grafite", "secondary": "azul royal", "accent": "branco duro"},
        ],
    },
    {
        "name": "laranja editorial",
        "colors": {
            "laranja brutal": "#EA580C",
            "azul royal": "#1D4ED8",
            "creme editorial": "#F5E9D4",
            "bordô seco": "#7F1D1D",
        },
        "schemes": [
            {"background": "laranja brutal", "primary": "creme editorial", "secondary": "bordô seco", "accent": "azul royal"},
            {"background": "creme editorial", "primary": "laranja brutal", "secondary": "azul royal", "accent": "bordô seco"},
            {"background": "azul royal", "primary": "creme editorial", "secondary": "laranja brutal", "accent": "bordô seco"},
            {"background": "bordô seco", "primary": "creme editorial", "secondary": "laranja brutal", "accent": "azul royal"},
        ],
    },
    {
        "name": "tech limão",
        "colors": {
            "verde ácido": "#84CC16",
            "roxo sintético": "#7C3AED",
            "preto absoluto": "#111111",
            "branco duro": "#FFFFFF",
        },
        "schemes": [
            {"background": "verde ácido", "primary": "preto absoluto", "secondary": "branco duro", "accent": "roxo sintético"},
            {"background": "preto absoluto", "primary": "verde ácido", "secondary": "branco duro", "accent": "roxo sintético"},
            {"background": "branco duro", "primary": "verde ácido", "secondary": "preto absoluto", "accent": "roxo sintético"},
            {"background": "roxo sintético", "primary": "branco duro", "secondary": "preto absoluto", "accent": "verde ácido"},
        ],
    },
    {
        "name": "oceano premium",
        "colors": {
            "azul elétrico": "#2563EB",
            "laranja cartaz": "#F97316",
            "branco duro": "#FFFFFF",
            "grafite": "#374151",
        },
        "schemes": [
            {"background": "azul elétrico", "primary": "branco duro", "secondary": "grafite", "accent": "laranja cartaz"},
            {"background": "branco duro", "primary": "azul elétrico", "secondary": "grafite", "accent": "laranja cartaz"},
            {"background": "grafite", "primary": "azul elétrico", "secondary": "branco duro", "accent": "laranja cartaz"},
            {"background": "laranja cartaz", "primary": "grafite", "secondary": "branco duro", "accent": "azul elétrico"},
        ],
    },
    {
        "name": "vinho de revista",
        "colors": {
            "bordô seco": "#7F1D1D",
            "rosa pálido": "#F9A8D4",
            "creme editorial": "#F5E9D4",
            "grafite": "#374151",
        },
        "schemes": [
            {"background": "bordô seco", "primary": "creme editorial", "secondary": "rosa pálido", "accent": "grafite"},
            {"background": "creme editorial", "primary": "bordô seco", "secondary": "grafite", "accent": "rosa pálido"},
            {"background": "grafite", "primary": "rosa pálido", "secondary": "creme editorial", "accent": "bordô seco"},
            {"background": "rosa pálido", "primary": "bordô seco", "secondary": "creme editorial", "accent": "grafite"},
        ],
    },
    {
        "name": "amarelo manifesto",
        "colors": {
            "amarelo total": "#FACC15",
            "vermelho cartaz": "#DC2626",
            "preto absoluto": "#111111",
            "creme editorial": "#F5E9D4",
        },
        "schemes": [
            {"background": "amarelo total", "primary": "preto absoluto", "secondary": "vermelho cartaz", "accent": "creme editorial"},
            {"background": "preto absoluto", "primary": "amarelo total", "secondary": "creme editorial", "accent": "vermelho cartaz"},
            {"background": "creme editorial", "primary": "vermelho cartaz", "secondary": "preto absoluto", "accent": "amarelo total"},
            {"background": "vermelho cartaz", "primary": "creme editorial", "secondary": "preto absoluto", "accent": "amarelo total"},
        ],
    },
    {
        "name": "ciano laboratório",
        "colors": {
            "ciano vivo": "#06B6D4",
            "azul royal": "#1D4ED8",
            "branco duro": "#FFFFFF",
            "preto absoluto": "#111111",
        },
        "schemes": [
            {"background": "ciano vivo", "primary": "preto absoluto", "secondary": "branco duro", "accent": "azul royal"},
            {"background": "azul royal", "primary": "branco duro", "secondary": "ciano vivo", "accent": "preto absoluto"},
            {"background": "branco duro", "primary": "azul royal", "secondary": "preto absoluto", "accent": "ciano vivo"},
            {"background": "preto absoluto", "primary": "ciano vivo", "secondary": "branco duro", "accent": "azul royal"},
        ],
    },
    {
        "name": "rosa terminal",
        "colors": {
            "rosa chiclete": "#EC4899",
            "azul elétrico": "#2563EB",
            "preto absoluto": "#111111",
            "branco duro": "#FFFFFF",
        },
        "schemes": [
            {"background": "rosa chiclete", "primary": "preto absoluto", "secondary": "branco duro", "accent": "azul elétrico"},
            {"background": "preto absoluto", "primary": "rosa chiclete", "secondary": "branco duro", "accent": "azul elétrico"},
            {"background": "branco duro", "primary": "rosa chiclete", "secondary": "preto absoluto", "accent": "azul elétrico"},
            {"background": "azul elétrico", "primary": "branco duro", "secondary": "rosa chiclete", "accent": "preto absoluto"},
        ],
    },
    {
        "name": "musgo sofisticado",
        "colors": {
            "verde total": "#16A34A",
            "ouro sujo": "#C08A00",
            "creme editorial": "#F5E9D4",
            "bordô seco": "#7F1D1D",
        },
        "schemes": [
            {"background": "verde total", "primary": "creme editorial", "secondary": "ouro sujo", "accent": "bordô seco"},
            {"background": "creme editorial", "primary": "verde total", "secondary": "bordô seco", "accent": "ouro sujo"},
            {"background": "bordô seco", "primary": "creme editorial", "secondary": "verde total", "accent": "ouro sujo"},
            {"background": "ouro sujo", "primary": "bordô seco", "secondary": "creme editorial", "accent": "verde total"},
        ],
    },
]

def pick_direction():
    mode = random.choice(["bom", "ruim_bom"])
    palette = random.choice(PALETTES)
    scheme = random.choice(palette["schemes"])

    def color(role_name: str):
        name = scheme[role_name]
        return {"name": name, "hex": palette["colors"][name]}

    return {
        "mode": mode,
        "colors": {
            "background": color("background"),
            "primary": color("primary"),
            "secondary": color("secondary"),
            "accent": color("accent"),
        },
        "notes": [
            "não deixar a IA cair no default tech-clean genérico",
            "accent should be used sparingly",
        ],
    }


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--pretty", action="store_true", help="saída legível")
    args = parser.parse_args()

    result = pick_direction()

    if args.pretty:
        print(f"🎲 Modo: {result['mode']}")
        print(f"🎨 Background: {result['colors']['background']['name']} ({result['colors']['background']['hex']})")
        print(f"🎨 Primary: {result['colors']['primary']['name']} ({result['colors']['primary']['hex']})")
        print(f"🎨 Secondary: {result['colors']['secondary']['name']} ({result['colors']['secondary']['hex']})")
        print(f"🎨 Accent: {result['colors']['accent']['name']} ({result['colors']['accent']['hex']})")
        print("\n📌 Notas:")
        for note in result['notes']:
            print(f"- {note}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
