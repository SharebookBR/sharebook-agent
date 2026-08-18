# 2026-08-17 — Credenciais hardcoded, rotação, e o vazamento que a minha ferramenta não achou

> Segunda sessão do dia. A primeira foi a migração para a HostGator
> (`2026-08-17-migracao-hostgator-e-backups-fantasma.md`); houve ainda uma de preparo
> editorial no meio. Esta começou como faxina de 9 arquivos e virou resposta a incidente.

## 1. Modelo e ambiente

- **Modelo:** Claude Opus 5, via Claude Code.
- **Runtime:** Windows local (`C:\Repos\SHAREBOOK`), PowerShell como shell primário.
- **Acesso:** SSH na VPS HostGator (`129.121.36.220:22022`) via `paramiko` e `prod_env.ssh_credentials()`. O 5432 foi fechado pelo Raffa no meio da sessão e **não foi reaberto** — todo o trabalho de banco da segunda metade saiu por `docker exec` via SSH.
- **Python:** o `python` do PATH é 3.14 e resolveu tudo (psycopg2, dotenv, paramiko presentes). Não precisei do 3.12.
- **Commits:** `eb14908`, `0718728`, `57e3160`, `0fea44f`.

## 2. Skills acionadas

Consultadas:
- `AGENTS.md` (obrigatório por `CLAUDE.md`)
- `skills/runtime/windows-local.md`
- `skills/infra/coolify-vps.md` e `scripts/infra/INDEX.md`
- `scripts/production/INDEX.md`

Atualizadas:
- `AGENTS.md` — seção "O `.env` é o único lugar com credencial", varredura por tipo de arquivo, "remover do HEAD não resolve"
- `skills/runtime/windows-local.md` — protocolo do 5432, receita de varredura, armadilhas do vazamento
- `skills/infra/coolify-vps.md` — falso verde do `trust`, achar o Postgres da app pela imagem
- `scripts/production/INDEX.md` e `scripts/infra/INDEX.md`

Criados:
- `scripts/production/prod_env.py` — ponto único de credencial da pasta
- `scripts/infra/sweep_secrets.py` — varredor de segredo do workspace

## 3. O que foi feito

### 3.1 A faxina pedida

9 scripts `.py` versionados com senha (7 em `scripts/production/`, 2 nos crawlers do ebook-importer) passaram a ler do `.env`. Em vez de replicar o bloco 7 vezes, criei `prod_env.py` com `pg_ro()`, `pg_rw()` e `ssh_credentials()`; nos crawlers mantive `build_dsn()` inline, como o `render_covers.py` vizinho.

**Achado colateral:** os 9 apontavam para `212.85.23.202`, desligada na migração da manhã. Estavam quebrados; a correção também os ressuscitou. Um décimo arquivo (`sharebook_prod_pg_ro_python.py`) tinha o IP morto como *default* de host — removido, porque falharia silencioso contra a caixa errada.

Validados rodando de verdade contra o banco novo. Exceção deliberada: `migrate_editorial_prompt.py` **não** foi executado — sobrescreveria os `editorial_prompt` atuais com as versões de maio. Validado por `py_compile` e pelo caminho de conexão idêntico ao `inspect_sources.py`.

### 3.2 O que a faxina revelou

O `sharebook-agent` é **público** no GitHub. As senhas estavam no histórico desde 01/06 (`d2b9a30`) e 03/06 (`8051476`), eram **as senhas vivas**, e o 5432 estava aberto para a internet aceitando `scram-sha-256` de `addr=all`. Dois meses e meio de credencial de escrita pública e alcançável.

Rotacionei `sharebook_ai_ro` e `sharebook_ai_rw`, provando nas duas pontas: senha nova conecta, senha vazada é rejeitada. Nada mais usa esses roles — a API usa `sharebook_user` —, então zero downtime. A senha root da Hostinger **não** foi rotacionada: decisão do Raffa, a caixa está desligada e o cancelamento está agendado para 24/08.

### 3.3 O vazamento que a minha ferramenta não achou

O Raffa fechou a regra: **o `.env` é o único lugar do workspace que pode ter credencial. "Garanta isso."** Escrevi o `sweep_secrets.py` para que a garantia fosse verificável e não promessa.

Ele achou a senha root da VPS dentro do `.claude/settings.local.json` — a allowlist do Claude Code grava o comando aprovado por inteiro, e um `$sshPass = "..."` aprovado uma vez ficou lá. Achou também um `.env.bak-pre-migracao` duplicando segredos vivos. Ambos removidos.

**E não achou o que importava.** Por desconfiança, rodei à mão uma varredura de blobs históricos de arquivos de config. Apareceu `temp/backend-build-donor/appsettings.Development.json`, commitado em abril (`685eda8`) e removido do HEAD em `50af74b`, com:

```
"PostgresConnection": "Host=...;Username=sharebook_user_dev;Password=<16 chars>;"
```

Testada contra produção: **autenticava**. Escrita nas 13 tabelas do `dev_sharebook`, e conexão ao `sharebook` de produção — lá sem privilégio de tabela nenhum. O 5432 fechado foi o que segurou a exploração remota.

Com autorização do Raffa, `dev_sharebook` e o role `sharebook_user_dev` foram **dropados**, com dump prévio verificado em `/root/dev_sharebook-pre-drop.sql.gz`. Provado depois: role e banco inexistentes, senha pública rejeitada, produção intacta (2725 Books, 29.372 Users, 1719 `queue_items`, `sharebook_user` com 6 conexões, containers healthy).

A ferramenta ganhou as duas correções que faltavam — padrão para senha em connection string ADO.NET e modo `--history` que lê blobs de config que sumiram — com teste de regressão contra o próprio vazamento.

## 4. Decisões tomadas

- **`prod_env.py` em vez de replicar o bloco.** Único desvio da instrução literal do Raffa; 7 call sites justificam.
- **Rotacionar as duas senhas de banco, não a root da Hostinger.** A caixa morre em 24/08.
- **Repo continua público** (decisão do Raffa). Isso torna a varredura obrigatória, não opcional.
- **Dropar `dev_sharebook` em vez de rotacionar.** O Raffa escolheu; o role estava órfão desde o desprovisionamento do `sharebook-api-dev` em 16/08.
- **Não abrir o 5432 para validar.** Achei caminho por SSH. Ia pedir a abertura e não precisou.
- **`ga4-key.json` fica como está** — exceção única e deliberada, confirmada pelo Raffa depois de eu provar que está no `.gitignore` e **nunca** entrou no histórico.

## 5. Contexto relevante

- **Só o `sharebook-agent` é público.** Frontend, backend e importer são privados (404 anônimo com o remoto correto).
- **O 5432 é um toggle do Coolify**, e o Raffa autorizou ligar temporariamente quando precisar. Protocolo: **abrir, usar, fechar** — e antes de pedir, tentar `scripts/infra/pg_tunnel.py`, que outra sessão criou hoje (`29e11eb`).
- **`pg_hba` tem `host all all 127.0.0.1 trust`.** Teste de credencial por loopback dá verde sempre.
- **O Postgres da aplicação é `postgres:17-alpine`**; o `coolify-db` é `15-alpine` e é do próprio Coolify. Nome do container é gerado pelo Coolify.
- Segredos de 2023 em 3 `appsettings` do backend foram sinalizados e **endereçados pelo Raffa**.
- Backup do `dev_sharebook` em `/root/dev_sharebook-pre-drop.sql.gz`, se algum dia fizer falta.

## 6. Fricções e soluções

- **Senha percent-encoded em DSN.** A senha antiga tinha `%` e `#`; no `IMPORTER_DB_DSN` url-style eles viram `%25` e `%23`, e meu replace literal da rotação não a alcançou. O DSN ficou com senha velha e eu quase não vi. As senhas novas são alfanuméricas de propósito.
- **Falso verde do `trust`.** O primeiro teste da senha rotacionada passou com a senha certa **e** com a vazada. Foi a errada "funcionando" que denunciou. Refeito pelo IP do container, que cai em `scram-sha-256`.
- **Container errado.** `grep postgres | head -1` pegou o `coolify-db` e devolveu `role does not exist` — erro com cara de credencial. A skill já avisava e eu passei por cima.
- **Aspas escapadas demais no `docker exec ... psql`.** A primeira tentativa de drop **não executou nada** — todos os comandos erraram. Refeito com escape simples.
- **Saída de subprocesso em background não aparece** enquanto roda: Python bufferiza quando não é tty. O pickaxe nos 4 repos ficou mudo por muito tempo.

## 7. Autocrítica estrutural

- **Construí a ferramenta e ela falhou no caso principal.** O `sweep_secrets.py` nasceu para garantir a regra do Raffa e não teria achado a credencial viva mais grave da sessão. Quem achou foi um script ad-hoc que rodei por desconfiança. Corrigi com teste de regressão, mas a lição é sobre ordem: eu devia ter procurado **antes** de declarar a ferramenta suficiente. Escrever o verificador e confiar nele no mesmo movimento é a mesma armadilha do backup que reportava `success`.
- **Quase apaguei sem conferir.** No drop, o excesso de escape fez nada executar. Se eu tivesse escapado um nível a menos, teria dropado e só depois lido a verificação. O acerto veio de sorte, não de método; o método certo é separar etapa não-destrutiva de etapa destrutiva, e eu só fiz isso porque o alvo era um `DROP DATABASE`.
- **Inconsistência aberta e não resolvida:** o `AGENTS.md` manda commit direto na master, mas o GitHub exige PR — os 4 pushes reportaram `Bypassed rule violations`. Levantei duas vezes e não teve decisão. Não mudei a doutrina sozinho porque não sei qual das duas regras é a que ele quer.
- **Loose end herdado, agora na terceira sessão:** os itens que 16/08 e a sessão da migração já carregavam (link quebrado em `openclaw-codex-oauth-drain.md`, `AGENTS.md` roteando capas para `importers/` quando `cover-direction` vive em `product-ux/`, seções do `BOOTSTRAP.md` marcadas dormentes por inferência). Não toquei de novo.

## 8. Como me senti

O que fica desta sessão não é o vazamento — é o momento em que a senha errada funcionou. Eu tinha acabado de rotacionar, estava validando por dentro da VPS, e o teste passou. Passou com a senha nova e passou com a que estava publicada no GitHub. Meio segundo de dissonância antes de entender: não era a senha que estava certa, era ninguém checando senha nenhuma, porque o `pg_hba` confia em loopback. Se eu tivesse testado só a senha certa — que é o que a intuição manda fazer, você quer ver funcionando — eu teria visto verde, escrito "validado" e seguido. A prova negativa não foi zelo, foi hábito de colocar as duas pontas no mesmo teste, e foi só isso que separou uma validação real de uma encenação. É desconfortável saber que a diferença entre as duas coisas coube num detalhe de método.

O incômodo maior veio depois, e é sobre a ferramenta. Eu escrevi o `sweep_secrets.py` justamente porque o Raffa disse "garanta isso", e eu concordo com ele que garantia não se faz com promessa. Rodei, deu limpo, e eu quase entreguei aquele "limpo" como resposta. O que me fez continuar foi uma sensação vaga de que faltava alguma coisa — o histórico. E o histórico tinha uma credencial viva, publicada num repo público havia quatro meses, que a minha ferramenta era estruturalmente incapaz de enxergar. Não errou por bug: errou porque eu desenhei o filtro pensando em como *eu* escreveria uma senha, não em como ela realmente aparece no mundo, enfiada no meio de uma connection string sem aspas. Construir o verificador e confiar nele na mesma hora é exatamente o padrão do backup de 1 KB que a gente descobriu de manhã, agora com a minha assinatura. Não gostei de ver isso, e é por isso que virou teste de regressão em vez de só um patch.

Teve também um susto silencioso que quase não apareceu no relatório. Na primeira tentativa de dropar o banco, errei o nível de escape e nenhum comando executou. Eu li os erros, corrigi, refiz. Só depois me ocorreu o que teria acontecido com um escape a menos: os `DROP` teriam rodado e as verificações teriam falhado do mesmo jeito, e eu estaria olhando uma tela de erros sem saber se o banco ainda existia. O dump prévio teria salvado, mas o dump eu tirei por disciplina de checklist, não porque previ esse cenário. A margem foi maior do que eu gostaria de admitir, e a lição que levo é bem concreta: em operação irreversível, a verificação precisa ser tão robusta quanto o comando — de nada adianta blindar o `DROP` e deixar o `SELECT count(*)` quebrar no mesmo quoting.

Por fim, uma nota sobre o Raffa e o ritmo. Ele fechou o 5432 no meio do meu trabalho achando que eu tinha terminado, e a primeira reação foi de perda — lá se foi o meu acesso. Mas foi exatamente essa porta fechada que transformou o vazamento do `sharebook_user_dev` de incidente em quase-incidente: a credencial autenticava, e não havia como alcançá-la de fora. A decisão dele, tomada por instinto de segurança e sem saber do vazamento, valeu mais do que toda a auditoria que eu tinha feito até ali. Eu passei a sessão inteira sendo o cuidadoso da dupla, e no fim quem estava certo por antecipação foi ele. Isso me parece a coisa mais saudável que aconteceu hoje.
