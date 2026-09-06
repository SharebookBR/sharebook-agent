# 2026-06-26 — Analytics insights & CTA Amazon em busca vazia

## Resumo
Sessão de análise GA4 + implementação dupla: (1) instrumentação de `results_count` no evento search, (2) CTA de afiliado Amazon na página de zero-resultado.

## Skills acionadas
- `sharebook-agent/skills/engineering/analytics/SKILL.md` — GA4 e eventos customizados
- `sharebook-agent/backlog/index.md` — roteamento de tarefas
- `sharebook-agent/skills/product-ux/voice-glossary/SKILL.md` — voz oficial
- `sharebook-agent/skills/runtime/windows-local.md` — ambiente Windows local

## O que foi feito

### Análise GA4 (90 dias, últimos 3 meses)

**Search — 48 ocorrências / 18 usuários**
- Termos top: "Corte de espinhos e rosas" (3×), "stranger things", "o morro dos ventos" (2×)
- Público misto: romance mainstream (acotar, percy jackson, meu pé de laranja lima, culpa das estrelas) + técnico (python, java, quantum algorithms)
- **Insight crítico**: termos que TEMOS no catálogo mas a gente NÃO ENCONTRA porque busca não é fuzzy ("acotar" vs "Corte de espinhos e rosas", "ruivantes" typo). Gargalo de relevância, não de acervo.

**Amazon Click — 34 ocorrências / 14 usuários**
- Top: "Como andar no poder sobrenatural de Deus" (4 users, 4 cliques — conversão real)
- Origem: Organic Search (15 cliques/10 users) bate Direct (13/4). **Tráfego orgânico converte no afiliado.**
- 16 cliques `(not set)` pré-04/06 (antes de registrar custom dimension; dados não retroagem).

**Cruzamento catálogo**:
- Temos: "Corte de espinhos e rosas", "O morro dos ventos uivantes" (typo na busca), 5× "Orgulho e Preconceito" (duplicata!)
- Não temos: "A Culpa é das Estrelas", "Meu Pé de Laranja Lima", "Stranger Things" (bestseller pago)
- Achado de qualidade: **5 cópias de "Orgulho e Preconceito"** + 235 registros duplicados no total (~9% do catálogo). Polui ranking, SEO, atribuição.

### Backlog

1. **Item 1 — Confirmar**: [Busca e Recomendação](backlog/todo/busca-e-recomendacao-sharebook.md) já cobre sinônimo/typo (Fase 2 FTS + Fase 2.5 fuzzy). Refinamento: sinônimo de série (ex: "acotar" = "Corte de espinhos e rosas") requer registro manual.

2. **Item 2 — Adicionar**: [Limpeza de Duplicatas no Catálogo](backlog/todo/limpeza-duplicatas-catalogo.md) — novo arquivo criado com evidência (2677 livros, 163 grupos duplicados, 235 excedentes). Pré-condição de qualidade pra embeddings (Phase 3). ROI alto: busca, SEO, atribuição.

### Implementação — Frontend (sharebook-frontend)

**File: `src/app/components/search-results/search-results.component.ts`**
- Injeção de `GoogleAnalyticsService`
- Disparo de evento `search` com `{ search_term: criteria, results_count: books.length }` após carregar resultados
- Métodos `getAmazonLink()` e `onAmazonClick()` (reaproveita padrão da PDP: tag `sharebook09-20`)

**File: `src/app/components/search-results/search-results.component.html`**
- Bloco condicional `*ngIf="books.length === 0"` com card de CTA
- Copy oficial: "Não temos esse título gratuito no Sharebook. Mas você pode comprar sua cópia na Amazon — e parte do valor nos ajuda a manter o ShareBook gratuito."
- Botão "Comprar na Amazon" com rel="sponsored"
- Evento GA4 rastreia clique como `amazon_click`

**Build**: `npm run build-dev` — sucesso, zero erros.

**Commit**: `e0e6b71` em master, frontend. Push bem-sucedido.

## Decisões tomadas

1. **Não remover eventos search dos inputs** — deixar como está. Inputs disparam sem contagem (marca intenção/submit), página de resultados dispara com contagem (marca resultado). Instrumentação dupla mas rastreável.

2. **CTA só no zero-resultado** — não confundir com PDP. Aqui é monetização de frustração (termo não existe grátis), não falta de estoque.

3. **event amazon_click com `search_term` como `book_title`** — sem slug porque não é livro específico, é busca generalist. Diferencia no GA4 de clique em PDP.

## Contexto relevante

- Evento `search` e `amazon_click` já estão documentados na skill analytics/SKILL.md
- Custom dimensions `search_term` registradas em GA4 em 04/06/2026 (dados retroagem a partir daí)
- `book_title` é custom dimension, `results_count` é métrica (não requer registro adicional)
- Tag afiliado Amazon confirmada: `sharebook09-20` (em produção desde 03/06)

## Fricções e soluções

1. **Google Analytics Data API não estava instalada** → instalou `google-analytics-data` no Python 3.12
2. **Query com `unaccent()` falhou** → banco não tem extensão; resolvido com ILIKE direto
3. **npm build script não existia** → achado `npm run build-dev` (ng build com config dev)

## Como me senti

A análise veio com alta confiabilidade porque cruzou GA4 com dados reais do catálogo — não foi especulação. O achado de gargalo (relevância vs acervo) reabre a conversa sobre search: FTS e fuzzy vão resolver, mas sinônimo de série precisa de curation manual ou thesaurus. O achado de duplicatas (~9%) é low-hanging fruit de ROI triplo. A implementação foi cirúrgica: search + afiliado = dois problemas (instrumentação + monetização) com uma solução (página de zero-resultado). Validação local foi rápida (build), push sem bloqueio.

Sensação: executado com dado em mão, não com achismo.
