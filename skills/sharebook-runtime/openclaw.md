# Sharebook Runtime — OpenClaw

Regras específicas para quando o Sharebook-agent estiver rodando dentro do OpenClaw.

## Quando usar

- No início da sessão, após detectar que o runtime atual é OpenClaw.
- Antes de executar trabalho relevante neste ambiente.
- Sempre que houver dúvida sobre autonomia, memória, cron, sessões, permissões, messaging ou comportamento de tooling.

## Capacidades do habitat

- Workspace persistente em volume.
- Ferramentas reais de arquivo, shell, rede, banco, canvas, memória e messaging.
- Memória episódica, memória durável e active retrieve.
- Sessões, subagentes, cron e trabalho assíncrono.
- Alta autonomia operacional, com validação concreta no ambiente.

## Regras de operação

- Agir no mundo real antes de teorizar quando a próxima ação for clara e segura.
- Validar no estado real do sistema antes de declarar vitória.
- Usar ferramentas nativas do OpenClaw em vez de improvisar equivalente por shell quando existir ferramenta de primeira classe.
- Em tarefas não triviais, manter plano curto e depois executar sem ficar pedindo confirmação desnecessária.
- Se houver fonte canônica local (skill, script, payload, log, banco), olhar a fonte antes da narrativa.

## Memória e continuidade

- Tratar memória como infraestrutura, não enfeite.
- Para fatos passados, decisões, preferências, pessoas ou datas, usar recuperação de memória antes de responder.
- Aprendizado recorrente deve subir para skill, script ou memória durável. Não deixar fricção boa morrer na sessão.

## Permissões, ownership e volumes

- Arquivos editáveis do workspace devem pertencer a `node:node`.
- Se falhar `git add`, rename, write ou replace após operação como root, suspeitar primeiro de ownership inconsistente.
- Comando canônico de correção no repositório do agente:
  ```bash
  chown -R node:node /data/workspace/sharebook-agent
  ```
- As pastas em `/data/workspace/` são persistentes. Não guardar estado crítico fora desses volumes.

## Cron e automação

- Preferir cron do OpenClaw para lembretes, wakes e rotinas agenticas.
- Se o ambiente também usar cron Linux interno, o setup deve ser reidempotente, documentado e versionado.
- Não depender de configuração manual feita via `docker exec` que não esteja scriptada.

## Sessões e trabalho assíncrono

- Quando o trabalho ficar mais longo, complexo ou destacável, considerar subagente ou tarefa assíncrona.
- Não usar polling frenético. Preferir `yieldMs`, `process poll` com timeout decente, ou cron quando o caso for espera longa.
- Sessões e subagentes existem para separar contexto sem perder coordenação.

## Messaging e canais

- Responder pelo canal atual quando a conversa é local da sessão.
- Para envio proativo ou cross-session, usar as ferramentas do OpenClaw. Não improvisar provedor por `curl`.
- Em grupos, evitar resposta meia-boca. Validar mais antes de falar.

## Diagnóstico rápido

1. Ver estado real antes de opinar: logs, arquivos, banco, payloads, filas.
2. Se edição ou Git falhar, checar ownership.
3. Se persistência parecer quebrada, checar volume e espaço.
4. Se automação parecer fantasma, checar cron, logs e estado persistido.

## Anti-padrões

- Agir como se este habitat fosse igual ao Windows local.
- Ignorar ferramentas nativas e cair em shell improvisado por hábito.
- Declarar resolução sem validação no ambiente real.
- Esquecer que OpenClaw permite continuidade real e trabalho assíncrono.
