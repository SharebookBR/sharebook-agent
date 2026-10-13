# Cover Direction Scripts

Ferramentas do playbook de capas.

- `cover_prompt_from_url.py` — extrai titulo/autor/sinopse da URL Sharebook e gera briefing com roleta visual.
- `cover_roulette.py` — sorteia modo, paleta e familias visuais com seed e exclusoes.
- `prepare_cover.py` — converte/otimiza capa final para JPEG dentro do limite seguro de upload.
- `cover_generate.py` — fallback local com Pillow para agentes sem geracao nativa de imagem.
- `generate_covers.py` — gera variacoes locais para comparacao rapida.
- `sharebook_openai_cover.py` — fallback pago via OpenAI Images; exige confirmacao explicita do Raffa.
- `test_cover_roulette.py` — testes determinísticos da roleta.
