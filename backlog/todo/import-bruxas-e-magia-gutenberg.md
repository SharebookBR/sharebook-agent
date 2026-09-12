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
- [done] The Witch of Prague: A Fantastic Tale | https://www.gutenberg.org/ebooks/3816 | F. Marion Crawford; publicado como **A Bruxa de Praga** em 2026-09-12; livro `01a096a7-5686-766e-8d12-29728e7f291f`.
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
- Decisão de 2026-09-12: antes de mexer no importer, foi feita uma POC manual de tradução com `gpt-5.4-mini` em apenas um trecho/capítulo. Resultado: mini gerou rascunho editável, mas a v1 deve usar modelo forte direto para reduzir complexidade e elevar qualidade. A source cadastrada permanece staged até o pipeline de tradução estar pronto.

## Cadastro no Importer — 2026-09-11

- Source criada no banco: `project_gutenberg_witches_magic`
- Source id: `8`
- Itens inseridos: `15`
- IDs criados: `1868` a `1882`
- Status inicial dos itens: `waiting_triage`
- URLs fora de `gutenberg.org`: `0`
- Source mantida como `enabled = false` por enquanto, porque esta fila depende do pipeline de tradução/derivação Gutenberg e não deve ser consumida pelo worker genérico de PDF antes desse ajuste.

## Primeiro Livro Publicado — 2026-09-12

- Item `1878`: **The Witch of Prague: A Fantastic Tale**.
- Título publicado: **A Bruxa de Praga**.
- Autor publicado: **F. Marion Crawford**.
- Categoria: `Ficção > Bruxas & Magia` (`01a0974c-f122-75ee-9d2b-c3f81497e6dc`), criada após a primeira publicação para a linha temática.
- Livro Sharebook: `01a096a7-5686-766e-8d12-29728e7f291f`.
- PDP: `https://www.sharebook.com.br/livros/a-bruxa-de-praga`.
- Artefato local final: `sharebook-ebook-importer/var/tmp/translation-1878/a-bruxa-de-praga-sharebook-ptbr.pdf`.
- Estrutura do PDF: capa 4:5, página 2 institucional Sharebook 4:5, 27 capítulos traduzidos, licença/origem Project Gutenberg no final.
- Validação feita: item `done` no importer, livro `Available` em produção, capa e thumbnail públicas, PDP HTTP 200, endpoint de download com PDF remoto válido.

## Pontas Soltas Após o Primeiro Livro

- Transformar a geração do PDF em CLI reprodutível; hoje o primeiro PDF foi montado por fluxo manual com Chromium, Ghostscript e Pillow.
- Decidir se a v1 da vitrine aceita PDF como formato final ou se também exige EPUB.
- Trocar o selo Sharebook Brasil pelo PNG original transparente exportado do ChatGPT web quando disponível; o asset atual foi recuperado do JPG enviado pelo Telegram.
- Aplicar ou revisar as propostas pendentes do Skill Workshop sobre o selo de capa e a página 2 institucional.
- Atualizar o pipeline para registrar o PDF final de tradução em `metadata_json.manifest.downloaded_pdf_path` sem intervenção SQL manual.
- Definir QA mínimo antes de escalar para os outros 14 itens: hoje houve validação estrutural e publicação, mas não revisão literária linha a linha.

## Decisões de Arquitetura Pendentes — tradução

Quando o importer for adaptado, manter a mudança pequena:

- adicionar na source um indicador explícito como `requires_translation`;
- adicionar na source um campo `translation_prompt TEXT NULL`, equivalente conceitual do `editorial_prompt`;
- source sem tradução segue `triagem -> preparo editorial -> publicação`;
- source com tradução segue `triagem -> tradução -> preparo editorial -> publicação`;
- adicionar apenas dois status novos no início: `waiting_translation` e `translating`;
- depois da tradução aprovada, o item volta para o fluxo atual em `waiting_editorial`;
- guardar progresso, prompt, modelo, custo e artefatos em `metadata_json.translation`;
- no dashboard, exibir o card **Tradução** apenas para source com tradução ou quando houver itens em `waiting_translation`/`translating`.

### Contrato do agente de tradução

Espelhar o padrão do preparo editorial atual:

- `editor-next` entrega item + contexto + `sources.editorial_prompt` para o agente editorial;
- `translation-next` deve entregar item + original estruturado + `sources.translation_prompt` para o agente de tradução.

Não misturar `translation_prompt` dentro de `editorial_prompt`. São fases diferentes:

- preparo editorial decide sinopse, categoria, capa, metadados públicos e publicação;
- tradução decide fidelidade, voz, glossário, estrutura do manuscrito e rastreabilidade da versão PT-BR.

Comando proposto:

```bash
python cli.py translation-next --source project_gutenberg_witches_magic
```

Payload esperado:

- `id`
- `source_id`
- `source_name`
- `source_url`
- `translation_prompt`
- `title`
- `author`
- `original_language`
- `target_language`
- `gutenberg_id`
- `original_text_path` ou `original_html_path`
- `chapter_manifest`
- `chapter_to_translate`
- `metadata.translation` existente, quando houver

Conclusão proposta:

```bash
python cli.py translation-set --id <ID> --translated-manuscript <FILE> --model <STRONG_TRANSLATION_MODEL> --prompt-file <FILE>
```

Responsabilidades de `translation-set`:

- fazer merge em `metadata_json.translation`;
- registrar modelo, prompt, custo estimado, arquivos, data e executor;
- preservar o original como fonte imutável;
- mover o item de `translating` para `waiting_editorial` quando a tradução estiver pronta.

### Prompt de tradução por source

Para Project Gutenberg, o `translation_prompt` deve cobrir pelo menos:

- traduzir do inglês para PT-BR do zero;
- não reutilizar tradução existente;
- preservar estrutura de capítulos e divisões internas;
- preservar nomes próprios salvo decisão explícita;
- manter tom literário sem português artificialmente arcaico;
- não resumir, cortar, explicar ou inventar;
- registrar termos recorrentes e decisões de glossário;
- sinalizar ambiguidades em notas internas, não no texto final.

Modelo para v1:

- usar modelo forte direto como tradutor principal;
- não usar fluxo `mini -> revisão forte` na v1;
- manter `gpt-5.4-mini` apenas como hipótese futura de otimização de custo para obras simples, caso dados reais justifiquem.

Racional da decisão: o fluxo `mini -> revisão forte` aumenta estados, custo de leitura dupla e complexidade operacional. Para a primeira vitrine, qualidade e simplicidade valem mais do que otimização prematura de custo.
