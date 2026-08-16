# Ciclo Manual Windows

Ciclo completo de processamento de um item a partir do Windows local, incluindo os casos em que o worker não dá conta sozinho (`source_blocked`, PDF grande demais).

Desde 2026-08-16, com o OpenClaw dormente, **este é o único ciclo com runtime**. Não há worker agendado em lugar nenhum — todo item avança por execução manual daqui.

---

## ⚠️ Regra crítica sobre triage no Windows — pressuposto vencido

A regra antiga era: **nunca rodar `triage-once` no Windows para avançar um item de verdade**, porque o triage materializa arquivos localmente (`var/tmp/triage-<ID>/`) e o worker de publish rodava no OpenClaw, esperando encontrá-los lá.

Esse pressuposto morreu com o container. Não existe mais publish remoto, então não existe mais a divisão que a regra protegia.

O que continua verdadeiro: **triage e publish precisam ver os mesmos arquivos**. No Windows isso significa materializar os assets nos caminhos que o worker espera (Passo 3b) antes de chamar `publish-once`. Se os caminhos não baterem, o publish falha exatamente como antes — só que agora sem nenhum outro lugar para onde apontar.

**Pendência aberta**: o ciclo `triage-once` → `publish-once` inteiramente no Windows nunca foi validado ponta a ponta. O que está validado em produção é o Passo 3b (assets espelhados em `C:\data\workspace\...` + `publish-once`) e o Passo 4 (fake PDF + S3). Não presumir que a triagem local encaixa sozinha no resto — validar antes de tratar como caminho canônico.

---

## Quando usar

- Item em `source_blocked` com PDF baixável manualmente (WAF, signed URL, domínio migrado)
- Item em `error` com "pdf grande demais" — nginx `client_max_body_size` bloqueia upload direto
- PDF já disponível em `C:\Users\raffa\Downloads\<id>.pdf`

## Publish remoto via SSH/docker exec — dormente

> **Status: dormente desde 2026-08-16.**
> O container OpenClaw foi desprovisionado. Não presumir este runtime disponível no presente.
> Este trecho é preservado intencionalmente para tornar barato um eventual retorno — não apagar.
>
> **No presente**: não existe atalho remoto. Todo item cai no ciclo manual descrito abaixo. O `vps_ssh.py` continua útil para a VPS em si (containers de backend, frontend, banco), só não há mais container do agente para entrar.

Enquanto o habitat existiu, itens triados pelo worker do OpenClaw já tinham os assets (`source.pdf`, `preview-pages/`) materializados no container. Nesse caso **não** se defaultava para o workaround de fake PDF + S3 — ele existe para contornar limite do nginx, não é o caminho preferencial.

Antes de qualquer workaround Windows, checava-se se dava para publicar no lugar certo:

```powershell
python scripts/infra/vps_ssh.py --cmd "docker exec <container_openclaw> ls /data/workspace/sharebook-ebook-importer/var/tmp/triage-<ID>/"
```

Existindo os assets, disparava-se o worker canônico direto dentro do container (sem materializar nada no Windows):

```powershell
python scripts/infra/vps_ssh.py --cmd "docker exec <container_openclaw> sh -lc 'cd /data/workspace/sharebook-ebook-importer && python3 cli.py publish-once --source <SOURCE> --limit 1'"
```

O item ia para `done` em uma única passada, sem fake PDF, sem upload manual de S3. Validado em produção em 2026-07-11 (item 1367).

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

### Passo 4 — Publicação (fake PDF + S3)

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

O nginx tem `client_max_body_size` restritivo na rota `/api/Book`. PDFs grandes falham com `WinError 10053/10054` quando o request vem de fora do servidor — que é sempre o caso hoje, já que a operação é toda a partir do Windows. Enquanto existiu um runtime dentro da VPS, a conexão interna contornava o limite; essa saída não existe mais, então o limite do nginx virou gargalo estrutural (item de backlog aberto, arrastado desde 06-21).

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
