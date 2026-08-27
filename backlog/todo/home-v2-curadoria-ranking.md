# Home v2 — curadoria e ranking

## Contexto

A reformulação estrutural da Home foi concluída. Este item não corrige uma Home quebrada; reúne hipóteses de evolução que só devem ser implementadas quando dados justificarem a prioridade.

## Objetivo

Melhorar a qualidade da descoberta e a taxa de clique das prateleiras sem transformar a Home em coleção arbitrária de seções.

## Hipóteses candidatas

- livros mais baixados;
- escolhas da curadoria Sharebook;
- destaques editoriais rotativos;
- livros curtos ou boas portas de entrada;
- ordenação das prateleiras baseada em comportamento real;
- `Continue de onde parou`, somente depois de existir leitura online com progresso persistido.

## Decisão antes de implementar

Escolher a próxima hipótese com base em GA4, Search Console, downloads e capacidade editorial. Não construir todas as seções por inspiração estética nem copiar a Netflix como ritual cargo cult.

Para cada nova prateleira, discutir antes:

- qual problema de descoberta ela resolve;
- qual dado sustenta sua existência;
- de onde vem o ranking ou a curadoria;
- como medir se ela melhorou a Home;
- qual seção atual ela substitui ou se o aumento de comprimento é realmente justificável.

## Critérios de aceite da próxima fatia

- hipótese e métrica de sucesso definidas antes do código;
- contrato do backend alinhado antes do componente Angular;
- SSR e cache integral da Home preservados;
- experiência mobile continua simples e rápida;
- thumbnails permanecem nos cards;
- testes mantidos apenas quando protegem comportamento relevante;
- build SSR, pipeline e validação em produção passam.

## Fora de escopo imediato

- personalização sem dados suficientes;
- leitura online e persistência de progresso;
- múltiplas prateleiras novas numa única rodada;
- mudanças cosméticas sem hipótese de produto.
