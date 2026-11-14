# Restore drill controlado dos backups

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
