---
name: category-organizer
description: Organizar, simplificar ou reestruturar categorias e subcategorias do Sharebook com foco em descoberta. Use quando o usuário pedir para repensar taxonomia, dividir categoria superlotada, mapear livros para subcategoria, migrar livros em lote, aposentar categorias confusas, ou corrigir classificação editorial em produção.
---

# Sharebook Category Organizer

## Objetivo

Melhorar descoberta de livros no Sharebook.

A taxonomia deve ajudar o usuário a encontrar algo que ele quer ler.
Não precisa parecer catálogo acadêmico.
Não precisa preservar categorias só porque "faz sentido" teoricamente.

## Princípios editoriais

1. **Descoberta > ortodoxia**
   - O que importa é intenção do usuário e facilidade de navegação.
   - Evitar decisões guiadas por catalogação acadêmica quando isso piorar descoberta.

2. **Efeito de leitura > forma textual**
   - Preferir classificar por experiência editorial dominante:
     - psicológico
     - social
     - moral/ético
     - trágico
     - satírico/irônico
     - comédia
     - aventura
     - fantasia
     - etc.
   - Evitar categorias baseadas só em forma, como “narrativas curtas”, “dramaturgia”, “peça”, quando isso não ajuda a descoberta.
   - Regra útil validada:
     - `Drama Satírico / Irônico` = sátira, crítica, acidez, ironia social ou política
     - `Ficção > Comédia` = leitura leve, espirituosa, humor relacional, prazer de leitura mais solto

3. **Amor é território protegido**
   - A categoria raiz `Amor` tem prioridade como decisão de negócio.
   - Se uma obra pende claramente para romance amoroso, não forçar encaixe em `Drama` ou outra árvore só por tradição literária.

4. **Categoria vazia ou confusa pode morrer**
   - Se uma categoria gera ruído, sobreposição ou pouca utilidade prática, pode ser aposentada.
   - Não manter duplicatas semânticas ou categorias redundantes por apego histórico.

5. **Taxonomia boa é curta e clara**
   - Poucas subcategorias, nomes legíveis e critérios distinguíveis.
   - Evitar misturar no mesmo nível:
     - tema
     - tom
     - forma
     - período

## Fluxo padrão

1. **Diagnosticar a categoria alvo**
   - Levantar livros da categoria.
   - Preferir recorte explícito quando fizer sentido (ex.: físicos/digitais, disponíveis, etc.).
   - Medir volume.

2. **Detectar problema editorial**
   Perguntas práticas:
   - a categoria está superlotada?
   - mistura forma com tema?
   - conflita com outra categoria forte?
   - tem duplicidade?
   - ajuda descoberta de verdade?

3. **Propor taxonomia enxuta**
   - Criar poucas subcategorias.
   - Dar nomes orientados a descoberta.
   - Se possível, reaproveitar categorias já existentes.
   - Antes de criar nova categoria, sempre checar duplicidade.

4. **Mapear livro -> destino sugerido**
   - Para cada livro, apontar categoria de destino.
   - Em ambiguidade real, escolher uma destas saídas:
     - escalar para decisão manual
     - segurar sem mover
     - mover só os casos de alta confiança

5. **Executar por lotes**
   - Preferir migrar primeiro o que está claro.
   - Deixar blockers separados.
   - Update no livro existente, sem delete/create.

6. **Limpar legado**
   - Se restar categoria `- old`, duplicada ou vazia, validar e remover.

## Heurísticas práticas

### Quando subcategorizar
- `>30` livros: vale propor subcategorias.
- `>50` livros: subcategorização tende a ser obrigatória.

### Quando NÃO usar categoria por forma
Evitar subcategoria baseada só em forma quando o objetivo é descoberta, por exemplo:
- narrativas curtas
- teatro & dramaturgia
- peça teatral

Só usar se houver valor claro para a navegação real do usuário.

### Comédia vs Drama Satírico / Irônico
Usar esta distinção quando houver dúvida:
- **`Ficção > Comédia`**
  - humor leve
  - mal-entendidos
  - relações humanas
  - ironia suave
  - tom mais agradável ou agridoce
- **`Drama > Drama Satírico / Irônico`**
  - crítica de costumes
  - sátira social/política
  - ironia mais ácida
  - humor como ataque, desconforto ou corrosão

### Quando escalar em vez de mover
Escalar se houver:
- conflito com `Amor`
- obra muito fora do eixo da árvore atual
- antologia/coletânea difícil de resumir em um único destino
- dúvida real entre duas árvores fortes

## Guardrails

- Não alterar produção sem confirmação explícita do usuário.
- Em migração por lote aprovada, pode executar os moves seguros sem pedir confirmação livro a livro.
- Antes de remover categoria, validar que está vazia.
- Antes de criar categoria nova, verificar se já existe equivalente.
- Se houver blocker editorial real, não chutar.
- Para diagnóstico, preferir primeiro **query read-only no Postgres** em vez de sair batendo na API sem necessidade.

## Operação no OpenClaw

### Exec de scripts Python
- No OpenClaw, o preflight de `exec` pode bloquear **interpretador + shell complexo**.
- Preferir sempre comando direto com `workdir` definido.
- Exemplo certo:
  - `python3 scripts/production/sharebook_prod_book.py categories`
- Evitar:
  - `cd ... && python3 ...`
  - pipes, redirecionamentos e shell enfeitado no mesmo comando
- Se precisar de script auxiliar, escrever um arquivo temporário curto e rodar com `python3 <arquivo>`.

### Fonte de verdade para diagnóstico
- Para medir volume, detectar duplicidade, checar categoria pai/filha e mapear livros, preferir **Postgres produção read-only** quando isso for mais rápido e confiável.
- Usar API principalmente para:
  - validar comportamento exposto
  - criar categoria (`POST /api/Category`)
  - mover livro (`PUT /api/Book/{id}` via script utilitário)
- Regra prática:
  - **RO no banco para entender**
  - **API para escrever**

### Criação de subcategoria
- Antes de criar, listar a árvore atual e confirmar duplicidade por `name + parentCategoryId`.
- Para criar categoria filha, usar `POST /api/Category` com:
  - `Name`
  - `ParentCategoryId`
  - `Order` (quando fizer sentido para exibição)
- Validar no retorno se a categoria nasceu com o `parentCategoryId` correto.

## Saídas esperadas

### A) Diagnóstico rápido
- total da categoria
- problema editorial em 1–3 linhas
- proposta de estrutura

### B) Mapa editorial
Tabela mínima:
- livro
- destino sugerido
- observação curta (se necessário)

### C) Distribuição
Tabela:
- categoria destino
- total
- %

### D) Execução
- quantos foram movidos
- quantos ficaram pendentes
- blockers
- categorias legadas que podem ser removidas

## Regras que valem ouro

- **Descoberta vence taxonomia bonita**
- **Forma textual não manda sozinha**
- **`Amor` não deve ser atropelada**
- **Duplicata sem ganho deve morrer**
- **Mover o claro primeiro é melhor que travar tudo**

## Comandos úteis

```bash
python3 sharebook-agent/scripts/production/sharebook_prod_book.py categories
```

```bash
python3 sharebook-agent/scripts/production/sharebook_prod_book.py find --title "..." --author "..."
```

```bash
python3 sharebook-agent/scripts/production/sharebook_prod_book.py update --id <book_id> --category-id <subcategory_id>
```

Para volume maior, preferir Postgres produção com consulta RO e execução RW controlada.
