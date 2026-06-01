---
name: public-ebook-importer
description: Opera e recupera o importer de ebooks públicos/gratuitos do Sharebook. Use quando precisar sincronizar fila, rodar triagem mecânica, preparar publicação, publicar/aprovar ebooks, revisar status canônico, ajustar ou reinstalar cron local do importer, reanimar o worker após restart de container, diagnosticar ambiente quebrado ou revisar a operação do repositório sharebook-ebook-importer.
---

# Sharebook Public Ebook Importer

Skill única do importer. Sem teatro.

## Quando usar

Use esta skill para qualquer operação do `sharebook-ebook-importer`, especialmente:

- sincronizar source/fila
- rodar `triage-once`
- rodar `publish-once`
- revisar `retry_later`, `error`, `waiting_editor`, `waiting_process` por ID
- instalar, remover, auditar ou reinstalar o cron local
- reanimar worker quebrado após restart de container
- diagnosticar ausência de bins/deps mínimas no ambiente
- operar ou recuperar o handoff editorial automático (`editor-next` + `plan-set`)
- diagnosticar logs e estado do importer

## Fonte da verdade

Antes de diagnosticar importer neste habitat, partir do container OpenClaw local onde o agente roda. Checar host remoto por SSH ou outro container (`sharebook-api`) pode fabricar falso negativo sobre ausência de repo, `cli.py` ou artefatos. O repo íntegro do importer fica visível neste mesmo container.

A fonte da verdade operacional agora é o repositório:

- `/data/workspace/sharebook-ebook-importer/README.md`
- `/data/workspace/sharebook-ebook-importer/cli.py`
- `/data/workspace/sharebook-ebook-importer/setup-importer-cron.sh`

Se esta skill divergir do código/README do importer, o importer manda.

## Guardrails curtos

- **ID Único**: O campo `position` foi EXORCIZADO. Toda operação manual deve usar `--id`.
- PostgreSQL é a única fonte da verdade. O banco de dados do importer é `sharebook_importer` (não confundir com o banco principal `sharebook`).
- não inventar status fora do conjunto canônico.
- `duplicate` não é `done`.
- `triage_rejected` conta como como erro.
- se falha temporária já cabe em `retry_later`, não usar `error`.
- se faltar editorial, devolver para `waiting_editor`, não mascarar como erro técnico.
- cron agentic do OpenClaw não é o default saudável para triagem mecânica ou publish Python.
- bootstrap/recovery local é tapa-buraco operacional, não substitui correção no build/deploy.
- **`metadata_json` é acumulativo**: cada etapa do pipeline deve fazer merge, nunca sobrescrever cegamente. `pg_db.mark_item()` deve preservar campos anteriores. Erosão de metadata entre triagem, editorial e publish é bug estrutural.
- **`sys.executable` em scripts Python**: nunca hardcode `python3` ou `python` — no Windows, `python3` resolve para o stub do Microsoft Store (rc=9009). Usar `sys.executable` é o fix correto e cross-platform.
- **Editorial por source vive no banco**: `importer.sources.editorial_prompt` é a fonte da verdade. Skills por source são obsoletas. Sempre consultar o banco antes de preparar editorial.
- **Categorias sempre folha**: antes de mapear categorias numa sinopse/plan, consultar `GET /api/category/Counts` para obter IDs reais. Nunca inventar categoria.

## Status canônico

- `waiting_triage`
- `triaging`
- `triage_rejected`
- `waiting_editor`
- `editing`
- `waiting_process`
- `processing`
- `done`
- `retry_later`
- `source_blocked`
- `duplicate`
- `error`

## Workflow real atual

### 1. Triagem mecânica

Comando:

```bash
cd /data/workspace/sharebook-ebook-importer
set -a && . /data/workspace/sharebook-agent/.env && set +a
python cli.py triage-once --source baixelivros_infantil
```

O `triage_worker.py` deve:
- pegar item em `waiting_triage`
- extrair da fonte via `extractors/`
- validar PDF real
- detectar bloqueios óbvios
- encaminhar para `waiting_editor`, `triage_rejected`, `source_blocked` ou `retry_later`

Não tentar fazer curadoria sofisticada aqui.

### 2. Handoff Editorial (Concierge)

Para obter o próximo item pronto para edição com contexto mastigado:

```bash
python cli.py editor-next --source baixelivros_infantil
```

Para salvar o plano editorial:

```bash
python cli.py plan-set --id <ID> --category-id <UUID> --synopsis-file <ARQUIVO_TEMP> --author "<AUTOR>"
```

### 3. Publicação/aprovação

Comando:

```bash
cd /data/workspace/sharebook-ebook-importer
set -a && . /data/workspace/sharebook-agent/.env && set +a
python cli.py publish-once --source baixelivros_infantil
```

O fluxo de publicação deve:
- pegar item em `waiting_process`
- validar plano editorial
- checar duplicata em produção
- criar e aprovar ebook
- marcar `done`, `duplicate`, `waiting_editor`, `retry_later` ou `error`

Guardrails que já sangraram em produção:
- `publish-once` consome realidade operacional, não intenção editorial.
- Para capa da fonte, o handoff precisa materializar caminho compatível com `resolve_cover_path()` antes de mandar para `waiting_process`.
- Estado inválido recorrente: `planned_cover_mode='source'` sem `manifest.downloaded_cover_path`, `local_cover` ou `planned_cover_url` termina em `capa da fonte não foi baixada`.
- O publisher precisa garantir `out_dir` explicitamente antes de gravar `synopsis.txt`. Não confiar em side effects de etapas antigas.

## Regra editorial que continua viva

- categoria final deve ser sempre folha
- sinopse final deve ter 3 parágrafos
- idioma padrão de publicação: português
- se o plano editorial estiver incompleto, o item volta para `waiting_editor`

## Capa e custo

- **proibido gerar imagens via API da OpenAI no fluxo Sharebook sem confirmação explícita do Raffa**
- se a capa da fonte servir, preferir reaproveitar
- se precisar gerar sem custo de API, usar alternativas locais já aprovadas

## Bootstrap e recovery do container

Quando o container reinicia e o importer "morre", tratar como incidente de ambiente antes de culpar fila ou código.

### Checklist mínimo de sobrevivência

Validar nesta ordem:

1. bins básicos
   - `python3`
   - `flock`
   - `cron` ou `crond`
   - `crontab`
2. bins/deps mínimas de processamento
   - `ghostscript`
   - `psycopg2`
   - `PIL`
3. arquivos canônicos existem
   - `run_worker.sh`
   - `setup-importer-cron.sh`
   - `/data/workspace/sharebook-agent/.env`
4. daemon de cron ativo
5. bloco gerenciado instalado no `crontab`
6. prova real com `triage-once` e `publish-once`

### Incidente real observado em 2026-05-23

Sintoma: o worker parecia saudável historicamente, mas os disparos pararam depois de um horário específico, sem crescer fila de `error` ou `retry_later`.

Causa real: o daemon de `cron` morreu dentro do container OpenClaw. Ficou um `pidfile` stale em `/run/crond.pid`, o `crontab` continuou instalado, os lock files continuaram existindo, mas nenhum novo pulso era disparado.

Como reconhecer rápido:
- `var/logs/importer-cron.log` para de avançar em um horário exato
- faltam os pulsos esperados de `triage-once` e `publish-once`
- `setup-importer-cron.sh status` mostra `cron_daemon=stopped`
- `pgrep -a cron` e `pgrep -a crond` não retornam processo vivo
- lock file vazio sozinho **não** prova lock ativo eterno

Ação corretiva aplicada e validada:
```bash
cd /data/workspace/sharebook-ebook-importer
cron
bash setup-importer-cron.sh status
```

Se o status voltar com `cron_daemon=running`, validar no relógio real se o próximo tick grava novo heartbeat no `var/logs/importer-cron.log`.

### Remediação rápida

Se o container vier pelado após restart:

```bash
apt-get update && apt-get install -y cron ghostscript python3-psycopg2 python3-pil
cd /data/workspace/sharebook-ebook-importer
bash setup-importer-cron.sh install
bash setup-importer-cron.sh status
```

Depois validar execução real:

```bash
cd /data/workspace/sharebook-ebook-importer
ENV_FILE=/data/workspace/sharebook-agent/.env MODE=triage-once ./run_worker.sh
ENV_FILE=/data/workspace/sharebook-agent/.env MODE=publish-once ./run_worker.sh
```

Se isso resolver, registrar mentalmente a verdade incômoda: o ambiente foi salvo por remendo local. A correção estrutural continua sendo ajustar Dockerfile/imagem/deploy para já nascer com essas dependências.

## Agendamento real: onde olhar

O importer pode ser afetado por **dois mecanismos diferentes**. Não assumir um só.

### 1. Cron Linux local do importer

Comandos canônicos:

```bash
cd /data/workspace/sharebook-ebook-importer
bash setup-importer-cron.sh install
bash setup-importer-cron.sh status
bash setup-importer-cron.sh remove
bash setup-importer-cron.sh start-daemon
```

Esse script instala duas entradas no `crontab` do container:
- `MODE=triage-once`
- `MODE=publish-once`

O detalhe fino do schedule não deve ser copiado para esta skill.
Se precisar do schedule real, consultar o próprio `setup-importer-cron.sh` ou `bash setup-importer-cron.sh status`.

Regras:
- instalar via script, não por `crontab -e` solto
- logs ficam em `var/logs/`
- lock/estado local ficam em `var/state/`

### 2. Cron agentic do OpenClaw

Existe um job interno do OpenClaw que pode mexer na fila real do importer:
- `editorial-preparer`

Esse job vive em:
- `/data/.openclaw/cron/jobs.json`

Ele não é triagem mecânica nem publish Python. Ele é preparação editorial automática baseada em `editor-next` + `plan-set`.

### Ordem certa de diagnóstico

Ao revisar incidente ou atividade "fantasma", olhar nesta ordem:
1. `crontab -l`
2. `var/logs/importer-cron.log`
3. estado no Postgres (`importer.runs`, `importer.queue_items`)
4. `/data/.openclaw/cron/jobs.json`

Se um item andou "sozinho", quase sempre a resposta está em um desses quatro lugares.

## Diagnóstico mínimo

Antes de culpar o fluxo:
- validar `IMPORTER_DB_DSN`
- se reclamar que faltam `importer.queue_items`, `importer.sources` ou `importer.runs`, a conexão está no banco errado
- se houver item preso em `processing`, `triaging` ou `editing`, destravar conscientemente
- confiar no README do importer mais do que em memória antiga

## Handoff com curadoria

`waiting_editor` e `editing` continuam sendo território natural da preparação editorial humana/LLM.

### Fluxo durável do preparador editorial automático

O modelo novo é simples e duro:
- **uma leitura** via `python cli.py editor-next --source <SOURCE>`
- **uma escrita** via `python cli.py plan-set --id <ID> ...`
- a regra editorial canônica por source vive em `importer.sources.editorial_prompt`
- não reabrir consultas extras ao banco quando o payload concierge já trouxer o contexto necessário
- quando o plano escolher capa da fonte ou `preview_pages[0]`, serializar isso em formato que o publisher já consome, preferencialmente preenchendo `manifest.downloaded_cover_path`
- `pg_db.mark_item()` deve preservar `metadata_json` existente por merge, não sobrescrever cegamente; erosão de metadata entre triagem, editorial e publish é bug estrutural

Campos esperados no payload concierge endurecido:
- `source_id`
- `source_name`
- `source_url`
- `editorial_prompt`
- artefatos visuais e contexto textual suficientes para a decisão editorial

### Regra de runtime no OpenClaw/mini

No habitat OpenClaw/mini, a invocação robusta da cron editorial deve usar shell explícito no repo correto:

```bash
cd /data/workspace/sharebook-ebook-importer && sh -c 'python3 cli.py editor-next --source <SOURCE>'
```

Não confiar em `cd` isolado num passo e `python3 cli.py ...` no passo seguinte quando a execução for agentic/cron desse runtime.

### Exceção nova: triagem manual assistida para casos WAF ou download humano já validado

Quando o item cair em `source_blocked` por WAF, JS challenge, download assinado ou proteção parecida, a régua mudou:
- **é permitido fazer triagem manual assistida** como exceção operacional
- isso não substitui o worker Python
- isso existe para destravar casos públicos que a stack simples não consegue baixar

Casos reais já observados:
- `1143` `cupola.gettysburg.edu` — WAF na primeira requisição, mas PDF baixável com browser real
- `1126` `milneopentextbooks.org` — landing page abre, PDF exige fluxo mais humano/browser

Ferramenta auxiliar criada:
- diretório: `/data/workspace/sharebook-agent/tools/browser-triage`
- base instalada: `playwright` + Chromium + libs nativas do sistema
- scripts úteis:
  - `triage_fetch.js` — inspeciona página e links candidatos
  - `download_probe.js` — tenta clique/download
  - `save_pdf_via_fetch.js` — usa browser real + fetch autenticado/contextual para salvar PDF

Quando usar:
- WAF challenge
- Cloudflare / AWS WAF / JS challenge
- download só funciona com browser real
- fonte pública parece boa, mas o worker Python falha cedo demais
- host vivo porém lento, mas o PDF já foi baixado manualmente de forma confiável para uma área neutra

Quando **não** usar:
- 404 claro
- 403 estrutural sem pista de PDF público
- login/autenticação institucional fechada sem rota pública real
- qualquer caso em que o browser não revele um PDF acessível com esforço razoável

Procedimento seguro:
1. tentar o worker normal primeiro
2. se cair em WAF/source_blocked mas parecer fonte pública legítima, usar browser assistido
3. baixar o PDF para uma área neutra (`/data/workspace/tmp/` ou `sharebook-agent/tools/browser-triage/output/`)
4. validar magic bytes `%PDF-1.x`
5. materializar manualmente em `sharebook-ebook-importer/var/tmp/triage-<ID>/source.pdf`
6. gerar `preview-pages/page-01.png` etc.
7. montar `manifest.json`
8. atualizar `metadata_json` com:
   - `local_pdf`
   - `local_cover`
   - `manifest`
   - `triage.mode = manual_browser_assisted`
   - `triage.preview_pages`
9. limpar `last_error`
10. mover para `waiting_editor`

Importante:
- fazer isso **como se fosse o worker de triagem**, não como gambiarra invisível
- registrar no metadata que foi exceção manual/browser-assisted
- não fingir que o worker Python conseguiu sozinho
- se o PDF veio por download manual validado, ainda assim materializar artefatos finais do worker (`source.pdf`, previews, manifest, metadata coerente) antes de devolver à fila

### Artefatos visuais são obrigatórios

Para preparo editorial com capa e `preview_pages`:
- leitura visual é obrigatória, não opcional
- se a tool de imagem recusar paths locais do importer fora da área permitida do agente, copiar capa e previews para um diretório permitido em `/data/workspace` antes da análise
- essa cópia é adaptação de habitat, não busca extra de contexto
- não escrever sinopse plausível com contexto visual incompleto

Sinal clássico da fricção:
- paths como `/data/workspace/sharebook-ebook-importer/var/tmp/...` podem existir, mas ainda assim serem rejeitados pela tool de imagem do agente

### Casos reais que valem heurística

- Em extractor `ebook_foundation`, algumas sources entregam HTML intermediário e exigem resolução até o PDF real, por exemplo Open Textbook Library via Pressbooks (`open/download?type=pdf` ou `print_pdf`). Corrigir só a URL inicial não basta se a capa da fonte continuar sem artefato serializado no manifest.
- Links de Google Sites podem apontar para PDFs reais em Google Docs/Drive. Aceitar `docs.google.com/file/d/...` resolvendo para `https://docs.google.com/uc?export=download&id=...` e tratar `application/octet-stream` como válido quando os bytes começam com `%PDF`.
- Quando um endurecimento arquitetural expõe falha nova, suspeitar primeiro de pré-condição implícita antes de culpar dados do item.
- Se a source estiver realmente morta, sem DNS/host resolvendo, isso é `source_blocked`, não retry teatral.

### Dependência ausente que parece erro de fila

Se surgir item em `error` no importer por falha de processamento de PDF/renderização, suspeitar cedo de dependência de sistema ausente no container.

Caso real já pago:
- ausência de `ghostscript` bloqueou processamento/publicação
- depois da instalação, o item voltou para `waiting_process` e o worker retomou normalmente

## Worker Hardening Patterns

Aprendizados consolidados de ciclos reais de triagem da `ebook_foundation_subjects`. Aplicar ao revisar ou evoluir o `triage_worker.py` e os extractors.

### Rejeição precoce (antes do extractor)

Barrar antes de qualquer download — mais barato:

- **Vídeos**: `_VIDEO_HOSTS` + `_is_video_url()` no `triage_worker.py`. Cobre YouTube, Vimeo, Twitch, Dailymotion. Mover para `triage_rejected` se confirmado vídeo.
- **Pirataria no Archive.org**: verificar `identifier` antes de consultar metadata API. Z-lib, Libgen, B-OK, Bookfi, Bookzz, Genesis → `ValueError` expressivo antes de qualquer request.

### `raise_for_restricted_html` — sinais corretos

- **Remover**: sinais genéricos de autenticação (`sign in`, `login`, `password`, `get access`, `access denied`). Esses sinais queimam páginas Open Access legítimas que têm navbar com login.
- **Manter**: sinais específicos de bloqueio de conteúdo.
- **Adicionar**: `AUTHOR_RESTRICTED_SIGNALS` para detectar "distribuição restrita pelo autor" — retornar mensagem expressiva em vez de erro genérico "sem magic bytes".
- **WAF**: detectar HTML de WAF challenge (`window.gokuProps`, `awsWafCookieDomainList`) e retornar mensagem semântica "AWS WAF challenge — requer browser com JavaScript".

### Wayback Machine

- Modificador `if_` força entrega do conteúdo bruto sem o toolbar HTML do Archive. Sem ele, `urllib.request.urlopen` recebe `text/html` mesmo para arquivos binários.
- `inject_wayback_raw_modifier`: inserir `if_` em URLs do Wayback que apontam para `.pdf`.
- `discover_assets_from_wayback_html`: extrair links de download do HTML do Wayback, tentar cada um com `if_`. Cobre padrão DotNetSlackers: entry page → `download.aspx` → PDF.
- **WebFetch bloqueia `web.archive.org`**: usar Python + `urllib` diretamente para verificar PDFs no Wayback.

### SSL fallback cross-platform

- Servidores universitários/institucionais frequentemente têm certificados quebrados.
- Detecção por string em vez de `isinstance(ssl.SSLError)` — `isinstance` funciona no Windows mas falha no Linux (OpenClaw).
- Markers: `certificate`, `ssl`, `handshake`, `hostname mismatch`.
- Aplicar fallback em `resolve_direct_pdf_assets`, `resolve_generic_http_assets` e `download_bytes`.

### Handlers especializados por família de URL

- **GitHub repo raiz**: detectar `github.com/{owner}/{repo}` (sem `/blob/`) → buscar PDF na última release via `api.github.com/repos/{repo}/releases/latest`. Preferir sem sufixos `-print`, `-scala`, `-a4`.
- **Microsoft Download Center**: nova família `microsoft_download_center`. Parsear o bloco JSON da página para extrair URL direta do PDF.
- **URL encoding**: URLs extraídas do HTML podem ter espaços no nome. Usar `urlparse` + `quote` antes de validar magic bytes.
- **freeCodeCamp**: detectar pelo prefixo `freecodecamp.org/news/`, não por substring `/book` (não casaria com `-book`).
- **bepress** (`viewcontent.cgi`): handler dedicado `resolve_bepress_assets`.

### `sync_queue` — comportamento correto

Sync só deve atualizar `title` e `updated_at` em itens **existentes**. Nunca resetar `status`, `last_error` ou metadados operacionais. A função do sync é descoberta de população, não auditoria de estado.

### EbookFoundation — padrão de curadoria

A EbookFoundation lista **plataformas/agregadores** como recursos além de livros individuais. Entradas como `dBooks homepage`, `Goalkicker`, `FreeTechBooks`, `InTech Open` chegam na fila como se fossem livros. Isso é design correto da raspagem — responsabilidade da triagem separar livros reais de diretórios e homepages. 6 dessas fontes são candidatas a novas sources no backlog.

---

## Dashboard do Importador

Funcionalidades adicionadas ao painel administrativo em 2026-05 e 2026-06.

### admin_notes

- Campo `TEXT` em `importer.queue_items` para comentários administrativos por item.
- Endpoint: `PATCH /Operations/ImporterItems/{id}/AdminNotes`
- UI: área verde (`#16a34a`) abaixo do blockquote de erro, botão "Comentário do adm" / "Editar nota".
- Grant: `GRANT UPDATE (admin_notes)` cirúrgico — não na tabela inteira.

### queue_item_history (event sourcing)

- Tabela `importer.queue_item_history` criada em 2026-05-29.
- Instrumentada em 3 pontos do `pg_db.py`: `mark_item`, `set_plan`, `set_status`.
- Campo `changed_by` semântico: `'worker'`, `'agent'`, `'admin'`.
- `from_status` nullable — primeiro registro de um item não tem "de".
- Fundação para análise de funil, tempo por status, quem moveu o quê.

### Delta D-1

Exibido nos big number cards do dashboard. Cálculo correto:
```sql
-- first_today_transition: para itens que mudaram hoje, from_status da 1ª transição = estado à meia-noite
-- unchanged_today: itens sem transição hoje = status atual (não se moveram)
-- pre_midnight = UNION ALL dos dois
-- yesterday_counts = contagem por status a partir de pre_midnight
```
- **Não usar** `last to_status antes da meia-noite` — a tabela pode ter poucos registros históricos.
- Delta zero oculto (não tem informação útil).
- Delta sempre cinza `#94a3b8` — sem julgamento de valor.
- Timezone: `America/Sao_Paulo` hardcoded (tool interna).

### Histórico por item

- Endpoint: `GET /api/Operations/ImporterItems/{id}/History`
- UI: botão "Histórico" nos cards (outline neutro `--history`), abre modal com tabela Data/De/Para.
- `changed_by` omitido da tabela — decisão operacional (sem valor para o caso de uso).
- Mobile: `overflow-x: auto` no wrapper, `min-width: unset`, padding reduzido.

---

Esta skill não substitui julgamento curatorial. Ela só descreve a operação do importer.
