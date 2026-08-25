# SEO v1 — épico

> Última revisão: 24/08/2026 — auditoria do código, banco e HTML SSR de produção

## Objetivo

Transformar o catálogo público do ShareBook em aquisição orgânica sustentável, com páginas tecnicamente corretas, conteúdo útil e decisões mensuradas por dados reais.

Este arquivo é a única unidade de backlog do épico. As fatias abaixo orientam a execução sem criar um arquivo ou uma entrada no índice para cada microtarefa.

## Fotografia atual

- 2.225 livros têm PDP pública e slug.
- 1.073 estão disponíveis; 1.152 PDPs históricas continuam públicas e indexáveis.
- 2.058 PDPs usam meta description acima de 170 caracteres; 1.933 passam de 300.
- A sinopse usada como description tem média de 888 e mediana de 865 caracteres.
- 173 títulos, já com o sufixo `| ShareBook`, passam de 60 caracteres.
- O sitemap publica 2.278 entradas e contém 17 URLs duplicadas, cobrindo 36 registros.
- 15 categorias disponíveis têm mais de 24 livros.
- Os números de impressões, cliques, CTR e indexação do GSC ainda são de junho de 2026; não servem como fotografia atual.

## Concluído

- SSR real nas rotas públicas, com conteúdo e metadados no HTML inicial.
- HTTP `404` real para PDP inexistente.
- Sitemap dinâmico com páginas estáticas, PDPs, categorias e `lastmod`.
- `robots.txt` público apontando para o sitemap canônico.
- PDP com title, canonical, Open Graph, Twitter e JSON-LD `Book`.
- Home e catálogo com links internos para descoberta de PDPs e categorias.
- Busca interna mostra somente livros disponíveis; PDPs enviadas/recebidas continuam públicas e no sitemap. A decisão que antes estava pendente já foi implementada.
- Categorias, subcategorias, lista de categorias e novidades digitais usam canonical, Open Graph e Twitter coerentes com a própria URL.
- Alt da capa da PDP descreve título e autoria: `Capa do livro {título}, de {autor}`.

## Fatia 1 — Meta descriptions das PDPs — próxima

### Problema

A PDP envia a sinopse inteira para `description`, `og:description` e `twitter:description`. Isso não é um resumo: em produção, a mediana é 865 caracteres.

O Google não define um limite rígido. A solução não deve ser cortar cegamente no caractere 160, e sim gerar uma descrição curta, legível, específica e única com título, autoria, tipo do livro e uma síntese segura da sinopse.

### Critério de pronto

- PDPs novas e antigas recebem description programática útil e sem corte no meio de palavra.
- Meta description, Open Graph e Twitter compartilham o mesmo resumo curto.
- Casos sem sinopse degradam para uma descrição válida baseada em título, autoria e tipo.
- Testes cobrem sinopse longa, curta, vazia e texto com quebra de linha.
- HTML SSR de amostras físicas e digitais confirma o contrato.

## Fatia 2 — Breadcrumb e arquitetura de JSON-LD

Adicionar `BreadcrumbList` à PDP e às páginas de categoria.

Antes disso, o `SeoService` precisa suportar múltiplos dados estruturados ou um `@graph`: hoje `addStructuredData()` usa um ID fixo e a segunda chamada substituiria o schema `Book`.

### Critério de pronto

- `Book` e `BreadcrumbList` coexistem no HTML SSR.
- Hierarquia reflete Home → categoria → subcategoria → livro.
- O markup passa em validação estrutural e usa somente informação visível ou verdadeira.

## Fatia 3 — Higiene do sitemap

O sitemap repete 17 URLs porque 36 registros públicos compartilham slugs. Livros físicos repetidos podem ser legítimos; URL duplicada no sitemap não agrega descoberta.

### Critério de pronto

- Cada `<loc>` aparece uma vez.
- A correção não apaga, cancela nem funde exemplares físicos.
- Colisões de slug continuam registradas como diagnóstico de catálogo separado da emissão do sitemap.

## Fatia 4 — Search Console e mensuração

Resolver o acesso programático descrito em [`search-console-access.md`](../search-console-access.md) antes de priorizar por CTR, posição ou indexação.

Depois do acesso:

- atualizar a fotografia de queries, páginas, cliques, impressões, CTR e posição;
- cruzar coortes de publicação com tempo até primeira impressão e primeiro clique;
- medir as mudanças de meta description por grupo de páginas, sem atribuir causalidade cedo demais.

## Fatia 5 — Conhecimento estruturado — futura

Keypoints, idioma, nível, pré-requisitos, ISBN, páginas e gênero não existem hoje no schema de `Books`. Isso não é preenchimento de JSON-LD: exige decisão de produto, persistência e pipeline editorial antes de exposição pública.

Também não presumir que enriquecer o JSON-LD isolado produzirá estrelas ou rich results de livros. O recurso Book Actions do Google depende de feed, identificadores e participação aceita do provedor.

Só iniciar esta fatia quando os dados tiverem fonte confiável e uso além de SEO, como filtros, busca, recomendações ou experiência da PDP.

## Hipóteses preservadas, ainda não provadas

- Keypoints específicos podem ampliar cobertura semântica e melhorar snippets.
- O catálogo maior pode aumentar aquisição orgânica por cobertura temática.
- PDPs históricas podem converter em afiliado Amazon mesmo quando o livro não está disponível para solicitação.

Essas hipóteses dependem de Search Console e coortes; não devem virar implementação por entusiasmo.

## Ordem interna

1. Meta descriptions das PDPs.
2. Breadcrumb + múltiplos JSON-LD.
3. Dedupe da emissão do sitemap.
4. Search Console antes de experimentos orientados por CTR.
5. Conhecimento estruturado somente após desenho de dados e produto.

## Posição no backlog

O épico inteiro não é uma tarefa executável e não deve competir como bloco. A **Fatia 1 — Meta descriptions das PDPs** permanece no topo por combinar impacto amplo, evidência direta e esforço baixo. Quando ela terminar, o índice deve apontar para a próxima fatia real ou retirar SEO da primeira posição, conforme o valor relativo naquele momento.
