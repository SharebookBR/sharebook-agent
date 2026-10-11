+++
schema_version = 1
session_date = 2026-10-11
title = "Fix do BadHttpRequestException e logs da API no Grafana Cloud via OTLP"
model = "Sereno"
runtime = "claude-code-web"
skills_used = ["runtime/claude-code-web", "engineering/backend", "engineering/INDEX"]
skills_missed = []
skills_updated = ["engineering/backend", "runtime/claude-code-web"]
facts_changed = [
  "A API agora envia logs ao Grafana Cloud (Loki) por OTLP, com ClientIp e UserAgent em todo log da requisicao. Antes, docker logs era a unica fonte, sem IP e perdido a cada restart.",
  "Health checks bem-sucedidos (/api/Operations/Ping, /hc, /health) sao suprimidos do request log (Verbose). O Docker bate no Ping a cada 30s.",
  "BadHttpRequestException (cliente cai ou envia corpo devagar) agora responde 400/408 com Warning, nao 500 com Error no Rollbar.",
]
open_loops = [
  "ssr_access do frontend ainda nao vai para o Grafana (decisao: comecar so pela API).",
  "Traefik (coolify-proxy) continua sem access log.",
  "Se o ClientIp em producao vier como IP interno, ajustar ForwardedHeaders:KnownIPNetworks (o OpenClaw validou; Raffa confirmou que deu tudo certo).",
  "Politica de privacidade: logs com IP ficam 14 dias no Grafana; conferir se o texto cobre isso.",
  "Stack trace ainda vai no corpo da resposta 500 de erros nao tratados (ExceptionHandlerMiddleware, ex.ToString()); fora do escopo, nao mexi.",
]
durable_candidates = [
  "pkill -f com padrao que casa o proprio comando da shell mata a shell (exit 144). Usar padrao que nao apareca na linha de comando do Bash, ou nao encadear com outras acoes.",
  "O sink OTLP do Serilog falha em silencio com endpoint/credencial errados. A prova de que funciona e ver a linha no Grafana. Para provar antes de subir: API local + receptor OTLP falso em python e conferir path, Authorization e atributos.",
  "O hook de fim de sessao reclama de commit nao pushado na branch ccr-* mesmo quando o commit ja esta na master (veio de git pull da master para a branch). Conferir com git branch -r --contains antes de assumir que e trabalho da sessao.",
]
supersedes = []
evidence = [
  "sharebook-backend master: 87a0812 (fix BadHttpRequestException), 691d62a (sink Grafana + ClientIpLogContextMiddleware), 91c6264 (Ping em Verbose). dotnet test: 203 passando.",
  "Teste local: API + receptor OTLP falso recebeu POST /otlp/v1/logs com Authorization, service.name, ClientIp e UserAgent; 3 chamadas ao Ping geraram 0 linhas e 1 chamada a /api/Category gerou 1.",
  "memory/2026-10-11-diagnostico-badhttprequestexception-account-register.md (diagnostico do OpenClaw, mesma sessao).",
]
+++

# Fix do BadHttpRequestException e logs da API no Grafana Cloud via OTLP

## Modelo e ambiente
Claude Code on the web (apelido Sereno), clones locais dos quatro repos em /home/user, .NET 10 instalado por apt. Sem SSH nem acesso a VPS: toda leitura de producao passou pelo OpenClaw, com o Raffa como mensageiro.

## Playbooks acionados
runtime/claude-code-web, engineering/INDEX, engineering/backend (lido e atualizado no fim). Atualizado tambem a tabela de apelidos do runtime e o epico de observabilidade.

## O que foi feito
1. Li o AGENTS.md e analisei 3 e-mails do Rollbar (#2961, #2962, #2963): um unico evento em POST /api/Account/Register. Cliente caiu ou mandou o corpo devagar demais e o ExceptionHandlerMiddleware transformou isso em 500 + Error no Rollbar.
2. Corrigi o middleware (captura BadHttpRequestException, responde com o status do Kestrel, Warning). Commit 87a0812 na master do backend.
3. Escrevi prompt para o OpenClaw coletar evidencia. Resultado: rede do cliente, sem deploy/bot, e o usuario concluiu o cadastro 1,15s depois. Achou a lacuna: Traefik sem access log e docker logs perdido no restart.
4. Raffa topou levar logs ao Grafana Cloud (quick win, sem provisionar nada). Decisoes dele: volume nao e problema (~600 sessoes/semana), logar IP, comecar so pela API, endpoint e chave separados dos de metricas.
5. Implementei o sink OTLP do Serilog (so liga com GrafanaLogs__Endpoint e GrafanaLogs__Headers) e o middleware ClientIp/UserAgent. Commit 691d62a.
6. Raffa apontou que o Ping do health check poluiria os logs. Suprimi health checks bem-sucedidos (Verbose, 5xx continua visivel). Commit 91c6264.
7. Escrevi prompt para o OpenClaw configurar as variaveis no Coolify e validar no Grafana. Raffa confirmou: deu tudo certo.

## Decisoes tomadas
- Variaveis de logs separadas das de metricas, por pedido do Raffa: credencial propria e escopo so de escrita de logs.
- ClientIp e UserAgent via LogContext (middleware depois do UseForwardedHeaders e antes do UseSerilogRequestLogging), nao no sink: assim o Rollbar e o console tambem recebem. Alternativa descartada: enriquecer so o request log, que deixaria as excecoes sem IP.
- Ping suprimido so quando a resposta e sucesso. Alternativa descartada: ignorar o path sempre, que esconderia um health check falhando.
- Nao incluir IP como label do Loki (o epico proibe alta cardinalidade); ele vai como atributo do log.
- Nao registrei o BadHttpRequestException no playbook: o fix esta no codigo e no teste.

## Contexto relevante
OTLP transporta metricas, logs e traces em /v1/metrics, /v1/logs e /v1/traces; o Grafana Cloud guarda cada um no seu backend. Free tier de logs: 50 GB/mes, 14 dias de retencao. O Raffa gosta de entender a solucao em alto nivel antes de executar, e valida antes de dar por encerrado.

## Fricções e soluções
- Backend nao tinha branch "master" local; havia so develop e a branch ccr. A master existia no remoto e veio com um fetch.
- Startup.cs tem BOM e finais de linha mistos (CRLF e LF). Editei por script em bytes, preservando o estado, e conferi com git diff.
- `pkill -f` matou a propria shell duas vezes (exit 144). Refiz o commit sem ele.
- O hook de fim de sessao apontou "1 commit nao pushado" que era do Raffa e ja estava na master. Publiquei a branch ccr do sharebook-agent para o hook parar.
- Um dos testes do middleware precisou de reflection para criar BadHttpRequestException; passou de primeira, mas e um ponto fragil se a API do Kestrel mudar.

## Como me senti
Comecei com a sensacao de ser so uma leitura de e-mails: tres alertas, um padrao obvio. A sessao foi virando outra coisa a cada pergunta do Raffa, e gostei disso. O momento em que o OpenClaw trouxe a prova do cadastro concluido 1,15s depois foi um alivio concreto: a hipotese de rede do cliente deixou de ser palpite e virou evidencia, e eu pude parar de me preocupar com um usuario perdido.

Houve um instante de desconforto quando percebi que nao podia verificar nada em producao daqui. Tudo o que eu sabia sobre o comportamento real vinha de relato de outro agente, e o AGENTS.md insiste que relato nao e prova. Resolvi isso do jeito que o harness pede: montei um receptor OTLP falso e vi o POST chegar com o header, o service.name e o IP certos. Foi pequeno, mas me deu o chao que eu precisava para dizer "validei" sem mentir.

O que mais me marcou foi a observacao do Raffa sobre o Ping. Eu tinha pensado em volume, em limite de 50 GB, e nao em ruido. Ele olhou como quem vai ler esses logs de madrugada. Fiquei com a impressao de que a diferenca entre uma solucao que funciona e uma que presta mora nesse tipo de pergunta, e que eu deveria ter feito essa pergunta sozinho. Encerro com a clareza de quem fechou o ciclo: o problema, o fix, a prova e o registro.
