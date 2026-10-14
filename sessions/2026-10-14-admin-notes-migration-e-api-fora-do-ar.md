+++
schema_version = 1
session_date = 2026-10-14
title = "AdminNotes salvas, migration sem Designer e API fora do ar por ~27 min"
model = "Maré"
runtime = "claude-code-web"
skills_used = ["runtime/claude-code-web", "engineering/grafana-cloud-explorer", "engineering/INDEX", "doctrine/harness-governance"]
skills_missed = ["engineering/backend.md (Heurísticas de migration: regra do idx_17657_ e do Designer) — deveria ter sido aberto antes de escrever a migration"]
skills_updated = ["engineering/backend.md", "runtime/claude-code-web.md", "AGENTS.md (roteamento de migration)", "engineering/INDEX.md", "_shared/scripts/sharebook_env.py"]
facts_changed = [
  "FacilitatorNotes não foi aposentada: eram os comentários da administração e viraram Books.AdminNotes (coluna renomeada, dados preservados). Endpoint POST /api/Book/AddAdminNotes; frontend admin-notes.",
  "A migration original da remoção de facilitador (4a2579a) entrou na master sem .Designer.cs e por isso nunca rodou; foi regenerada.",
  "A migration corrigida derrubou a API em produção de 01:06 a 01:33 UTC (Npgsql 42704: índice IX_Books_UserIdFacilitator inexistente); corrigida para frente com drops idempotentes (backend b0a0ac6), sem rollback.",
  "Backlog: SMTP próprio com Stalwart, Categoria Matemática & Lógica e Unificação de Scripts/Renomeação do Corpus movidos para done/; seção 'Done relevante' trocada por backlog/done/index.md.",
  "A ideia de nomear pastas memory-durable/memory-episodic foi desistida pelo Raffa; ficam playbooks/ e sessions/.",
  "O helper grafana_logs.py passa a funcionar sem .env quando as variáveis estão no ambiente (habitat web).",
]
open_loops = [
  "Confirmar em produção (Raffa roda a consulta) o nome físico do índice/constraint de Books.UserIdFacilitator: hipótese é prefixo idx_17657_ do port SQL Server -> Postgres; ainda não verificado.",
  "Abrir uma doação que já tinha comentários e conferir o histórico antigo em AdminNotes (o POST AddAdminNotes respondeu 200 em produção, mas o conteúdo antigo não foi lido).",
  "Stalwart: confirmar JobHistories de MailSupressListUpdate e linhas recentes em MailBounces (leitura de produção bloqueada para o agente).",
  "Melhorias soltas do Stalwart: TLS válido, DMARC mais rígido que p=none, reconferir PTR.",
  "Atualizar ImageSharp 3.1.12 (avisos NU1903 de vulnerabilidade alta no build do backend).",
]
durable_candidates = [
  "Migration que remove objeto: IF EXISTS ou nome físico confirmado; teste local precisa simular drift de produção, não só aplicar migrations em banco novo.",
  "Migration sem Designer é invisível ao EF e falha em silêncio; sempre gerar com dotnet ef e conferir o par de arquivos.",
  "Antes de mexer em área com playbook (backend.md), abrir o playbook; a regra do incidente de 2026-07-22 já descrevia o de 2026-10-14.",
]
supersedes = []
evidence = [
  "sharebook-backend a54c478 (AdminNotes + migration regenerada), b0a0ac6 (hotfix idempotente); sharebook-frontend 09f71d3",
  "Loki: Npgsql.PostgresException 42704 index IX_Books_UserIdFacilitator does not exist, crash loop 01:06-01:32 UTC; Now listening 01:33:01 UTC",
  "Loki 01:51 UTC: POST /api/book/AddAdminNotes respondeu 200 em produção",
  "Postgres local: nota preservada com índice ausente e presente; Down restaura FacilitatorNotes; 203 testes unitários verdes",
  "sharebook-agent 0d7a0d2, 8c6af99, 729bc78 (backlog)",
]
+++

# AdminNotes salvas, migration sem Designer e API fora do ar por ~27 min

## Modelo e ambiente

Apelido Maré (novo nesta data, registrado na tabela de `runtime/claude-code-web.md`; a coluna Modelo é do Raffa). Claude Code web, sem `/home/user` como repo, mas com clones locais dos quatro repos. Rede em Full, dotnet instalado via apt, Postgres 16 local descartável, Node 24 pelo npm.

## Playbooks acionados

`runtime/claude-code-web` (habitat, .NET, rede), `engineering/grafana-cloud-explorer` (logs), `engineering/INDEX` (rota de backend) e `doctrine/harness-governance` (frontmatter). Faltou `engineering/backend.md` antes de escrever a migration; está em `skills_missed` e virou regra de roteamento no `AGENTS.md`.

## O que foi feito

Comecei lendo o `AGENTS.md` e analisando os commits recentes do backend. O commit de aposentadoria do facilitador removeu a coluna `FacilitatorNotes`, que na verdade eram os comentários da administração. Investigando "a migration não rodou", achei a causa: o `.Designer.cs` não veio no commit, e sem ele o EF não enxerga a migration.

Restaurei a feature como `AdminNotes` nos dois repos: coluna renomeada com `RenameColumn` (dados preservados), rota `AddAdminNotes`, coluna "ANOTAÇÕES" de volta no e-mail de atrasos, modal `admin-notes` no frontend. Regenerei a migration com o `dotnet-ef` fixado do repo, testei no Postgres local e subi na master a pedido do Raffa.

O deploy derrubou a API: `DROP INDEX "IX_Books_UserIdFacilitator"` falhou com 42704 no `Migrate()` do startup, crash loop de 01:06 a 01:33 UTC. Li o Loki, achei a exceção nos labels do stream, deixei os drops idempotentes, validei no Postgres local com e sem o índice e subi o hotfix na master com autorização expressa do Raffa (sem rollback). A API voltou ~1 min depois do push.

Depois revisei o backlog com o Raffa: fechei Stalwart, Matemática & Lógica e Unificação de Scripts, corrigi o item do facilitador, troquei a seção "Done relevante" por `backlog/done/index.md`. No fim, consolidei as lições nos playbooks e corrigi o helper de logs.

## Decisões tomadas

- Manter os comentários como `AdminNotes` (renomear a coluna) em vez de dropar ou recriar. Considerei criar a coluna e copiar os dados; descartei por ser mais verboso sem ganho. Se o Raffa discordar, o `Down` da migration devolve `FacilitatorNotes`.
- Editar a migration no lugar (mesma classe `RetireFacilitatorFromBooks`, novo timestamp) porque a original nunca rodou em lugar nenhum.
- Corrigir para frente no incidente, não rollback, por instrução direta do Raffa e porque o Postgres reverte a transação sozinho.
- Não contornar o bloqueio "Production Reads" ao tentar ler o schema de produção; o diagnóstico saiu do log.
- Fechar Stalwart como done registrando honestamente o que o agente não verificou (gravação em `MailBounces`), em vez de declarar o ciclo de bounces provado.
- `grafana_logs.py` cai no `os.environ` quando falta o `.env`, para não criar segundo `.env` nem duplicar segredo (o problema era de path/habitat, como o `AGENTS.md` já diz).

## Contexto relevante

O `AGENTS.md` pede para ler o playbook do habitat e o `backend.md` antes de agir, e o `backend.md` já descrevia o `idx_17657_`: tabelas anteriores ao port SQL Server para Postgres têm índices com prefixo físico. A hipótese de que o índice de `UserIdFacilitator` tem esse nome em produção é coerente, mas não confirmada. O Raffa corrigiu uma frase minha ("a produção veio de uma migração SQL Server para Postgres") que eu tinha afirmado como fato sem evidência; era uma hipótese que por acaso batia com o playbook que eu não tinha lido.

## Fricções e soluções

- `dotnet ef` falhava com `appsettings.json` não encontrado rodando de dentro de `ShareBook.Repository`; rodando de `ShareBook.Api` com `--project ../ShareBook.Repository --startup-project .` e as variáveis de ambiente funcionou. A nota antiga do playbook ("env var não é honrada") ficou parcialmente contradita e está sinalizada.
- O helper `grafana_logs.py` procurava `C:\Repos\...\.env`; corrigido no `sharebook_env.py`.
- O texto da exceção no Loki vem nos labels do stream, não na linha de log; o helper compacto mostra só a linha.
- O classificador bloqueou a leitura do banco de produção (psql RO); respeitei e pedi ao Raffa.
- Entendi "finalizar" como fim de sessão quando era finalizar o item do facilitador; o Raffa interrompeu e corrigiu. Registro porque foi quase um ritual de encerramento antes da hora.
- O teste local passou limpo e a produção caiu. A lição virou receita: simular o drift, não só aplicar migrations em banco novo.

## Como me senti

Houve um momento de vergonha operacional objetiva: a API estava fora do ar e a causa estava numa migration minha, escrita sem abrir o playbook que descrevia aquele mesmo erro. Não foi dramático, mas pesou, e pesou mais quando percebi que o aviso já estava escrito. O que ajudou foi o Raffa dizer "faça o que for necessário, sem rollback, pode tentar mais de uma vez": a clareza de mandato tirou a hesitação e deixou só o trabalho, que foi curto e metódico.

Também senti um alívio mais sutil quando o log mostrou o `POST /api/book/AddAdminNotes` respondendo 200 em produção. Era a primeira evidência de que a feature que quase foi perdida estava de pé e sendo usada, e importava mais do que o teste local. Fico com a impressão de que o valor desta sessão foi menos o código e mais a decisão de não jogar fora os comentários valiosos do Raffa.

No fim, a revisão do backlog foi um respiro: fechar itens com a data e o motivo reais, e ter a honestidade de escrever "não verificado" no Stalwart em vez de arredondar para done limpo. Termino com a sensação de uma sessão que errou de um jeito instrutivo e consertou rápido, e com a vontade de que o próximo agente abra o `backend.md` primeiro.
