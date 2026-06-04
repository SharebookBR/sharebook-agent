# 🌐 SEO v1 — Plano Atualizado

> Última revisão: 2026-06-03 — dados reais do GSC e análise de PDP

---

## 📊 Estado atual do catálogo (GSC + banco, jun/2026)

| Métrica | Valor |
|---|---|
| Livros com slug no banco | 2.576 |
| Páginas indexadas pelo Google | 1.360 |
| Páginas não indexadas | 375 |
| Páginas ainda não descobertas | ~841 |
| Cliques orgânicos (mar–jun/2026) | 384 |
| Tendência | ↑ crescendo desde abril |

O spike de indexação aconteceu em ~06/04/2026 — quando o Google processou o bulk import de março (home passou a linkar para livros). Antes: ~300 páginas. Depois: ~1.800.

**Conclusão:** o problema não é mais descoberta/indexação. É qualidade de conteúdo e CTR.

---

## 🔑 Hipótese dos Keypoints (alta confiança, não validada estatisticamente)

**Observação:** "Como andar no poder sobrenatural de Deus" (Cash Luna) ranqueia top 1 no Google para o termo exato — acima de Sebo Viana e Touché Livros que são e-commerces com domínio velho.

**O que diferencia essa página:** o Google usou os bullet points dos keypoints como snippet nos resultados:
> *"Recursos — Entender e operar no sobrenatural; — Promover cura aos enfermos; — Ouvir a voz de Deus..."*

**Hipótese:** keypoints ricos funcionam como mini índice temático do livro. O Google mapeia subtópicos que aparecem em buscas relacionadas, gerando cobertura semântica ampla com uma única página.

**Implicação:** livros sem keypoints ou com keypoints genéricos provavelmente não ranqueiam. Livros com keypoints densos e específicos têm vantagem desproporcional.

**Como validar:**
```sql
SELECT
  COUNT(*) FILTER (WHERE "KeyPoints" IS NOT NULL AND "KeyPoints" != '[]') as com_keypoints,
  COUNT(*) FILTER (WHERE "KeyPoints" IS NULL OR "KeyPoints" = '[]') as sem_keypoints
FROM "Books"
WHERE "Status" = 1; -- Available
```
Cruzar com dados de posição no GSC por URL para confirmar correlação.

---

## 🎯 Oportunidades identificadas no GSC (jun/2026)

### Alta impressão, baixo CTR — ganho imediato sem melhorar ranking

| Query | Impressões | Cliques | CTR | Ação |
|---|---|---|---|---|
| ponto de impacto | 242 | 1 | 0,4% | Meta description + title melhores |
| arraiá na floresta vem cá | 150 | 1 | 0,7% | Idem |

Essas páginas já aparecem no Google — só não estão sendo clicadas. Meta description controlada pode multiplicar cliques sem mudança de posição.

---

## 🛠️ Gaps técnicos da PDP (identificados em análise de página)

| Gap | Impacto | Status |
|---|---|---|
| Sem `meta description` | Google escolhe o trecho — às vezes funciona, mas perde controle do CTR | pendente |
| Schema.org `Book` (JSON-LD) | Rich results: estrelas, autor, tipo — aumenta CTR e confiança | **parcialmente feito** — `addStructuredData` já existe no `getBook()`, mas sem `isbn`, `numberOfPages`, `inLanguage` |
| Open Graph tags | Compartilhamento social sem preview rico | pendente |
| Alt text da capa | Sinal de imagem desperdiçado (`alt="Book image"` genérico) | pendente |
| Categoria "Conhecimento & Carreira" em livros religiosos | Sinal temático errado para o Google | editorial — corrigir no banco caso a caso |

---

## 📋 Escopo original (revisado)

### 1. ~~Sitemap.xml dinâmico~~ — baixa prioridade
Google já indexou 1.360 páginas sem sitemap. Útil para garantir cobertura dos ~841 restantes, mas não é o gargalo.

### 2. robots.txt — manter no escopo
Ainda vale orientar o Googlebot e bloquear áreas admin.

### 3. Breadcrumb JSON-LD — manter no escopo
`BreadcrumbList` na PDP aumenta CTR via rich result de navegação.

### 4. Meta description dinâmica — **nova prioridade alta**
Gerar a partir dos primeiros ~160 chars da sinopse ou dos keypoints. Controla o snippet no Google.

### 5. Schema `Book` completo — **nova prioridade média**
Expandir o que já existe: adicionar `isbn`, `inLanguage`, `numberOfPages`, `genre`.

### 6. Alt text dinâmico na capa — **nova prioridade baixa**
Substituir `"Book image"` por `"Capa do livro {título} de {autor}"`.

---

## 📊 Métricas de sucesso

- Páginas indexadas: de 1.360 → 2.000+
- CTR médio das PDPs: de ~0,3% → 1%+
- "ponto de impacto" e "arraiá na floresta": de 1 clique → 5+ cliques/mês
- Rich results aparecendo para livros com Schema `Book` completo

## 📌 Status

**Atualizado.** Prioridade: **média-alta** — base indexada, hora de otimizar qualidade.
