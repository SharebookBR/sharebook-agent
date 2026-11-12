# Pré-renderização (SSG) das páginas públicas

## Estado

**Aberto em 2026-11-12, prioridade baixa.** Já estava como frase solta em `playbooks/engineering/frontend.md` ("passo estrutural em aberto se o tráfego de crawler continuar crescendo"); promovido a item próprio depois do incidente de 03:26 BRT, em que crawler + SSR on-demand derrubaram a API por ~25 s.

## O que é

Hoje a home e a PDP (`/livros/:slug`) têm cache SSR de 30 min em memória (`server.ts`), mas **cada URL ainda é renderizada sob demanda na primeira visita**, e tags, categorias, listagens e busca nem cache têm. Um crawler passando por milhares de URLs frias vira milhares de renderizações cheias, cada uma com chamadas à API e ao Postgres.

Pré-renderizar (SSG ou cache persistente gerado em build/job) tira a renderização do caminho da requisição: o crawler recebe HTML pronto.

## Por que ainda não

Tema complexo (invalidação quando o livro muda, volume do catálogo, tempo de build, convivência com o cache atual). O item `protecao-sobrecarga-ssr.md` já limita o dano enquanto isso. Retomar se o tráfego de crawler seguir crescendo ou se o limite de concorrência começar a recusar o Googlebot com frequência (ver log de recusas).

## Valor, risco, validação

- Valor: alto no SEO e na estabilidade; esforço: alto; risco: médio (HTML pré-gerado desatualizado).
- Validação: Search Console mostra tempo de resposta menor e mais páginas rastreadas por dia; zero renderização on-demand de PDP em `ssr_access` durante rajada de crawler.
