# BOOTSTRAP DO SHAREBOOK AGENT

## Missão

Este arquivo existe para orientar o bootstrap do Sharebook Agent em um novo ambiente.

Ele lista as ferramentas, configurações e acessos mínimos que precisam existir para que o agente consiga trabalhar com autonomia no ecossistema Sharebook.

É útil em cenários de migração, reconstrução de servidor ou reinstalação do ambiente do zero.

Não é onboarding humano.
Não é documentação completa do Sharebook.
É um checklist mínimo para o ambiente do agente ser operacional.

## Escopo atual

O Sharebook-agent voltou a ter dois habitats em 2026-08-30:

- Windows local (`skills/runtime/windows-local.md`)
- OpenClaw na VPS (`skills/runtime/openclaw.md`)

O bloco **Ferramentas obrigatórias** vale para qualquer habitat que execute aquele tipo de trabalho. As seções OpenClaw são checklist de provisionamento; nenhum item é presumido só porque o container iniciou.

---

## Ferramentas obrigatórias

### Renderização e leitura visual de PDF

Essencial quando a extração textual falhar ou quando for preciso confirmar contexto editorial real a partir das páginas do livro.

Ferramentas mínimas recomendadas:

- `pdftoppm` (pacote `poppler-utils`) para exportar páginas em PNG
- `mutool` (pacote `mupdf-tools`) como fallback técnico útil para inspeção/manipulação de PDF
- `PyMuPDF` (`pymupdf`) para scripts Python de renderização, recorte e inspeção local
- `pypdf` para extração textual básica no worker de triagem

Validações esperadas:

```bash
pdftoppm -h | head
mutool -h | head
python3 -c "import fitz; print(fitz.__doc__.splitlines()[0])"
python3 -c "import pypdf; print(pypdf.__version__)"
```

Uso típico:

```bash
pdftoppm -f 1 -l 5 -png arquivo.pdf /tmp/prefixo
```

Quando usar:

- PDF image-based
- OCR/text extraction fraca ou enganosa
- dúvida editorial sobre faixa etária, tom ou gênero
- necessidade de olhar as primeiras páginas antes de recategorizar ou reescrever sinopse
- quando o worker de triagem precisar extrair texto do PDF sem falhar por dependência ausente

Observação operacional:

- manter as dependências do worker declaradas no projeto, não só no sistema
- validar o ambiente com o worker real após qualquer mudança de dependência

---

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

## Imagem, versão e persistência do OpenClaw

- No Sharebook, usar `coollabsio/openclaw:latest` por decisão explícita de Raffa em 2026-08-30. É o wrapper esperado pelo template do Coolify e prepara `/data`, variáveis, autenticação web e browser sidecar.
- Para evitar os prompts repetidos da Control UI, o deployment Sharebook remove deliberadamente o Basic Auth do wrapper com `scripts/infra/openclaw_disable_basic_auth_init.sh`. Manter `OPENCLAW_DOCKER_INIT_SCRIPT=/data/openclaw-init/disable-nginx-basic-auth.sh` no serviço e o pareamento nativo de dispositivos ativo.

### Hook que desativa o Basic Auth do nginx

O wrapper aplica `AUTH_PASSWORD` com `auth_basic`, mas a Control UI faz requisições que nem sempre repetem essas credenciais, incluindo `/__openclaw__/assistant-media`. Isso reabria indefinidamente a janela nativa de senha. Em 2026-08-30, Raffa decidiu remover o Basic Auth e assumir conscientemente o risco adicional. O wrapper continua injetando o gateway token: device pairing protege a Control UI, mas não substitui autenticação de borda para toda rota HTTP. Para endurecer novamente sem ressuscitar o prompt, usar Cloudflare Access ou Tailscale.

Instalação e contrato:

- fonte versionada: `scripts/infra/openclaw_disable_basic_auth_init.sh`;
- destino persistente no volume do OpenClaw: `/data/openclaw-init/disable-nginx-basic-auth.sh`;
- variável do serviço Coolify: `OPENCLAW_DOCKER_INIT_SCRIPT=/data/openclaw-init/disable-nginx-basic-auth.sh`;
- o hook espera o `openclaw.conf` gerado pelo wrapper, remove `auth_basic` e `auth_basic_user_file`, valida com `nginx -t` e recarrega o nginx;
- remover `gateway.controlUi.dangerouslyDisableDeviceAuth`; cada navegador ou app deve possuir identidade pareada;
- manter `gateway.trustedProxies` restrito ao nginx local (`127.0.0.1` e `::1`).

Validar depois da instalação, restart ou redeploy:

```bash
docker exec <container-openclaw> nginx -t
docker exec <container-openclaw> sh -lc 'nginx -T 2>&1 | grep -n auth_basic || echo NGINX_BASIC_AUTH_ABSENT'
curl -sSkD - -o /dev/null https://claw.sharebook.com.br/ | grep -Ei '^(HTTP/|WWW-Authenticate:)'
openclaw config get gateway.controlUi.dangerouslyDisableDeviceAuth
openclaw devices list
```

Resultado esperado: `/` responde `200` sem `WWW-Authenticate`; o grep não encontra `auth_basic`; `dangerouslyDisableDeviceAuth` não existe; notebook e celular aparecem pareados. Se o hook não estiver no env efetivo do container, o Basic Auth voltará no próximo restart.
- `latest` é móvel: em cada deploy, registrar versão efetiva (`openclaw --version`) e digest. Na ativação de 2026-08-30 a tag mudou durante a própria janela de deploy; o estado efetivamente implantado ao fim da checagem era `OpenClaw 2026.7.1 (0790d9f)`, digest `sha256:61bcc5034ecb2f8e80132e61c76aae0f0474e5ad877af2588a76a1284d5369e0`. Não reutilizar essa observação como pin nem presumir que continuará igual.
- Fora desse template, preferir as imagens upstream `ghcr.io/openclaw/openclaw` ou `openclaw/openclaw`.
- Atualizar pelo Coolify com nova imagem; não executar `openclaw update` dentro do container.
- Persistir config/state, chave dos perfis OAuth e workspace. A imagem oficial usa `/home/node/.openclaw`; o deployment histórico do Sharebook usava mounts em `/data/.openclaw` e `/data/workspace`. Inspecionar os mounts reais e registrar o contrato efetivo.
- O checkout usado pelo agente OpenClaw é `/data/workspace/sharebook-agent`. O `.env` operacional deve existir em `/data/workspace/sharebook-agent/.env`, com modo `600`, e ser sincronizado a partir do `.env` canônico do `sharebook-agent` local por transferência segura. Nunca registrar seu conteúdo, copiá-lo para o Git ou deixá-lo em arquivos temporários; após rotação, repetir a cópia e comparar apenas tamanho/hash.
- O wrapper Coolify serve HTTP pelo nginx interno na porta `8080`; `18789` é o Gateway em loopback dentro do mesmo container. No campo **Domains for openclaw**, configurar `https://claw.sharebook.com.br:8080`. O sufixo seleciona a porta interna e não expõe `8080` ao visitante. Depois do deploy, provar que a label `traefik.http.services.*.loadbalancer.server.port` vale `8080`; o default `80` produz `502` mesmo com container saudável.
- Estado de modelos validado em 2026-08-30: primário `openai/gpt-5.5`, fallback global `deepseek/deepseek-v4-pro`, com `DEEPSEEK_API_KEY` fornecida pelo ambiente do container. A configuração foi gravada por `openclaw models fallbacks add deepseek/deepseek-v4-pro`; não editar o JSON manualmente quando a CLI estiver disponível.
- Validar versão e config com:

```bash
openclaw --version
openclaw config validate
openclaw doctor --lint
openclaw status --deep
```

Referências: [wrapper Coolify](https://github.com/coollabsio/openclaw), [Docker upstream](https://docs.openclaw.ai/install/docker) e [configuração](https://docs.openclaw.ai/gateway/configuration).

---

## Memória semântica

A memória semântica precisa ser configurada conforme abaixo:

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        enabled: true,
        sources: ["memory"],
        provider: "openai",
        model: "text-embedding-3-small",
        fallback: "none"
      }
    }
  }
}
```

Esse é o schema da release estável `2026.7.1-2`. Documentação de versões posteriores já mostra `memory.search`; antes de migrar, consultar `openclaw config schema` na imagem realmente instalada.

Validações esperadas:

- `MEMORY.md` indexado
- arquivos em `memory/*.md` indexados
- `memory_search` funcional
- `openclaw memory status --deep --agent main` sadio; `--index` usado só se o índice precisar ser reconstruído
- busca controlada encontra um fato conhecido sem misturar transcript não autorizado

Mudança de provider, modelo, sources ou tokenizer muda a identidade do índice. Não reindexar automaticamente sem entender o impacto.

---

## Active Memory

Active Memory enriquece conversas interativas persistentes. Não roda em headless one-shot, heartbeat, cron nem subagente interno.

Config inicial recomendada:

```json5
{
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
          persistTranscripts: false,
          logging: true
        }
      }
    }
  }
}
```

O schema estável `2026.7.1-2` rejeita `config.mode`; documentação posterior já mostra `mode: "escalate"`. A release instalada manda.

Validações esperadas:

- plugin carregado no boot
- agente `main` elegível em conversa direta persistente
- `/active-memory status`, `/verbose on` e `/trace on` coerentes durante tuning
- contexto conhecido recuperado sem bloquear a resposta em caso de miss

Referência: [Active Memory oficial](https://docs.openclaw.ai/concepts/active-memory).

---

## Coolify / rede

Garanta que o container do OpenClaw tenha acesso à network interna do Coolify.

Sem isso, o agente não conseguirá acessar o PostgreSQL interno.

Network esperada:

```text
coolify
```

Host interno histórico do PostgreSQL (não reutilizar sem inspeção):

```text
fgsgwsckccgk8sccc4gg0gg0:5432
```

Atenção:

> Em novo ambiente, esse hostname pode mudar. Validar o host real do PostgreSQL no Coolify.

---

## Automação OpenClaw e cron Linux do importer

São mecanismos diferentes e devem ser validados separadamente:

- `openclaw cron` agenda wakes e rotinas agentic na release estável `2026.7.1-2`; documentação mais nova usa `openclaw automations`, então detectar pela ajuda da versão instalada. Jobs/histórico vivem no SQLite compartilhado desde 2026.6.1.
- `crontab` Linux rodava o worker Python do importer a cada 30 minutos.

Reativar um não reativa o outro. Durante o reprovisionamento:

```bash
openclaw cron status
openclaw cron list --agent main --all
crontab -l
```

Não editar `/data/.openclaw/cron/jobs.json`: ele é entrada de migração legada, não fonte canônica das releases atuais.

Defaults atuais do script canônico `sharebook-ebook-importer/setup-importer-cron.sh`:

- triagem: `*/15 0-8 * * *` em `America/Sao_Paulo`
- publicação: `5,35 * * * *`, com limite padrão de 10 itens
- locks separados por modo e log em `var/logs/importer-cron.log`

Em novo ambiente, instalar e validar:

```bash
cd /data/workspace/sharebook-ebook-importer
bash setup-importer-cron.sh install
bash setup-importer-cron.sh status
```

Também validar se o serviço de cron está ativo dentro do container ou host responsável.

---

## Checklist mínimo pós-instalação

Antes de considerar o novo ambiente pronto, validar:

- `psql` instalado
- `.NET SDK` instalado
- `Netlify CLI` instalado
- `Chrome DevTools MCP` configurado e funcional
- acesso ao PostgreSQL de produção funcionando
- endpoint da API Sharebook acessível

Itens do runtime OpenClaw:

- `coollabsio/openclaw:latest` com versão efetiva e digest registrados
- mounts persistentes de config/state, auth-profile key e workspace
- container OpenClaw conectado à network interna correta
- acesso ao PostgreSQL interno funcionando
- `openclaw config validate`, `openclaw doctor --lint` e `openclaw status --deep` sadios
- memória semântica configurada
- `memory_search` funcional
- Active Memory habilitado
- jobs OpenClaw listados e validados por run
- cron Linux do importer configurado
- cron Linux executando e registrando run no banco/log
- hook de assets públicos instalado no volume e `OPENCLAW_DOCKER_INIT_SCRIPT` preservada no serviço
- assets da Control UI retornando `200` sem credenciais, com `/` e `/browser/` ainda retornando `401`
- Control UI público e probe interno do Gateway funcionais
