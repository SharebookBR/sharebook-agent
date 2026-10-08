# Materializa no Windows assets de itens cujo volume OpenClaw original foi removido em 2026-08-16.
#
# Problema que resolve:
#   Itens triados antes de 2026-08-16 têm metadata_json apontando para
#   /data/workspace/sharebook-ebook-importer/var/tmp/triage-<ID>/, cujos arquivos antigos não voltam com o novo volume.
#   O publisher resolve o PDF por caminho absoluto do manifest, então falha com
#   "item sem PDF materializado pela triagem" mesmo com a triagem íntegra no banco.
#
# O que faz, por item:
#   1. Baixa o PDF de metadata_json.manifest.source_url (pula se já existir)
#   2. Valida magic bytes %PDF-
#   3. Renderiza a página 1 e prepara a capa como JPEG sob o limite de upload
#   4. Reaponta manifest.downloaded_pdf_path / downloaded_cover_path e triage.preview_pages
#      para os caminhos Windows, por merge (nunca sobrescreve metadata_json cegamente)
#
# Uso:
#     python materialize_assets_windows.py --ids 1553 1582 1502 1471
#     python materialize_assets_windows.py --ids 1471 --max-cover-bytes 120000
#
# Depois disso o item publica pelo worker normal:
#     cd C:\Repos\SHAREBOOK\sharebook-ebook-importer
#     python cli.py publish-once --id <ID>
#
# A capa da página 1 nem sempre é capa de verdade (folha de rosto acadêmica). Conferir visualmente
# antes de publicar; se não servir, gerar capa via scripts/covers/ e passar --cover-path no plan-set.
#
# Credenciais vêm de C:\Repos\SHAREBOOK\sharebook-agent\.env — nunca hardcode.

from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

ENV_PATH = Path(r"C:\Repos\SHAREBOOK\sharebook-agent\.env")
# Caminho que o worker espera no Windows (espelho do layout POSIX do importer).
TRIAGE_TMP_DIR = Path(r"C:\data\workspace\sharebook-ebook-importer\var\tmp")
PDFTOPPM = (
    r"C:\Users\raffa\AppData\Local\Microsoft\WinGet\Packages"
    r"\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\poppler-25.07.0\Library\bin\pdftoppm.exe"
)
PREPARE_COVER = Path(r"C:\Repos\SHAREBOOK\sharebook-agent\scripts\covers\prepare_cover.py")
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


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


def build_opener() -> urllib.request.OpenerDirector:
    # CookieJar resolve WAF civilizado (Cloudflare simples) em fontes como realtimerendering.
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    opener.addheaders = [
        ("User-Agent", USER_AGENT),
        ("Accept", "application/pdf,text/html,*/*"),
        ("Accept-Language", "en-US,en;q=0.9"),
    ]
    return opener


def download_pdf(url: str, dest: Path, opener) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with opener.open(url, timeout=300) as response:
        data = response.read()
    if data[:5] != b"%PDF-":
        raise ValueError(
            f"resposta não é PDF (magic={data[:12]!r}, {len(data)} bytes). "
            "Fonte provavelmente serve interstitial/HTML — resolver a URL real do asset."
        )
    dest.write_bytes(data)
    return len(data)


def render_cover(pdf: Path, out_dir: Path, max_bytes: int) -> Path:
    raw_prefix = out_dir / "page"
    subprocess.run(
        [PDFTOPPM, "-png", "-r", "150", "-l", "1", str(pdf), str(raw_prefix)],
        check=True,
    )
    # pdftoppm usa N dígitos no sufixo conforme o total de páginas do PDF.
    rendered = next(
        (p for p in (out_dir / f"page-{s}.png" for s in ("1", "01", "001", "0001")) if p.exists()),
        None,
    )
    if rendered is None:
        raise FileNotFoundError(f"pdftoppm não gerou PNG para {pdf}")

    cover = out_dir / "cover.jpg"
    subprocess.run(
        [sys.executable, str(PREPARE_COVER), str(rendered), str(cover),
         "--max-bytes", str(max_bytes)],
        check=True, capture_output=True, text=True,
    )
    rendered.unlink(missing_ok=True)
    return cover


def rehome(item_id: int, cur, max_cover_bytes: int, opener) -> str:
    cur.execute("SELECT metadata_json FROM importer.queue_items WHERE id = %s", (item_id,))
    row = cur.fetchone()
    if row is None:
        raise LookupError(f"item {item_id} não existe na fila")
    meta = row[0] or {}

    manifest = dict(meta.get("manifest") or {})
    source_url = manifest.get("source_url")
    if not source_url:
        raise ValueError("manifest sem source_url — nada de onde baixar")

    out_dir = TRIAGE_TMP_DIR / f"triage-{item_id}"
    pdf = out_dir / "source.pdf"
    notes = []
    if pdf.exists() and pdf.stat().st_size > 100_000:
        notes.append(f"pdf reaproveitado {pdf.stat().st_size / 1e6:.2f}MB")
    else:
        notes.append(f"pdf baixado {download_pdf(source_url, pdf, opener) / 1e6:.2f}MB")

    cover = render_cover(pdf, out_dir, max_cover_bytes)
    notes.append(f"capa {cover.stat().st_size / 1024:.0f}KB")

    manifest["downloaded_pdf_path"] = str(pdf)
    manifest["downloaded_cover_path"] = str(cover)
    manifest["manifest_path"] = str(out_dir / "manifest.json")
    meta["manifest"] = manifest

    triage = dict(meta.get("triage") or {})
    triage["preview_pages"] = [str(cover)]
    triage["assets_rehomed"] = "windows_local"
    meta["triage"] = triage

    cur.execute(
        "UPDATE importer.queue_items SET metadata_json = %s WHERE id = %s",
        (json.dumps(meta, ensure_ascii=False), item_id),
    )
    return ", ".join(notes)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Materializa no Windows assets perdidos com o volume OpenClaw removido"
    )
    parser.add_argument("--ids", nargs="+", type=int, required=True)
    parser.add_argument(
        "--max-cover-bytes", type=int, default=250_000,
        help="Limite da capa JPEG. Capa grande já causou SSLEOFError no publish (default: 250000)",
    )
    args = parser.parse_args()

    opener = build_opener()
    conn = psycopg2.connect(build_dsn())
    cur = conn.cursor()

    ok, fail = 0, 0
    for item_id in args.ids:
        try:
            print(f"#{item_id} -> {rehome(item_id, cur, args.max_cover_bytes, opener)}  OK")
            conn.commit()
            ok += 1
        except Exception as exc:
            conn.rollback()
            print(f"#{item_id} ERRO: {exc}", file=sys.stderr)
            fail += 1

    cur.close()
    conn.close()
    print(f"\n{ok} ok  |  {fail} falhou")


if __name__ == "__main__":
    main()
