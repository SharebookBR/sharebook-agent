#!/usr/bin/env python3
"""Query importer schema using RW credentials via SSH heredoc."""
import sys
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
sql = sys.argv[1] if len(sys.argv) > 1 else "SELECT 1"

pg_container = env["SHAREBOOK_PROD_PG_RW_HOST"]
pg_user = env["SHAREBOOK_PROD_PG_RW_USER"]
pg_pass = env["SHAREBOOK_PROD_PG_RW_PASSWORD"]
pg_port = env["SHAREBOOK_PROD_PG_RW_PORT"]

remote_cmd = (
    "docker exec -e PGPASSWORD='{}' -i {} ".format(pg_pass, pg_container)
    + "psql -U {} -d sharebook_importer -p {} ".format(pg_user, pg_port)
    + "-v ON_ERROR_STOP=1 -P pager=off --csv 2>&1 <<'HEREDOC_SQL'\n"
    + "{}\nHEREDOC_SQL".format(sql)
)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(
    env["VPS_SSH_HOST"],
    port=int(env.get("VPS_SSH_PORT", "22")),
    username=env["VPS_SSH_USER"],
    password=env["VPS_SSH_PASSWORD"],
    timeout=15
)

stdin, stdout, stderr = client.exec_command(remote_cmd, timeout=30)
exit_code = stdout.channel.recv_exit_status()

out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
if err.strip():
    print(err, file=sys.stderr)
print(out, end="")
sys.exit(exit_code)
