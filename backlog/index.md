## BACKLOG

### 🌟 Visão Geral
- **North star do produto**: tornar o Sharebook o melhor hub de livros gratuitos do Brasil. Critérios duráveis em `skills/product-ux/catalog-strategy/SKILL.md`.

### 🎯 Ordem de prioridade

Revisada em **2026-10-05**, após decisão do Raffa de tratar **Bruxas & Magia** como a frente de maior valor atual, mover **Tags e conhecimento estruturado** para done e rebaixar **Busca e recomendação** para o fim da fila.

**Regra para débitos técnicos:** débito técnico concreto entra como item próprio no backlog, com escopo, valor, risco e validação. Não manter categoria genérica aberta como tarefa permanente.

1. **[Vitrine Bruxas & Magia](todo/vitrine-bruxas-e-magia.md)** — top 1 atual por decisão do Raffa em 2026-10-05. A frente já provou tração editorial com livros publicados, pipeline Gutenberg/tradução/capa/PDF em funcionamento e uma categoria temática com identidade clara.
2. **[Lista de Desejos](todo/lista-de-desejos.md)** — maior aposta de valor direto ao usuário fora da frente editorial. Transforma busca frustrada em demanda explícita e reaproveita a confiança do fluxo atual de doação; v1 conectiva, sem pagamento, com caminho natural para patrocínio/Amazon na v2. **Em execução pelo Josué (humano) — não é item livre para agentes pegarem.**
3. **[Home v2 — mais baixados e vitrines temáticas](todo/home-v2-curadoria-ranking.md)** — entregue em 2026-09-10. A Home ganhou a prateleira "Mais baixados" com `BookDownloadEvent`, `UserId` opcional via JWT, backfill GA4 de 30 dias e cache SSR preservado; agora fica em observação de clique/download.
4. **[Social e Reviews](todo/social/_plano.md) + [Pegasus](todo/pegasus-engagement-engine.md)** — valor ainda incerto, esforço muito alto. Adiar até existir sinal real de retenção.
5. **[Sharebook Audio — Converse com seus livros](todo/sharebook-audio-converse-com-seus-livros.md)** — valor potencialmente altíssimo, esforço e risco muito altos. Discovery antes de implementação: benchmark de um mês, catálogo juridicamente seguro, prova do loop `PLAY → PAUSE → ASK → RESUME` e unit economics desde o MVP.
6. **[Agente Sharebook — companheiro de leitura e jornadas](todo/agente-sharebook/index.md)** — valor potencialmente altíssimo, esforço e risco muito altos. Separado do Audio: começa com identidade e capacidades read-only; memória, ações e novos canais avançam apenas com jornadas comprovadas.
7. **[Expansão de sources do acervo](todo/expansao-sources-acervo.md)** — valor baixo no momento, esforço contínuo. A fila ativa já sustenta meses de processamento deliberadamente lento.
8. **[Capas v2 — S3 + CDN](todo/pipeline-capas-s3-cdn.md)** — valor baixo na escala atual, esforço alto. As thumbnails locais reduziram em 94,8% o peso das capas da home; retomar storage externo quando escala, custo ou operação justificarem.
9. **[Cloudflare: CDN + DDoS](todo/cloudflare-cdn-ddos-protection.md)** — baixo valor na escala atual, esforço médio. Retomar quando tráfego ou risco justificarem.
10. **[Manutenção Autônoma de Produção — Rollbar + OpenClaw](todo/manutencao-autonoma-producao-rollbar-openclaw.md)** — alto valor operacional, esforço e risco altos. Construir fluxo Rollbar → OpenClaw → investigação → patch → harness → deploy → observação → rollback, com humano como supervisor por exceção e confiança concentrada no harness.
11. **[Aposentadoria completa do facilitador](todo/aposentadoria-completa-facilitador.md)** — valor baixo após a retirada da experiência visível, esforço médio. Fechar domínio, banco, jobs, contratos e documentação numa rodada própria.
12. **[Unificação Scripts + Renomeação do Corpus](todo/unificacao-scripts-memory-durable.md)** — baixo valor para produto, esforço médio. Não competir com trabalho de produto e operação.
13. **[SMTP próprio com Stalwart](todo/smtp-proprio-stalwart.md)** — economia potencial, esforço e risco operacional médios. Retomar quando o custo do provedor justificar PTR próprio, aquecimento de reputação e desacoplamento SMTP/IMAP dos bounces.
14. **[Migração dos backups GCP para AWS](todo/migracao-backups-gcp-aws.md)** — baixa urgência no curto prazo: há R$ 16,81 de crédito na GCP e gasto perto de R$ 4/mês. Retomar quando formos consolidar storage ou quando o crédito estiver perto do fim.
15. **[Footer de build-info mostra "dev-local"](todo/footer-build-info-dev-local.md)** — valor baixo, esforço baixo depois de ter o log de build real do Coolify. Bug conhecido, deliberadamente adiado pelo Raffa em 2026-09-19; movido da memória episódica pro backlog em 2026-09-20 só pra não ficar esquecido.
16. **[Update de ebook não troca o PDF](todo/fix-update-ebook-nao-troca-pdf.md)** — valor médio, esforço baixo. `BookService.UpdateAsync` ignora `PdfBytes` e responde sucesso; hoje trocar PDF exige sobrescrever no S3. Achado pelo OpenClaw em 2026-09-27, causa confirmada no código.
17. **[Categoria "Matemática & Lógica"](todo/revisao-escopo-matematica-corredor-tecnologia.md)** — valor médio, esforço baixo a médio. **Executada no banco em 2026-10-02 e verificação pública fechada em 2026-10-05**: raiz com 50 livros, 6 subcategorias com contagens corretas, Home e páginas públicas OK; decisões curatoriais fechadas.
18. **[Devroye cadastrado como errata](todo/fix-devroye-errata-cadastrada-como-livro.md)** — bug de qualidade de catálogo: `Non-Uniform Random Variate Generation` promete o livro completo, mas o PDF público confirmado tem 7 páginas e é uma corrigenda/errata. Pode frustrar fortemente o usuário; corrigir por substituição do asset, remoção/cancelamento ou representação honesta do objeto.
19. **[Busca e recomendação](todo/busca-e-recomendacao-sharebook/index.md)** — valor baixo na leitura atual do Raffa. A v1 útil já está publicada com busca lexical e recomendações pragmáticas; tolerância a erro, embeddings, re-ranking e personalização ficam no fim da fila até dados reais provarem dor relevante.

### ✅ Done relevante

- **[Tags e conhecimento estruturado](done/tags-e-conhecimento-estruturado/index.md)** — missão cumprida em 2026-10-03. Entregou vocabulário controlado, modelo, navegação pública, motor mecânico na criação de livros, backfill técnico controlado e skill operacional; a antiga Tarefa 7 foi cancelada por falta de valor percebido.


---
Para detalhes de execução de cada item, consulte o arquivo correspondente na pasta `todo/`.
