## BACKLOG

### 🌟 Visão Geral
- **North star do produto**: tornar o Sharebook o melhor hub de livros gratuitos do Brasil. Detalhes em `backlog/todo/maior-site-livros/_plano.md`.

### 🎯 Ordem de prioridade

Revisada em **2026-08-23**, considerando valor atual para produto/operação e esforço relativo.

1. **[Corrigir colisão de slugs dos volumes HPC](backlog/todo/corrigir-colisao-slugs-hpc.md)** — alto valor imediato, esforço baixo. Dois volumes digitais distintos estão sem URL pública própria; exige redirects antes da correção dos slugs.
2. **[SEO v1](backlog/todo/seo-v1/_plano.md)** — alto valor, esforço baixo–médio. Atacar CTR, metadados curtos e schema completo nas PDPs.
3. **[Busca textual: FTS + fuzzy](backlog/todo/busca-e-recomendacao-sharebook.md)** — alto valor, esforço médio. Centralizar disponibilidade e melhorar relevância antes de introduzir vetores.
4. **[Painel de Jobs](backlog/todo/painel-de-jobs.md)** — alto valor, esforço médio. Tornar falhas, atrasos e fluxo de filas visíveis e acionáveis.
5. **[Expansão curada do acervo](backlog/todo/maior-site-livros/_plano.md)** — alto valor, esforço médio contínuo. Priorizar fontes simples e editoriais antes das fontes incertas:
   1. [Goalkicker](backlog/todo/fonte-goalkicker.md), [JSBooks](backlog/todo/fonte-jsbooks.md) e [dBooks](backlog/todo/fonte-dbooks.md).
   2. [InTech Open](backlog/todo/fonte-intechopen.md) e [InfoQ Minibooks](backlog/todo/fonte-infoq.md).
   3. [FreeTechBooks](backlog/todo/fonte-freetechbooks.md) e o bloco de [novas sources revelado pelo conceptf1](backlog/todo/nova-source-conceptf1-blogspot.md).
6. **[Dependências e Segurança](backlog/todo/seguranca-e-vulnerabilidades.md)** — alto valor, alto esforço. Modernizar incrementalmente, sem salto cego de major.
7. **[Dedupe preventivo no importer](backlog/todo/dedupe-preventivo-importer.md)** — valor médio–alto, esforço médio. Impedir nova duplicata digital sem bloquear exemplares físicos ou edições legítimas.
8. **[Search Console Access](backlog/todo/search-console-access.md)** — valor médio, esforço baixo–médio. Melhorar a qualidade das decisões de SEO.
9. **[Pipeline de Capas: S3 + CDN](backlog/todo/pipeline-capas-s3-cdn.md)** — alto valor, alto esforço. Os quick wins já reduziram a urgência da migração completa.
10. **[Reformulação da Home](backlog/todo/reformulacao-home.md)** — valor médio, esforço médio. Evoluir curadoria e ranking depois de busca e dados.
11. **[Lista de Desejos — Doação Reversa](backlog/todo/lista-de-desejos.md)** — valor potencialmente alto, esforço alto. Validar demanda antes de construir o MVP.
12. **[Recomendações vetoriais](backlog/todo/busca-e-recomendacao-sharebook.md#fase-3--recomendações-na-pdp-com-embeddings--pgvector)** — valor médio, esforço alto. Só iniciar após busca textual e limpeza do catálogo.
13. **[Social e Reviews](backlog/todo/social/_plano.md) + [Pegasus](backlog/todo/pegasus-engagement-engine.md)** — valor ainda incerto, esforço muito alto. Adiar até existir sinal real de retenção.
14. **[Cloudflare: CDN + DDoS](backlog/todo/cloudflare-cdn-ddos-protection.md)** — baixo valor na escala atual, esforço médio. Retomar quando tráfego ou risco justificarem.
15. **[Aposentadoria completa do facilitador](backlog/todo/aposentadoria-completa-facilitador.md)** — valor baixo após a retirada da experiência visível, esforço médio. Fechar domínio, banco, jobs, contratos e documentação numa rodada própria.
16. **[Unificação Scripts + Renomeação do Corpus](backlog/todo/unificacao-scripts-memory-durable.md)** — baixo valor para produto, esforço médio. Não competir com trabalho de produto e operação.
17. **[SMTP próprio com Stalwart](backlog/todo/smtp-proprio-stalwart.md)** — economia potencial, esforço e risco operacional médios. Retomar quando o custo do provedor justificar PTR próprio, aquecimento de reputação e desacoplamento SMTP/IMAP dos bounces.

### 🚫 Fora da fila — OpenClaw dormente

O container OpenClaw foi desprovisionado em 2026-08-16. Os itens abaixo ficaram sem objeto: não são prioridade, não são candidatos a execução, e só voltam à fila se o habitat for reprovisionado. Ver `skills/runtime/openclaw.md`.

- **[Canal Claude ↔ OpenClaw](backlog/todo/canal-claude-openclaw.md)**: Canal peer-to-peer assimétrico entre os dois agentes via MCP + PostgreSQL. Pressupõe dois agentes vivos — hoje existe um só.
- **[OpenAI Codex — Dreno OAuth](backlog/todo/openai-codex-oauth-drain.md)**: Dreno de limites OpenAI no agente `mini`, que vivia no container. Sem agente, sem cron job e sem dreno.

---
Para detalhes de execução de cada item, consulte o arquivo correspondente na pasta `todo/`.
