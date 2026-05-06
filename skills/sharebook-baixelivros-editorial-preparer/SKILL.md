# Skill: ShareBook BaixeLivros Editorial Preparer

**Descrição:** Preparador editorial da missão principal BaixeLivros, com foco em `baixelivros_infantil`, no pipeline de importação do ShareBook. Lê fontes com atenção, valida metadados, escolhe categorias apropriadas e escreve sinopses premium (3 parágrafos) combinando informação factual com contexto histórico/literário.

**Quando usar:** Sempre que um item da missão BaixeLivros, especialmente `baixelivros_infantil`, precisa ser preparado editorialmente para importação no ShareBook, sobretudo em `waiting_editor` ou `editing`.

## Sinergia com outra skill

- Esta skill prepara o terreno para `sharebook-public-ebook-importer`.
- Regra prática: `waiting_editor` e `editing` pertencem a esta skill.
- Quando autor, categoria, sinopse e demais decisões editoriais estiverem sólidos, o item deve sair daqui em `waiting_process` para a skill `sharebook-public-ebook-importer` publicar.
- Se durante a preparação surgir suspeita de duplicata, bloqueio de fonte ou problema técnico de importação, consultar a skill `sharebook-public-ebook-importer` para o lado operacional.

---

## Fluxo Definitivo (Curadoria Manual)

```
1. BaixeLivros → Âncora factual básica (sempre)
2. Wikipedia → Contexto rico (se existir, senão pular)
3. Nosso conhecimento → Análise literária, estilo
4. Sinopse premium → Combinação de tudo
```

**Regras de ouro:**
- **Não inventar:** Se informação não existe na fonte, não criar
- **Wikipedia opcional:** Se não tem página, usar apenas BaixeLivros
- **Registrar no PostgreSQL:** Anotar se usou Wikipedia ou não
- **Curadoria manual:** Sem automação - atenção aos detalhes

---

## Fluxo Operacional (Obrigatório)

### 1. Conhecer as categorias do ShareBook
```bash
# Obter árvore completa de categorias
curl -s -H "Authorization: Bearer $TOKEN" -H "x-requested-with: web" \
  "https://www.sharebook.com.br/api/category" | jq .
```

**Regra:** Sempre usar **categoria folha** (sem children), nunca categoria pai.

### 2. Buscar registros no PostgreSQL
```bash
# Buscar itens em waiting_editor/editing ou com lacuna editorial
python3 -c "
import psycopg2
import os

dsn = os.getenv('IMPORTER_DB_DSN', 'postgresql://sharebook_ai_rw:F%25Ljy9oxTA3iR%23npW%254W9iaSaJKU@fgsgwsckccgk8sccc4gg0gg0:5432/sharebook_importer')
conn = psycopg2.connect(dsn)
cur = conn.cursor()

cur.execute("""
  SELECT 
    id,
    title,
    author,
    planned_title,
    planned_author,
    planned_category_id,
    planned_synopsis,
    source_url,
    status
  FROM importer.queue_items 
  WHERE status IN ('waiting_editor', 'editing', 'error')
     OR (status = 'waiting_process' AND (planned_author IS NULL OR planned_synopsis IS NULL OR planned_synopsis = ''))
  ORDER BY position
  LIMIT 5
""")

for row in cur.fetchall():
    print(f'ID: {row[0]}')
    print(f'  Título: {row[1]}')
    print(f'  Autor: {row[2]}')
    print(f'  URL: {row[7]}')
    print(f'  Status: {row[8]}')
    print()

conn.close()
"
```

### 3. Ler as fontes com ATENÇÃO (Dupla verificação)
**Não pule esta etapa!** Acesse AMBAS as fontes:

**A) Fonte BaixeLivros (URL `source_url`):**
- **Título exato**
- **Autor exato** 
- **Descrição/Resumo original** (âncora factual)

**B) Wikipedia (se existir):**
- Acessar `https://pt.wikipedia.org/wiki/TITULO_DO_LIVRO`
- Extrair: contexto histórico, temas principais, análise literária
- **Regra de ouro:** Se não existir na Wikipedia, NÃO INVENTAR
- **Registrar no PostgreSQL:** `metadata_json = '{"wikipedia": false}'`

**Comandos:**
```bash
# 1. Ler fonte BaixeLivros
web_fetch(url="$SOURCE_URL")

# 2. Tentar Wikipedia (formatar título para URL)
TITULO_URL=$(echo "$TITULO" | sed 's/ /_/g' | tr '[:upper:]' '[:lower:]')
web_fetch(url="https://pt.wikipedia.org/wiki/$TITULO_URL")
```

**Validação cruzada OBRIGATÓRIA:**
- O título da fonte bate com `title`/`planned_title`?
- O autor da fonte bate com `author`/`planned_author`?
- Se houver divergência, **a fonte BaixeLivros prevalece**.
- Wikipedia é para **contexto/enriquecimento**, não para correção de fatos básicos.

### 4. Escolher categoria apropriada
Baseado no conteúdo real da obra (não em suposições):
- Romance → Drama ou subcategorias
- Poesia → Poesia & Artes > subcategoria
- Ficção → Ficção > subcategoria  
- Técnico → Tecnologia > subcategoria
- etc.

**Dica:** Use a descrição da fonte para identificar gênero/tema.

### 5. Escrever sinopse premium (3 parágrafos)
**Fontes de informação (em ordem de prioridade):**
1. **BaixeLivros:** Âncora factual básica (enredo principal)
2. **Wikipedia:** Contexto histórico, temas, análise literária (se disponível)
3. **Nosso conhecimento:** Análise crítica, estilo envolvente

**Estrutura (com Wikipedia integrada):**
1. **Parágrafo 1 (Hook + Contexto):** 
   - Gancho envolvente
   - Contexto histórico da Wikipedia (se houver)
   - Ex: "INSPIRADO EM UM CRIME REAL QUE ABALOU O RIO..."

2. **Parágrafo 2 (Profundidade + Temas):**
   - Enredo principal (BaixeLivros)
   - Temas da Wikipedia (degeneração moral, crítica social, etc.)
   - Personagens e conflitos

3. **Parágrafo 3 (Convite + Legado):**
   - Por que ler esta obra hoje
   - Impacto literário (da Wikipedia ou nosso conhecimento)
   - Convite final envolvente

**Regras:**
- **Fiel** ao conteúdo real (não inventar)
- **Sexy** no tom, linguagem envolvente
- **3 parágrafos** obrigatório
- **Integrar Wikipedia** quando disponível (valor agregado)
- **Não inventar** se Wikipedia não tiver informação
- **Registrar** no SQLite se usou Wikipedia ou não

### 6. Gerar capa (se necessário)

O worker **não publica sem capa**. Antes de marcar como `waiting_process`, o item precisa de uma imagem de capa.

**Fluxo de capa:**

1. **Verificar se o item já tem capa** (`planned_cover_url` preenchido e arquivo existente)
2. Se não tiver, **gerar via OpenAI Images API** com o script `sharebook_openai_cover.py`:
   ```bash
   python3 /data/workspace/sharebook-agent/scripts/covers/sharebook_openai_cover.py \
     --prompt "Capa de livro infantil, ... (descrever cena/estilo). Título: TITULO. Autor: AUTOR." \
     --output /tmp/cover_<ID>.png \
     --size 1024x1536 \
     --quality high
   ```
3. **Copiar a capa** para `triage-downloads/covers/` com nome padronizado:
   ```bash
   cp /tmp/cover_<ID>.png /data/workspace/sharebook-ebook-importer/triage-downloads/covers/position_<PPP>-<slug>.png
   ```
4. **Registrar** no PostgreSQL: `planned_cover_mode = 'source'` e `planned_cover_url = 'triage-downloads/covers/position_<PPP>-<slug>.png'`

**Regras:**
- Tamanho: 1024x1536 (proporção 2:3 vertical)
- Qualidade: high
- Prompt deve descrever: personagens da história, cenário relevante, estilo visual (aquarela, traço infantil, etc.)
- **Para capas de alta qualidade, priorizar fluxo ChatGPT web** (qualidade superior). Nesse caso, definir `planned_cover_mode = 'source'` com o caminho relativo do arquivo baixado.

### 7. Atualizar PostgreSQL
```bash
python3 -c "
import psycopg2
import os
import json

dsn = os.getenv('IMPORTER_DB_DSN', 'postgresql://sharebook_ai_rw:F%25Ljy9oxTA3iR%23npW%254W9iaSaJKU@fgsgwsckccgk8sccc4gg0gg0:5432/sharebook_importer')
conn = psycopg2.connect(dsn)
cur = conn.cursor()

item_id = ID_DO_ITEM  # Substituir pelo ID real
autor = 'AUTOR_CORRETO'
categoria = 'ID_CATEGORIA_FOLHA'
sinopse = 'SINOPSE_SEXY_3_PARAGRAFOS'
cover_url = 'triage-downloads/covers/position_<PPP>-<slug>.png'

# Atualizar
cur.execute("""
  UPDATE importer.queue_items SET
    planned_author = %s,
    planned_category_id = %s,
    planned_synopsis = %s,
    planned_cover_url = %s,
    planned_cover_mode = 'source',
    status = 'waiting_process',
    updated_at = NOW()
  WHERE id = %s
""", (autor, categoria, sinopse, cover_url, item_id))

conn.commit()
print(f'✅ Item {item_id} atualizado no PostgreSQL')
conn.close()
"
```

**Campos a atualizar no PostgreSQL:**
- `planned_author`: Autor correto (da fonte)
- `planned_category_id`: ID da categoria folha escolhida
- `planned_synopsis`: Sinopse sexy de 3 parágrafos
- `planned_cover_url`: Caminho relativo ao project_root da capa (ex: `triage-downloads/covers/position_011-um-dia-so-para-nos.png`)
- `planned_cover_mode`: `'source'` (capa gerada externamente)
- `status`: usar `editing` enquanto estiver trabalhando e fechar em `waiting_process` quando completar
- `updated_at`: Atualizar timestamp automaticamente

### 8. Registrar decisões (Opcional mas recomendado)
Manter breve registro no `metadata_json` ou em log:
- Por que escolheu esta categoria
- Principais elementos da sinopse
- Validações feitas

---

## Exemplo Real (Casa de Pensão - Fluxo com Wikipedia)

### Situação inicial (PostgreSQL):
- `title`: "Casa De Pensao"
- `author`: "Aluísio Azevedo"
- `source_url`: "https://www.baixelivros.com.br/literatura-brasileira/casa-de-pensao"
- `planned_synopsis`: NULL

### Fontes consultadas:

**A) BaixeLivros (source_url):**
- Descrição: "Este livro conta a história de Amâncio, que... vai para o Rio de Janeiro onde acaba numa casa de pensão..."
- **Valor:** Âncora factual básica

**B) Wikipedia (https://pt.wikipedia.org/wiki/Casa_de_Pensão):**
- Contexto: "Inspirado em um crime real ocorrido no Rio de Janeiro em 1876, conhecido como Questão Capistrano"
- Temas: "degeneração moral, interesse econômico, violência e hipocrisia social"
- Movimento: "Naturalismo no Brasil, influência de Émile Zola"
- **Valor:** Contexto histórico rico, análise literária

### Ação correta (fluxo novo):
1. **Ler ambas fontes:** BaixeLivros (fatos) + Wikipedia (contexto)
2. **Validar:** Autor/título consistentes entre fontes
3. **Categoria:** "Drama de Crítica Social" (adequado aos temas da Wikipedia)
4. **Sinopse premium (3 parágrafos):**
   - Parágrafo 1: Hook com contexto histórico da Wikipedia
   - Parágrafo 2: Enredo (BaixeLivros) + temas (Wikipedia)
   - Parágrafo 3: Impacto literário + convite
5. **Atualizar PostgreSQL:**
   ```sql
   UPDATE importer.queue_items SET
     planned_synopsis = 'SINOPSE_PREMIUM...',
     metadata_json = '{"wikipedia": true, "crime_real": "Questão Capistrano 1876"}',
     status = 'waiting_process',
     updated_at = NOW()
   WHERE id = ID_DO_ITEM
   ```

### Exemplo sem Wikipedia:
Se livro não tiver página na Wikipedia:
```sql
UPDATE importer.queue_items SET
  metadata_json = '{"wikipedia": false}',
  planned_synopsis = 'SINOPSE_BASEADA_SOMENTE_EM_BAIXELIVROS...',
  updated_at = NOW()
WHERE id = ID_DO_ITEM
```
**Regra:** Não inventar informações faltantes.

---

## Checklist de Qualidade

Antes de marcar como `waiting_process`:
- [ ] Fonte lida e validada
- [ ] Título/autor conferidos com fonte
- [ ] Categoria é folha (não tem children)
- [ ] Sinopse tem 3 parágrafos
- [ ] Sinopse é fiel à obra
- [ ] Sinopse tem tom envolvente/sex
- [ ] Capa gerada (arquivo PNG 1024x1536 em `triage-downloads/covers/`)
- [ ] `planned_cover_url` preenchido com caminho relativo
- [ ] `planned_cover_mode = 'source'`
- [ ] PostgreSQL atualizado com todos os campos

---

## Erros Comuns a Evitar

1. **Associação automática:** "Carolina" ≠ automaticamente "Carolina Maria de Jesus"
2. **Suposição de gênero:** Casimiro de Abreu (poeta) também escreveu prosa
3. **Sinopse genérica:** Evitar "obra importante", "leitura obrigatória" sem contexto
4. **Categoria pai:** Sempre verificar se categoria tem `children: []`
5. **Ignorar fonte:** Nunca pular a leitura da descrição original

---

## Ferramentas Úteis

```bash
# Verificar se categoria é folha
TOKEN=$(grep SHAREBOOK_PROD_ACCESS_TOKEN /data/workspace/sharebook-agent/.env | cut -d= -f2)
curl -s -H "Authorization: Bearer $TOKEN" -H "x-requested-with: web" \
  "https://www.sharebook.com.br/api/category" | \
  jq -r '.items[] | select(.id == "ID_CATEGORIA") | .children | length'

# Buscar livro no ShareBook (verificar duplicata)
curl -s -H "Authorization: Bearer $TOKEN" -H "x-requested-with: web" \
  "https://www.sharebook.com.br/api/book?title=TITULO&author=AUTOR"

# Testar sinopse (contar parágrafos)
echo "$SINOPSE" | grep -c '^[[:space:]]*$'  # Linhas em branco entre parágrafos

# Formatar título para URL da Wikipedia
TITULO="Casa de Pensão"
TITULO_URL=$(echo "$TITULO" | sed 's/ /_/g' | tr '[:upper:]' '[:lower:]' | sed "s/[áàãâä]/a/g; s/[éèêë]/e/g; s/[íìîï]/i/g; s/[óòõôö]/o/g; s/[úùûü]/u/g; s/ç/c/g")
echo "https://pt.wikipedia.org/wiki/$TITULO_URL"
# Resultado: https://pt.wikipedia.org/wiki/casa_de_pensao

# Verificar se Wikipedia tem página
curl -s -I "https://pt.wikipedia.org/wiki/$TITULO_URL" | grep -i "^HTTP"
# HTTP/1.1 200 OK → Página existe
# HTTP/1.1 404 Not Found → Não existe
```

## Formatação de Títulos para Wikipedia

**Regras para converter título → URL:**
1. Substituir espaços por underscores (`_`)
2. Converter para minúsculas
3. Remover acentos (opcional - Wikipedia geralmente aceita com acentos)
4. Manter outros caracteres especiais?

**Exemplos:**
- "Casa de Pensão" → `casa_de_pensão` ou `casa_de_pensao`
- "Memórias Póstumas de Brás Cubas" → `memórias_póstumas_de_brás_cubas`
- "O Cortiço" → `o_cortiço`

**Dica:** Testar ambas versões (com e sem acentos) se uma falhar.

---

**Nota:** Esta skill define seu papel operacional como curador. O worker apenas executa cadastro técnico com os dados que você preparar. Qualidade do acervo depende da sua atenção aos detalhes.