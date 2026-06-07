# Ciclo Manual Windows

Usado quando o worker automático falha (`source_blocked`, PDF grande demais) e o PDF precisa ser processado a partir do Windows local.

---

## ⚠️ Regra crítica: não rodar triage no Windows (exceto validação)

**Nunca rodar `triage-once` no Windows para avançar um item de verdade.** O triage materializa arquivos localmente (`var/tmp/triage-<ID>/`). O worker de publish roda no OpenClaw e espera encontrar esses arquivos lá — se foram criados no Windows, o publish falha.

**Exceção permitida**: rodar `triage-once` no Windows *apenas para validar* que o worker conseguiria processar o item (ex: confirmar que um PDF direto é acessível). Nesse caso, após a validação, resetar o item para `waiting_triage` e deixar o OpenClaw triá-lo de verdade.

---

## Quando usar

- Item em `source_blocked` com PDF baixável manualmente (WAF, signed URL, domínio migrado)
- Item em `error` com "pdf grande demais" — nginx `client_max_body_size` bloqueia upload direto
- PDF já disponível em `C:\Users\raffa\Downloads\<id>.pdf`

---

## Pré-requisitos

```powershell
pip install psycopg2 pypdf pikepdf boto3   # já instalados
winget install oschwartz10612.Poppler --scope user   # pdftoppm para capas
```

`pdftoppm` fica em:
```
C:\Users\raffa\AppData\Local\Microsoft\WinGet\Packages\
  oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\
  poppler-25.07.0\Library\bin\pdftoppm.exe
```

**Token**: verificar antes de começar. Se houver 401, rodar:
```powershell
python scripts/production/sharebook_refresh_token.py
```

---

## Sequência canônica

### Passo 1 — Triagem manual (opcional)

Usar quando o item ainda está em `source_blocked` sem metadata de triagem.

```powershell
cd C:\Repos\SHAREBOOK\sharebook-agent
python skills/importers/ebook-importer/scripts/manual_triage_windows.py --ids <id1> <id2>
```

Replica `TriageWorker.run_once()`: valida magic bytes, extrai texto, checa duplicata, monta `metadata_json`, move para `waiting_editorial`.

PDFs esperados em `C:\Users\raffa\Downloads\<id>.pdf`.

### Passo 2 — Plano editorial

Ler o `editorial_prompt` da source no banco:
```sql
SELECT name, editorial_prompt FROM importer.sources WHERE name = '<source_name>';
```

Salvar o plano via CLI (canônico — não criar script one-shot):
```powershell
cd C:\Repos\SHAREBOOK\sharebook-ebook-importer
python cli.py plan-set --id <ID> --category-id <UUID> --synopsis-file <FILE> --author "<AUTOR>"
```

Se a decisão humana for não publicar após a triagem, usar o comando canônico:

```powershell
cd C:\Repos\SHAREBOOK\sharebook-ebook-importer
python cli.py editorial-reject --id <ID> --reason "<motivo humano claro>"
```

Opcionalmente, informar `--rejected-by <identificador>`. Não usar `status-set` genérico como playbook de rejeição editorial.

**Nota**: o worker automático pode resetar o item para `waiting_triage` ("item sem PDF materializado"). Ignorar — o próximo passo bypassa o worker.

### Passo 3 — Capa

```powershell
cd C:\Repos\SHAREBOOK\sharebook-agent
python skills/importers/ebook-importer/scripts/render_covers.py --ids <id1> <id2>
```

Renderiza página 1 como PNG, grava path em `metadata_json.triage.preview_pages`.

### Passo 4 — Publicação (fake PDF + S3)

```powershell
python skills/importers/ebook-importer/scripts/publish_fake_pdf.py --id <ID>
```

Fluxo:
1. Publica com `C:\Temp\fake.pdf` (287 bytes) — cria o livro, obtém slug e S3 key
2. Aprova o livro
3. Upload do PDF real para o S3 key retornado via `boto3`
4. Marca item como `done` no banco

---

## Por que o workaround de PDF fake

O nginx tem `client_max_body_size` restritivo na rota `/api/Book`. PDFs grandes falham com `WinError 10053/10054` quando o request vem de fora do servidor. Do OpenClaw funciona (conexão interna). Do Windows, não.

Criar `C:\Temp\fake.pdf` uma vez:
```python
from pathlib import Path
minimal = (
    b'%PDF-1.0\n1 0 obj<</Type /Catalog /Pages 2 0 R>>endobj\n'
    b'2 0 obj<</Type /Pages /Kids [3 0 R] /Count 1>>endobj\n'
    b'3 0 obj<</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]>>endobj\n'
    b'xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n'
    b'0000000058 00000 n\n0000000115 00000 n\n'
    b'trailer<</Size 4 /Root 1 0 R>>\nstartxref\n190\n%%EOF'
)
Path(r'C:\Temp\fake.pdf').write_bytes(minimal)
```

---

## Armadilhas conhecidas

| Problema | Causa | Solução |
|---|---|---|
| Worker reseta para `waiting_triage` | "item sem PDF materializado" — PDF no Windows, não no servidor | Ignorar, `publish_fake_pdf.py` bypassa o worker |
| `WinError 10053/10054` no publish | nginx `client_max_body_size` | PDF fake + S3 direto |
| 401 no publish | Token expirado | `sharebook_refresh_token.py` |
| pdftoppm não encontrado | winget atualiza PATH mas requer nova sessão | Usar path absoluto no script |
| PNG com sufixo errado (`-001` em vez de `-1`) | pdftoppm usa N dígitos conforme total de páginas | `render_covers.py` já normaliza automaticamente |
| PowerShell here-string falha | `'@` deve estar na coluna 0 | `@'...'@` com `'@` na margem esquerda |

---

## Scripts

Ver `scripts.md` para índice completo. Scripts do ciclo manual:

| Script | Uso |
|---|---|
| `skills/importers/ebook-importer/scripts/manual_triage_windows.py` | Triagem: `source_blocked` → `waiting_editorial` |
| `skills/importers/ebook-importer/scripts/render_covers.py` | Capa: página 1 do PDF como PNG |
| `skills/importers/ebook-importer/scripts/publish_fake_pdf.py` | Publish: fake PDF + S3 real → `done` |
