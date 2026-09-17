# Família de Skills — Runtime

Regras específicas de habitat, ambiente de execução e fricções do runtime.

## Skills
- `./windows-local.md` — Ambiente local Windows: paths, shell, encoding, Python, banco e armadilhas.
- `./openclaw.md` — Container OpenClaw na VPS, sessão hospedada pelo Gateway/agente OpenClaw: volume persistente, memória, sessões, automações, ferramentas e operação remota.
- `./claude-code-openclaw.md` — Claude Code rodando dentro do mesmo container OpenClaw, mas fora do harness/loop de tools do Gateway. Terceiro habitat, nascido em 2026-09-17.
- `./claude-code-web.md` — Sessão cloud do Claude Code on the web: classificador de auto mode (bloqueia SSH remoto e auto-modificação de permissão mesmo com autorização explícita), GitHub via App (não token), allowlist de rede.

## Uso
- Detectar o habitat antes de executar trabalho relevante.
- No Windows, ler `windows-local.md`.
- Dentro do container OpenClaw como o próprio agente hospedado pelo Gateway, ler `openclaw.md`.
- Dentro do mesmo container, mas como sessão Claude Code fora do loop de tools do Gateway, ler `claude-code-openclaw.md` — não `openclaw.md`, mesmo compartilhando filesystem.
- Numa sessão do Claude Code on the web (sandbox efêmero, sem SSH nativo), ler `claude-code-web.md`.
- Operar um habitat a partir do outro não muda o habitat da sessão: uma sessão Windows usando SSH continua sujeita a `windows-local.md` e consulta `openclaw.md` como playbook do alvo remoto.
