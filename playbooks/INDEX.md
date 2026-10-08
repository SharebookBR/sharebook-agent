# Inventario de Playbooks e Capacidades do Sharebook-agent

Este e o mapa mestre de descoberta do conhecimento operacional local do Sharebook-agent.

Use quando:

- o tema do pedido nao encaixar imediatamente em um playbook;
- o agente acordar apenas com `AGENTS.md` e precisar se orientar;
- uma capacidade existir, mas nao estiver obvia pelo nome do arquivo;
- Raffa apontar que algo deveria ser mais encontravel.

Regra de seguranca: este inventario pode citar nomes de variaveis do `.env`, mas nunca valores.

## Vocabulario

- **OpenClaw skill**: mecanismo/plataforma do OpenClaw.
- **Sharebook-agent playbook**: arquivo `.md` versionado neste repo para orientar agentes futuros.
- **Familia**: agrupamento de playbooks por dominio.
- **Capacidade**: acesso, credencial, integracao ou superficie operacional disponivel.

## Familias

| Familia | Indice | Quando abrir |
| --- | --- | --- |
| Runtime | `runtime/INDEX.md` | Habitat atual, paths, ferramentas, OpenClaw, Windows, Claude Code e limitacoes do runtime. |
| Engineering | `engineering/INDEX.md` | Frontend, backend, banco, analytics, Search Console, SEO, observabilidade, Prometheus/Grafana, tags e performance. |
| Infra | `infra/INDEX.md` | VPS, Coolify, deploy, containers, backups, GCP bucket, restore, dominios, proxy e migracao. |
| Importers | `importers/INDEX.md` | Fila de ebooks, triagem, publicacao, livros fisicos, categorias e producao editorial. |
| Product/UX | `product-ux/INDEX.md` | Produto, catalogo, voz, UX, direcao visual, capas e ganhador de doacao. |
| Doctrine | `doctrine/INDEX.md` | Governanca do harness, memoria, Dream, encontrabilidade e saude estrutural. |

## Playbooks primarios

### Runtime

- `runtime/windows-local.md` — Windows local do Raffa: paths, shell, encoding, Python, banco e armadilhas.
- `runtime/openclaw.md` — Container OpenClaw na VPS: Gateway, sessoes, memoria, ferramentas e operacao remota.
- `runtime/claude-code-openclaw.md` — Claude Code dentro do container OpenClaw, fora do loop de tools do Gateway.
- `runtime/claude-code-web.md` — Claude Code on the web: sandbox, GitHub App, auto mode e limites de SSH/rede.

### Engineering

- `engineering/frontend.md` — Angular, SSR, layout tecnico, componentes, interceptors e download.
- `engineering/backend.md` — .NET, API, EF Core, migrations, arquitetura hexagonal e logs de backend.
- `engineering/tag-manager.md` — tags, vocabulario, aliases, retaggear, pagina publica de tag.
- `engineering/postgres-ro/PLAYBOOK.md` — consultas read-only, auditoria de dados, schema e top lists.
- `engineering/postgres-slow-query-analysis/PLAYBOOK.md` — slow queries, `pg_stat_statements`, performance do banco.
- `engineering/analytics/PLAYBOOK.md` — GA4, GSC, funil, trafego, SEO e BI.
- `engineering/search-console-explorer/PLAYBOOK.md` — Search Console, queries organicas, CTR, impressoes, posicao e landing pages.
- `engineering/prometheus-explorer.md` — Grafana Cloud, Prometheus, OpenTelemetry, PromQL, GC, active series e cardinalidade.

### Infra

- `infra/coolify-vps.md` — Coolify, VPS, deploy, containers, logs, env vars, backup, GCP bucket, S3 storage, restore e healthcheck.
- `infra/vps-migration.md` — migracao de VPS, DNS, certificado, restore do Coolify e GitHub App source.

### Importers

- `importers/ebook-importer/PLAYBOOK.md` — fila de ebooks, triage, publish, source_blocked, retry, Gutenberg e worker.
- `importers/daily-triage-recovery/PLAYBOOK.md` — triagem do dia, recuperar itens e worker noturno.
- `importers/physical-book-importer/PLAYBOOK.md` — livro fisico, doacao, cadastro, frete e foto de capa.
- `importers/category-organizer/PLAYBOOK.md` — categorias, taxonomia, leaf category e migracoes.
- `importers/sharebook-pdf-typesetting/PLAYBOOK.md` — PDF, diagramacao, miolo, preset 4:5 e Gutenberg traduzido.
- `importers/escrever-livros/PLAYBOOK.md` — escrever livro, PDF autoral, capa autoral e manuscrito.

### Product/UX

- `product-ux/catalog-strategy/PLAYBOOK.md` — estrategia de catalogo, curadoria, sources, vitrines e qualidade percebida.
- `product-ux/art-director/PLAYBOOK.md` — arte, campanha, post, imagem gerada, banner, hero visual e marca.
- `product-ux/voice-glossary/PLAYBOOK.md` — copy, microcopy, nomenclatura, glossario, emails e labels.
- `product-ux/ux-reviewer/PLAYBOOK.md` — UX, revisao de tela, fluxo, interface e clareza.
- `product-ux/web-design-reviewer/PLAYBOOK.md` — design review, CSS, layout, responsivo e acessibilidade visual.
- `product-ux/catalog-premium-scan/PLAYBOOK.md` — scan premium, livros recentes e shortlist editorial.
- `product-ux/cover-direction/PLAYBOOK.md` — roleta, capa, paleta, direcao cromatica e geracao/troca de capa.
- `product-ux/winner-selection/PLAYBOOK.md` — escolher ganhador, doacao fisica, shortlist e solicitacoes.

### Doctrine

- `doctrine/harness-governance/PLAYBOOK.md` — harness, indice, memoria episodica, Dream, governanca, encontrabilidade e auditoria estrutural.

## Capacidades encontraveis

Nunca imprimir valores. Apenas saber onde procurar.

| Capacidade | Onde descobrir | Observacao |
| --- | --- | --- |
| GitHub push por HTTPS | `.env`: `GITHUB_PERSONAL_ACCESS_TOKEN` | Usar askpass/env seguro; nao colocar token em URL, arquivo, memoria ou log. |
| GA4 | `.env`: `GA4_PROPERTY_ID`, `GA4_KEY_FILE_PATH` | Analytics e comportamento de produto. |
| Search Console | `engineering/search-console-explorer/PLAYBOOK.md`, `.env`: `GA4_KEY_FILE_PATH` | Usa a service account do GA4; nao procurar necessariamente por `GSC_*`. |
| Grafana/Prometheus | `.env`: `GRAFANA_CLOUD_*` | PromQL read-only e OTLP write; nunca imprimir token/header. |
| VPS/Coolify | `infra/coolify-vps.md` + `.env` | Deploy, logs, containers, backups, GCP bucket e restore. |
| Postgres read-only | `engineering/postgres-ro/PLAYBOOK.md` + `.env` | Preferir scripts oficiais e consultas read-only. |
| Rollbar | backlog/epico de observabilidade | Error tracking existe; acesso API read-only ainda e desejavel se nao estiver documentado. |

## Rotas de descoberta rapida

- Search Console, GSC, indexacao, CTR, impressoes, queries organicas -> `engineering/search-console-explorer/PLAYBOOK.md`.
- GA4, funil, trafego, comportamento, downloads -> `engineering/analytics/PLAYBOOK.md`.
- Grafana, Prometheus, OpenTelemetry, metricas .NET, GC, active series, cardinalidade, PromQL -> `engineering/prometheus-explorer.md`.
- Git push/pull por HTTPS pedindo usuario -> `.env` com `GITHUB_PERSONAL_ACCESS_TOKEN`.
- Backup, restore, GCP bucket, Coolify backup, volume backup, `s3_uploaded`, lifecycle, DR -> `infra/coolify-vps.md`.
- VPS, containers, logs, deploy, Coolify -> `infra/coolify-vps.md`.
- Banco, SQL read-only, dados, top lists -> `engineering/postgres-ro/PLAYBOOK.md`.
- Slow query, `pg_stat_statements`, performance do banco -> `engineering/postgres-slow-query-analysis/PLAYBOOK.md`.
