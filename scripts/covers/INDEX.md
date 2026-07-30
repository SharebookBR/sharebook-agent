# Scripts de Covers

Geração, variação e utilitários de capa.

## Scripts
- `cover_generate.py` — fallback local para agentes sem geração de imagem nativa. Gera capa 600x900 com Pillow, sem API externa. Cross-platform desde 2026-06-30. Uso: `python cover_generate.py "<TITULO>" "<AUTOR>" -o <arquivo.jpg>`.
- `cover_prompt_from_url.py` — extrai título, autor e sinopse da URL do Sharebook, roda a roleta e produz um briefing com paleta-base e 3 famílias de macrogrupos distintos. Aceita `--avoid-group` e `--avoid-style` para excluir tendências recentes.
- `prepare_cover.py` — converte a capa escolhida para JPEG otimizado e reduz progressivamente qualidade/dimensões até o limite seguro de 800 KB para upload.
- `cover_roulette.py` — sorteia modo, paleta-base e famílias visuais estruturadas. Gera 3 estilos de macrogrupos distintos por padrão; suporta `--avoid-group`, `--avoid-style`, `--seed`, `--pretty` e `--list-styles`.
- `generate_covers.py` — gera múltiplas variações locais de capa para comparação rápida, sem API externa.
- `sharebook_openai_cover.py` — geração de capa via OpenAI. Uso bloqueado por padrão; exige confirmação explícita do Raffa.
- `test_cover_roulette.py` — testes determinísticos de diversidade, exclusões, seed e briefing.

## Regra operacional
- Com ferramenta nativa de geração de imagem: revisar as 8 capas recentes, excluir famílias dominantes, seguir as 3 direções sorteadas, escolher a melhor e publicar pela API.
- Sem ferramenta nativa: usar `generate_covers.py`/`cover_generate.py`.
- `sharebook_openai_cover.py` e outras chamadas de API cobradas exigem confirmação explícita do Raffa; geração nativa já disponível no harness não usa esse fallback.
