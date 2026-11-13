# Recomendações pré-processadas

## Estado

**Aberto em 2026-11-13. Não é urgente. A solução ainda será discutida com o Raffa: nada foi decidido nem deve ser implementado antes dessa conversa.**

## Posição do Raffa

As recomendações de uma página de livro deveriam ser **pré-processadas**, e não calculadas quando a página é visitada.

## Por que isso entrou no backlog

O incidente de 2026-11-12 (ver `protecao-sobrecarga-ssr.md`) mostrou que `GET /api/book/Recommendations/{id}` era a rota mais pesada do site: p50 de 221,69 ms e p95 de 425,90 ms no baseline, cerca de 40 vezes o `Slug`, com ~35 mil chamadas por semana.

O cache entregue na fatia 3a (backend `6d4f2cb`) tirou do banco a carga do catálogo, mas a latência melhorou pouco na medição parcial de 2026-11-13: p50 de 191,92 ms e p95 de 319,43 ms. O custo que sobrou parece ser CPU da API a cada visita a um livro cujo resultado ainda não está em cache. Isso é **hipótese, não medida**; o detalhamento está na seção "Observação de Claude sobre o resultado parcial de `Recommendations`" do item de proteção.

## O que ainda não está decidido

Tudo sobre a forma de fazer, incluindo quando e onde o cálculo acontece, como e quando ele é atualizado e o que se faz com livros novos ou que mudaram de status. A conversa com o Raffa define o escopo.

## Valor, risco e validação (a detalhar depois da conversa)

- **Valor:** hoje um crawler que visita muitos livros diferentes ainda gera custo de CPU em cada um; o objetivo é que a visita deixe de pagar por esse cálculo.
- **Risco a considerar:** recomendações defasadas em relação ao catálogo; resultados diferentes dos atuais (o ranker tem testes que protegem o comportamento).
- **Validação esperada:** latência de `Recommendations` perto da de uma leitura simples; CPU da API estável durante uma rajada de livros diferentes; ranking equivalente ao atual nos casos cobertos pelos testes.

## Relação com outros itens

- `protecao-sobrecarga-ssr.md`: origem das medições e do incidente.
- `busca-e-recomendacao-sharebook/index.md`: tema geral de busca e recomendação (valor baixo na leitura atual do Raffa); este item é só a parte de custo de execução.
- `pre-renderizacao-paginas-publicas.md`: solução estrutural para o custo do SSR; este item trata do custo do cálculo de recomendações.
