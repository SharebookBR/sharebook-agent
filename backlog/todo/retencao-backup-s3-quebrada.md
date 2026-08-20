# Retenção de backup no bucket não apaga nada

## O sintoma
A cada ~30 minutos, o `laravel.log` do container `coolify` registra:

```
production.ERROR: One or more S3 backup files could not be deleted.
  at /var/www/html/bootstrap/helpers/databases.php:255
  #0 deleteBackupsS3()
  #1 deleteOldBackupsFromS3()
  #2 App\Jobs\CleanupInstanceStuffsJob->enforceBackupRetention()
```

O `CleanupInstanceStuffsJob` roda, tenta aplicar a retenção no bucket `pegasus-coolify-backups` (Google Cloud Storage) e falha em todo delete.

## Por que importa
- **Nada é apagado do bucket.** Os dumps diários (~117 MB/dia entre bancos e imagens) acumulam indefinidamente. É conta de storage crescendo em silêncio.
- O erro é barulho recorrente no log, o que treina a ignorar log do Coolify — mesmo antipadrão do backup que reportava `success` com 1 KB.
- **Não afeta a gravação.** Upload funciona e está provado por listagem dentro do bucket (20/08/2026). É só a limpeza que está quebrada.

## Hipótese principal
A credencial HMAC que o Coolify usa no GCS tem permissão de escrita e leitura, mas não de `storage.objects.delete`. Confirmar antes de mexer — não é o único caminho possível (prefixo de path e formato de bucket S3-compatível também são candidatos).

## O que fazer
1. Reproduzir o delete isolado com a credencial do próprio Coolify (mesmo método de verificação usado em 17/08: script PHP montando um disk e chamando `\Storage::disk()->delete()`), para ver o erro cru em vez do genérico do Laravel.
2. Se for permissão, ajustar a role da service account / chave HMAC no GCS.
3. Definir a política de retenção desejada — hoje `retention_amount_locally = 3` no volume backup, e a retenção remota é a que está inerte.
4. Validar apagando de fato um objeto antigo e conferindo por listagem que ele sumiu do bucket.

## Contexto
Descoberto em 20/08/2026 na revisão de saúde pós-migração para a HostGator. Ver `skills/infra/coolify-vps.md`, seções de backup.
