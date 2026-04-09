---
name: sharebook-category-organizer
description: Organizar ou reestruturar categorias e subcategorias do Sharebook com foco em descoberta (UX) sem perder curadoria. Use quando o usuário pedir para avaliar categoria superlotada, propor taxonomia, mapear livros para subcategoria, calcular distribuição por subcategoria, ou preparar plano seguro de migração por lote.
---

# Sharebook Category Organizer

## Objetivo
Padronizar organização de categorias quando uma categoria começa a ficar hostil para navegação.

## Fluxo padrão

1. **Diagnosticar volume e recorte**
   - Levantar livros da categoria alvo (preferir recorte `status=Available` + `type=Eletronic` quando o tema for acervo digital).
   - Regra prática de gatilho:
     - `>30` livros: recomendar subcategorização.
     - `>50` livros: subcategorização obrigatória.

2. **Propor taxonomia enxuta**
   - Criar poucas subcategorias, mutuamente claras e com nome amigável.
   - Evitar sobreposição semântica (ex.: “Poesia” vs “Lírica” sem critério explícito).

3. **Mapear livro -> subcategoria candidata**
   - Entregar tabela com duas colunas mínimas:
     - `livro`
     - `possível subcategoria`
   - Em caso ambíguo, escolher a melhor opção editorial e marcar observação curta.

4. **Validar distribuição**
   - Entregar totais por subcategoria para medir concentração.
   - Se uma subcategoria passar de ~40% do conjunto, considerar nova quebra.

5. **Executar migração em lotes (se aprovado)**
   - Não fazer big-bang.
   - Migrar primeiro top títulos (mais desejáveis/visitados), depois cauda longa.
   - Preferir `update` no livro existente; evitar delete+create.

## Guardrails
- Não alterar produção sem confirmação explícita do usuário.
- Antes de criar subcategoria nova, checar se já existe para evitar duplicata semântica.
- Sempre mostrar plano curto antes de executar mudanças em lote.
- Priorizar descoberta do usuário (navegação/escaneabilidade), não perfeccionismo taxonômico.

## Saídas esperadas

### A) Diagnóstico rápido
- total da categoria
- gargalo de descoberta (1–2 linhas)
- proposta de subcategorias

### B) Mapa editorial
Tabela:
- `Livro`
- `Subcategoria sugerida`

### C) Distribuição
Tabela:
- `Subcategoria`
- `Total`
- `%`

### D) Plano de execução
- lote 1 (alta prioridade)
- lote 2 (médio)
- lote 3 (cauda)

## Comandos úteis (operacionais)
- Listar categorias: `python3 sharebook-agent/scripts/sharebook_prod_book.py categories`
- Buscar livro específico: `python3 sharebook-agent/scripts/sharebook_prod_book.py find --title "..." --author "..."`
- Atualizar categoria de livro: `python3 sharebook-agent/scripts/sharebook_prod_book.py update --id <book_id> --category-id <subcategory_id>`

Quando precisar de listagem massiva por categoria, usar script Python rápido no shell com `API_BASE/Book/1/9999` e filtrar por `categoryId`.
