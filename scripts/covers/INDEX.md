# Scripts de Covers

Geração, variação e utilitários de capa.

## Scripts
- `cover_generate.py` — fallback local para agentes sem geração de imagem nativa. Gera capa 600x900 com Pillow, sem API externa. Cross-platform desde 2026-06-30. Uso: `python cover_generate.py "<TITULO>" "<AUTOR>" -o <arquivo.jpg>`.
- `cover_prompt_from_url.py` — extrai título, autor e sinopse da URL do Sharebook, roda a roleta e produz a direção completa para geração.
- `prepare_cover.py` — converte a capa escolhida para JPEG otimizado e reduz progressivamente qualidade/dimensões até o limite seguro de 800 KB para upload.
- `cover_roulette.py` — sorteia paleta + estilo apenas (wrapper legado, sem geração de imagem).
- `generate_covers.py` — gera múltiplas variações locais de capa para comparação rápida, sem API externa.
- `sharebook_openai_cover.py` — geração de capa via OpenAI. Uso bloqueado por padrão; exige confirmação explícita do Raffa.

## Regra operacional
- Com ferramenta nativa de geração de imagem: seguir `skills/product-ux/cover-direction/SKILL.md`, gerar 3 capas independentes, escolher a melhor e publicar pela API.
- Sem ferramenta nativa: usar `generate_covers.py`/`cover_generate.py`.
- `sharebook_openai_cover.py` e outras chamadas de API cobradas exigem confirmação explícita do Raffa; geração nativa já disponível no harness não usa esse fallback.
