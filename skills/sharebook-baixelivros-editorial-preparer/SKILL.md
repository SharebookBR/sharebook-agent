---
name: sharebook-baixelivros-editorial-preparer
description: Prepara editorialmente itens do importer, especialmente `baixelivros_infantil`, quando estão em `waiting_editor` ou `editing`. Use para validar autor, escolher categoria folha, escrever sinopse final de 3 parágrafos e liberar o item para `waiting_process` no importer.
---

# Sharebook BaixeLivros Editorial Preparer

Curadoria editorial. Só isso.

## Quando usar

Use esta skill quando um item do importer precisar de preparação editorial antes da publicação, especialmente em:

- `waiting_editor`
- `editing`
- `waiting_process` com lacuna editorial real

Se o problema for técnico, duplicata, cron, triagem mecânica ou publicação, usar a skill do importer, não esta.

## Fonte da verdade

- página original do item
- árvore de categorias do Sharebook
- estado atual no PostgreSQL do importer

Wikipedia pode ajudar, mas é opcional.
Se não existir ou não ajudar, não inventar contexto.

## O que esta skill deve entregar

Antes de sair daqui, o item precisa ter:

- `planned_author`
- `planned_category_id`
- `planned_synopsis`
- opcionalmente `planned_cover_url`, se houver capa escolhida externamente
- status final em `waiting_process`

## Regras editoriais que importam

### 1. Fonte primeiro

Ler a página original com atenção.
Não assumir autor, gênero ou contexto por associação preguiçosa.

### 2. Categoria sempre folha

Nunca deixar item em categoria pai.
Se a categoria tiver `children`, ela está proibida como destino final.

### 3. Sinopse final

A sinopse deve ter:
- 3 parágrafos
- tom envolvente
- fidelidade à obra
- sem clichê vazio
- sem invenção factual

### 4. Idioma

O padrão editorial é publicar em português.
Sem aprovação explícita do Raffa, não liberar item em inglês para publicação.

### 5. Capa

Se a capa já existe e está boa, reaproveitar.
Se for preciso gerar capa:
- priorizar fluxo ChatGPT web quando a qualidade importar
- **não usar API de imagem da OpenAI sem confirmação explícita do Raffa**

## Fluxo curto

1. Buscar item no importer
2. Ler a página da fonte
3. Corrigir/confirmar autor
4. Escolher categoria folha
5. Escrever sinopse final de 3 parágrafos
6. Registrar capa, se houver
7. Atualizar PostgreSQL
8. Fechar o item em `waiting_process`

## Atualização no PostgreSQL

Campos centrais:
- `planned_author`
- `planned_category_id`
- `planned_synopsis`
- `planned_cover_url` (quando existir)
- `planned_cover_mode = 'source'` quando a capa vier de arquivo externo reaproveitado/gerado fora do worker
- `status = 'waiting_process'`

## Checklist mínimo

- [ ] li a página original
- [ ] autor validado
- [ ] categoria folha escolhida
- [ ] sinopse com 3 parágrafos
- [ ] sinopse fiel à obra
- [ ] capa resolvida ou conscientemente pendente
- [ ] item salvo no PostgreSQL
- [ ] status final em `waiting_process`

## Erros comuns

- assumir autor por associação de nome
- assumir gênero pela fama do autor
- usar categoria pai por preguiça
- escrever sinopse genérica
- empurrar item incompleto para publicação
- inventar contexto histórico/literário sem base suficiente

## Relação com o importer

- esta skill cuida do julgamento editorial
- a skill `sharebook-public-ebook-importer` cuida da operação do importer
- quando terminar aqui, o item deve estar pronto para `publish-once`
