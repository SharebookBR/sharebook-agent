# Sharebook Runtime — OpenClaw

> **Status: em reativação desde 2026-08-30.**
> O container só é considerado operacional depois do preflight desta skill. Existir no Coolify ou responder HTTP não prova workspace, memória, ferramentas nem automações.

Regras específicas para sessões que rodam dentro do OpenClaw. Uma sessão Windows operando a VPS por SSH continua sendo Windows e usa este arquivo como playbook do alvo remoto.

## Quando usar

- No início de uma sessão hospedada pelo OpenClaw.
- Ao provisionar, atualizar ou diagnosticar o container, sua persistência, memória, sessões, ferramentas, canais ou automações.
- Como referência ao operar o OpenClaw a partir do Windows.

## Princípio do habitat

OpenClaw é infraestrutura cognitiva e operacional: workspace persistente, memória recuperável, sessões, subagentes, automações e messaging podem existir. **Podem** não significa **existem**. Depois de rebuild, upgrade ou troca de volume, provar cada capacidade antes de usá-la.

## Abertura de sessão

1. Confirmar runtime e versão com `openclaw --version`.
2. Confirmar workspace, config e ownership reais; não presumir que o layout histórico sobreviveu.
3. Fazer sync dos quatro repositórios e ler todas as memórias episódicas do dia corrente.
4. Ler `AGENTS.md`, esta skill e `SOUL.md` a partir do checkout efetivo.
5. Consultar skill, script, log, payload, banco ou estado real antes de improvisar narrativa.
6. Para passado, decisão, preferência, pessoa ou data, usar `memory_search` quando disponível e confrontar o resultado com a fonte canônica.

## Preflight obrigatório após provisionamento ou upgrade

Executar no container e guardar a saída sem segredos:

```bash
openclaw --version
openclaw config validate
openclaw doctor --lint
openclaw status --deep
openclaw memory status --deep --agent main
openclaw cron status
openclaw cron list --agent main --all
```

Além disso:

1. Confirmar os mounts persistentes do ponto de vista do host e do container.
2. Confirmar os quatro repositórios em `/data/workspace/` ou registrar o novo path real.
3. Confirmar escrita como o usuário do processo e ownership consistente.
4. Confirmar `memory_search` com uma busca controlada que tenha resultado conhecido.
5. Confirmar ferramentas efetivas na própria sessão (`/tools` ou equivalente), sem deduzir pelo perfil configurado.
6. Confirmar Control UI, canal usado pelo Raffa e um round-trip real do agente.
7. Confirmar jobs um por um. Job listado não basta: exigir histórico recente ou execução controlada.

Falha em um item não invalida todo o runtime; invalida apenas a capacidade correspondente. Documentar o estado parcial em vez de declarar vitória binária.

## Versão e atualização

- O deployment Sharebook via template do Coolify usa deliberadamente `coollabsio/openclaw:latest` (decisão de Raffa em 2026-08-30). Esse wrapper prepara `/data`, variáveis, autenticação web e browser sidecar; trocar pela imagem upstream sem adaptar o compose quebra esse contrato.
- `latest` é política explícita deste deployment. Como a tag é móvel, registrar em todo deploy a versão efetiva (`openclaw --version`) e o digest da imagem.
- Na ativação de 2026-08-30, a tag mudou durante a própria janela de deploy. O estado efetivamente implantado ao fim da checagem era `OpenClaw 2026.7.1 (0790d9f)`, digest `sha256:61bcc5034ecb2f8e80132e61c76aae0f0474e5ad877af2588a76a1284d5369e0`. Nunca usar essa observação como pin nem como substituto da checagem atual.
- Para instalação Docker fora do template, preferir as imagens upstream `ghcr.io/openclaw/openclaw` ou `openclaw/openclaw`.
- Não executar `openclaw update` dentro do container. Atualização de produção é nova imagem + redeploy pelo Coolify.
- Depois do upgrade, rodar o preflight inteiro. Migração automática de config não prova plugins, índice de memória nem jobs.

Referências: [wrapper Coolify](https://github.com/coollabsio/openclaw), [Docker upstream](https://docs.openclaw.ai/install/docker), [releases](https://github.com/openclaw/openclaw/releases) e [configuração](https://docs.openclaw.ai/gateway/configuration).

## Configuração e persistência

- Preferir `openclaw config get|set|unset` para mudanças simples.
- Antes de editar campo incerto, consultar `openclaw config schema` ou `config.schema.lookup`; a validação atual é estrita.
- Rodar `openclaw config validate` depois de qualquer mudança. Usar `openclaw doctor --fix` somente após ler os achados e entender a migração proposta.
- A configuração usa hot reload `hybrid` por padrão. `config set` prova persistência, não aplicação; validar o valor efetivo e o estado do subsistema.
- O deployment histórico do Sharebook montava config em `/data/.openclaw` e workspace em `/data/workspace`. A imagem oficial atual usa `/home/node/.openclaw` internamente. O mount real do Coolify decide: inspecionar, não adivinhar.
- Persistir juntos o config, o banco compartilhado `state/openclaw.sqlite`, os bancos por agente e o workspace. Preservar separadamente o diretório da chave que cifra perfis OAuth.
- Credenciais Sharebook continuam apenas em `sharebook-agent/.env`. Segredos do gateway/provider entram por variáveis/SecretRefs do runtime e nunca no Git, em memória episódica ou output de diagnóstico.

## Gateway, proxy e Control UI

- Para acesso público, `gateway.controlUi.allowedOrigins` deve conter origins completos e exatos, por exemplo `https://claw.sharebook.com.br`, sem barra final.
- No wrapper `coollabsio/openclaw`, o nginx público do container escuta em `8080` e encaminha ao Gateway em `127.0.0.1:18789`. No campo **Domains for openclaw** do Coolify, usar `https://claw.sharebook.com.br:8080`; esse sufixo escolhe a porta interna, enquanto o acesso público continua no HTTPS normal. Confirmar depois do deploy que a label `traefik.http.services.*.loadbalancer.server.port` vale `8080`. Se ela valer `80`, o domínio retorna `502` embora o healthcheck esteja verde.
- Não usar `allowedOrigins: ["*"]` nem `dangerouslyAllowHostHeaderOriginFallback` em produção.
- `gateway.controlUi.dangerouslyDisableDeviceAuth=true` reduz uma camada de autenticação e não deve virar default silencioso. Quando for uma exceção deliberada, manter o basic auth do nginx ativo, restringir a origin e registrar o aviso do `openclaw security audit`.
- Em Docker, preferir o bind suportado pela versão (`lan` no setup oficial atual) em vez de transportar cegamente o antigo `0.0.0.0`.
- `gateway.trustedProxies` deve conter apenas o proxy/rede real do Coolify. O antigo `0.0.0.0/0` era permissivo demais e não é receita canônica.
- Validar o domínio público e também o probe interno do Gateway; uma camada verde não prova a outra.

Referências oficiais: [Control UI](https://docs.openclaw.ai/control-ui) e [segurança do Gateway](https://docs.openclaw.ai/gateway/security).

## Memória e continuidade

- A memória canônica do projeto continua em `MEMORY.md` e `memory/*.md`; índice é mecanismo de acesso, não fonte superior.
- Na release estável `2026.7.1-2`, a configuração vive em `agents.defaults.memorySearch`. Documentação de versões posteriores já mostra `memory.search`; consultar `openclaw config schema` antes de migrar.
- O provider padrão é OpenAI; `sources: ["memory"]` evita indexar transcripts por acidente. Não habilitar `sessions` ou `experimental.sessionMemory` sem decisão explícita sobre a fronteira de recall.
- Mudança de provider, modelo, sources ou tokenizer pode invalidar a identidade do índice. Inspecionar com `openclaw memory status --deep --agent main`; usar `--index` deliberadamente apenas quando a reconstrução for necessária.
- Active Memory é para conversas interativas persistentes. Não roda em headless one-shot, heartbeat, cron ou subagente interno.

Configuração inicial recomendada para o Sharebook:

```json5
{
  agents: {
    defaults: {
      memorySearch: {
      enabled: true,
      provider: "openai",
      model: "text-embedding-3-small",
      fallback: "none",
      sources: ["memory"],
      },
    },
  },
  plugins: {
    entries: {
      "active-memory": {
        enabled: true,
        config: {
          agents: ["main"],
          allowedChatTypes: ["direct"],
          queryMode: "recent",
          promptStyle: "balanced",
          timeoutMs: 15000,
          maxSummaryChars: 220,
          logging: true,
        },
      },
    },
  },
}
```

O schema estável `2026.7.1-2` rejeita `config.mode`; esse campo aparece em versões posteriores. Só adicioná-lo depois de upgrade e `openclaw config schema` confirmar suporte.

Referências oficiais: [memória](https://docs.openclaw.ai/reference/memory-config) e [Active Memory](https://docs.openclaw.ai/concepts/active-memory).

## Sessões e subagentes

- Usar `sessions_spawn` para trabalho de fundo isolado. O default atual é `mode: "run"` e contexto isolado.
- Usar `context: "fork"` apenas quando o filho realmente depender da conversa atual; não é substituto para um briefing claro.
- `mode: "session"` exige `thread: true` e só funciona em canais com thread binding. Não usar como default universal.
- Trabalho que o Raffa acompanhará ou retomará deve usar sessão visível quando a ferramenta oferecer `visible: true`.
- Usar `sessions_yield` para esperar resultado quando disponível. Não recriar espera com polling frenético.
- Subagentes têm custo e política de tools próprios; confirmar `/tools` e limites efetivos antes de delegar operação sensível.

Referência oficial: [subagentes](https://docs.openclaw.ai/tools/subagents).

## Automações e trabalho assíncrono

- Na release estável `2026.7.1-2`, a CLI é `openclaw cron`. A documentação mais nova já chama o mesmo subsistema de `openclaw automations`; detectar pela ajuda da versão instalada em vez de presumir alias.
- Usar automações para wakes, follow-ups e rotinas agentic. Não usar `sleep` longo.
- Automação OpenClaw e cron Linux do importer são mecanismos diferentes. Restaurar um não restaura o outro.
- Desde 2026.6.1, jobs e histórico vivem no SQLite compartilhado. O `jobs.json` é entrada de migração legada; não editá-lo como fonte canônica.
- Após restore ou upgrade, listar jobs e validar um run controlado. Ausência de erro no boot não prova scheduler.

Referência oficial: [automações](https://docs.openclaw.ai/cli/cron).

## Ferramentas, shell e ownership

- Preferir ferramenta nativa quando houver ação de primeira classe; usar `exec` para scripts e diagnóstico local.
- O perfil `coding` inclui filesystem, runtime, web, sessions, memory e automação, mas políticas allow/deny ainda podem remover tools.
- Repositórios ficam em pastas irmãs do workspace persistente. Confirmar o path real antes de Git.
- Arquivos editáveis devem pertencer ao usuário do processo. O histórico usava `node:node`, mas não rodar `chown -R` até confirmar UID/GID e mount corretos.
- Se `git add`, rename ou escrita falhar depois de uma operação root, checar ownership antes de culpar Git.

## Diagnóstico de sessões silenciosas / falhas de modelo

Quando sessões completarem sem output real, sem tool calls e com `usage: {}`, suspeitar de auth/provider antes de chamar de rate limit.

1. Ler trajectory, logs e duração reais.
2. Comparar perfis de auth dos agentes sem imprimir tokens.
3. Rodar `openclaw models auth login --provider openai-codex --agent <agent-name>` se a evidência apontar OAuth.
4. Fazer teste controlado com outro provider/model. Se funcionar, o defeito é específico do caminho OpenAI+OAuth.
5. Não copiar auth de um agente para outro; os perfis são independentes.

## Diagnóstico rápido

1. `openclaw --version`, `openclaw config validate`, `openclaw doctor --lint`.
2. `openclaw status --deep` e logs do Gateway.
3. Mounts, disco e ownership.
4. `openclaw memory status --deep --agent main` e busca controlada.
5. `openclaw cron status`, `openclaw cron list --agent main --all` e histórico do job relevante na release estável.
6. Ferramentas efetivas da sessão.
7. Domínio público, origin exata e proxy real.

## Anti-padrões

- Tratar container `running` como habitat operacional completo.
- Transportar paths, tools ou processos do Windows para o Linux — ou o inverso.
- Usar config antiga sem consultar schema da versão instalada.
- Editar config/SQLite manualmente quando existe CLI ou RPC suportado.
- Atualizar pacote dentro do container e perder a mudança no próximo redeploy.
- Abrir origin ou trusted proxy para o mundo por conveniência.
- Declarar memória ou automação restaurada sem teste funcional.
- Deixar arquivo como root e descobrir a quebra só no commit seguinte.
