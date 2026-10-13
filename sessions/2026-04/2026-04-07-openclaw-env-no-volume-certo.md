# Sessão 2026-04-07 — OpenClaw, `.env` e o volume certo

## O que foi feito
- Foi localizado o `.env` operacional em `sharebook-agent/.env`.
- O arquivo foi enviado para a VPS para abastecer o OpenClaw.
- A primeira tentativa colocou o `.env` no caminho errado do host: `/data/workspace/sharebook-agent/.env`.
- Foi investigado o storage do Coolify e confirmado que o OpenClaw usa um volume Docker nomeado montado em `/data` dentro do container.
- O volume correto foi inspecionado com `docker volume inspect uxjdvnw08vlh79uvm1z8z9sj_openclaw-data`.
- O `.env` foi então copiado para o mountpoint real do volume no host: `/var/lib/docker/volumes/uxjdvnw08vlh79uvm1z8z9sj_openclaw-data/_data/workspace/sharebook-agent/.env`.
- A presença do arquivo foi validada de dentro do container com `docker exec`, no caminho `/data/workspace/sharebook-agent/.env`.
- O arquivo enviado por engano para o caminho errado do host foi removido depois.

## Decisões tomadas
- Para apps no Coolify com volume nomeado, o caminho visto dentro do container não pode mais ser tratado como se fosse caminho do host.
- A validação final de arquivo operacional dentro de container deve ser feita com `docker exec`, não só com SFTP ou `ls` no host.
- O `.env` operacional continua sendo fonte da verdade local e não deve ser replicado em memória, documentação ou chat.

## Contexto relevante
- O painel de storage do Coolify mostrava o volume `uxjdvnw08vlh79uvm1z8z9sj_openclaw-data` com destino `/data` dentro do container.
- Isso explicava por que o OpenClaw não encontrava o arquivo quando ele estava em `/data/...` no host: eram sistemas de arquivos diferentes.
- Depois da correção, o agente do OpenClaw conseguiu enxergar o `.env` normalmente.
- O `dream` mais recente é de `2026-04-05`, então não foi necessário rodar novo `dream` nesta rodada.

## Como me senti — brutalmente sincero
- A rodada começou com aquela confiança perigosa de quem acha que `/data` significa a mesma coisa em todo lugar. Não significa. Docker adora humilhar pressa.
- O erro foi simples e bem idiota, mas a correção veio rápida e com prova real de dentro do container, que é o que importa.
- O lado bom é que agora ficou registrada uma armadilha operacional legítima, daquelas que poupam retrabalho e evitam teatrinho técnico na próxima vez.
