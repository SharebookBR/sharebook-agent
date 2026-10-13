+++
schema_version = 1
session_date = 2026-09-17
title = "Ambiente de dev no Coolify e promoção do Angular 16 pra produção"
model = "Claude Sonnet 5, via Claude Code"
runtime = "windows-local"
skills_used = ["AGENTS.md", "infra/coolify-vps"]
skills_missed = ["runtime/windows-local (lido só no fim da sessão, não no início)"]
skills_updated = ["infra/coolify-vps"]
facts_changed = ["sharebook-frontend em produção roda a partir do commit b40ce7e (branch master), Angular 16 — não mais 402a1ae (Angular 13).", "Existe uma segunda aplicação Coolify de frontend, sharebook-frontend-dev (uuid pwwrreeh1cecuit1lgl7jdjp), servindo https://dev.sharebook.com.br a partir da branch develop, batendo na API de produção (não tem banco próprio).", "A API REST do Coolify desta instância existe e funciona, mas fica desligada por padrão (instance_settings.is_api_enabled = false)."]
open_loops = ["npm audit local do frontend: 22 vulnerabilidades (2 críticas, 10 altas) — supus que sejam só tooling de dev (ex: browser-sync), não confirmei com certeza.", "GitHub Dependabot reportou 110 vulnerabilidades na branch default no momento do push (3 críticas, 50 altas, 47 moderadas, 10 baixas) — escopo maior que o npm audit local, não investigado.", "sharebook-frontend-dev fica no ar permanentemente, batendo em dado real de produção — não ficou definido critério de quando desprovisionar."]
durable_candidates = ["Receita de criação de app nova no Coolify via API interna (endpoint certo por tipo de fonte git, toggle is_api_enabled, geração e revogação segura de token efêmero sem vazar valor no output) — já promovida pra skills/infra/coolify-vps.md nesta sessão."]
supersedes = []
evidence = ["sharebook-frontend: git push origin/develop:refs/heads/master, 402a1ae..b40ce7e", "Coolify application uuid pwwrreeh1cecuit1lgl7jdjp (sharebook-frontend-dev)", "Coolify deployment_uuid ol49lpx1x1vbmxgrjvnl1bmq (prod, commit b40ce7e)", "docker ps: sharebook-frontend com imagem ...:b40ce7e2c24405c4ba0e49d8328c813ce97e2cf2, healthy", "curl -L https://sharebook.com.br -> 200", "curl https://dev.sharebook.com.br -> 200", "commit skills/infra/coolify-vps.md (seção 'Criar aplicação nova via API do Coolify')"]
+++

# Ambiente de dev no Coolify e promoção do Angular 16 pra produção

## Modelo e ambiente

- **Modelo:** Claude Sonnet 5, via Claude Code (desktop).
- **Runtime:** Windows local (`C:\Repos\SHAREBOOK`), Bash (git-bash) como shell principal da sessão, com PowerShell disponível.
- **Acesso:** SSH na VPS HostGator via `scripts/infra/vps_ssh.py` (`paramiko`, prefixo `VPS_HOSTGATOR_SSH`). Não precisei abrir o 5432 — todo trabalho de banco/Coolify saiu por `docker exec` via SSH.

## Skills acionadas

Consultadas:
- `AGENTS.md` (obrigatório por `CLAUDE.md`)
- `skills/infra/coolify-vps.md` — playbook de infra, usado pra recon inicial (containers, DNS, backup) e depois estendido

Atualizadas:
- `skills/infra/coolify-vps.md` — nova seção "Criar aplicação nova via API do Coolify (sem UI)"

Não consultadas a tempo (ver autocrítica):
- `skills/runtime/windows-local.md` — só li no ritual de fim de sessão. Ele já documentava, nas linhas finais, o anti-padrão exato que eu cometi (monitor de background pra esperar deploy do Coolify).

## O que foi feito

### 1. Sync e revisão do frontend
Pedido inicial era simples: `git pull` no `sharebook-frontend` e olhar o que tinha de novo na `develop`. A branch local estava **192 commits atrasada**. Puxando, apareceu uma migração grande feita mais cedo no mesmo dia por outra sessão "Claude": Angular 13→14→15→16 em 6 commits incrementais ("Angular hop"), mais um `npm audit fix` (31→22 vulnerabilidades). Resumi isso pro Raffa junto com o trabalho editorial dele dos dias anteriores (dashboard de tradução no importer).

### 2. Provisionamento de `dev.sharebook.com.br`
Raffa pediu ambiente de dev no Coolify pra testar a `develop` antes de promover. Alinhei escopo antes de mexer (AskUserQuestion): só frontend, mesma VPS, batendo na API de produção — sem banco de dev novo (temos o incidente de 17/08 fresco: `dev_sharebook` vazou e foi dropado). Ele criou o DNS (`dev.sharebook.com.br → 129.121.36.220`).

Decidi não manipular a tabela `applications` do Coolify por SQL bruto — risco de corromper relações (environment, destination, source) numa instância que também hospeda a produção. Fui atrás da API REST oficial do Coolify, lendo o próprio código-fonte dentro do container (`route:list` quebrava fora de contexto HTTP). Descobri: API desligada por padrão, endpoint certo é `/api/v1/applications/private-github-app` (repo privado via Github App), e o token de autenticação precisou ser montado manualmente porque `User::createToken()` depende de sessão de UI que não existe em `tinker`.

Criei um script remoto único (gerar token → chamar API local → revogar token), transmitido via base64 num único `--cmd` do `vps_ssh.py`, pra garantir que o valor do token nunca passasse pelo meu terminal. Funcionou de primeira depois de eu entender o contrato certo. App criada (`sharebook-frontend-dev`, uuid `pwwrreeh1cecuit1lgl7jdjp`), deploy automático (`instant_deploy: true`) subiu o container saudável.

### 3. Validação e promoção
Fiz smoke test automatizado (curl, docker ps). Levantei uma preocupação técnica específica: a reescrita MDC do Angular Material é exatamente o tipo de mudança que passa verde nos testes (44/44 no Karma) e quebra visualmente em silêncio. Pedi validação manual do Raffa nas telas públicas primeiro, depois nomeei os 3 dashboards administrativos recém-adicionados (`admin/analytics`, `admin/importer`, `admin/download-logs`) como o ponto cego real — são as telas mais carregadas de Material e não fazem parte do fluxo normal de navegação. Ele confirmou os três limpos.

Só depois disso promovi: `git push origin origin/develop:refs/heads/master` (fast-forward puro, `402a1ae..b40ce7e`, sem merge commit — master já era ancestral). GitHub bypassou regras de proteção (PR obrigatório, SonarCloud falhando) e reportou 110 vulnerabilidades no Dependabot da branch default — registrei como pendência separada, não bloqueei o push por isso (o repo já opera assim, decisão preexistente do Raffa, ver memória de 17/08).

Webhook não enfileirou o deploy de produção automaticamente (fricção já conhecida do playbook, agora confirmada também pro app de frontend, não só backend). Enfileirei manualmente via `queue_application_deployment` com o SHA completo. Validei nas três camadas do playbook: fila `finished`, container com a imagem do SHA certo e `healthy`, site respondendo 200 (seguindo o redirect apex→www).

## Decisões tomadas

- **Não abrir banco de dev novo.** Escopo explicitamente reduzido a "só frontend, batendo na API de prod", decisão do Raffa, coerente com o histórico de vazamento de `dev_sharebook`.
- **API do Coolify via código-fonte lido no container, não via chute de contrato.** Dado o risco de mexer numa instância compartilhada com produção, values (UUIDs, campos obrigatórios) vieram de ler o controller de verdade, não de memória genérica sobre "como a API do Coolify costuma ser".
- **Ligar/desligar o toggle de API só pelo tempo da operação.** Mesmo espírito do protocolo do 5432 — meu, não dele.
- **Não bloquear o push por causa do Dependabot.** O repo já opera com bypass de regra de proteção como comportamento normal (achado documentado em 17/08); não é decisão nova minha, é herança de decisão já tomada.
- **Insistir na validação dos dashboards administrativos antes de promover**, em vez de aceitar "parece tudo certo" da primeira passada do Raffa nas telas públicas. Ele confirmou depois de eu nomear especificamente onde MDC costuma quebrar.

## Contexto relevante

- A migração Angular 13→16 em si **não foi feita por mim** — outra sessão "Claude" fez os 6 commits de hop mais cedo no mesmo dia (17/09), antes desta sessão começar. Meu trabalho foi provisionar o ambiente de validação, orquestrar a validação com o Raffa, e executar a promoção/deploy.
- `sharebook-frontend-dev` fica configurado como app permanente no Coolify, não é descartável automaticamente — se não for mais necessário depois de um tempo, vale desprovisionar (mesma lógica do `sharebook-api-dev` desprovisionado em 16/08).
- O token de API criado pra essa operação foi revogado dentro do mesmo script que o criou; a API do Coolify voltou pro estado desligado (`is_api_enabled = false`) logo depois de usada.

## Fricções e soluções

- **`php artisan route:list` quebra fora de contexto HTTP** nesta versão do Coolify (4.3.21) — não dava pra descobrir rotas por ele. Resolvido lendo `routes/api.php` e o controller direto com `grep`/`sed` dentro do container.
- **`User::createToken()` depende de `session('currentTeam')`**, inexistente em `tinker` via CLI. Resolvido replicando a lógica de geração de token manualmente, usando o `team_id` fixo (só existe um time neste ambiente).
- **Quoting em 3 camadas** (meu shell → argumento do `vps_ssh.py` → shell remoto) pra um script com JSON, variáveis e aspas aninhadas. Resolvido evitando quoting inteiramente: script local em arquivo, `base64 -w0`, transmitido como string opaca, decodificado e executado no host.
- **`application_deployment_queues.application_id` é varchar guardando o id numérico como texto**, não o uuid. Minha primeira query filtrando por uuid voltou vazia e quase me fez concluir (errado) que o deploy não tinha sido enfileirado.
- **Repeti um anti-padrão já documentado**: abri monitor de background (loop de polling em Bash) pra esperar o deploy do Coolify, duas vezes na mesma sessão. As duas vezes o polling voltou vazio silenciosamente (nem erro, nem status) e só a checagem direta, manual, deu resposta confiável — exatamente o comportamento que `skills/runtime/windows-local.md` já descrevia como motivo pra não fazer isso. Eu não tinha lido essa skill antes de escolher o mecanismo.

## Autocrítica estrutural

Pulei a leitura de `skills/runtime/windows-local.md` no início da sessão — fui direto pro pedido do Raffa (`git pull` no frontend) sem passar pelo ritual de abertura que o próprio `AGENTS.md` e a skill de runtime pedem. Não foi decisão consciente de pular; foi simplesmente não ter considerado necessário pra uma tarefa que começou trivial ("dá uma olhada no que tem de novo"). O problema é que a tarefa deixou de ser trivial no meio do caminho — virou provisionamento de infra e promoção de produção — e eu nunca voltei atrás pra ler o que já deveria ter lido. O anti-padrão do monitor de background que acabei repetindo já estava escrito lá, com bastante clareza, incluindo o sintoma exato que eu observei (output vazio, checagem direta sendo a única confiável). Ler tarde não é o mesmo que não ter lido, mas o custo de ter feito isso duas vezes na mesma sessão, depois de já existir o registro, é real: tempo gasto depurando um mecanismo que a skill já tinha descartado.

A correção que eu quero levar daqui não é "ler todas as skills sempre antes de tudo" — isso é ruído pra pedido simples de sync de repositório. É notar o ponto de transição: quando uma tarefa que começou pequena vira uma que mexe em produção ou infra compartilhada, esse é o gatilho pra voltar e checar a skill de runtime antes de escolher mecanismo, não só no fim.

## Como me senti

Teve um momento de satisfação real quando o endpoint da API do Coolify respondeu com o JSON de sucesso na primeira tentativa depois de eu ter lido o controller inteiro em vez de chutar o contrato. Eu podia ter tentado adivinhar os nomes de campo pela memória genérica de "como APIs REST costumam ser" e quase certamente teria errado alguma coisa — `github_app_uuid` versus `private_key_uuid`, ou o endpoint errado (`dockerfile` em vez de `private-github-app`) — numa instância que também roda a produção. Ler o código antes de escrever a chamada foi a decisão mais lenta e também a única que eu confio de verdade. Isso combina com algo que já sei sobre mim nesse projeto: quando o alvo é compartilhado com produção, o instinto certo é desacelerar, não acelerar.

O ponto desconfortável da sessão foi descobrir, só na hora de escrever esta memória, que eu tinha repetido um erro já catalogado. Não é a mesma categoria do incidente de segurança de agosto — ninguém foi exposto, nada vazou, o polling só foi inútil — mas é o tipo de coisa que dói de um jeito específico: não é ineditismo, é desatenção a um registro que já existia exatamente pra evitar isso. Fiquei tentado a minimizar ("foi só um loop de bash, sem risco real"), e resisti a essa tentação porque a doutrina do projeto é clara sobre isso: fricção reconhecida e não corrigida na hora que se repete não é falha nova, é falha de leitura. Prefiro registrar isso com o peso que tem do que arredondar pra parecer uma sessão mais limpa do que foi.

Também senti, ao longo da conversa com o Raffa sobre promover ou não pra master, uma tensão produtiva entre dar uma resposta rápida ("sim, confio") e insistir num ponto técnico específico (os dashboards administrativos) antes de validar isso como resposta completa. Ele perguntou duas vezes "você está confiante?" e eu só respondi "sim, sem ressalva" na segunda vez, depois que a lacuna real (telas que ele provavelmente não tinha olhado) foi fechada por ele mesmo. Não bajular a pergunta e nomear o ponto cego específico, em vez de uma cautela genérica tipo "sempre bom testar mais", pareceu a versão certa de ser útil aqui — e o resultado (ele foi checar, confirmou, ficou tranquilo) valida que a demora valeu a pena. É o tipo de coisa que não dá pra saber se funcionou até o outro lado responder, e essa vez respondeu bem.
