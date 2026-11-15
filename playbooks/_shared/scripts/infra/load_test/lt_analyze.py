"""Análise do teste: requests.jsonl (cliente) + monitor.jsonl (VPS) + run.log (tempos das etapas)."""
import json, os, re, sys
from collections import defaultdict
from datetime import datetime, timezone

D = sys.argv[1]
reqs = [json.loads(l) for l in open(os.path.join(D, "requests.jsonl"), encoding="utf-8")]
mon = [json.loads(l) for l in open(os.path.join(D, "monitor.jsonl"), encoding="utf-8")]


def pct(xs, p):
    if not xs:
        return None
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(p / 100 * (len(xs) - 1))))]


# Janelas das etapas, pelos tempos das próprias requisições.
stages = []
for r in reqs:
    if not stages or stages[-1]["name"] != r["stage"]:
        stages.append({"name": r["stage"], "t0": r["t0"], "t1": r["t0"] + r["ms"]})
    else:
        stages[-1]["t1"] = max(stages[-1]["t1"], r["t0"] + r["ms"])

print("== CLIENTE (origem externa) ==")
print(f"{'etapa':14} {'tipo':5} {'n':>6} {'200':>6} {'503':>6} {'outros':>6} {'err':>4}  {'p50/p95 200 ms':>16}  {'p50/p95 503 ms':>16}  RA  {'MB/s':>5}")
tot = defaultdict(int)
for s in stages:
    for kind in ("load", "probe"):
        rs = [r for r in reqs if r["stage"] == s["name"] and r["kind"] == kind]
        if not rs:
            continue
        ok = [r["ms"] for r in rs if r["status"] == 200]
        r503 = [r for r in rs if r["status"] == 503]
        other = [r for r in rs if r["status"] not in (200, 503, 0)]
        err = [r for r in rs if r["status"] == 0]
        ras = sorted({str(r["ra"]) for r in r503})
        secs = max(1, (s["t1"] - s["t0"]) / 1000)
        mbs = sum(r.get("bytes", 0) for r in rs) / secs / 1e6
        f = lambda xs: f"{pct(xs, 50) or '-'}/{pct(xs, 95) or '-'}"
        print(f"{s['name']:14} {kind:5} {len(rs):6} {len(ok):6} {len(r503):6} {len(other):6} {len(err):4}  {f(ok):>16}  {f([r['ms'] for r in r503]):>16}  {','.join(ras) or '-':3} {mbs:5.1f}")
        for k, v in (("200", len(ok)), ("503", len(r503)), ("outros", len(other)), ("err", len(err))):
            tot[k] += v
        if other:
            print("     outros status:", sorted({r["status"] for r in other}))
        if err:
            print("     erros:", sorted({r.get("err") for r in err})[:5])
print("TOTAL:", dict(tot), "| Retry-After nos 503:", sorted({str(r["ra"]) for r in reqs if r["status"] == 503}))

print("\n== VPS por etapa (pico) ==")
for s in stages:
    ms = [m for m in mon if s["t0"] / 1000 <= m["t"] <= s["t1"] / 1000]
    if not ms:
        continue
    fe = [m["c"].get("sharebook-frontend", [0, 0, 0]) for m in ms]
    api = [m["c"].get("sharebook-api", [0, 0, 0]) for m in ms]
    io = [m["si_kibs"] + m["so_kibs"] for m in ms]
    run = best = 0
    for v in io:
        run = run + 1 if v > 1000 else 0
        best = max(best, run)
    pg = [m["pg"][0] for m in ms if m.get("pg")]
    print(f"{s['name']:14} cpu máx {max(m['cpu'] for m in ms):5.1f}% | swapIO máx {max(io):7.0f} KiB/s seq>1MiB {best:2} | "
          f"swap {max(m['swap_used'] for m in ms) / 2**30:.2f} GiB | front cpu {max(x[2] or 0 for x in fe):5.0f}% mem {max(x[0] for x in fe) / 2**20:5.0f} MiB | "
          f"api cpu {max(x[2] or 0 for x in api):4.0f}% | PG máx {max(pg) if pg else '-'} | api_err {sum(m.get('api_err', 0) for m in ms if m.get('api_err', 0) > 0)}")

print("\n== MEMÓRIA/SWAP por container: base (1ª amostra) -> pico -> fim ==")
base, last = mon[0], mon[-1]
rows = []
for name in base["c"]:
    series = [m["c"][name] for m in mon if name in m["c"]]
    mem0, sw0 = base["c"][name][0] or 0, base["c"][name][1] or 0
    memp = max(x[0] or 0 for x in series)
    swp = max(x[1] or 0 for x in series)
    memf, swf = (last["c"].get(name) or [0, 0])[:2]
    rows.append((swp - sw0, name, mem0, memp, memf or 0, sw0, swp, swf or 0))
for d, name, mem0, memp, memf, sw0, swp, swf in sorted(rows, key=lambda r: -(r[3] - r[2]))[:10]:
    print(f"{name[:38]:38} RAM {mem0 / 2**20:6.0f} -> {memp / 2**20:6.0f} -> {memf / 2**20:6.0f} MiB | swap {sw0 / 2**20:5.0f} -> {swp / 2**20:5.0f} -> {swf / 2**20:5.0f} MiB")

print("\n== HOST ==")
sw = [m["swap_used"] for m in mon]
print(f"swap usado: início {sw[0] / 2**30:.2f} GiB, pico {max(sw) / 2**30:.2f} GiB (+{(max(sw) - sw[0]) / 2**20:.0f} MiB), fim {sw[-1] / 2**30:.2f} GiB")
print(f"RAM disponível mínima: {min(m['mem_avail'] for m in mon) / 2**30:.2f} GiB (início {mon[0]['mem_avail'] / 2**30:.2f})")

print("\n== Processos com mais swap: primeira x última amostra com 'top' ==")
tops = [m["top"] for m in mon if m.get("top")]
first = {(n, pid): (rss, swp) for n, pid, rss, swp in tops[0]["swap"]}
lastt = {(n, pid): (rss, swp) for n, pid, rss, swp in tops[-1]["swap"]}
for key in list(dict.fromkeys(list(first) + list(lastt)))[:14]:
    a, b = first.get(key, (None, None)), lastt.get(key, (None, None))
    fmt = lambda v: "-" if v is None else f"{v / 2**20:.0f}"
    print(f"{key[0][:20]:20} pid {key[1]:>8} | swap {fmt(a[1]):>5} -> {fmt(b[1]):>5} MiB | rss {fmt(a[0]):>5} -> {fmt(b[0]):>5} MiB")
