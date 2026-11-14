# Pré-processamento: recomendações e páginas públicas

> Mesclado em 2026-11-14 por decisão do Raffa: este item absorveu `pre-renderizacao-paginas-publicas.md` (que já havia absorvido o item de capacidade SSR) e `recomendacoes-pre-processadas.md`. Os dois eram a mesma direção vista de dois lados.

## Estado

**Direção decidida pelo Raffa: pré-processar, e não escalar a máquina para calcular tudo sob demanda.** A **forma** (como, onde, quando atualizar, com que mecanismo) **ainda será discutida com o Raffa; nada deve ser implementado antes dessa conversa.** Prioridade **baixa** até o Raffa subir.

## Por que os dois viraram um só

1. **Dependência direta:** a página de um livro contém as recomendações. Pré-renderizar N páginas chama `Recommendations` N vezes (~190 ms de CPU cada). Sem pré-processar as recomendações, a pré-renderização só **muda o custo de lugar**, do visitante para o job que gera as páginas.
2. **A mesma invalidação:** livro novo, livro que mudou de status e livro removido afetam a página dele **e** as recomendações dos vizinhos. É uma pergunta só: "o que precisa ser refeito quando o catálogo muda?".
3. **O mesmo tipo de execução:** trabalho em lote sobre o catálogo, fora do caminho da requisição, que também alimentaria uma CDN.
4. **A mesma validação:** o custo por visita deve ficar perto do de uma leitura simples, mesmo numa rajada de livros diferentes.

## Duas frentes (que podem andar em ordem diferente)

### A. Recomendações pré-processadas (backend)
`GET /api/book/Recommendations/{id}` era a rota mais pesada do site: p50 de 221,69 ms e p95 de 425,90 ms no baseline, cerca de 40 vezes o `Slug`, ~35 mil chamadas por semana. O cache entregue na fatia 3a (backend `6d4f2cb`) tirou do banco a carga do catálogo, mas a latência melhorou pouco (p50 de 191,92 ms e p95 de 319,43 ms em 2026-11-13). O custo que sobrou parece ser **CPU da API a cada visita a um livro cujo resultado ainda não está em cache** (o ranking recalcula os vetores do catálogo inteiro a cada miss). **Hipótese, não medida.** Detalhes em `backlog/done/protecao-sobrecarga-ssr.md`, seção "Observação de Claude sobre o resultado parcial de `Recommendations`".

### B. Pré-renderização das páginas públicas (frontend/SSR)
Hoje a home e a página de livro (`/livros/:slug`) têm cache SSR de 30 min em memória (`server.ts`), mas **cada URL ainda é renderizada sob demanda na primeira visita**, e tags, categorias, listagens e busca nem cache têm. Um crawler passando por milhares de URLs frias vira milhares de renderizações cheias. Pré-renderizar (SSG ou cache persistente gerado em build ou job) tira a renderização do caminho da requisição.

## O que já foi decidido e o que não foi

**Decidido:** a direção é pré-processar; VPS maior sozinha **não** aumenta a vazão de renderização do SSR (o Node usa 1 dos 4 núcleos por processo; ~3 a 4 renderizações novas por segundo é o teto medido de dentro da VPS; o limite 6/3 é defensivo, não capacidade provada).

**Não decidido (a discutir):** a forma de cada frente; quando e como atualizar; o que fazer com livros novos, que mudaram de status ou foram removidos; onde guardar o resultado; granularidade da invalidação; a ordem entre A e B.

**Reavaliar VPS maior ou mais instâncias do SSR apenas se** o teste de origem externa (`teste-carga-ssr-origem-externa.md`) mostrar que, mesmo com pré-processamento, falta capacidade. Mais instâncias usariam os núcleos parados, mas cada uma teria o seu cache em memória.

**Complementos conversados em 2026-11-14, não decididos:** CDN na frente com cache longo para home e páginas de livro (o HTML já sai com `Cache-Control: public, max-age=1800`). Cuidados anotados: TTLs diferentes para e-book e livro físico (o status muda), limpeza explícita nos eventos de mudança, revalidação em segundo plano, rotas logadas fora do cache, erros e páginas degradadas com `no-store` (já é assim). Ver `cloudflare-cdn-ddos-protection.md` e `pipeline-capas-s3-cdn.md`. Para o cenário de divulgação grande (1 milhão de usuários em 8 h, ~35 usuários por segundo na média e 100 a 175 no pico), o primeiro gargalo provável é a entrega de imagens e arquivos estáticos pela própria VPS, **não medido**.

## Por que ainda não

Tema complexo (invalidação, volume do catálogo, tempo de geração, convivência com o cache atual). `protecao-sobrecarga-ssr.md` (concluído) já limita o dano enquanto isso. Retomar se o tráfego de crawler crescer, se o limite de concorrência passar a recusar o Googlebot com frequência (ver `ssr_overloaded` no Loki) ou se o teste externo mostrar falta de capacidade.

## Valor, risco e validação

- **Valor:** alto para SEO e estabilidade; hoje um crawler que visita muitos livros diferentes paga CPU em cada um. Esforço: alto.
- **Risco:** HTML ou recomendações defasados em relação ao catálogo; resultados diferentes dos atuais (o ranker tem testes que protegem o comportamento, e a página pré-gerada pode servir um status velho).
- **Validação esperada:** latência de `Recommendations` perto da de uma leitura simples; CPU da API estável durante uma rajada de livros diferentes; ranking equivalente ao atual nos casos cobertos pelos testes; escolha da forma documentada com custo e capacidade; teste externo confirma zero 500, swap controlado e recuperação; Search Console mostra tempo de resposta menor e mais páginas rastreadas por dia; zero renderização sob demanda de página de livro no `ssr_access` durante uma rajada de crawler.

## Relações

- Origem: `backlog/done/protecao-sobrecarga-ssr.md`.
- Evidência de capacidade: `teste-carga-ssr-origem-externa.md`.
- Tema geral de busca e recomendação (valor baixo na leitura atual do Raffa): `busca-e-recomendacao-sharebook/index.md`; este item trata só do custo de execução.
- Complementos: `cloudflare-cdn-ddos-protection.md`, `pipeline-capas-s3-cdn.md`.
