# Arquitetura do Sharebook em alto nível

> **Conferido no servidor em 2026-11-13.** Esta é uma fotografia operacional; versões, containers e capacidades de observabilidade devem ser rechecados antes de uma intervenção.

Este documento explica como as peças se encaixam. Para operá-las, ver `coolify-vps.md`, `../engineering/backend.md`, `../engineering/frontend.md` e `../engineering/grafana-cloud-explorer.md`.

## Mapa

```
 Visitante / bot / Googlebot
          │ HTTPS
          ▼
 ┌──────────────────────────────────────────── VPS HostGator / Coolify ───────┐
 │ coolify-proxy (Traefik)                                                      │
 │          │                                                                    │
 │          ├── www.sharebook.com.br ──► sharebook-frontend                     │
 │          │       Angular + SSR (Node), 1 réplica, sem volume                 │
 │          │       • cache SSR em memória: home e /livros/:slug, 30 min        │
 │          │       • limite: 30 renders / 18 bots; timeout API de 4 s          │
 │          │       • 503 e no-store para render degradado/sobrecarregado       │
 │          │                                                                    │
 │          └── api.sharebook.com.br ──► sharebook-api                          │
 │                  .NET 10, 1 réplica; jobs no próprio processo                │
 │                  • IMemoryCache (inclui recomendações)                       │
 │                  • Npgsql: pool 80, Timeout=5, Command Timeout=15            │
 │                         │                                                      │
 │                         ▼                                                      │
 │                  Postgres da aplicação (postgres:17-alpine)                  │
 │                  dados Sharebook; volume Docker persistente                  │
 │                                                                              │
 │ Capas: bind local em /app/wwwroot/Images/Books                              │
 │ PDFs/e-books: S3, entregues por URL pré-assinada                              │
 │                                                                              │
 │ Coolify + coolify-db + Redis + Sentinel coordenam a plataforma.              │
 │ OpenClaw e seu browser sidecar dividem a mesma VPS; importador é separado.   │
 └──────────────────────────────────────────────────────────────────────────────┘
          │                         │                         │
          ▼                         ▼                         ▼
   Grafana Cloud              Rollbar                  GA4 / Search Console
  métricas/logs API;          alertas de erro            audiência e SEO
  logs SSR via shipper
```

O frontend usa `https://api.sharebook.com.br/api` também no bundle de produção do SSR; portanto essa chamada sai pelo domínio público e pelo Traefik, não por uma rota Docker interna.

## Componentes verificados

| Peça | Estado observado | Evidência / fonte |
|---|---|---|
| VPS | Produção na HostGator; prefixo operacional `VPS_HOSTGATOR_SSH_*` | `coolify-vps.md` e inspeção de 2026-11-13 |
| Orquestração | Coolify 4.7.5; `sharebook-api` e `sharebook-frontend` vêm de `master` usando a source `App\\Models\\GithubApp` | banco do Coolify, 2026-11-13 |
| Proxy | Traefik (`coolify-proxy`) | `docker ps`, 2026-11-13 |
| Frontend | Angular SSR em Node, uma réplica (`swarm_replicas=1`); imagem `c526152`; sem mount persistente | `docker ps`/`inspect`, 2026-11-13 |
| API | .NET, uma réplica (`swarm_replicas=1`); imagem `6d4f2cb`; `JobExecutor` é registrado no processo da API | `docker ps`, backend e logs, 2026-11-13 |
| Banco da app | `postgres:17-alpine`, container de nome gerado; não confundir com `coolify-db` (`postgres:15-alpine`) | `coolify-vps.md` e `docker ps` |
| Jobs | Não há container `Sharebook.Jobs`. O endpoint/serviço `JobExecutor` da API usa os repositórios EF do banco Sharebook, portanto usa `PostgresConnection`; o painel do importador usa adicionalmente `ImporterPostgresConnection` para seu banco isolado | `OperationsController`, `DatabaseConfiguration.cs`, `ImporterDashboardService.cs` |
| Imagens | Capas em volume local: o único mount da API é `Images/Books` para `/app/wwwroot/Images/Books` | `docker inspect sharebook-api`, 2026-11-13 |
| E-books | PDFs ficam no S3 de e-books e são servidos por URL pré-assinada; não ficam no volume de capas | `frontend.md`, script S3 compartilhado |
| Observabilidade | API envia métricas e logs por OTLP ao Grafana Cloud. O frontend é coletado pelo shipper Python provisório; a migração para Alloy está pendente na T5 | `grafana-cloud-explorer.md`, backlog de sobrecarga |
| Erros | Rollbar recebe alertas; este runtime não tem leitura autenticada da conta | incidente 2026-11-12 |

## Caminho de uma página de livro

1. Traefik entrega `/livros/:slug` ao frontend.
2. Em cache HIT, o frontend responde sem renderizar nem chamar a API.
3. Em MISS, o SSR chama a API pública: `book/Slug`, depois `book/Recommendations`; contagens de categoria e `freightOptions` são atendidos por cache/memória quando aplicável.
4. A API consulta o Postgres. Uma renderização normalmente ocupa uma conexão de cada vez.
5. Falha ou espera acima de 4 s na chamada à API torna a página degradada e `no-store`; falha do livro essencial responde 503 com `Retry-After`, não 404.
6. Uma resposta completa 200 entra no cache SSR por 30 min.

## Limites relevantes

- Há uma réplica de frontend e uma de API: os limites de SSR são globais no estado atual.
- O pool Npgsql é 80 e o Postgres aceita 100 conexões. `Timeout=5` e `Command Timeout=15` foram aplicados em 2026-11-12 e ainda exigem observação dos jobs noturnos.
- Cache de recomendações dura 10 min; cache SSR, 30 min. Essa é a janela máxima esperada de defasagem desses dados.
- Os logs do frontend eram voláteis antes do shipper atual; ainda não devem ser tratados como mecanismo de retenção de longo prazo até a troca por Alloy.

## Containers em execução na VPS em 2026-11-13

| Grupo | Containers |
|---|---|
| Sharebook | `sharebook-frontend`, `sharebook-api`, Postgres da app (`postgres:17-alpine`, nome gerado) |
| Plataforma Coolify | `coolify`, `coolify-db`, `coolify-redis`, `coolify-sentinel`, `coolify-proxy` |
| Outros workloads residentes | OpenClaw + browser sidecar, Stalwart, Filebrowser, Pegasus Core, Simula Plus e um container de serviço com nome gerado |

Volumes relevantes: Postgres da aplicação e `coolify-db` usam volumes Docker; a API monta somente o diretório de capas; Coolify monta seus diretórios de aplicações, bancos, serviços, backups e chaves; OpenClaw, Redis e Stalwart têm volumes próprios. O Sentinel tem acesso ao socket Docker e envia dados periodicamente ao Coolify. A inspeção confirmou o envio a cada minuto, mas não confirmou quais séries/campos o painel retém; não tratá-lo ainda como fonte de métricas de container equivalente ao Grafana.

## Deploy

Pushes para `master` são recebidos pelo GitHub App configurado no Coolify. A evidência de publicação é sempre tripla: entrada concluída em `application_deployment_queues`, container saudável com o SHA esperado e verificação funcional. Em 2026-11-13, a publicação do frontend `c526152` já estava saudável; o container iniciou às 21:38 UTC de 2026-11-12. Não há uma duração canônica estável de deploy registrada: Angular SSR pode levar alguns minutos e deve ser acompanhado pela fila, não estimado.

## Backups e restore

- Bancos Sharebook e o volume de capas têm backup diário pelo Coolify; a última execução observada foi 2026-11-13 03:00 UTC e os arquivos tiveram tamanhos coerentes.
- O backup do volume de capas estava configurado para armazenamento remoto e a última execução confirmou `s3_uploaded=true` (~1,23 GB). O destino é GCS pela interface S3-compatível do Coolify, com lifecycle de 60 dias; a migração para AWS continua apenas planejada.
- Não há evidência versionada de um restore drill controlado concluído. Ele permanece pendente no backlog de observabilidade/migração e é condição diferente de backup `success`.

## Itens antes “A confirmar” — resolução

- [x] **Rota SSR → API:** endereço público `https://api.sharebook.com.br/api`, passando pelo Traefik.
- [x] **Jobs:** executam no processo da API; não existe container separado. Os jobs do Sharebook usam a `PostgresConnection` do `ApplicationDbContext`; o dashboard do importador também acessa seu banco separado pela `ImporterPostgresConnection`.
- [x] **Imagens e PDFs:** capas no bind local da API; e-books no S3 por URL pré-assinada.
- [x] **Containers e volumes:** inventário e mounts relevantes acima, conferidos com `docker ps` e `docker inspect`.
- [~] **Sentinel:** confirmou-se que tem socket Docker e faz push a cada minuto para a API interna do Coolify; o conjunto exato de métricas e a retenção não foram verificados.
- [x] **Deploy:** GitHub App do Coolify para `master`; validar pela fila + container + endpoint. A duração varia e não deve ser presumida.
- [x] **Servidores:** esta topologia de produção está em uma VPS HostGator; não foi encontrada segunda VPS de produção nesta conferência.
- [~] **Último restore drill:** nenhuma evidência de drill concluído foi encontrada; permanece pendente, não deve ser deduzido de backups saudáveis.
