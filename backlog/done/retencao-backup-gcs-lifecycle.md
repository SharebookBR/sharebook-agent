# Retenção de backups consolidada no lifecycle nativo do GCS

## Conclusão

Resolvido em 2026-08-22.

O bucket `pegasus-coolify-backups` já tinha uma regra nativa de Object Lifecycle Management:

- ação: `Delete`
- condição: `Age = 60` dias

Portanto, a premissa de acúmulo indefinido estava errada. O erro recorrente vinha de uma segunda retenção configurada no Coolify, em paralelo ao TTL do bucket.

## Mudança aplicada

- Preservado o lifecycle nativo de 60 dias no GCS.
- Zerados somente os três critérios de retenção S3 dos backups de banco no Coolify.
- Zerados somente os três critérios de retenção S3 do backup de volume no Coolify.
- Retenção local e upload para o bucket permaneceram inalterados.

## Validação

- A API XML do GCS retornou HTTP 200 e a regra `Delete / Age 60`.
- Os campos remotos de retenção no Coolify ficaram todos em zero.
- O `CleanupInstanceStuffsJob` foi executado de forma controlada às 20:01:46Z.
- O último erro de delete permaneceu em 19:54:04Z: a execução controlada não gerou nova falha.
- Nenhum objeto-probe do diagnóstico permaneceu no bucket.

## Decisão durável

O TTL remoto dos backups pertence ao bucket. O Coolify continua responsável por gerar e enviar os backups, mas não deve manter uma segunda política de expiração S3 para este storage GCS-compatível.
