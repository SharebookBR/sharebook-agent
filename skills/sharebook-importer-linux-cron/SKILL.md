---
name: sharebook-importer-linux-cron
description: Instala, remove, audita e reaplica o cron Linux do worker `sharebook-ebook-importer` dentro do container do OpenClaw, sem gastar tokens com cron agentic. Use quando precisar configurar ou restaurar o agendamento local do importer, validar crontab após update de imagem, trocar frequência, revisar logs, ou garantir que o setup continue reidempotente e documentado.
---

# Sharebook Importer Linux Cron

Usar cron Linux aqui é escolha de custo, não acidente. Tratar como infra local simples, reproduzível e sem mística.

## Workflow

1. Tratar o código do worker como fonte da verdade. Se README/PLAYBOOK divergirem, corrigir ou remover.
2. Operar a partir de `sharebook-ebook-importer/setup-importer-cron.sh`.
3. Antes de instalar, validar:
   - `python3` disponível
   - `cron` ou `crond` disponível
   - `crontab` disponível
   - `flock` disponível
   - arquivo de env escolhido existe (`.env.postgres` por padrão)
4. Instalar cron via script reidempotente, nunca por edição manual solta no `crontab -e`.
5. Persistir logs em `sharebook-ebook-importer/var/logs/` e lock em `sharebook-ebook-importer/var/state/`.
6. Ao revisar incidente, verificar nesta ordem:
   - `crontab -l`
   - `var/logs/importer-cron.log`
   - `var/logs/importer.jsonl`
   - estado no Postgres `importer.runs` / `importer.queue_items`
7. Se a imagem do OpenClaw for atualizada, reaplicar o setup pelo script e validar a linha instalada.

## Comandos canônicos

Bootstrap do pacote no Debian quando necessário:

```bash
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y cron
```

Instalar com frequência padrão de 30 min, apenas de 00:00 até 08:00 no horário de São Paulo:

```bash
cd /data/workspace/sharebook-ebook-importer
bash setup-importer-cron.sh install
```

Instalar com cron customizado:

```bash
cd /data/workspace/sharebook-ebook-importer
CRON_TZ=America/Sao_Paulo CRON_SCHEDULE="*/15 0-8 * * *" bash setup-importer-cron.sh install
```

Remover a entrada gerenciada:

```bash
cd /data/workspace/sharebook-ebook-importer
bash setup-importer-cron.sh remove
```

Subir só o daemon de cron:

```bash
cd /data/workspace/sharebook-ebook-importer
bash setup-importer-cron.sh start-daemon
```

Ver status local:

```bash
cd /data/workspace/sharebook-ebook-importer
bash setup-importer-cron.sh status
```

Rodar teste manual sem esperar o cron:

```bash
cd /data/workspace/sharebook-ebook-importer
set -a && . ./.env.postgres && set +a
PYTHONPATH=src python3 -m sharebook_ebook_importer.cli run-once
```

## Guardrails

- Não usar cron do Gateway/OpenClaw para esse worker quando o objetivo explícito for economizar tokens.
- Não depender de arquivos dentro da imagem para restaurar o cron; usar apenas conteúdo persistido no workspace.
- Não editar a crontab manualmente se o script puder fazer o trabalho.
- Manter a entrada marcada por bloco gerenciado, para evitar duplicidade e drift.
- Se mudar caminho, env ou frequência, atualizar junto a documentação do importer.
