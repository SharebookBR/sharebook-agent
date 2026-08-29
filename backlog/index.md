## BACKLOG

### 🌟 Visão Geral
- **North star do produto**: tornar o Sharebook o melhor hub de livros gratuitos do Brasil. Critérios duráveis em `skills/product-ux/catalog-strategy/SKILL.md`.

### 🎯 Ordem de prioridade

Revisada em **2026-08-27**, após a revisão crítica dos itens já entregues, da dívida de testes e da capacidade atual do importer.

1. **[Busca textual: FTS + fuzzy](backlog/todo/busca-e-recomendacao-sharebook/index.md)** — alto valor, esforço médio. Disponibilidade pública e FTS estão em produção; o próximo passo é tolerância a erro com trigram e fallback fuzzy.
2. **[Tornar a busca encontrável no mobile](backlog/todo/busca-encontravel-mobile.md)** — alto valor, esforço baixo–médio. Discutir o desenho antes de implementar; a busca não pode continuar escondida, especialmente para visitantes deslogados.
3. **[Recuperar e tornar útil a suíte de testes do frontend](backlog/todo/recuperar-suite-testes-frontend.md)** — alto valor, esforço médio. Corrigir as causas-raiz, remover sem apego testes que não protegem valor e fazer a suíte bloquear o pipeline quando houver regressão real.
4. **[Dependências e Segurança](backlog/todo/seguranca-e-vulnerabilidades.md)** — alto valor, alto esforço. Modernizar incrementalmente, sem salto cego de major.
5. **[Dedupe preventivo no importer](backlog/todo/dedupe-preventivo-importer.md)** — valor médio–alto, esforço médio. Impedir nova duplicata digital sem bloquear exemplares físicos ou edições legítimas.
6. **[Painel de Jobs v2](backlog/todo/painel-de-jobs.md)** — valor médio, esforço médio. A v1 já está publicada; falta calcular saúde, expor histórico paginado e distinguir melhor quem enfileira de quem consome.
7. **[Lista de Desejos — Doação Reversa](backlog/todo/lista-de-desejos.md)** — valor potencialmente alto, esforço alto. Validar demanda antes de construir o MVP.
8. **[Tags e conhecimento estruturado](backlog/todo/tags-e-conhecimento-estruturado.md)** — valor médio–alto, esforço alto. Começar com vocabulário controlado e tags navegáveis; estruturar tópicos, nível e pré-requisitos em fatia posterior.
9. **[Recomendações vetoriais](backlog/todo/busca-e-recomendacao-sharebook/tarefa04-recomendacoes-semanticas-pdp.md)** — valor médio, esforço alto. Só iniciar após busca textual, tolerância a erro e limpeza do catálogo.
10. **[Home v2 — curadoria e ranking](backlog/todo/home-v2-curadoria-ranking.md)** — valor médio, esforço médio. A reformulação estrutural está concluída; evoluir apenas com dados e hipóteses claras de descoberta.
11. **[Social e Reviews](backlog/todo/social/_plano.md) + [Pegasus](backlog/todo/pegasus-engagement-engine.md)** — valor ainda incerto, esforço muito alto. Adiar até existir sinal real de retenção.
12. **[Expansão de sources do acervo](backlog/todo/expansao-sources-acervo.md)** — valor baixo no momento, esforço contínuo. A fila ativa já sustenta meses de processamento deliberadamente lento.
13. **[Capas v2 — S3 + CDN](backlog/todo/pipeline-capas-s3-cdn.md)** — valor baixo na escala atual, esforço alto. As thumbnails locais reduziram em 94,8% o peso das capas da home; retomar storage externo quando escala, custo ou operação justificarem.
14. **[Cloudflare: CDN + DDoS](backlog/todo/cloudflare-cdn-ddos-protection.md)** — baixo valor na escala atual, esforço médio. Retomar quando tráfego ou risco justificarem.
15. **[Aposentadoria completa do facilitador](backlog/todo/aposentadoria-completa-facilitador.md)** — valor baixo após a retirada da experiência visível, esforço médio. Fechar domínio, banco, jobs, contratos e documentação numa rodada própria.
16. **[Unificação Scripts + Renomeação do Corpus](backlog/todo/unificacao-scripts-memory-durable.md)** — baixo valor para produto, esforço médio. Não competir com trabalho de produto e operação.
17. **[SMTP próprio com Stalwart](backlog/todo/smtp-proprio-stalwart.md)** — economia potencial, esforço e risco operacional médios. Retomar quando o custo do provedor justificar PTR próprio, aquecimento de reputação e desacoplamento SMTP/IMAP dos bounces.


---
Para detalhes de execução de cada item, consulte o arquivo correspondente na pasta `todo/`.
