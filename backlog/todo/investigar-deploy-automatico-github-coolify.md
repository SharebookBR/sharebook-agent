# Investigar deploy automático GitHub + Coolify

## Problema

Em 31/08/2026, após push direto na `master` do `sharebook-frontend`, o Coolify não enfileirou deployment automaticamente. A produção continuou rodando o SHA anterior (`fa85983...`) até o deploy manual ser disparado pela VPS.

O deploy manual do SHA `85b9a27e4958f51b2212cfa4a712f23ff194a25f` funcionou: o build Docker passou por `npm test`, `build:ssr`, criou imagem nova e deixou o container `sharebook-frontend` saudável. Portanto a falha observada não foi build quebrado; foi ausência de disparo automático.

## Hipótese inicial

Investigar se a migração Hostinger -> HostGator quebrou alguma ponta do caminho GitHub + Coolify:

- webhook do GitHub ainda apontando para domínio, IP, secret ou instalação antiga;
- secret/manual webhook do Coolify recriado ou divergente após restore/migração;
- app `sharebook-frontend` no Coolify sem auto-deploy efetivo apesar de `manual_webhook_secret_github` existir;
- branch protection/status checks no GitHub interferindo no fluxo esperado;
- regra atual do Coolify exigindo deploy manual, sem integração automática real.

## Evidência coletada

- `application_deployment_queues` não tinha entradas novas após `fa85983` até o deploy manual.
- Entradas recentes do `sharebook-frontend` tinham `is_webhook = false`.
- App Coolify: `sharebook-frontend`, branch `master`, `manual_webhook_secret_github` presente.
- Deploy manual `2pxfbmwxnt6wlrnmcbbhegao` terminou `finished`.
- Container final: `sharebook-frontend` saudável na imagem `ykggs80oko0ck00gsk0c8ckg:85b9a27e4958f51b2212cfa4a712f23ff194a25f`.
- HTTP pós-deploy: `https://www.sharebook.com.br/` respondeu `200`.

## Escopo

- Verificar webhook configurado no GitHub para `SharebookBR/sharebook-frontend`.
- Conferir URL, secret, eventos e entregas recentes do webhook.
- Conferir logs do Coolify para chamadas de webhook no horário do push.
- Confirmar se o app está configurado para deploy automático ou apenas webhook manual.
- Repetir com um commit pequeno e observar se a fila recebe deployment sem intervenção manual.
- Documentar o caminho correto de deploy no `AGENTS.md` do frontend e/ou na skill `skills/infra/coolify-vps.md`.

## Fora de escopo

- Não mexer em DNS, proxy ou secrets sem evidência.
- Não reconfigurar GitHub/Coolify no escuro.
- Não confundir falha de webhook com falha de build.

## Critério de pronto

- Causa-raiz documentada.
- Um push controlado na `master` enfileira deployment automaticamente, ou a decisão explícita passa a ser "deploy manual pelo Coolify".
- O próximo agente sabe onde olhar: GitHub webhook deliveries, Coolify `application_deployment_queues`, logs do `coolify` e container final.
