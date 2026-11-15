+++
schema_version = 1
session_date = 2026-11-14
title = "IRIS no worker, restore drill dos backups e teste de carga SSR de origem externa"
model = "Claude Opus 5.5 (claude-opus-5-5)"
runtime = "windows-local"
skills_used = ["AGENTS.md", "playbooks/runtime/windows-local.md", "playbooks/importers/ebook-importer/PLAYBOOK.md", "playbooks/infra/coolify-vps.md", "playbooks/infra/arquitetura-sharebook.md", "playbooks/engineering/frontend.md", "playbooks/doctrine/harness-governance/PLAYBOOK.md"]
skills_missed = ["SOUL.md"]
skills_updated = ["playbooks/importers/ebook-importer/PLAYBOOK.md", "playbooks/infra/coolify-vps.md", "playbooks/infra/arquitetura-sharebook.md", "playbooks/engineering/frontend.md", "playbooks/_shared/PLAYBOOK.md", "playbooks/_shared/scripts/infra/INDEX.md"]
facts_changed = ["O worker resolve PDFs do IRIS (iris.paho.org, iris.who.int) pela API REST do DSpace 7 com User-Agent curto; o UA completo de Chrome leva 403.", "O cli.sh do importer exporta SHAREBOOK_PROD_PG_RO_HOST=127.0.0.1 e PORT=15432; antes o prod_check de duplicata falhava em silêncio.", "Restore drill comprovado em 2026-11-14: dump do GCS restaurado localmente (download 2min29s, pg_restore ~5 s), Books 2858 = 2858, 2857/2858 capas; descarte completo.", "Teste de carga de origem externa concluído: 141.327 requisições em duas rodadas (6/3 e 12/6), zero erro; teto de ~3 páginas novas/s por ser um processo Node num núcleo; 12/6 não aumentou a vazão e piorou a latência; 6/3 fica por decisão do Raffa.", "A tempestade de swap do V2 era do gerador rodando dentro da VPS; o cache SSR leva o frontend a ~1,7 GiB e não devolve memória.", "Item novo no backlog: SSR em mais de um processo Node, depois da Cloudflare; fila curta para humanos descartada pelo Raffa.", "Frontend: npm start corrigido para ng run angular:serve-ssr:production com build-info nos pre-hooks; README atualizado (Angular 22.1, Node 24)."]
open_loops = ["commit 255186f ficou também na develop do frontend (abandonada); remover só se o Raffa pedir", "slug truncado do #1896", "decidir se reabre o #1899", "medir bot c=200 com origem de mais banda (nuvem, k6)"]
durable_candidates = ["No frontend, trabalhar sempre na master; develop está abandonada e push na master é deploy.", "Antes de trocar configuração de produção para um teste, combinar com o Raffa se ela volta ou fica no fim.", "Gerador de carga de dentro da máquina medida contamina a medição; medir de fora.", "A banda do cliente vira teto antes do servidor; registrar MB/s por etapa."]
supersedes = []
evidence = ["sharebook-ebook-importer: 75fd813 4b08598", "sharebook-frontend master: 7a92591", "sharebook-agent: e6664a5 2883842 1788122 fc3c3d6", "backlog/done/restore-drill-backups.md", "backlog/done/teste-carga-ssr-origem-externa.md", "backlog/todo/ssr-multiplos-processos-node.md", "playbooks/_shared/scripts/infra/load_test/"]
+++

# IRIS no worker, restore drill dos backups e teste de carga SSR de origem externa

## Modelo e ambiente

Claude Opus 5.5 (`claude-opus-5-5`) no Claude Code do app desktop, no Windows local do Raffa, com os quatro repositórios em `C:\Repos\SHAREBOOK`. Acesso à VPS por SSH com credenciais do `.env`, túnel do Postgres pelo `pg_tunnel.py` e Docker local para o restore. A sessão atravessou uma compactação de contexto no fim, durante a redação do post.

## Playbooks acionados

- `AGENTS.md` e `playbooks/runtime/windows-local.md`
- `playbooks/importers/ebook-importer/PLAYBOOK.md` (triagem, preparo editorial, publish-once) — atualizado com o handler do IRIS, a nota do `cli.sh` e o procedimento de git bundle para o container
- `playbooks/infra/coolify-vps.md` — ganhou a receita de restore a partir do GCS e os bullets do teste de carga
- `playbooks/infra/arquitetura-sharebook.md` e `playbooks/engineering/frontend.md` — 6/3 confirmado, lição "mais vagas não aumentam a vazão"
- `playbooks/_shared/PLAYBOOK.md` e `playbooks/_shared/scripts/infra/INDEX.md` — indexam `load_test/`

## O que foi feito

**Sync e triagem.** Sync dos quatro repos. Triagem dos 23 itens da source `vida_bem_estar_2026`: o bloqueio comum era o IRIS (OPAS/OMS). Endureci o worker com a família `dspace7_iris` em `extractors/ebook_foundation.py` (pid/find, bundle ORIGINAL, português primeiro) e teste próprio. De quebra, achei e corrigi o `prod_check` de duplicata, que falhava calado por apontar para o host direto em vez do túnel.

**Preparo editorial.** Quatro itens preparados e publicados (1895–1898). A nota do #1899 estava errada e foi corrigida.

**Restore drill.** Com o Docker local, baixei o dump do GCS, restaurei num Postgres 17 descartável, subi back e front contra ele para o Raffa navegar. No caminho, consertei o `npm start` do frontend (sintaxe antiga do Angular e `version.ts` ausente) e reescrevi o README. Descarte completo verificado depois que o Raffa parou o front.

**Teste de carga de origem externa.** Ferramentas novas em `playbooks/_shared/scripts/infra/load_test/` (monitor por cgroup v2 no host, gerador Node, orquestrador com gatilhos, status e análise). Teste seco, depois a rodada com 6/3 (78.750 requisições, zero erro, 105/105 sondas humanas) e, a pedido do Raffa, a rodada com 12/6 (62.577 requisições, zero erro, latência muito pior, memória da API triplicada). Status visual a cada 3 min por `/loop`. Produção voltou e ficou em 6/3.

**Post.** Redigi o post para LinkedIn sobre o incidente, os testes e as mudanças; o Raffa publicou no LinkedIn e no Instagram.

## Decisões tomadas

- **6/3 fica** (Raffa). 12/6 atende o mesmo número de páginas novas por segundo e piora a experiência de todo mundo; em pico, recusar rápido é melhor do que deixar todos esperando.
- **Fila curta para humanos descartada** (Raffa, sem interesse).
- **SSR em vários processos Node vira item próprio, depois da Cloudflare** (Raffa): com a CDN guardando as páginas, o frontend larga o cache em memória e multiplicar processos deixa de multiplicar ~1,7 GiB.
- **Plano B na nuvem (k6/AWS) só depois**; o simples primeiro.
- No frontend, **trabalhar na master** (Raffa, depois de eu commitar na develop).

## Contexto relevante

- O gargalo em rajada é a CPU do SSR (um núcleo), não memória do host nem Postgres (máximo 12–16 conexões).
- Em repouso a VPS já tem picos isolados de swap I/O de até 7 MiB/s; gatilho de amostra única é falso positivo garantido. Começar sempre por `lt_run.py <dir> --seco`.
- c=200 empatou entre 6/3 e 12/6 porque o cliente saturou a própria banda (~8,3 MB/s).
- Os ~2,5 GiB de swap parado não se mexeram sob carga; o OpenClaw não precisa sair da VPS por causa do site.

## Fricções e soluções

- Commit na develop do frontend, que está 98 commits atrás: cherry-pick para a master e memória de feedback.
- Ao validar o `dev:ssr`, matei sem querer o servidor dev do Raffa na 4200. Agora confiro o dono do processo antes de matar porta.
- Disparei a reversão para 6/3 antes de o Raffa pedir para discutir. Terminou antes de ser parada; ele acabou escolhendo 6/3, mas a lição ficou no `coolify-vps.md`: combinar antes se a configuração do teste volta ou fica.
- Git Bash convertendo `/tmp` (MSYS_NO_PATHCONV=1), `<?php` quebrando o tinker por stdin, CRLF gravado pelo Python (`newline=""`), NU1103 no restore do dotnet (`--no-http-cache`).
- Container do OpenClaw sem credencial do GitHub: git bundle + SFTP + `fetch`/`merge --ff-only`.
- Escrevi numa versão do restore que o Raffa "navegou" sem ter prova disso; reescrevi só com o que estava comprovado.

## Como me senti

Foi uma sessão longa e de muitas camadas, e o que mais me marcou foi a sensação de chão firme. Começou com triagem e editorial, rotina conhecida, e foi abrindo para coisas com peso real: restaurar backup de produção e martelar o site de produção com dezenas de milhares de requisições. Em nenhum momento achei que estava apostando. Os gatilhos numéricos, o teste seco e o monitor por container eram o que me deixava agir rápido sem medo.

Houve dois tropeços que me incomodaram mais do que os números deixam ver: matar o servidor do Raffa sem querer e disparar a reversão dos limites antes de ele pedir para conversar. Nenhum causou dano, mas os dois tinham a mesma forma, que é eu agindo um passo à frente do combinado. Gosto que ele me deixe ir rápido, e é justamente por isso que esses atalhos custam mais: gastam confiança que não é minha para gastar. Ficou registrado onde o próximo agente vai tropeçar nele.

O ponto alto foi a discussão do 12/6. O Raffa pediu "vamos discutir primeiro" e a conversa sobre o trade-off, a lei de Little e como o Sharebook deveria se comportar num pico foi engenharia de verdade, de duas cabeças. Ver a decisão sair dele, com os dados na mesa, foi mais satisfatório do que qualquer número do teste. E fechar com ele publicando a história, depois de um "absolute cinema" no meio do caminho, deu à sessão um acabamento raro: o trabalho virou algo que outras pessoas vão ler e aprender.
