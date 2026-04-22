---
name: sharebook-category-organizer
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
     - aventura
     - fantasia
     - etc.
   - Evitar categorias baseadas só em forma, como “narrativas curtas”, “dramaturgia”, “peça”, quando isso não ajuda a descoberta.

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
python3 sharebook-agent/scripts/sharebook_prod_book.py categories
```

```bash
python3 sharebook-agent/scripts/sharebook_prod_book.py find --title "..." --author "..."
```

```bash
python3 sharebook-agent/scripts/sharebook_prod_book.py update --id <book_id> --category-id <subcategory_id>
```

Para volume maior, preferir Postgres produção com consulta RO e execução RW controlada.
