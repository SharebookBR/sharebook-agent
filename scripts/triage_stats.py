#!/usr/bin/env python3
"""Get pipeline stats from importer queue."""
import sys, subprocess

sql = """
SELECT status, COUNT(*) as total
FROM importer.queue_items
GROUP BY status
ORDER BY status;
"""

result = subprocess.run(
    [sys.executable, "/data/workspace/sharebook-agent/scripts/query_triage_rw.py", sql],
    capture_output=True, text=True, timeout=60
)
print(result.stdout)
if result.stderr.strip():
    print("STDERR:", result.stderr)
