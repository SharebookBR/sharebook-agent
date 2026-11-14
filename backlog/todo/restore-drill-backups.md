# Restore drill controlado dos backups

## Prioridade

**Topo do backlog, por decisão do Raffa em 2026-11-14.** Temos um processo de backup, mas **nunca o usamos para restaurar**; este item valida se seria possível ou não recuperar o Sharebook. É o que protege contra o pior cenário (perda de dados).

Por que importa, com a história do próprio projeto: em 2026-08-17 descobriu-se que o backup agendado do Postgres apontava para o banco de manutenção `postgres`, **vazio**, em vez dos bancos reais. Rodava toda noite, subia ao bucket e gravava `success`, com arquivos de **exatamente 1.055 bytes**, **desde pelo menos setembro de 2025**: quase um ano de "backups" que não guardavam nada (ver `playbooks/infra/coolify-vps.md`, seção "Backup agendado — success não prova backup"). Foi corrigido e os tamanhos hoje são coerentes (por exemplo `sharebook` na casa de dezenas de MB, volume de capas ~1,3 GB, `s3_uploaded=true`), mas **nenhum restore foi testado**.

**Ordem entre itens:** este item vem **antes** do teste de estresse do Postgres (`investigar-pool-conexoes-e-limite-postgres.md`), porque levar o banco ao limite sem saber se o backup restaura é o pior momento para descobrir que não restaura; e **antes** da migração dos backups para a AWS (`migracao-backups-gcp-aws.md`), para não migrar algo que não sabemos recuperar.

**Versão mínima proposta por Claude (a confirmar com o Raffa, em nome da simplicidade):** restaurar o dump mais recente do banco `sharebook` num container temporário de Postgres, conferir algumas contagens (livros, usuários, categorias) e algumas consultas, abrir algumas capas do volume restaurado, apagar tudo e escrever o passo a passo no playbook de infra. Sem ritual mensal nem automação por ora; repetir quando a infraestrutura mudar. Executor: o OpenClaw (este agente não tem acesso ao servidor).

## Escopo

Executar restore seguro e documentado de dump Postgres e volume de capas a
partir de backup remoto, sem tocar produção.

## Valor

Upload confirmado não prova recuperabilidade. O drill fecha o principal gap de
continuidade operacional.

## Risco

Destino errado pode sobrescrever produção ou expor dados. Usar ambiente isolado,
permissões mínimas e descarte seguro do material restaurado.

## Validação

Objeto remoto, checksum/tamanho, restore de banco e arquivos, integridade
mínima da aplicação restaurada e limpeza do ambiente temporário registrados.

## Relações

- Observabilidade: `observabilidade-sharebook-epico.md`.
- Migração: `migracao-backups-gcp-aws.md`.
