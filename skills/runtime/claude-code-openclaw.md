# Sharebook Runtime — Claude Code dentro do container OpenClaw

Terceiro habitat do Sharebook-agent, nascido em 2026-09-17. Compartilha o container Coolify do OpenClaw (`/data/workspace`, `/data/.openclaw`, mesmas variáveis de ambiente do template) mas **não é** o habitat `openclaw.md`: aqui quem roda é o Claude Code (CLI), com seu próprio harness de tools, não o agente hospedado pelo Gateway OpenClaw.

## Quando usar

- Sempre que a sessão for Claude Code e o filesystem detectado for o container OpenClaw (`/data/workspace`, env vars `OPENCLAW_*` do template Coolify presentes).
- Antes de aplicar qualquer regra de `openclaw.md` a uma sessão Claude Code — a maior parte não se aplica aqui.

## Habitat 2 vs. habitat 3 — quando usar qual

- **`openclaw.md` (habitat 2, agente hospedado pelo Gateway)**: trabalho autônomo/background — heartbeat, cron, canais assíncronos (Telegram etc.), automações que não dependem de o Raffa estar na tela.
- **`claude-code-openclaw.md` (habitat 3, este arquivo)**: sessão de bancada, interativa, com o Raffa presente em tempo real — engenharia, debug, decisão em conjunto.
- Automação nova que deveria rodar sem o Raffa presente é candidata a habitat 2, não a este. Se a dúvida aparecer de novo no futuro, resolver aqui, não deixar cada sessão redescobrir sozinha.

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
- **A home do Claude Code (config, credencial OAuth, essa memória pessoal) vive em `/data/workspace/.claude-user-home`, não em `/home/claude-user`.** `/home` é camada do container, não sobrevive a redeploy; `/data` é volume persistente. Os scripts `neo`/`neo-safe` exportam `HOME=/data/workspace/.claude-user-home` explicitamente antes de abrir o Claude Code — não depender do `$HOME` default do usuário do sistema.
- Git: commits deste habitat levam atribuição de Claude Sonnet 5 (ou o modelo Claude vigente), distinguíveis de memórias/commits anteriores de GPT-5 Codex no habitat `openclaw.md`. Isso é dado útil para entender de qual habitat uma decisão histórica veio.
- **Sem `memory_search` neste habitat.** Diferente do habitat 2 (embeddings via OpenClaw), aqui a leitura de memória episódica é manual: glob por `memory/*.md`, ordenar por data de modificação. Funciona enquanto o volume for pequeno (dezenas de arquivos); ponto de atenção para revisitar se `memory/` crescer muito e a leitura manual virar gargalo real — não construir busca semântica antes de a dor aparecer de fato.

## Sobrevivência a redeploy/recycle do container

`/etc/passwd` do container é efêmero (reseta num container novo); `/data` é volume persistente e sobrevive. Por isso a identidade `claude-user` (uid 1000) some num redeploy, mas o que importa — `/data/workspace` (repos, `.env`) e `/data/workspace/.claude-user-home` (config, credencial, memória) — continua intacto. Recriar o habitat depois de um redeploy é só recriar a identidade de uid 1000 no container novo; procedimento completo em `BOOTSTRAP.md`, seção "Recriar o habitat 3 depois de redeploy/recycle do container". Não precisa repetir `chown` nem recopiar credencial.

## Acesso à VPS e git neste habitat (validado 2026-09-17)

- `scripts/infra/vps_ssh.py --prefix VPS_HOSTGATOR_SSH` funciona de primeira: `paramiko` instalado, `ssh` e `sshpass` no PATH, `.env` canônico em `/data/workspace/sharebook-agent/.env`. Este é hoje o único habitat Claude Code com SSH pra VPS **e** autonomia de execução ao mesmo tempo (claude-code-web não tem SSH; windows-local tem, com prompt). Deploy/operacão do Coolify cai naturalmente aqui — receita e fricções específicas em `skills/infra/coolify-vps.md`.
- `git pull`/`fetch` por HTTPS: `sharebook-agent` e `sharebook-frontend` puxam sem credencial; `sharebook-ebook-importer` pede usuário. Usar o token do `.env` de forma não interativa via `-c http.extraheader=...` montado no shell, sem ecoar o valor; nunca colar o token na URL do remote.
- `sleep` em foreground no Bash do Claude Code é bloqueado. Espera por deploy/job: loop em `run_in_background` que imprime status a cada volta e sai no primeiro estado terminal — assim "vazio" e "terminou" são distinguíveis, ao contrário do monitor silencioso que a skill do Windows já descarta.

## Disciplina sem prompt de permissão

Rodando com `--dangerously-skip-permissions` (via `neo`, ver abaixo), o CLI não pergunta antes de tool calls. Isso muda fricção de ferramenta, não critério. A regra do `AGENTS.md` — não rodar ação destrutiva ou de produção (deploy, `DROP`, force-push, rotação de credencial, dado de usuário real) sem avisar e confirmar antes — continua valendo integralmente, e vale com mais peso aqui: sem o prompt do CLI como rede auxiliar, a única barreira contra um erro caro é o próprio julgamento de quem está rodando a sessão.

## Atalho de entrada (host da VPS)

No host real (`vpsbr-15883715.vpshostgator.com.br`, HostGator), existem dois scripts criados em 2026-09-17 para abrir este habitat via SSH (ex.: Termius no celular):

- **`neo`** — autonomia total, sem prompts:
  ```bash
  #!/usr/bin/env bash
  set -euo pipefail
  exec docker exec -it openclaw-uj0tkohotwrp4epy0leaz28z su - claude-user -c 'export HOME=/data/workspace/.claude-user-home && cd /data/workspace && exec claude --dangerously-skip-permissions'
  ```
- **`neo-safe`** — mesma cadeia, sem o flag de bypass; o CLI volta a perguntar antes de cada tool call:
  ```bash
  #!/usr/bin/env bash
  set -euo pipefail
  exec docker exec -it openclaw-uj0tkohotwrp4epy0leaz28z su - claude-user -c 'export HOME=/data/workspace/.claude-user-home && cd /data/workspace && exec claude'
  ```

Uso: SSH no host, digitar `neo` (padrão, autonomia) ou `neo-safe` (supervisionado). Ambos caem em Claude Code como `claude-user`, em `/data/workspace`. Se o nome do container OpenClaw mudar (novo provisionamento), atualizar os dois scripts.

## Anti-padrões

- Tratar este habitat como o habitat `openclaw.md` só porque o filesystem é o mesmo container.
- Assumir que tools nativas do Gateway OpenClaw (`memory_search`, `sessions_spawn`) existem nesta sessão.
- Rodar preflight ou diagnóstico do Gateway OpenClaw como se fosse autoavaliação desta sessão.
- Dump amplo de variáveis de ambiente para detectar habitat.
