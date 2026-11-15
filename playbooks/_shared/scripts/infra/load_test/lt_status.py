"""Status parcial amigável do teste de carga (markdown)."""
import json, os, sys, time

D = sys.argv[1]
STAGES = [("humano c=3", 60), ("humano c=6", 60), ("humano c=12", 60), ("humano c=24", 60),
          ("bot c=5", 60), ("bot c=15", 60), ("bot c=50", 60), ("bot c=200", 30), ("recuperacao", 180)]
TOTAL = sum(s for _, s in STAGES)


def load(name):
    p = os.path.join(D, name)
    if not os.path.exists(p):
        return []
    out = []
    for line in open(p, encoding="utf-8"):
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out


reqs, mon = load("requests.jsonl"), load("monitor.jsonl")
runlog = open(os.path.join(D, "run.log"), encoding="utf-8").read() if os.path.exists(os.path.join(D, "run.log")) else ""
gatilho = next((l.split("GATILHO: ")[1] for l in runlog.splitlines() if "GATILHO:" in l), None)
fim = "FIM." in runlog

feitas = {r["stage"] for r in reqs}
atual = reqs[-1]["stage"] if reqs else None
idx = next((i for i, (n, _) in enumerate(STAGES) if n == atual), -1)
decorrido = sum(s for _, s in STAGES[:idx]) if idx >= 0 else 0
if idx >= 0:
    t_ini = min(r["t0"] for r in reqs if r["stage"] == atual)
    decorrido += min(STAGES[idx][1], (time.time() * 1000 - t_ini) / 1000)
frac = 1.0 if fim else decorrido / TOTAL
bar = "█" * round(frac * 20) + "░" * (20 - round(frac * 20))


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(p / 100 * (len(xs) - 1))))] if xs else None


estado = "🛑 PARADO POR GATILHO" if gatilho else ("✅ CONCLUÍDO" if fim else "🟢 RODANDO")
print(f"### Teste de carga — {estado}")
print(f"`{bar}` **{frac * 100:.0f}%** · etapa atual: **{atual or 'base'}**")
if gatilho:
    print(f"\n> Gatilho: {gatilho}")

print("\n| Etapa | Req | ✅ 200 | 🚦 503 | ❌ erro | p95 200 | p95 503 |")
print("|---|---:|---:|---:|---:|---:|---:|")
for nome, _ in STAGES:
    rs = [r for r in reqs if r["stage"] == nome]
    if not rs:
        continue
    ok = [r["ms"] for r in rs if r["status"] == 200]
    q = [r["ms"] for r in rs if r["status"] == 503]
    err = sum(1 for r in rs if r["status"] not in (200, 503))
    marca = " ⏳" if nome == atual and not fim else ""
    f = lambda v: "—" if v is None else f"{v:,} ms".replace(",", ".")
    print(f"| {nome}{marca} | {len(rs):,} | {len(ok):,} | {len(q):,} | {err} | {f(pct(ok, 95))} | {f(pct(q, 95))} |".replace(",", "."))

if mon:
    m = mon[-1]
    io = m["si_kibs"] + m["so_kibs"]
    sw0 = mon[0]["swap_used"]
    dsw = (m["swap_used"] - sw0) / 2**20
    c = m["c"]
    run = best = 0
    for x in mon:
        v = x["si_kibs"] + x["so_kibs"]
        run = run + 1 if v > 1000 else 0
        best = max(best, run)
    pgs = [x["pg"][0] for x in mon if x.get("pg")]
    errs = sum(x.get("api_err", 0) for x in mon if x.get("api_err", 0) > 0)
    sinal = lambda ok: "🟢" if ok else "🟡"
    print("\n**VPS agora** (gatilho entre parênteses)")
    print(f"- {sinal(m['cpu'] < 90)} CPU do host **{m['cpu']:.0f}%** · frontend {c['sharebook-frontend'][2] or 0:.0f}% · API {c['sharebook-api'][2] or 0:.0f}% (90% por 30 s)")
    print(f"- {sinal(best < 10)} Swap I/O **{io:,.0f} KiB/s** · maior sequência acima de 1 MiB/s: {best} s (10 s)".replace(",", "."))
    print(f"- {sinal(dsw < 300)} Swap usado **{m['swap_used'] / 2**30:.2f} GiB** ({dsw:+.0f} MiB desde o início) (+300 MiB)")
    print(f"- {sinal(errs == 0)} Erros 500/Npgsql na API: **{errs}** · Postgres: **{pgs[-1] if pgs else '—'}** conexões, máx {max(pgs) if pgs else '—'} (80)")
