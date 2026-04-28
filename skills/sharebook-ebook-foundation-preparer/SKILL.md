---
name: sharebook-ebook-foundation-preparer
description: Prepara itens da fonte ebook_foundation (status waiting_editor) para publicação no ShareBook. Curadoria editorial completa: sinopse via índice do PDF, capa gerada localmente com Pillow (sorteio de paleta + fonte + layout + elemento decorativo + gradiente + efeito de texto), categorização, metadados e publicação via worker.
---

# ShareBook Ebook Foundation Preparer

Prepara itens da `ebook_foundation` que passaram pela triagem e estão em `waiting_editor`.

## Diferenciais

- **Capa única por sorteio** — cada capa combina aleatoriamente: 10 paletas, 10 fontes, 4 layouts, 4 elementos geométricos, 3 direções de gradiente, 4 efeitos de texto. Nunca duas capas iguais.
- **Fonte sem Wikipedia** → material técnico raramente tem cobertura. Extrair contexto do **índice do PDF**.
- **Zero custo de API** — capa gerada localmente com Pillow (grátis). ChatGPT web para capa premium quando necessário.
- **Worker roda dentro do container OpenClaw** (não no host) — acesso à rede Docker do Coolify.
- **Reuso de PDF da triagem** — worker usa PDF já baixado em `triage-downloads/`.

## Pré-requisitos

- DSN PostgreSQL com senha URL-encoded (`%25` para `%`, `%23` para `#`)
- Token `TOKEN_V2` válido (não expirado)
- Worker com: `IMPORTER_DB_DSN` + `TOKEN_V2` + `PGSSLMODE=disable`
- Fontes ousadas instaladas: `fonts-kaushanscript`, `fonts-cabinsketch`, `fonts-humor-sans` (já instaladas)

## 📋 Antes de tudo: pare e leia o índice

**Regra absoluta: antes de escrever qualquer parágrafo de sinopse, você DEVE extrair e ler o índice completo do PDF.**

Nunca confiar no título, no nome da fonte ou em conhecimento prévio sobre o assunto. O título pode esconder ou distorcer o conteúdo real.

### Checklist "antes de escrever"

Responder estas 3 perguntas com base no índice, não no título:
1. **Estrutura:** qual a sequência de capítulos/tópicos? O que o material cobre do começo ao fim?
2. **Autoria:** único autor, coletivo (várias pessoas), institucional/organização? Tem licença específica?
3. **Diferencial inesperado:** tem algo que salta aos olhos e não está no título? Ex.: dicionário ortográfico em português, vimdiff, máquina do tempo, certificações, multi cloud

**O primeiro parágrafo da sinopse DEVE conter algo específico do índice** — não pode ser genérico. Se dava pra escrever sem ler o índice, está errado.

#### ⚠️ Limite de tamanho da sinopse

**A sinopse não pode ultrapassar 2000 caracteres.** Sinopses longas demais poluem a página e raramente são lidas por inteiro.

- Após escrever, verifique o tamanho: `wc -c`
- Se passar de 2000 caracteres, corte o terceiro parágrafo ou enxuga o segundo mantendo a especificidade
- Ideal: 1200-1800 caracteres — suficiente pra 3 parágrafos sem encher linguiça

#### ⚠️ Revisão ortográfica obrigatória

**Toda sinopse deve ser revisada para acentos e ortografia antes de publicar.** Erros de acentuação ("voce" em vez de "você", "nao" em vez de "não") passam imagem de descuido e prejudicam a credibilidade do acervo.

- Após escrever, leia a sinopse por completo procurando palavras sem acento
- Palavras comuns que costumam ser esquecidas: **você, não, é, já, só, através, início, através, própria, específica, através**
- Caso encontre erros em livros já publicados (do acervo existente), reporte ao operador para correção via `update`

---

## Fluxo

### 1. Buscar próximo item

```sql
SELECT id, position, title, author, source_url, metadata_json, created_at
FROM importer.queue_items
WHERE status = 'waiting_editor'
ORDER BY position
LIMIT 1;
```

### 2. Deduplicar — verificar se já foi processado

**Antes de gastar recursos com o item, verificar se ele não é duplicata de outro já processado.**

#### 2a. Verificar MD5 do PDF contra itens já publicados

O caminho do PDF está em `metadata_json->>'local_pdf'`, relativo a `triage-downloads/`. Calcule o MD5:

```bash
md5sum /data/workspace/sharebook-ebook-importer/triage-downloads/<ARQUIVO.pdf>
```

#### 2b. Comparar com outros itens da fila (inclusive de outras sources)

```sql
SELECT qi.id, qi.position, qi.title, qi.status, s.name
FROM importer.queue_items qi
JOIN importer.sources s ON s.id = qi.source_id
WHERE qi.status IN ('waiting_process', 'done')
  AND qi.id != <ITEM_ATUAL>
ORDER BY qi.position;
```

Se encontrar itens com status `done` que tenham o mesmo PDF, hash SHA-1 do conteúdo (`metadata_json->>'source_hash'`) ou mesmo título/autor, **marque o item atual como `duplicate` e PULE para o próximo**. Não desperdice sinopse, capa e worker num item duplicado.

#### 2c. Verificar duplicata no ShareBook via API

```bash
TOKEN_V2="..."
curl -s -H "Authorization: Bearer $TOKEN_V2" -H "x-requested-with: web" \
  "https://www.sharebook.com.br/api/Book/search?q=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''<TITULO> <AUTOR>'''))")" | \
  jq '.items[] | {id, title, author}'
```

Se encontrar correspondência no ShareBook, marcar como `duplicate` e pular.

#### 2d. Deduplicar PDF por hash MD5

Antes de extrair índice, compute o MD5 do PDF. Consulte itens do `waiting_editor` também — dois itens na mesma fila podem ter o mesmo arquivo (ex.: mesma obra de sources diferentes).

```sql
-- Verificar se já existe item com mesmo MD5 (via metadata_json)
SELECT qi.id, qi.position, qi.title, qi.status
FROM importer.queue_items qi
WHERE qi.metadata_json->>'pdf_md5' = '<MD5_DO_PDF>'
  AND qi.id != <ITEM_ATUAL>;
```

Se encontrar, marcar como `duplicate` e pular.

> **Nota:** o MD5 do PDF deve ser registrado em `metadata_json.pdf_md5` no momento em que o PDF é baixado (triage ou extração). Se não existir, compute agora e grave.

### 2e. Detecção de sobreposição de assunto (dedup semântico)

**Regra de ouro:** dois livros com **MD5s diferentes** ainda podem ser duplicatas se tratam do **mesmo assunto no mesmo nível**. A pergunta decisiva é:

> "O leitor que gostou deste livro teria motivo para baixar o outro?"

Se a resposta é "não, porque os dois cobrem exatamente a mesma coisa", é duplicata.
Se a resposta é "sim, porque um é básico e o outro é avançado", não é.

#### Fluxo

1. Extrair o índice completo do PDF (passo 3)
2. **Classificar o nível do livro:**
   - **Básico:** cobre só fundamentos (variáveis, condicionais, loops, vetores, funções) — público iniciante
   - **Intermediário:** avança pra mais conceitos mas sem se aprofundar (ponteiros, arquivos, structs simples)
   - **Avançado:** estruturas de dados, recursão, complexidade, ordenação, busca, tópicos densos
3. **Consultar itens já publicados na mesma categoria:**

```sql
SELECT qi.id, qi.position, qi.title, qi.planned_author,
       qi.planned_category_id, qi.metadata_json->>'cover_palette' as palette
FROM importer.queue_items qi
WHERE qi.source_url LIKE '%<DOMINIO DA FONTE>%'
  AND qi.status IN ('done', 'waiting_process')
  AND qi.id != <ITEM_ATUAL>;
```

4. **Comparar nível + categoria:**

| Livro atual | Já publicado | Decisão |
|---|---|---|
| Básico | Básico na mesma categoria | ⛔ **DUPLICATA** — mesmo assunto, mesmo nível |
| Básico | Avançado na mesma categoria | ✅ OK — complementares (um ensina, outro aprofunda) |
| Avançado | Básico na mesma categoria | ✅ OK — complementares |
| Intermediário | Básico na mesma categoria | ✅ OK — escada de aprendizado |
| Intermediário | Avançado na mesma categoria | ✅ OK — escada de aprendizado |
| Básico/Inter./Avanç. | Categoria diferente | ✅ OK — assuntos distintos |

**A única situação que gera duplicata é: mesmo nível + mesma categoria.** Fora isso, convivem.

#### Registrar decisão

```sql
UPDATE importer.queue_items SET
  status = 'duplicate',
  metadata_json = metadata_json || '{"duplicate_reason": "same_subject", "duplicate_of": <ID_DO_MELHOR_ITEM>, "current_level": "basico|intermediario|avancado"}'::jsonb,
  updated_at = NOW()
WHERE id = <ITEM_ATUAL>;
```

#### Critério de desempate (qual fica quando há duplicata)

1. **Maior profundidade** — nível mais avançado sempre fica sobre o mais básico (mas isso já é coberto pela regra acima: só há duplicata se mesmo nível)
2. **Autoridade da fonte** — universidade > instituição técnica > autor independente
3. **Primeiro a chegar** — quem já está publicado permanece em caso de empate

### 3. Extrair índice do PDF

```bash
pdftotext -f 1 -l 10 /data/workspace/sharebook-ebook-importer/triage-downloads/<ARQUIVO.pdf> - | head -150
```

Extrair páginas do sumário (normalmente nas primeiras páginas). Aplicar a **checklist "antes de escrever"** antes de seguir.

### 4. Escrever sinopse (3 parágrafos)

Sem Wikipedia, sem datas, sem "parece atual".

- **Parágrafo 1:** Gancho com a dor do leitor + algo específico do índice que prova que você leu o material
- **Parágrafo 2:** Conteúdo real extraído do índice (tópicos principais, descobertas inesperadas)
- **Parágrafo 3:** Valor do material, diferencial, o que o leitor leva

**Proibido:**
- Subtítulos nos parágrafos ("Parágrafo 1 —")
- Datas, séculos, épocas
- "Neste livro", "Nesta obra"
- Sinopse genérica que poderia servir pra qualquer livro
- Escrever antes de ler o índice completo

**Dica de ouro — sinopse sexy:**
A sinopse não é descrição de conteúdo. É uma **conversa com o leitor**.

1. **Identificar a dor do leitor** — qual ansiedade, confusão ou medo o público-alvo sente?
2. **Responder "por que eu deveria me importar?"** — o que muda na vida do leitor depois de ler
3. **Público-alvo explícito** — profissional de TI perdido? Estudante? Gestor?
4. **Tom de autoridade pessoal** — simular a voz de quem já passou pelo problema
5. **Fechar com entrega concreta** — o que o leitor leva?

**Formato:** 3 parágrafos, linguagem direta, tom de quem entende e fala de igual pra igual com o leitor.

### 5. Gerar capa — processo de 2 estágios com análise visual

#### Estágio 1 — Gerar 6 variações

Gere 6 capas com paletas sorteadas (use `-p` vazio para sorteio automático):

```bash
for i in 1 2 3 4 5 6; do
  python3 skills/sharebook-ebook-foundation-preparer/scripts/cover_generate.py \
    "<TITULO>" \
    "<AUTOR>" \
    -o sharebook-ebook-importer/triage-downloads/<slug>-var-$i.jpg
done
```

Cada execução sorteia independentemente: paleta, fonte, layout, elemento decorativo, gradiente e efeito de texto. As 6 são diferentes entre si.

**Importante:** salve os metadados de cada iteração (paleta, fonte, layout, efeito) para referência.

#### Estágio 2 — Analisar visualmente e escolher a melhor

Use `image` tool para analisar cada uma das 6 imagens geradas. Critérios de avaliação:

1. **Legibilidade** — o título e autor são claramente legíveis? Contraste suficiente?
2. **Harmonia de paleta** — bg, fg e accent conversam bem entre si?
3. **Adequação temática** — a capa parece de um livro técnico? (evitar paletas muito artísticas ou infantis)
4. **Layout** — equilíbrio entre texto e elemento decorativo
5. **Efeito de texto** — o efeito escolhido valoriza ou prejudica a leitura?

Após analisar todas, defina um ranking e copie a melhor como capa definitiva:

```bash
cp sharebook-ebook-importer/triage-downloads/<slug>-var-<N>.jpg \
   sharebook-ebook-importer/triage-downloads/<slug>-cover.jpg
```

> **Nota:** este fluxo de gerar 6 variações, analisar visualmente e escolher a melhor é o comportamento padrão. O agente executante (seja subagente de curadoria ou cron do OpenClaw) usa o mesmo modelo e tem capacidade de `image` para análise visual — não são necessárias heurísticas de aproximação.

### 5.5. Verificar e otimizar tamanho do PDF

**⚠️ PDFs acima de 5MB brutos podem travar o worker.** O servidor do ShareBook fecha conexões SSL em POSTs com payload > ~10MB (base64 do PDF). O worker não tem compressão automática — é responsabilidade do curador garantir que o PDF cabe.

```bash
# Verificar tamanho do PDF bruto
ls -lh sharebook-ebook-importer/triage-downloads/position_XXX-*.pdf
```

**Regras:**

| Tamanho do PDF bruto | Ação |
|---|---|
| < 5MB | ✅ Segue direto, sem compressão |
| 5MB — 15MB | ⚠️ Comprimir com Ghostscript `/prepress` (preserva 300 DPI, qualidade de imagem): `gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/prepress -dNOPAUSE -dQUIET -dBATCH -sOutputFile=/tmp/compressed.pdf <input.pdf>` |
| > 15MB | ⚠️ O PDF muito grande pode ter imagens pesadas (prints de emulador, scans). Comprimir com `/prepress`. Se ainda > 15MB após compressão, **avaliar se o conteúdo realmente precisa de todas as imagens**. Nunca usar `/ebook` (destrói legibilidade de prints técnicos). |

**Após comprimir, substituir o PDF original pelo comprimido antes de registrar no banco:**

```bash
cp /tmp/compressed.pdf sharebook-ebook-importer/triage-downloads/position_XXX-*.pdf
```

**Nunca usar `--delete-existing` no script de publicação.** O correto é usar `update` — substitui o PDF sem perder o histórico.

---

### 6. Escolher categoria — regras rigorosas

**⚠️ Erro comum: o curador frequentemente escolhe categorias genéricas como "Conhecimento & Carreira" para livros de tecnologia. Isso precisa ser evitado.**

O ShareBook tem uma árvore de categorias. Livros técnicos da ebook_foundation DEVEM ficar em **Tecnologia** e suas subcategorias.

#### Árvore completa de Tecnologia:

```
Tecnologia
  ├── DevOps       — Linux, shell, redes, infraestrutura, automação, Docker, Git, CI/CD
  ├── IA           — inteligência artificial, machine learning, NLP
  ├── Frontend     — HTML, CSS, JavaScript, UI/UX
  ├── Backend      — lógica de programação, algoritmos (básico), Java, C#, Python, PHP, Ruby
  ├── Dados        — algoritmos avançados, estrutura de dados, banco de dados, SQL, BI
  └── Cloud        — computação em nuvem, AWS, Azure, GCP, SaaS
```

#### Mapeamento de assunto → subcategoria:

| Assunto duvidoso, não encaixa nas específicas | **Geral** (guarda-chuva) | `019dcbfc-0a09-702e-a0ab-090acb5597b6` |

#### Regra de ouro:

**NUNCA** escolha "Conhecimento & Carreira" (`019d7e18-3fd3-7434-8033-28750c0881b5`) para livros de tecnologia. Na dúvida entre duas subcategorias específicas, escolha **Geral**.

---

| Assunto do livro | Subcategoria correta | ID |
|---|---|---|
| Linux, shell script, sistemas operacionais, redes | **DevOps** | `019d636c-640a-7e2f-babd-c22d3b37c226` |
| Git, Docker, CI/CD, infraestrutura | **DevOps** | `019d636c-640a-7e2f-babd-c22d3b37c226` |
| Inteligência Artificial, Machine Learning, NLP | **IA** | `019d636c-6365-74c5-9323-14be85d8b0a3` |
| HTML, CSS, JavaScript | **Frontend** | `019d636c-616a-7dcb-af70-77619c9dbaf5` |
| Lógica de programação, algoritmos (iniciante), Java, C#, Python, PHP | **Backend** | `019d636c-5fdd-7505-9c76-e02944d9b618` |
| Estruturas de dados, algoritmos avançados, banco de dados, SQL | **Dados** | `019d636c-62c1-71e9-9a51-099d3304753e` |
| Computação em nuvem, AWS, Azure, GCP | **Cloud** | `019d636c-6206-7f05-ade0-14ed095dd21c` |
| Arduino, hardware, IoT | **DevOps** | `019d636c-640a-7e2f-babd-c22d3b37c226` |
| Go, Rust, Julia, Pascal, Fortran, LISP | **Backend** | `019d636c-5fdd-7505-9c76-e02944d9b618` |
| LaTeX | **Backend** | `019d636c-5fdd-7505-9c76-e02944d9b618` |
| Python para matemáticos | **Backend** | `019d636c-5fdd-7505-9c76-e02944d9b618` |
| Git, shell scripting | **DevOps** | `019d636c-640a-7e2f-babd-c22d3b37c226` |
| R, análise de dados | **Dados** | `019d636c-62c1-71e9-9a51-099d3304753e` |

#### Regra de ouro:

**NUNCA** escolha "Conhecimento & Carreira" (`019d7e18-3fd3-7434-8033-28750c0881b5`) para livros de tecnologia. Se não encaixar em nenhuma subcategoria de Tecnologia, prefira a categoria raiz **Tecnologia** (`1dc0f9e3-70d9-4bc8-a76c-90d7144e318c`) a qualquer outra categoria genérica.

Categoria folha é obrigatória, mas se houver dúvida genuína entre duas, use a tabela acima como referência.

#### Para verificar se a categoria existe:

```bash
TOKEN_V2=$(grep SHAREBOOK_PROD_ACCESS_TOKEN /data/workspace/sharebook-agent/.env | cut -d= -f2)
curl -s -H "Authorization: Bearer $TOKEN_V2" -H "x-requested-with: web" \
  "https://www.sharebook.com.br/api/category" | python3 -c "
import json, sys
data = json.load(sys.stdin)
# Mostrar apenas árvore de tecnologia
for cat in data['items']:
    if cat['name'] == 'Tecnologia':
        print('Tecnologia:', cat['id'])
        for child in cat['children']:
            print(f'  └ {child[\"name\"]:25s} {child[\"id\"]}')
"
```

Categoria folha obrigatória.

### 7. Registrar no PostgreSQL

Usar Python com psycopg2 (não SQL direto) para evitar escaping e encoding:

```python
import os, urllib.parse, psycopg2, json

dsn = os.environ["IMPORTER_DB_DSN"]
parsed = urllib.parse.urlparse(dsn)
password = urllib.parse.unquote(parsed.password)
conn = psycopg2.connect(host=parsed.hostname, port=parsed.port or 5432,
                        dbname=parsed.path.lstrip("/"), user=parsed.username, password=password)
cur = conn.cursor()
cur.execute("""
    UPDATE importer.queue_items SET
      planned_author = %s,
      planned_category_id = %s,
      planned_synopsis = %s,
      planned_cover_mode = 'source',
      planned_cover_url = %s,
      metadata_json = metadata_json || %s::jsonb,
      status = 'waiting_process',
      updated_at = NOW()
    WHERE id = %s
""", (author, category_id, synopsis, cover_url_rel,
      json.dumps({"cover_palette": palette, "cover_style": "pillow", "synopsis_source": "pdf_toc", "cover_path": cover_path_abs}),
      item_id))
conn.commit()
cur.close()
conn.close()
```

**Nota:** `planned_cover_mode` só aceita `'source'` (check constraint). Detalhes da capa (caminho absoluto, paleta, fonte, etc.) vão no `metadata_json`.

### 8. Publicar via worker

```bash
cd /data/workspace/sharebook-ebook-importer/src
env \
  IMPORTER_DB_DSN="postgresql://..." \
  TOKEN_V2="..." \
  python3 -m sharebook_ebook_importer.cli run-once --source ebook_foundation
```

O worker:
- Pega o próximo item `waiting_process` da source `ebook_foundation`
- Reusa PDF de `triage-downloads/` se `metadata_json->>'local_pdf'` existir
- Usa capa de `metadata_json->>'cover_path'` (caminho absoluto)
- Publica e aprova automaticamente

**Se o worker falhar com 401 (token expirado):**
1. Pegar token novo de `sharebook-agent/.env`
2. Resetar status: `UPDATE importer.queue_items SET status = 'waiting_process', last_error = NULL, updated_at = NOW() WHERE id = <ID>;`
3. Rodar worker de novo

## Scripts

- `scripts/cover_roulette.py` — sorteia paleta apenas (wrapper legado)
- `scripts/cover_generate.py` — gera capa 600x900 com sorteio completo (fonte, layout, gradiente, efeito, elemento decorativo)
  - Aceita `--efeito` (glow|outline|shadow|glow+outline) para debug
  - Aceita `-p` (paleta) para forçar paleta específica
  - Aceita `--json` para saída JSON consumível

## Efeitos de texto disponíveis

| Efeito | Descrição |
|---|---|
| `shadow` | Sombra padrão no canto inferior direito |
| `glow` | Brilho branco suave ao redor das letras |
| `outline` | Contorno preto nas bordas |
| `glow+outline` | Outline preto + glow branco combinados |

## Fontes disponíveis (10)

Cantarell, Dosis, Cabin, EB Garamond, Roboto, DejaVu Serif, Liberation Sans, KaushanScript, CabinSketch, Humor Sans

## Paletas (10)

tron, deep-ocean, lava, frost, matrix, sunset, graphite, cyber, forest, platinum

## Armadilhas conhecidas (aprendidas em produção)

### `planned_cover_url` é relativo ao project_root, não ao triage-downloads

O worker resolve `planned_cover_url` como `project_root / planned_cover_url`.

- ✅ Correto: `triage-downloads/position_XX-nome-do-livro-cover.jpg`
- ❌ Errado: `position_XX-nome-do-livro-cover.jpg` (só o nome, sem pasta)

### Worker roda no container OpenClaw, não no host SSH

PDF e capa precisam estar no **workspace local** (`/data/workspace/sharebook-ebook-importer/triage-downloads/`), não no servidor remoto. Fazer scp pro host não adianta — o worker não enxerga arquivos que estão fora do volume do container.

### Fonte original pode estar fora do ar

Várias fontes antigas do IME-USP, UFPB e similares têm links mortos. A triagem (beat) pode registrar `local_pdf` sem o arquivo existir de verdade. Verificar:

```bash
ls -lh /data/workspace/sharebook-ebook-importer/triage-downloads/position_XX-*.pdf
```

Se não existir, buscar no Wayback Machine ou mirror alternativo.

### Registre todos os campos obrigatórios de uma vez
O worker valida:
- `planned_title`
- `planned_author`
- `planned_category_id`
- `planned_synopsis`
- `planned_cover_mode` (deve ser `'source'`)
- `planned_cover_url`

Qualquer campo faltando → worker joga de volta pra `waiting_editor`. Registrar tudo no mesmo UPDATE.

### Referência por position, não por id

O operador humano sempre se refere ao número da **position** (ex.: #115), que pode ser diferente do `id` no banco. Ao buscar, filtrar por `position`, não por `id`.

## Regras de ouro

- **Índice do PDF é a fonte primária da sinopse** — não inventar
- **Sem Wikipedia** — material técnico não tem cobertura
- **Sinopse específica** — baseada nos tópicos reais, tom envolvente
- **Capa sempre aleatória** — nunca fixar paleta/fonte/layout em produção
- **Categoria folha** — verificar que não tem children
- **Worker com `--source ebook_foundation`** — o default é `baixelivros`
- **Erro de fonte = quebra proposital** — se path de fonte sumir, o script falha com `FileNotFoundError`
