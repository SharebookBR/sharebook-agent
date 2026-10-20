# Tag Manager Scripts

Ferramentas de tagueamento, backfill e verificacao do catalogo.

- `seed_tags_v0.py` — seed inicial do vocabulario de tags.
- `backfill_technical_tags.py` — backfill regex para ebooks tecnicos.
- `complete_technical_tags.py` — completa cobertura criando tags e aplicando lotes.
- `refine_technical_tag_overrides.py` — aplica overrides editoriais explicitos.
- `enrich_single_tag_books.py` — enriquece ebooks tecnicos com exatamente uma tag.
- `discover_tag_books.py` e `probe_tags.py` — sondas de descoberta e endpoints de tag.
- `verify_tags_e2e.py` — verificacao ponta a ponta.
- `seed_amores_perigosos.py` — cria a tag editorial transversal e aplica a curadoria inicial sem apagar tags existentes.
