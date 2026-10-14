## BACKLOG

### 🌟 Visão Geral
- **North star do produto**: tornar o Sharebook o melhor hub de livros gratuitos do Brasil. Critérios duráveis em `playbooks/product-ux/catalog-strategy/PLAYBOOK.md`.

### 🎯 Ordem de prioridade

Revisada em **2026-10-12**, após restaurar a tool dinâmica `memory_search` do OpenClaw. O bloqueio era estado velho no Gateway; CLI e índice estavam saudáveis, e restart controlado resolveu. Validação final: `memory_search` e `memory_get` funcionando, índice `280/280`, `Dirty: no`.

**Regra para débitos técnicos:** débito técnico concreto entra como item próprio no backlog, com escopo, valor, risco e validação. Não manter categoria genérica aberta como tarefa permanente.

1. **[Lista de Desejos](todo/lista-de-desejos.md)** — maior aposta de valor direto ao usuário fora da frente editorial. Transforma busca frustrada em demanda explícita e reaproveita a confiança do fluxo atual de doação; v1 conectiva, sem pagamento, com caminho natural para patrocínio/Amazon na v2. **Em execução pelo Josué (humano) — não é item livre para agentes pegarem.**
2. **[Social e Reviews](todo/social/_plano.md) + [Pegasus](todo/pegasus-engagement-engine.md)** — valor ainda incerto, esforço muito alto. Adiar até existir sinal real de retenção.
3. **[Sharebook Audio — Converse com seus livros](todo/sharebook-audio-converse-com-seus-livros.md)** — valor potencialmente altíssimo, esforço e risco muito altos. Discovery antes de implementação: benchmark de um mês, catálogo juridicamente seguro, prova do loop `PLAY → PAUSE → ASK → RESUME` e unit economics desde o MVP.
4. **[Agente Sharebook — companheiro de leitura e jornadas](todo/agente-sharebook/index.md)** — valor potencialmente altíssimo, esforço e risco muito altos. Separado do Audio: começa com identidade e capacidades read-only; memória, ações e novos canais avançam apenas com jornadas comprovadas.
5. **[Expansão de sources do acervo](todo/expansao-sources-acervo.md)** — valor baixo no momento, esforço contínuo. A fila ativa já sustenta meses de processamento deliberadamente lento.
6. **[Capas v2 — S3 + CDN](todo/pipeline-capas-s3-cdn.md)** — valor baixo na escala atual, esforço alto. As thumbnails locais reduziram em 94,8% o peso das capas da home; retomar storage externo quando escala, custo ou operação justificarem.
7. **[Cloudflare: CDN + DDoS](todo/cloudflare-cdn-ddos-protection.md)** — baixo valor na escala atual, esforço médio. Retomar quando tráfego ou risco justificarem.
8. **[Manutenção Autônoma de Produção — Rollbar + OpenClaw](todo/manutencao-autonoma-producao-rollbar-openclaw.md)** — alto valor operacional, esforço e risco altos. Construir fluxo Rollbar → OpenClaw → investigação → patch → harness → deploy → observação → rollback, com humano como supervisor por exceção e confiança concentrada no harness.
9. **[Observabilidade Sharebook — saúde, diagnóstico e continuidade](todo/observabilidade-sharebook-epico.md)** — cerca de 45% concluído. Métricas .NET e logs Grafana Cloud/Loki já estão operacionais; faltam dashboard mínimo, correlação Rollbar + Grafana, restore drill e traces quando houver pergunta clara.
10. **[SMTP próprio com Stalwart](todo/smtp-proprio-stalwart.md)** — economia potencial, esforço e risco operacional médios. Retomar quando o custo do provedor justificar PTR próprio, aquecimento de reputação e desacoplamento SMTP/IMAP dos bounces.
11. **[Migração dos backups GCP para AWS](todo/migracao-backups-gcp-aws.md)** — baixa urgência no curto prazo: há R$ 16,81 de crédito na GCP e gasto perto de R$ 4/mês. Retomar quando formos consolidar storage ou quando o crédito estiver perto do fim.
12. **[Footer de build-info mostra "dev-local"](todo/footer-build-info-dev-local.md)** — valor baixo, esforço baixo depois de ter o log de build real do Coolify. Bug conhecido, deliberadamente adiado pelo Raffa em 2026-09-19; movido da memória episódica pro backlog em 2026-09-20 só pra não ficar esquecido.
13. **[Update de ebook não troca o PDF](todo/fix-update-ebook-nao-troca-pdf.md)** — valor médio, esforço baixo. `BookService.UpdateAsync` ignora `PdfBytes` e responde sucesso; hoje trocar PDF exige sobrescrever no S3. Achado pelo OpenClaw em 2026-09-27, causa confirmada no código.
14. **[Categoria "Matemática & Lógica"](todo/revisao-escopo-matematica-corredor-tecnologia.md)** — valor médio, esforço baixo a médio. **Executada no banco em 2026-10-02 e verificação pública fechada em 2026-10-05**: raiz com 50 livros, 6 subcategorias com contagens corretas, Home e páginas públicas OK; decisões curatoriais fechadas.
15. **[Busca e recomendação](todo/busca-e-recomendacao-sharebook/index.md)** — valor baixo na leitura atual do Raffa. A v1 útil já está publicada com busca lexical e recomendações pragmáticas; tolerância a erro, embeddings, re-ranking e personalização ficam no fim da fila até dados reais provarem dor relevante.

### ✅ Done relevante

- **[Tags e conhecimento estruturado](done/tags-e-conhecimento-estruturado/index.md)** — missão cumprida em 2026-10-03. Entregou vocabulário controlado, modelo, navegação pública, motor mecânico na criação de livros, backfill técnico controlado e playbook operacional; a antiga Tarefa 7 foi cancelada por falta de valor percebido.
- **[Aposentadoria completa do facilitador](done/aposentadoria-completa-facilitador.md)** — concluída em 2026-10-14. Removeu o conceito do backend, frontend, jobs/e-mails e scripts/playbooks; a migração retira `Books.UserIdFacilitator` e **renomeia `FacilitatorNotes` para `AdminNotes`** (os comentários da administração foram mantidos). A primeira versão sem Designer não rodou e a corrigida derrubou a API por ~27 min (índice inexistente em produção); resolvido por hotfix idempotente, detalhes no arquivo.
- **[Unificação de Scripts e Renomeação do Corpus](done/unificacao-scripts-e-renomeacao-corpus.md)** — concluída em 2026-10-14. Scripts passaram a morar junto dos playbooks que os explicam; a memória episódica vive em `sessions/`. A ideia de nomear as pastas `memory-durable/` e `memory-episodic/` foi desistida pelo Raffa.
- **[Vitrine Bruxas & Magia](done/vitrine-bruxas-e-magia.md)** — frente editorial fechada em 2026-10-14. Validou pipeline Gutenberg/tradução/capa/PDF, categoria temática e vitrine com identidade clara.
- **[Home v2 — mais baixados e vitrines temáticas](done/home-v2-curadoria-ranking.md)** — concluída em 2026-10-14. Entregou a prateleira "Mais baixados", `BookDownloadEvent`, backfill GA4, endpoint público e cache SSR preservado.
- **[Restaurar índice de memória do OpenClaw](done/restaurar-indice-de-memoria.md)** — concluído em 2026-10-12. O índice e a CLI estavam saudáveis; a tool dinâmica `memory_search` falhava por estado velho do Gateway com `401 token_expired`. Restart controlado resolveu; `memory_search`/`memory_get` voltaram e a CLI confirmou `280/280`, `Dirty: no`.
- **[Laboratório Sharebook — observabilidade .NET por 24h](done/observabilidade-dotnet-laboratorio-24h.md)** — concluído em 2026-10-12. A POC provou valor e virou stack mínima permanente: métricas OTLP/Grafana Cloud, logs Loki, playbook `grafana-cloud-explorer.md` e helper compacto de consulta.
- **[Devroye cadastrado como errata](done/fix-devroye-errata-cadastrada-como-livro.md)** — removido do catálogo público em 2026-10-05. `Non-Uniform Random Variate Generation` prometia o livro completo, mas o PDF publicado era uma corrigenda/errata de 7 páginas.


---
Para detalhes de execução de cada item, consulte o arquivo correspondente na pasta `todo/`.
