## BACKLOG

### 🌟 Visão Geral
- **North star do produto**: tornar o Sharebook o melhor hub de livros gratuitos do Brasil. Critérios duráveis em `playbooks/product-ux/catalog-strategy/PLAYBOOK.md`.

### 🎯 Ordem de prioridade

**Regra para débitos técnicos:** débito técnico concreto entra como item próprio no backlog, com escopo, valor, risco e validação. Não manter categoria genérica aberta como tarefa permanente.

1. **[Lista de Desejos](todo/lista-de-desejos.md)** — maior aposta de valor direto ao usuário fora da frente editorial. Transforma busca frustrada em demanda explícita e reaproveita a confiança do fluxo atual de doação; v1 conectiva, sem pagamento, com caminho natural para patrocínio/Amazon na v2. **Em execução pelo Josué (humano) — não é item livre para agentes pegarem.**
2. **[Teste de carga SSR de origem externa e investigação de memória/swap do host](todo/teste-carga-ssr-origem-externa.md)** — alta prioridade de evidência. O V2 validou os limites 6/3 sem 500, mas saiu da própria VPS e terminou por 10 s de swap I/O intenso. Um só teste, de fora da VPS, prova o caminho real e atribui a pressão de memória antes de subir capacidade (item mesclado em 2026-11-14).
3. **[Capacidade SSR: VPS, réplicas ou pré-renderização](todo/capacidade-ssr-vps-replicas-pre-renderizacao.md)** — decisão estrutural após a medição externa. Liga custo de infraestrutura à solução de longo prazo sem abandonar a pré-renderização.
4. **[Investigar pool de conexões e limite real do Postgres](todo/investigar-pool-conexoes-e-limite-postgres.md)** — o `Maximum Pool Size=80` provavelmente é um número herdado, não calibrado. Investigar com dados (e um teste de estresse do Postgres fora do horário comercial, autorizado pelo Raffa mesmo que derrube o site) o pool mínimo e máximo ideais para 4 vCPU. Antes do teste, confirmar backup restaurável.
5. **[Proxy do docker.sock antes de ampliar Alloy](todo/proxy-docker-sock-antes-de-ampliar-alloy.md)** — hardening obrigatório antes de coletar além do frontend; `:ro` não restringe a API Docker.
6. **[Restore drill controlado dos backups](todo/restore-drill-backups.md)** — backup remoto está comprovado, restore ainda não.
7. **[Teste HTTP automatizado do limitador SSR](todo/teste-http-automatizado-limitador-ssr.md)** — fecha em CI os contratos 503/Retry-After, HIT e coalescimento.
8. **[Observabilidade do onboarding por e-mail](todo/observabilidade-onboarding-email.md)** — medir abertura rastreável e clique por etapa no PostgreSQL, com painel administrativo. V1 deliberadamente sem GA4: pixel, redirect e telemetria própria dão o funil que importa.
9. **[Social e Reviews](todo/social/_plano.md) + [Pegasus](todo/pegasus-engagement-engine.md)** — valor ainda incerto, esforço muito alto. Adiar até existir sinal real de retenção.
10. **[Sharebook Audio — Converse com seus livros](todo/sharebook-audio-converse-com-seus-livros.md)** — valor potencialmente altíssimo, esforço e risco muito altos. Discovery antes de implementação: benchmark de um mês, catálogo juridicamente seguro, prova do loop `PLAY → PAUSE → ASK → RESUME` e unit economics desde o MVP.
11. **[Agente Sharebook — companheiro de leitura e jornadas](todo/agente-sharebook/index.md)** — valor potencialmente altíssimo, esforço e risco muito altos. Separado do Audio: começa com identidade e capacidades read-only; memória, ações e novos canais avançam apenas com jornadas comprovadas.
12. **[Expansão de sources do acervo](todo/expansao-sources-acervo.md)** — valor baixo no momento, esforço contínuo. A fila ativa já sustenta meses de processamento deliberadamente lento.
13. **[Capas v2 — S3 + CDN](todo/pipeline-capas-s3-cdn.md)** — valor baixo na escala atual, esforço alto. As thumbnails locais reduziram em 94,8% o peso das capas da home; retomar storage externo quando escala, custo ou operação justificarem.
14. **[Cloudflare: CDN + DDoS](todo/cloudflare-cdn-ddos-protection.md)** — baixo valor na escala atual, esforço médio. Retomar quando tráfego ou risco justificarem.
15. **[Manutenção Autônoma de Produção — Rollbar + OpenClaw](todo/manutencao-autonoma-producao-rollbar-openclaw.md)** — alto valor operacional, esforço e risco altos. Construir fluxo Rollbar → OpenClaw → investigação → patch → harness → deploy → observação → rollback, com humano como supervisor por exceção e confiança concentrada no harness.
16. **[Observabilidade Sharebook — saúde, diagnóstico e continuidade](todo/observabilidade-sharebook-epico.md)** — cerca de 45% concluído. Métricas .NET e logs Grafana Cloud/Loki já estão operacionais; faltam dashboard mínimo, correlação Rollbar + Grafana, restore drill e traces quando houver pergunta clara.
17. **[Migração dos backups GCP para AWS](todo/migracao-backups-gcp-aws.md)** — baixa urgência no curto prazo: há R$ 16,81 de crédito na GCP e gasto perto de R$ 4/mês. Retomar quando formos consolidar storage ou quando o crédito estiver perto do fim.
18. **[Footer de build-info mostra "dev-local"](todo/footer-build-info-dev-local.md)** — valor baixo, esforço baixo depois de ter o log de build real do Coolify. Bug conhecido, deliberadamente adiado pelo Raffa em 2026-09-19; movido da memória episódica pro backlog em 2026-09-20 só pra não ficar esquecido.
19. **[Busca e recomendação](todo/busca-e-recomendacao-sharebook/index.md)** — valor baixo na leitura atual do Raffa. A v1 útil já está publicada com busca lexical e recomendações pragmáticas; tolerância a erro, embeddings, re-ranking e personalização ficam no fim da fila até dados reais provarem dor relevante.
20. **[Segunda vitrine transversal](todo/segunda-vitrine-transversal.md)** — decidir só depois de 30 dias de dados de **Amores Perigosos**; cruzar desempenho real, profundidade do catálogo em português e coerência editorial antes de escolher o tema.
21. **[Pré-renderização das páginas públicas](todo/pre-renderizacao-paginas-publicas.md)** — alto valor para SEO e estabilidade, esforço alto. Solução estrutural contra renderização on-demand sob crawler; `protecao-sobrecarga-ssr.md` é a rede de proteção até lá. Retomar se o tráfego de crawler crescer ou o limite começar a recusar o Googlebot.
22. **[Recomendações pré-processadas](todo/recomendacoes-pre-processadas.md)** — baixa urgência; solução ainda a discutir com o Raffa. Hoje cada visita a um livro fora do cache recalcula as recomendações (~190 ms de CPU na API, medido em 2026-11-13). A direção desejada é pré-processar; escopo e forma não estão decididos.

### ✅ Concluídos

Ver [done/index.md](done/index.md).

---
Para detalhes de execução de cada item, consulte o arquivo correspondente na pasta `todo/`.
