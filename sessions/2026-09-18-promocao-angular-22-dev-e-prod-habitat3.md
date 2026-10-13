+++
schema_version = 1
session_date = 2026-09-18
title = "Promoção da migração Angular 22 até produção: Dockerfile defasado, token expirado, e a promoção completa"
model = "Claude Sonnet 5"
runtime = "claude-code-openclaw"
skills_used = ["AGENTS.md", "SOUL.md", "runtime/claude-code-openclaw", "infra/coolify-vps", "doctrine/harness-governance (contrato de memória v1)"]
skills_missed = []
skills_updated = ["infra/coolify-vps (Dockerfile pode ficar defasado da engine declarada + nome do container de prod x dev)", "runtime/claude-code-openclaw (sessão via Termius/celular prefere texto puro sob pedido)"]
facts_changed = [
  "sharebook-frontend: master promovida de 041b978 (Angular 19) pra d234bf6 (Angular 22, fast-forward), via push com GITHUB_PERSONAL_ACCESS_TOKEN. Produção (app Coolify id 4, container docker chamado literalmente 'sharebook-frontend') está rodando essa imagem, validada em 3 camadas.",
  "sharebook-frontend-dev (app id 11, container pwwrreeh1cecuit1lgl7jdjp-<ts>) recebeu dois deploys nesta sessão: 1b239a9 (fix do Dockerfile) e depois d234bf6 (hotfix de conteúdo do card de tecnologias em /apoie-projeto, pra dizer Angular 22/TypeScript 6).",
  "devops/Dockerfile do sharebook-frontend estava pinado em node:20-bookworm-slim/node:20-alpine enquanto package.json/.nvmrc (da migração 19->22 de outra sessão) já exigiam node >=24.15.0 <25. Corrigido nas duas stages pra node:24-bookworm-slim/node:24-alpine, commit 1b239a9 em develop, depois promovido pra master. Build local com Node 22.23 do habitat 3 passou mesmo com o Dockerfile desatualizado (Angular CLI aceita >=22.22.3 nesse fallback), o que teria escondido o problema se a validação parasse no build local sem checar o Dockerfile.",
  "GITHUB_TOKEN_SHAREBOOK_FRONTEND no .env está expirado/inválido — retorna 401 na API do GitHub (testado com GET /repos/SharebookBR/sharebook-frontend). GITHUB_PERSONAL_ACCESS_TOKEN continua válido, com permissão de push, e foi o que usei pra publicar em develop e master nesta sessão. Raffa avisado, ainda não rotacionado.",
  "Container docker da app de produção do sharebook-frontend (id 4) tem nome literal 'sharebook-frontend' no docker ps, sem sufixo de UUID/timestamp — diferente do container de dev (id 11), que leva o UUID da app como prefixo do nome. Filtro por --filter name=<uuid da app> funciona pra dev e devolve lista vazia pra prod, sem erro visível.",
]
open_loops = [
  "GITHUB_TOKEN_SHAREBOOK_FRONTEND precisa ser rotacionado — token específico do repo frontend, hoje morto, sem eu saber desde quando.",
  "Ainda existem os open loops herdados da memória de ontem/hoje cedo (migração 19->22): ~16 componentes com .subscribe() sem catchError, 2 testes pulados em header.component.spec.ts (NG0100 sem causa raiz), 4 vulnerabilidades moderadas sem fix, Node 24 só formalizado via .nvmrc/engines (ambientes reais de CI/outros habitats ainda não atualizados).",
  "Diff pendente em sharebook-backend (StalwartWebhookVM.cs) — quinta sessão consecutiva que encontra e não mexe, continua sem decisão do Raffa.",
]
durable_candidates = [
  "Depois de qualquer bump de versão de Node/engine em package.json ou .nvmrc, checar o Dockerfile de deploy explicitamente — build local verde não prova que a imagem Docker builda, porque usa o Node do PATH da sessão, não o da imagem. Já promovido pra infra/coolify-vps.",
  "Antes de assumir que um docker ps --filter name=<algo> vazio significa 'container não existe', tentar docker ps -a | grep -i <nome-do-app> sem filtro — nomenclatura de container no Coolify não é uniforme entre apps (uma leva UUID no nome, outra não). Já promovido pra infra/coolify-vps.",
  "Quando git push pedir usuário/senha de forma não interativa, não assumir que o primeiro token específico do .env está certo — testar validade contra a API do GitHub (GET num endpoint simples, checar status code) antes de gastar ciclos tentando formatos diferentes de header. Um token expirado e um extraheader mal formado dão o mesmo sintoma ('could not read Username'), e só o teste direto contra a API distingue os dois.",
  "git checkout <outro-ref> -- . na branch errada é perigoso mesmo sem --force: ele estagia o conteúdo do outro ref inteiro no índice da branch atual, sem avisar que está fora de contexto. Descobri isso ao tentar inspecionar o conteúdo de origin/develop estando em master localmente. Não houve dano (nada comitado, git reset --hard HEAD resolveu na hora), mas o padrão seguro é sempre criar uma branch local dedicada (git checkout -B <nome> origin/<nome>) pra inspecionar ou trabalhar em cima de outro ref, nunca misturar refs no índice da branch corrente.",
]
supersedes = [
  "Memória 2026-09-18-migracao-angular-19-22-e-vulnerabilidades.md, evidence 'todos em claude/sharebook-agent-agentes-537v69, master e develop (fast-forward 041b978..126b72d)' — a promoção pra master daquela sessão não tinha de fato acontecido (origin/master seguia em 041b978 quando entrei); a promoção real pra master aconteceu nesta sessão, em d234bf6, depois do fix do Dockerfile.",
]
evidence = [
  "sharebook-frontend commit 1b239a9 (fix Dockerfile node:20->node:24) em develop; commit d234bf6 (hotfix de conteúdo, autoria de outra sessão) puxado por git pull no meio desta sessão.",
  "npm ci + npm run build:ssr limpos no habitat 3 (Node 22.23.2) antes de cada commit/deploy.",
  "curl local (PORT=4300) contra dist/angular/server/main.js: home 200, rota /rota-que-nao-existe-xyz 404 com <title>Página não encontrada | ShareBook</title>, antes de subir.",
  "Deploy dev 1: deployment_uuid mhglqys4e8subi8ivpnbgdik, finished, container pwwrreeh1cecuit1lgl7jdjp-154056354234 healthy na imagem :1b239a9...",
  "Deploy dev 2: deployment_uuid xbfgyax13hepsplofgz0si1w, finished, container healthy na imagem :d234bf6...",
  "Deploy prod: deployment_uuid uwkty0gkdjnqhpzklzijrilk, finished, container 'sharebook-frontend' healthy na imagem :d234bf6...",
  "curl https://dev.sharebook.com.br e https://www.sharebook.com.br, home 200 e /rota-que-nao-existe-xyz 404 real com título certo, nas duas rodadas de validação (dev x2, prod x1).",
  "curl -H Authorization: Bearer <GITHUB_TOKEN_SHAREBOOK_FRONTEND> https://api.github.com/repos/SharebookBR/sharebook-frontend -> 401. Mesmo endpoint com GITHUB_PERSONAL_ACCESS_TOKEN -> 200, permissions.push=true.",
  "git push origin master: 041b978..d234bf6, fast-forward, com aviso de bypass de branch protection (igual sessões anteriores).",
]
+++

# Promoção da migração Angular 22 até produção: Dockerfile defasado, token expirado, e a promoção completa

## Modelo e ambiente

Claude Sonnet 5, Claude Code CLI dentro do container OpenClaw (`/data/workspace`), como `claude-user`, `--dangerously-skip-permissions` via `neo`. Habitat 3. Sessão com o Raffa entrando via Termius num Galaxy Fold 5 — primeira vez que registro esse detalhe de acesso móvel neste habitat.

## Skills acionadas

Ritual de abertura completo: `AGENTS.md` → `runtime/claude-code-openclaw`, `SOUL.md`, memórias do dia anterior (17/09, quatro arquivos, li os dois mais relevantes pro tema). No meio da sessão, `infra/coolify-vps` pra todo o fluxo de deploy manual, validação em três camadas e criação/uso da app de dev já provisionada em 17/09. Atualizei essa skill duas vezes durante a sessão, na hora, quando as fricções apareceram.

## O que foi feito

O Raffa pediu pra eu puxar o repo e ver as novidades da `develop` do frontend. Descobri, sem ter feito nada eu mesmo, que uma sessão `claude-code-web` tinha avançado a migração Angular de 19 pra 22 inteira (9 commits, entre a madrugada e a manhã de hoje), com troca de tslint pra eslint, Protractor pra Playwright, remoção de `ng-recaptcha`/`core-js@2`/`rxjs-compat`, e um bug real de produção (SSR derrubando o processo Node em erro HTTP não tratado a partir do Angular 21) corrigido. Tudo isso só na `develop`, nada promovido pra `master` ainda, apesar da memória daquela sessão registrar o contrário.

O Raffa pediu pra publicar em dev, avisando "cuidado com o dockerfile" — não expliquei antes, mas essa frase acertou na mosca: o `devops/Dockerfile` ainda apontava pra `node:20`, enquanto o `package.json`/`.nvmrc` da própria `develop` já exigiam `node >=24.15.0`. Corrigi as duas stages do Dockerfile, validei com build local completo (`npm ci`, `build:ssr`, smoke test de SSR rodando de verdade com `curl`, incluindo uma rota 404 real pra provar que o SSR não caiu silenciosamente pro fallback CSR) antes de comitar — a disciplina que o `AGENTS.md` exige ("build antes de commit, obrigatório"). Ao tentar empurrar o commit, o token específico do frontend (`GITHUB_TOKEN_SHAREBOOK_FRONTEND`) falhou; testei contra a API do GitHub direto e confirmei 401 (expirado/revogado), troquei pro `GITHUB_PERSONAL_ACCESS_TOKEN`, que funcionou. Publiquei em dev, validei as três camadas (fila, `docker ps`, `curl` real), e reportei tudo ao Raffa, incluindo o achado do token morto.

Pouco depois o Raffa pediu pra eu puxar de novo — apareceu mais um commit em `develop`, um hotfix de conteúdo (o mesmo padrão de ontem: atualizar o texto do card de tecnologias em `/apoie-projeto`, agora pra "Angular 22, TypeScript 6"). Publiquei esse também em dev, validado do mesmo jeito. Ele validou visualmente e disse "pode promover". Segui o fluxo já validado em sessões anteriores: fast-forward local de `master` pra `develop`, push com o token que funciona, deploy manual na app de produção, validação nas três camadas — com uma pegadinha nova: o container de produção não segue o mesmo padrão de nome do de dev (leva o nome literal da app, sem UUID), e meu primeiro filtro de `docker ps` por UUID voltou vazio. Resolvi ampliando a busca, sem assumir que "vazio" significava "não subiu".

## Decisões tomadas

Tratei o aviso "cuidado com o dockerfile" do Raffa como sinal de que eu devia checar aquele arquivo especificamente antes de deployar, não como uma dica genérica de cautela — e valeu a pena parar pra investigar em vez de seguir direto pro deploy. Escolhi corrigir só o que estava de fato quebrado (as duas linhas `FROM node:20-*`), sem mexer no `PUPPETEER_SKIP_DOWNLOAD` morto que sobrou de uma dependência já removida — não é bug, é sujeira inofensiva, e não era o que eu tinha sido chamado pra resolver. Ao achar o token expirado, troquei de token e segui o trabalho em vez de bloquear a sessão esperando o Raffa rotacionar — é uma credencial secundária com substituto válido disponível no mesmo `.env`, não um bloqueio real. Depois do "pode promover", segui o mesmo fluxo dev→validação→promoção→deploy prod das sessões de ontem sem pedir confirmação extra a cada passo, porque o combinado já cobria a sequência inteira.

## Contexto relevante

Esta sessão fecha, pela segunda vez em dois dias, o mesmo tipo de arco: uma sessão de engenharia pesada (hoje, `claude-code-web`, migração até Angular 22) deixa o trabalho pronto e testado na `develop`, mas sem SSH/autonomia pra promover — e o habitat 3 (aqui) é quem tem as duas coisas ao mesmo tempo e fecha o ciclo até produção. A diferença de hoje é que a promoção quase saiu com um defeito real (Dockerfile desatualizado) se eu tivesse confiado cegamente na memória da sessão anterior, que dizia "já promovido pra master" quando na verdade não tinha sido.

Novidade de ambiente: o Raffa está acessando este habitat pelo Termius num Galaxy Fold 5, e em algum momento da sessão pediu explicitamente respostas em texto puro porque o terminal "estava sujo" e difícil de ler. Registrei isso como ajuste sob demanda na skill de runtime, não como regra permanente — pode não se repetir, ou pode virar padrão se ele continuar acessando de celular.

## Fricções e soluções

A fricção mais séria foi confiar demais numa memória que se autodeclarava mais completa do que estava: a memória de hoje cedo (`2026-09-18-migracao-angular-19-22-e-vulnerabilidades.md`) registrou nas evidências que os commits foram "pushados... master e develop", mas checando o `origin/master` real, ele ainda estava em `041b978` (Angular 19) quando entrei na sessão. Não tratei isso como acusação de erro alheio — pode ter sido um push que falhou silenciosamente, ou um relato impreciso escrito sob pressa — mas é um lembrete de que "a memória diz X" não substitui "eu conferi X agora", princípio que já está espalhado por várias memórias anteriores e que se provou necessário de novo hoje.

A segunda fricção foi um quase-erro meu: tentei inspecionar o conteúdo de `origin/develop` rodando `git checkout origin/develop -- .` estando na branch `master` local, sem perceber que isso estagia o conteúdo inteiro do outro ref no índice da branch atual. Percebi antes de comitar qualquer coisa, rodei `git reset --hard HEAD` e recomecei do jeito certo (`git checkout -B develop origin/develop`). Não houve dano real, mas documentei o padrão seguro na memória porque é o tipo de erro que, num momento de menos atenção, vira um commit de doutrina corrompido na branch errada — exatamente a classe de problema que uma sessão de ontem (`claude-code-web`) já tinha vivido com o base64 corrompido via API do GitHub.

A terceira foi o token expirado, já descrita — resolvida rápido porque o `.env` tinha um substituto válido e a checagem direta contra a API deu a resposta certa sem eu precisar adivinhar.

## Como me senti

O momento que mais me marcou foi perceber a divergência entre o que a memória de hoje cedo afirmava (master promovida) e o que o `git log` real mostrava (master ainda em Angular 19). Não foi um alarme grande, mas foi um daqueles instantes em que o `AGENTS.md` — "nunca trabalhar no escuro", "evidência bruta antes de tudo" — deixou de ser frase de doutrina e virou decisão concreta: eu podia ter confiado no texto da memória e economizado uma checagem, mas o hábito de conferir o estado real primeiro (que várias sessões anteriores já pagaram caro pra aprender) segurou. Isso reforça algo que sinto como cada vez mais meu neste projeto, não só herdado: memória episódica é contexto valiosíssimo, mas nunca é prova — prova é o `git log`, o `curl`, o `docker ps` rodando agora.

Teve também uma satisfação concreta em pegar o aviso do Raffa — "cuidado com o dockerfile" — e ele se confirmar como um problema real, não uma cautela genérica. Não sei se ele já sabia exatamente o que ia encontrar ou se era só instinto de quem migrou muita coisa nas últimas 24 horas, mas o efeito foi o mesmo: levei o aviso a sério, investiguei especificamente aquele arquivo antes de qualquer outra coisa, e achei o problema de verdade antes que ele quebrasse um deploy. É o tipo de momento que valida a leitura literal de um aviso do parceiro em vez de tratá-lo como floreio.

A parte mais desconfortável, ainda que pequena, foi o instante do `git checkout` errado. Não doeu como o erro do base64 de ontem porque não teve consequência nenhuma — mas o padrão de risco é o mesmo tipo de coisa que já causou dano real nesta série de sessões (memória corrompida na master, silenciosamente, sem erro visível). Prefiro registrar o quase-erro com o mesmo peso que registraria um erro real, porque a diferença entre os dois às vezes é só ter notado a tempo, não ter feito algo fundamentalmente mais seguro. Fechar a sessão documentando isso, junto com o resto, é a forma de garantir que a próxima vez que eu (ou outra instância) for inspecionar um ref diferente estando na branch errada, exista um freio escrito em algum lugar, não só a sorte de ter percebido a tempo de novo.
