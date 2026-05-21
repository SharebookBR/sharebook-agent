#!/usr/bin/env python3
"""Generate 6 cover variations for the Beej's Networking Guide."""
import subprocess, json, sys

script = 'sharebook-agent/skills/importers/sharebook-ebook-foundation-preparer/scripts/cover_generate.py'
title = "Guia Beej's Para Programação em Rede"
author = "Brian Beej Jorgensen Hall"

results = []
for i in range(1, 7):
    outpath = f"sharebook-ebook-importer/triage-downloads/beej-var-{i}.jpg"
    result = subprocess.run(
        ['python3', script, title, author, '-o', outpath, '--json'],
        capture_output=True, text=True, timeout=30
    )
    try:
        data = json.loads(result.stdout) if result.stdout else {}
        data['var'] = i
        data['stderr'] = result.stderr[:300] if result.stderr else ''
        results.append(data)
    except:
        results.append({'var': i, 'error': result.stderr[:500], 'stdout': result.stdout[:500]})
    print(f"VAR {i}: palette={data.get('palette','?')} output={data.get('output','?')}")

print("\n\n=== SUMMARY ===")
for r in results:
    print(f"Var {r['var']}: palette={r.get('palette','?')}, bg={r.get('bg','?')}, fg={r.get('fg','?')}, accent={r.get('accent','?')}")
