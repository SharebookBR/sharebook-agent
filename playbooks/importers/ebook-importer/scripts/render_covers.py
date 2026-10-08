# Renderiza capa (página 1) de PDFs do ciclo manual Windows.
#
# Uso:
#     python render_covers.py --ids 1186 1302 1311
#
# PDF procurado, nesta ordem:
#   1. C:\data\workspace\sharebook-ebook-importer\var\tmp\triage-<id>\source.pdf  (Passo 3b)
#   2. C:\Users\raffa\Downloads\<id>.pdf
# PNGs gravados em sharebook-ebook-importer\var\triage\preview-pages\<id>-page-1.png
# metadata_json.triage.preview_pages atualizado no banco.
#
# Credenciais vêm de C:\Repos\SHAREBOOK\sharebook-agent\.env — nunca hardcode.

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

PDFTOPPM = (
    r"C:\Users\raffa\AppData\Local\Microsoft\WinGet\Packages"
    r"\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\poppler-25.07.0\Library\bin\pdftoppm.exe"
)
ENV_PATH = Path(r"C:\Repos\SHAREBOOK\sharebook-agent\.env")
DOWNLOADS_DIR = Path(r"C:\Users\raffa\Downloads")
TRIAGE_TMP_DIR = Path(r"C:\data\workspace\sharebook-ebook-importer\var\tmp")
PREVIEW_DIR = Path(r"C:\Repos\SHAREBOOK\sharebook-ebook-importer\var\triage\preview-pages")


def build_dsn() -> str:
    load_dotenv(ENV_PATH)
    dsn = os.getenv("IMPORTER_DB_DSN")
    if dsn:
        return dsn
    return (
        f"host={os.getenv('SHAREBOOK_PROD_PG_RW_HOST')} "
        f"port={os.getenv('SHAREBOOK_PROD_PG_RW_PORT')} "
        f"dbname=sharebook_importer "
        f"user={os.getenv('SHAREBOOK_PROD_PG_RW_USER')} "
        f"password={os.getenv('SHAREBOOK_PROD_PG_RW_PASSWORD')} "
        f"sslmode={os.getenv('SHAREBOOK_PROD_PG_RW_SSLMODE', 'disable')}"
    )


def locate_pdf(item_id: int) -> Path:
    candidates = [
        TRIAGE_TMP_DIR / f"triage-{item_id}" / "source.pdf",
        DOWNLOADS_DIR / f"{item_id}.pdf",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    tried = " | ".join(str(c) for c in candidates)
    raise FileNotFoundError(f"PDF não encontrado para item {item_id}. Tentado: {tried}")


def render_one(item_id: int, cur) -> Path:
    pdf = locate_pdf(item_id)

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    for f in PREVIEW_DIR.glob(f"{item_id}-page*.png"):
        f.unlink()

    out_prefix = PREVIEW_DIR / f"{item_id}-page"
    subprocess.run(
        [PDFTOPPM, "-png", "-r", "150", "-l", "1", str(pdf), str(out_prefix)],
        check=True
    )

    # pdftoppm gera sufixo variável conforme o nº total de páginas
    png = PREVIEW_DIR / f"{item_id}-page-1.png"
    if not png.exists():
        for suffix in ["-01.png", "-001.png", "-0001.png"]:
            alt = PREVIEW_DIR / f"{item_id}-page{suffix}"
            if alt.exists():
                alt.rename(png)
                break

    if not png.exists():
        raise FileNotFoundError(f"PNG não foi gerado para item {item_id}")

    # Atualiza metadata_json no banco
    cur.execute("SELECT metadata_json FROM importer.queue_items WHERE id = %s", (item_id,))
    row = cur.fetchone()
    meta = row[0] or {} if row else {}
    triage = meta.get("triage", {})
    triage["preview_pages"] = [str(png)]
    meta["triage"] = triage
    cur.execute(
        "UPDATE importer.queue_items SET metadata_json = %s WHERE id = %s",
        (json.dumps(meta, ensure_ascii=False), item_id)
    )
    return png


def main() -> None:
    parser = argparse.ArgumentParser(description="Renderiza capas do ciclo manual Windows")
    parser.add_argument("--ids", nargs="+", type=int, required=True)
    args = parser.parse_args()

    conn = psycopg2.connect(build_dsn())
    cur = conn.cursor()

    ok, fail = 0, 0
    for item_id in args.ids:
        try:
            png = render_one(item_id, cur)
            print(f"#{item_id} -> {png}  OK")
            ok += 1
        except Exception as exc:
            print(f"#{item_id} ERRO: {exc}", file=sys.stderr)
            fail += 1

    conn.commit()
    conn.close()
    print(f"\n{ok} ok  |  {fail} falhou")


if __name__ == "__main__":
    main()
