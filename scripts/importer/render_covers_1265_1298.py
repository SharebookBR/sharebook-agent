# Renderiza pagina 1 de cada PDF e atualiza metadata_json.triage.preview_pages no banco.
# Prerequisito: pdftoppm disponivel no PATH (winget install oschwartz10612.Poppler --scope user).
# Uso: python render_covers_1265_1298.py

from __future__ import annotations

import json
import shutil
import subprocess
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import psycopg2

DOWNLOADS_DIR = Path(r"C:\Users\raffa\Downloads")
PREVIEW_DIR = Path(r"C:\Repos\SHAREBOOK\sharebook-ebook-importer\var\triage\preview-pages")
ITEM_IDS = [1265, 1268, 1295, 1297, 1298]

POPPLER_BIN = Path(
    r"C:\Users\raffa\AppData\Local\Microsoft\WinGet\Packages"
    r"\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\poppler-25.07.0\Library\bin"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    with open(r"C:\Repos\SHAREBOOK\sharebook-agent\.env", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"')
    return env


def pg_connect(dsn: str):
    prefix = "postgresql://"
    rest = dsn[len(prefix):]
    userpass, hostdb = rest.rsplit("@", 1)
    user, password = userpass.split(":", 1)
    hostport, database = hostdb.split("/", 1)
    host, port = hostport.split(":", 1)
    return psycopg2.connect(
        user=urllib.parse.unquote(user),
        password=urllib.parse.unquote(password),
        host=host,
        port=int(port),
        dbname=database,
    )


def find_pdftoppm() -> str:
    candidate = POPPLER_BIN / "pdftoppm.exe"
    if candidate.exists():
        return str(candidate)
    found = shutil.which("pdftoppm")
    if found:
        return found
    raise RuntimeError("pdftoppm não encontrado. Instalar: winget install oschwartz10612.Poppler --scope user")


def render_page1(pdftoppm_path: str, pdf_path: Path, item_id: int) -> Path:
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    prefix = PREVIEW_DIR / f"{item_id}-page"
    subprocess.run(
        [pdftoppm_path, "-f", "1", "-l", "1", "-png", str(pdf_path), str(prefix)],
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    )
    # pdftoppm outputs <prefix>-1.png (single digit without leading zero when only 1 page range)
    # or <prefix>-01.png depending on version. Find what was created.
    candidates = sorted(PREVIEW_DIR.glob(f"{item_id}-page*.png"))
    if not candidates:
        raise RuntimeError(f"pdftoppm não gerou PNG para #{item_id}")
    return candidates[0]


def update_preview_pages(conn, item_id: int, png_path: Path) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT metadata_json FROM importer.queue_items WHERE id=%s",
            (item_id,),
        )
        row = cur.fetchone()
        if not row:
            raise ValueError(f"item #{item_id} não encontrado")

        raw = row[0]
        meta: dict = {}
        if raw:
            meta = json.loads(raw) if isinstance(raw, str) else dict(raw)

        triage = meta.get("triage") or {}
        triage["preview_pages"] = [str(png_path)]
        meta["triage"] = triage

        cur.execute(
            "UPDATE importer.queue_items SET metadata_json=%s, updated_at=%s WHERE id=%s",
            (json.dumps(meta, ensure_ascii=False), utc_now(), item_id),
        )
        print(f"  #{item_id} preview_pages -> {png_path.name}  ({cur.rowcount} row updated)")


def main() -> None:
    pdftoppm_path = find_pdftoppm()
    print(f"pdftoppm: {pdftoppm_path}\n")

    env = load_env()
    conn = pg_connect(env["IMPORTER_DB_DSN"])

    for item_id in ITEM_IDS:
        pdf_path = DOWNLOADS_DIR / f"{item_id}.pdf"
        print(f"  Renderizando #{item_id} ...")
        if not pdf_path.exists():
            print(f"  [ERRO] PDF não encontrado: {pdf_path}")
            continue
        try:
            png_path = render_page1(pdftoppm_path, pdf_path, item_id)
            print(f"  PNG: {png_path}  ({png_path.stat().st_size:,} bytes)")
            update_preview_pages(conn, item_id, png_path)
        except Exception as exc:
            print(f"  [ERRO] #{item_id}: {exc}")

    conn.commit()
    conn.close()
    print("\nFeito.")


if __name__ == "__main__":
    main()
