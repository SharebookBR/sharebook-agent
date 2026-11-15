# Teste de carga SSR de origem externa e investigação de memória/swap do host

> **Concluído em 2026-11-14 (noite).** Duas rodadas do roteiro V2 completo, de fora da VPS (Windows local do Raffa, pela URL pública): com os limites de produção **6/3** e, por pedido do Raffa, com **12/6**. **Zero erro nas duas** (0 HTTP 500, 0 Npgsql, 0 falha de cliente em 141.327 requisições), nenhum gatilho de parada, nenhuma tempestade de swap. **Decisão do Raffa: 6/3 fica.** O 12/6 não aumentou a vazão e piorou a experiência de todo mundo. Ferramentas reaproveitáveis em `playbooks/_shared/scripts/infra/load_test/`.

## Resultado (2026-11-14)

**Origem:** Windows local do Raffa, banda medida de ~8,3 MB/s. Gerador Node (`lt_gen.mjs`) com `Accept-Encoding: gzip` (página ~50 KB comprimida), User-Agents `SharebookLoadTest/1.0` e `SharebookLoadTest-bot/1.0`, só GET público de 2.402 URLs de livro e categoria do sitemap, teto de 500 req/s. Monitor de 1 s no host (`lt_monitor.py`): CPU, RAM, swap, `pswpin/pswpout`, **RAM, swap e CPU por container via cgroup v2** (`memory.current`, `memory.swap.current`, `cpu.stat`), top de processos por RSS/swap a cada 5 s, saúde/restarts e erros da API. Gatilhos do V2, avaliados a cada amostra pelo orquestrador (`lt_run.py`). Antes, 60 s de teste seco com o site em repouso: nenhum gatilho.

**Rodada 6/3 (produção), por etapa:**

| Etapa | 200 | 503 (`Retry-After: 5`) | erro | p95 200 | p95 503 | 200/s | frias/s |
|---|---:|---:|---:|---:|---:|---:|---:|
| humano c=3 | 182 | 0 | 0 | 1.403 ms | — | 3,0 | 2,8 |
| humano c=6 | 194 | 0 | 0 | 2.995 ms | — | 3,2 | 2,7 |
| humano c=12 | 1.631 | 6.051 | 0 | 2.357 ms | 118 ms | 26,7 | 3,2 |
| humano c=24 | 5.248 | 13.893 | 0 | 260 ms | 143 ms | 85,1 | 3,6 |
| bot c=5 | 1.110 | 1.840 | 0 | 1.475 ms | 45 ms | 18,8 | 2,8 |
| bot c=15 | 5.481 | 7.988 | 0 | 186 ms | 133 ms | 90,7 | 3,0 |
| bot c=50 | 9.392 | 12.673 | 0 | 258 ms | 201 ms | 154,8 | 3,6 |
| bot c=200 (30 s) | 5.532 | 7.394 | 0 | 1.103 ms | 503 ms | 181,0 | — |

("frias/s" = 200 com 500 ms ou mais, proxy de página montada do zero.) Sondas humanas durante os bots: **105/105 HTTP 200**, p95 2,1 s; recuperação 36/36, p95 569 ms, sem restart. Postgres no máximo 12 conexões. CPU do host no máximo 76%; **frontend a 100–112%, um núcleo inteiro**.

**Critérios:** zero 500/Npgsql ✅; Postgres < 80 ✅; reserva humana ✅; cache HIT rápido ✅; `Retry-After: 5` em 49.839/49.839 503 ✅; recuperação sem restart ✅; p95 do 503 < 300 ms ✅ até bot c=50. Em bot c=200 foi 503 ms, mas **a origem saturou**: o cliente recebeu 9,4 MB/s contra ~8,3 MB/s de banda medida, e a fila foi do lado do cliente, não do limitador. Medir c=200 de verdade exige origem com mais banda (plano B: k6/gerador numa nuvem), ainda não feito.

**Rodada 12/6 (pedido do Raffa, aplicada por restart do Coolify e revertida a 6/3 em seguida):**

| Etapa | p95 200 (6/3 → 12/6) | 200 entregues (6/3 → 12/6) | frias/s (12/6) |
|---|---|---|---:|
| humano c=12 | 2,4 s → **5,6 s** | 1.631 → **218** | 2,7 |
| humano c=24 | 0,26 s → **4,6 s** | 5.248 → **2.781** | 3,4 |
| bot c=15 | 0,19 s → **1,2 s** | 5.481 → **3.395** | 3,4 |
| bot c=200 | 1,1 s → 1,3 s | 5.532 → 5.474 (empate: teto da banda do cliente) | — |

Sondas humanas 124/124 HTTP 200, mas p95 de 3,2 s (2,1 s com 6/3). Zero erro. **Memória da API triplicou** (308 MiB → 1,23 GiB de pico; 391 MiB com 6/3) e a RAM disponível do host caiu a 2,17 GiB.

**Leitura:** o teto de páginas novas é **~3 por segundo (~180 por minuto)** com 6 ou com 12 vagas, porque o SSR é um único processo Node, um núcleo. Mais vagas não aumentam a vazão (lei de Little): só aumentam a espera de cada um e, como o Node faz uma coisa por vez, atrasam **até as páginas em cache**. Páginas em cache chegaram a ~180/s, limitadas pela banda da origem. **O gargalo em rajada é a CPU do SSR (um núcleo)**, não memória do host nem Postgres.

**Parte B (memória e swap):** nas duas rodadas, swap usado **+0 MiB** e nunca 2 s seguidos de swap I/O acima de 1 MiB/s; picos isolados (até 7,6 MiB/s) aparecem igual com o site em repouso (teste seco: 3 de 53 amostras acima de 1 MiB/s, sempre isoladas). Conclusão: **a tempestade de swap do V2 veio do gerador rodando dentro da VPS**, não do site. Os 2,4–2,6 GiB de swap em repouso são páginas paradas, que não se mexeram sob carga: gateway do OpenClaw ~344 MiB, Coolify ~274 MiB, Stalwart ~230 MiB, Claude Code dentro do OpenClaw ~212 MiB, API ~189 MiB, `fwupd` ~129 MiB. **Não é preciso tirar o OpenClaw da VPS por causa da carga do site.** Achado novo: o **cache SSR** levou o frontend de ~250 MiB a **1,7 GiB** e não devolve memória (1,63 GiB depois do teste); a RAM disponível do host foi de 4,2 a 2,5 GiB.

**Desdobramentos (2026-11-14):**

- ~~Fila curta só para humanos (esperar até ~3 s por uma vaga antes do 503)~~: **descartada pelo Raffa em 2026-11-14**, sem interesse.
- Alavancas que sobem o teto: mais processos Node (**virou item próprio, depois da Cloudflare: `../todo/ssr-multiplos-processos-node.md`**) (usar 2–3 dos 4 núcleos, mas cada um com seu cache de até 1,6 GiB: exige limitar ou compartilhar o cache), Cloudflare na frente (`../todo/cloudflare-cdn-ddos-protection.md`) e pré-processamento (`../todo/pre-processamento-paginas-e-recomendacoes.md`).
- Medir bot c=200 com origem de mais banda (nuvem).

---

> Mesclado em 2026-11-14 por decisão do Raffa: este item absorveu `pressao-memoria-swap-host-sob-inundacao.md`. As duas frentes pedem o mesmo teste, a mesma janela e as mesmas amostras; fazer separado dobraria o risco para o site.

## Escopo

**Parte A: repetir o teste de carga de fora da VPS.** Repetir o roteiro controlado do V2 com uma máquina **fora da VPS**, pela URL pública e com os limites atuais 6/3. Manter guardrails de parada, User-Agents identificáveis (`SharebookLoadTest/1.0` e `SharebookLoadTest-bot/1.0`), coleta por requisição (início, tempo total, status e **valor** do `Retry-After`) e amostragem de 1 s de CPU, memória, swap e Postgres.

**Parte B: atribuir a pressão de memória e swap do host.** No V2, apesar de zero 500, houve **10 s consecutivos de swap I/O acima de 1 MiB/s** (última amostra: 1.091,1 KiB/s de swap-in e 5.541,1 KiB/s de swap-out) e crescimento de ~273 MiB de swap. Identificar **quem** consome memória e gera esse I/O sob rajada, com série **por processo e por cgroup**, e decidir se OpenClaw, browser sidecar e outros processos residentes devem sair da VPS de produção.

O que já se sabe (rodada 4, `backlog/done/protecao-sobrecarga-ssr.md`): VPS de 4 vCPU, 7,8 GiB de RAM, 4 GiB de swap, `swappiness=10`; **2,2 GiB de swap já em uso em repouso**, com ~3,5 GiB de RAM disponível (swap antigo, de páginas paradas, não necessariamente aperto contínuo). Maiores consumidores de RAM: OpenClaw ~1,1 GiB, frontend ~800 MiB de RSS (cache SSR de até 1.000 páginas), API ~275 MiB. Maiores `VmSwap`: gateway do OpenClaw 316 MB, Stalwart 180 MB, `fwupd` 129 MB, `dockerd` 81 MB, `dotnet` da API 78 MB. **Não há série histórica de RAM e swap.**

**Hipóteses, nenhuma medida:** o OpenClaw divide a máquina com o site; o cache SSR de 1.000 páginas infla o Node; o próprio gerador de carga contribuiu quando rodou dentro da VPS (a Parte A elimina isso).

## Valor

- **A:** separa o gerador da CPU e da rede da produção e valida o caminho Internet → Traefik → SSR de verdade; é o que falta para responder "quantos usuários por minuto o Sharebook aguenta" com um número defensável.
- **B:** hoje o limite 6/3 funciona, mas **não sabemos se a máquina passa perto do limite por memória**. Atribuir a pressão antes de chamar o limite de estável e antes de subir capacidade.
- Juntas: um só teste produz as duas respostas, e a série por processo permite distinguir carga do site, do gerador e dos vizinhos.

## Risco

Pode degradar o site se limites ou guardrails falharem; o profiling e a carga competem com a produção. Exige janela autorizada (preferir madrugada, fora de jobs agendados e backups), origem única externa, comando de parada imediato e retenção segura das amostras. Avisar o time antes (e-mails do Rollbar).

## Validação

- 503 com `Retry-After: 5` e p95 abaixo de 300 ms; zero 500 e zero erro Npgsql; Postgres abaixo de 80 conexões; reserva de vaga humana sob bot; cache HIT rápido; `peakInFlight=6`; recuperação sem restart. Comparar explicitamente com o V2 local de 2026-11-14.
- Série por processo/cgroup e do host **atribui** a pressão de memória e swap a consumidores identificados.
- Uma nova rajada **sem 10 s consecutivos acima de 1 MiB/s de swap I/O e sem crescimento de swap acima de 300 MiB**, **ou** uma correção documentada (por exemplo, retirar processos da VPS ou ajustar o cache) com revalidação.
- Resposta registrada: o gargalo em rajada é CPU do SSR, memória do host ou outro.

## Relações

- Origem: `backlog/done/protecao-sobrecarga-ssr.md` (V1, V2 e rodada 4).
- Capacidade e direção estrutural (pré-processar): `pre-processamento-paginas-e-recomendacoes.md`.
- Pode compartilhar a janela do teste de estresse do Postgres: `investigar-pool-conexoes-e-limite-postgres.md`.
- A série de CPU, memória, swap e conexões vem da fase 3 do Alloy: `observabilidade-sharebook-epico.md` (M7).
