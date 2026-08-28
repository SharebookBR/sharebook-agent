# SEO v1 — concluída

> Encerrada em 27/08/2026 após revisão crítica das pendências restantes.

## Objetivo

Transformar o catálogo público do ShareBook em aquisição orgânica sustentável, com páginas tecnicamente corretas, conteúdo útil e decisões mensuradas por dados reais.

Este arquivo preserva o histórico das fatias entregues no épico.

## Fotografia atual

- 2.225 livros têm PDP pública e slug único.
- 1.073 estão disponíveis; 1.152 PDPs históricas continuam públicas e indexáveis.
- As PDPs agora usam meta descriptions programáticas, preservando título, autoria, tipo e uma síntese curta. Antes da correção, 2.058 passavam de 170 caracteres e 1.933 passavam de 300; a mediana era 865.
- 173 títulos, já com o sufixo `| ShareBook`, passam de 60 caracteres.
- O sitemap publica 2.278 entradas e todas as `<loc>` são distintas.
- Os 2.729 registros de `Books` têm slugs distintos e o banco possui índice único preventivo.
- 2 categorias-folha disponíveis têm mais de 100 livros, com apenas 6 livros além da primeira página; paginação indexável não justificou prioridade própria.
- Nos 28 dias consolidados de 27/07/2026 a 23/08/2026, o GSC registrou 1.167 cliques, 24.103 impressões, CTR de 4,84% e posição média de 9,11.
- Nos 28 dias anteriores, de 29/06/2026 a 26/07/2026, foram 981 cliques, 25.785 impressões, CTR de 3,80% e posição média de 5,04.

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
- Meta description, Open Graph e Twitter da PDP compartilham um resumo determinístico, normalizado e seguro no limite de palavra. A sinopse visível e o JSON-LD `Book` permanecem integrais.
- Slugs públicos são únicos no catálogo inteiro. A URL que cada colisão resolvia foi preservada; os demais exemplares receberam o primeiro sufixo `_copyN` disponível.
- Search Console está acessível pela service account e resumido no painel `/admin/analytics`, com comparação de períodos, tendência diária e oportunidades de CTR.

## Fatia 1 — Meta descriptions das PDPs — concluída em 25/08/2026

### Problema

A PDP enviava a sinopse inteira para `description`, `og:description` e `twitter:description`. Isso não era um resumo: em produção, a mediana era 865 caracteres.

O Google não define um limite rígido. A solução não deve ser cortar cegamente no caractere 160, e sim gerar uma descrição curta, legível, específica e única com título, autoria, tipo do livro e uma síntese segura da sinopse.

### Critério de pronto

- PDPs novas e antigas recebem description programática útil e sem corte no meio de palavra.
- Meta description, Open Graph e Twitter compartilham o mesmo resumo curto.
- Casos sem sinopse degradam para uma descrição válida baseada em título, autoria e tipo.
- Testes cobrem sinopse longa, curta, vazia e texto com quebra de linha.
- HTML SSR de amostras físicas e digitais confirma o contrato.

### Entrega

- Gerador puro e testável com alvo flexível de 170 caracteres.
- Fallback válido sem sinopse e degradação segura sem autoria.
- Testes para sinopse longa, curta, vazia, primeira frase longa e whitespace irregular.
- Commit frontend `97e3d38d086aecdb34d4fcb7cfad1b49deefed2c`.
- Deployment Coolify `nfyd3svzxougvcdjruffw5e8`, imagem exata saudável.
- HTML de produção validado em três PDPs reais: ebook longo, ebook institucional e livro físico; as três tags ficaram idênticas e o JSON-LD preservou a sinopse completa.

## Fatia 2 — Restaurar unicidade dos slugs públicos — concluída em 25/08/2026

Antes da entrega, produção tinha 2.225 registros no endpoint do sitemap, mas somente 2.206 slugs distintos: 17 slugs estavam repetidos em 36 livros.

O problema não nascia no sitemap. `Books.Slug` não possuía índice nem constraint única no Postgres, e o `BookMap` definia apenas o tamanho máximo. O gerador truncava o título em 45 caracteres e procurava exemplares pelo título completo, não por colisão do slug final. A rota por slug retornava uma única linha, tornando ambígua a resolução quando havia duplicata.

Livros e exemplares físicos repetidos continuam legítimos; o que precisa ser único é a chave pública de rota de cada registro.

### Ordem de correção executada

1. Identificar, em cada grupo, qual registro a URL atual resolve e preservar essa continuidade.
2. Dar slugs próprios aos demais registros, com redirects apenas onde existir uma URL histórica inequívoca a preservar.
3. Corrigir a geração para verificar colisão pelo slug final e suportar retry diante de concorrência.
4. Criar constraint única no banco para impedir regressão.
5. Confirmar que a API e o sitemap passam a emitir somente URLs únicas; dedupe defensivo na emissão não substitui o invariante de dados.

### Critério de pronto

- Zero grupos de slug duplicado entre registros públicos.
- Cada slug resolve exatamente um livro.
- O banco rejeita nova colisão de slug.
- A geração cria slugs distintos mesmo para títulos longos com os mesmos 45 caracteres iniciais e em criações concorrentes.
- A correção não apaga, cancela nem funde exemplares físicos.
- Cada `<loc>` aparece uma vez no sitemap como consequência do dado íntegro.

### Entrega

- Inventário encontrou 41 grupos duplicados no catálogo inteiro: 87 registros envolvidos e 46 slugs a corrigir. Os 17 grupos visíveis no sitemap eram apenas a parcela pública do problema.
- A migration preservou em cada grupo o registro que a rota já resolvia e atribuiu aos demais o primeiro slug livre no padrão existente: base, `_copy1`, `_copy2` etc.
- Novos livros calculam colisão pelo slug final, inclusive quando títulos diferentes truncam para os mesmos 45 caracteres.
- Corridas de criação são contidas pelo índice único `UX_Books_Slug`; a tentativa perdedora recalcula o próximo `_copyN` e repete a persistência.
- Edição de título não altera mais a URL pública do livro.
- Commit backend `0b86ee7284ebe272c67a1235e093d49fcbab0653`; deployment Coolify `q5tx8gmbq0aybbyyscckiwoz`, imagem exata saudável.
- Produção validada: 2.729 livros / 2.729 slugs distintos, zero sufixos GUID, maior slug com 51 caracteres, 2.225 slugs distintos no endpoint do sitemap e 2.278 `<loc>` distintas no XML.

## Fatia 3 — Search Console e mensuração — concluída em 26/08/2026

O acesso programático foi resolvido com a service account existente e a propriedade de domínio `sc-domain:sharebook.com.br`. A Search Analytics API agora alimenta o endpoint consolidado e uma visão simples em `/admin/analytics`.

### Entrega

- Recorte fixo dos últimos 28 dias consolidados, com atraso de 3 dias, comparado aos 28 dias anteriores.
- KPIs de cliques, impressões, CTR e posição média, além de série diária.
- Até cinco oportunidades de CTR por query e landing page, priorizadas pelo potencial estimado de cliques perdidos.
- Falha isolada: indisponibilidade do Search Console não derruba o restante do painel de GA4.
- Detalhes operacionais e evidências em [`search-console-access.md`](search-console-access.md).

Coortes de publicação e mensuração longitudinal das meta descriptions continuam como análises futuras orientadas pelos dados; não são bloqueios técnicos desta fatia.

## Hipóteses preservadas, ainda não provadas

- O catálogo maior pode aumentar aquisição orgânica por cobertura temática.
- PDPs históricas podem converter em afiliado Amazon mesmo quando o livro não está disponível para solicitação.

Essas hipóteses dependem de Search Console e coortes; não devem virar implementação por entusiasmo.

## Encerramento

- Meta descriptions das PDPs, unicidade dos slugs públicos e mensuração pelo Search Console foram entregues.
- `BreadcrumbList` e suporte genérico a múltiplos JSON-LD foram avaliados e cancelados: o possível ganho de apresentação no resultado de busca é incerto e não justifica competir com problemas de produto comprovados.
- Conhecimento estruturado da PDP também foi removido do backlog; qualquer retomada futura exige evidência nova, não herança deste épico.
- As hipóteses acima permanecem como perguntas analíticas, não como tarefas de implementação.
