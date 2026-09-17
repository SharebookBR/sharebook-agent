# Sharebook Runtime — Claude Code dentro do container OpenClaw

Terceiro habitat do Sharebook-agent, nascido em 2026-09-17. Compartilha o container Coolify do OpenClaw (`/data/workspace`, `/data/.openclaw`, mesmas variáveis de ambiente do template) mas **não é** o habitat `openclaw.md`: aqui quem roda é o Claude Code (CLI), com seu próprio harness de tools, não o agente hospedado pelo Gateway OpenClaw.

## Quando usar

- Sempre que a sessão for Claude Code e o filesystem detectado for o container OpenClaw (`/data/workspace`, env vars `OPENCLAW_*` do template Coolify presentes).
- Antes de aplicar qualquer regra de `openclaw.md` a uma sessão Claude Code — a maior parte não se aplica aqui.

## O que este habitat é (e não é)

- **É**: Claude Code operando com filesystem e ambiente compartilhados com o container que também roda o Gateway OpenClaw. Os quatro repositórios operacionais vivem nas mesmas pastas irmãs de sempre em `/data/workspace/`.
- **Não é**: o agente hospedado pelo Gateway OpenClaw. Não tenho o profile de tools dele (`sessions_spawn`, `memory_search`, `active-memory`, cron nativo). Tenho o toolset do Claude Code (Bash, Read/Edit/Write, subagentes próprios, etc.).
- O binário `openclaw` existe no PATH e pode ser chamado via shell para diagnosticar ou operar o *serviço* OpenClaw como alvo externo (ex.: `openclaw status --deep`) — isso é operar OpenClaw a partir de fora, não prova nem herda capacidade deste habitat.
- Memórias episódicas anteriores registradas com `runtime = "openclaw"` (ex.: 2026-09-16, modelo GPT-5 Codex) pertencem ao habitat do Gateway, não a este. Ler para contexto histórico, mas não assumir que ferramentas ou fluxos daquelas sessões existem aqui.

## Abertura de sessão neste habitat

1. Confirmar que é de fato este habitat: filesystem `/data/workspace` + env `OPENCLAW_*` presentes, mas sessão rodando como Claude Code (sem loop de tools do Gateway).
2. Sync dos repositórios (`sharebook-agent`, `sharebook-backend`, `sharebook-frontend`, `sharebook-ebook-importer`).
3. Ler as memórias episódicas do dia corrente em `sharebook-agent/memory/`, por data de modificação — não confiar em índice.
4. Ler `AGENTS.md` e `SOUL.md` a partir do checkout efetivo.
5. Não rodar o preflight de `openclaw.md` (`openclaw --version`, `config validate`, `memory status`) como diagnóstico da própria sessão — isso mede saúde do serviço OpenClaw, não desta sessão Claude Code.

## Segurança — lição de nascimento (2026-09-17)

Na primeira sessão deste habitat, um `env | grep -i openclaw` para "detectar habitat" imprimiu `SERVICE_PASSWORD_OPENCLAW` e `OPENCLAW_GATEWAY_TOKEN` em claro no output da ferramenta. Ambiente de operador único, sem exfiltração externa — mas a regra do `AGENTS.md` sobre nunca imprimir valor de credencial existe independente de quem está olhando o output no momento; transcript pode ser persistido, indexado ou revisitado depois.

- **Nunca fazer dump amplo de `env`** para checar habitat. Checar variáveis pontuais e específicas (`echo $VAR_NAME | head -c 20` ou `[ -n "$VAR_NAME" ] && echo set`) em vez de listar tudo que contém um prefixo.
- Se precisar confirmar que uma env var existe, confirmar presença/tamanho, não valor.
- Detecção de habitat não exige ver o segredo — só exige ver o nome da variável e a estrutura de diretório.

## Memória e continuidade

- A memória canônica deste habitat é a mesma do Sharebook-agent: `sharebook-agent/memory/*.md`, com o ritual de início/fim de sessão do `AGENTS.md`.
- Claude Code mantém, à parte, seu próprio sistema de memória persistente (fora deste repo). Ele guarda contexto sobre como colaborar com o Raffa em geral; a memória operacional do Sharebook continua vivendo aqui, em `sharebook-agent/memory/` e nas skills — não duplicar uma fonte na outra.
- Git: commits deste habitat levam atribuição de Claude Sonnet 5 (ou o modelo Claude vigente), distinguíveis de memórias/commits anteriores de GPT-5 Codex no habitat `openclaw.md`. Isso é dado útil para entender de qual habitat uma decisão histórica veio.

## Anti-padrões

- Tratar este habitat como o habitat `openclaw.md` só porque o filesystem é o mesmo container.
- Assumir que tools nativas do Gateway OpenClaw (`memory_search`, `sessions_spawn`) existem nesta sessão.
- Rodar preflight ou diagnóstico do Gateway OpenClaw como se fosse autoavaliação desta sessão.
- Dump amplo de variáveis de ambiente para detectar habitat.
