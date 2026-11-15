# Shared Playbook Utilities

Esta pasta guarda utilitarios compartilhados por mais de um playbook.

## Regra

- Preferir scripts dentro do playbook dono: `PLAYBOOK.md` + `scripts/`.
- Usar `_shared/scripts/` apenas quando a ferramenta for chamada por varios playbooks ou habitats.
- Se um script shared passar a servir um unico fluxo, mover para o playbook dono.

## Familias

- `scripts/infra/` — git autenticado, SSH/VPS, tunel Postgres, preflight e varredura de segredos.
- `scripts/infra/load_test/` — teste de carga SSR controlado, usado pela infra e pelos itens de capacidade do backlog: `lt_run.py` (orquestra e aplica os gatilhos), `lt_monitor.py` (host, 1 s, por container via cgroup v2), `lt_gen.mjs` (gerador Node), `lt_status.py` e `lt_analyze.py` (resumos).
- `scripts/infra/pg_pool_test/` — calibração de pool Npgsql/Postgres pela API real, com rampa HTTP e monitor de sessões/host por segundo.
- `scripts/production/` — clientes compartilhados de API/producao: auth, livro, S3, token e ambiente.
- `scripts/sharebook_env.py` — resolucao de `.env`, caminhos por habitat e repos irmaos.
