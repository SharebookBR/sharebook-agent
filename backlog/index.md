## BACKLOG

### 🌟 Visão Geral
- **North star do produto**: tornar o Sharebook o melhor hub de livros gratuitos do Brasil. Critérios duráveis em `skills/product-ux/catalog-strategy/SKILL.md`.

### 🎯 Ordem de prioridade

Revisada em **2026-09-20**, após modernização visual de 8 templates de e-mail transacional.

1. **[Lista de Desejos](todo/lista-de-desejos.md)** — maior aposta de valor direto ao usuário. Transforma busca frustrada em demanda explícita e reaproveita a confiança do fluxo atual de doação; v1 conectiva, sem pagamento, com caminho natural para patrocínio/Amazon na v2. **Em execução pelo Josué (humano) — não é item livre para agentes pegarem.**
2. **[Simplificação e modernização do código (backend)](todo/simplificacao-modernizacao-backend/index.md)** — alto valor, esforço ainda não estimado. Continuação natural da mesma frente do frontend ([concluída em 2026-09-19](done/simplificacao-modernizacao-frontend/index.md), validada em dev pelo Raffa), agora no `sharebook-backend`: mesmo objetivo de reduzir custo cognitivo e tornar o código humano/IA-friendly, sem apego a arquitetura histórica nem a patterns modernos por si só. Pedido do Raffa em 2026-09-19. **As 11 tarefas do épico foram concluídas em 2026-09-20** (`develop` promovido pra `master`); falta a validação do Raffa em dev pra fechar o checkpoint final e mover pra `done/`, igual foi feito no frontend.
3. **[Débitos técnicos backend](todo/debitos-tecnicos-backend.md)** — **ambos os itens corrigidos em 2026-09-20** (commits `2c9a841` e `722cf4e`, direto em `develop`). Dois achados incidentais durante o épico acima: teste `HelperTests.ImageResize` que fazia chamada HTTP de verdade pra URL externa de terceiro (frágil por design, não só na sandbox), e migration `RenameEFLogs` com nome de índice hardcoded do banco de produção que impedia rodar a cadeia de migrations do zero num ambiente limpo.
4. **[Modernização dos templates de e-mail restantes](todo/modernizacao-templates-email-restantes.md)** — valor médio, esforço baixo. 8 templates de alta prioridade já modernizados e em produção em 2026-09-20 (visual card + azul Sharebook `#29abe2`); faltam ~10 templates de prioridade média/baixa, um ajuste de cor pontual num template já moderno mas fora da paleta, e uma decisão de copy adiada pelo Raffa.
5. **[Dedupe preventivo no importer](todo/dedupe-preventivo-importer.md)** — valor médio–alto, esforço médio. Impedir nova duplicata digital sem bloquear exemplares físicos ou edições legítimas.
6. **[Tolerância a erro na busca](todo/busca-e-recomendacao-sharebook/tarefa03-tolerancia-a-erro.md)** — valor incremental, esforço médio. O núcleo lexical já está em produção; retomar trigram e fallback fuzzy quando buscas sem resultado mostrarem custo real de typos.
7. **[Painel de Jobs v2](todo/painel-de-jobs.md)** — valor médio, esforço médio. A v1 já está publicada; falta calcular saúde, expor histórico paginado e distinguir melhor quem enfileira de quem consome.
8. **[Tags e conhecimento estruturado](todo/tags-e-conhecimento-estruturado.md)** — valor médio–alto, esforço alto. Começar com vocabulário controlado e tags navegáveis; estruturar tópicos, nível e pré-requisitos em fatia posterior.
9. **[Recomendações semânticas com embeddings](todo/busca-e-recomendacao-sharebook/tarefa05-recomendacoes-semanticas-embeddings.md)** — valor médio, esforço alto. A recomendação pragmática da PDP já está publicada; só adicionar embeddings quando seus limites lexicais aparecerem em amostra editorial ou dados de navegação.
10. **[Home v2 — mais baixados e vitrines temáticas](todo/home-v2-curadoria-ranking.md)** — entregue em 2026-09-10. A Home ganhou a prateleira "Mais baixados" com `BookDownloadEvent`, `UserId` opcional via JWT, backfill GA4 de 30 dias e cache SSR preservado; agora fica em observação de clique/download.
11. **[Social e Reviews](todo/social/_plano.md) + [Pegasus](todo/pegasus-engagement-engine.md)** — valor ainda incerto, esforço muito alto. Adiar até existir sinal real de retenção.
12. **[Sharebook Audio — Converse com seus livros](todo/sharebook-audio-converse-com-seus-livros.md)** — valor potencialmente altíssimo, esforço e risco muito altos. Discovery antes de implementação: benchmark de um mês, catálogo juridicamente seguro, prova do loop `PLAY → PAUSE → ASK → RESUME` e unit economics desde o MVP.
13. **[Agente Sharebook — companheiro de leitura e jornadas](todo/agente-sharebook/index.md)** — valor potencialmente altíssimo, esforço e risco muito altos. Separado do Audio: começa com identidade e capacidades read-only; memória, ações e novos canais avançam apenas com jornadas comprovadas.
14. **[Expansão de sources do acervo](todo/expansao-sources-acervo.md)** — valor baixo no momento, esforço contínuo. A fila ativa já sustenta meses de processamento deliberadamente lento.
15. **[Capas v2 — S3 + CDN](todo/pipeline-capas-s3-cdn.md)** — valor baixo na escala atual, esforço alto. As thumbnails locais reduziram em 94,8% o peso das capas da home; retomar storage externo quando escala, custo ou operação justificarem.
16. **[Cloudflare: CDN + DDoS](todo/cloudflare-cdn-ddos-protection.md)** — baixo valor na escala atual, esforço médio. Retomar quando tráfego ou risco justificarem.
17. **[Aposentadoria completa do facilitador](todo/aposentadoria-completa-facilitador.md)** — valor baixo após a retirada da experiência visível, esforço médio. Fechar domínio, banco, jobs, contratos e documentação numa rodada própria.
18. **[Unificação Scripts + Renomeação do Corpus](todo/unificacao-scripts-memory-durable.md)** — baixo valor para produto, esforço médio. Não competir com trabalho de produto e operação.
19. **[SMTP próprio com Stalwart](todo/smtp-proprio-stalwart.md)** — economia potencial, esforço e risco operacional médios. Retomar quando o custo do provedor justificar PTR próprio, aquecimento de reputação e desacoplamento SMTP/IMAP dos bounces.
20. **[Migração dos backups GCP para AWS](todo/migracao-backups-gcp-aws.md)** — baixa urgência no curto prazo: há R$ 16,81 de crédito na GCP e gasto perto de R$ 4/mês. Retomar quando formos consolidar storage ou quando o crédito estiver perto do fim.
21. **[Vitrine Bruxas & Magia](todo/vitrine-bruxas-e-magia.md)** — aposta temática de catálogo com Project Gutenberg como source preferencial. POC manual com `gpt-5.4-mini` validou que mini serve como rascunho, mas a v1 deve usar modelo forte direto para simplicidade e qualidade.
22. **[Footer de build-info mostra "dev-local"](todo/footer-build-info-dev-local.md)** — valor baixo, esforço baixo depois de ter o log de build real do Coolify. Bug conhecido, deliberadamente adiado pelo Raffa em 2026-09-19; movido da memória episódica pro backlog em 2026-09-20 só pra não ficar esquecido.


---
Para detalhes de execução de cada item, consulte o arquivo correspondente na pasta `todo/`.
