#!/bin/bash
# Triage batch: processa ate 5 itens em waiting_triage usando subagentes
# Executado pelo cron do OpenClaw a cada 5 minutos

DSN=$(grep IMPORTER_DB_DSN /data/workspace/sharebook-ebook-importer/.env | cut -d= -f2-)

# Contar quantos em waiting_triage
COUNT=$(psql "$DSN" -t -A -c "SELECT COUNT(*) FROM importer.queue_items WHERE status = 'waiting_triage';")

if [ "$COUNT" -eq 0 ]; then
  echo "Nenhum item na fila. Pulando."
  exit 0
fi

echo "Fila tem $COUNT itens. Proximo ciclo de subagentes cuidara."
# O subagente e disparado pelo OpenClaw via cron job
