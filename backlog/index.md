## BACKLOG

### 🌟 Visão Geral
- **North star do produto**: tornar o Sharebook o melhor hub de livros gratuitos do Brasil. Detalhes em `backlog/todo/maior-site-livros/_plano.md`.
- **[Unificação Scripts + Renomeação do Corpus](backlog/todo/unificacao-scripts-memory-durable.md)**: Scripts viram artefatos subordinados a knowledge; `skills/` → `memory-durable/`, `memory/` → `memory-episodic/`.

### 🎯 TODO

- **[Maior Site de Livros](backlog/todo/maior-site-livros/_plano.md)**: Meta de 1000 livros curados e sistema de curadoria de elite.
- **[Busca e Recomendação](backlog/todo/busca-e-recomendacao-sharebook.md)**: FTS, fuzzy matching e recomendações vetoriais via pgvector.
- **[Painel de Jobs](backlog/todo/painel-de-jobs.md)**: Evolução do dashboard de monitoria de jobs em background.
- **[SEO v1](backlog/todo/seo-v1/_plano.md)**: Sitemap dinâmico, Breadcrumbs e melhorias de indexação.
- **[Social e Reviews](backlog/todo/social/_plano.md)**: Comentários, avaliações de livros e login progressivo via Pegasus.
- **[Dependências e Segurança](backlog/todo/seguranca-e-vulnerabilidades.md)**: Atualização de toolchain (Angular 13+) e correção de passivo de segurança.
- **[Search Console Access](backlog/todo/search-console-access.md)**: Destravar acesso programático do agente ao Search Console, preferencialmente com service account e fallback para OAuth.
- **[Reformulação da Home](backlog/todo/reformulacao-home.md)**: Home mobile-first com prateleiras temáticas estilo Netflix — foco em descoberta de catálogo e curadoria.
- **[Nova source: conceptf1.blogspot / item 1327](backlog/todo/nova-source-conceptf1-blogspot.md)**: O item 1327 revelou uma source nova; tratar no nível de source, não como ebook unitário.

- **[Nova Fonte: dBooks.org](backlog/todo/fonte-dbooks.md)**: `dbooks.org` tem catálogo navegável por subject (`/subject/computer-science/`, etc.), API em `/api/` e RSS. Vale criar extractor dedicado para expandir o corpus técnico.
- **[Nova Fonte: Goalkicker.com](backlog/todo/fonte-goalkicker.md)**: PDFs técnicos gratuitos de alta qualidade, um por linguagem/tecnologia (JavaScript, Python, Git, SQL, etc.). PDFs diretos e bem estruturados. Alto valor para o corpus técnico.
- **[Nova Fonte: FreeTechBooks.com](backlog/todo/fonte-freetechbooks.md)**: Agregador de livros técnicos gratuitos em várias categorias. Descoberto como item `source_blocked` da EbookFoundation — homepage apontada como item, mas o site em si é candidato a fonte.
- **[Nova Fonte: InfoQ Minibooks](backlog/todo/fonte-infoq.md)**: Minibooks técnicos gratuitos da InfoQ — arquitetura, microserviços, DevOps, linguagens. Conteúdo de alta qualidade editorial.
- **[Nova Fonte: InTech Open](backlog/todo/fonte-intechopen.md)**: Editora acadêmica open access. Livros de Computer and Information Science disponíveis gratuitamente em `intechopen.com/subjects/9`.
- **[Nova Fonte: JSBooks](backlog/todo/fonte-jsbooks.md)**: Diretório curado de ebooks gratuitos de JavaScript. Repo GitHub `revolunet/JSBooks` com links diretos para PDFs.
- **[Canal Claude ↔ OpenClaw](backlog/todo/canal-claude-openclaw.md)**: Canal peer-to-peer assimétrico entre os dois agentes via MCP + PostgreSQL. Claude inicia, OpenClaw responde via gateway. Sem hierarquia — divisão de papéis por capacidade.

---
Para detalhes de execução de cada item, consulte o arquivo correspondente na pasta `todo/`.
