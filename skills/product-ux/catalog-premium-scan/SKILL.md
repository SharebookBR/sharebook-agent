---
name: catalog-premium-scan
description: Analisa livros publicados recentemente no Sharebook para revisão editorial diária de catálogo. Use quando o usuário pedir um scan premium do catálogo, quiser a lista dos livros publicados nas últimas 24 horas com título, autor, categoria pai, categoria folha e data/hora de criação, e também uma shortlist dos itens com maior potencial de valorizar o catálogo.
---

# Catalog Premium Scan

Skill para o ritual diário de revisão do catálogo recém-publicado.

## Quando usar

Use esta skill quando o pedido for algo como:
- `catalog-premium-scan`
- `premium scan do catálogo`
- `quais livros foram publicados de ontem pra hoje?`
- `quais desses mais valorizam o catálogo?`
- pedidos de tabela dos publicados recentes + shortlist premium

## Objetivo

Entregar, em uma resposta só:
1. tabela dos livros publicados recentemente
2. leitura editorial curta
3. shortlist `premium` dos itens com maior potencial de valor de catálogo

## Workflow

1. Ler primeiro a skill `sharebook-agent/skills/engineering/sharebook-postgres-ro/SKILL.md`.
2. Consultar o importer (`importer.queue_items`) para descobrir os `sharebook_book_id` marcados como `done` na janela pedida.
3. Consultar o banco read-only de produção do Sharebook para buscar, para esses IDs:
   - título
   - autor
   - data/hora de criação
   - categoria folha
   - categoria pai
4. Ordenar por data/hora de criação em ordem decrescente.
5. Montar a tabela.
6. Ler a lista com critério editorial e destacar os premiums.

## Janela padrão

- Se o usuário não disser outra coisa, usar `últimas 24 horas`.
- Se o usuário disser `hoje`, usar desde `00:00` no timezone `America/Sao_Paulo`.
- Nunca exibir horário em UTC para o Raffa.

## Critério editorial para premiums

Priorizar livros que aumentam percepção de catálogo, não só volume.

Sinais positivos:
- clássico forte
- mito, lenda, folclore ou repertório cultural durável
- título com força literária
- autor com peso ou assinatura marcante
- obra com alto potencial de capa e sinopse
- peça que dá sensação de acervo mais nobre, menos genérico

Sinais de menor prioridade premium:
- livro apenas funcional ou pedagógico sem brilho claro
- infantil simpático mas intercambiável
- título fraco ou genérico demais

## Saída padrão

Responder nesta ordem:

### 1. Tabela
Colunas:
- Título
- Autor
- Categoria pai
- Categoria folha
- Data/hora de criação

### 2. Premiums
Usar este formato enxuto:
- `Premium máximo:` lista curta (até 5)
- `Bons secundários:` opcional, se fizer sentido
- `Leitura:` 2 a 5 linhas com leitura editorial honesta

## Guardrails

- Não inventar prestígio onde não existe.
- Não tratar todo infantil como premium só porque é novo.
- Se a lista for muito grande, mostrar a tabela completa quando couber e manter a análise premium curta.
- Se houver ambiguidade em categoria ou autor, preferir o dado do banco de produção.
- Se faltar contexto para julgar um item com confiança, dizer isso brevemente em vez de forçar ranking falso.
