# SSR em mais de um processo Node (depois da Cloudflare)

## Prioridade

**Logo depois da Cloudflare, por decisão do Raffa em 2026-11-14.** A ordem importa: com a Cloudflare guardando as páginas públicas na borda, o frontend deixa de precisar do cache SSR em memória, e multiplicar processos deixa de multiplicar esse cache.

## Por que

O teste de carga de 2026-11-14 (`../done/teste-carga-ssr-origem-externa.md`) mostrou o teto real: **~3 páginas novas por segundo**, porque o SSR é **um único processo Node, um núcleo**. O frontend ficou em 100–112% de CPU enquanto o host não passou de 76% (a VPS tem 4 vCPU). Aumentar as vagas do limitador no mesmo processo (12/6) **não aumentou a vazão**: só dobrou a latência e atrasou até as respostas de cache. A alavanca que sobra para páginas novas é usar mais núcleos.

O que impede fazer isso hoje: cada processo teria o próprio cache SSR em memória, e um cache cheio custou **~1,7 GiB** no teste. Dois ou três processos assim não cabem com folga numa VPS de 7,8 GiB que já tem ~2,5 GiB de swap parado.

## Escopo

- Rodar o SSR em 2–3 processos (cluster do Node ou réplicas atrás do Traefik), deixando núcleo livre para API, Postgres e proxy.
- **Reduzir ou retirar o cache SSR em memória**, já que a Cloudflare passa a ser o cache das páginas públicas. Manter a limpeza explícita de cache funcionando na borda.
- **Limitador por processo:** hoje o 6/3 vale para o processo único. Com N processos, decidir o limite de cada um (o total por núcleo que o teste validou é 6/3).
- Repetir o teste de carga com `playbooks/_shared/scripts/infra/load_test/` e comparar com 2026-11-14: páginas novas por segundo, p95 humano, memória do frontend e da API (no 12/6 a memória da API triplicou: mais montagens simultâneas = mais chamadas à API).

## Valor

Multiplica a capacidade de páginas novas, que é o que a CDN não resolve: a cauda longa do catálogo e os crawlers batendo em páginas frias.

## Risco

- Memória: se o cache em memória não sair, N processos multiplicam ~1,7 GiB.
- A API passa a receber N vezes mais chamadas simultâneas.
- O limitador e os logs `ssr_overloaded` passam a ser por processo; a leitura dos painéis muda.

## Validação

- Páginas novas por segundo sobem perto de N vezes, com zero 500 e humanos atendidos.
- Memória do host com folga sob carga (sem crescimento de swap).
- Comparação registrada com `../done/teste-carga-ssr-origem-externa.md`.

## Relações

- Pré-requisito: `cloudflare-cdn-ddos-protection.md`.
- Evidência: `../done/teste-carga-ssr-origem-externa.md`.
- Alternativa estrutural para a cauda longa: `pre-processamento-paginas-e-recomendacoes.md`.
