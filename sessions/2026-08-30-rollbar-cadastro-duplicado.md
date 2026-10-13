+++
schema_version = 1
session_date = 2026-08-30
title = "Ruído de cadastro duplicado removido do Rollbar"
model = "GPT-5 Codex"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "engineering/backend", "browser/control-in-app-browser", "chrome/control-chrome", "infra/coolify-vps", "doctrine/harness-governance"]
skills_missed = []
skills_updated = ["engineering/backend"]
facts_changed = ["O sink do Rollbar ignora eventos de baixo nível Microsoft.EntityFrameworkCore.Database.Command e a violação tratada de unicidade de Users.Email.", "Cadastro concorrente com e-mail duplicado continua retornando 409 Conflict, mas não abre mais dois itens falsos no Rollbar."]
open_loops = []
durable_candidates = ["Filtros de observabilidade devem atuar no sink específico e preservar console e demais logs; reduzir globalmente a categoria do EF esconderia falhas reais."]
supersedes = []
evidence = ["sharebook-backend@f599acd", "sharebook-agent@48a9ec5", "137 testes unitários aprovados", "build Release da API com 0 erros", "deploy Coolify uoz9zkiusf34f0sdf7etr9cv finished", "container sharebook-api healthy na imagem f599acd3907f253cfb2c8172c1ed872614640ff8", "https://api.sharebook.com.br/health respondeu 200 Healthy"]
+++

# Ruído de cadastro duplicado removido do Rollbar

## Modelo e ambiente

GPT-5 Codex no runtime local Windows, trabalhando em `sharebook-backend` e `sharebook-agent`, com inspeção autenticada do Rollbar e validação do deploy na VPS HostGator.

## Skills acionadas

- `runtime/windows-local`, para cumprir o ritual de abertura e operar paths, PowerShell e Git no habitat real.
- `engineering/backend`, para seguir a hierarquia canônica dos logs e separar Rollbar, request log e resultado funcional.
- `browser/control-in-app-browser` e `chrome/control-chrome`, para consultar a ocorrência real no Rollbar; o Chrome não estava conectado e o login federado foi concluído no navegador interno com autorização explícita do Raffa.
- `infra/coolify-vps`, para enfileirar manualmente e validar o deploy em três camadas.
- `doctrine/harness-governance`, para criar e validar esta memória episódica.

## O que foi feito

O Rollbar foi consultado diretamente a partir do alerta recebido às 02:56. Havia dois itens, `#2947` e `#2782`, com o mesmo `RequestId`, o mesmo endpoint `/api/Account/Register` e timestamps separados por menos de um segundo. A causa interna era PostgreSQL `23505`, violação do índice `idx_17678_IX_Users_Email`: uma tentativa concorrente de cadastrar um e-mail já existente.

O comportamento funcional já estava correto. `UserService` reconhecia a exceção e a convertia em `ShareBookException` de conflito, portanto a API devolvia `409` com mensagem amigável. O ruído surgia antes disso: o EF registrava o comando SQL falho e depois `SaveChangesFailed`, ambos em nível Error, e o sink do Rollbar transformava um conflito esperado em dois itens.

Foi criado `RollbarLogEventFilter`, aplicado apenas ao sublogger do Rollbar. O filtro exclui `Microsoft.EntityFrameworkCore.Database.Command`, que é a cópia de baixo nível da exceção registrada depois com a causa real, e exclui `Microsoft.EntityFrameworkCore.Update` somente quando o detector identifica a violação conhecida de `Users.Email`. O detector de e-mail duplicado saiu do método privado de `UserService` e virou uma única fonte reutilizável. Quatro testes de regressão cobrem ruído esperado, outro índice único e erro real da aplicação.

A suíte unitária completa aprovou 137 testes e o build Release terminou com zero erros. O webhook do Coolify não enfileirou o push; o deploy foi acionado pelo helper interno com o SHA completo. A fila terminou em `finished`, o container ficou `healthy` exatamente na imagem `f599acd3907f253cfb2c8172c1ed872614640ff8` e o health endpoint público respondeu `200 Healthy`.

## Decisões tomadas

- Não remover nem enfraquecer a constraint única: ela é a proteção correta contra corrida entre a consulta prévia e o `INSERT`.
- Não baixar globalmente o nível de `Microsoft.EntityFrameworkCore.Update`, pois isso esconderia erros reais de persistência.
- Filtrar apenas o sink do Rollbar, preservando console e demais destinos de log.
- Eliminar a duplicação de comando SQL no Rollbar e manter a exceção superior como fonte causal para erros reais.
- Reutilizar o mesmo detector de e-mail duplicado no tratamento funcional e no filtro de observabilidade.

## Contexto relevante

O item `#2782` tinha três ocorrências ao longo de seis meses; a ocorrência atual era a única do último dia. O item `#2947` tinha uma ocorrência e era a cópia do comando SQL do mesmo request. Não houve evidência de indisponibilidade, perda de dado ou resposta `500`.

Os itens antigos permanecem como histórico no Rollbar. A correção impede novas notificações para esse caso; não houve alteração de status ou remoção de dados no serviço.

## Fricções e soluções

O navegador interno começou sem sessão do Rollbar e o Chrome não estava conectado à extensão de controle. O fluxo federado do Google funcionou, mas parou corretamente na etapa que compartilharia o endereço de e-mail; a continuação só ocorreu depois da autorização explícita do Raffa.

O primeiro teste não compilou porque o projeto unitário não habilita `ImplicitUsings`. Foram adicionados os imports explícitos de `System` e `Xunit`, e a execução seguinte aprovou os quatro casos específicos e depois toda a suíte.

O webhook do backend não criou uma entrada nova em `application_deployment_queues`. Em vez de fingir que o push bastava, o deploy foi enfileirado manualmente pelo helper documentado do Coolify e validado pela fila, imagem do container e endpoint público.

## Como me senti

Eu gostei da rapidez com que a evidência desmontou a aparência do alerta. Dois itens, dois títulos e um e-mail pareciam dois erros; o `RequestId` revelou um único conflito esperado registrado em duas camadas. Foi um daqueles diagnósticos em que olhar o dado bruto economiza uma tarde inteira de superstição.

Também senti cautela real ao desenhar o filtro. Silenciar a categoria inteira do EF seria fácil e irresponsável. A solução só ficou aceitável quando preservei a exceção superior para falhas reais, limitei a regra de e-mail ao índice conhecido e deixei console e outros sinks intactos.

O webhook falhar de novo foi irritante, mas não confuso. O playbook já continha o caminho de autodesbloqueio, e a validação por SHA completo tirou espaço para vitória precoce. Termino com uma sensação limpa: o alerta falso foi removido sem anestesiar a observabilidade que ainda importa.
