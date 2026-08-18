# Garante que o .env e o UNICO lugar do workspace com credencial.
#
# Uso:
#     python sweep_secrets.py                 # varre C:\Repos\SHAREBOOK
#     python sweep_secrets.py --root <path>
#     python sweep_secrets.py --history       # + pickaxe no historico dos repos (lento)
#
# Sai com codigo 1 se achar segredo do .env fora do .env.
#
# Duas varreduras complementares:
#   A) por VALOR  — pega cada segredo real do .env e procura literalmente.
#      E a que pega o caso que nenhum regex previu. Considera tambem a forma
#      percent-encoded, porque senha com % ou # aparece codificada dentro de DSN.
#   B) por PADRAO — pega segredo que nem esta no .env (chave AWS, private key).
#
# Nunca imprime o valor do segredo, so o NOME da variavel e o arquivo.

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

from dotenv import dotenv_values

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_ROOT = Path(r"C:\Repos\SHAREBOOK")
ENV_PATH = DEFAULT_ROOT / "sharebook-agent" / ".env"
REPOS = ["sharebook-agent", "sharebook-frontend", "sharebook-backend", "sharebook-ebook-importer"]

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", "dist", "obj", "bin", ".angular",
    ".vs", ".vscode", "packages", "coverage", ".nyc_output", "var", "temp",
    "tmp", "codex-temp", ".next", "out", "build",
}
SKIP_DIR_PREFIX = (".venv",)
SKIP_EXT = {
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".zip", ".gz",
    ".tar", ".7z", ".exe", ".dll", ".pyd", ".so", ".woff", ".woff2", ".ttf",
    ".eot", ".mp4", ".mp3", ".pyc", ".pack", ".idx", ".epub", ".docx", ".xlsx",
}
MAX_BYTES = 3_000_000

# Chaves cujo valor e segredo de verdade — host, porta e path nao sao.
SECRET_KEY_RE = re.compile(r"(PASSWORD|TOKEN|SECRET|API_KEY|ACCESS_KEY|_DSN)$")

PATTERNS = [
    ("chave AWS", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("chave OpenAI/Anthropic", re.compile(r"sk-(proj|ant)-[A-Za-z0-9_\-]{20,}")),
    ("token GitHub", re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("senha inline", re.compile(r"""(?i)\b(password|senha|pwd)\s*[=:]\s*["'][^"'\s]{6,}["']""")),
    ("DSN com senha", re.compile(r"""(?i)postgres(ql)?://[^:\s"']+:[^@\s"']{6,}@""")),
    # Connection string ADO.NET: a senha vem SEM aspas, dentro de um valor maior.
    # O padrao "senha inline" acima nao pega, e foi assim que a senha de
    # sharebook_user_dev ficou publica dentro de "PostgresConnection": "Host=...;Password=...".
    ("senha em connection string", re.compile(r"(?i)[;\"']\s*(password|pwd)\s*=\s*[^;\"'\s]{6,}\s*;")),
]

# Falsos positivos ja triados em 17/08/2026 — placeholder e fixture de teste.
# ga4-key.json e excecao deliberada: service account do Google nao cabe no .env.
CONHECIDOS = {
    "sharebook-agent/scripts/production/ga4-key.json",
    "sharebook-ebook-importer/.env.example",
    "sharebook-backend/ShareBook/ShareBook.Test.Unit/Services/UserServiceTests.cs",
    "sharebook-backend/ShareBook/ShareBook.Test.Unit/Validators/UserValidatorTests.cs",
}


def carregar_segredos(env_path: Path) -> dict[str, set[str]]:
    alvos: dict[str, set[str]] = {}
    for key, value in dotenv_values(env_path).items():
        if not value or len(value) < 8 or not SECRET_KEY_RE.search(key):
            continue
        formas = {value}
        embutida = re.search(r"://[^:]+:([^@]+)@", value)
        if embutida:
            formas.add(embutida.group(1))
        else:
            formas.add(quote(value, safe=""))
        alvos[key] = formas
    return alvos


def arquivos(root: Path):
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if set(p.parts) & SKIP_DIRS or any(s.startswith(SKIP_DIR_PREFIX) for s in p.parts):
            continue
        if p.suffix.lower() in SKIP_EXT:
            continue
        try:
            if p.stat().st_size > MAX_BYTES:
                continue
        except OSError:
            continue
        yield p


def varrer_arvore(root: Path, env_path: Path, alvos: dict[str, set[str]]) -> list[str]:
    achados_valor: list[str] = []
    achados_padrao: list[str] = []
    lidos = 0

    for path in arquivos(root):
        try:
            texto = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        lidos += 1
        rel = path.relative_to(root).as_posix()
        if path.resolve() == env_path.resolve():
            continue

        for key, formas in alvos.items():
            for forma in formas:
                if forma in texto:
                    linha = texto[: texto.index(forma)].count("\n") + 1
                    achados_valor.append(f"  {rel}:{linha}  <- valor de {key}")
                    break

        if rel in CONHECIDOS:
            continue
        for nome, rx in PATTERNS:
            m = rx.search(texto)
            if m:
                achados_padrao.append(f"  {rel}:{texto[: m.start()].count(chr(10)) + 1}  <- {nome}")

    print(f"Arquivos lidos: {lidos}\n")
    print("=== A) Segredo do .env aparecendo FORA do .env ===")
    print("\n".join(achados_valor) if achados_valor else "  nenhum")
    print("\n=== B) Padrao de segredo, fora dos ja triados ===")
    print("\n".join(sorted(set(achados_padrao))) if achados_padrao else "  nenhum")
    return achados_valor


CONFIG_HINTS = (
    ".env", "appsettings", "environment.", "secrets", "docker-compose",
    "web.config", "app.config", "launchsettings", "credentials", "connectionstrings",
)
CONFIG_IGNORA = (".venv", "node_modules", "/obj/", "/bin/", "packages/",
                 ".example", ".template", ".sample")


def varrer_configs_historicos(root: Path) -> list[str]:
    """Le os blobs de arquivos de CONFIG que ja existiram e aplica os padroes.

    E a varredura que encontra o que a busca por valor nao encontra: segredo que
    foi commitado, depois apagado, e que nunca esteve no .env. Foi assim que a
    senha de sharebook_user_dev apareceu, num appsettings temporario commitado
    no repo publico em abril/2026 e removido depois.
    """
    print("\n=== D) Segredo em arquivo de config que ja existiu no historico ===")
    achados: list[str] = []
    for repo in REPOS:
        path = root / repo
        if not (path / ".git").exists():
            continue
        listagem = subprocess.run(
            ["git", "log", "--all", "--diff-filter=A", "--name-only", "--format="],
            cwd=path, capture_output=True, text=True, errors="replace",
        )
        arquivos_cfg = sorted({
            ln.strip() for ln in listagem.stdout.splitlines()
            if ln.strip()
            and any(t in ln.lower() for t in CONFIG_HINTS)
            and not any(g in ln.lower() for g in CONFIG_IGNORA)
        })
        for arq in arquivos_cfg:
            revs = subprocess.run(
                ["git", "log", "--all", "--format=%H", "--", arq],
                cwd=path, capture_output=True, text=True, errors="replace",
            ).stdout.split()
            for sha in revs:
                blob = subprocess.run(
                    ["git", "show", f"{sha}:{arq}"],
                    cwd=path, capture_output=True, text=True, errors="replace",
                )
                if blob.returncode != 0:
                    continue
                for nome, rx in PATTERNS:
                    if rx.search(blob.stdout):
                        achados.append(f"  {repo} {sha[:8]} {arq}  <- {nome}")
                        break
                else:
                    continue
                break  # uma revisao suja ja basta para sinalizar o arquivo
    print("\n".join(sorted(set(achados))) if achados else "  nenhum")
    if achados:
        print("\n  Config com segredo no historico = credencial comprometida.")
        print("  Conferir se o valor ainda autentica; se sim, rotacionar ou remover o role.")
    return achados


def varrer_historico(root: Path, alvos: dict[str, set[str]]) -> list[str]:
    print("\n=== C) Segredo vivo no historico do git (pickaxe) ===")
    achados: list[str] = []
    for repo in REPOS:
        path = root / repo
        if not (path / ".git").exists():
            print(f"  {repo}: nao e repo git, pulado")
            continue
        sujo = False
        for key, formas in alvos.items():
            for forma in formas:
                r = subprocess.run(
                    ["git", "log", "--all", "--oneline", "-S", forma],
                    cwd=path, capture_output=True, text=True, errors="replace",
                )
                if r.stdout.strip():
                    commits = r.stdout.strip().splitlines()
                    achados.append(f"  {repo}: {key} em {len(commits)} commit(s), 1o: {commits[-1].split()[0]}")
                    sujo = True
                    break
        print(f"  {repo}: {'ACHADOS' if sujo else 'limpo'}")
    if achados:
        print("\n".join(achados))
        print("\n  Segredo no historico = comprometido. Rotacionar, nao so apagar.")
    return achados


def main() -> int:
    parser = argparse.ArgumentParser(description="Varre o workspace atras de credencial fora do .env")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--env-file", default=str(ENV_PATH))
    parser.add_argument("--history", action="store_true", help="Inclui o pickaxe no historico (lento)")
    args = parser.parse_args()

    root = Path(args.root)
    env_path = Path(args.env_file)
    if not env_path.exists():
        raise SystemExit(f".env nao encontrado: {env_path}")

    alvos = carregar_segredos(env_path)
    print(f"Segredos carregados do .env: {len(alvos)} variaveis")
    print(f"Raiz varrida: {root}\n")

    achados = varrer_arvore(root, env_path, alvos)
    if args.history:
        achados += varrer_configs_historicos(root)
        achados += varrer_historico(root, alvos)
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())
