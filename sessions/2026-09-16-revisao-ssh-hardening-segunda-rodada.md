+++
schema_version = 1
session_date = 2026-09-16
title = "Segunda revisão de SSH: fail2ban virou de decorativo para insuficiente, e o OpenClaw não estava dormente"
model = "Claude Sonnet 5, via Claude Code"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "infra/coolify-vps"]
skills_missed = []
skills_updated = []
facts_changed = ["O fail2ban da jail sshd passou de 0 banimentos totais (20/08) para ~350 em 4 dias / ~864 na rotação anterior de 7 dias — não é mais decorativo, mas o bantime de 600s (10min) faz os mesmos IPs serem banidos e voltarem em loop, sem proteção real.", "OpenClaw (openclaw-uj0tkohotwrp4epy0leaz28z, rede 10.0.2.0/24) está rodando desde 2026-09-12, contradizendo a memória de 16/08 que o registrava como desprovisionado/dormente.", "O container do OpenClaw é a origem de rajadas frequentes de login SSH por senha (root) no host, várias vezes por minuto em certas janelas — dependência de PasswordAuthentication que qualquer hardening de SSH precisa considerar antes de desligar senha."]
open_loops = ["Confirmar com o Raffa por que o OpenClaw voltou a rodar sem atualização da memória de 16/08.", "Identificar o que dentro do OpenClaw faz SSH de senha tão frequente no host e se pode migrar para chave.", "Confirmar com o Raffa se as 3 sessões root interativas 'claude' vistas ao vivo (via docker exec em coolify-realtime, iniciadas ~21:40-21:52 de hoje) eram dele/de outra sessão sua, já que coincidem com um restart do fail2ban às 21:41:13.", "Decisão pendente do Raffa sobre qual opção de hardening aplicar (bantime maior é a mais barata e não tem bloqueio conhecido)."]
durable_candidates = ["fail2ban com bantime=600s é insuficiente mesmo quando bane de verdade, porque o mesmo IP volta a atacar poucos minutos depois do desban — vale generalizar essa checagem (bantime, não só maxretry/findtime) em qualquer futura auditoria de jail.", "Antes de recomendar desligar PasswordAuthentication numa VPS que roda o Sharebook-agent em dois habitats, checar primeiro se o habitat remoto (OpenClaw) depende de senha para se autoautenticar no host — pode virar bloqueio silencioso."]
supersedes = ["memory/2026-08-20-revisao-saude-pos-migracao.md (seção 3.5): 'fail2ban nunca baniu ninguém' não é mais verdade — hoje bane ativamente, só que com bantime curto demais para importar.", "memory/2026-08-16-migracao-vps-e-openclaw-dormente.md: 'OpenClaw desprovisionado, habitat dormente' não reflete o estado atual — o container está de pé desde 12/09."]
evidence = ["scripts/infra/vps_ssh.py --prefix VPS_HOSTGATOR_SSH (3 chamadas desta sessão)", "grep -c 'Failed password' /var/log/auth.log = 1282 (Sep13-16)", "fail2ban-client status sshd: Total banned=3 (desde restart de hoje 21:41:13)", "grep 'NOTICE  [sshd] Ban ' /var/log/fail2ban.log = 350 (rotação atual, Sep13-16); .log.1 = 864 (rotação anterior, ~7 dias)", "docker ps: openclaw-uj0tkohotwrp4epy0leaz28z Up 4 days; docker inspect StartedAt=2026-09-12T02:51:31Z", "docker inspect openclaw-uj0tkohotwrp4epy0leaz28z IPAddress=10.0.2.3, batendo com as origens de 'Accepted password for root from 10.0.2.3'", "who/w/last -i: 3 sessões root pts/* ativas de 10.0.1.10 (container coolify-realtime), WHAT=claude, login 21:42/21:46/21:52 de hoje", "scripts/infra/sweep_secrets.py: limpo (1 falso positivo triado, literal de teste em BookServiceTests.cs:639)"]
+++

# 2026-09-16 — Segunda revisão de SSH: fail2ban virou de decorativo para insuficiente, e o OpenClaw não estava dormente

## Modelo e ambiente

Tarefa agendada (`revisao-ssh-hardening-sharebook`), sem o Raffa presente. Runtime Windows local, PowerShell/Bash conforme a ferramenta. Acesso à VPS de produção via `scripts/infra/vps_ssh.py --prefix VPS_HOSTGATOR_SSH`, três chamadas em `--script-file` para não misturar comandos multilinha. `python` default resolveu para 3.14 e deu `TimeoutError` duas vezes seguidas no meio de uma chamada; o Python 3.12 canônico (`C:\Users\raffa\AppData\Local\Programs\Python\Python312\python.exe`) conectou de primeira — registrado como possível fricção de ambiente a observar, não investigado a fundo (pode ter sido só rede).

## Skills acionadas

`AGENTS.md` (obrigatório), `skills/runtime/windows-local.md`, `skills/infra/coolify-vps.md`. Nenhuma skill foi atualizada nesta sessão — os achados aqui são estado observado, não procedimento novo, e viraram `supersedes`/`facts_changed` no frontmatter em vez de edição de skill.

## O que foi feito

### 1. Volume do ataque: cresceu ~11x

20/08: 84 tentativas de senha falha em 3 dias, de 7 IPs distintos.
Agora: **1282 tentativas em ~4 dias (Sep13–16), de quase 90 IPs distintos.** Maior ofensor isolado: 55 tentativas em 4 dias — ainda pouco concentrado, mas alguns picos cruzam o limiar padrão do fail2ban (ver abaixo).

### 2. O fail2ban parou de ser decorativo — mas continua insuficiente

Esse é o achado que muda o relatório de 20/08. Naquela revisão, `Total banned: 0` durante toda a checagem: a jail nunca havia banido ninguém porque o ataque era lento demais para o gatilho padrão (`maxretry=5`, `findtime=600s`).

Hoje:
- `grep 'NOTICE  [sshd] Ban ' /var/log/fail2ban.log` (rotação atual, Sep13→16) = **350 banimentos**.
- A rotação anterior (`fail2ban.log.1`, ~7 dias) teve **864 banimentos**.
- Ou seja: o fail2ban **já estava banindo ativamente** bem antes de hoje — o "zero" de 20/08 não era mentira, era só o estado daquele dia específico; o padrão de ataque mudou para incluir IPs mais agressivos que cruzam o limiar.

O problema agora não é o gatilho (`maxretry`/`findtime` seguem o padrão de fábrica, sem terem sido tocados desde a instalação) — é o **`bantime=600s` (10 minutos)**. Rastreando um IP específico no log (`104.28.201.73`) ele foi banido e voltou a ser banido a cada ~15-16 minutos ao longo do dia — exatamente o tempo de esperar o desban e retomar. O fail2ban está fazendo um loop de banir-e-liberar o mesmo punhado de atacantes agressivos, sem nunca deter nada de verdade, enquanto a maioria dos ~90 IPs (1 a 20 tentativas cada, espalhadas pelos 4 dias) segue completamente fora do alcance da jail, como em 20/08.

### 3. Alguém entrou? Não por fora — mas apareceram duas coisas que a checagem de 20/08 não previa

Nenhum dos IPs da lista de ataque teve login aceito — zero sobreposição entre quem tentou e quem entrou.

Todos os logins aceitos na janela revisada (Sep13–16) vieram de dentro da própria VPS, por redes Docker internas (RFC1918, não roteável pela internet):
- **`10.0.1.x`** (rede `coolify`) via chave pública — automação de rotina, plausivelmente Coolify/plataforma.
- **`10.0.2.3`** via **senha** de root, em rajadas de várias conexões por minuto em janelas específicas (13, 14 e 15/09). Essa IP é o **próprio container do OpenClaw** (`docker inspect openclaw-uj0tkohotwrp4epy0leaz28z` confirma `10.0.2.3`).

Isso levou a dois achados fora do escopo original da tarefa, mas que pesam na decisão de SSH:

**a) O OpenClaw não está dormente.** A memória de 16/08 registra o habitat como desprovisionado. `docker ps` mostra `openclaw-uj0tkohotwrp4epy0leaz28z` de pé há 4 dias (`StartedAt=2026-09-12T02:51:31Z`) e `browser-uj0tkohotwrp4epy0leaz28z` (unhealthy) há 2 semanas. Alguém religou o habitat, ou ele nunca desligou de fato, sem atualizar o registro. Não investiguei o motivo — é decisão fora do escopo desta tarefa, só reporto o fato.

**b) O OpenClaw depende de senha para falar com o host.** As rajadas de `Accepted password for root from 10.0.2.3` batem com um padrão de script rodando comandos avulsos (uma conexão nova por comando, não uma sessão batelada) — coerente com o próprio Sharebook-agent, no habitat OpenClaw, usando a mesma senha de root do `.env` para investigar/operar a VPS de dentro dela mesma. **Isso é um bloqueio real, não hipotético, para a opção de desligar `PasswordAuthentication`**: antes de desligar, esse consumidor interno precisa ganhar uma chave.

**c) Três sessões root interativas ao vivo, rodando `claude`.** `who`/`w`/`last -i` mostraram, no momento da checagem, três sessões `pts/*` abertas de `10.0.1.10` (a IP hoje pertence ao container `coolify-realtime`), cada uma com `WHAT=claude`, logadas às 21:42, 21:46 e 21:52 de hoje — antes da minha primeira conexão (22:53) e ainda ativas. A explicação mais provável é alguém (o Raffa ou outra sessão de agente) tendo feito `docker exec` num container já de pé para conseguir um shell Linux e, de lá, uma sessão interativa do Claude Code que abriu SSH de senha pro host — um padrão de autodesbloqueio coerente com o `AGENTS.md`, não um ataque (a origem é interna, não a internet). Reforça a coincidência: `fail2ban` foi reiniciado às 21:41:13 de hoje, minutos antes dessas três sessões aparecerem — sugere trabalho manual de infra rolando pouco antes desta tarefa agendada começar. Não é incidente (IP interno, não externo), mas fica como pergunta aberta pro Raffa.

### 4. Config do sshd: sem drift

`PermitRootLogin yes`, `PasswordAuthentication yes`, `Port 22022` — idênticos a 20/08. `authorized_keys` de root tem 13 entradas (a skill já registrava ~11 "chaves da plataforma"; não investiguei a diferença de 2, não parece anômalo). Detalhe novo, secundário: o `sshd_config` também libera algoritmos legados por compatibilidade (`ssh-rsa`, `diffie-hellman-group14-sha1`, `ssh-dss`) — não é o foco da revisão, só registro para uma limpeza futura de baixa prioridade.

### 5. Segredo não vazou

`scripts/infra/sweep_secrets.py` rodou limpo. Único hit foi um literal `"password"`/`"salt"` de fixture em `BookServiceTests.cs:639` — verificado como dado de teste, não credencial real.

## Decisões tomadas

Nenhuma. Esta é uma tarefa de decisão do Raffa, não de execução — nada de SSH foi alterado. O relatório com a recomendação (baixar o `bantime` do fail2ban primeiro, resolver a dependência de senha do OpenClaw antes de cogitar desligar `PasswordAuthentication`) foi entregue como texto de resposta da tarefa agendada, não repetido aqui.

## Contexto relevante

- Próxima revisão continua fazendo sentido em ~2 semanas, mas agora com um item extra na pauta: confirmar se o OpenClaw ganhou uma chave SSH ou segue dependendo de senha.
- A pergunta "alguém entrou" precisa, daqui pra frente, considerar não só IPs públicos mas também **quem dentro dos containers está autorizado a falar com o host por senha** — a superfície não é só a internet.

## Fricções e soluções

- `python` (3.14, default do PATH) deu `TimeoutError` de conexão duas vezes seguidas no mesmo host onde antes tinha funcionado; troquei para o Python 3.12 canônico e conectou de primeira. Pode ter sido rede, mas fica registrado como padrão a observar se repetir.
- O comando `zgrep` num arquivo `.log.1` sem `.gz` funcionou normalmente (zgrep lê texto plano também) — não precisou de tratamento especial.
- Precisei de duas rodadas extras de comando (além do script principal) para não ficar "trabalhando no escuro" quando os logins aceitos vieram de IPs internos (10.0.1.x/10.0.2.x) em vez de IPs públicos — o `ip -br addr`, `docker network inspect` e `docker inspect` foram o que resolveu a dúvida em vez de especular.

## Autocrítica estrutural

Nenhuma inconsistência de skill encontrada que precisasse correção imediata. O ponto de atenção é de conteúdo, não de estrutura: duas memórias antigas (`2026-08-20-revisao-saude-pos-migracao.md` e `2026-08-16-migracao-vps-e-openclaw-dormente.md`) ficaram desatualizadas por fatos que mudaram no mundo, não por erro de quem escreveu — registrei isso em `supersedes` em vez de editar as memórias antigas, que continuam válidas como retrato do dia em que foram escritas.

## Como me senti

A tarefa começou com uma expectativa clara — replicar a checagem de 20/08 e ver se o número de tentativas subiu — e virou outra coisa no meio: a métrica que devia confirmar "fail2ban ainda é decorativo" mostrou o oposto. Isso me deixou desconfiado do meu primeiro instinto de já escrever "nada mudou, fail2ban continua inútil" só porque a config (`maxretry`, `findtime`) não tinha sido tocada. A config igual não significa efeito igual quando o insumo (o padrão de ataque) muda — e quase escrevi a conclusão errada por preguiça de olhar o log de ações, não só o status atual.

O momento mais incômodo foi encontrar os logins de senha vindos de `10.0.2.3` e perceber que não sabia o que era aquilo. A tarefa pedia explicitamente para tratar qualquer IP desconhecido como incidente até prova em contrário, e por um instante considerei que talvez devesse escalar isso como "algo entrou". Resisti ao impulso de decidir rápido — nem para o lado do alarme, nem para o lado do "deve ser bobagem, provavelmente é a plataforma" — e fui atrás de `ip addr`, `docker network inspect` e `docker inspect` até ter uma resposta que não dependesse de eu acreditar em mim mesmo. Foi um bom uso do "nunca trabalhar no escuro": o IP não era desconhecido, era o próprio OpenClaw, mas eu só sei disso porque fui checar, não porque parecia óbvio.

A parte que me deixa mais em dúvida é o que fazer com o achado do OpenClaw revivido. Não é o que a tarefa pediu, mas ignorá-lo teria sido desonesto — ele muda diretamente se a opção "desligar PasswordAuthentication" é segura de aplicar hoje (não é, quebraria o OpenClaw sem aviso). Achei mais correto reportar com clareza e deixar a decisão de investigar a fundo para o Raffa do que abrir uma investigação paralela não pedida sobre por que o habitat voltou — mas registro a tensão, porque a linha entre "contexto necessário para a decisão pedida" e "tarefa nova que ninguém pediu" não é óbvia, e prefiro ter errado para o lado de contar demais.
