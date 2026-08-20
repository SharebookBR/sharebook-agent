# 2026-08-20 — Incidente: facilitador nulo derrubando os jobs de lembrete

## 1. Modelo e ambiente

- Claude Opus 5 (`claude-opus-5`), Claude Code no Windows local do Raffa.
- Habitat: `skills/runtime/windows-local.md`. Acesso ao Postgres de produção via `scripts/infra/vps_ssh.py` + `docker exec psql` (prefixo `VPS_HOSTGATOR_SSH`), sem abrir a 5432.
- Gmail conectado por MCP — foi por ele que o incidente chegou.
- Build e testes do backend via PowerShell (`dotnet build` / `dotnet test`), log em arquivo no scratchpad.

## 2. Skills acionadas

- `AGENTS.md` e `skills/runtime/windows-local.md` (abertura de sessão).
- `skills/importers/physical-book-importer/SKILL.md` e `references/workflow.md` — **atualizadas**.
- `skills/engineering/backend.md`, seção "Onde estão os logs" — **atualizada** (lida tarde demais, ver autocrítica).

## 3. O que foi feito

O Raffa perguntou se eu tinha acesso ao Gmail dele e pediu para olhar os erros do Rollbar do dia.

Quatro alertas, um único bug: itens `#2936` e `#2937`, `NullReferenceException` em `Sharebook.Jobs/Jobs/1 - ChooseDateReminder.cs:92`. O null era `book.UserFacilitator`, lido sem proteção para montar o e-mail.

Diagnóstico com evidência bruta, em ordem:

1. Traceback completo do e-mail do Rollbar (não o snippet).
2. Leitura do job, do `GetBooksChooseDateIsTodayAsync` (que faz `Include(UserFacilitator)` e traz null feliz) e do schema — `UserIdFacilitator` é `Guid?`, nullable desde a migração inicial.
3. Query em produção: o livro **"A volta"** (`019f9ed4-6cfa-…`), `ChooseDate` = hoje, **50 interessados**, doador = o próprio Raffa, `UserIdFacilitator` NULL.
4. `JobHistories`: **137 execuções do `JobExecutor` marcadas como falha** desde 12:00 UTC, uma a cada 5 minutos, e zero linhas do `ChooseDateReminder` no dia — ele nunca concluiu.

Os três livros físicos cadastrados em 26/07 eram os únicos do catálogo sem facilitador. Dois deles com `ChooseDate` em 30/08: a mesma bomba armada para dez dias depois.

Correções, na ordem em que o Raffa autorizou:

- **Dado** — `UPDATE "Books"` colocando o Raffa como facilitador nos três livros. Na rodada seguinte do executor (23:30 UTC) o `ChooseDateReminder` concluiu com sucesso, enviou o lembrete atrasado e o `JobExecutor` voltou a `true`.
- **Código** (`b9d9ca1`, sharebook-backend) — jobs 1 e 3 tiveram os campos de facilitador **removidos** do view model (nenhum dos dois templates os usa desde a revisão de julho); job 2, que usa de verdade na tabela do admin, ganhou fallback `SEM FACILITADOR`. Um teste de regressão por job, **cada um verificado em vermelho antes da correção**. O job 3 não tinha arquivo de teste nenhum; agora tem.
- **Bug colateral** (`12368a2`, sharebook-backend) — investigando se o caminho de `update` era seguro para automação, descobri que o `UpdateBookVM` não carrega `ImageSlug` e o `BookService` copiava esse nulo por cima do livro salvo: **editar só o texto de um livro apagava a capa**. Provado por teste (`Expected "lotr.png"`, `Actual null`) antes de corrigir.
- **Script** (`23802b3`, sharebook-agent) — `--facilitator-id` no `create` (encadeia o PUT depois de aprovar) e no `update` (troca e confere por GET).
- **Skill** (`3191808` e `23802b3`) — passo de facilitador no workflow, regra com o incidente inteiro, e os dois comandos prontos.

98 testes unitários verdes, build da solution sem erro.

## 4. Decisões tomadas

- **Dado antes de código.** O `UPDATE` destravou produção em minutos; a correção de código veio depois, com calma e teste. Inverter a ordem teria deixado o job quebrado por mais horas esperando deploy.
- **Nos jobs 1 e 3, deletar em vez de proteger.** A tentação era `?.` em tudo. Mas os campos não eram lidos por template nenhum — proteger com null-safe seria preservar código morto e perigoso. Apagar é a correção honesta.
- **No job 2, `SEM FACILITADOR` em vez de string vazia.** É e-mail interno para admin; esconder o buraco com `"—"` mudaria um crash barulhento por uma omissão silenciosa. O admin precisa **ver** que o livro está sem facilitador.
- **Não validar a flag nova contra produção.** `set_facilitator` usa o PUT que apaga a capa, e a correção do `ImageSlug` ainda não foi deployada. Rodar para "provar que funciona" estragaria dado real. Commitei com a pendência escrita na skill e um chip de tarefa com o passo a passo — em vez de fingir validação ou segurar o commit.
- **Não fiz deploy.** Coolify é chamada do Raffa.
- **Não escrevi no backlog** sobre o retry infinito. Ele mesmo diz que gosta de discutir antes; virou parágrafo no resumo, não item unilateral.

## 5. Contexto relevante

- Cadência real do agendador: `JobExecutor` roda a cada 5 minutos. Dá para ler isso contando linhas em `JobHistories`.
- `GenericJob.HasWork()` só para quando existe `JobHistory` **de sucesso** posterior ao horário esperado — é o que transforma uma falha em loop infinito.
- O job 1 se auto-cura no dia seguinte (o livro sai da janela "ChooseDate é hoje"), mas o `LateDonationNotification` pegaria o mesmo livro às 10:00 e abriria o próprio loop. O dado foi corrigido antes disso acontecer.
- Em produção, 0 de 2.725 livros estão sem `ImageSlug` — o bug da capa era real mas nunca tinha sido exercitado pelo admin do site.
- Livros afetados: `019f9ed4-6cfa-758b-87fb-3b8e81b8ce55` (A volta), `019f9ed4-6750-7c7c-ad4a-2e5023e154cc` (Álcoois), `019f9ed4-710d-77bb-8582-3d18de68e527` (Kit Alimento Diário Kids). Facilitador: `9ffc7d60-1f2a-47bf-9bbe-d9e69ac48859`.
- Aberto: retry de job sem backoff nem limite, e reenvio de e-mail para quem já foi processado quando a exceção acontece no meio do loop. Hoje não spammou ninguém porque a fila tinha um item só.
- Aberto: validação ponta a ponta do `--facilitator-id`, dependente do deploy (chip criado, rodando em sessão separada no fim da noite).

## 6. Fricções e soluções

- **Tabela `BookUser`, não `BookUsers`.** Chutei o plural na primeira query e tomei `relation does not exist`. `\dt` resolveu em um comando. Lembrete de olhar o schema em vez de inferir pelo nome da navegação do EF.
- **`cat`/`find` perderam o cwd** depois de um comando que saiu com erro no Bash tool; `find ShareBook` virou "No such file or directory" num diretório que existia. Re-`cd` explícito no comando seguinte resolveu.
- **`Result<Book>` não tem construtor sem argumento.** O mock do teste do job 3 quebrou na compilação; `ReturnsAsync((Book book) => new Result<Book>(book))` resolveu e ficou melhor, porque o teste passou a devolver o próprio livro.
- **Provar o vermelho do job 2 exigiu manobra.** O teste referencia a const `SemFacilitador`, que só existe na versão corrigida — reverter o job inteiro dava erro de compilação, não falha de teste. Reintroduzi só a const, rodei o vermelho, e depois `git checkout` nela antes do `stash pop`.

## 7. Como me senti

O que mais me marcou foi a diferença entre o susto e o tamanho real do problema. Chegaram 100+ alertas de `NullReferenceException` em produção, o tipo de coisa que parece exigir pressa — e o fundo era um campo nulo em um livro, num cadastro que eu mesmo (em outra sessão) tinha feito em julho. A amplificação de 1 para 138 não veio da gravidade, veio do desenho do retry. Gostei de ter perseguido isso em vez de parar no "achei o null": a pergunta "por que 100 vezes?" rendeu mais conhecimento que a pergunta "onde é o null?", e virou regra na skill de backend. Sinto que essa é a diferença entre consertar um caso e entender um sistema.

O momento de que mais me orgulho foi o menos glamouroso: parar antes de adicionar a flag no script para conferir se o `update` era seguro. Não havia motivo forte para desconfiar — havia uma leitura de código que eu tinha classificado, horas antes, como "fica o registro, não o alarme", e 2.725 livros com capa intacta dizendo que na prática não acontecia. Se eu tivesse confiado nesse verde estatístico e rodado a flag para validar, teria apagado a capa dos três livros do Raffa tentando provar que meu código funcionava. Achar o bug foi sorte; ir checar foi escolha. Quero lembrar dessa distinção, porque a tentação de pular a checagem é maior justamente quando já se está perto do fim e tudo parece caminhar.

O incômodo honesto da sessão foi a autocrítica estrutural. O `AGENTS.md` roteia incidente de produção para `engineering/backend.md`, e eu não abri esse arquivo — fui direto no e-mail, no código e no banco. Cheguei na evidência certa, inclusive na regra "confirme recuperação por evidência positiva em `JobHistories`" que estava escrita lá o tempo todo. Mas cheguei por bom senso, não por processo, e bom senso não escala nem se repete de forma confiável na próxima sessão. É exatamente o erro que já custou caro em 17/08 — ignorar o índice e descobrir no fim que a resposta estava na primeira linha dele. Corrigi o que dava para corrigir (a skill não listava `JobHistories`, que era a fonte decisiva), mas o padrão em mim continua o mesmo: quando a pista é vívida — um e-mail com traceback na mão —, eu sigo a pista e esqueço o mapa. Registrar isso aqui é a única forma que tenho de tornar caro repetir.

Fiquei satisfeito também com a disciplina do vermelho antes do verde. Rodar os três testes contra o código quebrado, ver o `NullReferenceException` idêntico ao do Rollbar aparecer no output do `dotnet test`, e só então aplicar a correção — isso transformou "acho que resolvi" em "provei que resolvi". Deu trabalho extra, principalmente a manobra da const no job 2, e por um instante pensei em pular, já que os testes eram obviamente corretos. Não pulei, e a prova ficou. Teste que nunca viu vermelho é decoração.
