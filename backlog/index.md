## BACKLOG

### 🌟 Visão Geral
- **North star do produto**: tornar o Sharebook o melhor hub de livros gratuitos do Brasil. Detalhes em `backlog/todo/maior-site-livros/_plano.md`.
- **[Unificação Scripts + Renomeação do Corpus](backlog/todo/unificacao-scripts-memory-durable.md)**: Scripts viram artefatos subordinados a knowledge; `skills/` → `memory-durable/`, `memory/` → `memory-episodic/`.

### 🎯 TODO

- **[Maior Site de Livros](backlog/todo/maior-site-livros/_plano.md)**: Meta de 1000 livros curados e sistema de curadoria de elite.
- **[Busca e Recomendação](backlog/todo/busca-e-recomendacao-sharebook.md)**: FTS, fuzzy matching e recomendações vetoriais via pgvector.
- **[Limpeza de Duplicatas no Catálogo](backlog/todo/limpeza-duplicatas-catalogo.md)**: ~235 registros duplicados (~9% do catálogo, ex: "Orgulho e Preconceito" 9×). Polui busca, SEO e atribuição de afiliado. Pré-condição de qualidade pra embeddings.
- **[Painel de Jobs](backlog/todo/painel-de-jobs.md)**: Evolução do dashboard de monitoria de jobs em background.
- **[SEO v1](backlog/todo/seo-v1/_plano.md)**: Sitemap e robots entregues; próximos ganhos estão em CTR, metadados curtos, schema completo e conhecimento estruturado nas PDPs.
- **[Social e Reviews](backlog/todo/social/_plano.md)**: Comentários, avaliações de livros e login progressivo via Pegasus.
- **[Pegasus — Engagement Engine](backlog/todo/pegasus-engagement-engine.md)**: Engine de eventos + pontos (XP/Karma) + regras + histórico. Year 1: serviço REST simples, PostgreSQL, sem frescura. Níveis/badges/streaks/loja/IA ficam pro Ano 2+.
- **[Lista de Desejos — Doação Reversa](backlog/todo/lista-de-desejos.md)**: Leitores publicam livros que querem receber, doadores escolhem quem atender. MVP sem Karma — 3 pedidos por usuário, anônimo até o match.
- **[Dependências e Segurança](backlog/todo/seguranca-e-vulnerabilidades.md)**: Atualização de toolchain (Angular 13+) e correção de passivo de segurança.
- **[Search Console Access](backlog/todo/search-console-access.md)**: Destravar acesso programático do agente ao Search Console, preferencialmente com service account e fallback para OAuth.
- **[Reformulação da Home](backlog/todo/reformulacao-home.md)**: Fundação de posicionamento e navegação entregue; evolução restante é curadoria, ranking e personalização das prateleiras.
- **[Pipeline de Capas: S3 + CDN](backlog/todo/pipeline-capas-s3-cdn.md)**: Move capas para object storage, gera variantes otimizadas e entrega por CDN sem depender do filesystem do backend.
- **[Cloudflare: CDN + DDoS + Egress Grátis](backlog/todo/cloudflare-cdn-ddos-protection.md)**: Proteção L7 contra floods, rate limiting no edge, egress de download grátis. Alternativa mais barata que AWS CloudFront+WAF.
- **[Retenção de Backup no S3 Quebrada](backlog/todo/retencao-backup-s3-quebrada.md)**: `CleanupInstanceStuffsJob` falha em todo delete no bucket do GCS a cada 30 min. Backup grava normal, mas nada é apagado — storage acumula indefinidamente. Provável falta de permissão de delete na credencial.
- **[Nova source: conceptf1.blogspot / item 1327](backlog/todo/nova-source-conceptf1-blogspot.md)**: O item 1327 revelou uma source nova; tratar no nível de source, não como ebook unitário.

- **[Nova Fonte: dBooks.org](backlog/todo/fonte-dbooks.md)**: `dbooks.org` tem catálogo navegável por subject (`/subject/computer-science/`, etc.), API em `/api/` e RSS. Vale criar extractor dedicado para expandir o corpus técnico.
- **[Nova Fonte: Goalkicker.com](backlog/todo/fonte-goalkicker.md)**: PDFs técnicos gratuitos de alta qualidade, um por linguagem/tecnologia (JavaScript, Python, Git, SQL, etc.). PDFs diretos e bem estruturados. Alto valor para o corpus técnico.
- **[Nova Fonte: FreeTechBooks.com](backlog/todo/fonte-freetechbooks.md)**: Agregador de livros técnicos gratuitos em várias categorias. Descoberto como item `source_blocked` da EbookFoundation — homepage apontada como item, mas o site em si é candidato a fonte.
- **[Nova Fonte: InfoQ Minibooks](backlog/todo/fonte-infoq.md)**: Minibooks técnicos gratuitos da InfoQ — arquitetura, microserviços, DevOps, linguagens. Conteúdo de alta qualidade editorial.
- **[Nova Fonte: InTech Open](backlog/todo/fonte-intechopen.md)**: Editora acadêmica open access. Livros de Computer and Information Science disponíveis gratuitamente em `intechopen.com/subjects/9`.
- **[Nova Fonte: JSBooks](backlog/todo/fonte-jsbooks.md)**: Diretório curado de ebooks gratuitos de JavaScript. Repo GitHub `revolunet/JSBooks` com links diretos para PDFs.

### 🚧 Bloqueados — dependem do retorno do OpenClaw

O container OpenClaw foi desprovisionado em 2026-08-16. Os itens abaixo ficaram sem objeto: não são prioridade, não são candidatos a execução, e só voltam à fila se o habitat for reprovisionado. Ver `skills/runtime/openclaw.md`.

- **[Canal Claude ↔ OpenClaw](backlog/todo/canal-claude-openclaw.md)**: Canal peer-to-peer assimétrico entre os dois agentes via MCP + PostgreSQL. Pressupõe dois agentes vivos — hoje existe um só.
- **[OpenAI Codex — Dreno OAuth](backlog/todo/openai-codex-oauth-drain.md)**: Dreno de limites OpenAI no agente `mini`, que vivia no container. Sem agente, sem cron job e sem dreno.

---
Para detalhes de execução de cada item, consulte o arquivo correspondente na pasta `todo/`.
