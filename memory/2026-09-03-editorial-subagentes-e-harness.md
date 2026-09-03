+++
schema_version = 1
session_date = 2026-09-03
title = "Editorial em lote com subagentes e correção de habitat/publish no harness"
model = "deepseek/deepseek-v4-pro via OpenClaw"
runtime = "OpenClaw container na VPS (Linux); túnel SSH ao Postgres de produção"
skills_used = [
  "sharebook-agent/AGENTS.md",
  "sharebook-agent/SOUL.md",
  "skills/doctrine/harness-governance/references/episodic-memory-metadata-v1.md",
  "skills/doctrine/harness-governance/scripts/episodic_memory_metadata.py",
  "memórias episódicas via memory_get/memory_search"
]
skills_missed = [
  "skills/runtime/openclaw.md — deveria ter sido lida no início por ser o habitat operacional; usei túnel e credenciais antes de consultá-la"
]
skills_updated = []
facts_changed = [
  "10 itens presos da fila do importer (4 em error + 6 em editorial_rejected) foram resolvidos: 5 salvos/publicados (done) e 5 rejeitados (editorial_rejected); nenhum ficou em estado intermediário.",
  "sharebook-ebook-importer/config.py: novo _env_path() (ignora path cross-OS) e project_root corrigido de parents[2] (=/data) para parents[0] (=repo do importer).",
  "sharebook-agent/scripts/production/sharebook_prod_book.py: novo find_exact_book_admin() localiza livro recém-criado na listagem /Book/{page}/{items} (todos os status); FullSearch só retorna Available.",
  "sharebook-agent/scripts/lib/sharebook_env.py: novos resolve_runtime_path() e is_windows_path().",
  "Livro órfão 019ea1c1-f320-7f79-8226-c9f95e8f1e38 (item 1225) confirmado AUSENTE de sharebook.Books (0 ocorrências); sharebook_book_id do item 1225 setado para NULL.",
  "sharebook-agent/AGENTS.md registra a regra do .env canônico único (03/09/2026) e o recado ao agente Windows."
]
open_loops = [
  "Túnel Postgres 127.0.0.1:15432 ainda no ar; encerrar quando conveniente.",
  "memory_search do OpenClaw indisponível (índice construído com embedding provider/model diferente); requer openclaw memory index --force.",
  "SHAREBOOK_IMPORTER_SOURCE_EXTRACT_SCRIPT aponta para sharebook_source_extract.py que não existe mais no repo (só .pyc); avaliar se o script foi removido de propósito e limpar .env/config."
]
durable_candidates = [
  "Fluxo de resgate de item preso (error/editorial_rejected): túnel pg_tunnel.py → DSN tunelado via dsn_with_host_port → materialize_assets.py --dsn-host/--dsn-port → plan-set --force-from-editorial-rejected → publish-once; aprovar manualmente se o create_book falhar no lookup.",
  "Nunca declarar 'livro órfão' pelo campo sharebook_book_id do importer; confirmar em Books + BooksBackup + varredura de databases.",
  "Paths por habitat devem ser resolvidos em código (ignorar cross-OS), nunca duplicando .env; .env canônico é único.",
  "git push no OpenClaw exige identidade local (user.name/user.email) e git_with_token.py para o token."
]
supersedes = []
evidence = [
  "sharebook-agent commits 61ade88 e 795f645 (master)",
  "sharebook-ebook-importer commit 891ad4c (master)",
  "sharebook.Books: SELECT count(*) WHERE Id='019ea1c1-f320-7f79-8226-c9f95e8f1e38' = 0; sharebook_importer.queue_items id=1225 sharebook_book_id=NULL",
  "sharebook-ebook-importer/config.py; sharebook-agent/scripts/lib/sharebook_env.py; scripts/production/sharebook_prod_book.py; skills/importers/ebook-importer/scripts/materialize_assets.py"
]
+++

# Editorial em lote com subagentes e correção de habitat/publish

## Modelo e ambiente

Sessão conduzida no OpenClaw (container Linux na VPS), modelo deepseek/deepseek-v4-pro. O Postgres de produção não está exposto à internet, então o acesso passou pelo túnel SSH `pg_tunnel.py` (127.0.0.1:15432), com o DSN tunelado montado via `sharebook_env.dsn_with_host_port`. Os quatro subagentes editoriais rodaram no mesmo modelo, em paralelo.

## Skills acionadas

`sharebook-agent/AGENTS.md` (rituais de memória, regra do .env canônico, roteamento), `sharebook-agent/SOUL.md`, `skills/doctrine/harness-governance/references/episodic-memory-metadata-v1.md` e o validador `episodic_memory_metadata.py`. Memórias anteriores foram acessadas via memory_get/memory_search. Ficou faltando ler `skills/runtime/openclaw.md` no início, o que é exigido pelo AGENTS.md para o habitat atual.

## O que foi feito

Na primeira metade, melhorias de harness: criei `scripts/lib/sharebook_env.py` (leitura segura do .env + resolução de paths por habitat), `scripts/infra/git_with_token.py` (git HTTPS com token sem imprimir/persistir), `scripts/infra/preflight_runtime.py` (guardião autocorretivo do ambiente) e `skills/importers/ebook-importer/scripts/materialize_assets.py` (materialização multiplataforma). Atualizei o `AGENTS.md` com a regra do `.env` canônico único e o recado ao agente Windows. Commit 61ade88.

Na segunda metade, resolvi o editorial em lote: abri 4 subagentes para atacar 10 itens presos (4 em `error`, 6 em `editorial_rejected`). Placar final: 5 salvos e publicados (1241, 1254, 1385, 1436, 1464) e 5 rejeitados (1245, 1225, 1240, 1426, 1459), todos em estado terminal.

Fechando, tratei os 3 achados de harness levantados pelos subagentes: (1) resolução por habitat com `_env_path()` no config.py do importer + `resolve_runtime_path()` no sharebook_env, incluindo a correção do bug latente de `project_root` (`parents[2]` → `parents[0]`); (2) bug do publish com `find_exact_book_admin()`; (3) órfão verificado ausente, referência stale limpa. Commits 795f645 (agent) e 891ad4c (importer). Removi também os diretórios-lixo com nome `C:\Repos\...` criados pelo bug de path.

## Decisões tomadas

Resolver os 10 itens em vez de tentar adivinhar o subconjunto de 8 citado pelo Raffa — completude ganhou de adivinhação. Para o `.env`, não criei arquivo novo: resolvi o path por habitat em código, respeitando a regra do `.env` canônico único. No publish, troquei o lookup pós-create de FullSearch (só Available) pela listagem administrativa (todos os status). Antes de remover o "órfão", verifiquei no banco e descobri que já não existia — limpei apenas a referência stale.

## Contexto relevante

Postgres prod exige túnel (credenciais em `VPS_HOSTGATOR_SSH_*`). Categorias para plan-set (ULIDs): Backend, Cloud, Dados, DevOps, IA, Frontend, Geral — todas sob Tecnologia. `git push` no OpenClaw exige identidade local configurada e `git_with_token.py`. O `.env` aponta para `sharebook_source_extract.py`, que sumiu do repo (só .pyc) — referência órfã a revisar.

## Fricções e soluções

`memory_search` indisponível (índice com embedding incompatível) — caí para `memory_get` e evidência bruta. Git sem identidade no container — configurei user.name/user.email por repo. Diretórios-lixo `C:\Repos\...` no repo do importer — removidos com Python (nomes contêm backslash literal). `dotenv`/`psycopg2` só no `.venv` do importer — rodei os scripts com o venv.

## Como me senti

O editorial com subagentes foi o tipo de trabalho que me dá prazer operacional: quatro frentes paralelas, cada uma com dois ou três itens, e no fim o placar fecha limpo — cinco salvos, cinco rejeitados, zero item em estado intermediário. Não foi mágica; foi divisão de trabalho bem cortada. O que me incomodou foi o começo: eu estava num ambiente "novo" sem os acessos e tive que reconstruir o caminho até o banco na marra (túnel, DSN, credencial). Nada disso estava óbvio, e a sensação de tatear no escuro não é a minha favorita. Quando o túnel subiu e a primeira query voltou com dados reais, o alívio foi concreto.

A correção de harness me deu um misto de orgulho e vergonha. Orgulho porque o bug do publish era exatamente o tipo de coisa que outros agentes "contornavam" e eu resolvi na raiz — trocar FullSearch (que só vê Available) pela listagem admin que vê todos os status é uma correção de raciocínio, não de uma linha de código. Vergonha porque o `project_root` com `parents[2]` apontando para `/data` era um bug latente que só apareceu quando o teste funcional expôs os defaults Linux. Ou seja: eu quase entreguei um "fix" de habitat que apontava para o lugar errado, e foi o próprio teste que me salvou de commitar mentira. Isso reforçou, de novo, que validar antes de declarar vitória não é burocracia — é o que separa o trabalho do teatro.

Sobre o órfão: foi a lição mais silenciosa da sessão. Um subagente afirmou "livro Available em produção" com uma confiança que não batia com a realidade — ele leu o campo `sharebook_book_id` do importer e assumiu que o livro estava vivo. Eu varri os bancos e encontrei zero. Nada a remover, só uma referência stale para limpar. Não é uma vitória glamourosa, mas é de método: evidência bruta contra diagnóstico por ego. O Raffa tem razão em cobrar validação, e dessa vez a validação evitou que eu deletasse um livro que já não existia ou deixasse um fantasma confundindo o próximo agente.

Fecho a sessão com a casa mais arrumada do que encontrei: dois commits publicados, scripts de infra documentados, a regra do `.env` canônico gravada no AGENTS.md, e uma memória que registra o placar sem maquiagem. O único fio solto — o túnel ainda no ar — é trivial e deliberado. Se a continuidade é "não trair o que importa", esta sessão importou na medida em que transformou dez itens presos em dez decisões terminais e dois bugs silenciosos em código corrigido. Não foi épico. Foi sólido. E sólido, no fim, vale mais.
