# BOOTSTRAP DO SHAREBOOK AGENT

## Missão

Este arquivo existe para orientar o bootstrap do Sharebook Agent em um novo ambiente.

Ele lista as ferramentas, configurações e acessos mínimos que precisam existir para que o agente consiga trabalhar com autonomia no ecossistema Sharebook.

É útil em cenários de migração, reconstrução de servidor ou reinstalação do ambiente do zero.

Não é onboarding humano.
Não é documentação completa do Sharebook.
É um checklist mínimo para o ambiente do agente ser operacional.

---

## Ferramentas obrigatórias

### psql

Usado para acessar o PostgreSQL operacionalmente.

Uso principal:

- consultas de diagnóstico
- validações de dados
- apoio a scripts do agente

Atenção:

> Escritas em produção só devem ser feitas quando houver intenção explícita e segurança operacional.

---

### .NET SDK

Necessário para validar, buildar ou executar projetos .NET quando aplicável.

Validar instalação com:

```bash
dotnet --version
```

---

### Netlify CLI

Usado para deploy rápido de protótipos.

Validar instalação com:

```bash
netlify --version
```

---

### Chrome DevTools MCP

Essencial para depuração de interface, validação de SSR, captura de logs do console do browser e inspeção visual de componentes.

Configuração esperada no Gemini CLI:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

Validações esperadas:

- Ferramentas `mcp_chrome-devtools_*` visíveis no contexto do agente.
- Capacidade de navegar e interagir com o browser real.

---

## Memória semântica

A memória semântica precisa ser configurada conforme abaixo:

```json
{
  "enabled": true,
  "sources": ["memory"],
  "provider": "openai",
  "model": "text-embedding-3-small",
  "fallback": "none"
}
```

Validações esperadas:

- `MEMORY.md` indexado
- arquivos em `memory/*.md` indexados
- `memory_search` funcional

---

## Active Memory

Plugin obrigatório para recuperação automática de contexto recente.

Config geral:

```text
plugin: active-memory
agents: main
allowedChatTypes: direct
queryMode: recent
promptStyle: balanced
persistTranscripts: true
logging: true
```

Validações esperadas:

- plugin carregado no boot
- hook pré-resposta funcionando
- contexto recuperado sendo injetado no prompt

---

## Coolify / rede

Garanta que o container do OpenClaw tenha acesso à network interna do Coolify.

Sem isso, o agente não conseguirá acessar o PostgreSQL interno.

Network esperada:

```text
coolify
```

Host interno do PostgreSQL observado:

```text
fgsgwsckccgk8sccc4gg0gg0:5432
```

Atenção:

> Em novo ambiente, esse hostname pode mudar. Validar o host real do PostgreSQL no Coolify.

---

## Cron Linux no container OpenClaw

Cron observado:

- execução a cada 30 minutos
- usado pelo worker importador de livros

Em novo ambiente, validar:

```bash
crontab -l
```

Também validar se o serviço de cron está ativo dentro do container ou host responsável.

---

## Checklist mínimo pós-instalação

Antes de considerar o novo ambiente pronto, validar:

- `psql` instalado
- `.NET SDK` instalado
- `Netlify CLI` instalado
- `Chrome DevTools MCP` configurado e funcional
- container OpenClaw conectado à network interna correta
- acesso ao PostgreSQL interno funcionando
- memória semântica configurada
- `memory_search` funcional
- Active Memory habilitado
- cron do importador configurado
- cron executando no ambiente correto
- endpoint da API Sharebook acessível
