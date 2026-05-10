# 🌐 SEO v1 — Sitemap + Breadcrumb

## 🎯 Objetivo

Melhorar a indexação do catálogo no Google e a apresentação nos resultados de busca, garantindo que:
- **todas as URLs públicas do site sejam descobertas** (sitemap dinâmico)
- **a navegação seja compreendida** (breadcrumb JSON-LD nas PDPs e categorias)

## 📋 Escopo

### 1. Sitemap.xml dinâmico
- Script separado (Node/Python — a definir)
- Consulta o banco e gera um XML com todas as URLs públicas:
  - home (`https://www.sharebook.com.br`)
  - categorias (`/categoria/<slug>`)
  - livros (`/livros/<slug>`)
- Servir em `/sitemap.xml`
- Atualizado semanalmente via job agendado (GitHub Action, Coolify job ou cron)

### 2. Breadcrumb JSON-LD
- Schema `BreadcrumbList` injetado via SSR
- Na PDP: `Home > Categoria > Título do Livro`
- Na categoria: `Home > Categoria`
- Depende de investigar se a API já retorna nome da categoria no payload do livro

### Fora do escopo
- Schema `Book` (missão separada se quiser)
- Canonical URL explícita (já é coberta pelo `og:url`, mas pode virar ajuste fino)
- Core Web Vitals / Lighthouse

## 🔍 Pré-requisitos

- [ ] Investigar se a API da PDP (`/api/Books/{slug}`) já retorna `categoryId` + `categoryName` — sem isso, breadcrumb na PDP exige chamada extra
- [ ] Decidir linguagem do script de sitemap (Node.js com acesso ao banco ou C# endpoint no backend)

## 📊 Métricas de sucesso

- Google descobre **100% das páginas públicas** em até 7 dias
- Breadcrumb aparece nos resultados de busca (CTR maior)
- Número de páginas indexadas no Search Console sobe

## 📌 Status

**Criada.** Não priorizada.
