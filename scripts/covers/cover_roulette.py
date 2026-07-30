#!/usr/bin/env python3
"""
Roleta de direção visual para capas de livros.

Objetivo:
- aumentar a diversidade real do catálogo
- sortear a partir de paletas-mãe coerentes
- distribuir background, primary, secondary e accent sem perder harmonia
- sortear um modo conceitual: bom vs ruim_bom
- sortear famílias visuais distintas, com materialidade, luz e profundidade
- permitir excluir estilos recentes para reduzir repetição na prateleira
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

MODE_GUIDANCE = {
    "bom": (
        "acabamento intencional, coerente e publicável; hierarquia forte, "
        "sem esterilidade corporativa"
    ),
    "ruim_bom": (
        "imperfeição deliberada e energia ingênua controlada; estranho com propósito, "
        "nunca texto errado ou execução descuidada"
    ),
}

STYLE_FAMILIES = [
    {
        "id": "fotografia-editorial",
        "group": "realista",
        "name": "fotografia editorial",
        "medium": "fotografia realista ou composição fotorrealista editorial",
        "materiality": "pele, tecido, vidro, metal e ambiente com textura natural",
        "lighting": "luz natural ou editorial suave, com contraste crível",
        "depth": "cena profunda e habitável",
        "subject": "pessoa, objeto ou ambiente real em contexto",
        "palette_behavior": "usar as cores como direção de color grading; preservar tons naturais necessários",
        "guidance": "buscar presença humana, gesto, atmosfera e um instante narrativo",
        "avoid": "retrato corporativo genérico, banco de imagem e pessoa apontando para holograma",
    },
    {
        "id": "cena-cinematografica",
        "group": "realista",
        "name": "cena cinematográfica",
        "medium": "ilustração fotorrealista ou concept art cinematográfico",
        "materiality": "materiais ricos, reflexos controlados e atmosfera",
        "lighting": "luz dramática com contraste quente-frio e foco narrativo",
        "depth": "ambiente profundo com primeiro, médio e último plano",
        "subject": "uma situação em andamento, não um objeto isolado",
        "palette_behavior": "expandir a paleta com tons derivados, luz ambiente e cores materiais",
        "guidance": "construir uma cena que pareça ter acontecido um segundo antes ou depois",
        "avoid": "pôster de filme genérico, excesso de lens flare e espetáculo sem ideia",
    },
    {
        "id": "diorama-3d",
        "group": "tridimensional",
        "name": "diorama 3D",
        "medium": "miniatura tridimensional estilizada ou maquete isométrica",
        "materiality": "clay, papel, plástico, metal pintado ou madeira em miniatura",
        "lighting": "luz de estúdio com sombras macias e volume legível",
        "depth": "objeto espacial ou corte em camadas",
        "subject": "um pequeno mundo, máquina ou arquitetura simbólica",
        "palette_behavior": "usar as âncoras como materiais dominantes e permitir variações de luz e sombra",
        "guidance": "fazer o leitor querer explorar o objeto e descobrir relações internas",
        "avoid": "render de produto vazio, plástico genérico e isometria corporativa sem narrativa",
    },
    {
        "id": "neon-emissivo",
        "group": "digital-luminoso",
        "name": "neon emissivo",
        "medium": "arte digital luminosa com interfaces, vidro, energia ou tipografia emissiva",
        "materiality": "luz, vidro, superfícies escuras e transparências",
        "lighting": "noturna, emissiva e colorida",
        "depth": "camadas luminosas com perspectiva e atmosfera",
        "subject": "sistema, portal, objeto ou ambiente energizado",
        "palette_behavior": "expandir as âncoras em gradientes luminosos e acentos espectrais coerentes",
        "guidance": "usar brilho como estrutura e narrativa, não como maquiagem",
        "avoid": "cyberpunk genérico, excesso de glow e UI ilegível espalhada",
    },
    {
        "id": "abstracao-geometrica",
        "group": "grafico-abstrato",
        "name": "abstração geométrica",
        "medium": "composição abstrata de formas, ritmo, escala e tensão espacial",
        "materiality": "formas vetoriais, recortes ou planos translúcidos",
        "lighting": "plana ou sutilmente volumétrica",
        "depth": "do plano gráfico a camadas rasas",
        "subject": "relações visuais abstratas inspiradas no tema",
        "palette_behavior": "usar âncoras, tons derivados e transparências; não exigir quatro tintas rígidas",
        "guidance": "traduzir o argumento do livro em ritmo e forma, sem pictogramas literais demais",
        "avoid": "formas aleatórias decorativas e Bauhaus de banco de imagem",
    },
    {
        "id": "serigrafia-editorial",
        "group": "impresso-colagem",
        "name": "serigrafia editorial",
        "medium": "pôster impresso, serigrafia, risografia ou gravura editorial",
        "materiality": "papel, tinta fosca, retícula e registro imperfeito",
        "lighting": "plana, gráfica e sem brilho",
        "depth": "superfície de pôster ou colagem muito rasa",
        "subject": "metáfora visual forte, diagrama ou personagem gráfico",
        "palette_behavior": "usar estritamente as quatro cores como tintas spot",
        "guidance": "assumir a materialidade impressa com convicção e economia",
        "avoid": "usar este estilo como default, falsa sujeira e nostalgia sem relação com o livro",
    },
    {
        "id": "colagem-mista",
        "group": "impresso-colagem",
        "name": "colagem de mídia mista",
        "medium": "fotografia, papel recortado, desenho e textura combinados",
        "materiality": "papéis, rasgos, fita, impressão, foto e marcas manuais",
        "lighting": "variável, unificada pela direção de arte",
        "depth": "camadas rasas com sobreposição tátil",
        "subject": "fragmentos reais e gráficos formando uma ideia nova",
        "palette_behavior": "usar âncoras para unificar materiais e permitir cores incidentais controladas",
        "guidance": "produzir contraste entre fontes visuais sem perder hierarquia",
        "avoid": "scrapbook aleatório, recorte decorativo e excesso de elementos pequenos",
    },
    {
        "id": "pintura-expressiva",
        "group": "ilustrado-narrativo",
        "name": "pintura expressiva",
        "medium": "pintura digital, guache, acrílica ou pincelada gestual",
        "materiality": "pigmento, pincel, manchas e bordas orgânicas",
        "lighting": "atmosférica e emocional",
        "depth": "livre, do campo pictórico à paisagem profunda",
        "subject": "cena, figura, objeto ou abstração interpretada pelo gesto",
        "palette_behavior": "usar as âncoras como harmonia dominante e permitir mistura cromática ampla",
        "guidance": "priorizar emoção, movimento e unidade pictórica",
        "avoid": "pintura digital genérica, fantasia sem tema e textura aplicada como filtro",
    },
    {
        "id": "quadrinhos-autoral",
        "group": "ilustrado-narrativo",
        "name": "quadrinhos autoral",
        "medium": "desenho narrativo, cartum editorial ou pequena sequência de quadrinhos",
        "materiality": "linha, tinta, lápis, aguada ou cor digital desenhada",
        "lighting": "gráfica ou dramática conforme a narrativa",
        "depth": "painel único dinâmico ou sequência curta",
        "subject": "personagem e ação comunicando o conflito central",
        "palette_behavior": "usar âncoras com tons derivados e cores locais controladas",
        "guidance": "contar uma micro-história legível antes mesmo de ler o título",
        "avoid": "mascote infantil automático, super-herói genérico e balões com texto inventado",
    },
    {
        "id": "ilustracao-cientifica",
        "group": "explicativo-tecnico",
        "name": "ilustração científica",
        "medium": "corte técnico, atlas, diagrama anatômico, mapa ou desenho explicativo",
        "materiality": "linha precisa, superfícies seccionadas e detalhes funcionais",
        "lighting": "clara e descritiva, sem dramatização vazia",
        "depth": "estrutura em corte, explodida ou mapeada",
        "subject": "um sistema revelado por dentro",
        "palette_behavior": "usar âncoras com tons funcionais derivados para separar camadas",
        "guidance": "fazer a explicação virar imagem memorável, não infográfico de slide",
        "avoid": "diagrama corporativo, rótulos falsos e excesso de microdetalhe ilegível",
    },
    {
        "id": "tipografia-conceitual",
        "group": "grafico-abstrato",
        "name": "tipografia conceitual",
        "medium": "composição liderada por letras, palavras, escala e espaço negativo",
        "materiality": "tipo impresso, digital, recortado, construído ou integrado a objetos",
        "lighting": "adequada à materialidade escolhida",
        "depth": "do plano tipográfico ao tipo como objeto espacial",
        "subject": "o título transformado no próprio conceito visual",
        "palette_behavior": "usar âncoras e variações tonais; permitir extensão cromática quando a ideia exigir",
        "guidance": "fazer a tipografia agir, quebrar, ocupar ou revelar algo",
        "avoid": "apenas título grande sobre fundo bonito e deformar a legibilidade",
    },
    {
        "id": "minimalismo-simbolico",
        "group": "grafico-abstrato",
        "name": "minimalismo simbólico",
        "medium": "um símbolo, objeto ou gesto visual dominante com muito espaço",
        "materiality": "gráfica, fotográfica ou tridimensional conforme o conceito",
        "lighting": "simples e precisa",
        "depth": "um plano ou um objeto isolado",
        "subject": "uma única metáfora inevitável",
        "palette_behavior": "usar poucas âncoras, tons derivados e contraste extremo",
        "guidance": "reduzir até restar somente a ideia que o livro realmente possui",
        "avoid": "minimalismo vazio, ícone genérico e excesso de espaço sem tensão",
    },
    {
        "id": "surrealismo-editorial",
        "group": "tridimensional",
        "name": "surrealismo editorial",
        "medium": "imagem impossível tratada como fotografia, pintura, colagem ou 3D",
        "materiality": "realismo material aplicado a uma relação absurda",
        "lighting": "cinematográfica ou editorial coerente",
        "depth": "cena ou objeto com presença espacial forte",
        "subject": "metáfora impossível que condensa o argumento do livro",
        "palette_behavior": "usar âncoras como direção e permitir espectro natural ou atmosférico",
        "guidance": "produzir estranhamento imediato e significado depois do segundo olhar",
        "avoid": "surrealismo aleatório, sonho genérico e objetos flutuando sem relação",
    },
    {
        "id": "pop-digital-cromatico",
        "group": "digital-luminoso",
        "name": "pop digital cromático",
        "medium": "arte digital de alta energia, gradientes, camadas e cor expandida",
        "materiality": "luz, superfícies gráficas, transparências e formas digitais",
        "lighting": "luminosa, vibrante e multicolorida",
        "depth": "camadas dinâmicas ou espaço digital profundo",
        "subject": "objeto, sistema, personagem ou tipografia em transformação",
        "palette_behavior": "usar as âncoras como pontos de partida e expandir para um espectro harmônico",
        "guidance": "buscar exuberância controlada, ritmo e prazer visual",
        "avoid": "rainbow gratuito, excesso de efeitos e estética de template promocional",
    },
]


def style_ids() -> set[str]:
    return {style["id"] for style in STYLE_FAMILIES}


def style_groups() -> set[str]:
    return {style["group"] for style in STYLE_FAMILIES}


def pick_direction(
    rng: random.Random | None = None,
    style_count: int = 3,
    avoid_styles: list[str] | None = None,
    avoid_groups: list[str] | None = None,
):
    rng = rng or random.Random()
    avoided_styles = set(avoid_styles or [])
    avoided_groups = set(avoid_groups or [])
    unknown_styles = avoided_styles - style_ids()
    unknown_groups = avoided_groups - style_groups()
    if unknown_styles:
        raise ValueError(f"Estilos desconhecidos: {', '.join(sorted(unknown_styles))}")
    if unknown_groups:
        raise ValueError(f"Macrogrupos desconhecidos: {', '.join(sorted(unknown_groups))}")

    available_styles = [
        style
        for style in STYLE_FAMILIES
        if style["id"] not in avoided_styles and style["group"] not in avoided_groups
    ]
    styles_by_group: dict[str, list[dict]] = {}
    for style in available_styles:
        styles_by_group.setdefault(style["group"], []).append(style)

    if style_count < 1:
        raise ValueError("style_count deve ser maior que zero")
    if style_count > len(styles_by_group):
        raise ValueError(
            f"style_count={style_count} excede os {len(styles_by_group)} macrogrupos disponíveis"
        )

    mode = rng.choice(list(MODE_GUIDANCE))
    palette = rng.choice(PALETTES)
    scheme = rng.choice(palette["schemes"])
    selected_groups = rng.sample(list(styles_by_group), k=style_count)
    selected_styles = [
        rng.choice(styles_by_group[group])
        for group in selected_groups
    ]

    def color(role_name: str):
        name = scheme[role_name]
        return {"name": name, "hex": palette["colors"][name]}

    return {
        "mode": mode,
        "mode_guidance": MODE_GUIDANCE[mode],
        "palette": palette["name"],
        "colors": {
            "background": color("background"),
            "primary": color("primary"),
            "secondary": color("secondary"),
            "accent": color("accent"),
        },
        "styles": selected_styles,
        "notes": [
            "não deixar a IA cair no default tech-clean genérico",
            "as quatro cores são âncoras; seguir o palette_behavior de cada estilo",
            "as famílias pertencem a macrogrupos distintos; não misturá-las em uma única capa",
        ],
    }


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--pretty", action="store_true", help="saída legível")
    parser.add_argument("--styles", type=int, default=3, help="quantidade de famílias visuais")
    parser.add_argument(
        "--avoid-style",
        action="append",
        default=[],
        choices=sorted(style_ids()),
        help="família visual recente a excluir; pode repetir a opção",
    )
    parser.add_argument(
        "--avoid-group",
        action="append",
        default=[],
        choices=sorted(style_groups()),
        help="macrogrupo visual recente a excluir; pode repetir a opção",
    )
    parser.add_argument("--seed", type=int, help="seed para reproduzir um sorteio")
    parser.add_argument("--list-styles", action="store_true", help="listar famílias visuais")
    args = parser.parse_args()

    if args.list_styles:
        for style in STYLE_FAMILIES:
            print(f"{style['id']} [{style['group']}]: {style['name']}")
        return

    try:
        result = pick_direction(
            rng=random.Random(args.seed),
            style_count=args.styles,
            avoid_styles=args.avoid_style,
            avoid_groups=args.avoid_group,
        )
    except ValueError as exc:
        parser.error(str(exc))

    if args.pretty:
        print(f"🎲 Modo: {result['mode']}")
        print(f"🧭 Tratamento: {result['mode_guidance']}")
        print(f"🎨 Paleta-mãe: {result['palette']}")
        print(f"🎨 Background: {result['colors']['background']['name']} ({result['colors']['background']['hex']})")
        print(f"🎨 Primary: {result['colors']['primary']['name']} ({result['colors']['primary']['hex']})")
        print(f"🎨 Secondary: {result['colors']['secondary']['name']} ({result['colors']['secondary']['hex']})")
        print(f"🎨 Accent: {result['colors']['accent']['name']} ({result['colors']['accent']['hex']})")
        print("\n🎭 Famílias visuais:")
        for index, style in enumerate(result["styles"], start=1):
            print(f"{index}. {style['name']} ({style['id']})")
            print(f"   Macrogrupo: {style['group']}")
            print(f"   Meio: {style['medium']}")
            print(f"   Luz: {style['lighting']}")
            print(f"   Profundidade: {style['depth']}")
            print(f"   Cor: {style['palette_behavior']}")
        print("\n📌 Notas:")
        for note in result['notes']:
            print(f"- {note}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
