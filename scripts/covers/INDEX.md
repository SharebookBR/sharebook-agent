# Scripts de Covers

Geração, variação e utilitários de capa.

## Scripts
- `cover_generate.py` — gera capa 600x900 com sorteio completo (paleta, fonte, layout, gradiente, efeito, elemento decorativo). Principal script de capa local. Cross-platform desde 2026-06-30 (fontes nativas Windows adicionadas + filtragem por pares realmente disponíveis; antes só conhecia fontes Linux e falhava no Windows). Uso: `python cover_generate.py "<TITULO>" "<AUTOR>" -o <arquivo.jpg>`.
- `cover_roulette.py` — sorteia paleta + estilo apenas (wrapper legado, sem geração de imagem).
- `generate_covers.py` — gera múltiplas variações locais de capa para comparação rápida, sem API externa.
- `sharebook_openai_cover.py` — geração de capa via OpenAI. Uso bloqueado por padrão; exige confirmação explícita do Raffa.

## Regra operacional
- Preferir o fluxo local para evitar custo.
- Só usar OpenAI quando houver confirmação explícita do Raffa.
