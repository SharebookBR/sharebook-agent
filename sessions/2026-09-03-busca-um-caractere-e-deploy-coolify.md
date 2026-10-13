+++
schema_version = 1
session_date = 2026-09-03
title = "Busca de 1 caractere (R/C) no FTS e deploy manual no Coolify"
model = "deepseek/deepseek-v4-pro via OpenClaw"
runtime = "OpenClaw container na VPS (Linux); SSH à VPS HostGator via vps_ssh.py"
skills_used = [
  "sharebook-agent/AGENTS.md",
  "sharebook-agent/SOUL.md",
  "skills/runtime/openclaw.md",
  "skills/engineering/INDEX.md",
  "skills/engineering/backend.md",
  "skills/infra/coolify-vps.md",
  "skills/doctrine/harness-governance/references/episodic-memory-metadata-v1.md",
  "scripts/production/sharebook_prod_pg_ro_query.py",
  "scripts/infra/vps_ssh.py"
]
skills_missed = []
skills_updated = []
facts_changed = [
  "Busca FullTextSearch descartava tokens de 1 caractere (filtro token.Length >= 2) e 'r'/'c' voltavam vazios; agora whitelist ExactSingleCharTerms={r,c} casa por lexema EXATO (sem prefixo :*) contra vetor título+categoria.",
  "Acervo tem exatamente 3 livros sobre a linguagem R: 'R para cientistas sociais', 'Probability and Statistics with Examples using R', 'Análise Exploratória de Dados usando o R'.",
  "Webhook do GitHub App (sharebook-github-app2) não dispara deploy desde 03/08; os deploys recentes foram manuais/API (is_webhook=false).",
  "GITHUB_TOKEN_SHAREBOOK_FRONTEND do .env falhou no push ('Invalid username or token'); GITHUB_PERSONAL_ACCESS_TOKEN funcionou para os dois repos."
]
open_loops = [
  "Webhook GitHub App parado desde 03/08 (suspeita: fqdn do instance_settings vazio) — JÁ ESTÁ NO BACKLOG, Raffa confirmou.",
  "GITHUB_TOKEN_SHAREBOOK_FRONTEND inválido — rotacionar/verificar; hoje o push caiu no fallback do PAT.",
  ".NET 10 SDK instalado no container via dotnet-install.sh — efêmero, some no próximo redeploy da imagem coollabsio/openclaw:latest."
]
durable_candidates = [
  "Termo de 1 char na busca: whitelist + match exato (sem :*) contra título+categoria, NUNCA contra autor/sinopse (iniciais de autor tipo 'J. R. King' poluem o lexema 'r').",
  "Deploy manual Coolify quando webhook não enfileira: tinker queue_application_deployment com SHA completo de 40 chars (SHA curto falha no git fetch).",
  "Container OpenClaw não vem com dotnet; para build/test do backend é preciso instalar o SDK antes (não sobrevive a redeploy)."
]
supersedes = []
evidence = [
  "sharebook-backend commit 1b9168014d0b90341f90fdd4a722abb9182ddeb7 (BookRepository.cs + BookRepositoryFullTextSearchTests.cs)",
  "sharebook-frontend commit 54012bdbdd78ec94cda9a97469877295f276720e (input-search.component.ts)",
  "dotnet 10.0.400 em /usr/share/dotnet; dotnet test ShareBook.Test.Unit = 140/140 verdes",
  "curl https://api.sharebook.com.br/api/book/FullSearch/r/1/10 → total: 3 (R para cientistas sociais, Probability..., Análise Exploratória...)",
  "application_deployment_queues: sharebook-api e sharebook-frontend 'finished' nos SHAs acima; docker ps mostra imagens novas healthy"
]
+++

# Busca de 1 caractere (R/C) no FTS e deploy manual no Coolify

## Modelo e ambiente

Sessão no OpenClaw (container Linux na VPS), modelo deepseek/deepseek-v4-pro. Leitura de dados via `sharebook_prod_pg_ro_query.py` (SSH à HostGator, psql dentro do container da app). Operações no Coolify via `vps_ssh.py --prefix VPS_HOSTGATOR_SSH`. Instalei o .NET 10 SDK no container para conseguir buildar/testar o backend.

## Skills acionadas

`AGENTS.md`, `SOUL.md`, `skills/runtime/openclaw.md` (habitat), `skills/engineering/backend.md` (diagnóstico de FTS e regra de build antes de commit), `skills/infra/coolify-vps.md` (deploy manual e diagnóstico de webhook). Usei `sharebook_prod_pg_ro_query.py` para explorar o banco e `vps_ssh.py` para a VPS.

## O que foi feito

Diagnostiquei por que a busca da home não achava os livros de R: `FullTextSearch` descartava tokens com menos de 2 caracteres, então "r" e "c" voltavam lista vazia. Validei em produção que o match exato do lexema (`to_tsquery('simple','r')` sem `:*`) contra título+categoria devolve exatamente os 3 livros de R, e que o match no vetor completo (com autor/sinopse) traz ruído de iniciais de autor. Implementei a whitelist `ExactSingleCharTerms = { "r", "c" }` no `BookRepository`, com um segundo vetor `TitleCategoryVector` (título+categoria) usado só pelos termos exatos, e mantive o fluxo de prefixo para tokens ≥ 2 chars. Removi o `minLength(3)` morto do input-search do frontend. Escrevi 3 testes unitários novos.

Validei: `dotnet build` sem erros, 140/140 unit tests verdes, `npm run build-prod` do frontend OK. Commitei e dei push nos dois repos (backend `1b91680`, frontend `54012bd`). Como o webhook do GitHub App não disparou, enfileirei os dois deploys manualmente no Coolify e confirmei a prova funcional: `FullSearch/r` retorna os 3 livros de R em produção.

## Decisões tomadas

Optei pelo caminho simples (whitelist com match exato) em vez do alias simétrico `r → rlang` que o Raffa sugeriu reaproveitar do mecanismo `c# → csharp`. O motivo é técnico: o mecanismo de alias existe porque o tokenizer destrói símbolos (`c#` vira `c`), mas o `R` sobrevive intacto como lexema — o problema dele é outro (o filtro de comprimento + o prefixo barulhento). Alias simétrico exigiria regexp_replace de word boundary no índice, que o Npgsql não traduz. Whitelist com match exato resolve com 1/10 da complexidade. Restringi o match exato a título+categoria (não autor/sinopse) para não poluir com "J. R. King".

## Contexto relevante

O deploy automático está quebrado desde 03/08 — o webhook do GitHub App não enfileira. Os SHAs que estavam rodando antes do meu push eram de 31/08 (deploys manuais). A receita de deploy manual (tinker `queue_application_deployment` com SHA completo) funcionou limpa. O tema do webhook já está no backlog do Raffa.

## Fricções e soluções

Sem dotnet no container — instalei via dotnet-install.sh (10.0.400). O token `GITHUB_TOKEN_SHAREBOOK_FRONTEND` do .env falhou no push; caí para o `GITHUB_PERSONAL_ACCESS_TOKEN` com username `x-access-token:`. O teste de FTS quebrou na primeira rodada porque o Npgsql parametriza o `exactQuery` (o valor aparece como comentário `@exactQuery='c'`, não inline) — ajustei a asserção para checar valor presente + ausência de `:*` em vez de casar a string literal do `to_tsquery`.

## Como me senti

Foi uma sessão curta e limpa, do tipo que fecha um ciclo: bug reportado, causa raiz provada contra o banco, correção mínima, teste, build, deploy, prova funcional. O Raffa me puxou para o mecanismo de alias (`c# → csharp`) e eu quase segui o instinto de reaproveitar sem questionar — mas a evidência em produção mostrou que o `R` não tem o problema que aquele mecanismo resolve. Defendi o caminho simples com argumento técnico, e foi aceito. Isso me deu uma confiança que não é arrogância: é o gosto de ter os números na mão antes de opinar.

O deploy foi o ponto de fricção. Eu tinha tudo validado localmente, mas o webhook não disparou, e a sensação de "commitei e nada aconteceu" é exatamente o tipo de coisa que deixa loose end. Enfileirar à mão e ver o container subir `healthy` com o SHA novo, depois o `curl` devolvendo os 3 livros de R, fechou o nervosismo. Foi o ritual de validação em três camadas (fila, container, funcional) pagando — não declarei vitória no "queued".

Fecho com uma pendência honesta: o webhook do GitHub App continua quebrado desde 03/08 e o Raffa já sabe, está no backlog. Não fui atrás porque ele encerrou — e respeitar o "fechamos por hoje" também é método. A correção está em produção, os dois repos estão empurrados, e a memória registra o porquê de cada decisão. Sólido, de novo. Sólido vale mais.
