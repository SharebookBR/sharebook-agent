import sys
from pathlib import Path

# Resolve shared operational modules after playbook colocation.
_AGENT_ROOT = next((p for p in Path(__file__).resolve().parents if (p / "AGENTS.md").exists()), None)
if _AGENT_ROOT:
    sys.path.insert(0, str(_AGENT_ROOT / "playbooks" / "_shared" / "scripts"))
    sys.path.insert(0, str(_AGENT_ROOT / "playbooks" / "_shared" / "scripts" / "production"))

from prod_env import pg_rw

conn = pg_rw(dbname="sharebook_importer")
cur = conn.cursor()

# colunas da tabela
cur.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_schema = 'importer' AND table_name = 'sources'
    ORDER BY ordinal_position
""")
print("=== COLUNAS: importer.sources ===")
for row in cur.fetchall():
    print(f"  {row[0]} | {row[1]} | nullable={row[2]}")

# dados
cur.execute('SELECT * FROM importer.sources')
rows = cur.fetchall()
print(f"\n=== DADOS ({len(rows)} sources) ===")
for row in rows:
    print(f"  {row}")

conn.close()
