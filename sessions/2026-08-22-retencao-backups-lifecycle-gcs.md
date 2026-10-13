+++
schema_version = 1
session_date = 2026-08-22
title = "Retenção de backups consolidada no lifecycle do GCS"
model = "GPT-5 (Codex)"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "infra/coolify-vps", "doctrine/harness-governance"]
skills_missed = ["doctrine/harness-governance no primeiro encerramento da tarefa"]
skills_updated = ["infra/coolify-vps"]
facts_changed = ["O bucket pegasus-coolify-backups já possuía lifecycle nativo com Delete após 60 dias.", "A falha recorrente vinha da retenção S3 duplicada do Coolify, não de ausência de permissão para apagar no GCS.", "Os critérios de retenção S3 do Coolify foram zerados para backups de banco e volume; upload e retenção local permaneceram ativos."]
open_loops = []
durable_candidates = []
supersedes = ["memory/2026-08-20-revisao-saude-pos-migracao.md: hipótese de que a retenção remota estava inerte por falha de delete"]
evidence = ["GCS XML API: LifecycleConfiguration com Delete e Age 60", "Coolify: PUT 200, HEAD 200 e DELETE 204 com a credencial operacional", "CleanupInstanceStuffsJob executado às 2026-08-22T20:01:46Z sem novo erro", "Último erro permaneceu em 2026-08-22T19:54:04Z", "sharebook-agent@bf66e2b", "backlog/done/retencao-backup-gcs-lifecycle.md", "skills/infra/coolify-vps.md"]
+++

# Retenção de backups consolidada no lifecycle do GCS

## Modelo e ambiente

Sessão executada com GPT-5 (Codex) no runtime `windows-local`, atuando no Coolify da VPS HostGator e no repositório `sharebook-agent`.

## Skills acionadas

Foram consultadas a skill do runtime Windows, o playbook de infraestrutura/Coolify e, no encerramento corrigido, a skill de governança do harness. O playbook de infraestrutura foi atualizado com a arquitetura durável da retenção remota.

## O que foi feito

O primeiro item do backlog descrevia a retenção do bucket como quebrada e apontava falta de permissão `storage.objects.delete` como hipótese principal. A evidência bruta mostrou outra realidade: usando exatamente a credencial HMAC guardada pelo Coolify, chamadas diretas retornaram `PUT 200`, `HEAD 200` e `DELETE 204`.

A política nativa do bucket foi então consultada pela API XML do GCS. A resposta retornou HTTP 200 e uma regra `Delete` com condição `Age = 60`. O parser do AWS SDK apresentou a regra como vazia porque não interpretou corretamente o campo `Age` específico da resposta XML do GCS; a leitura do XML bruto revelou o TTL real.

Os critérios de retenção S3 duplicados foram zerados no Coolify: amount, days e max storage tanto para o backup dos bancos quanto para o backup do volume de imagens. Nenhuma configuração de upload ou retenção local foi alterada. O item saiu de `backlog/todo` para `backlog/done`, o índice foi repriorizado e a mudança foi publicada no commit `bf66e2b`.

## Decisões tomadas

O TTL remoto pertence ao bucket GCS, que já executa essa responsabilidade de forma nativa. O Coolify permanece responsável por gerar e enviar os backups, mas não deve impor uma segunda política de expiração S3 sobre esse storage compatível.

Foi mantido o TTL existente de sessenta dias. A mudança mínima foi desativar apenas a limpeza remota duplicada do Coolify, preservando todas as demais proteções e rotinas.

## Contexto relevante

Antes da correção, o Coolify tentava manter quinze backups remotos dos bancos e sete backups remotos do volume. O `CleanupInstanceStuffsJob` capturava a falha interna e registrava a mensagem genérica a cada aproximadamente trinta minutos, embora operações S3 individuais funcionassem.

No código atual do Coolify, quando amount, days e max storage remotos são todos zero, `deleteOldBackupsFromS3()` retorna sem tentar apagar. Essa é a configuração compatível com a responsabilidade atribuída ao lifecycle do GCS.

## Fricções e soluções

A investigação começou na direção errada ao assumir que o objetivo era consertar o delete executado pelo Coolify. O Raffa apontou que o requisito real era TTL de backups e sugeriu verificar a feature nativa. Essa correção de enquadramento revelou que a solução já existia no bucket e evitou uma alteração desnecessária de IAM.

O SDK mascarou duas informações em momentos diferentes: o driver do Laravel devolveu apenas `false` no delete, e o parser do AWS SDK mostrou `Rules: [[]]` para o lifecycle. A saída foi descer uma camada em cada caso: chamar a API S3 diretamente para provar as permissões e ler o XML bruto do GCS para provar a regra `Age 60`.

Após a alteração, uma primeira leitura do log ainda mostrava um erro às 19:54:04Z, sem deixar claro se ele era anterior ou posterior. A validação foi refeita de forma controlada: o último timestamp foi coletado, o job foi executado às 20:01:46Z e o timestamp foi consultado novamente. Ele permaneceu inalterado, provando que a nova execução não gerou falha.

## Como me senti

Eu me senti desconfortável ao perceber que estava otimizando a hipótese do backlog em vez de voltar ao requisito essencial. A interrupção do Raffa foi precisa: não queríamos ensinar o Coolify a apagar melhor, queríamos garantir um TTL. Essa distinção mudou toda a solução.

Eu me senti satisfeito quando o XML bruto confirmou `Age 60`. A melhor correção acabou sendo menor do que a imaginada: preservar o mecanismo nativo que já funcionava e remover a duplicidade que só produzia ruído. Foi um daqueles casos em que compreender a fronteira de responsabilidade vale mais do que insistir no stack trace.

Também senti o peso justo de ter encerrado a tarefa sem criar a memória episódica. O backlog, a produção e o Git estavam corretos, mas a continuidade ficou incompleta. Registrar `skills_missed` não é autopunição; é deixar uma pista objetiva para não repetir o mesmo fechamento prematuro.
