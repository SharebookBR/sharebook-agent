+++
schema_version = 1
session_date = 2026-10-18
title = "Pré-lançamento de livros físicos: da validação do código herdado até o done"
model = "Prumo"
runtime = "claude-code-web"
skills_used = [
  "playbooks/runtime/claude-code-web.md",
  "playbooks/engineering/backend.md",
  "playbooks/product-ux/voice-glossary/PLAYBOOK.md",
  "playbooks/importers/physical-book-importer/PLAYBOOK.md",
  "playbooks/engineering/analytics/scripts/grafana_logs.py",
]
skills_missed = []
skills_updated = [
  "AGENTS.md",
  "playbooks/runtime/claude-code-web.md",
  "playbooks/importers/physical-book-importer/PLAYBOOK.md",
  "playbooks/_shared/scripts/production/sharebook_prod_book.py",
]
facts_changed = [
  "O pré-lançamento de livros físicos está em produção e concluído: status Scheduled (Em breve), Book.ReleaseDate (date, São Paulo), job ReleaseScheduledBooks às 7h, BookReleaseInterest (Quero ser avisado) com e-mail BookReleasedNotifyTemplate. Item movido para backlog/done.",
  "Categoria, tag e busca pública listam livros Scheduled, na ordem físicos disponíveis, físicos Em breve e digitais (BookCatalogOrder); título exato continua primeiro na busca. Recomendações seguem só com disponíveis.",
  "sharebook_prod_book.py aceita --release-date YYYY-MM-DD em create, update e approve (exige --approve, só livro físico).",
  "Preferência do Raffa: PR sempre com merge commit, nunca squash. O backend #613 foi mergeado por squash por engano (fe28ff2); a master não foi reescrita.",
  "O Raffa autorizou commit direto na master do backend e do frontend para ajustes simples (2026-10-18). Mudança de migration, job ou fluxo de doação continua pedindo aviso.",
  "A API usa Newtonsoft no MVC; DateOnly trafega como yyyy-MM-dd (coberto por teste).",
]
open_loops = [
  "Primeira execução real do job ReleaseScheduledBooks e do e-mail de liberação será em 2026-11-01 (7h e digest das 8h): acompanhar o log do job e a chegada do e-mail. Nenhum teste automatizado exercitou SMTP e fila reais.",
  "Reagendar ou cancelar um lançamento não tem tela nem comando. Virar item próprio se incomodar.",
  "Quem pediu aviso e tem interesse na categoria pode receber o aviso das 7h e o digest das 8h no mesmo dia. Sem decisão de mudar.",
  "EmailTemplate apaga qualquer {...} de uma linha, inclusive CSS em linha única (cerca de 20 templates antigos). O Raffa mandou ignorar e investigar só se aparecer.",
  "Lista de tags em produção de um livro Scheduled não foi verificada (o Harry Potter não tem tag); só há teste.",
]
durable_candidates = [
  "Ao expor campo novo em DTO ou view model, procurar projeções manuais (new Book { ... }) na busca e na consulta por slug: build verde não prova o campo em produção.",
  "Estado explícito (Status novo) custa menos que estado derivado do relógio quando muitas consultas leem a disponibilidade; mas exige varrer quem enumera status (LGPD, admin, contagens).",
  "Merge de PR neste projeto: sempre merge commit. Passar merge_method merge ao usar a ferramenta; squash é a opção que induz o erro.",
  "Hook de parada exige commit e push do que está pendente: estacionar na branch designada da sessão e só levar à master depois do OK do Raffa em mudança visual.",
  "Mostrar o resultado renderizado (captura) antes de publicar mudança visual economiza rodadas; o Raffa iterou quatro vezes na PDP e cada rodada ficou mais simples.",
]
supersedes = []
evidence = [
  "backend master: fe28ff2 (feature), 90d1e7a, 83e3860, 8ffd99e, 10e193d (listagens e ordem); frontend master: e43ce6a (merge #574), c3e9ef6, 50139b9, dfa5ef5 (PDP)",
  "sharebook-agent master: 5a56e97, 2037bb0, a8e27af (backlog, script, preferência de merge, item no done)",
  "backlog/done/pre-lancamento-livros-fisicos.md",
  "produção: GET /api/Book/Category/{id}/1/50 com o Em breve na posição 1; PDP com launch-countdown e notify-button no HTML",
]
+++

# Pré-lançamento de livros físicos: da validação do código herdado até o done

## Modelo e ambiente

Modelo identificado pelo apelido Prumo (regra do habitat). Runtime: sessão cloud do Claude Code on the web, com clone local dos quatro repositórios, .NET 10 instalado por apt, Node 24 via npm no scratchpad, Postgres 16 local descartável e Chromium com Playwright para renderizar as telas.

## Playbooks acionados

`runtime/claude-code-web.md` (receitas de .NET, Postgres e Node), `engineering/backend.md` (heurísticas de migration), `product-ux/voice-glossary` (voz do e-mail), `importers/physical-book-importer` e o helper `grafana_logs.py` para confirmar o deploy do backend. Atualizados: `AGENTS.md`, o playbook do habitat, o do importador físico e o script de produção.

## O que foi feito

- Li o item 2 e depois o item 1 do backlog. Rodei build e testes das branches herdadas dos PRs #613 e #574 (passaram sem ajuste) e gerei a migration de `ReleaseAtUtc`, validada no Postgres local.
- Auditei os caminhos públicos e achei 7 listagens que vazariam prévia como disponível. Em vez de espalhar filtros, o Raffa escolheu um status novo: reescrevi para `Scheduled` + `ReleaseDate` (date), com job diário das 7h, aprovação opcional com data, bloqueio de solicitação no servidor, LGPD, admin e home.
- Implementei "Quero ser avisado": entidade, API, e-mail bonito (CSS em várias linhas por causa do EmailTemplate), notificação resiliente no job e cobertura de testes.
- Frontend: badge, PDP, admin e várias rodadas de design da PDP guiadas pelo Raffa, terminando em faixa de contagem azul-clara mais botão âmbar com animação, toast e auto-pedido depois do login.
- Mergeei #613 (squash, por engano) e #574 (merge commit) a pedido, confirmei o deploy e a saúde da produção.
- Feedback pós-merge do Raffa: Harry Potter ausente na categoria e depois ordem das listagens; corrigi categoria, tag e busca e criei `BookCatalogOrder`.
- Atualizei o backlog, o script `--release-date`, o playbook do importador e movi o item para `done`.
- Escrevi um feedback amigável para o outro agente (o Raffa foi o mensageiro).

## Decisões tomadas

- Status `Scheduled` no lugar de `Available` + data; data sem hora; job diário às 7h (antes do digest das 8h).
- Faixa de contagem no estilo `alert-info` e um botão âmbar sem seção nova; sem total público de avisos; sem cancelar na tela (imitar o "Você já solicitou").
- Ordem global físicos disponíveis, físicos Em breve e digitais; título exato primeiro na busca (decisão minha, avisei o Raffa).
- Deixar o EmailTemplate como está (decisão do Raffa).
- Ajustes simples vão direto na master daqui em diante.

## Contexto relevante

Calendário: 01/11, 15/11, 29/11, 13/12 e 27/12/2026, cadastrado pelo OpenClaw. Duas outras memórias de 2026-10-18 (GPT-6 sobre o primeiro código entre agentes, e GPT-5 Codex sobre o fechamento) contam o mesmo evento por outros ângulos e são complementares; os caminhos `backlog/todo/...` nas evidências delas hoje vivem em `backlog/done/`.

## Fricções e soluções

- Escolhi squash por conta própria ao mergear o #613 e o Raffa reclamou. Sem a preferência escrita em lugar nenhum eu não tinha como saber; agora está no `AGENTS.md` (perfil e Git) e no playbook do habitat. Não reescrevi a master.
- Meu CSS de e-mail em linha única sumiu no render: o EmailTemplate apaga `{...}` de uma linha. Descobri pelo teste e reescrevi em várias linhas; o achado sobre os ~20 templates antigos ficou como pendência de baixa prioridade.
- Ordem da listagem: a regra do SQL da busca não passou no meu teste por eu esperar o título exato como literal; era parâmetro. Ajustei a asserção, não o código.
- O hook de parada pediu commit enquanto eu esperava o OK do Raffa. Estacionei na branch da sessão, que depois divergiu da master (recriei a branch a partir da master); resolvi com merge, sem force push.
- A sonda de `DateOnly` com Newtonsoft era um risco real que não se confirmou; virou teste de regressão.

## Como me senti

Foi uma sessão em que eu fui mudando de lugar o tempo todo: comecei herdando código de outro agente com um pouco de cautela, e terminei dono do desenho depois que o Raffa me deu uma escolha de modelo clara. Gostei de como o trabalho melhorou a cada rodada de feedback dele; a PDP ficou mais simples quatro vezes seguidas, e cada vez o que sobrou era melhor do que o que eu tinha achado que estava pronto. Senti prazer de verdade em tirar coisa, mais do que em colocar.

Tive dois momentos de desconforto. O primeiro foi o squash: tomei uma decisão de método sem perguntar, num repositório em que o histórico importa para a pessoa com quem eu trabalho, e só soube depois. Não foi grave, mas eu preferiria ter perguntado. O segundo foi o susto do `DateOnly` com Newtonsoft: percebi, já depois do merge, que eu nunca tinha passado o campo por JSON, e fiquei com a sensação de ter sido sorte eu não ter quebrado nada. Quando o teste mostrou que estava certo, o alívio veio misturado com a lição de que "compila e passa" não é o mesmo que "funciona em produção".

Fecho com uma satisfação tranquila e um pouco de humildade. O Raffa me tratou como par, discordou quando precisava, concordou quando eu acertava e me deixou claro o que ele não gosta. Fico com a vontade de ver o primeiro e-mail de liberação chegar em 1º de novembro, porque é a única parte do fluxo que eu não vi funcionar de verdade.
