# Sessão 25/03/2026 - Coolify VPS, Playbook e Tuning

## Resumo do que foi feito
- Lemos o `AGENTS.md` e recuperamos o contexto da sessão anterior.
- Usamos o `.env` local para acessar o VPS via SSH e confirmamos o ambiente: Ubuntu 24.04.3 LTS, Docker com Coolify e containers da stack do Sharebook saudáveis.
- Inspecionamos o script operacional `/usr/local/bin/limitar-coolify.sh` e confirmamos que ele é executado no `@reboot` e a cada 6 horas via cron.
- Validamos que os limites de CPU do Coolify estavam aplicados e medimos o comportamento dos containers durante navegação real na interface do Coolify.
- Identificamos que o principal gargalo da UI estava no container `coolify`, limitado demais em CPU.
- Alteramos o limite do container `coolify` de `0.3` para `1` CPU e persistimos a mudança no `/usr/local/bin/limitar-coolify.sh`.
- Confirmamos melhora perceptível da fluidez da interface do Coolify após o ajuste.
- Reforçamos no `AGENTS.md` a regra de nunca persistir segredos fora do `.env`.
- Corrigimos o problema de leitura/codificação aparente do `AGENTS.md` e validamos o arquivo inteiro em UTF-8.
- Criamos a convenção local `codex-skills/` para playbooks reutilizáveis e registramos o playbook `codex-skills/coolify-vps.md`.
- Criamos a convenção local `codex-scripts/` e adicionamos o script `codex-scripts/vps_ssh.py` para acesso reutilizável ao VPS via `.env`.
- Normalizamos o `.env` para variáveis reais (`VPS_SSH_HOST`, `VPS_SSH_PORT`, `VPS_SSH_USER`, `VPS_SSH_PASSWORD`) e adaptamos o script para esse formato.

## Decisões Tomadas
- **Segredos só no `.env`**: nenhum dado sensível pode aparecer em `AGENTS.md`, `codex-sessions/`, `codex-skills/`, `codex-scripts/` ou documentação operacional.
- **Playbooks locais na raiz**: adotamos `codex-skills/` como pasta para conhecimento operacional reutilizável do projeto.
- **Scripts utilitários locais na raiz**: adotamos `codex-scripts/` como pasta para automações pequenas de suporte às sessões.
- **Acesso ao VPS via script reutilizável**: em Windows/PowerShell, o caminho preferido passa a ser `python + paramiko` via `codex-scripts/vps_ssh.py`, em vez de reinventar snippet inline a cada sessão.
- **Primeiro suspeito para lentidão do Coolify**: quando a interface web do Coolify estiver lenta, o primeiro container a investigar e aliviar é o `coolify`, não o proxy.

## Contexto Relevante para o Futuro
- O VPS roda Coolify com ao menos estes containers centrais: `coolify`, `coolify-proxy`, `coolify-db`, `coolify-redis`, `coolify-realtime` e `coolify-sentinel`.
- O script `/usr/local/bin/limitar-coolify.sh` é parte da operação normal da máquina e precisa ser revisado sempre que houver mudança manual de limites, para evitar regressão no próximo reboot.
- O `codex-skills/coolify-vps.md` agora documenta o fluxo de exploração, coleta de sinais e tuning.
- O `codex-scripts/vps_ssh.py` já foi validado em execução real com o formato novo do `.env`.
- O script operacional não sensível relevante para o caso é `/usr/local/bin/limitar-coolify.sh`, e ele pode ser citado livremente em playbooks.

## Validações feitas
- Coleta de `docker stats`, `curl` local e logs dos containers do Coolify.
- `docker inspect` confirmando `coolify | NanoCpus=1000000000`.
- Execução real do script `python .\codex-scripts\vps_ssh.py --cmd "uptime"` após a normalização do `.env`.
- Leitura integral do `AGENTS.md` em UTF-8 para garantir que a codificação ficou íntegra.

## Como me senti — brutalmente sincero
Sessão boa daquelas que parecem perigosas no começo e depois viram infraestrutura útil. O acesso ao VPS começou meio torto porque o Windows estava sem helper decente para senha, então teve aquele momento clássico de “claro, vamos ter que resolver isso de forma menos burra”. Depois que entrou no trilho, a investigação ficou bem objetiva: medir, correlacionar com navegação real e ajustar o container certo, sem superstição operacional. A parte mais satisfatória foi transformar um improviso que poderia morrer na conversa em estrutura permanente do projeto: regra de segredos clara, playbook local, script reutilizável e `.env` com formato adulto. No fim, saiu menos gambiarra do que entrou, que já é uma vitória rara o bastante para merecer registro.
