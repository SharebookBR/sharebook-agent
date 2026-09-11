# Missão - Importar Bruxas & Magia via Project Gutenberg

## Objetivo

Cadastrar a source inicial da vitrine **Bruxas & Magia** no importer do Sharebook, usando Project Gutenberg como origem operacional única.

Esta missão não publica automaticamente a vitrine. Ela alimenta a fila para o pipeline posterior de tradução PT-BR, QA editorial, geração de EPUB/capa e publicação.

## Fonte

- Source sugerida: `project_gutenberg_witches_magic`
- Source URL sugerida: `https://www.gutenberg.org/`
- Origem operacional: Project Gutenberg
- Idioma original esperado: inglês
- Idioma final desejado: pt-BR
- Tradução final: Sharebook AI Translation, criada do zero a partir do original elegível

## Fila

- [waiting_triage] The Witch of Salem; or, Credulity Run Mad | https://www.gutenberg.org/ebooks/26282 | John R. Musick; bruxaria/Salem; elegível BR provável.
- [waiting_triage] The Lancashire Witches: A Romance of Pendle Forest | https://www.gutenberg.org/ebooks/15493 | W. H. Ainsworth; romance de bruxas; elegível BR provável.
- [waiting_triage] Salem Witchcraft, Volumes I and II | https://www.gutenberg.org/ebooks/17845 | Charles W. Upham; Salem/documental; elegível BR provável.
- [waiting_triage] Letters on Demonology and Witchcraft | https://www.gutenberg.org/ebooks/14461 | Walter Scott; demonologia/bruxaria; elegível BR provável.
- [waiting_triage] The Superstitions of Witchcraft | https://www.gutenberg.org/ebooks/22822 | Howard Williams; bruxaria/superstição; elegível BR provável.
- [waiting_triage] Black Magic | https://www.gutenberg.org/ebooks/77782 | Marjorie Bowen; magia negra/ficção; elegível BR provável.
- [waiting_triage] Living Alone | https://www.gutenberg.org/ebooks/14907 | Stella Benson; fantasia/bruxa; elegível BR provável.
- [waiting_triage] Dulcibel: A Tale of Old Salem | https://www.gutenberg.org/ebooks/20569 | Henry Peterson; Salem/ficção histórica; elegível BR provável.
- [waiting_triage] The Discovery of Witches | https://www.gutenberg.org/ebooks/14015 | Matthew Hopkins; caça às bruxas; elegível BR provável.
- [waiting_triage] Mary Schweidler, the Amber Witch | https://www.gutenberg.org/ebooks/8743 | Wilhelm Meinhold; bruxa/ficção gótica; elegível BR provável.
- [waiting_triage] The Witch of Prague: A Fantastic Tale | https://www.gutenberg.org/ebooks/3816 | F. Marion Crawford; bruxa/romance fantástico; substitui The King in Yellow por aderência temática mais forte.
- [waiting_triage] The Great God Pan | https://www.gutenberg.org/ebooks/389 | Arthur Machen; paganismo/ocultismo/horror; elegível BR provável.
- [waiting_triage] The Necromancers | https://www.gutenberg.org/ebooks/14275 | Robert Hugh Benson; necromancia/espiritualismo; elegível BR provável.
- [waiting_triage] Zanoni | https://www.gutenberg.org/ebooks/2664 | Edward Bulwer-Lytton; rosacrucianismo/iniciação/ocultismo; elegível BR provável.
- [waiting_triage] The Book of Were-Wolves | https://www.gutenberg.org/ebooks/5324 | Sabine Baring-Gould; folclore sombrio/licantropia; encaixe adjacente em folclore e horror mágico.

## Substituição Curatorial

Substituição aplicada em 2026-09-11:

- Removido do pool principal: **The King in Yellow**, por ser mais adequado a uma vitrine futura de horror cósmico/oculto do que a **Bruxas & Magia**.
- Adicionado: **The Witch of Prague: A Fantastic Tale**, por aderência mais literal ao tema de bruxas/magia e bom potencial de vitrine.

## Notas Operacionais

- Linhas validadas contra o formato aceito por `mission_parser.py`.
- A source é segmentada por origem, não por campanha genérica: todos os itens apontam para `gutenberg.org`.
- O pipeline atual do importer ainda deve tratar esta source como uma missão de tradução/derivação, não como importação direta de PDF pronto.
- Antes de publicar, manter a regra: original elegível + tradução PT-BR própria + QA + rastreabilidade.

## Cadastro no Importer — 2026-09-11

- Source criada no banco: `project_gutenberg_witches_magic`
- Source id: `8`
- Itens inseridos: `15`
- IDs criados: `1868` a `1882`
- Status inicial dos itens: `waiting_triage`
- URLs fora de `gutenberg.org`: `0`
- Source mantida como `enabled = false` por enquanto, porque esta fila depende do pipeline de tradução/derivação Gutenberg e não deve ser consumida pelo worker genérico de PDF antes desse ajuste.
