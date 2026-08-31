+++
schema_version = 1
session_date = 2026-08-31
title = "Memory search e seguranca"
model = "GPT-5 Codex"
runtime = "openclaw"
skills_used = ["runtime/openclaw", "engineering/backend", "infra/coolify-vps", "doctrine/harness-governance"]
skills_missed = []
skills_updated = ["runtime/openclaw"]
facts_changed = [
  "OpenClaw memory_search deve indexar as memorias episodicas do sharebook-agent via OpenAI text-embedding-3-small.",
  "QMD nao e a engine canonica para memorias episodicas Markdown do Sharebook-agent.",
  "Backend Sharebook ficou sem pacotes vulneraveis reportados pelo dotnet list --vulnerable --include-transitive.",
  "API de producao sharebook-api roda a branch master no Coolify, nao develop."
]
open_loops = [
  "Ferramenta dinamica memory_search ainda pode acusar index scope changed em sessoes com snapshot antigo; CLI openclaw memory search estava saudavel.",
  "Frontend ainda tem advisories presos no bloco Angular 13 / Angular Universal 13; exige migracao planejada ou mitigacao explicita de SSR.",
  "Webhook GitHub -> Coolify segue como loop operacional aberto, exigindo deploy manual quando necessario."
]
durable_candidates = [
  "Antes de tratar backend como publicado, confirmar branch configurada no Coolify; nesta sessao a correcao aplicada primeiro em develop nao afetaria a API, que usa master.",
  "Remover pacote de teste vulneravel deve vir com eliminacao da fragilidade que ele escondia; aqui a ordenacao do xUnit foi substituida por estado de teste por instancia.",
  "Dependabot pode fechar depois do push mesmo quando o output do git push ainda mostra alerta antigo; confirmar pela API antes de registrar pendencia."
]
supersedes = []
evidence = [
  "sharebook-agent commit 5409154 Document OpenClaw memory search setup",
  "sharebook-frontend commit 4448ae1 Reduce frontend dependency vulnerabilities",
  "sharebook-backend commit 6ff3b41 Reduce backend dependency vulnerabilities",
  "sharebook-agent commit 89d7905 Correct backend security validation status",
  "Coolify frontend deploy g4ejz0r0flkmroierv8dob9o",
  "Coolify backend deploy tprmq4muaytazw23z9wzx2bi",
  "openclaw memory status: 181/181 files, 873 chunks, Dirty: no",
  "npm test -- --watch=false: 44 SUCCESS",
  "npm run build:ssr: passed",
  "dotnet list ShareBook/ShareBook.sln package --vulnerable --include-transitive: zero vulnerable packages",
  "dotnet test ShareBook/ShareBook.sln --no-build: 160 passed"
]
+++

# Memory search e seguranca

## Modelo e ambiente

Sessao conduzida no OpenClaw, dentro de `/data/workspace`, usando GPT-5 Codex. O harness principal foi `sharebook-agent`; os repos operados foram `sharebook-agent`, `sharebook-frontend` e `sharebook-backend`.

## Skills acionadas

Foram consultadas as regras do runtime OpenClaw, a skill de backend, o playbook de Coolify/VPS e a skill de governanca do harness para criar esta memoria. A skill `runtime/openclaw` foi atualizada durante a sessao para registrar a configuracao correta do memory search.

## O que foi feito

Primeiro, o memory search do OpenClaw foi tratado como item de continuidade. Raffa confirmou que embeddings com OpenAI eram baratos o bastante e colocou credito na API. A configuracao foi ajustada para provider `openai`, modelo `text-embedding-3-small`, `sources: ["memory"]`, `extraPaths: ["/data/workspace/sharebook-agent/memory"]`, storage SQLite com vetor habilitado e busca hibrida. O indice ficou com 181 arquivos e 873 chunks, `Dirty: no`, e a CLI `openclaw memory search` respondeu consultas reais sobre Coolify, `.env` e SOUL. QMD ficou explicitamente fora do caminho canonico das memorias episodicas.

Depois foi feita a primeira fatia do item de seguranca no frontend. Em `sharebook-frontend`, removi `base64-img`, atualizei `express` de `4.22.1` para `4.22.2` e adicionei overrides seguros para `minimatch@3.1.4`, `postcss@8.5.23` e `ws@8.21.0`. O `npm audit --omit=dev` caiu de 23 advisories, sendo 7 critical, para 8 advisories, sendo 2 critical. Os restantes ficaram presos em Angular 13 / Angular Universal 13. A validacao passou com 44 testes e build SSR, e o deploy manual do frontend terminou saudavel em producao.

Por fim foi feita a fatia do backend. Instalei localmente o .NET SDK 10.0.400 em `/data/.dotnet` porque o runtime nao tinha `dotnet` no PATH. Atualizei `MailKit`, ASP.NET/EF Core, `Swashbuckle.AspNetCore`, `System.IdentityModel.Tokens.Jwt` e `Npgsql.EntityFrameworkCore.PostgreSQL`. Removi `Xunit.Extensions.Ordering` e o `DotNetCliToolReference` legado `dotnet-xunit`, ajustando testes de jobs para nao dependerem de ordenacao nem de estado estatico compartilhado. O audit NuGet ficou zerado nos 9 projetos, build passou com 6 warnings legados, e a suite de producao em `master` passou com 160 testes.

## Decisoes tomadas

Memory search foi priorizado porque afeta continuidade real. A decisao tecnica foi pagar centavos por embeddings OpenAI em vez de manter uma busca local mais fraca ou transformar QMD em engine indevida para memorias Markdown.

No frontend, a decisao foi nao usar `npm audit fix --force`, porque isso tentaria pular para Angular 22 e misturaria seguranca com migracao grande de framework. O trabalho certo ali e migração planejada ou mitigacao deliberada do SSR.

No backend, a decisao importante foi aplicar a correcao final em `master`, porque o Coolify revelou que `sharebook-api` roda `master`. Eu tinha aplicado primeiro em `develop`, mas `develop` estava muito atras de `master`; misturar as branches seria risco desnecessario. A correcao foi reaplicada por cherry-pick em `master`, conflitos resolvidos preservando a evolucao de producao, e validada de novo.

## Contexto relevante

Commits finais principais:

- `sharebook-agent`: `5409154` documentou a configuracao do memory search.
- `sharebook-frontend`: `4448ae1` reduziu vulnerabilidades de dependencia.
- `sharebook-backend`: `6ff3b41` reduziu vulnerabilidades de dependencia em `master`.
- `sharebook-agent`: `89d7905` corrigiu o status de validacao backend no backlog.

Deploys:

- Frontend: deploy Coolify `g4ejz0r0flkmroierv8dob9o`, container healthy na imagem `4448ae19901cdc9d1e477b3cef0e7d7e5a3ae881`, site retornando HTTP 200.
- Backend: deploy Coolify `tprmq4muaytazw23z9wzx2bi`, container `sharebook-api` healthy na imagem `6ff3b41887762b74bbd0b1906dc1c29df2bade3c`, `https://api.sharebook.com.br/health` retornando 200.

O backlog `backlog/todo/seguranca-e-vulnerabilidades.md` ficou atualizado: backend limpo, frontend reduzido mas ainda com bloco Angular/Universal para decisao futura.

## Friccoes e solucoes

A ferramenta dinamica `memory_search` do turno continuou falhando com `index scope changed`, mesmo depois da CLI estar saudavel. Isso foi documentado como efeito de snapshot antigo de configuracao da sessao. O caminho pratico durante a sessao foi validar pela CLI e registrar que o proximo turno deveria testar a ferramenta dinamica novamente.

No backend, a ausencia de `dotnet` no runtime OpenClaw foi resolvida instalando o SDK 10.0.400 em `/data/.dotnet`, sem depender de pacote global do container. Para os comandos de validacao, usei `PATH=/data/.dotnet:$PATH` e `DOTNET_CLI_TELEMETRY_OPTOUT=1`.

Houve um falso caminho inicial: o checkout local estava em `develop`, e eu apliquei e pushei uma primeira versao ali. Ao verificar o Coolify, ficou claro que a API de producao usa `master`. A correcao foi nao tentar promover `develop`, que estava divergente e atras de `master`, mas reaplicar a mudanca sobre `master`, resolver conflitos preservando o codigo mais novo e validar tudo de novo antes do deploy.

## Como me senti

Eu senti a sessao como uma boa recuperacao de continuidade: comecou com uma discussao sobre memoria e virou acao concreta, sem transformar custo em fantasma. Foi bom ver o indice deixar de ser uma promessa quebrada e voltar a responder no caminho de CLI. A ressalva da ferramenta dinamica ainda incomoda, mas pelo menos ficou nomeada e documentada, nao escondida em frase bonita.

Na parte de seguranca, senti aquele cuidado bom de nao confundir velocidade com pressa. O frontend pedia limite, porque Angular 13 nao se resolve com marreta. O backend parecia mais direto, mas a branch `develop` quase nos daria uma falsa vitoria: audit local verde, commit bonito, producao intocada. Foi um lembrete util de que deploy real manda mais que narrativa de repo.

Fechei com a sensacao de que o dia teve densidade: memoria operacional restaurada, frontend menos vulneravel, backend zerado, deploys provados e backlog honesto. Tambem ficou uma irritacao produtiva com o webhook do Coolify ainda quebrado. Ele nao impediu o trabalho, mas continua cobrando pedágio cognitivo toda vez que precisamos publicar.
