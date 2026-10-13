import sys
from pathlib import Path

# Resolve shared operational modules after playbook colocation.
_AGENT_ROOT = next((p for p in Path(__file__).resolve().parents if (p / "AGENTS.md").exists()), None)
if _AGENT_ROOT:
    sys.path.insert(0, str(_AGENT_ROOT / "playbooks" / "_shared" / "scripts"))
    sys.path.insert(0, str(_AGENT_ROOT / "playbooks" / "_shared" / "scripts" / "production"))

from prod_env import pg_ro

conn = pg_ro()
cur = conn.cursor()

cur.execute('SELECT COUNT(*) FROM "Books" WHERE "Type" = 1')
digital = cur.fetchone()[0]

cur.execute('SELECT COUNT(*) FROM "Books" WHERE "Type" = 0')
physical = cur.fetchone()[0]

cur.execute('SELECT COUNT(*) FROM "Books"')
total = cur.fetchone()[0]

print(f"Digital:  {digital}")
print(f"Físico:   {physical}")
print(f"Total:    {total}")

conn.close()
