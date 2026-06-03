import psycopg2, json

conn = psycopg2.connect(
    host="212.85.23.202", port=5432, dbname="sharebook_importer",
    user="sharebook_ai_rw", password="F%Ljy9oxTA3iR#npW%4W9iaSaJKU", sslmode="disable"
)
cur = conn.cursor()
cur.execute("SELECT metadata_json FROM importer.queue_items WHERE id = 1086")
meta = cur.fetchone()[0]
meta["subject"] = "0 - Meta-Lists"
cur.execute(
    "UPDATE importer.queue_items SET metadata_json = %s WHERE id = 1086",
    (json.dumps(meta, ensure_ascii=False),)
)
conn.commit()
print(f"subject restaurado: {meta['subject']}")
conn.close()
