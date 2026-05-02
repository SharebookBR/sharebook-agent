---
name: sharebook-triage-baixelivros
description: "Triagem inicial de itens do BaixeLivros no pipeline de importação do ShareBook. Use quando items de sources BaixeLivros estão em `waiting_triage`, especialmente `baixelivros_infantil`, `baixelivros`, literatura brasileira e estrangeira. Avalia se o material é livro aproveitável, detecta links quebrados, conteúdo não-livro, pirataria, duplicatas, didático fora de escopo e risco jurídico de obras contemporâneas. O output é um item em `waiting_editor`, `duplicate`, `triage_rejected` ou `source_blocked`."
---

# ShareBook Triage, BaixeLivros

## Quando usar

Items recém-chegados de sources do **BaixeLivros** com status `waiting_triage`.  
Este é o **primeiro filtro humano** do pipeline, antes da curadoria editorial.

Sources-alvo mais importantes:
- `baixelivros`
- `baixelivros_infantil`
- recortes de literatura brasileira
- recortes de literatura estrangeira

Se a origem não for BaixeLivros e a lógica principal depender de outra fonte, esta skill pode não ser a mais adequada.

---

## Critérios de decisão

### 🔴 Bloqueantes

1. **Link morto / acesso negado / anti-download**
   - página não responde
   - download volta HTML disfarçado
   - proteção do site impede obter PDF real
2. **Pirataria / risco jurídico alto**
   - scan de livro comercial ainda vendido
   - obra contemporânea sem licença clara
   - edição ilustrada recente de texto clássico sem base de autorização clara
   - tradução/adaptação moderna sem segurança jurídica mínima
3. **Não é livro**
   - videoaula, podcast, software, palestra, curso, atividade solta, cartilha avulsa, folheto, slide deck
4. **Material didático / pedagógico fora do alvo editorial**
   - alfabetização, caderno de atividades, exercícios, apoio escolar, material de professor, conteúdo para colorir
5. **PDF inconsistente**
   - HTML fingindo ser PDF
   - arquivo muito curto / quebrado / ilegível

Regra prática para BaixeLivros:
- problema estrutural recorrente da source → `source_blocked`
- problema isolado do item → `triage_rejected`

Para BaixeLivros, evitar usar `error` como lixeira semântica. Se a triagem humana decidiu rejeitar, o status normal é `triage_rejected`.

### 🟡 Duplicata → `duplicate`

4. **Mesma obra já publicada no Sharebook**.  
   ⚠️ **Só conta como duplicata se o livro já existe no produto** (tabela `"Books"` do banco `sharebook`).  
   ⚠️ **Item rejeitado ou em fila não é base para duplicata**: outros itens em `triage_rejected` ou `waiting_editor` não tornam o atual duplicata. Só o banco do produto é fonte da verdade.
   ⚠️ **Não confundir com obras complementares**: "PHP para Iniciantes" e "PHP Avançado" são livros diferentes, ambos bem-vindos.  
   ⚠️ **Variações de título do mesmo conteúdo** contam como duplicata.

   **Como verificar**: consultar o banco do produto (`sharebook-backend`) no schema `public`, tabela `"Books"`. O mesmo host PostgreSQL, database `sharebook`:
   ```sql
   -- DSN base: mesmo host/user do IMPORTER_DB_DSN, database = sharebook
   SELECT "Id", "Title", "Author", "Status", "Slug"
   FROM public."Books"
   WHERE LOWER("Title") LIKE '%<palavra-chave-1>%'
      OR LOWER("Title") LIKE '%<palavra-chave-2>%';
   ```
   Extrair 2-3 palavras-chave do título do item e buscar no banco. Se encontrar match próximo → `duplicate`. Se não encontrar → segue limpo.
   
   **Nota**: colunas com maiúsculas exigem aspas duplas no PostgreSQL (`"Title"`, `"Author"`, etc.).

### 🟢 Segue limpo → `waiting_editor`

- domínio público claro
- licença explícita clara
- literatura consolidada com risco jurídico baixo
- conto, fábula, folclore ou clássico com base razoável
- PDF real, íntegro e minimamente legível
- **Idioma**: português

Para BaixeLivros infantil, o default saudável é conservador.
Se houver dúvida jurídica séria, rejeitar cedo em vez de empurrar problema para frente.

---

## Regras específicas para `baixelivros_infantil`

A source `baixelivros_infantil` é valiosa, mas misturada e juridicamente heterogênea.

### O que tende a ser candidato forte
- Andersen
- Esopo
- Monteiro Lobato em obras clássicas já consolidadas
- fábulas
- contos tradicionais
- lendas e folclore
- obras com licença explícita

### O que tende a ser suspeito
- autores contemporâneos pouco conhecidos com PDF completo
- livros infantis recentes com ilustração/editorial moderna
- adaptações modernas de clássicos sem licença clara
- compilações genéricas tipo `100 histórias` sem origem jurídica clara
- material escolar ou paradidático disfarçado de infantil

### Regra de escopo
- URL em `/infantil/` não basta para aprovar
- URL em `/didatico/` deve ser rejeitada por escopo
- item com cara de atividade escolar, caderno, apoio pedagógico ou alfabetização deve virar `triage_rejected`

### Regra jurídica dura
Se o item parecer contemporâneo e não houver licença explícita ou base forte de legitimidade, rejeitar.
Não tentar ser advogado heroico no meio da fila.

## Informações sobre as fontes

Consulte `references/sources.md` para detalhes das fontes e padrões de URL.

---

## Referência de identificação

Cada item tem dois números:
- **`id`**: chave primária global da tabela (usado nos comandos SQL)
- **`position`**: número sequencial por source (o que o dashboard mostra)

**Sempre use `position` quando se referir ao número do item com o Raffa.**

---

## Fluxo operacional

## Fonte de verdade operacional

Antes de qualquer triagem, validar a fonte atual nesta ordem:

1. `sharebook-ebook-importer/src/sharebook_ebook_importer/pg_db.py`
2. `sharebook-ebook-importer/README.md`
3. `sharebook-ebook-importer/docs/PLAYBOOK.md`

Se a documentação desta skill divergir do código do importer, corrigir a skill.

**Importante**: a fila real fica em **Postgres, schema `importer`**, nas tabelas `importer.queue_items`, `importer.sources` e `importer.runs`.
Se sua conexão SQL não enxergar esse schema, você está no banco errado. Não improvise triagem em outra base.

### 1. Buscar próximo item e marcar como `triaging`

```sql
-- Buscar item (sempre incluir id e position)
SELECT qi.id,
       qi.position,
       qi.title,
       qi.author,
       qi.source_url,
       s.name as source_name
FROM importer.queue_items qi
JOIN importer.sources s ON s.id = qi.source_id
WHERE qi.status = 'waiting_triage'
ORDER BY qi.position
LIMIT 1;
```

**Antes de começar a análise**, atualizar o status para `triaging` para evitar corrida com outro operador/processo:

```sql
UPDATE importer.queue_items
SET status = 'triaging', updated_at = NOW()
WHERE id = <ID_DO_ITEM>
  AND status = 'waiting_triage';
```

### 2. Validar a URL e o conteúdo

- Acessar a página diretamente
- Verificar:
  - a página existe?
  - o download real é PDF ou HTML disfarçado?
  - o conteúdo é livro de verdade?
  - há indício jurídico ruim?
  - o item está dentro do escopo editorial?
  - o idioma é português?

No BaixeLivros, desconfiar da vitrine. O que manda é a página real do item e o arquivo real baixado.

### 3. Decidir o destino

| Situação | Status | planned_author | planned_category_id | planned_synopsis |
|---|---|---|---|---|
| ✅ Tudo ok | `waiting_editor` | Preencher se disponível | Deixar vazio (preparer decide) | Deixar vazio (preparer escreve) |
| 🟡 Duplicata | `duplicate` | - | - | - |
| 🔴 Link quebrado / HTML no lugar do PDF | `triage_rejected` | - | - | - |
| 🔴 Não é livro | `triage_rejected` | - | - | - |
| 🔴 Pirataria / risco jurídico alto | `triage_rejected` | - | - | - |
| 🔴 Didático / pedagógico fora do alvo | `triage_rejected` | - | - | - |
| 🔴 Problema estrutural recorrente da source | `source_blocked` | - | - | - |

**`triage_rejected`** é o status para itens que passaram pelo filtro humano e foram rejeitados. Isso o diferencia de `error` (falha técnica do worker/extrator).

⚠️ **Regra de ouro**: `triage_rejected` **não** é um túmulo. O metadata é o rastro que permite recuperar itens no futuro. Se amanhã surgir um conversor Markdown→PDF, uma assinatura Leanpub, ou uma nova fonte, a query `WHERE metadata_json->'triage'->>'reason' = 'no_pdf'` traz todos os itens esperando. **Registre o motivo com precisão — isso é tão importante quanto a decisão.**

### Por que rejeitou? — Registro no metadata_json

Sempre registrar o motivo da rejeição em `metadata_json` para rastreabilidade futura:

```json
{
  "triage": {
    "rejected_by": "Raffa",
    "reason": "paywall",
    "detail": "Redirecionou para Leanpub — conteúdo gratuito apenas com assinatura"
  }
}
```

**Razões comuns (`reason`):**
- `dead_link` — 404, domínio morto, conteúdo não acessível
- `fake_pdf` — HTML, redirecionamento ou anti-download no lugar do PDF
- `not_a_book` — videoaula, curso, software, atividade, cartilha, slide, material modular
- `pirate` — material protegido sem autorização clara
- `legal_risk` — obra contemporânea ou edição suspeita sem segurança jurídica mínima
- `didactic_out_of_scope` — material pedagógico fora da missão editorial
- `incomplete` — rascunho, amostra, obra truncada
- `language` — fora do idioma aceito

Isso permite consultar depois: quantos itens foram rejeitados por paywall? Por link quebrado?

**Importante**: na triagem, **só preenchemos `planned_author`** se o autor estiver claro na fonte.  
Categoria e sinopse são responsabilidade da skill `sharebook-book-preparer` (status `waiting_editor`/`editing`).

### Gatilhos de suspeita — quando desconfiar e verificar mais

| Gatilho | Ação |
|---|---|
| Item em `/didatico/` | `triage_rejected` por `didactic_out_of_scope` |
| Título com cara de atividade escolar, alfabetização, caderno, colorir, professor, 1º ano, creche | suspeitar forte de `didactic_out_of_scope` |
| PDF < 100 KB | suspeitar de slide, amostra, artigo ou não-livro |
| Autor contemporâneo pouco conhecido com PDF completo | suspeitar de `legal_risk` |
| Tradução/adaptação moderna de clássico | suspeitar de `legal_risk` |
| Coletânea genérica sem origem clara | suspeitar de `legal_risk` ou `not_a_book` |
| Já temos livro do mesmo tema (não mesma obra) | não barrar, mas anotar se ajudar |

### Transição de status

```
waiting_triage  →  triaging  →  waiting_editor    (segue no pipeline)
                                duplicate         (já temos)
                                triage_rejected   (link quebrado / não-livro / pirataria / sem PDF)
                                source_blocked    (padrão problemático na fonte inteira)
      ①              ②                 ③
```

1. **① → ②**: Ao pegar o item para análise
2. **② → ③**: Após decisão tomada e banco atualizado

### 4. Baixar o PDF (obrigatório para itens aprovados)

Se o item for aprovado (`waiting_editor`), **o triador é responsável por baixar o PDF imediatamente**.  
O link original pode ficar indisponível. A triagem é a melhor hora para garantir o arquivo.

Salvar em:
```
sharebook-ebook-importer/triage-downloads/position_<PPP>-<slug>.pdf
```

Onde `<PPP>` é o `position` com zero-padding de 3 dígitos e `<slug>` é o slug do título.

Exemplo: position 11, título "Guia Foca Linux" →
```
triage-downloads/position_011-guia-foca-linux.pdf
```

### 4a. Validar o PDF baixado (obrigatório)

Antes de registrar no banco, validar:

```bash
file /tmp/<arquivo>.pdf
# Deve retornar: PDF document, version X.X, <N> pages
```

Se o comando `file` não estiver disponível no ambiente, instalar:
```bash
apt-get install -y file
```

Se o comando `pdftotext` não estiver disponível, instalar:
```bash
apt-get install -y poppler-utils
pdftotext /tmp/<arquivo>.pdf - -l 3 | head -20
```

**O que checar:**
- É um PDF válido? (não HTML disfarçado)
- Tem páginas reais? (6+ páginas — menos que isso é provavelmente artigo, não livro)
- O conteúdo está legível? (primeiras páginas com pdftotext)

### 4b. Gerar o slug

Sempre em lowercase, sem acentos, sem caracteres especiais:

```python
import re, unicodedata

normalized = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode('ascii')
slug = re.sub(r'[^a-z0-9]+', '-', normalized.lower()).strip('-')
slug = slug[:80]
# 'O Editor de Texto Vim' → 'o-editor-de-texto-vim'
# 'Guia da Computação em Nuvem: Conceito, Prática & Capacitação' → 'guia-da-computacao-em-nuvem-conceito-pratica-capacitacao'
```

### 5. Atualizar o PostgreSQL

Use sempre o banco do importer, schema `importer`.

Atualizar o `metadata_json` com o caminho do PDF baixado (relativo à raiz do `sharebook-ebook-importer`):

```python
import psycopg2, os, json

dsn = os.getenv('IMPORTER_DB_DSN')
conn = psycopg2.connect(dsn)
cur = conn.cursor()

item_id = <ID>
novo_status = '<waiting_editor|triage_rejected|source_blocked>'
autor = '<autor ou None>'
local_pdf = f"triage-downloads/position_{position:03d}-{slug}.pdf" if pdf_baixado else None

metadata = json.dumps({"local_pdf": local_pdf}) if local_pdf else None

cur.execute("""
  UPDATE importer.queue_items SET
    planned_author = COALESCE(%s, planned_author),
    status = %s,
    metadata_json = COALESCE(%s::jsonb, metadata_json),
    updated_at = NOW()
  WHERE id = %s AND status = 'triaging'
""", (autor, novo_status, metadata, item_id))

conn.commit()
conn.close()
```

**Exemplo completo de rejeição com motivo:**

```python
import psycopg2, os, json

dsn = os.getenv('IMPORTER_DB_DSN')
conn = psycopg2.connect(dsn)
cur = conn.cursor()

item_id = 136
motivo = json.dumps({
    "triage": {
        "rejected_by": "Raffa",
        "reason": "paywall",
        "detail": "Redirecionou para Leanpub — Free With Membership, conteúdo pago"
    }
})

cur.execute("""
  UPDATE importer.queue_items SET
    status = 'triage_rejected',
    metadata_json = %s::jsonb,
    updated_at = NOW()
  WHERE id = %s AND status = 'triaging'
""", (motivo, item_id))

conn.commit()
conn.close()
```

---

## Checklist de triagem

- [ ] URL acessível? (não 404, não domínio morto)
- [ ] Conteúdo é livro/publicação? (não curso, não atividade, não material pedagógico avulso)
- [ ] Não há risco jurídico alto?
- [ ] Não é didático fora do escopo?
- [ ] Idioma: português?
- [ ] Não é duplicata de obra já importada?
- [ ] Autor identificável? (se sim, preencher `planned_author`)
- [ ] Se aprovado: PDF do conteúdo baixado e validado?
- [ ] Para rejeição: status é `triage_rejected`, não `error`
- [ ] Para rejeição: `metadata_json->'triage'` preenchido com reason + detail
- [ ] Se aprovado: PDF salvo em `triage-downloads/position_<PPP>-<slug>.pdf`
- [ ] Se aprovado: `metadata_json->>'local_pdf'` preenchido
- [ ] Item marcado com status correto no PostgreSQL

---

## Teste cego de skill (validação)

Quando uma regra da skill for corrigida com base em erro do triador, validar a correção com um **teste cego**:

1. Corrigir a skill com a nova regra
2. Resetar o item para `waiting_triage` (limpar `planned_author`, `metadata_json`, remover PDF baixado)
3. Disparar um **subagente novo** com instrução apenas de ler a SKILL.md e executar a triagem
4. Se o subagente acertar seguindo a skill → regra validada
5. Se errar → a skill ainda está ambígua ou incompleta

**Regra**: nunca usar o mesmo agente que errou para validar a correção. O teste só vale com agente fresco que não sabe do erro anterior.

Nome técnico: **Teste Cego de Skill (Blind Skill Test)**.

---

## Erros comuns

1. **Confundir duplicata com complemento**: "CSS Iniciante" ≠ "CSS Avançado" , ambos seguem
2. **Aceitar infantil contemporâneo por simpatia**: bonitinho não é critério jurídico
3. **Confundir infantil com didático**: caderno, atividade e alfabetização não entram só porque falam com criança
4. **Aceitar conteúdo fora do português**: neste fluxo, manter português como padrão
5. **Marcar como `error` o que é rejeição humana**: rejeição deliberada usa `triage_rejected`
6. **Empurrar dúvida jurídica para frente**: se a dúvida é séria, rejeite cedo
7. **Rodar query no banco errado**: se `importer.queue_items` não existir, a conexão está errada
8. **Confiar mais nesta skill do que no código**: `pg_db.py`, `README.md` e `docs/PLAYBOOK.md` mandam mais que este arquivo.
