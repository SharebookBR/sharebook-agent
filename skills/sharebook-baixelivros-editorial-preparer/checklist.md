# Checklist do Preparador Editorial

## Entrada
- [ ] item está em `waiting_editor` ou `editing`
- [ ] página original do item identificada
- [ ] conexão com PostgreSQL do importer ok

## Curadoria
- [ ] li a fonte original
- [ ] confirmei/corrigi autor
- [ ] escolhi categoria folha
- [ ] escrevi sinopse final com 3 parágrafos
- [ ] mantive fidelidade à obra
- [ ] não inventei contexto sem base

## Capa
- [ ] capa existente reaproveitada, ou
- [ ] capa externa definida em `planned_cover_url`, ou
- [ ] decisão consciente de resolver a capa antes da publicação
- [ ] não usei API de imagem da OpenAI sem confirmação explícita do Raffa

## Saída
- [ ] `planned_author` preenchido
- [ ] `planned_category_id` preenchido
- [ ] `planned_synopsis` preenchido
- [ ] `planned_cover_url` preenchido se houver capa
- [ ] item salvo em `waiting_process`

## Anti-autoengano
- [ ] não usei categoria pai
- [ ] não escrevi sinopse genérica
- [ ] não empurrei item incompleto para publicação
