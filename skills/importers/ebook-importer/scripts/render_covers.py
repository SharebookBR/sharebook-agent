# Renderiza capa (página 1) de PDFs do ciclo manual Windows.
#
# Uso:
#     python render_covers.py --ids 1186 1302 1311
#
# PDFs esperados em C:\Users\raffa\Downloads\<id>.pdf
# PNGs gravados em sharebook-ebook-importer\var\triage\preview-pages\<id>-page-1.png
# metadata_json.triage.preview_pages atualizado no banco.

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import psycopg2

PDFTOPPM = (
    r"C:\Users\raffa\AppData\Local\Microsoft\WinGet\Packages"
    r"\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\poppler-25.07.0\Library\bin\pdftoppm.exe"
)
DOWNLOADS_DIR = Path(r"C:\Users\raffa\Downloads")
PREVIEW_DIR = Path(r"C:\Repos\SHAREBOOK\sharebook-ebook-importer\var\triage\preview-pages")


def render_one(item_id: int, cur) -> Path:
    pdf = DOWNLOADS_DIR / f"{item_id}.pdf"
    if not pdf.exists():
        raise FileNotFoundError(f"PDF não encontrado: {pdf}")

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

    conn = psycopg2.connect(
        host="212.85.23.202", port=5432, dbname="sharebook_importer",
        user="sharebook_ai_rw", password="F%Ljy9oxTA3iR#npW%4W9iaSaJKU", sslmode="disable"
    )
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
