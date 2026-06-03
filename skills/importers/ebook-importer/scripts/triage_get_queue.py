#!/usr/bin/env python3
"""Get waiting_triage items from the importer queue via SSH."""
import sys
sys.path.insert(0, "/data/workspace/sharebook-agent/scripts")

# Just exec the query_triage_rw module directly
import subprocess
import json

sql = "SELECT qi.id, qi.title, qi.author, qi.source_url, s.name as source_name FROM importer.queue_items qi JOIN importer.sources s ON s.id = qi.source_id WHERE qi.status = 'waiting_triage' ORDER BY qi.id LIMIT 5;"

result = subprocess.run(
    [sys.executable, "/data/workspace/sharebook-agent/scripts/importer/query_triage_rw.py", sql],
    capture_output=True, text=True, timeout=60
)

print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("EXIT:", result.returncode)
