# Família de Playbooks — Infra e Operação da Casa

Infraestrutura, deploy, VPS, backups, restore e operação da casa fora do fluxo estrito de produto.

## Playbooks
- `./arquitetura-sharebook.md` — Mapa de alto nível: containers, caminho de uma requisição, limites que importam e o que ainda precisa de confirmação no servidor. **Ler primeiro** para se situar antes de qualquer investigação.
- `./coolify-vps.md` — Gestão de infraestrutura, deploy, VPS, containers, logs, backups do Coolify, invalidação manual do cache SSR do frontend, GCP bucket/S3, `s3_uploaded`, volume backup, restore drill e operação do dia a dia.
- `./mail/PLAYBOOK.md` — Operações de e-mail do agente: envio SMTP/Stalwart e processamento de bounces por IMAP.
- `./vps-migration.md` — Playbook de migração de VPS: checklist proativo, DNS de três camadas, restore do Coolify entre caixas, backup/restore, GitHub App source quebrando silenciosamente.

## Uso
- Ler `arquitetura-sharebook.md` quando precisar entender como frontend, API, bancos, Coolify, observabilidade e agentes se conectam, ou antes de investigar um incidente.
- Ler `coolify-vps.md` quando a tarefa envolver servidor, deploy, runtime externo, proxy, domínio, container, Docker logs, `.env` remoto, **limpar o cache do front**, invalidar cache SSR, forçar atualização da Home/PDP, backups, GCP bucket, S3 storage, `s3_uploaded`, volume backup, restore drill, auto-update ou operação da VPS.
- Ler `mail/PLAYBOOK.md` quando a tarefa envolver SMTP do agente, Stalwart, envio operacional de e-mail, bounce, IMAP ou entregabilidade.
- Ler `vps-migration.md` antes de qualquer migração de VPS, ou ao investigar um problema que pode ter origem numa migração passada (deploy quebrado, DNS, backup, restore, certificado).
