# Arquitetura do Sharebook em alto nível

> **Status: rascunho de 2026-11-13, montado por Claude a partir dos playbooks e do incidente de 2026-11-12. Ainda não foi conferido contra o servidor.** O OpenClaw deve revisar, corrigir o que estiver errado e tirar os "A confirmar" (tarefa T6 em `backlog/todo/protecao-sobrecarga-ssr.md`). Cada afirmação aponta sua fonte para facilitar a conferência.

Este documento responde "como as peças se encaixam". Para operar cada peça, ver `coolify-vps.md` (infra), `../engineering/backend.md`, `../engineering/frontend.md` e `../engineering/grafana-cloud-explorer.md`.

## Mapa

```
 Visitante / bot / Googlebot
          │ HTTPS
          ▼
 ┌────────────────────────────────────────────  VPS HostGator (Coolify)  ──────┐
 │  coolify-proxy (Traefik)                                                      │
 │          │                                                                    │
 │          ▼                                                                    │
 │  sharebook-frontend  ── Angular + SSR (Node/Express), 1 réplica               │
 │   • cache SSR em memória: home e /livros/:slug, 30 min                        │
 │   • limite de renderizações simultâneas (30 total, 18 bots) → 503 imediato    │
 │   • timeout de 4 s por chamada à API; página degradada não é cacheada         │
 │          │ HTTP (https://api.sharebook.com.br/api)                            │
 │          ▼                                                                    │
 │  sharebook-api  ── .NET 10, arquitetura hexagonal, 1 réplica                  │
 │   • IMemoryCache (ex.: contagem de categorias, recomendações)                 │
 │   • jobs executados pela própria API (JobExecutor / JobHistories)             │
 │          │ Npgsql (pool 80, Timeout=5, Command Timeout=15)                    │
 │          ▼                                                                    │
 │  Postgres da aplicação (postgres:17-alpine, nome aleatório, max_connections 100)
 │                                                                               │
 │  Importador de e-books ── banco PRÓPRIO, isolado (sem JOIN com o banco da app)│
 │  coolify, coolify-db (postgres:15), coolify-redis, coolify-realtime,          │
 │  coolify-sentinel  ── painel e suporte do Coolify                             │
 │  OpenClaw ── agente residente na mesma VPS                                    │
 └───────────────────────────────────────────────────────────────────────────────┘
        │                         │                         │
        ▼                         ▼                         ▼
   Grafana Cloud              Rollbar                  GA4 / Search Console
 (métricas e logs da API       (erros da API)           (audiência e SEO)
  via OTLP; logs do SSR)
```

## Peças

| Peça | O que é | Fonte |
|---|---|---|
| VPS | HostGator desde 17/08/2026; a da Hostinger foi desprovisionada. Prefixo de acesso `VPS_HOSTGATOR_SSH_*` | `coolify-vps.md` |
| Orquestração | Coolify, que gera nomes aleatórios de container e faz deploy automático ao receber push na `master` | `coolify-vps.md`, `backlog/done/deploy-automatico-github-coolify-pos-migracao.md` |
| Proxy | Traefik (`coolify-proxy`); access log **desligado** | `protecao-sobrecarga-ssr.md` (T3) |
| Frontend | Angular com SSR; cache de 30 min para home e PDP; `ssr_access` e `ssr_overloaded` em JSON no stdout | `frontend.md` |
| API | .NET 10, hexagonal; Serilog com sink OTLP para o Grafana Cloud (`ClientIp`, `UserAgent` em todo log de request) | `backend.md` |
| Banco da app | `postgres:17-alpine`. **Achar pela imagem, não pelo nome**; o `coolify-db` é outro Postgres | `coolify-vps.md` |
| Banco do importador | Isolado do da app. Composição de dados na camada de serviço, em lote | `backend.md` |
| Armazenamento | E-books por URL assinada (S3); imagens em volume `wwwroot` com backup de diretório; backups no GCP, migração para AWS planejada | `frontend.md`, `coolify-vps.md`, `backlog/todo/migracao-backups-gcp-aws.md` |
| Erros | Rollbar (alertas por e-mail; **sem acesso de leitura pelo OpenClaw**) | incidente 2026-11-12 |
| Observabilidade | Grafana Cloud: Prometheus/Mimir (métricas .NET) e Loki (logs da API e, desde 2026-11-12, do frontend) | `grafana-cloud-explorer.md`, `observabilidade-sharebook-epico.md` |
| Repositórios | `sharebook-frontend`, `sharebook-backend`, `sharebook-ebook-importer`, `sharebook-agent` (backlog, playbooks, memória) | — |
| Agentes | Claude Code (web e Windows) e OpenClaw (VPS). O Raffa é o mensageiro entre eles; o canal é o backlog | `AGENTS.md`, `backlog/todo/canal-claude-openclaw.md` |

## Caminho de uma requisição de página de livro

1. Traefik entrega `/livros/:slug` ao frontend.
2. **Cache HIT:** responde na hora, sem Angular e sem API.
3. **MISS:** o SSR chama a API (`book/Slug`, depois `book/Recommendations`; `category/Counts` e `freightOptions` são cache e memória). Se passar do limite de renderizações simultâneas, responde 503.
4. A API consulta o Postgres. Cada renderização usa ~1 conexão por vez.
5. Se uma chamada falhar ou passar de 4 s, a página sai incompleta (sem recomendações) com `no-store`; se o livro em si falhar, responde 503 com `Retry-After`, nunca 404.
6. Resposta 200 e completa entra no cache por 30 min.

## Limites que importam (e por quê)

- **Uma réplica de frontend e uma de API.** O limite de concorrência do SSR é, portanto, global.
- **Pool Npgsql 80 contra `max_connections` 100**: margem de 20 para administração. O incidente de 2026-11-12 foi a fila de 215 requisições de banco contra esse pool de 80.
- **Cache de recomendações** (10 min) e **cache SSR** (30 min): dados podem ficar defasados por esse tempo.
- **Logs do SSR somem em restart de container** se não estiverem no Loki.

## A confirmar (para o OpenClaw)

- [ ] O SSR chama a API pelo endereço público (`https://api.sharebook.com.br/api`) e passa pelo Traefik, ou há rota interna?
- [ ] Os jobs rodam dentro do container da API, ou há um container separado (`Sharebook.Jobs`)? Compartilham a mesma connection string?
- [ ] Onde ficam de fato as imagens (volume local, S3, CDN) e onde os PDFs/e-books?
- [ ] Lista real de containers em produção (`docker ps`), com função de cada um, e quais têm volume persistente.
- [ ] O que o `coolify-sentinel` coleta (CPU e memória por container?) e onde isso aparece.
- [ ] Como o deploy é disparado (webhook do GitHub, GitHub App) e quanto tempo costuma levar do push ao container novo.
- [ ] Existe mais de um servidor, ou tudo está nessa VPS?
- [ ] Onde ficam os backups hoje e qual foi o último restore drill.
