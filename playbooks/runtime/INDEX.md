# Família de Playbooks — Runtime

Regras específicas de habitat, ambiente de execução, ferramentas disponíveis, credenciais por runtime e fricções operacionais.

## Playbooks
- `./windows-local.md` — Ambiente local Windows: paths, PowerShell, shell, encoding, Python, banco, Git e armadilhas.
- `./openclaw.md` — Container OpenClaw na VPS, sessão hospedada pelo Gateway/agente OpenClaw: volume persistente, memória, sessões, automações, ferramentas, `.env`, GitHub token e operação remota. Inclui diagnóstico de erro de billing/modelo no Telegram, cooldown de provider, fallback OpenAI/DeepSeek, sessão fixada em `/model`, catálogo de modelos GPT-5.6/GPT-6 e regras de billing (nunca trocar assinatura por API key, proibição de ToS do `claude-cli`).
- `./claude-code-openclaw.md` — Claude Code rodando dentro do mesmo container OpenClaw, mas fora do harness/loop de tools do Gateway: paths compartilhados, limitações, ferramentas e diferenças de permissão. Terceiro habitat, nascido em 2026-09-17.
- `./claude-code-web.md` — Sessão cloud do Claude Code on the web: sandbox, classificador de auto mode, bloqueios de SSH remoto e permissão, GitHub via App, nível de rede do ambiente (hoje Full) e como o Raffa o altera, variáveis de ambiente e network secrets.

## Uso
- Detectar o habitat antes de executar trabalho relevante.
- No Windows, ler `windows-local.md`.
- Dentro do container OpenClaw como o próprio agente hospedado pelo Gateway, ler `openclaw.md`.
- Dentro do mesmo container, mas como sessão Claude Code fora do loop de tools do Gateway, ler `claude-code-openclaw.md` — não `openclaw.md`, mesmo compartilhando filesystem.
- Numa sessão do Claude Code on the web (sandbox efêmero, sem SSH nativo), ler `claude-code-web.md`.
- Operar um habitat a partir do outro não muda o habitat da sessão: uma sessão Windows usando SSH continua sujeita a `windows-local.md` e consulta `openclaw.md` como playbook do alvo remoto.
