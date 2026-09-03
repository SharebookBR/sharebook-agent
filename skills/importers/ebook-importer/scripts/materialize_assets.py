#!/usr/bin/env python3
from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

import psycopg2

SCRIPT_PATH = Path(__file__).resolve()
# skills/importers/ebook-importer/scripts/materialize_assets.py
# parents: [0]=scripts [1]=ebook-importer [2]=importers [3]=skills [4]=sharebook-agent
AGENT_DIR_FALLBACK = SCRIPT_PATH.parents[4]
LIB_DIR = AGENT_DIR_FALLBACK / "scripts" / "lib"
sys.path.insert(0, str(LIB_DIR))

from sharebook_env import (
    dsn_with_host_port,
    load_env,
    resolve_agent_dir,
    resolve_env_file,
    resolve_runtime_path,
    sibling_repo,
)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def build_opener() -> urllib.request.OpenerDirector:
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    opener.addheaders = [
        ("User-Agent", USER_AGENT),
        ("Accept", "application/pdf,text/html,*/*"),
        ("Accept-Language", "en-US,en;q=0.9"),
    ]
    return opener


def download_pdf(url: str, dest: Path, opener: urllib.request.OpenerDirector) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with opener.open(url, timeout=300) as response:
        data = response.read()
    if data[:5] != b"%PDF-":
        raise ValueError(
            f"resposta não é PDF (magic={data[:12]!r}, {len(data)} bytes). "
            "Fonte provavelmente serve HTML/interstitial ou asset errado."
        )
    dest.write_bytes(data)
    return len(data)


def find_pdftoppm(values: dict[str, str]) -> str:
    configured = values.get("PDFTOPPM") or values.get("PDFTOPPM_PATH")
    if configured and Path(configured).exists():
        return configured
    found = shutil.which("pdftoppm")
    if found:
        return found
    windows_default = Path(
        r"C:\Users\raffa\AppData\Local\Microsoft\WinGet\Packages"
        r"\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe"
        r"\poppler-25.07.0\Library\bin\pdftoppm.exe"
    )
    if windows_default.exists():
        return str(windows_default)
    raise SystemExit("pdftoppm não encontrado. Instale Poppler ou configure PDFTOPPM_PATH no .env.")


def render_cover(pdf: Path, out_dir: Path, max_bytes: int, pdftoppm: str, prepare_cover: Path) -> Path:
    raw_prefix = out_dir / "page"
    subprocess.run(
        [pdftoppm, "-png", "-r", "150", "-f", "1", "-l", "1", str(pdf), str(raw_prefix)],
        check=True,
    )
    rendered = next(
        (p for p in (out_dir / f"page-{suffix}.png" for suffix in ("1", "01", "001", "0001")) if p.exists()),
        None,
    )
    if rendered is None:
        raise FileNotFoundError(f"pdftoppm não gerou PNG para {pdf}")

    cover = out_dir / "cover-final.jpg"
    subprocess.run(
        [sys.executable, str(prepare_cover), str(rendered), str(cover), "--max-bytes", str(max_bytes)],
        check=True,
    )
    rendered.unlink(missing_ok=True)
    return cover


def db_dsn(values: dict[str, str], host: str | None, port: int | None) -> str:
    dsn = values.get("IMPORTER_DB_DSN")
    if not dsn:
        raise SystemExit("IMPORTER_DB_DSN ausente no .env")
    if host:
        return dsn_with_host_port(dsn, host, port or 5432)
    return dsn


def rehome(
    item_id: int,
    cur,
    tmp_dir: Path,
    opener: urllib.request.OpenerDirector,
    max_cover_bytes: int,
    pdftoppm: str,
    prepare_cover: Path,
) -> str:
    cur.execute("SELECT metadata_json FROM importer.queue_items WHERE id = %s", (item_id,))
    row = cur.fetchone()
    if row is None:
        raise LookupError(f"item {item_id} não existe na fila")
    meta = row[0] or {}
    manifest = dict(meta.get("manifest") or {})
    source_url = manifest.get("source_url")
    if not source_url:
        raise ValueError("manifest sem source_url")

    out_dir = tmp_dir / f"triage-{item_id}"
    pdf = out_dir / "source.pdf"
    notes: list[str] = []
    if pdf.exists() and pdf.stat().st_size > 100_000:
        notes.append(f"pdf reaproveitado {pdf.stat().st_size / 1e6:.2f}MB")
    else:
        notes.append(f"pdf baixado {download_pdf(source_url, pdf, opener) / 1e6:.2f}MB")

    cover = render_cover(pdf, out_dir, max_cover_bytes, pdftoppm, prepare_cover)
    notes.append(f"capa {cover.stat().st_size / 1024:.0f}KB")

    manifest["downloaded_pdf_path"] = str(pdf)
    manifest["downloaded_cover_path"] = str(cover)
    manifest["manifest_path"] = str(out_dir / "manifest.json")
    meta["manifest"] = manifest

    triage = dict(meta.get("triage") or {})
    triage["preview_pages"] = [str(cover)]
    triage["assets_rehomed"] = "current_runtime"
    meta["triage"] = triage

    cur.execute(
        "UPDATE importer.queue_items SET metadata_json = %s, updated_at = now() WHERE id = %s",
        (json.dumps(meta, ensure_ascii=False), item_id),
    )
    return ", ".join(notes)


def main() -> int:
    parser = argparse.ArgumentParser(description="Materializa assets do importer no runtime atual.")
    parser.add_argument("--ids", nargs="+", type=int, required=True)
    parser.add_argument("--env-file", type=Path, default=None)
    parser.add_argument("--importer-dir", type=Path, default=None)
    parser.add_argument("--tmp-dir", type=Path, default=None)
    parser.add_argument("--dsn-host", help="Sobrescreve host do IMPORTER_DB_DSN, útil para túnel SSH local.")
    parser.add_argument("--dsn-port", type=int, help="Sobrescreve porta do IMPORTER_DB_DSN.")
    parser.add_argument("--max-cover-bytes", type=int, default=250_000)
    args = parser.parse_args()

    env_file = resolve_env_file(args.env_file)
    values = load_env(env_file)
    agent_dir = resolve_agent_dir(env_file)
    importer_dir = args.importer_dir or resolve_runtime_path(
        values.get("SHAREBOOK_EBOOK_IMPORTER_DIR"),
        sibling_repo(agent_dir, "sharebook-ebook-importer"),
    )
    tmp_dir = args.tmp_dir or resolve_runtime_path(
        values.get("SHAREBOOK_IMPORTER_TMP_DIR"), importer_dir / "var" / "tmp"
    )
    prepare_cover = agent_dir / "scripts" / "covers" / "prepare_cover.py"
    if not prepare_cover.exists():
        raise SystemExit(f"prepare_cover.py não encontrado: {prepare_cover}")

    pdftoppm = find_pdftoppm(values)
    opener = build_opener()
    conn = psycopg2.connect(db_dsn(values, args.dsn_host, args.dsn_port))
    cur = conn.cursor()

    ok = 0
    fail = 0
    for item_id in args.ids:
        try:
            print(f"#{item_id} -> {rehome(item_id, cur, tmp_dir, opener, args.max_cover_bytes, pdftoppm, prepare_cover)}  OK")
            conn.commit()
            ok += 1
        except Exception as exc:
            conn.rollback()
            print(f"#{item_id} ERRO: {exc}", file=sys.stderr)
            fail += 1

    cur.close()
    conn.close()
    print(f"\n{ok} ok  |  {fail} falhou")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
