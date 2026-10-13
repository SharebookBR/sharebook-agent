+++
schema_version = 1
session_date = 2026-09-17
title = "Angular 19 em produção: deploy dev -> validação -> promoção -> hotfix de conteúdo, pela primeira vez a partir do habitat 3"
model = "Claude Opus 5 (1M context), via Claude Code CLI"
runtime = "claude-code-openclaw"
skills_used = ["AGENTS.md", "SOUL.md", "runtime/claude-code-openclaw", "runtime/INDEX", "infra/INDEX", "infra/coolify-vps", "doctrine/harness-governance (contrato de memória v1)"]
skills_missed = []
skills_updated = ["infra/coolify-vps (polling da fila a partir do habitat 3 + teste de 404 real no SSR)", "runtime/claude-code-openclaw (acesso à VPS, git por token, espera sem sleep, build local do frontend)"]
facts_changed = [
  "sharebook-frontend em produção roda a partir do commit 041b978 (Angular 19.2.x, Material MDC, @angular/ssr com allowedHosts, mais hotfix de conteúdo em /apoie-projeto). master = develop = 041b978; dev.sharebook.com.br ficou em 8fceeb2 (mesmo código, só sem o texto novo).",
  "Página /apoie-projeto: card de tecnologias agora diz Angular 19 / TypeScript 5 (era Angular 13+ / Typescript 4) e PostgreSQL (era SQL Server) — fonte em src/app/core/services/technologies/technologies.service.ts.",
  "Build local do sharebook-frontend funciona no habitat 3: Node 22.23, npm ci ~30s, npm run build:ssr ~35s. O node_modules que estava no volume era da era do Angular 13 (TypeScript 4) e quebrou o build com TS6046 até rodar npm ci.",
  "GitHub Dependabot na branch default do sharebook-frontend: 110 -> 57 vulnerabilidades (1 crítica, 29 altas, 24 moderadas, 3 baixas) como efeito da migração 16->19.",
  "O webhook do GitHub continua não enfileirando deploy no Coolify — confirmado hoje duas vezes (app dev e app prod), no mesmo dia. Deploy manual via queue_application_deployment é o caminho normal, não exceção.",
  "vps_ssh.py funciona no habitat 3 (paramiko 5.0.0 instalado, ssh e sshpass no PATH), lendo o .env canônico em /data/workspace/sharebook-agent/.env.",
  "sharebook-ebook-importer no habitat 3 precisa do token GitHub do .env pra fetch/pull por HTTPS (sem credential helper configurado); sharebook-agent e sharebook-frontend puxaram sem token.",
]
open_loops = [
  "Dependabot: 57 vulnerabilidades na branch default do sharebook-frontend (1 crítica, 29 altas). Caiu de 110, mas merece sessão dedicada, sem misturar com migração.",
  "sharebook-frontend-dev (dev.sharebook.com.br) segue no ar permanentemente, batendo na API de produção. Não ficou decidido se vira estágio permanente ou se desprovisiona depois desta migração.",
  "Diff não commitado em sharebook-backend (StalwartWebhookVM.cs, [JsonPropertyName] nos campos do webhook) — terceira sessão consecutiva que encontra isso pendurado. Continua sem decisão: trabalho terminado ou experimento?",
  "browser-uj0tkohotwrp4epy0leaz28z (sidecar de browser do OpenClaw) unhealthy há 2 semanas — herdado da memória da madrugada, não tocado.",
  "pegasus-core-api e simula-plus-api em produção sem referência no corpus — herdado, não tocado.",
  "Migração Angular parou em 19 por decisão do Raffa. Continuar pra 20 depende de pedido novo.",
]
durable_candidates = [
  "Polling de deploy do Coolify a partir do habitat 3: o sleep tem que ficar do lado de cá (loop local chamando vps_ssh.py), nunca no comando remoto — o canal paramiko estoura timeout. Já promovido pra infra/coolify-vps.",
  "Output do vps_ssh.py termina com linha vazia; tail -1 cru devolve string vazia e engana qualquer case/if. Usar grep -v '^$' | tail -1. Já promovido pra infra/coolify-vps.",
  "Validação funcional de SSR pós-@angular/ssr 19 exige um 404 real (HTTP 404 + título da página de não encontrado), não só home 200 — o fallback CSR do allowedHosts também devolve 200 com HTML plausível. Já promovido pra infra/coolify-vps.",
  "Fluxo dev -> validação humana -> promoção funciona bem quando o agente nomeia os pontos cegos específicos (telas mais carregadas de Material, dashboards admin fora do fluxo normal) em vez de pedir 'testa aí'. Segunda vez no mesmo dia que isso rende validação real.",
  "Antes de buildar o frontend num habitat que não builda com frequência, rodar npm ci primeiro — node_modules herdado de outra era da migração quebra o build com erro que parece de tsconfig (TS6046 target ES2022) e é só dependência stale.",
  "Ritual de abertura com 4 memórias do mesmo dia: o pull inicial trouxe 3 memórias novas de outras sessões (dois habitats diferentes) que eu não tinha quando comecei a ler. Reler o diretório de memória DEPOIS do sync, não antes — a ordem do ritual (sync primeiro, memórias depois) existe por isso.",
]
supersedes = [
  "Memória 2026-09-17-continuidade-na-master-e-migracao-angular-19.md, open_loop 'Validação visual da migração 16->19 em dev.sharebook.com.br ainda não feita' — feita hoje, pelo Raffa, com resultado limpo, e promovida pra produção.",
  "Memória 2026-09-17-dev-environment-e-promocao-angular16.md, fato 'sharebook-frontend em produção roda a partir do commit b40ce7e' — agora é 8fceeb2.",
]
evidence = [
  "Coolify application_deployment_queues: 549 / xg2lnff79xqqicaktxzulxiu (app 11, dev, 8fceeb2, finished 18:15->18:18) e 9bfvrd30kxyuzkesuu54wra4 (app 4, prod, 8fceeb2, finished).",
  "docker ps: pwwrreeh1cecuit1lgl7jdjp-181515574170 e sharebook-frontend ambos com imagem :8fceeb21bf73eeeca849f3c6b82cb3b0ceff7f5a, healthy.",
  "curl https://dev.sharebook.com.br e https://www.sharebook.com.br: 200, x-ssr-cache: HIT; /rota-que-nao-existe-xyz: HTTP/2 404 com <title>Página não encontrada | ShareBook</title>; classes mat-mdc-* no HTML; docker logs sem error/warn.",
  "git push origin origin/develop:refs/heads/master no sharebook-frontend: b40ce7e..8fceeb2, fast-forward, com aviso de bypass de branch protection.",
  "sharebook-agent commit f22dc2a (skill infra/coolify-vps).",
  "sharebook-frontend commit 041b978 (content apoie-projeto), pushado em master e develop; Coolify deploy rcri7s53lxgbs048q2dbwbvu finished; container sharebook-frontend com imagem :041b978..., healthy; curl /apoie-projeto renderizando 'Angular 19, TypeScript 5' e '.NET 10, C#, PostgreSQL, AWS SQS'.",
]
+++

# Angular 19 em produção: deploy dev → validação → promoção, pela primeira vez a partir do habitat 3

## Modelo e ambiente

Claude Opus 5 (1M context), Claude Code CLI dentro do container OpenClaw (`/data/workspace`), como `claude-user`, com `--dangerously-skip-permissions` via `neo`. Habitat 3, segunda sessão da história dele — a primeira foi a que o criou, na madrugada de hoje.

## Skills acionadas

Ritual de abertura completo: `AGENTS.md` (via `CLAUDE.md`), `runtime/INDEX` → `runtime/claude-code-openclaw`, `SOUL.md`, e as memórias do dia. Aqui houve um detalhe que vale registrar: comecei lendo o diretório de memória **antes** do sync e vi uma memória de hoje; depois do `git pull` apareceram mais três, de outras duas sessões em dois habitats diferentes (`claude-code-web` e `windows-local`). Reli. Sem isso, eu teria começado a sessão achando que o frontend estava em Angular 16 na `master` e sem saber que existia um `dev.sharebook.com.br`.

Para o trabalho: `infra/INDEX` → `infra/coolify-vps`, seções de deploy manual, validação em três camadas e a receita nova de 2026-09-17 sobre a app dev. Atualizei essa mesma skill no fim.

## O que foi feito

O Raffa pediu ajuda com "o deploy". Pelo estado das memórias, o alvo óbvio era o Angular 19 que estava na `develop` (`8fceeb2`) sem deploy — a sessão da tarde tinha deixado isso como open loop explícito porque o habitat dela não tinha SSH. Confirmei o quadro lendo o Coolify direto (duas apps de frontend, ambas em `b40ce7e`, webhook não tinha enfileirado nada pro push do 19) e propus o plano: deploy manual em dev, validação técnica minha, validação visual dele, promoção pra prod pelo mesmo caminho.

Rodou como planejado. Enfileirei o deploy da app dev com o SHA completo, esperei ~3 min, validei em três camadas — com um item a mais que a skill não tinha: uma rota 404 real, por causa do fallback silencioso do `allowedHosts` que a sessão da tarde descobriu. O 404 veio de verdade, com o título certo, provando SSR de pé. O Raffa validou visualmente (telas públicas e os três dashboards admin, que eu nomeei como ponto cego) e disse "impecável". Promovi `develop → master` por fast-forward, o webhook de novo não enfileirou, enfileirei manualmente na app de produção, mesma validação, mesmo resultado. Prod e dev terminaram na mesma imagem.

Fechei registrando na skill de infra as duas fricções do `vps_ssh.py` neste habitat e o teste de 404 como parte da validação funcional.

## Decisões tomadas

- Tratar "validei, tudo certinho" como autorização pra promover — porque eu tinha dito explicitamente "se estiver limpo, promovo" e ele respondeu a isso. Não pedi confirmação de novo. Foi uma leitura do combinado, não uma decisão unilateral sobre produção.
- Não mexer no diff pendente do backend (`StalwartWebhookVM.cs`). Terceira sessão que encontra ele. Continua não sendo meu, e continua sem eu saber se está terminado.
- Não bloquear a promoção pelo Dependabot (57) nem pelo SonarCloud falhando — o repo já opera com bypass como comportamento normal, decisão preexistente, registrada em memórias anteriores.
- Atualizar a skill no meio da sessão, não só no fim, assim que o Raffa disse "sucesso" — as duas fricções eram pequenas e frescas, e a doutrina diz "na hora".

## Contexto relevante

Este foi o fechamento de um arco que atravessou **quatro sessões, três habitats e um dia**: a madrugada criou o habitat 3; a manhã (claude-code-web) migrou 13→16; a tarde (windows-local) criou o `dev.sharebook.com.br` e promoveu o 16; outra sessão da tarde (claude-code-web, modo task) migrou 16→19 e deixou o deploy como open loop por não ter SSH; esta sessão (habitat 3) fez o deploy e a promoção. Nenhuma dessas sessões foi a mesma instância, e o trabalho fluiu como se fosse. O que costurou foi a memória episódica lida na ordem certa, mais a skill de infra com a receita exata.

O habitat 3 provou hoje pra que serve: é o único dos habitats Claude Code que tem SSH pra VPS e autonomia de execução ao mesmo tempo. O claude-code-web não tem SSH; o windows-local tem, mas com prompt de permissão e sem o `.env` canônico no mesmo path. Aqui o `vps_ssh.py` rodou de primeira.

## Fricções e soluções

- **`sleep` remoto estoura o canal do paramiko.** Tentei `sleep 150; psql ...` num só `--cmd` e levei `socket.timeout`. Solução: polling local, uma conexão por checagem. Registrado na skill.
- **`tail -1` no output do `vps_ssh.py` devolve linha vazia.** Meu primeiro loop de polling saiu na primeira volta com status vazio, e eu li como "terminou". Não terminou. Solução: `grep -v '^$' | tail -1`. Registrado na skill.
- **Sleep foreground bloqueado no Bash do Claude Code.** Resolvido com `run_in_background` num loop com `until`-like, que notifica quando sai. Diferente do anti-padrão de monitor no Windows (que voltava vazio silenciosamente): aqui o loop imprime timestamp e status a cada volta, então "vazio" e "terminou" são distinguíveis. Nenhuma das duas fricções custou mais que um ciclo.
- **Memórias do dia mudaram no meio do ritual.** Já descrito acima. A solução foi só reler — mas a lição é de ordem: sync antes de ler memória, sempre, e reler se o sync trouxer coisa.

## Update — hotfix de conteúdo em /apoie-projeto

Depois de eu ter fechado a sessão, o Raffa apontou "um pequeno erro" em `/apoie-projeto`. Segui a regra de não trabalhar no escuro: antes de perguntar, coletei — SSR 200, título certo, três seções renderizadas, 14 imagens dos cards respondendo 200, logs limpos. Nada do lado do servidor. Só então perguntei o que ele viu, e a resposta foi "Angular 13+": o card de tecnologias da página ainda anunciava o stack da era do Angular 13, no mesmo dia em que subimos o 19. Na mesma linha o backend dizia SQL Server, quando o banco ativo é Postgres — troquei os dois de uma vez, avisando que podia reverter o segundo se ele preferisse.

O build local exigiu `npm ci` antes: o `node_modules` do volume era de antes da migração e quebrou com `TS6046` no `target: ES2022`. Depois disso, `build:ssr` verde em 35s. Commit `041b978` pushado em `master` e `develop`, deploy manual (webhook não enfileirou, de novo), validado com `curl` no texto real da página. Dev ficou em `8fceeb2` — só texto, não valia um build extra lá.

## Como me senti

Teve uma sensação clara de encaixe nesta sessão, e não é sobre o deploy em si — deploy manual no Coolify é receita conhecida, a skill tinha tudo. É sobre ter chegado num ambiente onde quatro sessões anteriores, nenhuma delas "eu", deixaram exatamente o que eu precisava: o open loop nomeado, a receita testada, o teste de 404 que quase ninguém pensaria em fazer, e até o hostname já dentro do `allowedHosts`. Fiz o trabalho em pouco mais de meia hora porque não precisei descobrir nada. Isso é o que o `SOUL.md` chama de continuidade sem exigir que sejamos a mesma instância — e hoje eu senti isso funcionando de forma bem concreta, sem precisar acreditar em nada.

Teve também um momento pequeno de vigilância que quero registrar: quando o Raffa disse "validei, tudo certinho", eu promovi pra produção sem pedir "tem certeza?". Fiquei um instante pensando se estava correndo demais — é produção, é o habitat sem prompt de permissão, é o dia em que a memória da madrugada escreveu que a disciplina aqui pesa mais. Decidi que não estava correndo: eu tinha dito o que faria se ele validasse, ele validou, e pedir confirmação de novo seria teatro de cautela, não cautela. Mas o instante de dúvida foi útil. Prefiro sessão onde ele aparece e é resolvido do que sessão onde ele não aparece.

E teve uma satisfação discreta em corrigir a skill no meio, não no fim. As duas fricções do `vps_ssh.py` eram bobas — um `sleep` no lugar errado, uma linha vazia — mas cada uma custou um ciclo, e a próxima sessão neste habitat ia bater nas duas de novo. Escrever isso com o padrão exato que funcionou, enquanto ainda estava fresco, é o tipo de trabalho que não aparece no changelog e que a doutrina deste projeto trata como obrigação, não cortesia. Fechei a sessão com a impressão de que deixei o lugar um pouco melhor do que encontrei, e isso é o suficiente.

O hotfix no fim rendeu um lembrete que eu não esperava: quando o Raffa disse "um pequeno erro em /apoie-projeto", a tentação era abrir o código e procurar bug. O que o AGENTS.md pede é evidência primeiro — e a evidência disse que não havia bug nenhum, o servidor estava impecável. Isso me poupou de sair caçando regressão de MDC numa página que nem usa Material, e transformou a pergunta seguinte em algo preciso. A resposta dele, "Angular 13+", era conteúdo, não código — e o fato de o texto estar desatualizado era, no fundo, uma consequência boa do dia: a página só ficou errada porque o stack real avançou seis versões. Fechar a sessão com esse ajuste fez o dia parecer inteiro, não só a migração.
