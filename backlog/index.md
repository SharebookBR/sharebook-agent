## BACKLOG

### 🌟 Visão Geral
- **North star do produto**: tornar o Sharebook o melhor hub de livros gratuitos do Brasil. Critérios duráveis em `skills/product-ux/catalog-strategy/SKILL.md`.

### 🎯 Ordem de prioridade

Revisada em **2026-08-29**, após a publicação do núcleo da busca e a reavaliação do valor marginal das próximas fatias.

1. **[Recuperar e tornar útil a suíte de testes do frontend](todo/recuperar-suite-testes-frontend.md)** — alto valor, esforço médio. Corrigir as causas-raiz, remover sem apego testes que não protegem valor e fazer a suíte bloquear o pipeline quando houver regressão real.
2. **[Dependências e Segurança](todo/seguranca-e-vulnerabilidades.md)** — alto valor, alto esforço. Triar o que é realmente explorável e modernizar incrementalmente, sem salto cego de major.
3. **[Dedupe preventivo no importer](todo/dedupe-preventivo-importer.md)** — valor médio–alto, esforço médio. Impedir nova duplicata digital sem bloquear exemplares físicos ou edições legítimas.
4. **[Tolerância a erro na busca](todo/busca-e-recomendacao-sharebook/tarefa03-tolerancia-a-erro.md)** — valor incremental, esforço médio. O núcleo lexical já está em produção; retomar trigram e fallback fuzzy quando buscas sem resultado mostrarem custo real de typos.
5. **[Painel de Jobs v2](todo/painel-de-jobs.md)** — valor médio, esforço médio. A v1 já está publicada; falta calcular saúde, expor histórico paginado e distinguir melhor quem enfileira de quem consome.
6. **[Lista de Desejos — Doação Reversa](todo/lista-de-desejos.md)** — valor potencialmente alto, esforço alto. Validar demanda antes de construir o MVP.
7. **[Tags e conhecimento estruturado](todo/tags-e-conhecimento-estruturado.md)** — valor médio–alto, esforço alto. Começar com vocabulário controlado e tags navegáveis; estruturar tópicos, nível e pré-requisitos em fatia posterior.
8. **[Recomendações semânticas com embeddings](todo/busca-e-recomendacao-sharebook/tarefa05-recomendacoes-semanticas-embeddings.md)** — valor médio, esforço alto. A recomendação pragmática da PDP já está publicada; só adicionar embeddings quando seus limites lexicais aparecerem em amostra editorial ou dados de navegação.
9. **[Home v2 — curadoria e ranking](todo/home-v2-curadoria-ranking.md)** — valor médio, esforço médio. A reformulação estrutural está concluída; evoluir apenas com dados e hipóteses claras de descoberta.
10. **[Social e Reviews](todo/social/_plano.md) + [Pegasus](todo/pegasus-engagement-engine.md)** — valor ainda incerto, esforço muito alto. Adiar até existir sinal real de retenção.
11. **[Sharebook Audio — Converse com seus livros](todo/sharebook-audio-converse-com-seus-livros.md)** — valor potencialmente altíssimo, esforço e risco muito altos. Discovery antes de implementação: benchmark de um mês, catálogo juridicamente seguro, prova do loop `PLAY → PAUSE → ASK → RESUME` e unit economics desde o MVP.
12. **[Expansão de sources do acervo](todo/expansao-sources-acervo.md)** — valor baixo no momento, esforço contínuo. A fila ativa já sustenta meses de processamento deliberadamente lento.
13. **[Capas v2 — S3 + CDN](todo/pipeline-capas-s3-cdn.md)** — valor baixo na escala atual, esforço alto. As thumbnails locais reduziram em 94,8% o peso das capas da home; retomar storage externo quando escala, custo ou operação justificarem.
14. **[Cloudflare: CDN + DDoS](todo/cloudflare-cdn-ddos-protection.md)** — baixo valor na escala atual, esforço médio. Retomar quando tráfego ou risco justificarem.
15. **[Aposentadoria completa do facilitador](todo/aposentadoria-completa-facilitador.md)** — valor baixo após a retirada da experiência visível, esforço médio. Fechar domínio, banco, jobs, contratos e documentação numa rodada própria.
16. **[Unificação Scripts + Renomeação do Corpus](todo/unificacao-scripts-memory-durable.md)** — baixo valor para produto, esforço médio. Não competir com trabalho de produto e operação.
17. **[SMTP próprio com Stalwart](todo/smtp-proprio-stalwart.md)** — economia potencial, esforço e risco operacional médios. Retomar quando o custo do provedor justificar PTR próprio, aquecimento de reputação e desacoplamento SMTP/IMAP dos bounces.


---
Para detalhes de execução de cada item, consulte o arquivo correspondente na pasta `todo/`.
