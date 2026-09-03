# Scripts de Infra

Acesso, automação e utilitários de infraestrutura.

## Scripts
- `git_with_token.py` — wrapper para `git` HTTPS usando `GITHUB_PERSONAL_ACCESS_TOKEN` do `.env` via `http.extraHeader`, sem persistir nem imprimir o token. Subcomandos: `sync` (fetch+rebase+push) e `run <args...>` (comando arbitrário). Aceita `--repo` e `--env-file`. Preferir isto a `git push` puro quando o container não tem credencial configurada.
- `preflight_runtime.py` — guardião do ambiente: verifica e **corrige** automaticamente o que faltar (venv do importer, `poppler-utils`, dependências Python) em vez de só parar e reclamar. `--task importer --no-fix` para só diagnosticar.
- `../lib/sharebook_env.py` — leitura segura do `.env` canônico e resolução de paths por habitat. Fonte da verdade: `SHAREBOOK_AGENT_DIR` no `.env`. Expõe `load_env`, `resolve_agent_dir`, `resolve_env_file`, `sibling_repo`, `github_extra_header`, `dsn_with_host_port` e `print_env_keys` (nunca imprime valores).
- `github_askpass.sh` — helper para autenticação Git/HTTPS.
- `openclaw_telegram_send.py` — envia mensagem pelo Telegram configurado no OpenClaw. Aceita `--target` ou `OPENCLAW_TELEGRAM_TARGET`; se ausentes, descobre o chat direto Telegram mais recente em `openclaw sessions --json`. Use `--dry-run` para validar sem disparar mensagem.
- `openclaw_disable_basic_auth_init.sh` — hook do `coollabsio/openclaw` que remove o Basic Auth gerado pelo nginx; o deployment público passa a depender do pareamento nativo de dispositivos do OpenClaw. Usado via `OPENCLAW_DOCKER_INIT_SCRIPT` no volume persistente do serviço.
- `pg_tunnel.py` — túnel SSH do Windows até o Postgres dentro da VPS, para quando o Coolify não está expondo a 5432 na internet. Descobre o IP do container sozinho e não altera nada no servidor. Aceita `--local-port`, `--container` e `--prefix`. **Preferir isto a pedir a abertura da porta** — ver o protocolo do 5432 em `skills/runtime/windows-local.md`.
- `sweep_secrets.py` — garante que o `.env` é o único lugar do workspace com credencial. Varre os 4 repos por **valor** (pega cada segredo do `.env` e procura literalmente, inclusive percent-encoded) e por **padrão** (chave AWS, private key, DSN com senha). `--history` adiciona o pickaxe do git sobre todo o histórico, que é lento mas é o que responde "isso já foi commitado alguma vez?". Sai com código 1 se achar. Nunca imprime o valor do segredo, só o nome da variável e o arquivo. Rodar antes de commit que mexa em credencial, e depois de qualquer rotação.
- `vps_ssh.py` — acesso e automação SSH na VPS. Aceita `--prefix` para escolher o conjunto de credenciais no `.env` (padrão `VPS_SSH`, que hoje aponta para a caixa antiga da Hostinger; use `--prefix VPS_HOSTGATOR_SSH` para a VPS de produção).

## Uso
- Preferir para acesso remoto, automação e tarefas de suporte operacional.
