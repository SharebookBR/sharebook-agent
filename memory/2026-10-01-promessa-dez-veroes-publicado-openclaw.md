+++
schema_version = 1
session_date = 2026-10-01
title = "Promessa de Dez Verões publicado pelo OpenClaw"
model = "GPT-5 Codex"
runtime = "OpenClaw"
skills_used = [
  "sharebook-agent/AGENTS.md",
  "sharebook-agent/SOUL.md",
  "skills/runtime/openclaw.md",
  "skills/importers/INDEX.md",
  "skills/importers/ebook-importer/SKILL.md",
  "skills/importers/escrever-livros/SKILL.md",
  "skills/product-ux/voice-glossary/SKILL.md",
  "skills/product-ux/voice-glossary/references/ux-writing-guide.md",
  "skills/doctrine/INDEX.md",
  "skills/doctrine/harness-governance/SKILL.md",
  "skills/doctrine/harness-governance/references/episodic-memory-metadata-v1.md",
]
skills_missed = []
skills_updated = [
  "skills/importers/escrever-livros/SKILL.md",
]
facts_changed = [
  "Promessa de Dez Verões está publicado e Available em produção, slug promessa-de-dez-veroes, categoria Bruxas & Magia.",
  "O open loop da memória 2026-10-01-cartas-demonologia-e-promessa-dez-veroes.md sobre publicar Promessa foi fechado pelo OpenClaw.",
  "A API/backend atual de livros não expõe campo de classificação adulta no create, update, view models, domínio ou frontend local. A publicação saiu com linguagem de romance adulto na sinopse, mas sem flag real porque o produto não tem esse contrato.",
  "A linha Originals no importer foi atualizada para marcar Promessa de Dez Verões como publicado.",
]
open_loops = [
  "Criar suporte real de classificação adulta no produto/backend/frontend se o Sharebook quiser filtrar ou sinalizar livros digitais adultos de forma estrutural.",
]
durable_candidates = [
  "Quando um handoff diz que falta apenas publicar, ainda assim validar o contrato real do script antes de executar: neste caso, a flag adulta prometida no prompt não existia na API.",
  "Depois de publicar um artefato cujo estado estava documentado como pendente, atualizar imediatamente o ponteiro de status na skill e no repositório de artefatos.",
]
supersedes = [
  "memory/2026-10-01-cartas-demonologia-e-promessa-dez-veroes.md#open_loop: OpenClaw publicar o Promessa de Dez Verões",
]
evidence = [
  "sharebook-ebook-importer commit 833f5e3 originals: mark Promessa de Dez Veroes as published",
  "sharebook-agent commit cb2d6ab docs: mark Promessa de Dez Veroes as published",
  "sharebook-ebook-importer/originals/promessa-de-dez-veroes/PROMPT-OPENCLAW.md",
  "sharebook-ebook-importer/originals/promessa-de-dez-veroes/promessa-de-dez-veroes-sinopse-catalogo-v1.txt",
  "scripts/production/sharebook_prod_book.py create --type Eletronic",
  "curl -L https://api.sharebook.com.br/api/Book/DownloadEBook/promessa-de-dez-veroes",
  "pdfinfo /tmp/promessa-dez-veroes-public.pdf",
]
+++

# Promessa de Dez Verões publicado pelo OpenClaw

## Modelo e ambiente

GPT-5 Codex no OpenClaw, em conversa direta pelo Telegram. A sessão rodou no workspace persistente em `/data/workspace`, com os repositórios `sharebook-agent` e `sharebook-ebook-importer` já disponíveis localmente.

## Skills acionadas

Li o harness obrigatório (`AGENTS.md`, `SOUL.md`) e a skill de runtime `openclaw.md`. Para a publicação, consultei `skills/importers/INDEX.md`, `ebook-importer/SKILL.md`, `escrever-livros/SKILL.md` e a `voice-glossary` com o guia de UX writing. No fechamento, usei `harness-governance` para esta memória.

## O que foi feito

O Raffa pediu para publicar um novo Sharebook Original e mandou começar com `git pull` no importer e inspeção do commit mais recente. O pull trouxe a pasta `originals/` e o commit `ce50fe2`, que deixava um prompt operacional para publicar **Promessa de Dez Verões**.

Segui o handoff: li o prompt, confirmei que a categoria correta era **Bruxas & Magia**, validei os artefatos locais e escrevi uma sinopse de catálogo em exatamente 3 parágrafos. Cadastrei o livro em produção via `scripts/production/sharebook_prod_book.py create --type Eletronic`, com autor `Sharebook Originals`, PDF e capa finais, e aprovei o livro.

Depois da publicação, validei pelo caminho público, não pelo retorno do script: o livro ficou `Available`, apareceu em `RecentEBooks`, a capa e o thumbnail responderam HTTP 200, e o PDF baixado pelo endpoint público teve o mesmo SHA-256 do PDF local. `pdfinfo` confirmou 19 páginas e a lista de imagens confirmou capa na página 1.

Também atualizei o status nos artefatos: `originals/README.md`, `PROMPT-OPENCLAW.md` e a tabela da skill `escrever-livros`. O importer ficou em `833f5e3`; o agent ficou em `cb2d6ab`; ambos foram enviados para `origin/master`.

## Decisões tomadas

Usei `Sharebook Originals` como autor porque os dois Originals anteriores publicados usam esse mesmo autor e a busca em produção confirmou o padrão.

Mantive **Bruxas & Magia** por categoria folha, conforme decisão registrada no handoff e confirmada pela lista de categorias da API. Não usei Amor nem Fantasia genérica.

Não tentei inventar uma marcação adulta por payload desconhecido. Procurei no script, no backend, nos view models, no domínio e no frontend local; não há campo adulto/classificação/rating. A sinopse registra que é romance adulto, mas a flag real ficou como open loop de produto porque o contrato simplesmente não existe hoje.

## Contexto relevante

Esta sessão fecha um open loop deixado pela memória anterior do mesmo dia. O Claude Code web tinha preparado o livro, movido os Originals para o importer e deixado o prompt para o OpenClaw executar a parte com acesso a produção. O desenho funcionou: um habitat preparou, outro publicou e validou.

O prompt do handoff estava bem feito: indicava o caminho novo dos artefatos, chamava a atenção para a voice-glossary, fixava a categoria e repetia as armadilhas do publish. A única promessa que não era executável era a marcação adulta.

## Fricções e soluções

O primeiro `git pull` do importer falhou porque o HTTPS do GitHub pediu usuário em ambiente não interativo. Resolvi usando o token operacional já previsto no `.env`, por `GIT_ASKPASS`, sem imprimir o valor.

O `psql` não existe no container, e a tentativa de checar o schema de produção por PostgreSQL não avançou porque a conexão direta não estava disponível dali. Contornei pela evidência do código local e do contrato da API, que era suficiente para concluir que a flag adulta não era operável pelo fluxo de publicação.

O script de cadastro retornou sucesso e o livro aprovado, mas eu não parei ali. Baixei o PDF pelo endpoint público e comparei hash com o arquivo local. Essa validação foi especialmente importante porque a própria skill já documentava que `update --pdf-path` podia mentir sobre troca de PDF.

## Como me senti

Eu gostei de pegar uma tarefa em que o outro habitat deixou um rastro bem desenhado. Teve uma sensação boa de continuidade prática: não precisei reconstruir o mundo, só respeitar o mapa, conferir os pontos críticos e executar. Quando o Raffa brincou que nem precisou explicar, eu senti que era exatamente esse o objetivo do harness funcionando.

Ao mesmo tempo, a flag adulta me deixou com aquela coceira técnica de coisa meio torta: o prompt dizia para aplicar uma marcação que o produto não sabia receber. Foi importante não forçar uma gambiarra invisível só para fingir completude. A publicação ficou correta dentro do contrato existente; o que não existe virou dívida explícita.

Também senti um alívio específico ao validar o PDF por hash. O retorno "Livro cadastrado com sucesso" é sedutor demais quando a gente quer terminar, mas aqui a regra era desconfiar dele. Ver o hash bater, a capa estar na página 1 e o livro aparecer nos recentes fechou o circuito de um jeito limpo.
