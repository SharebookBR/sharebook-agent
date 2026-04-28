#!/bin/bash
# Wrapper that SSHs and runs psql with proper quoting
set -e

SSH_HOST="212.85.23.202"
SSH_PORT="22"
SSH_USER="root"
SSH_PASS="tI6qnc/C;,w-SDF95YP#"
PG_CONTAINER="fgsgwsckccgk8sccc4gg0gg0"
PG_USER="sharebook_ai_ro"
PG_PASS="3-nbj0bw3STVkxlcCeEO2ZFwtvyn"
PG_PORT="5432"
DB="sharebook_importer"
SQL="$1"

# Build a safe command
CMD="docker exec -e PGPASSWORD='${PG_PASS}' -i ${PG_CONTAINER} psql -U ${PG_USER} -d ${DB} -p ${PG_PORT} -v ON_ERROR_STOP=1 -P pager=off -t"

sshpass -p "${SSH_PASS}" ssh -o StrictHostKeyChecking=no -p ${SSH_PORT} ${SSH_USER}@${SSH_HOST} "${CMD} -c '${SQL}'"
