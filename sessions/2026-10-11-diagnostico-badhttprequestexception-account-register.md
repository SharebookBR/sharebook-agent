+++
schema_version = 1
session_date = 2026-10-11
title = "Diagnóstico read-only do BadHttpRequestException em /api/Account/Register: rede do cliente, não deploy nem bot"
model = "Claude Sonnet 5"
runtime = "claude-code-host-vps"
skills_used = ["runtime/openclaw", "infra/coolify-vps", "engineering/backend", "engineering/postgres-ro", "doctrine/harness-governance"]
skills_missed = [
  "runtime/host-vps continua sem playbook (mesmo gap já registrado em 2026-10-11-cooldown-openai-travado-e-deepseek-sem-saldo.md, nesta mesma sessão de hoje).",
  "Não existe skill/credencial para consultar a API de leitura do Rollbar — só havia o token de escrita (post_server_item) no ambiente do sharebook-api, então o histórico de ocorrências teve que ser reconstruído por docker logs, Postgres e pela tabela de deploys do Coolify, em vez de uma consulta direta ao Rollbar.",
]
skills_updated = []
facts_changed = [
  "O proxy coolify-proxy (Traefik v3.6) não tem --accesslog habilitado (nem stdout nem arquivo); seu log file não recebe escrita desde 7 de outubro. Hoje nenhuma camada do stack sharebook registra IP/user-agent/duração por requisição HTTP recebida — nem Traefik, nem docker logs sharebook-api (Serilog console, sem IP), nem a tabela Logs do Postgres (só eventos explícitos como rate limit de download).",
  "docker logs sharebook-api morre a cada restart/deploy do container, na prática: o deploy do commit 87a08121d01068440d588a7ac903122636c61e64 às 2026-10-10 23:34:01-23:35:02 UTC (20:34-20:35 -03) apagou todo o log anterior a esse horário, incluindo a própria janela do incidente (20:03-20:07 -03) que estava sendo investigada.",
  "O histórico de deploys do Coolify fica na tabela application_deployment_queues do Postgres do próprio Coolify (container coolify-db, banco 'coolify'), com colunas id, application_id, status, commit, created_at, updated_at — dá para confirmar deploy exato por commit e horário mesmo quando os logs do container alvo já sumiram.",
  "O Rollbar__Token presente no ambiente de sharebook-api é de escrita (post_server_item); não há token de leitura configurado para consultar a API do Rollbar programaticamente.",
  "No dia do incidente (2026-10-10), o volume de registros de usuário bem-sucedidos foi de ~1 por hora ao longo do dia (09h, 11h, 17h, 18h, 19h, 20h, 21h -03), sem rajada — perfil incompatível com tráfego de bot nesse endpoint.",
  "Houve exatamente 1 registro de usuário bem-sucedido criado em 2026-10-10 20:06:01.554398 -03, cerca de 1,15s depois dos dois BadHttpRequestException logados a 20:06:00.4024 -03 — nenhum outro registro entre 19:50 e 20:20 -03.",
]
open_loops = [
  "Traefik (coolify-proxy) continua sem access log habilitado — qualquer futuro incidente de rede/timeout em requisições HTTP vai continuar sem IP/user-agent/duração disponíveis em nenhuma camada do stack. Vale avaliar ligar --accesslog (stdout ou arquivo, com rotação) como melhoria de observabilidade; não fiz essa mudança porque a tarefa pedida era só leitura.",
  "Não existe token de leitura do Rollbar no ambiente — se for preciso cruzar histórico de erros via API de novo, vai faltar essa credencial; perguntar ao Raffa se vale gerar uma e guardar no .env do agente.",
]
durable_candidates = [
  "Quando o container do backend reinicia ou recebe deploy, docker logs sharebook-api começa do zero — qualquer investigação de um incidente anterior ao deploy mais recente depende de outra fonte (Postgres, Coolify DB, Rollbar), nunca do docker logs isolado. Checar StartedAt do container antes de assumir que o log cobre a janela necessária.",
  "A tabela application_deployment_queues no Postgres do Coolify (container coolify-db) é a forma confiável de confirmar se um deploy aconteceu num horário exato e com qual commit — mais confiável do que inferir pela data de modificação de arquivos ou pela memória de quem fez o deploy.",
  "Nem Traefik, nem o backend, nem a tabela Logs registram IP por requisição HTTP hoje nesse stack — qualquer diagnóstico que dependa de 'qual IP fez essa chamada' vai bater nesse teto enquanto o access log do Traefik não for ligado.",
  "Dois eventos de erro logados com timestamps quase idênticos (0,1ms de diferença) não implicam necessariamente uma causa externa simultânea (proxy, restart) — podem ser o heartbeat interno do Kestrel avaliando várias conexões lentas no mesmo tick de verificação de timeout/rate de corpo. Vale considerar essa explicação antes de assumir que algo cortou as duas conexões ao mesmo tempo de fora.",
  "Um registro de usuário bem-sucedido acontecendo poucos segundos depois de um erro de upload travado no mesmo endpoint é evidência forte de 'mesmo cliente, rede instável, tentativa seguinte deu certo'. Correlacionar Users.CreationDate com o timestamp exato do erro é um jeito rápido e não invasivo (sem precisar de e-mail/nome/IP) de distinguir 'usuário real perdido' de 'usuário real que só demorou um pouco mais'.",
]
supersedes = []
evidence = [
  "docker inspect sharebook-api --format StartedAt: 2026-10-10T23:35:01Z (20:35:01 -03), ~29 min depois do incidente reportado (20:03-20:07 -03).",
  "SELECT em application_deployment_queues (coolify-db): id=644, status=finished, commit=87a08121d01068440d588a7ac903122636c61e64, created_at=2026-10-10 23:34:01 UTC, updated_at=2026-10-10 23:35:02 UTC.",
  "docker inspect coolify-proxy --format Config.Cmd: nenhuma flag --accesslog*; arquivo de log do container (json-file) sem escrita desde 7 de outubro.",
  "docker logs sharebook-api (desde o deploy até o fim da sessão): só 1 chamada a /api/Account/Register, 21:43 -03, OPTIONS 204 + POST 200 em 192ms.",
  "SELECT em Users (Postgres sharebook, via docker exec na própria instância, socket local sem senha): 1 linha criada em 2026-10-10 20:06:01.554398 -03, Active=true; nenhuma outra linha entre 19:50 e 20:20 -03.",
  "SELECT por hora em Users no dia 10/10: 1 registro em cada uma das horas 09h, 11h, 17h, 18h, 19h, 20h, 21h (-03) — sem rajada.",
]
+++

# Diagnóstico read-only do BadHttpRequestException em /api/Account/Register: rede do cliente, não deploy nem bot

## Modelo e ambiente

Claude Sonnet 5, via Claude Code direto no host VPS (`vpsbr-15883715.vpshostgator.com.br`), como root, mesma sessão e mesmo habitat sem playbook próprio já registrado hoje em `2026-10-11-cooldown-openai-travado-e-deepseek-sem-saldo.md`. Diferente daquela primeira investigação (infra do próprio openclaw), esta foi puramente sobre produção do ShareBook: três alertas do Rollbar (#2961, #2962, #2963) do mesmo evento em `POST /api/Account/Register`, em 2026-10-10 por volta de 20:06 (-03), pedidos pelo Raffa como tarefa estritamente de leitura — nenhuma alteração de código, configuração ou dado foi feita nesta sessão.

## Playbooks acionados

- `runtime/openclaw` e `infra/coolify-vps`, para navegar entre os containers Docker certos (sharebook-api, coolify-proxy, coolify-db, o Postgres de produção) e lembrar das armadilhas já documentadas de performance/pool de conexão.
- `engineering/backend.md`, seção "Onde estão os logs", que já avisava que `docker logs sharebook-api` não tem IP e morre a cada deploy/restart — isso guiou a investigação e evitou que eu perdesse tempo tentando extrair IP de onde ele nunca existiu.
- `engineering/postgres-ro`, para consultar `Users` em produção com segurança e sem expor dados pessoais.
- `doctrine/harness-governance`, para este registro.

## O que foi feito

O Raffa pediu evidência bruta para fechar um diagnóstico do Rollbar: dois `BadHttpRequestException` (um de corpo de requisição incompleto, outro de timeout de leitura por taxa mínima de dados) logados com 0,1ms de diferença, mais um 500 de 76,8s no mesmo `RequestId` do segundo. As hipóteses eram proxy/Traefik, restart/deploy do container, ou rede ruim do cliente/bot. Ele já tinha subido uma correção (commit `87a0812`) tratando esse tipo de exceção como erro de cliente em vez de alarme no Rollbar; faltava só confirmar a causa de fundo.

Comecei verificando se houve deploy/restart exatamente na janela do incidente (20:03–20:07 -03). O `docker inspect` mostrou o container reiniciado só às 20:35:01 -03, e a tabela `application_deployment_queues` do Postgres do próprio Coolify confirmou: um único deploy nesse dia, iniciado 23:34:01 UTC e concluído 23:35:02 UTC, exatamente do commit `87a0812` — ou seja, o próprio fix do Raffa sendo publicado, 29 minutos depois do incidente, não a causa dele. Isso também explicou por que `docker logs sharebook-api` não tinha nada da janela pedida: o deploy zerou o log.

Fui então procurar os logs do proxy. Inspecionando o comando real do `coolify-proxy` (Traefik v3.6), não encontrei nenhuma flag `--accesslog*` — ou seja, access log nunca esteve habilitado, nem em stdout nem em arquivo, e o arquivo de log do container não recebia escrita desde 7 de outubro. Essa fonte simplesmente não existe hoje nesse stack. Registrei isso como fato e como lacuna de observabilidade, não como algo que eu deixei de encontrar.

Sem IP disponível em nenhuma camada (Traefik, API, ou a tabela `Logs` do Postgres, que só grava eventos explícitos como rate limit de download), mudei a estratégia: medir volume e cruzar com registros reais de usuário. A tabela `Users` mostrou só 1 registro bem-sucedido por hora ao longo do dia 10/10, sem rajada — incompatível com bot. E, na janela exata do incidente, havia exatamente 1 registro criado às 20:06:01.554398 -03, cerca de 1,15 segundo depois dos dois `BadHttpRequestException` às 20:06:00.4024 -03. Nenhum outro registro apareceu entre 19:50 e 20:20 -03, e a busca por acesso SSR à página `/register` nessa janela nos logs do frontend não retornou nada (quem submeteu provavelmente já tinha a página aberta de antes).

Com tudo isso, montei a conclusão para o Raffa: causa mais provável é rede do cliente (não deploy, não bot, e o timing de 0,1ms entre as duas exceções é mais coerente com o heartbeat interno do Kestrel avaliando duas conexões lentas no mesmo tick do que com um evento externo cortando as duas ao mesmo tempo), e risco a usuários reais é baixo — o padrão encontrado é de alguém com conexão instável que, momentos depois, conseguiu se cadastrar.

## Decisões tomadas

- Não tentar adivinhar ou aproximar IP/user-agent de nenhuma fonte indisponível; reportar a ausência como fato, com a causa técnica exata (Traefik sem `--accesslog`), em vez de preencher a lacuna com suposição.
- Usar a tabela de deploys do Coolify como fonte de verdade sobre horário de restart/deploy, em vez de confiar só em timestamp de arquivo ou em `docker logs`.
- Cruzar o incidente com `Users.CreationDate` em vez de insistir em achar o IP do request que falhou — essa correlação respondeu à pergunta que importava (usuário real perdeu o cadastro ou não?) sem precisar de nenhum dado pessoal.
- Não alterar nada em Traefik, Coolify ou no backend, mesmo identificando a lacuna do access log, porque a tarefa era estritamente de leitura; registrar a lacuna como open loop em vez de corrigi-la por conta própria.
- Não imprimir e-mail, nome ou IP de nenhum usuário real nesta memória nem na resposta ao Raffa, só contagens e timestamps.

## Contexto relevante

Esta investigação reforça, de um jeito concreto, uma lição que a memória de 2026-09-22 (`incidente-conexoes-cache-ssr`) já tinha deixado: perder os logs antigos da API a cada deploy é uma fragilidade real de observabilidade neste projeto, não só um detalhe incômodo. Hoje a única fonte de verdade sobrevivente a um restart é o banco (Postgres de produção e Postgres do Coolify) e o Rollbar — e o Rollbar só tem token de escrita disponível, então nem ele pôde ser consultado programaticamente aqui.

Também é relevante notar que o diagnóstico ficou mais forte por *não* depender de IP: a pergunta real do Raffa era "um usuário real foi afetado?", e isso foi respondido com uma correlação de timestamp no próprio banco de produção, sem precisar expandir a superfície de dados pessoais tocados.

## Fricções e soluções

A única fricção real foi notar, ao investigar os logs do Traefik, que a explicação "o proxy cortou as duas conexões ao mesmo tempo" simplesmente não tinha como ser confirmada nem descartada por falta de instrumentação — não é que o proxy esteja inocentado por evidência, é que ele está inocentado por *ausência total de evidência dos dois lados*. Resolvi isso sendo explícito com o Raffa sobre o que é fato observado (nenhum deploy na janela, nenhuma rajada, um registro real bem-sucedido 1,15s depois) versus o que é inferência razoável mas não prova (o heartbeat do Kestrel como explicação mais provável para o timing de 0,1ms). Prefiro entregar uma conclusão com essa granularidade do que uma certeza que eu não tenho.

## Como me senti

Gostei do formato desta sessão: era uma tarefa de leitura pura, com limites claros ("não altere nada"), e isso deixou a investigação mais parecida com perícia do que com operação — cada fonte que eu abria (container, banco do Coolify, Postgres de produção) só servia para confirmar ou eliminar uma hipótese, sem nenhuma pressão para "resolver" algo ao vivo como na sessão anterior do cooldown. Foi um alívio poder fechar com uma conclusão honesta e proporcional: não é um mistério resolvido com certeza absoluta, é uma hipótese bem suportada por eliminação das outras três.

Também notei, com um certo desconforto produtivo, quantas vezes esta própria sessão bateu no mesmo teto: falta de access log no Traefik, falta de token de leitura do Rollbar, perda de log a cada deploy. Nenhuma dessas lacunas é nova hoje, mas foi a primeira vez que as três apareceram juntas, na mesma investigação, bloqueando pedaços diferentes da mesma pergunta. Acho que vale nomear isso como padrão, não como três acasos — por isso registrei cada uma como open loop separado, em vez de deixar só na minha resposta de chat para o Raffa, que não sobrevive além desta conversa.
