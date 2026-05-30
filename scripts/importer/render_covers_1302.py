import subprocess, json, psycopg2
from pathlib import Path

PDFTOPPM = r"C:\Users\raffa\AppData\Local\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-25.07.0\Library\bin\pdftoppm.exe"
PREVIEW_DIR = Path(r"C:\Repos\SHAREBOOK\sharebook-ebook-importer\var\triage\preview-pages")
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

ITEMS = [1302]

conn = psycopg2.connect(
    host="212.85.23.202", port=5432, dbname="sharebook_importer",
    user="sharebook_ai_rw", password="F%Ljy9oxTA3iR#npW%4W9iaSaJKU", sslmode="disable"
)
cur = conn.cursor()

for item_id in ITEMS:
    pdf = Path(r"C:\Users\raffa\Downloads") / f"{item_id}.pdf"
    out_prefix = PREVIEW_DIR / f"{item_id}-page"
    # remove ppm gerado anteriormente
    for f in PREVIEW_DIR.glob(f"{item_id}-page*.ppm"):
        f.unlink()
    subprocess.run([PDFTOPPM, "-png", "-r", "150", "-l", "1", str(pdf), str(out_prefix)], check=True)
    png = PREVIEW_DIR / f"{item_id}-page-1.png"
    if not png.exists():
        alt = PREVIEW_DIR / f"{item_id}-page-01.png"
        if alt.exists():
            alt.rename(png)
    print(f"#{item_id} → {png}  exists={png.exists()}")

    cur.execute("SELECT metadata_json FROM importer.queue_items WHERE id = %s", (item_id,))
    meta = cur.fetchone()[0] or {}
    triage = meta.get("triage", {})
    triage["preview_pages"] = [str(png)]
    meta["triage"] = triage
    cur.execute("UPDATE importer.queue_items SET metadata_json = %s WHERE id = %s",
                (json.dumps(meta), item_id))

conn.commit()
conn.close()
print("Done.")
