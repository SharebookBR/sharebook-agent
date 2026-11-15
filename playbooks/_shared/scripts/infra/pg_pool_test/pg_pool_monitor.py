#!/usr/bin/env python3
"""Amostra host, API, Postgres e sessões a cada segundo durante pg_pool_probe."""
import json
import os
import subprocess
import time


def sh(command):
    return subprocess.run(command, shell=True, capture_output=True, text=True).stdout.strip()


def read_cpu():
    with open("/proc/stat", encoding="utf-8") as handle:
        values = list(map(int, handle.readline().split()[1:]))
    return sum(values), values[3] + values[4]


def meminfo():
    result = {}
    with open("/proc/meminfo", encoding="utf-8") as handle:
        for line in handle:
            key, value = line.split(":", 1)
            result[key] = int(value.split()[0]) * 1024
    return result


def vmstat():
    wanted = {"pswpin", "pswpout"}
    result = {}
    with open("/proc/vmstat", encoding="utf-8") as handle:
        for line in handle:
            key, value = line.split()
            if key in wanted:
                result[key] = int(value)
    return result


def app_container():
    return sh("docker ps --filter name=sharebook-api --format '{{.Names}}' | head -n 1")


def pg_container():
    return sh("docker ps --filter ancestor=postgres:17-alpine --format '{{.Names}}' | head -n 1")


def cgroup_metrics(container):
    cid = sh(f"docker inspect -f '{{{{.Id}}}}' {container}")
    path = f"/sys/fs/cgroup/system.slice/docker-{cid}.scope"
    try:
        with open(path + "/memory.current", encoding="utf-8") as handle:
            memory = int(handle.read().strip())
        with open(path + "/memory.swap.current", encoding="utf-8") as handle:
            swap = int(handle.read().strip())
        with open(path + "/cpu.stat", encoding="utf-8") as handle:
            cpu = next(int(line.split()[1]) for line in handle if line.startswith("usage_usec"))
        return memory, swap, cpu
    except (FileNotFoundError, StopIteration, ValueError):
        return None, None, None


def pg_sessions(container):
    query = "select count(*), count(*) filter (where state='active'), count(*) filter (where wait_event_type is not null) from pg_stat_activity where datname='sharebook'"
    raw = sh(f"docker exec {container} psql -U postgres -At -c \"{query}\"")
    try:
        return [int(value) for value in raw.split("|")]
    except ValueError:
        return None


def healthy(container):
    return sh(f"docker inspect -f '{{{{if .State.Health}}}}{{{{.State.Health.Status}}}}{{{{else}}}}none{{{{end}}}} {{{{.RestartCount}}}}' {container}")


def main():
    api = app_container()
    postgres = pg_container()
    if not api or not postgres:
        raise SystemExit("API ou Postgres da aplicação não encontrado")
    previous_cpu = read_cpu()
    previous_vm = vmstat()
    previous_api = cgroup_metrics(api)[2]
    previous_pg = cgroup_metrics(postgres)[2]
    previous_t = time.time()
    while True:
        time.sleep(1)
        now = time.time()
        total, idle = read_cpu()
        current_vm = vmstat()
        elapsed = max(now - previous_t, 0.001)
        host_cpu = 100 * (1 - (idle - previous_cpu[1]) / max(total - previous_cpu[0], 1))
        memory = meminfo()
        api_memory, api_swap, api_cpu = cgroup_metrics(api)
        pg_memory, pg_swap, pg_cpu = cgroup_metrics(postgres)
        record = {
            "t": round(now, 3),
            "host_cpu": round(host_cpu, 1),
            "mem_avail": memory["MemAvailable"],
            "swap_used": memory["SwapTotal"] - memory["SwapFree"],
            "swap_in_kibs": round((current_vm["pswpin"] - previous_vm["pswpin"]) * 4 / elapsed, 1),
            "swap_out_kibs": round((current_vm["pswpout"] - previous_vm["pswpout"]) * 4 / elapsed, 1),
            "pg_sessions": pg_sessions(postgres),
            "api": {"memory": api_memory, "swap": api_swap, "cpu": None if previous_api is None or api_cpu is None else round((api_cpu - previous_api) / 1e4 / elapsed, 1), "health": healthy(api)},
            "postgres": {"memory": pg_memory, "swap": pg_swap, "cpu": None if previous_pg is None or pg_cpu is None else round((pg_cpu - previous_pg) / 1e4 / elapsed, 1), "health": healthy(postgres)},
        }
        print(json.dumps(record), flush=True)
        previous_cpu, previous_vm, previous_t = (total, idle), current_vm, now
        previous_api, previous_pg = api_cpu, pg_cpu


if __name__ == "__main__":
    main()
