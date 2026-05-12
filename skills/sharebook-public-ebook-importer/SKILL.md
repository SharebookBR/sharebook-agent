---
name: sharebook-public-ebook-importer
description: Opera o importer de ebooks públicos/gratuitos do Sharebook. Use quando precisar sincronizar fila, rodar triagem mecânica, preparar publicação, publicar/aprovar ebooks, revisar status canônico, ajustar cron local do importer ou diagnosticar a operação do repositório sharebook-ebook-importer.
---

# Sharebook Public Ebook Importer

Skill única do importer. Sem teatro.

## Quando usar

Use esta skill para qualquer operação do `sharebook-ebook-importer`, especialmente:

- sincronizar source/fila
- rodar `triage-once`
- rodar `publish-once`
- revisar `retry_later`, `error`, `waiting_editor`, `waiting_process`
- instalar, remover ou auditar o cron local
- diagnosticar logs e estado do importer

## Fonte da verdade

A fonte da verdade operacional agora é o repositório:

- `/data/workspace/sharebook-ebook-importer/README.md`
- `/data/workspace/sharebook-ebook-importer/cli.py`
- `/data/workspace/sharebook-ebook-importer/setup-importer-cron.sh`

Se esta skill divergir do código/README do importer, o importer manda.

## Guardrails curtos

- PostgreSQL é a única fonte da verdade
- não inventar status fora do conjunto canônico
- `duplicate` não é `done`
- `triage_rejected` conta como trabalho concluído, não como erro
- se falha temporária já cabe em `retry_later`, não usar `error`
- se faltar editorial, devolver para `waiting_editor`, não mascarar como erro técnico
- não usar cron agentic do OpenClaw para este fluxo quando o objetivo for economizar tokens

## Status canônico

- `waiting_triage`
- `triaging`
- `triage_rejected`
- `waiting_editor`
- `editing`
- `waiting_process`
- `processing`
- `done`
- `retry_later`
- `source_blocked`
- `duplicate`
- `error`

## Workflow real atual

### 1. Triagem mecânica

Comando:

```bash
cd /data/workspace/sharebook-ebook-importer
set -a && . /data/workspace/sharebook-agent/.env && set +a
python cli.py triage-once --source baixelivros_infantil
```

O `triage_worker.py` deve:
- pegar item em `waiting_triage`
- extrair da fonte via `extractors/`
- validar PDF real
- detectar bloqueios óbvios
- encaminhar para `waiting_editor`, `triage_rejected`, `source_blocked` ou `retry_later`

Não tentar fazer curadoria sofisticada aqui.

### 2. Publicação/aprovação

Comando:

```bash
cd /data/workspace/sharebook-ebook-importer
set -a && . /data/workspace/sharebook-agent/.env && set +a
python cli.py publish-once --source baixelivros_infantil
```

O fluxo de publicação deve:
- pegar item em `waiting_process`
- validar plano editorial
- checar duplicata em produção
- criar e aprovar ebook
- marcar `done`, `duplicate`, `waiting_editor`, `retry_later` ou `error`

## Regra editorial que continua viva

- categoria final deve ser sempre folha
- sinopse final deve ter 3 parágrafos
- idioma padrão de publicação: português
- se o plano editorial estiver incompleto, o item volta para `waiting_editor`

## Capa e custo

- **proibido gerar imagens via API da OpenAI no fluxo Sharebook sem confirmação explícita do Raffa**
- se a capa da fonte servir, preferir reaproveitar
- se precisar gerar sem custo de API, usar alternativas locais já aprovadas

## Cron local do importer

Comandos canônicos:

```bash
cd /data/workspace/sharebook-ebook-importer
bash setup-importer-cron.sh install
bash setup-importer-cron.sh status
bash setup-importer-cron.sh remove
bash setup-importer-cron.sh start-daemon
```

Regras:
- instalar via script, não por `crontab -e` solto
- logs ficam em `var/logs/`
- lock/estado local ficam em `var/state/`
- ao revisar incidente, olhar nesta ordem:
  1. `crontab -l`
  2. `var/logs/importer-cron.log`
  3. `var/logs/importer.jsonl`
  4. estado no Postgres (`importer.runs`, `importer.queue_items`)

## Diagnóstico mínimo

Antes de culpar o fluxo:
- validar `IMPORTER_DB_DSN`
- se reclamar que faltam `importer.queue_items`, `importer.sources` ou `importer.runs`, a conexão está no banco errado
- se houver item preso em `processing`, `triaging` ou `editing`, destravar conscientemente
- confiar no README do importer mais do que em memória antiga

## Handoff com curadoria

`waiting_editor` e `editing` continuam sendo território natural da preparação editorial humana/LLM.

Esta skill não substitui julgamento curatorial. Ela só descreve a operação do importer.