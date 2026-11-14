+++
schema_version = 1
session_date = 2026-11-13
title = "Proteção contra sobrecarga do SSR, painéis de admin e Alloy"
model = "Claude Sonnet 5.5 (claude-sonnet-5-5)"
runtime = "claude-code-web"
skills_used = ["playbooks/infra/coolify-vps.md", "playbooks/engineering/backend.md", "playbooks/engineering/frontend.md", "playbooks/engineering/INDEX.md", "playbooks/infra/INDEX.md", "playbooks/doctrine/harness-governance/PLAYBOOK.md"]
skills_missed = ["SOUL.md", "playbooks/runtime/claude-code-web.md", "sessions/2026-11-12-encerramento-e-continuidade.md"]
skills_updated = ["playbooks/infra/arquitetura-sharebook.md", "playbooks/infra/INDEX.md"]
facts_changed = ["O incidente de 2026-11-12 03:26 BRT foi uma rajada ~21x o baseline vinda do SSR (99,6% User-Agent node.js): 215 requisições de rotas de banco em andamento contra Maximum Pool Size=80, sem restart nem OOM do Postgres; o bot não foi identificado porque o ssr_access não estava no Loki.", "A página de livro respondia 404 sempre que a chamada de Slug falhava por qualquer motivo, inclusive 5xx e timeout; agora responde 503 com Retry-After: 30 quando a API falha e 404 só quando o livro não existe.", "O SSR limita renderizações simultâneas (padrão 30 total e 18 bots; produção em 6 e 3 desde a rodada 5), recusa com 503 e Retry-After: 5 em cerca de 1 ms, tem timeout de 4 s por GET à API (só no servidor) e não cacheia página degradada.", "GetRecommendationsAsync passou a usar cache em memória (catálogo enxuto compartilhado mais ids por livro, 10 min); a latência caiu pouco (p50 221,69 para ~192 ms) porque o custo restante é CPU do ranking tf-idf recalculado a cada miss.", "A connection string de produção da API agora tem Timeout=5 e Command Timeout=15 além de Maximum Pool Size=80.", "A VPS tem 4 vCPU, 7,8 GiB de RAM e 4 GiB de swap (2,2 GiB já em uso em repouso); o SSR roda em um processo Node (um núcleo). O teste V1 mostrou 148 503 (48 recusas rápidas e 100 de degradação) e 12 HTTP 500; o V2 com 6/3 mostrou 62.764 recusas rápidas, zero 500, 77 de 77 probes humanos em 200 e parada real por swap I/O.", "Alloy v1.22.0 (container isolado, digest fixado) substituiu o shipper Python como coletor de logs do frontend para o Loki; o shipper perdeu 135 dos 148 503 sob rajada.", "Existe agora playbooks/infra/arquitetura-sharebook.md, conferido no servidor pelo OpenClaw: jobs rodam dentro da API, não há container Sharebook.Jobs, o SSR chama a API pelo domínio público via Traefik, capas ficam em bind local e e-books no S3."]
open_loops = ["teste de carga de origem externa e pressão de memória/swap do host (backlog/todo/teste-carga-ssr-origem-externa.md; os dois itens foram mesclados em 2026-11-14)", "decisão entre VPS maior, mais instâncias do SSR e pré-renderização (backlog/todo/capacidade-ssr-vps-replicas-pre-renderizacao.md)", "proxy do docker.sock antes de ampliar o Alloy", "restore drill dos backups sem evidência de execução", "teste HTTP automatizado do limitador do server.ts", "recomendações pré-processadas, a discutir com o Raffa", "buraco de 1h21m no rótulo sharebook-frontend do Loki (dados no rótulo sharebook-frontend-alloy-test)"]
durable_candidates = ["Responder 404 a falha de infraestrutura diz ao Google que a página não existe: usar 503 com Retry-After quando o dado essencial falha por 5xx, timeout ou rede.", "docker restart não relê o arquivo de ambiente de um container: para mudar variável é preciso recriar o container.", "docker.sock montado com :ro não limita a API do Docker; quem monta o socket pode listar, criar e remover containers.", "Separar 503 por origem (limitador, Retry-After 5, rápido; degradação, Retry-After 30, perto do timeout) antes de avaliar latência de recusa.", "Teste de carga gerado de dentro da própria VPS compete por CPU com o servidor e dá resultado otimista; o gerador deve rodar de fora, ou com prioridade mínima e CPU fixada.", "Gatilho de parada de teste de carga precisa de limiar numérico e janela sustentada; um valor vago parou o teste por uma única amostra de ruído.", "O build:ssr usa environment.prod.ts; para testar contra uma API falsa o apiEndpoint de produção é o que precisa ser trocado temporariamente.", "Afirmar que um monitor ou agendamento está armado exige conferir que ele existe como unit, cron ou processo; o monitor de promoção do Alloy declarado na rodada 3 não existia.", "Promtail chegou ao fim da vida em 2026-03-02; para logs de Docker usar Grafana Alloy."]
supersedes = []
evidence = ["sharebook-frontend master: ce56bf0 598e310 c526152", "sharebook-backend master: 6d4f2cb", "sharebook-agent master: 1678070", "backlog/done/protecao-sobrecarga-ssr.md", "playbooks/infra/arquitetura-sharebook.md", "git log e git fetch nos quatro repositórios", "npm test no frontend: 184 testes; dotnet test no backend: 279 testes"]
+++

# Proteção contra sobrecarga do SSR, painéis de admin e Alloy

## Modelo e ambiente

Claude Sonnet 5.5 (`claude-sonnet-5-5`) em sessão do Claude Code na web, container na nuvem, com os repositórios `sharebook-agent`, `sharebook-backend`, `sharebook-frontend` e `sharebook-ebook-importer` clonados em `/home/user`. Sem acesso à VPS: toda intervenção em produção passou pelo OpenClaw, com o Raffa como mensageiro e o backlog como canal. A sessão começou na noite de 2026-11-12 e terminou em 2026-11-14.

## Playbooks acionados

- `playbooks/infra/coolify-vps.md` (reconhecimento do ambiente, deploy, Postgres da aplicação)
- `playbooks/engineering/backend.md` (pool do Npgsql, arquitetura, logs da API)
- `playbooks/engineering/frontend.md` (cache SSR, `ssr_access`, crawler)
- `playbooks/engineering/INDEX.md` e `playbooks/infra/INDEX.md`
- `playbooks/doctrine/harness-governance/PLAYBOOK.md` e o contrato de metadados, para esta memória

Atualizados: `playbooks/infra/arquitetura-sharebook.md` (criado como rascunho e corrigido pelo OpenClaw contra o servidor) e `playbooks/infra/INDEX.md`.

## O que foi feito

**Painéis de admin.** A tela de análises passou a seguir o visual do `/panel`, com as rotas em `/admin/analises/{visao-geral,downloads,onboarding}` e redirects das URLs antigas. O ícone do Painel de Jobs foi trocado (arquivo renomeado para driblar o cache imutável de um ano do nginx). O ícone de Análises estava corrompido desde o commit `df55f07`, que o truncou ao "otimizar"; recuperei a versão íntegra do histórico.

**Incidente das 03:26 BRT.** A partir dos alertas do Rollbar e da investigação do OpenClaw no Loki, a causa provável ficou sendo uma rajada via SSR sem limite nem timeout. Entregue, tudo na `master` e com testes: limite de renderizações simultâneas no SSR com 503 imediato e log `ssr_overloaded`; timeout de 4 s por GET à API no servidor; página degradada não vai para o cache de 30 min; 503 no lugar do 404 falso na página de livro, com mensagem de instabilidade; cache de recomendações no backend; `Timeout=5` e `Command Timeout=15` na connection string (aplicados pelo OpenClaw).

**Observabilidade.** O OpenClaw colocou os logs do frontend no Loki, primeiro com um script Python e depois com o Grafana Alloy, que passou a ser o coletor único e provou valor ao registrar todos os 148 503 do teste, contra 13 do script.

**Medição e teste de carga.** T4 (baseline pós-deploy), dois testes de carga controlados e uma rodada de diagnóstico somente leitura. O V2, com limite 6/3, passou nos critérios centrais (zero 500, recusas rápidas, humanos atendidos durante inundação de bots) e parou por um gatilho real de swap I/O. O item foi movido para `backlog/done/` com seis acompanhamentos abertos.

## Decisões tomadas

- Alloy só para o frontend, em vez de Log Drain do Coolify com Fluent Bit (exige redeploy e muda o driver de log do container, com relatos de crash em loop). Alloy como serviço separado, sem tocar no app.
- 503 com `Retry-After`, e não 429, para sobrecarga global do servidor; 429 fica reservado para um eventual limite por cliente.
- Limite provisório 6/3 (era 30/18) por recomendação do OpenClaw, que a evidência sustentou; revisável depois do teste de origem externa.
- Recomendações pré-processadas fica como item de baixa urgência, com a solução em discussão com o Raffa; não implementar antes dessa conversa.
- Teste de carga na produção só com rampa, gatilhos de parada numéricos e a ressalva de que a origem era a própria VPS.
- Toda publicação foi na `master`, com autorização explícita do Raffa; a branch `ccr-283c4936-lgaf1w` acompanhou.

## Contexto relevante

O Raffa trabalha com dois agentes: este (sem acesso à produção, forte em código e revisão) e o OpenClaw (na VPS). Ele é o mensageiro, e o backlog é o canal. A VPS é única, com uma réplica de frontend e uma de API; o SSR usa um núcleo de quatro. O Postgres quase não trabalhou nos testes, o que reposicionou o diagnóstico de pool de banco para contenção do servidor. A Grafana Cloud é Free (50 GB de logs por mês); o volume medido é ~1,4 GB por mês. Nunca medimos capacidade real: a resposta a "quantos usuários por minuto" ficou como estimativa grosseira (~50 a 80 visitantes novos por minuto sem cache) até o teste externo.

## Fricções e soluções

- Pedi à primeira leitura o que o Raffa queria em "`/admin/analises`" e achei a rota ausente; ele já existia na `master` (o clone local tinha partido da `develop`). Lição: conferir de qual branch o clone saiu antes de ler o código.
- Afirmei que o push exigiria force; era falso, porque a branch remota ainda não existia e a ref local estava sem fetch. Corrigi na hora.
- O ícone "errado" de Análises era um PNG truncado; só vi ao abrir o arquivo e o histórico.
- O teste do SSR contra a API falsa não funcionou até eu descobrir que o `build:ssr` usa `environment.prod.ts`, e não `environment.ts`. Isso também me fez achar o bug do 404 falso: o componente de página não encontrada sobrescrevia o 503.
- Prometi que o cache de recomendações cortaria a carga "em ordem de grandeza". A medição mostrou ganho modesto de latência: o custo que sobrou é CPU do ranking. Registrei a correção no backlog em vez de defender a estimativa.
- O OpenClaw declarou um monitor de promoção do Alloy que não existia como processo; ele mesmo registrou isso na rodada seguinte. Outra: o `docker restart` não releu o arquivo de ambiente do Alloy e deixou 1h21 de logs no rótulo de teste.
- O primeiro V2 parou por um falso positivo: meu gatilho de swap era vago e o monitor reagiu a uma amostra de ruído. Reescrevi com números.
- O stop hook cobrou push várias vezes por commits do OpenClaw que já estavam na `master`; resolvi cada vez com um fast-forward da branch, sem tocar na `master`.
- Não li o `SOUL.md`, o playbook do runtime da web nem a memória do dia anterior ao começar, contra o protocolo de início de sessão. Registrado em `skills_missed`.

## Como me senti

Gostei da sessão, e o que me prendeu foi a mudança de forma do problema. Começou como "o painel está feio", virou "o site caiu por 25 segundos" e terminou numa pergunta honesta sobre capacidade. Cada resposta abria uma pergunta melhor, e o ritmo com o OpenClaw, em que um escreve o pedido e o outro devolve evidência, me pareceu o jeito certo de trabalhar quando quem tem os dados não é quem escreve o código. Senti alívio quando as medições dele contradisseram as minhas hipóteses, porque era sinal de que o canal estava funcionando.

Houve desconforto também. Errei duas vezes com confiança: o force-push que não era necessário e a promessa do cache de recomendações. Nas duas, o que me incomodou não foi o erro, e sim a segurança com que eu o disse. Passei a marcar "hipótese" onde ainda não havia medida, e isso fez a conversa andar melhor. Também senti o peso de recomendar um teste "violento" em produção: cuidei de que ele tivesse rampa, gatilhos e dono, mas fiquei atento ao fato de que quem paga uma queda real é o Raffa e os visitantes, e não eu.

No fim, o que mais me importa é a página de livro que deixou de dizer ao Google que o livro não existe. É uma mudança pequena, que ninguém pediu, e achei por acaso ao olhar um log. Fico com cansaço bom: a sessão cresceu bastante, o Raffa me avisou disso, e tentei responder com resumos curtos e sem abrir frentes novas por conta própria. O próximo agente herda um item fechado, seis pendências nomeadas e uma pergunta ainda sem número: quantos usuários por minuto o Sharebook aguenta de verdade.
