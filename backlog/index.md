## BACKLOG

### 🌟 Visão Geral
- **North star do produto**: tornar o Sharebook o melhor hub de livros gratuitos do Brasil. Critérios duráveis em `playbooks/product-ux/catalog-strategy/PLAYBOOK.md`.

### 🎯 Ordem de prioridade

**Regra para débitos técnicos:** débito técnico concreto entra como item próprio no backlog, com escopo, valor, risco e validação. Não manter categoria genérica aberta como tarefa permanente.

1. **[Lista de Desejos](todo/lista-de-desejos.md)** — maior aposta de valor direto ao usuário fora da frente editorial. Transforma busca frustrada em demanda explícita e reaproveita a confiança do fluxo atual de doação; v1 conectiva, sem pagamento, com caminho natural para patrocínio/Amazon na v2. **Em execução pelo Josué (humano) — não é item livre para agentes pegarem.**
2. **[Cloudflare: CDN na frente do site, proteção DDoS e rate limit](todo/cloudflare-cdn-ddos-protection.md)** — **prioridade alta por decisão do Raffa em 2026-11-14.** É a resposta para uma divulgação grande: guarda páginas públicas e imagens na borda e tira o tráfego repetido da VPS. Substitui a V2 de capas (S3 + CloudFront, cancelada). Risco principal: o DNS. O restore drill, seu pré-requisito, foi concluído em 2026-11-14.
3. **[SSR em mais de um processo Node](todo/ssr-multiplos-processos-node.md)** — **depois da Cloudflare, por decisão do Raffa em 2026-11-14.** O teste de carga mostrou o teto de ~3 páginas novas/s porque o SSR é um processo, um núcleo (o host tem 4). Com a Cloudflare guardando as páginas, o frontend larga o cache em memória (~1,7 GiB cheio) e pode rodar em 2–3 processos sem multiplicar memória.
4. **[Investigar pool de conexões e limite real do Postgres](todo/investigar-pool-conexoes-e-limite-postgres.md)** — o `Maximum Pool Size=80` provavelmente é um número herdado, não calibrado. Investigar com dados (e um teste de estresse do Postgres fora do horário comercial, autorizado pelo Raffa mesmo que derrube o site) o pool mínimo e máximo ideais para 4 vCPU. Backup restaurável já provado pelo restore drill de 2026-11-14; repetir se a infraestrutura de backup mudar antes do teste.
5. **[Social e Reviews](todo/social/_plano.md) + [Pegasus](todo/pegasus-engagement-engine.md)** — valor ainda incerto, esforço muito alto. Adiar até existir sinal real de retenção.
6. **[Sharebook Audio — Converse com seus livros](todo/sharebook-audio-converse-com-seus-livros.md)** — valor potencialmente altíssimo, esforço e risco muito altos. Discovery antes de implementação: benchmark de um mês, catálogo juridicamente seguro, prova do loop `PLAY → PAUSE → ASK → RESUME` e unit economics desde o MVP.
7. **[Agente Sharebook — companheiro de leitura e jornadas](todo/agente-sharebook/index.md)** — valor potencialmente altíssimo, esforço e risco muito altos. Separado do Audio: começa com identidade e capacidades read-only; memória, ações e novos canais avançam apenas com jornadas comprovadas.
8. **[Expansão de sources do acervo](todo/expansao-sources-acervo.md)** — valor baixo no momento, esforço contínuo. A fila ativa já sustenta meses de processamento deliberadamente lento.
9. **[Manutenção Autônoma de Produção — Rollbar + OpenClaw](todo/manutencao-autonoma-producao-rollbar-openclaw.md)** — alto valor operacional, esforço e risco altos. Construir fluxo Rollbar → OpenClaw → investigação → patch → harness → deploy → observação → rollback, com humano como supervisor por exceção e confiança concentrada no harness.
10. **[Observabilidade Sharebook — saúde, diagnóstico e continuidade](todo/observabilidade-sharebook-epico.md)** — cerca de 45% concluído. Métricas .NET e logs Grafana Cloud/Loki já estão operacionais; faltam dashboard mínimo, correlação Rollbar + Grafana e traces (restore drill concluído em 2026-11-14) quando houver pergunta clara.
11. **[Migração dos backups GCP para AWS](todo/migracao-backups-gcp-aws.md)** — baixa urgência no curto prazo: há R$ 16,81 de crédito na GCP e gasto perto de R$ 4/mês. Retomar quando formos consolidar storage ou quando o crédito estiver perto do fim.
12. **[Footer de build-info mostra "dev-local"](todo/footer-build-info-dev-local.md)** — valor baixo, esforço baixo depois de ter o log de build real do Coolify. Bug conhecido, deliberadamente adiado pelo Raffa em 2026-09-19; movido da memória episódica pro backlog em 2026-09-20 só pra não ficar esquecido.
13. **[Busca e recomendação](todo/busca-e-recomendacao-sharebook/index.md)** — valor baixo na leitura atual do Raffa. A v1 útil já está publicada com busca lexical e recomendações pragmáticas; tolerância a erro, embeddings, re-ranking e personalização ficam no fim da fila até dados reais provarem dor relevante.
14. **[Segunda vitrine transversal](todo/segunda-vitrine-transversal.md)** — decidir só depois de 30 dias de dados de **Amores Perigosos**; cruzar desempenho real, profundidade do catálogo em português e coerência editorial antes de escolher o tema.
15. **[Pré-processamento: recomendações e páginas públicas](todo/pre-processamento-paginas-e-recomendacoes.md)** — direção decidida pelo Raffa em 2026-11-14: pré-processar, em vez de escalar a máquina para calcular sob demanda (mesclou pré-renderização, recomendações pré-processadas e o item de capacidade SSR). A forma ainda será discutida; prioridade baixa até o Raffa subir. Alto valor para SEO e estabilidade, esforço alto.
16. **[Captação de investimento recorrente](todo/captacao-investimento-recorrente.md)** — tema aberto pelo Raffa em 2026-11-17, **só para endereçar, sem execução agora e sem pressa**. Objetivo: patrocínio mensal de empresas, via associação sem fins lucrativos. Posição na fila a definir pelo Raffa. Valor potencialmente altíssimo (sustenta todo o resto), esforço alto e dependente de jurídico.

### ✅ Concluídos

Ver [done/index.md](done/index.md).

---
Para detalhes de execução de cada item, consulte o arquivo correspondente na pasta `todo/`.
