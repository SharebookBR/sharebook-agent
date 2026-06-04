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

### 7. Decisão pendente: livros doados devem aparecer na busca interna? — **discussão necessária**

Temos 1.647 livros físicos já doados (Received/Sent/Canceled) indexados e com PDP funcionando.
Agora que as PDPs desses livros têm o botão Amazon, elas têm valor real — não são mais becos sem saída.

**Trade-offs a discutir:**

| Abordagem | Prós | Contras |
|---|---|---|
| Mostrar normalmente na busca | Mais conteúdo indexável, mais chance de rankear, Amazon button ativo | Frustra usuário que quer receber o livro e não pode |
| Não mostrar na busca interna | Busca interna só retorna livros acionáveis | Perde tráfego orgânico do Google em livros populares já doados |
| Mostrar por último (depois dos disponíveis) | Equilíbrio — disponíveis primeiro, doados como fallback | Complexidade de ordenação, pode ainda frustrar |
| Mostrar com label claro "já doado" | Expectativa gerenciada desde a listagem | Usuário pode ignorar e não chegar na PDP |

**Perguntas que precisam de resposta antes de decidir:**
- Qual % dos cliques orgânicos do Google vai pra livros já doados vs. disponíveis?
- O usuário que chega via Google numa PDP de livro doado converte no Amazon? (monitorar com GA `amazon_click`)
- A busca interna e o tráfego orgânico do Google são públicos diferentes com intenções diferentes?

**Hipótese:** busca interna = intenção de receber grátis → filtrar doados faz sentido. Tráfego orgânico Google = descoberta/informação → manter indexado e com Amazon button é o correto. As duas estratégias podem coexistir.

---

## 📊 Métricas de sucesso

- Páginas indexadas: de 1.360 → 2.000+
- CTR médio das PDPs: de ~0,3% → 1%+
- "ponto de impacto" e "arraiá na floresta": de 1 clique → 5+ cliques/mês
- Rich results aparecendo para livros com Schema `Book` completo

## 📌 Status

**Atualizado.** Prioridade: **média-alta** — base indexada, hora de otimizar qualidade.
