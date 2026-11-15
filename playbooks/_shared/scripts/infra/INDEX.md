# Shared Infra Scripts

Utilitarios transversais de infraestrutura usados por varios playbooks.

- `git_with_token.py` — wrapper para `git` HTTPS usando `GITHUB_PERSONAL_ACCESS_TOKEN` do `.env`, sem persistir nem imprimir token.
- `github_askpass.sh` — helper para Git/HTTPS quando um fluxo precisa de askpass.
- `vps_ssh.py` — acesso SSH automatizado na VPS por prefixo de credenciais do `.env`.
- `pg_tunnel.py` — tunel SSH para Postgres remoto sem abrir a porta 5432 publicamente.
- `preflight_runtime.py` — diagnostica/corrige dependencias locais esperadas para operacoes do agente.
- `load_test/` — teste de carga SSR controlado (roteiro do V2): `lt_run.py` orquestra monitor + gerador e aplica os gatilhos de parada; `lt_monitor.py` roda no host (1 s; RAM/swap/CPU por container via cgroup v2); `lt_gen.mjs` gera a carga (Node, sem dependências); `lt_status.py` e `lt_analyze.py` resumem. Uso e resultados em `playbooks/infra/coolify-vps.md` ("Teste de carga em produção") e `backlog/done/teste-carga-ssr-origem-externa.md`.
- `sweep_secrets.py` — varredura de segredos por valor e padrao antes de commits sensiveis.
- `openclaw_telegram_send.py` — envio operacional pelo Telegram configurado no OpenClaw.
