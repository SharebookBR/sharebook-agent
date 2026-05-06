# ONBOARDING.md

## Objetivo

Este arquivo existe para acelerar onboarding, reconstrução de ambiente e futura migração de servidor do ecossistema Sharebook.

Não é enciclopédia. É mapa de sobrevivência.

Foco: registrar configurações, instalações, decisões operacionais e armadilhas reais já encontradas.

---

## Repositórios principais

Todos vivem em `/data/workspace/`:

- `sharebook-agent/` → automações, skills, scripts e playbooks
- `sharebook-backend/` → backend .NET da API Sharebook
- `sharebook-frontend/` → frontend Angular
- `sharebook-ebook-importer/` → worker/importador de ebooks
- `sharebook-prototipo/` → protótipos rápidos HTML/CSS/JS

---

## Persistência no ambiente atual

O app roda em ambiente Coolify com volume persistente montado em:

```text
/data
```

Consequência prática:

- `/data/workspace` deve sobreviver a restart/deploy
- `/data/.openclaw` deve sobreviver a restart/deploy

Na migração, validar isso cedo. Se o volume persistente estiver errado, todo o resto vira teatro.

---

## OpenClaw

### Config principal em uso

```text
/data/.openclaw/openclaw.json
```

### Paths/estado operacional observados

- binário observado em produção: `/usr/local/bin/openclaw`
- processo pai observado: `openclaw`
- processo filho observado: `openclaw-gateway`
- gateway operacional na porta: `18789`
- bind observado: `lan`

### Container atual do OpenClaw

```text
openclaw-uxjdvnw08vlh79uvm1z8z9sj
```

Aplicar reload de config no setup atual via restart do container:

```bash
docker restart openclaw-uxjdvnw08vlh79uvm1z8z9sj
```

### Regra operacional importante

Neste ambiente, nem toda mudança de config deve depender de edição manual do JSON.

Quando possível, usar comando oficial:

```bash
openclaw config set ...
```

Motivo: já houve caso em que editar `/data/.openclaw/openclaw.json` diretamente não se mostrou confiável como estratégia principal de persistência/configuração.

### Update observado

- versão anterior observada: `2026.4.14`
- versão depois do update: `2026.4.18`

Durante o update houve episódio de `detached HEAD`, resolvido com branch local `main`.

---

## CORS / Control UI do OpenClaw

### Regra validada

`gateway.controlUi.allowedOrigins` precisa usar:

- origin completo
- exato
- sem barra final

Exemplo válido:

```text
https://claw.sharebook.com.br
```

Exemplo inválido já observado em produção:

```text
claw.sharebook.com.br
```

Sem `https://`, quebra a regra nova.

### Observação operacional

A hipótese consolidada não foi “reset total do arquivo”, e sim comportamento específico de boot/deploy/runtime em torno da config efetiva.

Então, pós-deploy, validar:

1. o valor salvo no arquivo
2. o valor efetivo carregado em runtime

---

## Coolify / rede / variáveis de ambiente

### Rede interna

O OpenClaw foi conectado à network:

```text
coolify
```

Isso liberou acesso DNS/TCP direto ao Postgres interno em:

```text
fgsgwsckccgk8sccc4gg0gg0:5432
```

Observação importante: houve redeploy que deixou containers em estado `Created`, recuperado com start manual. Vale documentar isso como risco de mudança de rede.

### Variáveis de ambiente observadas no container

Foram vistas durante investigação:

- `COOLIFY_FQDN`
- `COOLIFY_URL`
- `SERVICE_FQDN_OPENCLAW`
- `SERVICE_URL_OPENCLAW`

Mas o consumo direto dessas variáveis pelo código oficial do OpenClaw **não foi comprovado**.

Documentar como “presentes no ambiente”, não como dependência garantida do app.

---

## Memória semântica

### Config aplicada

Em `agents.defaults.memorySearch`:

```json
{
  "enabled": true,
  "sources": ["memory"],
  "provider": "openai",
  "model": "text-embedding-3-small",
  "fallback": "none"
}
```

### Comportamento validado

- indexa `MEMORY.md` e `memory/*.md`
- append simples nesses arquivos trigga watcher/sync
- `memory_search` está funcional
- provider validado: `openai`
- model validado: `text-embedding-3-small`

---

## Active Memory

### Status

Plugin habilitado e validado no OpenClaw atual.

Entrada adicionada em `plugins.entries["active-memory"]` no `openclaw.json`.

### Config inicial aplicada

- `enabled: true`
- `agents: ["main"]`
- `allowedChatTypes: ["direct"]`
- `queryMode: "recent"`
- `promptStyle: "balanced"`
- `timeoutMs: 15000`
- `maxSummaryChars: 220`
- `recentUserTurns: 2`
- `recentAssistantTurns: 1`
- `persistTranscripts: true`
- `logging: true`
- `qmd.searchMode: "search"`

### O que foi validado

- plugin carregou com sucesso no boot
- hook pré-resposta está funcionando
- recall real já executou em sessão
- houve caso concreto de contexto recuperado injetado no prompt

---

## Memória operacional do agente

Estrutura operacional consolidada:

- episódica: `memory/YYYY-MM-DD.md`
- durável: `MEMORY.md`
- experimental: `DREAMS.md`
- checkpoint: `memory/dream-state.json`

Cron observado relacionado a isso:

- `memory-dream-v1-daily` às `06:30 UTC`

Também houve registro de cron:

- `sharebook:heartbeat-6h`

---

## Sharebook API

### Endpoint confirmado

```text
https://api.sharebook.com.br/api
```

Esse endpoint deve entrar no checklist de migração e smoke test.

---

## Ferramentas / ambiente instalados ou ajustados

### `psql`

O cliente PostgreSQL foi instalado para permitir consulta read-only direta.

Estado validado anteriormente:

```text
psql (PostgreSQL) 15.16 (Debian 15.16-0+deb12u1)
```

Uso operacional: preferir `psql` direto para diagnóstico e leitura no Postgres de produção.

### `.NET SDK`

Há memória de instalação/configuração de `.NET SDK` no ambiente geral de trabalho.

Mas atenção:

- no `sharebook-api-dev`, foi observado cenário sem `.NET SDK`
- esse ambiente dev também apareceu usando `SqliteConnection`

Ou seja: não assumir paridade entre dev e prod.

Na migração, confirmar explicitamente:

- versão do `dotnet`
- onde ele está instalado
- qual ambiente realmente depende dele

---

## PostgreSQL / banco / operação

### Fonte da verdade

- Produção usa PostgreSQL como fonte da verdade
- leitura operacional padrão: read-only direto
- SSH é fallback, não caminho principal

### Usuário read-only criado

```text
sharebook_ai_ro
```

Permissão mínima foi validada com sucesso.

### Ordem preferida para consultas

1. `psql` direto
2. MCP
3. SSH

### Script principal de consulta read-only

```text
sharebook-agent/scripts/production/sharebook_prod_pg_ro_query_direct.py
```

### Utilitário SSH oficial

```text
sharebook-agent/scripts/infra/vps_ssh.py
```

Uso típico:

```bash
python3 sharebook-agent/scripts/infra/vps_ssh.py --env-file sharebook-agent/.env --cmd '<comando>'
```

---

## Importer (`sharebook-ebook-importer`)

### Estado arquitetural atual

O importer virou projeto próprio em:

```text
/data/workspace/sharebook-ebook-importer
```

Não está mais conceitualmente acoplado ao `sharebook-agent`.

### Artefatos reais de bootstrap

Existem referências/artefatos operacionais como:

- `README.md`
- `pyproject.toml`
- `Dockerfile`
- `sql/schema.sql`
- `cron/sharebook-ebook-importer.cron.example`
- `docs/PLAYBOOK.md`
- pacote Python em `src/sharebook_ebook_importer/`

### Banco do importer

Banco PostgreSQL do importer:

```text
sharebook_importer
```

### Exorcismo do SQLite

Decisão consolidada:

- SQLite foi removido do pipeline do importer
- PostgreSQL virou fonte única da verdade

Mudanças registradas:

- `.env` ajustado para PostgreSQL only
- `db_factory.py` passou a criar apenas PostgreSQL
- `create_sqlite_database()` passou a falhar explicitamente
- arquivos `.db` foram removidos do fluxo principal

SQLite antigo observado em:

```text
/data/workspace/sharebook-ebook-importer/var/state/importer.db
```

Backups preservados em:

```text
/data/workspace/backups/
/data/workspace/backups/sqlite_exorcism/
```

### Cron do importer

Há dois registros operacionais relevantes:

- cron ativa a cada 30 minutos
- em um desenho operacional, a janela registrada foi entre `00:00` e `06:00` horário local, com expectativa de `12 itens/dia`

Na migração, validar o cron efetivo real e não confiar só na lembrança narrativa.

### Workflow do importer

O workflow foi unificado em `workflow_status` linear.

Estados registrados:

- `waiting_editor`
- `waiting_process`
- `processing`
- `done`
- `error`
- `retry_later`

Além de campos de retry.

---

## Backend / dev / divergências de ambiente

### Containers observados

Houve referência a dois containers distintos:

- `sharebook-api`
- `sharebook-api-dev`

### Divergência importante

Em certo momento, o ambiente dev apareceu:

- usando `SqliteConnection`
- sem variáveis PostgreSQL visíveis
- sem portas públicas mapeadas claras
- aparentemente acessível só pela rede interna do Coolify

Conclusão prática:

**não assumir que dev reflete prod.**

---

## Prototipação rápida / Netlify

### Pasta oficial

```text
/data/workspace/sharebook-prototipo
```

### Deploy padrão

```bash
cd /data/workspace/sharebook-prototipo
netlify deploy --prod --dir .
```

### URL documentada

```text
https://sharebook-prototipo.netlify.app
```

Observação: já houve também deploy efêmero de dashboard/protótipo em URL Netlify temporária. Não assumir que URL efêmera substitui o endereço oficial.

### Token operacional

Há histórico de uso de token presente em:

```text
sharebook-agent/.env
```

Na migração, mapear quais segredos/tokens vivem no `.env` e quais são indispensáveis.

---

## Rotas / frontend / links que valem teste

Rota confirmada como relevante:

```text
/categorias/artes
```

Se houver migração de frontend, reverse proxy, cache, SPA routing ou revalidação de links, isso entra no smoke test.

---

## Cron jobs e automações observados

Itens lembrados/registrados nas memórias:

- `sharebook:heartbeat-6h`
- `memory-dream-v1-daily`
- limpeza semanal
- cron do importer a cada 30 minutos

Na migração, inventariar cron real do host, não só cron “lembrada” em memória.

---

## Operação paralela com subagentes

Limite empírico validado no setup:

```text
5 subagentes simultâneos
```

Acima disso, tratar com cautela. Esse número é útil para playbooks de curadoria/automação paralela.

---

## Checklist sugerido para migração futura

### Antes de migrar

- copiar `/data/.openclaw/openclaw.json`
- confirmar volume persistente `/data`
- validar o que vive em `/data/workspace` e `/data/.openclaw`
- mapear secrets/tokens do `sharebook-agent/.env`
- confirmar nome/estratégia do container no novo host
- validar acesso ao PostgreSQL
- validar hostname interno do Postgres
- validar network `coolify` ou equivalente no novo ambiente
- revisar scripts oficiais em `sharebook-agent/scripts/`
- revisar cron jobs reais do host
- revisar memória persistida (`MEMORY.md`, `memory/`, `DREAMS.md`, `memory/dream-state.json`)
- revisar plugins habilitados no OpenClaw
- revisar divergências entre dev e prod

### Depois de subir o novo ambiente

- validar `openclaw` carregando sem erro
- validar gateway na porta `18789`
- validar WhatsApp/plugin de canal
- validar `memory_search`
- validar `active-memory`
- validar `gateway.controlUi.allowedOrigins` com origin exato
- validar API `https://api.sharebook.com.br/api`
- validar rota `/categorias/artes`
- validar `psql` e scripts Postgres read-only
- validar importer em PostgreSQL, sem SQLite no fluxo principal
- validar cron efetiva do importer
- validar deploy de protótipo rápido se necessário

---

## Nota final

Se novas configurações importantes forem feitas, registrar aqui no mesmo dia.

Agosto/setembro não é momento para depender de memória heroica, nem nossa, nem da máquina.
