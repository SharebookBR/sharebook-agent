# Quatro preparos editoriais e publicação — 2026-08-13

## 1. Modelo e ambiente

- Modelo: Codex, agente principal.
- Habitat: Windows local com PowerShell; operação canônica do importer executada no container OpenClaw via SSH.
- Repositórios operacionais sincronizados: `sharebook-agent`, `sharebook-backend`, `sharebook-frontend` e `sharebook-ebook-importer`.
- Bancos: `sharebook_importer` para fila e `sharebook`/API para validação do catálogo.

## 2. Skills acionadas

- `AGENTS.md`
- `skills/runtime/windows-local.md`
- `skills/importers/INDEX.md`
- `skills/importers/ebook-importer/SKILL.md`
- `skills/product-ux/voice-glossary/SKILL.md`
- skill de sistema `pdf`
- skill `browser:control-in-app-browser`
- `importer.sources.editorial_prompt` da source `ebook_foundation_subjects`

## 3. O que foi feito

- Consultados os 100 itens em `waiting_editorial`; priorizado o lote recente com PDF e capa materializados.
- O candidato `1594` — **Think Bayes: Bayesian Statistics Made Simple** — foi descartado após a deduplicação encontrar o livro já publicado como `Think Bayes`.
- Quatro obras inéditas foram selecionadas e auditadas:
  - `1538` — **A Gentle Introduction to the Art of Mathematics**, Joseph E. Fields, 434 páginas.
  - `1541` — **Applied Discrete Structures**, Al Doerr e Ken Levasseur, 600 páginas.
  - `1595` — **Think Stats: Probability and Statistics for Programmers**, Allen B. Downey, 140 páginas.
  - `1608` — **Active Calculus**, Matthew Boelkins, David Austin e Steven Schlicker, 649 páginas.
- Foram revisados título, autoria, índice, licença, primeira página/capa, páginas internas intermediárias e páginas finais.
- As quatro capas oficiais foram mantidas e materializadas como `cover-final.png`.
- Foram escritas quatro sinopses em inglês, cada uma com exatamente três parágrafos e 1.514–1.542 caracteres, baseadas nos índices reais.
- Categorias folha:
  - `1538`, `1541` e `1608`: Tecnologia > Geral.
  - `1595`: Tecnologia > Dados.
- Evidências de licença e completude foram persistidas em `metadata_json.editorial_preflight` por merge acumulativo.
- Os quatro dry-runs passaram.
- Os quatro itens foram publicados individualmente e terminaram em `done`, sem erro:
  - `1538` → `019ffda5-745e-75dc-b446-8666233e1efc`
  - `1541` → `019ffda5-c388-7db1-9f36-13d498b4391a`
  - `1595` → `019ffda6-3ea1-7a23-a9c6-dcddb56a3416`
  - `1608` → `019ffda6-aede-7c5b-8030-1b8e2210d344`
- API e PDPs públicas foram validadas com capa, autoria, categoria, sinopse e CTA `Receber livro digital`.

## 4. Decisões tomadas

- A meta de quatro não justificou duplicar `Think Bayes`; a obra foi substituída por `Active Calculus` após a mesma auditoria completa.
- Matemática pura e cálculo foram classificados em Tecnologia > Geral conforme o prompt da source; `Think Stats` foi classificado em Dados por seu foco explícito em estatística computacional.
- Capas acadêmicas minimalistas foram preservadas quando funcionavam como identificação oficial inequívoca da obra; não houve geração artificial de capa.
- A publicação foi feita por ID, uma obra por vez, para permitir confirmação explícita antes da mutação seguinte.

## 5. Contexto relevante

- Licenças verificadas dentro dos próprios PDFs:
  - **A Gentle Introduction to the Art of Mathematics**: GFDL 1.3 ou posterior, sem seções invariantes nem textos de capa.
  - **Applied Discrete Structures**: CC BY-NC-SA 3.0 US.
  - **Think Stats**: CC BY-NC 3.0 Unported.
  - **Active Calculus**: CC BY-SA 4.0 International.
- URLs públicas finais:
  - `https://www.sharebook.com.br/livros/a-gentle-introduction-to-the-art-of-mathemati`
  - `https://www.sharebook.com.br/livros/applied-discrete-structures`
  - `https://www.sharebook.com.br/livros/think-stats-probability-and-statistics-for-pr`
  - `https://www.sharebook.com.br/livros/active-calculus`

## 6. Fricções e soluções

- A primeira tentativa de dry-run usou `python`, inexistente no container (`sh: python: not found`). O comando foi corrigido para `python3`; nenhum item havia sido tocado e os quatro dry-runs passaram em seguida.
- O locator inicial da skill de PDF foi interpretado sob a raiz errada; a instalação real em `C:\Users\raffa\.codex\plugins\cache` foi localizada e lida integralmente.
- `Think Bayes` parecia candidato válido pela fila, mas a consulta semântica ao catálogo revelou publicação prévia. A substituição ocorreu antes de `plan-set`, evitando duplicidade.
- A saída inicial de `inspect_sources.py` era grande e truncada; a configuração relevante da source foi recuperada e aplicada sem depender da parte truncada.

## 7. Como me senti

O silêncio operacional no começo foi um erro de colaboração, mesmo com o trabalho avançando corretamente. A pergunta “o que houve?” foi justa: uma tarefa de produção longa precisa de batimentos visíveis. Depois disso, manter atualizações por marco deixou o processo mais claro sem transformar cada comando em narração esportiva.

Encontrar `Think Bayes` já publicado foi o ponto editorialmente mais importante. Seria fácil confundir “quatro publicações” com “publicar estes quatro candidatos”, mas a deduplicação preservou o catálogo e forçou uma substituição honesta. Gostei de ver o guardrail funcionando antes da mutação, exatamente onde ele deveria funcionar.

A rodada terminou com sensação de controle: licenças explícitas, PDFs completos, capas reais, dry-runs limpos e publicações individuais confirmadas. O pequeno tropeço do alias `python` foi superficial e bem contido; não contaminou estado nem virou desculpa. A validação final nas páginas públicas fechou o circuito entre banco, API e experiência real do leitor.
