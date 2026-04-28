#!/usr/bin/env python3
"""Check importer queue status via SSH."""
import sys, json, textwrap
from pathlib import Path

import paramiko

def parse_env(path):
    data = {}
    for raw in Path(path).read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip()
    return data

env = parse_env("/data/workspace/sharebook-agent/.env")

ssh_host = env["VPS_SSH_HOST"]
ssh_port = int(env.get("VPS_SSH_PORT", "22"))
ssh_user = env["VPS_SSH_USER"]
ssh_pass = env["VPS_SSH_PASSWORD"]
pg_container = env["SHAREBOOK_PROD_PG_RO_HOST"]
pg_user = env["SHAREBOOK_PROD_PG_RO_USER"]
pg_pass = env["SHAREBOOK_PROD_PG_RO_PASSWORD"]
pg_port = env["SHAREBOOK_PROD_PG_RO_PORT"]

sql = sys.argv[1] if len(sys.argv) > 1 else "SELECT 1"

# Use heredoc to avoid quoting issues with special chars
cmd = (
    f"docker exec -e PGPASSWORD='{pg_pass}' -i {pg_container} "
    f"psql -U {pg_user} -d sharebook_importer -p {pg_port} "
    f"-v ON_ERROR_STOP=1 -P pager=off --csv 2>/dev/null <<'SQLEOF'\n{sql}\nSQLEOF"
)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(ssh_host, port=ssh_port, username=ssh_user, password=ssh_pass, timeout=15)
_, stdout, stderr = client.exec_command(cmd, timeout=60)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
if out.strip():
    print(out.rstrip())
if err.strip():
    print(err.rstrip(), file=sys.stderr)
sys.exit(stdout.channel.recv_exit_status())
