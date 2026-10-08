# Família de Playbooks — Infra e Operação da Casa

Infraestrutura, deploy, VPS, backups, restore e operação da casa fora do fluxo estrito de produto.

## Playbooks
- `./coolify-vps.md` — Gestão de infraestrutura, deploy, VPS, containers, logs, backups do Coolify, GCP bucket/S3, `s3_uploaded`, volume backup, restore drill e operação do dia a dia.
- `./vps-migration.md` — Playbook de migração de VPS: checklist proativo, DNS de três camadas, restore do Coolify entre caixas, backup/restore, GitHub App source quebrando silenciosamente.

## Uso
- Ler `coolify-vps.md` quando a tarefa envolver servidor, deploy, runtime externo, proxy, domínio, container, Docker logs, `.env` remoto, backups, GCP bucket, S3 storage, `s3_uploaded`, volume backup, restore drill, auto-update ou operação da VPS.
- Ler `vps-migration.md` antes de qualquer migração de VPS, ou ao investigar um problema que pode ter origem numa migração passada (deploy quebrado, DNS, backup, restore, certificado).
