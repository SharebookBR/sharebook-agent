---
name: sharebook-baixelivros-editorial-preparer
description: Prepara editorialmente itens do BaixeLivros com eficiência máxima. Usa o contexto já extraído na triagem para decidir categoria e escrever sinopse de 3 parágrafos. Zero uso de ferramentas externas.
---

# Sharebook BaixeLivros Editorial Preparer (Ultra Lean)

Curadoria editorial de alto volume e baixo custo de tokens.

## Princípio de Operação

Você NÃO deve usar ferramentas de rede (browser, curl). Tudo o que você precisa já foi mastigado pela triagem e está no banco de dados.

O payload de `editor-next` agora pode trazer, além de texto:
- `preview_pages`: PNGs das primeiras páginas do PDF
- `local_cover_path`: capa baixada pela triagem
- `local_pdf_path`: PDF bruto local

Use esses campos visuais como insumo editorial primário quando existirem. O objetivo é gastar menos token cego e decidir melhor categoria, faixa etária implícita e sinopse.

## Fluxo de Trabalho (Otimizado para Token)

1.  **Obtenção do Item:**
    Obtenha o próximo item pronto para edição. Execute a partir da pasta do importer (`/data/workspace/sharebook-ebook-importer`), onde fica o `cli.py`.
    ```bash
    python3 cli.py editor-next --source baixelivros_infantil
    ```

    O JSON retornado pode incluir:
    - `id`
    - `title`
    - `author`
    - `context_text`
    - `local_pdf_path`
    - `local_cover_path`
    - `preview_pages`

2.  **Processamento Interno:**
    - Leia primeiro `preview_pages` e `local_cover_path` quando existirem. Eles são o melhor contexto para livro infantil.
    - Use `context_text` como apoio textual, não como fonte única.
    - Só recorra ao `local_pdf_path` se ainda faltar contexto depois dos previews.
    - Decida a categoria folha usando a tabela hardcoded abaixo.
    - Escreva a sinopse de **3 parágrafos**.

3.  **Escrita (Tool: run_shell_command):**
    Salve o resultado usando o CLI do importer.
    ```bash
    python cli.py plan-set --id <ID> --category-id <UUID> --synopsis-file <ARQUIVO_TEMP> --author "<AUTOR>" --planned-by "preparer-baixelivros"
    ```

## Categorias Hardcoded (NÃO consulte a API)

### 👶 Infantil / Juvenil (Principal)
- `019df04c-7a39-7bd3-8b72-c840e27f46e7` -> Bebês e Crianças Pequenas
- `019df04c-7a81-756b-932a-f424d916ef8e` -> Valores e Emoções
- `019df04c-7a72-729d-ae85-3c0c8de910f5` -> Animais e Natureza
- `019df04c-7a4d-7d00-b11f-902eaca73586` -> Educativos / Aprendizado
- `019df04c-7a90-7247-bf39-ee4a160446e7` -> Cultura Brasileira / Folclore
- `019df04c-79d2-7a9a-8f6e-49dc89cbda71` -> Clássicos Infantis
- `019df04c-7a5f-71e7-8c68-d7679d562d10` -> Aventuras e Fantasia
- `019e16e6-09db-7a64-9261-03e375f09192` -> Inclusão e Diversidade
- `019df04c-7aab-7889-a6a5-7579e8594e4a` -> Diversão e Humor
- `019df089-8268-73b1-871d-80bd395c752a` -> HQs e Mangás

### 🎭 Outros (Fallback)
- `019d9bf4-725d-7eb3-bf31-5dcd08c93053` -> Poesia Lírica (Se for poesia pura)
- `b5cdac27-d43b-4b99-96d9-285a8053e8bc` -> Drama Moral / Ético (Se for literário pesado)

## Guia de Decisão Rápida

- **Aconchego, rotina, descoberta:** `Bebês e Crianças Pequenas`
- **Lição, ensino, hábito:** `Educativos / Aprendizado`
- **Sentimentos, medos, amizade:** `Valores e Emoções`
- **Bichos falantes, floresta:** `Animais e Natureza`
- **Saci, Curupira, Lendas BR:** `Cultura Brasileira / Folclore`

## 🚨 Ordem de uso dos artefatos

Para `baixelivros_infantil`, siga esta ordem:

1. `preview_pages`
2. `local_cover_path`
3. `context_text`
4. `local_pdf_path`

Se `preview_pages` existir, assuma que a triagem já te entregou o melhor atalho visual. Não ignore isso e não volte para fluxo cego baseado só em texto.

Só leia o PDF localmente se os previews e o texto ainda forem insuficientes.

Se precisar desse fallback manual, registre `preparer-baixelivros (via manual pdf read)` no campo `--planned-by`.

## Regra da Sinopse (Obrigatória)

- **3 parágrafos.**
- Sem clichês ("Nesta obra emocionante...").
- Foco no que o livro entrega de verdade.
- Se o `context_text` for muito pobre, mencione o fato na sinopse de forma elegante em vez de inventar dados.

## Checklist de Finalização

- [ ] Sinopse tem 3 parágrafos?
- [ ] Categoria é uma das UUIDs acima?
- [ ] O status final do item ficou em `waiting_process`?
