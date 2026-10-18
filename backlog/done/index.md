# Backlog — Done

Itens concluídos. Raramente revisitados; a fila viva está em [`../index.md`](../index.md).

## Mais relevantes

- **[Pré-lançamento de livros físicos](pre-lancamento-livros-fisicos.md)** — concluído em 2026-10-18. Status `Scheduled` ("Em breve") com data de liberação, job das 7h que libera e avisa, "Quero ser avisado" com e-mail, PDP com faixa de contagem e botão âmbar, e a mesma ordem (físicos disponíveis, prévias, digitais) em categoria, tag e busca. Calendário de 5 livros para nov–dez/2026 cadastrado com `--release-date`. Lições (projeções manuais, Newtonsoft, EmailTemplate) e limites (sem tela de reagendar) no arquivo.
- **[Tags e conhecimento estruturado](tags-e-conhecimento-estruturado/index.md)** — missão cumprida em 2026-10-03. Entregou vocabulário controlado, modelo, navegação pública, motor mecânico na criação de livros, backfill técnico controlado e playbook operacional; a antiga Tarefa 7 foi cancelada por falta de valor percebido.
- **[Aposentadoria completa do facilitador](aposentadoria-completa-facilitador.md)** — concluída em 2026-10-14. Removeu o conceito do backend, frontend, jobs/e-mails e scripts/playbooks; a migração retira `Books.UserIdFacilitator` e **renomeia `FacilitatorNotes` para `AdminNotes`** (os comentários da administração foram mantidos). A primeira versão sem Designer não rodou e a corrigida derrubou a API por ~27 min (índice inexistente em produção); resolvido por hotfix idempotente, detalhes no arquivo.
- **[SMTP próprio com Stalwart](smtp-proprio-stalwart.md)** — concluído em 2026-10-14. Stalwart é o SMTP de produção desde 2026-09-08 e o Hostinger foi desprovisionado até 2026-09-16; bounces síncronos (webhook) e assíncronos (IMAP + job) implementados. Ficam como melhorias soltas: TLS válido, DMARC mais rígido e reconferir PTR.
- **[Categoria "Matemática & Lógica"](categoria-matematica-e-logica/index.md)** — concluída em 2026-10-14. Raiz com 50 livros em 6 subcategorias, tirados do corredor de Tecnologia; verificação pública fechada em 2026-10-05 e decisões curatoriais fechadas.
- **[Unificação de Scripts e Renomeação do Corpus](unificacao-scripts-e-renomeacao-corpus.md)** — concluída em 2026-10-14. Scripts passaram a morar junto dos playbooks que os explicam; a memória episódica vive em `sessions/`. A ideia de nomear as pastas `memory-durable/` e `memory-episodic/` foi desistida pelo Raffa.
- **[Vitrine Bruxas & Magia](vitrine-bruxas-e-magia.md)** — frente editorial fechada em 2026-10-14. Validou pipeline Gutenberg/tradução/capa/PDF, categoria temática e vitrine com identidade clara.
- **[Home v2 — mais baixados e vitrines temáticas](home-v2-curadoria-ranking.md)** — concluída em 2026-10-14. Entregou a prateleira "Mais baixados", `BookDownloadEvent`, backfill GA4, endpoint público e cache SSR preservado.
- **[Restaurar índice de memória do OpenClaw](restaurar-indice-de-memoria.md)** — concluído em 2026-10-12. O índice e a CLI estavam saudáveis; a tool dinâmica `memory_search` falhava por estado velho do Gateway com `401 token_expired`. Restart controlado resolveu; `memory_search`/`memory_get` voltaram e a CLI confirmou `280/280`, `Dirty: no`.
- **[Laboratório Sharebook — observabilidade .NET por 24h](observabilidade-dotnet-laboratorio-24h.md)** — concluído em 2026-10-12. A POC provou valor e virou stack mínima permanente: métricas OTLP/Grafana Cloud, logs Loki, playbook `grafana-cloud-explorer.md` e helper compacto de consulta.
- **[Devroye cadastrado como errata](fix-devroye-errata-cadastrada-como-livro.md)** — removido do catálogo público em 2026-10-05. `Non-Uniform Random Variate Generation` prometia o livro completo, mas o PDF publicado era uma corrigenda/errata de 7 páginas.
- **[Update de ebook não troca o PDF](fix-update-ebook-nao-troca-pdf.md)** — correção concluída em 2026-10-16. `BookService.UpdateAsync` passou a fazer upload do `PdfBytes` usando o slug salvo, persistir `EBookPdfPath` e preservar o PDF quando nenhum novo arquivo é enviado; inclui testes unitários e foi enviada à `master` no commit `6550162`.

## Demais

- [Missão Principal — 01 BaixeLivros Estrangeiros](01-baixelivros-estrangeiros.md)
- [Missão — 02 BaixeLivros Literatura Brasileira](02-baixelivros-literatura-brasileira.md)
- [📚 Refatoração da Categoria "Artes" → "Poesia & Artes"](03-refatoracao-categoria-artes.md)
- [🦞 OpenClaw Debug Session — Resumo + Próximos Passos](06-fix-openclaw-dashboard.md)
- [Missão — Aposentar `position` como chave operacional no importer](aposentar-position-como-chave-operacional-no-importer.md)
- [Missão — Automação BaixeLivros Worker (SQLite + Cron)](automacao-baixelivros-worker-plano.md)
- [Tornar a busca encontrável no mobile](busca-encontravel-mobile.md)
- [Cloud para Devs: fundamentos sem enrolação](cloud-para-devs-manuscrito-v1.md)
- [📘 Bíblia Editorial — Cloud para Devs](cloud-para-devs.md)
- [Correção da colisão de slugs dos volumes HPC](corrigir-colisao-slugs-hpc.md)
- [Débitos técnicos backend (achados incidentais)](debitos-tecnicos-backend.md)
- [Investigar deploy automático GitHub + Coolify](deploy-automatico-github-coolify-pos-migracao.md)
- [Missão — Ebook Foundation Português](ebook-foundation-portugues.md)
- [Etapa 07 - SEO técnico com SSR no frontend](etapa%2007%20-%20seo-ssr.md)
- [📚 Sharebook — Plano de Evolução de Categorias](etapa-02-reorganizar-categorias.md)
- [📚 Sharebook — Cobertura Mínima por Categoria](etapa-03-cobertura-minima-por-categoria.md)
- [Limpeza de duplicatas no catálogo](limpeza-duplicatas-catalogo.md)
- [Workflow MVP](livrosdominiopublico.md)
- [Maior site de livros v1 — fundação concluída](maior-site-livros-v1.md)
- [Migração incremental do Angular (13 → LTS ativa)](migracao-angular-13-lts.md)
- [Modernização dos templates de e-mail restantes](modernizacao-templates-email-restantes.md)
- [Painel de Jobs v2](painel-de-jobs-v2.md)
- [Recuperar a suíte de testes do frontend](recuperar-suite-testes-frontend.md)
- [Introdução a Redes Neurais](redes-neurais-manuscrito-v1.md)
- [📘 Bíblia Editorial — Sharebook](redes-neurais.md)
- [Reformulação da Home v1 — concluída](reformulacao-home-v1.md)
- [Retenção de backups consolidada no lifecycle nativo do GCS](retencao-backup-gcs-lifecycle.md)
- [Revisão de copy dos e-mails da leva 2](revisao-copy-emails-leva-2.md)
- [Search Console Access — concluído em 26/08/2026](search-console-access.md)
- [Missão — Dependências e Segurança](seguranca-e-vulnerabilidades.md)
- [SEO v1 — concluída](seo-v1.md)
- [Épico — Simplificação e modernização do código (sharebook-backend)](simplificacao-modernizacao-backend/index.md)
- [Épico — Simplificação e modernização do código (sharebook-frontend)](simplificacao-modernizacao-frontend/index.md)
