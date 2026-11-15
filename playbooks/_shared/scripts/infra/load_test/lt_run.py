"""Orquestrador do teste de carga SSR de origem externa.

Uso: lt_run.py <dir_saida> [--seco]
  --seco: só o monitor por 60 s (sem carga), para provar que os gatilhos não disparam em repouso.

Gatilhos de parada (os do V2): swap I/O > 1000 KiB/s por 10 amostras seguidas; swap usado
+300 MiB sobre o início; CPU do host > 90% por 30 amostras seguidas; frontend/API sem
'healthy' ou com restart; qualquer 500/Npgsql no log da API.
"""
import json, os, re, shutil, subprocess, sys, threading, time, urllib.request
import paramiko
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
SECO = "--seco" in sys.argv
os.makedirs(OUT, exist_ok=True)
STOP = os.path.join(OUT, "STOP")
NODE = shutil.which("node") or r"C:\Program Files\nodejs\node.exe"
URLS = os.path.join(OUT, "urls.json")

# Mesmo padrão dos outros scripts: .env do sharebook-agent (OpenClaw ou Windows local),
# ou o caminho em SHAREBOOK_ENV_FILE (útil numa máquina de nuvem montada para o teste).
ENV_FILE = os.getenv("SHAREBOOK_ENV_FILE") or next(
    (p for p in ("/data/workspace/sharebook-agent/.env", r"C:\Repos\SHAREBOOK\sharebook-agent\.env") if os.path.exists(p)), None)
load_dotenv(ENV_FILE)
P = "VPS_HOSTGATOR_SSH"


def ssh():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(os.getenv(f"{P}_HOST"), port=int(os.getenv(f"{P}_PORT") or 22),
              username=os.getenv(f"{P}_USER"), password=os.getenv(f"{P}_PASSWORD"), timeout=15)
    return c


def log(msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(os.path.join(OUT, "run.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")


class Triggers:
    def __init__(self):
        self.swap0 = None
        self.swapio_run = 0
        self.cpu_run = 0
        self.restarts0 = {}
        self.reason = None
        self.peak = {"swap_used": 0, "si+so": 0.0, "cpu": 0.0, "pg": 0}

    def check(self, r):
        if self.swap0 is None:
            self.swap0 = r["swap_used"]
        io = r["si_kibs"] + r["so_kibs"]
        self.swapio_run = self.swapio_run + 1 if io > 1000 else 0
        self.cpu_run = self.cpu_run + 1 if r["cpu"] > 90 else 0
        self.peak["swap_used"] = max(self.peak["swap_used"], r["swap_used"])
        self.peak["si+so"] = max(self.peak["si+so"], io)
        self.peak["cpu"] = max(self.peak["cpu"], r["cpu"])
        if r.get("pg"):
            self.peak["pg"] = max(self.peak["pg"], r["pg"][0])
        if self.swapio_run >= 10:
            return f"swap I/O > 1000 KiB/s por 10 s (último {io:.0f} KiB/s)"
        if r["swap_used"] - self.swap0 > 300 * 1024 * 1024:
            return f"swap usado +{(r['swap_used'] - self.swap0) / 2**20:.0f} MiB"
        if self.cpu_run >= 30:
            return "CPU do host > 90% por 30 s"
        for name, s in (r.get("health") or {}).items():
            parts = s.split()
            if not parts or parts[0] != "healthy":
                return f"{name} não está healthy: {s!r}"
            rc = parts[1] if len(parts) > 1 else "?"
            self.restarts0.setdefault(name, rc)
            if rc != self.restarts0[name]:
                return f"{name} reiniciou (RestartCount {self.restarts0[name]} -> {rc})"
        if r.get("api_err", 0) and r["api_err"] > 0:
            return f"{r['api_err']} linha(s) de 500/Npgsql no log da API"
        return None


def build_urls():
    """Páginas públicas de livro e categoria, tiradas do sitemap (só GET público)."""
    xml = urllib.request.urlopen("https://www.sharebook.com.br/sitemap.xml", timeout=60).read().decode()
    urls = [u for u in re.findall(r"<loc>([^<]+)", xml) if "/livros/" in u or re.search(r"/categorias/.", u)]
    json.dump(urls, open(URLS, "w"))
    log(f"{len(urls)} URLs do sitemap")


def main():
    if os.path.exists(STOP):
        os.remove(STOP)
    if not os.path.exists(URLS):
        build_urls()
    c = ssh()
    sftp = c.open_sftp()
    sftp.put(os.path.join(HERE, "lt_monitor.py"), "/tmp/lt_monitor.py")
    _, stdout, _ = c.exec_command("timeout 2400 python3 -u /tmp/lt_monitor.py", get_pty=True)
    trig = Triggers()
    state = {"phase": "base", "gen": None, "done": False}
    mon = open(os.path.join(OUT, "monitor.jsonl"), "a", encoding="utf-8")

    def reader():
        for line in iter(stdout.readline, ""):
            line = line.strip()
            if not line.startswith("{"):
                continue
            r = json.loads(line)
            r["phase"] = state["phase"]
            mon.write(json.dumps(r) + "\n")
            mon.flush()
            reason = trig.check(r)
            if reason and not trig.reason:
                trig.reason = reason
                open(STOP, "w").write(reason)
                log(f"GATILHO: {reason} -> STOP")
            if state["done"]:
                break

    th = threading.Thread(target=reader, daemon=True)
    th.start()

    log("monitor em repouso por 60 s (base)")
    time.sleep(60)
    if trig.reason:
        log("gatilho disparou em repouso: teste NÃO iniciado")
    elif SECO:
        log(f"teste seco ok; picos em repouso: {trig.peak}")
    else:
        state["phase"] = "carga"
        log("iniciando gerador")
        gen = subprocess.Popen([NODE, os.path.join(HERE, "lt_gen.mjs"), URLS,
                                os.path.join(OUT, "requests.jsonl"), STOP],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in gen.stdout:
            log("gen: " + line.rstrip())
        gen.wait()
        state["phase"] = "pos"
        log("gerador terminou; 30 s de monitor pós-teste")
        time.sleep(30)
    state["done"] = True
    c.exec_command("pkill -f /tmp/lt_monitor.py; rm -f /tmp/lt_monitor.py")
    time.sleep(2)
    c.close()
    swap_delta = (trig.peak["swap_used"] - (trig.swap0 or 0)) / 2**20
    log(f"FIM. gatilho={trig.reason or 'nenhum'} | pico swap I/O={trig.peak['si+so']:.0f} KiB/s | "
        f"pico swap +{swap_delta:.0f} MiB | pico CPU={trig.peak['cpu']:.0f}% | pico PG={trig.peak['pg']}")


main()
