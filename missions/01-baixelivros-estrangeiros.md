# Missão Principal — 01 BaixeLivros Estrangeiros

## Objetivo
Manter ingestão contínua e sequencial da fonte BaixeLivros (categoria Literatura Estrangeira), com foco em throughput estável, sem duplicação e sem quebrar publicação.

## Regra de status (canônica)
Quando Raffa pedir apenas **"status"**, responder a partir deste arquivo.

Formato preferido:
- total
- done
- pending
- %
- próximo item
- leitura curta

## Fila Canônica da Fonte

- Última sincronização: `2026-04-08`
- Fonte oficial: `https://www.baixelivros.com.br/biblioteca/literatura-estrangeira`
- Total canônico: `59` livros
- Status atual:
- `49` como `done`
- `9` como `pending`
- `1` como `source_blocked`
- `0` como `retry_later`
- Próximo item: `A Ilha Do Tesouro`

## Regras

- Este arquivo é a fonte da verdade para a fila sequencial da automação de ebook.
- Cada execução deve começar do primeiro item com status `pending`.
- Se o título já existir no Sharebook, mudar para `done`.
- Se a fonte estiver quebrada, mudar para `source_blocked`.
- Se o problema for temporário, usar `retry_later` com nota curta no fim da linha.
- Não reordenar a fila por gosto pessoal.

## Fila

- [done] 01. Contos Da Selva | https://www.baixelivros.com.br/literatura-estrangeira/contos-da-selva/ | ebook publicado em 2026-04-08; id `019d6f6f-2b6b-72bb-9b2c-9ad2ffec2e9d`
- [done] 02. O Ventre De Napoles | https://www.baixelivros.com.br/literatura-estrangeira/o-ventre-de-napoles/ | ebook publicado em 2026-04-08; id `019d6f70-8a08-787d-a8f8-3b105ed43773`
- [done] 03. Sonho De Uma Noite De Verao | https://www.baixelivros.com.br/literatura-estrangeira/sonho-de-uma-noite-de-verao/ | ebook publicado em 2026-04-09; id `019d6f8a-1ef7-7113-a84a-54ebc40cff07`
- [done] 04. Rei Lear | https://www.baixelivros.com.br/literatura-estrangeira/rei-lear/ | ebook publicado em 2026-04-09; id `019d6f96-fc17-7174-aeba-b03a1f0fa2d7`
- [done] 05. Otelo | https://www.baixelivros.com.br/literatura-estrangeira/otelo/ | ebook publicado em 2026-04-09; id `019d6f9f-4510-74fa-a944-f2ff9d4ca6f5`
- [done] 06. Os Tres Mosqueteiros | https://www.baixelivros.com.br/literatura-estrangeira/os-tres-mosqueteiros/ | ebook publicado em 2026-04-09; id `019d6fa3-0b2c-7eac-8617-b5e8a68b98ce`
- [done] 07. O Retorno | https://www.baixelivros.com.br/literatura-estrangeira/o-retorno/ | ebook publicado em 2026-04-09; id `019d6fab-5390-7503-ba35-78a688e2b94d`
- [done] 08. De Quanta Terra Um Homem Precisa | https://www.baixelivros.com.br/literatura-estrangeira/de-quanta-terra-um-homem-precisa/ | ebook publicado em 2026-04-09; id `019d701c-0679-7835-97ff-947da7860cdd`
- [done] 09. Oliver Twist | https://www.baixelivros.com.br/literatura-estrangeira/oliver-twist/ | ebook publicado em 2026-04-09; id `019d708c-4fc2-7e85-80e2-65a2c3562540`
- [done] 10. Livro De Magoas | https://www.baixelivros.com.br/literatura-estrangeira/livro-de-magoas/ | ebook já existia em produção; id `019d43c5-3ee7-7cdf-879c-1e6688936eeb`
- [done] 11. A Fada Melusina | https://www.baixelivros.com.br/literatura-estrangeira/a-fada-melusina/ | ebook publicado em 2026-04-09; id `019d70fd-1641-7da6-bfaf-3f33f6fa79b4`
- [done] 12. Dom Quixote | https://www.baixelivros.com.br/literatura-estrangeira/dom-quixote/ | ebook publicado em 2026-04-09; id `019d716e-06a3-7c9d-b6a7-9ae8e2194ab7`
- [done] 13. Faetonte | https://www.baixelivros.com.br/literatura-estrangeira/faetonte/ | ebook publicado em 2026-04-09; id `019d71de-7c41-773c-8895-3eb90795123c`
- [done] 14. O Rei Creso | https://www.baixelivros.com.br/literatura-estrangeira/o-rei-creso/ | ebook publicado em 2026-04-09; id `019d724f-94af-7379-a2e0-817e22403d02`
- [done] 15. A Caixa De Pandora | https://www.baixelivros.com.br/literatura-estrangeira/a-caixa-de-pandora/ | ebook publicado em 2026-04-09; id `019d72c0-0c18-7ee1-8611-21649dd612b4`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 16. Coracao De Cachorro | https://www.baixelivros.com.br/literatura-estrangeira/coracao-de-cachorro/ | ebook publicado em 2026-04-09; id `019d7330-2629-7ed2-988e-ff7731cbf493`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 17. A Ilha Do Tesouro Ed Bilingue | https://www.baixelivros.com.br/literatura-estrangeira/a-ilha-do-tesouro-ed-bilingue/ | ebook publicado em 2026-04-09; id `019d73a0-3eee-786b-a237-648d99ac75fe`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 18. Coracao Das Trevas | https://www.baixelivros.com.br/literatura-estrangeira/coracao-das-trevas/ | ebook publicado em 2026-04-09; id `019d73e5-a206-7571-b9a6-086772e02b84`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 19. As Roupas Fazem As Pessoas | https://www.baixelivros.com.br/literatura-estrangeira/as-roupas-fazem-as-pessoas/ | ebook publicado em 2026-04-09; id `019d744b-f74c-7940-9c20-dddde0c528b6`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 20. Os Miseraveis Aljahiz | https://www.baixelivros.com.br/literatura-estrangeira/os-miseraveis-aljahiz/ | ebook publicado em 2026-04-09; id `019d745b-d71a-7587-acfe-db1f57096210`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 21. O Jardim Secreto | https://www.baixelivros.com.br/literatura-estrangeira/o-jardim-secreto/ | ebook publicado em 2026-04-09; id `019d745f-3a50-7a98-ae6e-6fed58bc1b09`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 22. O Sinaleiro | https://www.baixelivros.com.br/literatura-estrangeira/o-sinaleiro/ | ebook já existia em produção; id `019d74bd-3be8-7f6a-abc5-dc97de20420a`
- [done] 23. 1984 | https://www.baixelivros.com.br/literatura-estrangeira/1984/ | ebook publicado em 2026-04-10; id `019d755f-165d-7fff-952c-fa2d58f8cfac`; categoria `Ficção > Ficção científica`; exceção manual fora da ordem sequencial por pedido do Raffa
- [done] 24. Fausto | https://www.baixelivros.com.br/literatura-estrangeira/fausto/ | ebook já existia em produção; id `019d4090-e19b-7049-b94d-e75c0fd3ffd6`
- [done] 25. Utopia | https://www.baixelivros.com.br/literatura-estrangeira/utopia/ | ebook publicado em 2026-04-10; id `019d7563-b594-78b7-9330-d51e5f25fe69`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 26. Crime E Castigo | https://www.baixelivros.com.br/literatura-estrangeira/crime-e-castigo/ | ebook publicado em 2026-04-10; id `019d75d3-6985-70e5-b8f4-7214ef1fc24d`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 27. Paraiso Perdido John Milton | https://www.baixelivros.com.br/literatura-estrangeira/paraiso-perdido-john-milton/ | ebook publicado em 2026-04-10; id `019d7685-e964-7631-8089-43f182189ce9`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 28. A Carta Roubada | https://www.baixelivros.com.br/literatura-estrangeira/a-carta-roubada/ | ebook publicado em 2026-04-10; id `019d76f6-1396-7ce9-8d0c-69a4abe2d2ff`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 29. Um Conto De Natal | https://www.baixelivros.com.br/literatura-estrangeira/um-conto-de-natal/ | ebook publicado em 2026-04-10; id `019d7766-66ad-7b0e-9489-64980763757a`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 30. Guia Para Os Classicos Moby Dick | https://www.baixelivros.com.br/literatura-estrangeira/guia-para-os-classicos-moby-dick/ | ebook publicado em 2026-04-10; id `019d77d6-7264-7323-9e0b-2295e0a1ca91`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 31. Guia Para Os Classicos A Divina Comedia | https://www.baixelivros.com.br/literatura-estrangeira/guia-para-os-classicos-a-divina-comedia/ | ebook publicado em 2026-04-10; id `019d7846-f49e-7874-96a9-311db6f145d7`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 32. A Ilha Do Dr Moreau | https://www.baixelivros.com.br/literatura-estrangeira/a-ilha-do-dr-moreau/ | ebook publicado em 2026-04-10; id `019d78b6-c314-793b-9d96-36ca9d844016`; categoria `Ficção > Ficção científica`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 33. A Comedia Dos Erros | https://www.baixelivros.com.br/literatura-estrangeira/a-comedia-dos-erros/ | ebook publicado em 2026-04-11; id `019d7a7c-e17a-759d-b32c-34b53bf55e0f`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 34. Porco E Porco Ed Bilingue | https://www.baixelivros.com.br/literatura-estrangeira/porco-e-porco-ed-bilingue/ | ebook publicado em 2026-04-11; id `019d7a98-83fc-77fe-9263-204d6be3bf1f`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 35. Iliada | https://www.baixelivros.com.br/literatura-estrangeira/iliada/ | ebook publicado em 2026-04-11; id `019d7ab3-a897-7f2f-b5df-3fa34b5a7088`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 36. Hamlet | https://www.baixelivros.com.br/literatura-estrangeira/hamlet/ | ebook publicado em 2026-04-11; id `019d7acf-3b01-7053-aada-6edf37a252a4`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 37. A Dama Da Camelias | https://www.baixelivros.com.br/literatura-estrangeira/a-dama-da-camelias/ | ebook já existia em produção; id `019d48ea-cec5-7650-9a25-1e47dd8b2c8d`
- [done] 38. O Conde De Monte Cristo | https://www.baixelivros.com.br/literatura-estrangeira/o-conde-de-monte-cristo/ | ebook publicado em 2026-04-11; id `019d7aeb-c970-7b38-a81b-50039949a6fd`; categoria `Ficção > Aventura`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 39. Odisseia | https://www.baixelivros.com.br/literatura-estrangeira/odisseia/ | ebook publicado em 2026-04-11; id `019d7b06-997a-7e8a-a58d-cb4dff70d6c5`; categoria `Ficção > Aventura`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 40. As Pupilas Do Senhor Reitor | https://www.baixelivros.com.br/literatura-estrangeira/as-pupilas-do-senhor-reitor/ | ebook publicado em 2026-04-11; id `019d7b21-9641-71de-9b7e-fc1eaa1571b5`; categoria `Amor`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 41. A Metamorfose | https://www.baixelivros.com.br/literatura-estrangeira/a-metamorfose/ | ebook já existia em produção; id `019d4134-4609-7dab-9bb6-6e9aca380c2a`
- [done] 42. O Processo | https://www.baixelivros.com.br/literatura-estrangeira/o-processo/ | ebook publicado em 2026-04-11; id `019d7b3d-f658-7b0f-87f3-6a101299d5f9`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 43. Alice No Pais Das Maravilhas | https://www.baixelivros.com.br/literatura-estrangeira/alice-no-pais-das-maravilhas/ | ebook publicado em 2026-04-11; id `019d7b58-763d-70a5-ac66-acea818d2eaa`; categoria `Infantil/Juvenil`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 44. Conto De Inverno | https://www.baixelivros.com.br/literatura-estrangeira/conto-de-inverno/ | ebook publicado em 2026-04-11; id `019d7b74-1753-7e3a-8dc3-92637212807c`; categoria `Ficção > Drama`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 45. A Divina Comedia Paraiso | https://www.baixelivros.com.br/literatura-estrangeira/a-divina-comedia-paraiso/ | ebook publicado em 2026-04-11; id `019d7cfb-474a-70b9-92d2-e92342be1518`; retry manual com fallback HTTP direto em `https://www.ebooksbrasil.org/adobeebook/paraiso.pdf` (PDF válido `%PDF`)
- [source_blocked] 46. A Divina Comedia Inferno | https://www.baixelivros.com.br/literatura-estrangeira/a-divina-comedia-inferno/ | download da fonte retorna HTML/404 (ebooksbrasil `inferno.pdf` indisponível) em 2026-04-11
- [done] 47. A Divina Comedia Purgatorio | https://www.baixelivros.com.br/literatura-estrangeira/a-divina-comedia-purgatorio/ | ebook já existia em produção; id `019d49c9-e709-719f-9f03-f079bee6dc4c`
- [done] 48. O Livro Da Selva | https://www.baixelivros.com.br/literatura-estrangeira/o-livro-da-selva/ | ebook publicado em 2026-04-11; id `019d7b91-d7ec-787c-ab81-be5f4001adeb`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [done] 49. Peter Pan E Wendy | https://www.baixelivros.com.br/literatura-estrangeira/peter-pan-e-wendy/ | ebook publicado em 2026-04-11; id `019d7baa-da30-725c-af15-38889946a4d0`; categoria `Infantil/Juvenil`; família visual `foto realista encenada` (reuso de capa original); macrofamília `foto realista`
- [pending] 50. A Ilha Do Tesouro | https://www.baixelivros.com.br/literatura-estrangeira/a-ilha-do-tesouro/
- [pending] 51. A Revolucao Dos Bichos | https://www.baixelivros.com.br/literatura-estrangeira/a-revolucao-dos-bichos/
- [pending] 52. A Arte Da Guerra | https://www.baixelivros.com.br/literatura-estrangeira/a-arte-da-guerra/
- [pending] 53. As Viagens De Gulliver | https://www.baixelivros.com.br/literatura-estrangeira/as-viagens-de-gulliver/
- [pending] 54. O Mercador De Veneza | https://www.baixelivros.com.br/literatura-estrangeira/o-mercador-de-veneza/
- [pending] 55. Cidadela | https://www.baixelivros.com.br/literatura-estrangeira/cidadela/
- [done] 56. Dracula Pdf | https://www.baixelivros.com.br/literatura-estrangeira/dracula-pdf/ | ebook publicado em 2026-04-10; id `019d752c-dad8-7d5f-9cc3-bc070b162e3f`; exceção manual fora da ordem sequencial por pedido do Raffa
- [pending] 57. Eneida Pdf | https://www.baixelivros.com.br/literatura-estrangeira/eneida-pdf/
- [pending] 58. Romeu E Julieta | https://www.baixelivros.com.br/literatura-estrangeira/romeu-e-julieta/
- [pending] 59. A Divina Comedia | https://www.baixelivros.com.br/literatura-estrangeira/a-divina-comedia/
