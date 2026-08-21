## BACKLOG

### 🌟 Visão Geral
- **North star do produto**: tornar o Sharebook o melhor hub de livros gratuitos do Brasil. Detalhes em `backlog/todo/maior-site-livros/_plano.md`.

### 🎯 Ordem de prioridade

Revisada em **2026-08-20**, considerando valor atual para produto/operação e esforço relativo.

1. **[Retenção de Backup no S3 Quebrada](backlog/todo/retencao-backup-s3-quebrada.md)** — alto valor, baixo esforço. Corrigir o acúmulo silencioso e o erro recorrente do Coolify.
2. **[Bugs de API, filtros e rotas](backlog/todo/maior-site-livros/_plano.md#-tech-debt--bugs-priorizar)** — alto valor, esforço baixo–médio. Corrigir Category PUT, filtros de Book, rota ambígua e identidade operacional do importer.
3. **[Limpeza de Duplicatas no Catálogo](backlog/todo/limpeza-duplicatas-catalogo.md)** — alto valor, esforço médio. Melhora busca, SEO e analytics e prepara o catálogo para embeddings.
4. **[SEO v1](backlog/todo/seo-v1/_plano.md)** — alto valor, esforço baixo–médio. Atacar CTR, metadados curtos e schema completo nas PDPs.
5. **[Busca textual: FTS + fuzzy](backlog/todo/busca-e-recomendacao-sharebook.md)** — alto valor, esforço médio. Centralizar disponibilidade e melhorar relevância antes de introduzir vetores.
6. **[Painel de Jobs](backlog/todo/painel-de-jobs.md)** — alto valor, esforço médio. Tornar falhas, atrasos e fluxo de filas visíveis e acionáveis.
7. **[Expansão curada do acervo](backlog/todo/maior-site-livros/_plano.md)** — alto valor, esforço médio contínuo. Priorizar fontes simples e editoriais antes das fontes incertas:
   1. [Goalkicker](backlog/todo/fonte-goalkicker.md), [JSBooks](backlog/todo/fonte-jsbooks.md) e [dBooks](backlog/todo/fonte-dbooks.md).
   2. [InTech Open](backlog/todo/fonte-intechopen.md) e [InfoQ Minibooks](backlog/todo/fonte-infoq.md).
   3. [FreeTechBooks](backlog/todo/fonte-freetechbooks.md) e o bloco de [novas sources revelado pelo conceptf1](backlog/todo/nova-source-conceptf1-blogspot.md).
8. **[Dependências e Segurança](backlog/todo/seguranca-e-vulnerabilidades.md)** — alto valor, alto esforço. Modernizar incrementalmente, sem salto cego de major.
9. **[Search Console Access](backlog/todo/search-console-access.md)** — valor médio, esforço baixo–médio. Melhorar a qualidade das decisões de SEO.
10. **[Pipeline de Capas: S3 + CDN](backlog/todo/pipeline-capas-s3-cdn.md)** — alto valor, alto esforço. Os quick wins já reduziram a urgência da migração completa.
11. **[Reformulação da Home](backlog/todo/reformulacao-home.md)** — valor médio, esforço médio. Evoluir curadoria e ranking depois de busca e dados.
12. **[Lista de Desejos — Doação Reversa](backlog/todo/lista-de-desejos.md)** — valor potencialmente alto, esforço alto. Validar demanda antes de construir o MVP.
13. **[Recomendações vetoriais](backlog/todo/busca-e-recomendacao-sharebook.md#fase-3--recomendações-na-pdp-com-embeddings--pgvector)** — valor médio, esforço alto. Só iniciar após busca textual e limpeza do catálogo.
14. **[Social e Reviews](backlog/todo/social/_plano.md) + [Pegasus](backlog/todo/pegasus-engagement-engine.md)** — valor ainda incerto, esforço muito alto. Adiar até existir sinal real de retenção.
15. **[Cloudflare: CDN + DDoS](backlog/todo/cloudflare-cdn-ddos-protection.md)** — baixo valor na escala atual, esforço médio. Retomar quando tráfego ou risco justificarem.
16. **[Unificação Scripts + Renomeação do Corpus](backlog/todo/unificacao-scripts-memory-durable.md)** — baixo valor para produto, esforço médio. Não competir com trabalho de produto e operação.

### 🚫 Fora da fila — OpenClaw dormente

O container OpenClaw foi desprovisionado em 2026-08-16. Os itens abaixo ficaram sem objeto: não são prioridade, não são candidatos a execução, e só voltam à fila se o habitat for reprovisionado. Ver `skills/runtime/openclaw.md`.

- **[Canal Claude ↔ OpenClaw](backlog/todo/canal-claude-openclaw.md)**: Canal peer-to-peer assimétrico entre os dois agentes via MCP + PostgreSQL. Pressupõe dois agentes vivos — hoje existe um só.
- **[OpenAI Codex — Dreno OAuth](backlog/todo/openai-codex-oauth-drain.md)**: Dreno de limites OpenAI no agente `mini`, que vivia no container. Sem agente, sem cron job e sem dreno.

---
Para detalhes de execução de cada item, consulte o arquivo correspondente na pasta `todo/`.
