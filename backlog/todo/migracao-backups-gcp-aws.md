# Migracao dos backups GCP para AWS

## Motivo

Hoje o Sharebook paga storage em dois provedores: AWS e GCP. A AWS ja e a direcao natural para consolidar infraestrutura de objetos do projeto, enquanto o GCP permanece principalmente por causa dos backups da VPS.

Concentrar os backups na AWS reduz dispersao operacional, simplifica auditoria de custo e evita manter duas superficies de storage para o mesmo projeto.

## Prioridade

Baixa no curto prazo.

Em 2026-09-08, ainda ha R$ 16,81 de credito na GCP e o gasto atual esta perto de R$ 4 por mes. Isso da aproximadamente quatro meses de folga antes de a conta virar custo real recorrente. A migracao deve ficar no backlog, mas nao competir com itens de produto ou riscos operacionais mais urgentes enquanto esse credito existir.

## Estado Atual

O GCP e usado hoje para backup da VPS:

- dumps do Postgres;
- filesystem de capas de livros;
- bucket GCS com lifecycle nativo de retencao.

Ha decisao anterior concluida em `backlog/done/retencao-backup-gcs-lifecycle.md`: a retencao remota pertence ao bucket, nao ao Coolify. Essa decisao deve ser preservada na migracao para AWS.

## Objetivo

Migrar os backups da VPS que hoje estao no GCP para AWS, mantendo retencao, restaurabilidade e custo previsivel.

## Escopo

- [ ] Levantar buckets, paths, volumes e jobs atuais de backup no Coolify.
- [ ] Medir custo atual do GCP e estimar custo equivalente na AWS.
- [ ] Criar bucket S3 exclusivo para backups da VPS, separado de ebooks e capas.
- [ ] Definir lifecycle no S3 equivalente ou melhor que a retencao GCS atual.
- [ ] Configurar credencial minima para escrita dos backups e leitura de restore.
- [ ] Migrar dumps do Postgres para o novo destino.
- [ ] Migrar backup do filesystem de capas para o novo destino.
- [ ] Executar restore controlado de Postgres e filesystem em ambiente seguro.
- [ ] Desativar o destino GCP somente depois de validar backups novos e restore.
- [ ] Documentar o procedimento de restore e a politica de retencao.

## Fora de Escopo

- Migrar o pipeline publico de capas para S3 + CDN; isso continua em `backlog/todo/pipeline-capas-s3-cdn.md`.
- Alterar storage de PDFs/ebooks.
- Otimizar CDN, DDoS ou egress publico.

## Riscos

- Backups sem restore testado viram enfeite caro.
- Misturar backups, ebooks e capas no mesmo bucket aumenta risco de permissao e lifecycle errado.
- Remover o GCP antes de observar pelo menos um ciclo completo de backup na AWS cria risco operacional desnecessario.

## Criterio de Conclusao

- Backups da VPS rodam para AWS com sucesso.
- Lifecycle remoto esta configurado no S3.
- Restore de Postgres e filesystem foi testado.
- Coolify nao tenta mais limpar retencao remota por conta propria.
- GCP fica sem dependencia operacional ativa para backups do Sharebook.
