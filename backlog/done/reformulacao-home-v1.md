# Reformulação da Home v1 — concluída

## Objetivo entregue

A Home deixou de ser uma lista genérica e passou a funcionar como vitrine de descoberta de livros gratuitos, com experiência mobile baseada em prateleiras horizontais.

## Entregas

- posicionamento explícito para livros digitais gratuitos e livros físicos disponíveis;
- hero com tamanho real do catálogo e CTAs para explorar e doar;
- assinatura `Doe. Ganhe. Leia.` preservada;
- prateleiras SSR de livros físicos, novidades digitais, vitrine editorial e categorias;
- navegação horizontal mobile e controles inteligentes no desktop;
- vitrine editorial fixa de mitologia grega;
- links para catálogo, categorias e página de novidades;
- `Organization`, `WebSite` e `SearchAction` em dados estruturados;
- sitemap, robots e metadados alinhados à descoberta de PDPs e categorias;
- endpoint compacto para livros físicos e cache integral do HTML SSR;
- thumbnails WebP nas prateleiras, reduzindo em 94,8% o peso das capas na amostra de produção de 26/08/2026.

## Decisão de encerramento — 2026-08-27

A fundação estrutural está concluída. Hero rotativo, ranking, curadoria dinâmica e personalização não são pendências desta entrega; são hipóteses de uma Home v2 e devem competir separadamente por prioridade.

## Evidências de referência

- `sharebook-frontend@ce6f85e` — redesign com hero e prateleiras horizontais;
- `sharebook-frontend@aaccdf0` — vitrine por categorias;
- `sharebook-frontend@593d374` — vitrine editorial de mitologia grega;
- `sharebook-frontend@b13bc6f` — descoberta de catálogo e SEO;
- `sharebook-frontend@404e5d2` — thumbnails nas listagens.
