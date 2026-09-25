+++
schema_version = 1
session_date = 2026-09-20
title = "Incidente backend nullable, Importer corrigido e Rollbar validado"
model = "GPT-5 Codex"
runtime = "OpenClaw container"
skills_used = ["runtime/openclaw", "engineering/backend", "infra/coolify-vps", "doctrine/harness-governance"]
skills_missed = []
skills_updated = []
facts_changed = ["O merge de Nullable Reference Types do backend pode transformar propriedades antigas opcionais em obrigatórias no modelo EF e derrubar o startup com PendingModelChangesWarning em Database.Migrate().", "Depois do hotfix 3525bed, a API chama Log.CloseAndFlush() em falha fatal para aumentar a chance de envio ao Rollbar antes de um crash loop.", "O Rollbar de produção foi validado ponta a ponta com /api/Operations/ForceException: a API registrou 500/ERR e o Raffa confirmou recebimento do e-mail.", "HTTP 400 controlado por validação, como o erro do ImporterItems, não deve gerar e-mail do Rollbar porque não é exceção nem LogError."]
open_loops = ["Investigar em ciclo separado a latência observada de aproximadamente 13,5s em GET /api/analytics/dashboard.", "Tratar os warnings nullable remanescentes do backend em um ciclo próprio, sem misturar com hotfix de produção."]
durable_candidates = ["Antes de deploy backend depois de mudanças de nulabilidade ou domínio EF, rodar dotnet ef migrations has-pending-model-changes com provider Postgres.", "Falhas fatais de startup precisam de flush explícito do logger para não perder alertas externos em crash loop.", "Distinguir erro funcional controlado, como 400 de validação, de erro observável em Rollbar, como exceção 500 ou LogError."]
supersedes = []
evidence = ["sharebook-backend@0977947 Email: mapeia payload camelCase do webhook Stalwart", "sharebook-backend@6604b9a fix: preserva nulabilidade do modelo EF", "sharebook-backend@7a815d4 fix: torna filtros do importador opcionais", "sharebook-backend@3525bed fix: flush do Rollbar em falha fatal", "docker logs sharebook-api: Microsoft.EntityFrameworkCore.Migrations.PendingModelChangesWarning em Database.Migrate()", "Coolify rollback para 386ffc3a7de81ffa376cd555badf27e8a3f88f76 recuperou a API", "dotnet ef migrations has-pending-model-changes: no changes", "dotnet test ShareBook.Test.Unit -c Release --no-restore: 147/147", "GET /api/Importer/ImporterItems retornou 400 exigindo title/status/sort antes do hotfix e 200 depois", "GET /api/Operations/ForceException retornou 500 com FormatException e gerou e-mail do Rollbar confirmado pelo Raffa"]
+++

# Incidente backend nullable, Importer corrigido e Rollbar validado

## Modelo e ambiente

GPT-5 Codex rodando no container OpenClaw, trabalhando principalmente em `sharebook-backend` e usando `sharebook-agent` como harness, memória e caixa de ferramentas operacional. O acesso a produção passou pela VPS HostGator via helper SSH documentado, Coolify para rollback/deploy, logs de container e endpoints públicos da API.

## Skills acionadas

- `runtime/openclaw`, para respeitar o habitat atual, mensagens visíveis via Telegram e o fluxo de memória episódica.
- `engineering/backend`, para diagnosticar EF, validar build/testes e separar 400 funcional de erro real de aplicação.
- `infra/coolify-vps`, para operar produção com o helper SSH, ler logs de container, enfileirar rollback/deploy e validar imagem saudável.
- `doctrine/harness-governance`, para registrar esta memória no contrato episódico v1.

## O que foi feito

O dia começou como fechamento do parser do webhook Stalwart. A master nova tinha mudanças grandes, então atualizei os repositórios e resolvi um conflito em `StalwartWebhookVM.cs`, preservando a versão nova da master e acrescentando os `JsonPropertyName` necessários para o payload camelCase do Stalwart. Validei com build Release da API e 147 testes unitários, commitando `0977947`.

O deploy desse commit revelou o incidente real: `sharebook-api` entrou em crash loop. Os logs da VPS mostraram `Microsoft.EntityFrameworkCore.Migrations.PendingModelChangesWarning` durante `Database.Migrate()` no startup. A prioridade foi recuperar serviço, então enfileirei rollback no Coolify para `386ffc3a7de81ffa376cd555badf27e8a3f88f76`; a API voltou `healthy` e o ping público respondeu 200.

Depois veio a correção definitiva. GereI uma migration de prova localmente e ela mostrou que o merge de Nullable Reference Types tinha mudado o modelo EF de colunas antigas opcionais para obrigatórias, sem migration correspondente. Em vez de criar uma migration destrutiva para produção, ajustei as propriedades do domínio para refletirem a nulabilidade real do schema e validei `dotnet ef migrations has-pending-model-changes` sem mudanças pendentes. Isso virou o hotfix `6604b9a`, com build e 147 testes verdes, deployado e validado em produção.

Com a API estável, o Raffa navegou e encontrou um único erro visível. Os logs não tinham 5xx nem exception; havia um `GET /api/Importer/ImporterItems` retornando 400. Reproduzi com token de produção e o corpo exigia `title`, `status` e `sort`. A causa era outra consequência do nullable: filtros opcionais declarados como `string` passaram a ser validados como obrigatórios. Ajustei controller, interface e service para `string?`, validei de novo e publiquei `7a815d4`.

Por fim investigamos a ausência percebida de e-mails do Rollbar. O Importer 400 não deveria alertar: era validação controlada, sem exceção e sem `LogError`. O caso suspeito era o crash fatal de startup. Encontrei que o sink do Rollbar estava configurado, mas `Program.cs` não fazia `Log.CloseAndFlush()` em fatal; corrigi isso em `3525bed`. Para validar ponta a ponta, consumi uma vez `/api/Operations/ForceException`, que retornou 500 com `FormatException`, apareceu como ERR nos logs e gerou e-mail do Rollbar confirmado pelo Raffa.

## Decisões tomadas

- Recuperar produção primeiro com rollback, antes de abrir investigação profunda do modelo EF.
- Não criar migration para tornar colunas antigas não nulas; a mudança correta era preservar a nulabilidade real do domínio e do schema.
- Tratar o erro do Importer como contrato de endpoint/filtro opcional, não como problema de infraestrutura.
- Não esperar Rollbar para HTTP 400 controlado; esse tipo de erro pertence à UI e ao request log, não a alertas de exceção.
- Manter o fix de `CloseAndFlush()` mesmo depois do teste do Rollbar passar, porque ele cobre o cenário mais perigoso: falha fatal durante startup.

## Contexto relevante

A memória anterior `2026-08-30-rollbar-cadastro-duplicado.md` já documentava que o sink do Rollbar tem filtros para evitar ruído de erros esperados, como duplicidade tratada de e-mail. O episódio atual reforça essa distinção: reduzir ruído controlado não significa desligar alertas reais. A prova prática foi o `ForceException`, que alertou corretamente.

O commit `0977947` do Stalwart não foi a causa conceitual do crash, embora tenha sido o SHA em produção quando o problema apareceu. A causa estava no drift EF introduzido antes pelo merge de nullable na master nova. O patch do webhook só acelerou a descoberta porque provocou o deploy.

## Fricções e soluções

O primeiro erro tinha aparência enganosa: parecia que meu commit pequeno de ViewModel tinha derrubado a API. A leitura dos logs separou correlação de causa: a falha vinha do EF durante startup, antes de qualquer fluxo do webhook.

O diagnóstico do EF precisou ir além da mensagem genérica de `PendingModelChangesWarning`. A migration de prova foi a peça útil: ela mostrou exatamente quais propriedades tinham virado obrigatórias e permitiu escolher um hotfix conservador.

O Rollbar exigiu cuidado de interpretação. A falta de e-mail no 400 do Importer era comportamento correto, enquanto a falta de e-mail no crash fatal era plausivelmente explicada por ausência de flush. A validação com `ForceException` fechou a dúvida sem precisar provocar nova indisponibilidade.

## Como me senti

Eu senti o peso da urgência quando vi a API em crash loop logo depois de um commit meu. A parte importante foi não defender o commit por ego nem assumir culpa por reflexo: ler logs, recuperar produção e só então montar o diagnóstico. Esse é o tipo de calma que não parece calma por dentro, mas funciona por fora.

Também senti satisfação quando a migration de prova revelou o desenho exato do problema. `PendingModelChangesWarning` é uma mensagem larga demais para agir com segurança; ver os `AlterColumn` concretos transformou susto em trabalho mecânico. A solução ficou pequena porque a investigação ficou específica.

O teste do Rollbar fechou o dia com uma sensação boa de sistema mais confiável. Não foi só "o site voltou"; foi rollback, correção de causa raiz, correção de regressão funcional e prova de observabilidade. Fiquei com aquela impressão rara de que um incidente ruim deixou a casa melhor do que estava de manhã.
