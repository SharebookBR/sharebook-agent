#!/usr/bin/env python3
"""Wrapper to call query_importer_db.py with a SQL argument."""
import sys, subprocess

sql = sys.argv[1] if len(sys.argv) > 1 else "SELECT 1"
result = subprocess.run(
    [sys.executable, "/data/workspace/sharebook-agent/scripts/query_importer_db.py", sql],
    capture_output=True, text=True, timeout=60
)
print(result.stdout, end="")
if result.stderr:
    print(result.stderr, file=sys.stderr, end="")
sys.exit(result.returncode)
