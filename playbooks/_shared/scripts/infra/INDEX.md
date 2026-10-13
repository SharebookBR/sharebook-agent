# Shared Infra Scripts

Utilitarios transversais de infraestrutura usados por varios playbooks.

- `git_with_token.py` — wrapper para `git` HTTPS usando `GITHUB_PERSONAL_ACCESS_TOKEN` do `.env`, sem persistir nem imprimir token.
- `github_askpass.sh` — helper para Git/HTTPS quando um fluxo precisa de askpass.
- `vps_ssh.py` — acesso SSH automatizado na VPS por prefixo de credenciais do `.env`.
- `pg_tunnel.py` — tunel SSH para Postgres remoto sem abrir a porta 5432 publicamente.
- `preflight_runtime.py` — diagnostica/corrige dependencias locais esperadas para operacoes do agente.
- `sweep_secrets.py` — varredura de segredos por valor e padrao antes de commits sensiveis.
- `openclaw_telegram_send.py` — envio operacional pelo Telegram configurado no OpenClaw.
