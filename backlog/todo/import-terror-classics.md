# Missao - Importar classicos de terror

## Objetivo

Cadastrar obras classicas de terror/horror para abastecer a vitrine Literatura de Terror.

## Fonte

- Source sugerida: `internet_archive_terror_classics`
- Source URL sugerida: `https://archive.org/details/texts`
- Extractor tecnico atual: `ebook_foundation` (resolver generico com suporte a Internet Archive)

## Fila

- [done] O Médico e o Monstro | https://archive.org/details/strangecasedrje00stevgoog | ebook publicado em 2026-09-10; id `01a08cac-9eb2-763e-8a3d-63b6194c790c`; slug `o-medico-e-o-monstro`.
- [done] Carmilla | https://archive.org/details/carmilla_20220725 | ebook publicado em 2026-09-10; id `01a08cac-b827-785a-8022-9a0c370357cf`; slug `carmilla`.
- [done] A Volta do Parafuso | https://archive.org/details/twomagicsturnofs00jameuoft | ebook publicado em 2026-09-10; id `01a08cac-ca1a-77a0-8cd8-f1376afb0deb`; slug `a-volta-do-parafuso`.
- [done] O Vampiro | https://archive.org/details/thevampyretale00poliuoft | ebook publicado em 2026-09-10; id `01a08cac-d768-7565-ae07-edc94ff1ac2d`; slug `o-vampiro`.
- [done] O Horla | https://archive.org/details/dli.ministry.14267 | ebook publicado em 2026-09-10; id `01a08cac-e892-7e23-b6b0-afe0c39a5a7f`; slug `o-horla`.
- [done] O Castelo de Otranto | https://archive.org/details/castleofotrant00walp | ebook publicado em 2026-09-10; id `01a08cac-fcc7-7494-a9b4-6b84445a0db0`; slug `o-castelo-de-otranto`.
- [done] O Gato Preto | https://archive.org/details/TheBlackCat_339 | ebook publicado em 2026-09-10; id `01a08cad-0b12-728b-9d3f-da1b38d6efa5`; slug `o-gato-preto`.
- [source_blocked] A Queda da Casa de Usher | https://archive.org/details/fallofhouseofush00poee | item `1863`; PDF do Internet Archive usa handler EBX e falha no `pdftoppm`; requer troca de edição.
- [waiting_triage] O Coração Delator | https://archive.org/details/telltaleheart0000poee_p6g0 | Edgar Allan Poe; Internet Archive; PDF resolvivel pelo importer.
- [waiting_triage] O Poço e o Pêndulo | https://archive.org/details/pitpendulumother0000poee | Edgar Allan Poe; Internet Archive; PDF resolvivel pelo importer.
- [waiting_triage] A Máscara da Morte Rubra | https://archive.org/details/the-masque-of-the-red-death-edgar-allan-poe_202507 | Edgar Allan Poe; Internet Archive; PDF resolvivel pelo importer.
- [waiting_triage] Berenice | https://archive.org/details/fallofhouseofush0000poee_x4h4 | Edgar Allan Poe; Internet Archive; PDF resolvivel pelo importer.

## Notas

- Linhas validadas contra o formato aceito por `mission_parser.py`.
- URLs Internet Archive testadas com `resolve_source_assets()` do extractor tecnico `ebook_foundation`.
- Source segmentada por origem: todos os itens desta missao apontam para Internet Archive.
- `A Queda da Casa de Usher` ficou `source_blocked` no item `1863`: o PDF escolhido no Internet Archive usa handler EBX e falha no `pdftoppm`.
- Metadados publicados corrigidos em 2026-09-10 para evitar surpresa de idioma. Os titulos e as sinopses publicados seguem o idioma real do PDF:
  - `o-medico-e-o-monstro` -> `Strange Case of Dr. Jekyll and Mr. Hyde` (PDF em ingles).
  - `carmilla` -> `Carmilla (edición en español)` (PDF em espanhol).
  - `a-volta-do-parafuso` -> `The Turn of the Screw` (PDF em ingles).
  - `o-vampiro` -> `The Vampyre` (PDF em ingles).
  - `o-horla` -> `The Horla` (PDF em ingles).
  - `o-castelo-de-otranto` -> `The Castle of Otranto` (PDF em ingles).
  - `o-gato-preto` -> `The Black Cat` (PDF em ingles).
