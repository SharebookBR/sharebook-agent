---
name: claude-code-host-vps
description: "Claude Code operando diretamente no host VPS, fora do container OpenClaw: Docker, logs, restart, processos e inspeção controlada de SQLite."
---

# Claude Code direto no host VPS

Este é um habitat distinto do container OpenClaw e do Claude Code dentro dele. A sessão roda diretamente no host VPS, normalmente com acesso root, e pode observar ou operar os containers do deployment. Não transportar automaticamente conclusões de permissão, paths, processos ou credenciais entre os habitats.

## Antes de operar

- Confirmar que a sessão está realmente no host (`hostname`, `pwd`, `docker ps`) e registrar o container alvo pelo nome exato.
- Ler o playbook do domínio da tarefa além deste playbook: `coolify-vps` para deploy/infra, `backend` para API e banco, `openclaw` para o comportamento do Gateway.
- Preferir investigação read-only. Restart, mudança de configuração, credencial, firewall e deploy exigem escopo explícito da tarefa.
- Nunca imprimir tokens, chaves ou conteúdo sensível de `.env` em saída ou memória.

## Superfícies disponíveis

- `docker logs <container>` e `docker inspect <container>` para logs, `StartedAt`, imagem, mounts e estado de restart.
- `docker exec <container> ...` para executar a ferramenta dentro do ambiente correto; o fato de o host conseguir executar Docker não significa que o container tenha a mesma ferramenta.
- `docker restart <container>` reinicia o processo inteiro e pode apagar a janela disponível em `docker logs`; confirmar antes o que precisa ser preservado.
- Processos do host (`ps`) ajudam a distinguir processo do Gateway, `codex app-server` e serviços do container, mas não substituem os logs da aplicação.
- Para SQLite de um container, localizar o mount/arquivo com `docker inspect` e usar uma ferramenta compatível (por exemplo `node --experimental-sqlite` quando disponível), sempre em leitura salvo autorização explícita.

## Diagnóstico operacional

1. Fixar a linha do tempo: `docker inspect --format '{{.State.StartedAt}}' <container>` e os horários do incidente.
2. Verificar se o container reiniciou ou foi redeployado antes de confiar em `docker logs`; logs anteriores ao `StartedAt` não estarão disponíveis ali.
3. Cruzar o log do container com a fonte persistente adequada: Coolify DB para deploys, Postgres para fatos de domínio e Grafana/Loki quando o log local já foi perdido.
4. Ao investigar falha de modelo/OpenClaw, entrar no container e seguir `playbooks/runtime/openclaw.md`; não concluir billing pela última mensagem do Telegram sem reconstruir a cadeia de fallback.
5. Registrar o comando, o horário, o alvo e a evidência que sustenta a conclusão.

## Guardrails

- Root no host aumenta capacidade, não autorização: não editar arquivos de produção, reiniciar serviços ou alterar credenciais apenas porque o comando é possível.
- `docker restart` é uma intervenção, não uma prova causal; só usar quando a tarefa autorizar e depois validar o estado real.
- Não confundir o filesystem agregado do host com o workspace versionado do Sharebook-agent.
