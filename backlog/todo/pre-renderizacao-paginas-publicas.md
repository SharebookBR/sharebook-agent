# Pré-renderização (SSG) das páginas públicas

> Mesclado em 2026-11-14 por decisão do Raffa: este item absorveu `capacidade-ssr-vps-replicas-pre-renderizacao.md`. A pergunta "VPS maior, mais instâncias ou pré-renderização?" já tem direção decidida: **pré-processar** (páginas aqui; recomendações em `recomendacoes-pre-processadas.md`).

## Estado

**Aberto em 2026-11-12, prioridade baixa.** Já estava como frase solta em `playbooks/engineering/frontend.md` ("passo estrutural em aberto se o tráfego de crawler continuar crescendo"); promovido a item próprio depois do incidente de 03:26 BRT, em que crawler + SSR on-demand derrubaram a API por ~25 s.

## Decisão

**Direção decidida pelo Raffa (2026-11-14): pré-processar**, e não escalar a máquina para renderizar mais sob demanda. A forma (SSG, cache persistente gerado por job, ou outra) **ainda será discutida**; nada deve ser implementado antes dessa conversa. A prioridade **continua baixa** até o Raffa subir.

Contexto que sustentou a decisão (vindo do item de capacidade que foi mesclado aqui):

- O Node usa **1 dos 4 núcleos** por processo; ~3 a 4 renderizações novas por segundo é o teto medido (de dentro da VPS). O limite 6/3 é defensivo, não capacidade provada.
- **VPS maior sozinha não aumenta a vazão de renderização** do SSR. Ajuda API e banco, que dividem a máquina.
- **Mais instâncias do SSR** usariam os núcleos parados, mas cada uma teria o seu cache em memória, e a invalidação precisaria chegar a todas.
- Riscos a lembrar: escalar antes de medir mascara desperdício (por exemplo, o cálculo de recomendações); HTML pré-gerado pode servir conteúdo desatualizado.

**Reavaliar VPS maior ou réplicas apenas se** o teste de origem externa (`teste-carga-ssr-origem-externa.md`) mostrar que, mesmo com pré-processamento, falta capacidade.

**Complementos conversados em 2026-11-14, não decididos:** CDN na frente com cache longo para home e páginas de livro (o HTML já sai com `Cache-Control: public, max-age=1800`). Cuidados anotados: TTLs diferentes para e-book e livro físico (status muda), limpeza explícita nos eventos de mudança, revalidação em segundo plano, rotas logadas fora do cache, erros e páginas degradadas com `no-store` (já é assim). Ver também `cloudflare-cdn-ddos-protection.md` e `pipeline-capas-s3-cdn.md`. Para o cenário de divulgação grande (1 milhão de usuários em 8 h, ~35 usuários por segundo na média e 100 a 175 no pico), o primeiro gargalo provável é a entrega de imagens e arquivos estáticos pela própria VPS, **não medido**.

## O que é

Hoje a home e a PDP (`/livros/:slug`) têm cache SSR de 30 min em memória (`server.ts`), mas **cada URL ainda é renderizada sob demanda na primeira visita**, e tags, categorias, listagens e busca nem cache têm. Um crawler passando por milhares de URLs frias vira milhares de renderizações cheias, cada uma com chamadas à API e ao Postgres.

Pré-renderizar (SSG ou cache persistente gerado em build/job) tira a renderização do caminho da requisição: o crawler recebe HTML pronto.

## Por que ainda não

Tema complexo (invalidação quando o livro muda, volume do catálogo, tempo de build, convivência com o cache atual). O item `protecao-sobrecarga-ssr.md` já limita o dano enquanto isso. Retomar se o tráfego de crawler seguir crescendo ou se o limite de concorrência começar a recusar o Googlebot com frequência (ver log de recusas).

## Valor, risco, validação

- Valor: alto no SEO e na estabilidade; esforço: alto; risco: médio (HTML pré-gerado desatualizado).
- Validação: escolha da forma documentada com custo e capacidade esperada; teste externo confirma zero 500, swap controlado e recuperação; Search Console mostra tempo de resposta menor e mais páginas rastreadas por dia; zero renderização on-demand de PDP em `ssr_access` durante rajada de crawler.

## Relações

- Origem: `backlog/done/protecao-sobrecarga-ssr.md`.
- Recomendações: `recomendacoes-pre-processadas.md` (mesma direção; solução a discutir).
- Evidência de capacidade: `teste-carga-ssr-origem-externa.md`.
- Complementos: `cloudflare-cdn-ddos-protection.md`, `pipeline-capas-s3-cdn.md`.
