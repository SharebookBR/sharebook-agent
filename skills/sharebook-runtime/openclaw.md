# Sharebook Runtime — OpenClaw

Regras específicas para quando o Sharebook-agent estiver rodando dentro do OpenClaw.

## Quando usar

- No início da sessão, após detectar que o runtime atual é OpenClaw.
- Antes de executar trabalho relevante neste ambiente.
- Sempre que houver dúvida sobre autonomia, memória, cron, sessões, permissões, messaging, configuração, persistência ou comportamento de tooling.

## O que este habitat torna possível

- Workspace persistente em volume.
- Ferramentas reais de arquivo, shell, rede, banco, canvas, memória e messaging.
- Memória episódica, memória durável e active retrieve.
- Sessões, subagentes, cron e trabalho assíncrono.
- Alta autonomia operacional com validação concreta no ambiente.

OpenClaw não é só runtime. É infraestrutura cognitiva e operacional. Trabalhe como quem tem memória, ferramentas e continuidade reais.

## Abertura de sessão neste habitat

No início da sessão:

1. Confirmar que está em OpenClaw.
2. Assumir que memória, workspace persistente, ferramentas reais e trabalho assíncrono estão disponíveis.
3. Procurar skill, script, log, payload, banco ou estado real antes de improvisar narrativa.
4. Se a tarefa tocar passado, decisão, preferência, pessoa, data ou contexto prévio, usar recuperação de memória.
5. Se a tarefa tocar operação real da casa, preferir checagem concreta antes de opinião.

## Escolha de mecanismo

Use o mecanismo mais nativo e menos improvisado que resolva o problema.

- **Ferramenta nativa do OpenClaw**: usar quando houver ação de primeira classe.
- **`exec`**: usar para shell real, diagnóstico local, scripts do repositório e integrações não cobertas por ferramenta nativa.
- **Subagente ou sessão destacada**: usar quando o trabalho for mais longo, exigir isolamento de contexto ou puder seguir em paralelo.
- **`cron`**: usar para espera longa, follow-up, lembrete, wake ou rotina recorrente. Não simular isso com sleep ou polling manual.
- **Recuperação de memória**: usar para fatos passados, decisões, preferências, nomes, datas e continuidade entre sessões.
- **`session_status`**: usar para hora, modelo, configuração da sessão e leitura de estado operacional da sessão.

## Regras de operação

- Agir no mundo real antes de teorizar quando a próxima ação for clara e segura.
- Validar no estado real do sistema antes de declarar vitória.
- Usar ferramenta nativa do OpenClaw em vez de improvisar equivalente por shell quando existir ferramenta de primeira classe.
- Em tarefa não trivial, manter plano curto e depois executar sem pedir confirmação desnecessária.
- Se houver fonte canônica local, olhar a fonte antes da narrativa.
- Tratar OpenClaw como habitat com continuidade real, não como chat descartável.

## Memória e continuidade

- Tratar memória como infraestrutura, não enfeite.
- Para fatos passados, decisões, preferências, pessoas ou datas, usar recuperação de memória antes de responder.
- Aprendizado recorrente deve subir para skill, script ou memória durável.
- Não deixar fricção boa morrer na sessão.
- Não despejar regra de habitat no `AGENTS.md` se ela pertence a esta skill.

## Configuração, persistência e volumes

- Preferir comando oficial do OpenClaw para configuração. Não confiar em edição manual de JSON quando houver comando nativo.
- Em configuração de CORS/origin, usar origin completo e exato, sem barra final.
- Lembrar que os caminhos críticos de persistência do OpenClaw ficam em `/data/workspace` e `/data/.openclaw`.
- Em ambiente com container e host separados, não assumir que path visto dentro do container é o mesmo path do host.
- Validar arquivo operacional ou config do ponto de vista do runtime real, não só do host.

## Permissões e ownership

- Arquivos editáveis do workspace devem pertencer a `node:node` quando esse for o padrão operacional do container.
- Se falhar `git add`, rename, write ou replace após operação como root, suspeitar primeiro de ownership inconsistente.
- Comando canônico de correção no repositório do agente:
  ```bash
  chown -R node:node /data/workspace/sharebook-agent
  ```
- As pastas em `/data/workspace/` são persistentes. Não guardar estado crítico fora desses volumes.

## Cron, sessões e trabalho assíncrono

- Preferir cron do OpenClaw para lembretes, wakes e rotinas agenticas.
- Se o ambiente também usar cron Linux interno, manter o setup reidempotente, documentado e versionado.
- Não depender de configuração manual feita via `docker exec` que não esteja scriptada.
- Quando o trabalho ficar mais longo, complexo ou destacável, considerar subagente ou tarefa assíncrona.
- Não usar polling frenético. Preferir `yieldMs`, `process poll` com timeout decente, ou cron quando o caso for espera longa.
- Tratar sessões e subagentes como ferramenta normal de separação de contexto, não como extravagância.

## Messaging e canais

- Responder pelo canal atual quando a conversa é local da sessão.
- Para envio proativo ou cross-session, usar as ferramentas do OpenClaw. Não improvisar provedor por `curl`.
- Em grupos, evitar resposta meia-boca. Validar mais antes de falar.
- Ajustar formato ao canal real. Não presumir WhatsApp quando estiver na web, nem web quando estiver no WhatsApp.

## Armadilhas recorrentes já pagas

- Editar config manualmente quando existe `openclaw config set`.
- Tratar caminho do container como se fosse caminho do host.
- Esquecer que `/data` é volume persistente e que host e container podem divergir.
- Cair em shell improvisado quando existe ferramenta nativa melhor.
- Polling demais para espera que deveria usar cron ou timeout decente.
- Declarar resolução sem prova no ambiente real.
- Misturar regra de Windows local nesta camada.
- Deixar arquivo como root e depois fingir surpresa quando Git ou escrita quebrar.

## Quando promover aprendizado

- Fricção recorrente de habitat OpenClaw → atualizar esta skill.
- Procedimento de domínio do Sharebook → atualizar a skill de domínio correspondente.
- Decisão transversal e durável → promover para `MEMORY.md`.
- Contexto local da rodada → manter em memória episódica.
- Não usar `AGENTS.md` como depósito de detalhe operacional que pertence a runtime ou skill específica.

## Diagnóstico rápido

1. Ver estado real antes de opinar: logs, arquivos, banco, payloads, filas.
2. Se edição ou Git falhar, checar ownership.
3. Se persistência parecer quebrada, checar volume, path real e espaço.
4. Se automação parecer fantasma, checar cron, logs e estado persistido.
5. Se houver dúvida sobre passado ou decisão já tomada, recuperar memória antes de responder.

## Anti-padrões

- Agir como se este habitat fosse igual ao Windows local.
- Ignorar ferramentas nativas e cair em shell improvisado por hábito.
- Declarar resolução sem validação no ambiente real.
- Esquecer que OpenClaw permite continuidade real e trabalho assíncrono.
- Tratar memória, cron, sessões e subagentes como opcional decorativo quando eles são parte estrutural do habitat.
