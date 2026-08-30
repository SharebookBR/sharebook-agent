# Ciclo Manual Windows

Ciclo completo de processamento de um item a partir do Windows local, incluindo os casos em que o worker remoto não dá conta sozinho (`source_blocked`, PDF grande demais) ou ainda não passou pelo preflight.

O OpenClaw entrou em reativação em 2026-08-30. Este fluxo continua sendo o fallback canônico até cron, checkout e assets remotos serem validados no novo container.

---

## ⚠️ Regra crítica: triage e publish no mesmo habitat

`triage-once` materializa arquivos em `var/tmp/triage-<ID>/`; o publish precisa enxergar exatamente esses assets.

- Se o item seguirá pelo worker remoto, triage e publish rodam no OpenClaw.
- Se o item seguirá por este ciclo, os assets ficam no Windows e são espelhados nos paths do Passo 3b.
- Não triar no Windows esperando que um publish remoto encontre os arquivos — os habitats não compartilham filesystem.

**Pendência aberta**: a metade `publish-once` está validada em produção — 4 itens (1553, 1502, 1582, 1471) publicados em 2026-08-17 direto do Windows, uma tentativa cada, com os assets espelhados pelo Passo 3b. O que **continua não validado** é a metade `triage-once`: nessas quatro publicações a triagem já existia no banco (feita pelo runtime antigo) e só os arquivos foram materializados na mão. Rodar `triage-once` no Windows e emendar no publish sem intervenção segue sem prova.

---

## Quando usar

- Item em `source_blocked` com PDF baixável manualmente (WAF, signed URL, domínio migrado)
- Item em `error` com "pdf grande demais" — mas confirmar o limite real antes, ver Passo 4
- PDF já disponível em `C:\Users\raffa\Downloads\<id>.pdf`
- **Item triado antes de 2026-08-16 com assets apontando para `/data/workspace/...`** — o volume antigo foi apagado; ver "Assets órfãos do volume removido"

---

## Assets órfãos do volume removido

Itens triados pelo container OpenClaw têm `metadata_json.manifest.downloaded_pdf_path` e
`triage.preview_pages` apontando para `/data/workspace/sharebook-ebook-importer/var/tmp/triage-<ID>/`.
O path pode voltar a existir no novo container, mas os arquivos antigos não: o volume de 16/08 foi apagado. A triagem no banco está íntegra
(`context_text`, `mode`, `reason`), mas o publisher resolve o PDF por caminho absoluto do manifest e
falha com **"item sem PDF materializado pela triagem"**.

Em 2026-08-17 havia 96 itens em `waiting_editorial` nessa situação. O conserto é baixar o PDF de novo
de `manifest.source_url` e reapontar os caminhos:

```powershell
cd C:\Repos\SHAREBOOK\sharebook-agent
python skills/importers/ebook-importer/scripts/materialize_assets_windows.py --ids <id1> <id2>
```

O script é idempotente (reaproveita PDF já baixado) e faz merge no `metadata_json` — não sobrescreve
`context_text` nem os campos de triagem. Depois dele o item publica pelo worker normal.

**Atenção**: `manifest.source_url` não é sempre a URL final do asset. Já apareceram duas falhas:
- Springer (`link.springer.com/content/pdf/...`) devolve HTML; o PDF real do mesmo livro estava em
  `automl.org`. O script aborta com "resposta não é PDF" em vez de gravar lixo — resolver a URL na mão.
- URLs `.php?chapter=...` (opentextbookstore) penduram sem responder. Não insistir; tratar como fonte
  a resolver manualmente.

## Publish remoto via SSH/docker exec

Só usar depois do preflight do novo container. Itens triados pelo worker do OpenClaw devem ter `source.pdf` e `preview-pages/` materializados no mesmo checkout; nesse caso não usar o workaround de fake PDF + S3.

Antes de qualquer workaround Windows, checar os assets no lugar certo:

```powershell
python scripts/infra/vps_ssh.py --prefix VPS_HOSTGATOR_SSH --cmd "docker exec <container_openclaw> ls /data/workspace/sharebook-ebook-importer/var/tmp/triage-<ID>/"
```

Existindo os assets, disparar o worker canônico por ID dentro do container:

```powershell
python scripts/infra/vps_ssh.py --prefix VPS_HOSTGATOR_SSH --cmd "docker exec <container_openclaw> sh -lc 'cd /data/workspace/sharebook-ebook-importer && python3 cli.py publish-once --id <ID>'"
```

O padrão remoto foi validado no runtime antigo em 2026-07-11 (item 1367). O novo container exige nova prova antes de virar caminho verde.

Após publicar, validar no catálogo real: rota do frontend é `/livros/:slug` (não `/livro/:slug`).

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

**Python**: o PATH pode ter Python 3.14 como `python`, mas o ambiente operacional com todas as dependências (`psycopg2`, `boto3`, `dotenv`) é o **Python 3.12**:
```
C:\Users\raffa\AppData\Local\Programs\Python\Python312\python.exe
```
Se `python` retornar 3.14 e falhar na importação de deps, usar o caminho completo acima. Verificar: `python --version`.

Se `boto3` não estiver no Python 3.12: `pip install --user boto3` (instalado no usuário, não precisa de admin).

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

**Atenção ao tamanho da capa**: PNG gerado pode ultrapassar 800KB. Um payload grande (capa + PDF) causa `SSLEOFError` na API. Comprimir a capa para JPEG (~86KB) antes de publicar resolve o problema:
```python
from PIL import Image
img = Image.open(r"C:\Users\raffa\Downloads\<id>-cover.png")
img.save(r"C:\Users\raffa\Downloads\<id>-cover.jpg", "JPEG", quality=75)
```
Atualizar o path da capa em `metadata_json.triage.preview_pages` após compressão.

### Passo 3b — Worker normal (alternativa ao fake PDF)

Quando o PDF não é grande demais para o nginx, é possível usar o worker normal no Windows. Para isso, o worker espera os assets nos caminhos canônicos POSIX do importer — que não existem naturalmente no Windows e precisam ser espelhados:

```
C:\data\workspace\sharebook-ebook-importer\var\tmp\triage-<ID>\source.pdf
C:\data\workspace\sharebook-ebook-importer\var\tmp\triage-<ID>\preview-pages\page-01.png
```

Materializar (espelhar) os assets nesses caminhos antes de rodar `publish-once`.

**`publish-once` aceita `--id`** no CLI atual. Para publicar um item específico pelo worker normal, preferir:
```powershell
cd C:\Repos\SHAREBOOK\sharebook-ebook-importer
python cli.py publish-once --id <ID>
```

`--source <SOURCE> --limit 1` continua válido para processar o próximo elegível da source, mas não deve substituir `--id` quando a intenção é um item conhecido.

Sequência de diagnóstico quando `SSLEOFError` persiste:
1. Checar tamanho da capa — comprimir se > ~300KB.
2. Verificar se o PDF é realmente grande; se sim, usar fake PDF + S3.
3. Renovar token se aparecer `401` em qualquer chamada.
4. Verificar catálogo e importer (`sharebook_prod_book.py`, SELECT no banco) após cada tentativa.
5. Não fazer retries cegos sem mudar a hipótese entre tentativas.

### Passo 4 — Publicação (fake PDF + S3) — **exceção, não default**

> **Limite real medido em 2026-08-17**: PDFs de **34,1 MB e 35,7 MB** subiram pelo worker normal
> (`publish-once --id`) direto do Windows, em uma tentativa, sem `WinError 10053/10054` e sem
> Ghostscript. O nginx **não** barrou. A hipótese antiga de que PDF grande obriga o fake PDF estava
> calibrada errada — provavelmente por confundir o limite do nginx com o estimador do próprio importer.
>
> **Sempre tentar `publish-once --id` primeiro**, independente do tamanho. O teto conhecido do importer
> é `upload_request_limit_bytes` (default 52.428.800), com expansão base64 de 1,37 e margem de
> 1.500.000 — ou seja, PDF útil de ~37 MB. Acima disso o próprio worker tenta Ghostscript antes de
> desistir. Só cair para o fake PDF diante de falha real e observada.

```powershell
python skills/importers/ebook-importer/scripts/publish_fake_pdf.py --id <ID> `
  --pdf-path <CAMINHO_DO_PDF_REAL> `
  --cover-path <CAMINHO_DA_CAPA_FINAL>
```

Fluxo:
1. Publica com `C:\Temp\fake.pdf` (287 bytes) — cria o livro, obtém slug e S3 key
2. Aprova o livro
3. Upload do PDF real para o S3 key retornado via `boto3`
4. Marca item como `done` no banco

---

## Por que o workaround de PDF fake

A justificativa histórica: o nginx teria `client_max_body_size` restritivo na rota `/api/Book`, e PDFs grandes falhariam com `WinError 10053/10054` vindos de fora do servidor. Enquanto existiu runtime dentro da VPS, a conexão interna contornava o limite.

**Revisão de 2026-08-17**: esse diagnóstico não se sustenta na faixa em que era invocado. Dois PDFs de ~34 e ~36 MB subiram do Windows sem nenhum erro de transporte. Ou o limite do nginx é bem mais alto do que se supunha, ou foi afrouxado em algum momento sem o corpus registrar. O gargalo real do fluxo hoje é o estimador do importer (`upload_request_limit_bytes`), não o proxy.

Portanto: o fake PDF continua existindo para PDF genuinamente acima do teto do importer, mas **deixou de ser a rota esperada para "PDF grande"**. Antes de usá-lo, é obrigatório ter em mãos a falha observada — traceback ou log real —, não a expectativa de falha.

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
| "item sem PDF materializado pela triagem" | manifest aponta para `/data/workspace/...` do container morto | `materialize_assets_windows.py --ids <id>`, depois `publish-once --id` |
| Worker reseta para `waiting_triage` | "item sem PDF materializado" — PDF no Windows, não no servidor | Ignorar, `publish_fake_pdf.py` bypassa o worker |
| `WinError 10053/10054` no publish | Antes atribuído ao nginx; **não reproduzido em 34–36 MB em 2026-08-17** | Coletar o erro real antes de concluir; só então PDF fake + S3 |
| Capa é folha de rosto, não capa | Página 1 de livro acadêmico costuma ser título + sumário | Gerar capa com `scripts/covers/generate_covers.py` e passar `--cover-path` no `plan-set` |
| `head_object` do S3 não acha a capa | Capa não vive no S3 — é servida por `api.sharebook.com.br/Images/Books/<slug>.jpg` | Validar a capa pela URL da API, não pelo bucket |
| `SSLEOFError` no publish com fake PDF | Capa PNG grande (>300KB) fecha a conexão | Comprimir capa para JPEG ~86KB antes de publicar |
| 401 no publish | Token expirado | `sharebook_refresh_token.py` |
| pdftoppm não encontrado | winget atualiza PATH mas requer nova sessão | Usar path absoluto no script |
| PNG com sufixo errado (`-001` em vez de `-1`) | pdftoppm usa N dígitos conforme total de páginas | `render_covers.py` já normaliza automaticamente |
| PowerShell here-string falha | `'@` deve estar na coluna 0 | `@'...'@` com `'@` na margem esquerda |
| `editor-next` retorna paths `/data/workspace/` | CLI usa paths canônicos POSIX independente do habitat; esses caminhos não existem em lugar nenhum hoje | Traduzir mentalmente; espelhar assets em `C:\data\workspace\...` |
| `python` no PATH é 3.14 sem deps | Python 3.14 instalado depois, sobrescreve PATH | Usar Python 3.12 explícito: `C:\Users\raffa\AppData\Local\Programs\Python\Python312\python.exe` |
| `publish-once --id` diverge da documentação antiga | O CLI ganhou seleção por ID e o manual ficou para trás | Confirmar com `python cli.py publish-once --help` e preferir `--id <ID>` para publicação dirigida |
| `boto3` não encontrado no Python 3.12 | Instalado no 3.14, não no 3.12 | `pip install --user boto3` (no Python 3.12) |
| `last_error` sobrevive à publicação por rota manual antiga | Script ou ajuste direto marcou `done` sem limpar o erro herdado | `publish_fake_pdf.py` atual já limpa `last_error` e `retry_after`; em outra rota manual, validar e limpar conscientemente |

---

## Scripts

Ver seção **Scripts** em `SKILL.md` para índice completo. Scripts do ciclo manual:

| Script | Uso |
|---|---|
| `skills/importers/ebook-importer/scripts/manual_triage_windows.py` | Triagem: `source_blocked` → `waiting_editorial` |
| `skills/importers/ebook-importer/scripts/render_covers.py` | Capa: página 1 do PDF como PNG |
| `skills/importers/ebook-importer/scripts/publish_fake_pdf.py` | Publish excepcional: `--id`, `--pdf-path` e `--cover-path`; fake PDF + S3 real → `done` |
