#!/usr/bin/env python3
"""Monitor do teste de carga: roda no host da VPS e imprime uma linha JSON por segundo.

Host: CPU, RAM, swap usado, swap I/O (pswpin/pswpout). Por container (cgroup v2):
RAM, swap e CPU. A cada 5 s: top processos por RSS e por swap, saúde/restarts de
frontend e API, e erros 500/Npgsql no log da API. A cada 2 s: conexões do Postgres.
"""
import json, os, subprocess, sys, time

PG = "fgsgwsckccgk8sccc4gg0gg0"
WATCH = ("sharebook-frontend", "sharebook-api")


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()


def containers():
    out = {}
    for line in sh("docker ps --no-trunc --format '{{.ID}} {{.Names}}'").splitlines():
        cid, name = line.split(" ", 1)
        path = f"/sys/fs/cgroup/system.slice/docker-{cid}.scope"
        if os.path.isdir(path):
            out[name] = path
    return out


def readint(path):
    try:
        with open(path) as f:
            return int(f.read().split()[0])
    except Exception:
        return None


def cpu_usec(path):
    try:
        with open(path + "/cpu.stat") as f:
            for line in f:
                if line.startswith("usage_usec"):
                    return int(line.split()[1])
    except Exception:
        return None


def host_cpu():
    with open("/proc/stat") as f:
        v = list(map(int, f.readline().split()[1:]))
    idle = v[3] + v[4]
    return sum(v), idle


def meminfo():
    m = {}
    with open("/proc/meminfo") as f:
        for line in f:
            k, v = line.split(":")
            m[k] = int(v.split()[0]) * 1024
    return m


def vmstat():
    d = {}
    with open("/proc/vmstat") as f:
        for line in f:
            k, v = line.split()
            if k in ("pswpin", "pswpout"):
                d[k] = int(v)
    return d


def top_procs(n=10):
    rows = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            with open(f"/proc/{pid}/status") as f:
                st = dict(line.split(":", 1) for line in f if ":" in line)
            rss = int(st.get("VmRSS", "0 kB").split()[0]) * 1024
            swp = int(st.get("VmSwap", "0 kB").split()[0]) * 1024
            rows.append((st["Name"].strip(), int(pid), rss, swp))
        except Exception:
            continue
    by_rss = sorted(rows, key=lambda r: -r[2])[:n]
    by_swap = sorted(rows, key=lambda r: -r[3])[:n]
    return {"rss": by_rss, "swap": by_swap}


def health():
    out = {}
    for name in WATCH:
        s = sh(f"docker inspect -f '{{{{.State.Health.Status}}}} {{{{.RestartCount}}}} {{{{.State.StartedAt}}}}' {name}")
        out[name] = s
    return out


def api_errors(since):
    logs = sh(f"docker logs --since {since} sharebook-api 2>&1 | grep -c -i -E 'responded 500|NpgsqlException|connection to database|connection pool|canceling statement' || true")
    try:
        return int(logs.splitlines()[-1])
    except Exception:
        return -1


def pg_conns():
    s = sh(f"docker exec {PG} psql -U postgres -At -c \"select count(*), count(*) filter (where state='active') from pg_stat_activity where datname is not null\"")
    try:
        a, b = s.split("|")
        return [int(a), int(b)]
    except Exception:
        return None


def main():
    ctrs = containers()
    prev_cpu = host_cpu()
    prev_vm = vmstat()
    prev_c = {n: cpu_usec(p) for n, p in ctrs.items()}
    prev_t = time.time()
    i = 0
    last_err_check = time.time()
    while True:
        time.sleep(1)
        now = time.time()
        dt = now - prev_t
        tot, idle = host_cpu()
        cpu = 100.0 * (1 - (idle - prev_cpu[1]) / max(1, tot - prev_cpu[0]))
        vm = vmstat()
        si = (vm["pswpin"] - prev_vm["pswpin"]) * 4 / dt
        so = (vm["pswpout"] - prev_vm["pswpout"]) * 4 / dt
        m = meminfo()
        rec = {
            "t": round(now, 3), "cpu": round(cpu, 1),
            "mem_used": m["MemTotal"] - m["MemAvailable"], "mem_avail": m["MemAvailable"],
            "swap_used": m["SwapTotal"] - m["SwapFree"], "si_kibs": round(si, 1), "so_kibs": round(so, 1),
            "load1": float(open("/proc/loadavg").read().split()[0]),
            "c": {},
        }
        for n, p in ctrs.items():
            u = cpu_usec(p)
            pu = prev_c.get(n)
            rec["c"][n] = [readint(p + "/memory.current"), readint(p + "/memory.swap.current"),
                           None if (u is None or pu is None) else round((u - pu) / 1e4 / dt, 1)]
            prev_c[n] = u
        if i % 2 == 0:
            rec["pg"] = pg_conns()
        if i % 5 == 0:
            rec["top"] = top_procs()
            rec["health"] = health()
            rec["api_err"] = api_errors(f"{int(now - last_err_check) + 1}s")
            last_err_check = now
        print(json.dumps(rec), flush=True)
        prev_cpu, prev_vm, prev_t = (tot, idle), vm, now
        i += 1


if __name__ == "__main__":
    main()
