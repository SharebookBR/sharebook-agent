# Scripts de Infra

Acesso, automação e utilitários de infraestrutura.

## Scripts
- `github_askpass.sh` — helper para autenticação Git/HTTPS.
- `pg_tunnel.py` — túnel SSH do Windows até o Postgres dentro da VPS, para quando o Coolify não está expondo a 5432 na internet. Descobre o IP do container sozinho e não altera nada no servidor. Aceita `--local-port`, `--container` e `--prefix`.
- `vps_ssh.py` — acesso e automação SSH na VPS. Aceita `--prefix` para escolher o conjunto de credenciais no `.env` (padrão `VPS_SSH`, que hoje aponta para a caixa antiga da Hostinger; use `--prefix VPS_HOSTGATOR_SSH` para a VPS de produção).

## Uso
- Preferir para acesso remoto, automação e tarefas de suporte operacional.
