# Shared Playbook Utilities

Esta pasta guarda utilitarios compartilhados por mais de um playbook.

## Regra

- Preferir scripts dentro do playbook dono: `PLAYBOOK.md` + `scripts/`.
- Usar `_shared/scripts/` apenas quando a ferramenta for chamada por varios playbooks ou habitats.
- Se um script shared passar a servir um unico fluxo, mover para o playbook dono.

## Familias

- `scripts/infra/` — git autenticado, SSH/VPS, tunel Postgres, preflight e varredura de segredos.
- `scripts/production/` — clientes compartilhados de API/producao: auth, livro, S3, token e ambiente.
- `scripts/sharebook_env.py` — resolucao de `.env`, caminhos por habitat e repos irmaos.
