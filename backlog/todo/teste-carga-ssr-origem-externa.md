# Teste de carga SSR de origem externa e investigação de memória/swap do host

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
- Capacidade e direção estrutural (pré-processar): `pre-renderizacao-paginas-publicas.md`.
- Pode compartilhar a janela do teste de estresse do Postgres: `investigar-pool-conexoes-e-limite-postgres.md`.
- A série de CPU, memória, swap e conexões vem da fase 3 do Alloy: `observabilidade-sharebook-epico.md` (M7).
