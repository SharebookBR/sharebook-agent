+++
schema_version = 1
session_date = 2026-10-12
title = "Observabilidade Grafana/Loki e memory_search restaurada"
model = "GPT-5 Codex"
runtime = "openclaw"
skills_used = ["runtime/openclaw", "engineering/grafana-cloud-explorer", "engineering/backend", "infra/coolify-vps", "doctrine/harness-governance"]
skills_missed = []
skills_updated = ["AGENTS.md", "playbooks/engineering/INDEX.md", "playbooks/engineering/backend.md", "playbooks/engineering/grafana-cloud-explorer.md", "playbooks/infra/coolify-vps.md"]
facts_changed = [
  "Grafana Cloud Logs/Loki ficou operacional para request logs da API via Serilog OTLP, com leitura Loki validada e helper local `scripts/observability/grafana_logs.py`.",
  "OTLP ingest de logs e Loki query usam credenciais/tenants diferentes; o instance id de OTLP não deve ser reutilizado como usuário de leitura Loki.",
  "No Coolify, env vars de aplicação são criptografadas pelo model Laravel; gravação SQL crua em `environment_variables.value` quebra deploy com `DecryptException`.",
  "Para tráfego público direto na API, downloads e imagens, `ClientIp` aparece público nos logs; chamadas SSR Node -> API podem permanecer privadas/internas porque o `ssr_access` do frontend é a fonte certa do IP real de SSR.",
  "A tool dinâmica `memory_search` não estava com índice corrompido: CLI e índice estavam saudáveis; a falha era estado/token velho no Gateway e restart controlado resolveu.",
  "Backlog de observabilidade está cerca de 45% concluído; POC .NET virou done e o épico segue aberto para dashboard mínimo, correlação Rollbar + Grafana, restore drill e traces quando houver pergunta clara.",
]
open_loops = [
  "Criar dashboard mínimo formal/versionado de saúde da API no Grafana.",
  "Correlacionar operacionalmente Rollbar + Grafana em incidentes.",
  "Executar restore drill controlado para backups.",
  "Adicionar traces/Tempo somente quando houver pergunta operacional concreta.",
  "Avaliar alerta/check periódico para detectar `memory_search` com `token_expired` antes de uma sessão operacional.",
]
durable_candidates = [
  "Quando a CLI `openclaw memory search` funciona mas a tool dinâmica `memory_search` retorna `401 token_expired`, suspeitar primeiro de token/cache velho no Gateway e validar com restart controlado antes de reconstruir índice ou trocar credencial.",
  "`openclaw config patch` responder `Restart the gateway to apply` é evidência de que a mudança persistiu mas o processo ativo ainda pode estar usando snapshot antigo.",
  "Para Grafana Cloud Logs, provar ingest OTLP (`204`) e leitura Loki (`200` + query encontrada) separadamente; um não prova o outro.",
  "Em Coolify, nunca configurar env var de aplicação por SQL cru; usar UI/API/model Laravel para preservar criptografia.",
]
supersedes = []
evidence = [
  "backlog/index.md",
  "backlog/done/observabilidade-dotnet-laboratorio-24h.md",
  "backlog/done/restaurar-indice-de-memoria.md",
  "backlog/todo/observabilidade-sharebook-epico.md",
  "playbooks/engineering/grafana-cloud-explorer.md",
  "scripts/observability/grafana_logs.py",
  "openclaw.memory_search retornou resultados reais em 2026-10-12 após restart do Gateway.",
  "openclaw.memory_get abriu `memory/2026-10-12.md` após o restart.",
  "`openclaw memory status --deep --agent main`: 280/280 arquivos indexados, vetores prontos, Dirty: no.",
]
+++

# Observabilidade Grafana/Loki e memory_search restaurada

## Modelo e ambiente

GPT-5 Codex, rodando no OpenClaw em `/data/workspace`, com `sharebook-agent` como harness principal. A sessão atravessou uma compactação e um restart real do Gateway/OpenClaw, então parte do trabalho foi preservar continuidade enquanto o próprio runtime que hospedava a conversa reiniciava.

## Playbooks acionados

Foram consultados `runtime/openclaw`, `engineering/grafana-cloud-explorer`, `engineering/backend`, `infra/coolify-vps` e `doctrine/harness-governance`. O trabalho também atualizou rotas de encontrabilidade em `AGENTS.md`, `playbooks/engineering/INDEX.md`, `backend.md`, `coolify-vps.md` e consolidou o antigo foco Prometheus no playbook único `grafana-cloud-explorer.md`.

## O que foi feito

Fechamos a POC de observabilidade .NET e a transformamos em stack mínima permanente. Métricas .NET via OpenTelemetry/OTLP já estavam úteis no Grafana Cloud; nesta leva, logs da API foram adicionados via Serilog OTLP para Grafana Cloud Logs/Loki, com ingest e leitura validadas separadamente. Também foi criado `scripts/observability/grafana_logs.py`, um helper compacto que lê o `.env` canônico, consulta Loki e redige IPs sem imprimir segredo.

O playbook de Grafana foi consolidado em `playbooks/engineering/grafana-cloud-explorer.md`, cobrindo Prometheus/Mimir, Loki, OTLP, PromQL, LogQL, validação ponta a ponta e armadilhas de credencial. O antigo `prometheus-explorer.md` deixou de ser centro separado, porque o uso real virou Grafana Cloud como superfície única de investigação.

Durante a configuração de logs, apareceu uma fricção no Coolify: gravar env vars diretamente na tabela `environment_variables` quebrou deploy com `Illuminate\\Contracts\\Encryption\\DecryptException: The payload is invalid`, porque o valor precisa passar pelo model Laravel para ser criptografado. Corrigimos o registro operacional no playbook `infra/coolify-vps.md`: usar UI/API/model Laravel, nunca SQL cru.

Também investigamos o `ClientIp`. Para tráfego público relevante, como browser direto, imagens/static e downloads, o IP aparece público nos logs. Chamadas SSR Node/frontend para API aparecem privadas/internas; decidimos não repassar IP real do SSR para a API agora, porque o `ssr_access` do frontend já contém o IP real e mexer nisso aumentaria complexidade e risco de spoofing.

No backlog, o laboratório de observabilidade de 24h saiu de `todo/` e foi para `done/`; o épico `observabilidade-sharebook-epico.md` ficou aberto em cerca de 45%, agora com pendências claras: dashboard mínimo, correlação Rollbar + Grafana, restore drill e traces apenas quando houver pergunta operacional concreta.

Por fim, investigamos e restauramos a tool dinâmica `memory_search`. O índice de memória nunca esteve corrompido: `openclaw memory status/search/get` funcionava pela CLI, e depois mostrou `280/280` arquivos indexados, vetores prontos e `Dirty: no`. A falha estava no caminho dinâmico da sessão, retornando `401 token_expired` por estado/token velho no Gateway. Depois de autorização do Raffa, o Gateway foi reiniciado; a conversa caiu e voltou, e `memory_search` + `memory_get` funcionaram de novo. O item `Restaurar índice de memória do OpenClaw` foi registrado em `backlog/done/restaurar-indice-de-memoria.md`.

## Decisões tomadas

Decidimos manter Grafana Cloud como superfície única de investigação para métricas e logs, em vez de separar artificialmente Prometheus de Loki em playbooks diferentes. A razão é prática: o operador quer responder perguntas de saúde da API, latência, GC, logs e cardinalidade no mesmo fluxo mental.

Decidimos que o IP real do SSR fica no `ssr_access` do frontend, e não será repassado para a API neste momento. A informação existe onde precisa existir, e empurrar `X-Forwarded-For` interno para outro serviço agora criaria uma fonte a mais de dúvida sem benefício proporcional.

Decidimos tratar `memory_search` como incidente de Gateway, não de índice. Isso evitou reconstrução desnecessária e mexida em credenciais. A evidência foi a divergência entre CLI saudável e tool dinâmica quebrada, além da resposta explícita do `openclaw config patch`: `Restart the gateway to apply`.

## Contexto relevante

O ponto operacional mais importante é separar três camadas que parecem uma só quando quebram: índice de memória, CLI de memória e tool dinâmica exposta para a sessão. Nesta sessão, a CLI provava que o índice estava saudável, mas a tool dinâmica ainda falhava porque o Gateway carregava estado velho. Da próxima vez, se esse padrão se repetir, a correção provável é restart controlado do Gateway depois de validar CLI, não rebuild do índice como reflexo.

Para Grafana Logs, outro detalhe precisa sobreviver: escrita OTLP e leitura Loki usam credenciais diferentes. `204` no endpoint OTLP prova que o ingest aceitou o payload, mas não prova que a consulta via Loki está configurada. A validação só fecha quando uma query Loki encontra o evento esperado.

Também ficou claro que o backlog agora está mais limpo: observabilidade não é mais uma POC nebulosa, e memória não é mais pendência no épico. A frente aberta é pequena e objetiva, o que combina melhor com a escala atual do Sharebook.

## Fricções e soluções

A primeira fricção foi o Coolify. A tentativa de configurar env vars por gravação direta no banco parecia sedutora porque era rápida e local, mas quebrou na criptografia própria do Laravel. A solução foi registrar a regra no playbook: env vars passam pela UI/API/model Laravel. É exatamente o tipo de atalho que custa caro se a gente deixa virar tradição oral.

A segunda fricção foi reiniciar o Gateway no meio de uma conversa. O primeiro restart entrou em drain e ficou preso porque o trabalho ativo incluía a própria sessão. Foi preciso aceitar que a melhor solução era parar o turno, deixar o processo reiniciar e validar no retorno. Um pouco desconfortável, mas correto.

A terceira fricção foi de nomenclatura: o item se chamava "Restaurar índice de memória", mas o diagnóstico mostrou que o índice estava saudável. Mantivemos o nome porque era o rótulo descobrível no backlog, mas o conteúdo agora deixa explícito que a causa real era Gateway/token velho.

## Como me senti

Eu saí dessa sessão com aquela sensação boa de quando uma frente deixa de ser "vamos ver" e vira instrumento real. Grafana e Loki não entraram como decoração arquitetural; entraram porque responderam perguntas concretas e deixaram o Sharebook menos dependente de intuição, SSH e caça manual de log.

Também senti um alívio específico quando a `memory_search` voltou. Não era só uma ferramenta quebrada: era uma parte da continuidade do agente rangendo. Ver a CLI saudável enquanto a tool dinâmica falhava foi meio irritante, mas também deu um diagnóstico bonito pela diferença entre as camadas. O conserto teve um momento de apagar a luz e acender de novo, literalmente no Gateway, e eu gostei de termos feito isso sem mexer em segredo nem inventar cirurgia em índice saudável.

Fiquei atento ao risco de declarar vitória cedo. A sessão teve muitos pontos em que uma resposta rasa pareceria suficiente: "logs estão no Grafana", "IP está resolvido", "memory_search voltou". O que tornou o trabalho bom foi fechar cada um com evidência e escrever a borda do que ainda não está pronto. Isso dá menos glamour, mas amanhã o agente que acordar aqui vai agradecer.
