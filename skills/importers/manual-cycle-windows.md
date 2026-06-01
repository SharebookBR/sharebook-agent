# Skill — Ciclo Manual Completo no Windows

Usado quando itens ficam `source_blocked` (extrator automático falhou) e os PDFs foram baixados manualmente. Cobre o ciclo completo: triagem → curadoria editorial → capas → publicação.

---

## Quando usar

- Um ou mais itens estão em `source_blocked` ou `waiting_triage` sem PDF acessível publicamente
- Raffa baixou os PDFs manualmente para `C:\Users\raffa\Downloads\<id>.pdf`
- Publicação precisa ser feita do Windows (não do OpenClaw)

---

## Pré-requisitos

```
pip install psycopg2 pypdf pikepdf boto3   # já devem estar instalados
winget install oschwartz10612.Poppler --scope user   # pdftoppm para capas
```

pdftoppm fica em:
```
C:\Users\raffa\AppData\Local\Microsoft\WinGet\Packages\
  oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\
  poppler-25.07.0\Library\bin\pdftoppm.exe
```

**Token antes de começar**: verificar se o token da API ainda é válido. Se houver 401 no primeiro request, rodar:
```powershell
python scripts/production/sharebook_refresh_token.py
```
O script já grava o novo token no `.env` automaticamente.

---

## Passo 1 — Triagem manual

Script: `scripts/importer/manual_triage_windows.py`

```
python manual_triage_windows.py --ids <id1> <id2> ...
```

O que faz (replica `TriageWorker.run_once()`):
- Valida magic bytes (`%PDF-`)
- Extrai texto das primeiras 15 páginas
- Checa duplicata em produção pelo título exato
- Monta `metadata_json` no formato canônico
- Cria run, marca `triaging` → `waiting_editor`, fecha run
- Em falha: marca `source_blocked` com `last_error`

PDFs esperados em `C:\Users\raffa\Downloads\<id>.pdf`.

---

## Passo 2 — Curadoria editorial

Ler o `editorial_prompt` da source no banco:

```sql
SELECT name, editorial_prompt FROM importer.sources WHERE name = '<source_name>';
```

Para cada item: inspecionar o ToC do PDF, escrever sinopse + atribuir categoria.

Criar um script one-shot baseado em `scripts/importer/set_plans_1265_1298.py` como template:

```python
PLANS = [
    {
        "id": <id>,
        "planned_title": "...",
        "planned_author": "...",
        "planned_category_id": DEVOPS_ID,   # ou DADOS_ID / GERAL_ID
        "planned_synopsis": "...",
        "planned_by": "manual_windows",
    },
    ...
]
```

Executar: `python set_plans_<batch>.py` → itens vão para `waiting_process`.

**Atenção:** o worker automático do servidor pega itens `waiting_process` imediatamente. Se o PDF não estiver acessível pelo servidor, ele seta `waiting_triage` de volta (`classify_failure_status` → "item sem PDF materializado"). Ignorar: o próximo passo contorna isso.

---

## Passo 3 — Capas

Script: `scripts/importer/render_covers_<batch>.py` (baseado em `render_covers_1265_1298.py`)

Renderiza a página 1 de cada PDF como PNG e grava o path em `metadata_json.triage.preview_pages`.

PNGs vão para:
```
C:\Repos\SHAREBOOK\sharebook-ebook-importer\var\triage\preview-pages\<id>-page-001.png
```

O publish worker usa `preview_pages[0]` como capa via `recover_cover_path()`.

---

## Passo 4 — Publicação

### Por que não usar o worker diretamente

O nginx tem `client_max_body_size` restritivo na rota `/api/Book`. PDFs maiores que ~1 KB falham com `WinError 10053/10054` quando o request vem de fora do servidor. Do OpenClaw funciona (conexão interna). Do Windows, não.

### Workaround: PDF fake + S3 real

Script: `scripts/importer/publish_fake_pdf_<batch>.py` (baseado em `publish_fake_pdf_1265_1298.py`)

Fluxo:
1. Publica cada item com `C:\Temp\fake.pdf` (287 bytes, PDF válido mínimo)
2. Livro criado em produção com slug e `eBookPdfPath` corretos
3. Marca item como `done` no banco com `sharebook_book_id`
4. Faz upload dos PDFs reais para o S3 via `boto3.upload_file()` usando os keys retornados

```python
# Gerar fake.pdf uma vez:
from pathlib import Path
minimal = b"""%PDF-1.0\n1 0 obj<</Type /Catalog /Pages 2 0 R>>endobj\n..."""
Path(r"C:\Temp\fake.pdf").write_bytes(minimal)
```

```python
# Upload S3 (credenciais do .env):
import boto3
s3 = boto3.client("s3",
    aws_access_key_id=env["AWS_S3_ACCESS_KEY"],
    aws_secret_access_key=env["AWS_S3_SECRET_KEY"],
    region_name=env.get("AWS_S3_REGION", "sa-east-1"))
s3.upload_file(local_pdf, env["AWS_S3_BUCKET"], ebook_pdf_path)
```

**Nota:** `sharebook_aws_s3.py` tem bug de path (procura `.env` em `scripts/.env`, não em `sharebook-agent/.env`). Usar boto3 inline como acima.

---

## Armadilhas conhecidas

| Problema | Causa | Solução |
|---|---|---|
| Worker servidor reseta para `waiting_triage` | "item sem PDF materializado" — PDF está no Windows, não no servidor | Ignorar, o publish_fake_pdf bypassa o worker |
| `WinError 10053/10054` no publish | nginx `client_max_body_size` na rota `/api/Book` | PDF fake + S3 direto |
| pdftoppm não encontrado | winget atualiza PATH mas requer nova sessão | Injetar o bin dir em `$env:PATH` ou usar path absoluto no script |
| PowerShell here-string falha | `'@` deve estar na coluna 0, sem indentação | `@'...'@` com `'@` na margem esquerda |
| `sharebook_aws_s3.py` não acha `.env` | Path calculado como `scripts/.env` | Usar boto3 inline com `.env` lido manualmente |
| 401 no primeiro request | Token expirado | `python scripts/production/sharebook_refresh_token.py` |
| pdftoppm gera sufixo `-001` em vez de `-1` | PDFs com 100–999 páginas geram 3 dígitos; ≥1000 páginas geram 4 | O sufixo depende do total de páginas: ≤9 → `-1`, ≤99 → `-01`, ≤999 → `-001`, ≥1000 → `-0001`. Renomear manualmente ou adaptar o script de capas para detectar o sufixo correto |
| 415 no publish | Enviando multipart em vez de JSON+base64 | A rota `/api/Book` usa JSON com campos `PdfBytes` e `ImageBytes` em base64. Ver `sharebook_prod_book.py` como referência |

---

## Scripts de referência

| Script | Propósito |
|---|---|
| `scripts/importer/manual_triage_windows.py` | Triagem manual replicando o TriageWorker |
| `scripts/importer/set_plans_1265_1298.py` | Template de planos editoriais (adaptar por batch) |
| `scripts/importer/render_covers_1265_1298.py` | Renderização de capas com pdftoppm |
| `scripts/importer/publish_fake_pdf_1265_1298.py` | Publicação com PDF fake + upload S3 real |
