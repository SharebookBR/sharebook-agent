## BACKLOG

### 🌟 Visão Geral
- **North star do produto**: tornar o Sharebook o melhor hub de livros gratuitos do Brasil. Critérios duráveis em `skills/product-ux/catalog-strategy/SKILL.md`.

### 🎯 Ordem de prioridade

Revisada em **2026-09-04**, após refinamento de produto da Lista de Desejos. A v1 ficou deliberadamente simples: apenas livros físicos, pedido revisado antes de aparecer, `Book` como fonte da verdade, sem pagamento, doador conectado ao solicitante como no fluxo atual.

1. **[Lista de Desejos](todo/lista-de-desejos.md)** — maior aposta de valor direto ao usuário. Transforma busca frustrada em demanda explícita e reaproveita a confiança do fluxo atual de doação; v1 conectiva, sem pagamento, com caminho natural para patrocínio/Amazon na v2.
2. **[Investigar deploy automático GitHub + Coolify](todo/investigar-deploy-automatico-github-coolify.md)** — alto valor operacional, esforço baixo–médio. O gate de teste passou no Docker/Coolify, mas o deploy não foi enfileirado automaticamente; investigar webhook, secret, branch protection e possível efeito da migração Hostinger → HostGator.
3. **[Dependências e Segurança](todo/seguranca-e-vulnerabilidades.md)** — alto valor, alto esforço. Triar o que é realmente explorável e modernizar incrementalmente, sem salto cego de major.
4. **[Dedupe preventivo no importer](todo/dedupe-preventivo-importer.md)** — valor médio–alto, esforço médio. Impedir nova duplicata digital sem bloquear exemplares físicos ou edições legítimas.
5. **[Tolerância a erro na busca](todo/busca-e-recomendacao-sharebook/tarefa03-tolerancia-a-erro.md)** — valor incremental, esforço médio. O núcleo lexical já está em produção; retomar trigram e fallback fuzzy quando buscas sem resultado mostrarem custo real de typos.
6. **[Painel de Jobs v2](todo/painel-de-jobs.md)** — valor médio, esforço médio. A v1 já está publicada; falta calcular saúde, expor histórico paginado e distinguir melhor quem enfileira de quem consome.
7. **[Tags e conhecimento estruturado](todo/tags-e-conhecimento-estruturado.md)** — valor médio–alto, esforço alto. Começar com vocabulário controlado e tags navegáveis; estruturar tópicos, nível e pré-requisitos em fatia posterior.
8. **[Recomendações semânticas com embeddings](todo/busca-e-recomendacao-sharebook/tarefa05-recomendacoes-semanticas-embeddings.md)** — valor médio, esforço alto. A recomendação pragmática da PDP já está publicada; só adicionar embeddings quando seus limites lexicais aparecerem em amostra editorial ou dados de navegação.
9. **[Home v2 — mais baixados e vitrines temáticas](todo/home-v2-curadoria-ranking.md)** — entregue em 2026-09-10. A Home ganhou a prateleira "Mais baixados" com `BookDownloadEvent`, `UserId` opcional via JWT, backfill GA4 de 30 dias e cache SSR preservado; agora fica em observação de clique/download.
10. **[Social e Reviews](todo/social/_plano.md) + [Pegasus](todo/pegasus-engagement-engine.md)** — valor ainda incerto, esforço muito alto. Adiar até existir sinal real de retenção.
11. **[Sharebook Audio — Converse com seus livros](todo/sharebook-audio-converse-com-seus-livros.md)** — valor potencialmente altíssimo, esforço e risco muito altos. Discovery antes de implementação: benchmark de um mês, catálogo juridicamente seguro, prova do loop `PLAY → PAUSE → ASK → RESUME` e unit economics desde o MVP.
12. **[Agente Sharebook — companheiro de leitura e jornadas](todo/agente-sharebook/index.md)** — valor potencialmente altíssimo, esforço e risco muito altos. Separado do Audio: começa com identidade e capacidades read-only; memória, ações e novos canais avançam apenas com jornadas comprovadas.
13. **[Expansão de sources do acervo](todo/expansao-sources-acervo.md)** — valor baixo no momento, esforço contínuo. A fila ativa já sustenta meses de processamento deliberadamente lento.
14. **[Capas v2 — S3 + CDN](todo/pipeline-capas-s3-cdn.md)** — valor baixo na escala atual, esforço alto. As thumbnails locais reduziram em 94,8% o peso das capas da home; retomar storage externo quando escala, custo ou operação justificarem.
15. **[Cloudflare: CDN + DDoS](todo/cloudflare-cdn-ddos-protection.md)** — baixo valor na escala atual, esforço médio. Retomar quando tráfego ou risco justificarem.
16. **[Aposentadoria completa do facilitador](todo/aposentadoria-completa-facilitador.md)** — valor baixo após a retirada da experiência visível, esforço médio. Fechar domínio, banco, jobs, contratos e documentação numa rodada própria.
17. **[Unificação Scripts + Renomeação do Corpus](todo/unificacao-scripts-memory-durable.md)** — baixo valor para produto, esforço médio. Não competir com trabalho de produto e operação.
18. **[SMTP próprio com Stalwart](todo/smtp-proprio-stalwart.md)** — economia potencial, esforço e risco operacional médios. Retomar quando o custo do provedor justificar PTR próprio, aquecimento de reputação e desacoplamento SMTP/IMAP dos bounces.
19. **[Migração dos backups GCP para AWS](todo/migracao-backups-gcp-aws.md)** — baixa urgência no curto prazo: há R$ 16,81 de crédito na GCP e gasto perto de R$ 4/mês. Retomar quando formos consolidar storage ou quando o crédito estiver perto do fim.
20. **[Vitrine Bruxas & Magia](todo/vitrine-bruxas-e-magia.md)** — aposta temática de catálogo com Project Gutenberg como source preferencial. POC manual com `gpt-5.4-mini` validou que mini serve como rascunho, mas a v1 deve usar modelo forte direto para simplicidade e qualidade.


---
Para detalhes de execução de cada item, consulte o arquivo correspondente na pasta `todo/`.
