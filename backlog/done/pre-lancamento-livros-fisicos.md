# Pré-lançamento de livros físicos — calendário editorial e avisos

## Estado: concluído em 2026-10-18
Prioridade Top 1 definida pelo Raffa em 2026-10-17; **implementado, validado pelo Raffa e em produção em 2026-10-18** (backend `fe28ff2` + ajustes na `master`, frontend `e43ce6a` + ajustes na `master`). O OpenClaw cadastra o calendário com `--release-date`. Este arquivo fica como memória do desenho, das decisões e dos limites conhecidos.

## Calendário editorial aprovado — novembro e dezembro de 2026

**Decisão de produto:** publicar **o calendário inteiro desde o começo**, com título, capa, sinopse e countdown de cada livro. Sem títulos secretos, revelação gradual, `RevealAt` ou trabalho manual quinzenal de divulgação. A liberação para solicitações é automática na data/hora configurada. O hype vem da programação pública e da expectativa pela data.

| Liberação | Título | Autor | Papel na temporada | Teto-alvo de aquisição* |
| --- | --- | --- | --- | ---: |
| 01/11/2026 | Harry Potter e a Pedra Filosofal | J. K. Rowling | Grande estreia / nostalgia | R$ 35 |
| 15/11/2026 | A Menina que Roubava Livros | Markus Zusak | Emoção / afinidade com leitura | R$ 30 |
| 29/11/2026 | A Paciente Silenciosa | Alex Michaelides | Suspense / curiosidade | R$ 25 |
| 13/12/2026 | É Assim que Acaba | Colleen Hoover | Romance contemporâneo / público ampliado | R$ 35 |
| 27/12/2026 | O Hobbit | J. R. R. Tolkien | Grande final / fantasia | R$ 40 |

\* **Metas de compra, não cotações verificadas.** Valores incluem frete e devem ser confirmados antes de anunciar. Soma das metas: **R$ 165**; reserva proposta de **R$ 35**; orçamento total de referência **R$ 200**. A liberação é por data (job das 7h, São Paulo), sem hora.

### Estratégia de aquisição e curadoria
- O Sharebook **compra o exemplar somente após a escolha do ganhador**, preferencialmente no sebo online com menor **preço total (livro + frete)** e entrega diretamente no endereço da pessoa. Não exige compra ou estoque antecipado.
- A condição de livro usado é natural ao Sharebook; **não adicionar avisos explicativos redundantes na campanha**. Evitar prometer uma edição específica sem garantia de fornecimento.
- Maximizar **desejo/hype por real gasto**: reconhecimento, vontade de receber, circulação de usados, disponibilidade, custo total e diversidade de públicos.
- Antes de confirmar qualquer título, conferir se **já está na vitrine atual ou participou de campanha recente**, para assegurar novidade. **O Código Da Vinci foi descartado por já estar na vitrine**, substituído por **A Paciente Silenciosa**.
- **Não pesquisar sebo ou preço no cadastro/pré-lançamento.** Raffa fará essa pesquisa muito mais adiante, quando houver pessoa ganhadora e for a hora real da compra. Nesse momento, conferir disponibilidade, preço total com frete e alternativa em caso de esgotamento. Os tetos acima continuam apenas como metas de referência.
- Esta heurística de curadoria é candidata a uma **local skill** futura, após aprendizado com a primeira temporada.
- A execução pressupõe que a operação de doação patrocinada pelo Sharebook e envio direto ao ganhador seja compatível com o fluxo de doador/seleção existente. **Ainda não validado de ponta a ponta**: conferir na primeira escolha de ganhador de um livro do calendário.

## Objetivo e hipótese
Transformar a vitrine de livros físicos em uma experiência de antecipação e retorno: anunciar doações futuras, deixar o público pedir um aviso e abrir as solicitações só na data anunciada. Hipótese: calendário quinzenal aumenta revisitas, interesse e participação. Validar com métricas reais.

**Quem usa o quê:** o calendário (aprovar com data de liberação) é gerido só pelo Raffa e pelos agentes. O público usa o "Quero ser avisado". O fluxo de doação das pessoas comuns não muda.

## Desenho final (o que está em produção)

### Modelo
- **`BookStatus.Scheduled`** ("Em breve"), último valor do enum (coluna `integer`, sem migration de status). Livro físico aprovado com data futura nasce nele. `Status == Available` continua significando "disponível": nenhuma listagem, busca, categoria, tag, recomendação, contagem ou sitemap precisou mudar.
- **`Book.ReleaseDate`**: `date`, sem hora, fuso de São Paulo. Só preenchida enquanto o livro está `Scheduled`; vira `null` ao liberar. Serializa como `"yyyy-MM-dd"` (a API usa Newtonsoft; coberto por teste).
- **`BookReleaseInterest`** (livro + pessoa, único por par, `NotifiedAt`): é o "Quero ser avisado". Não é solicitação, reserva, inscrição na seleção nem prioridade.

### Aprovação (`POST /api/Book/Approve/{id}`)
- Corpo opcional `{"ReleaseDate": "yyyy-MM-dd"}`. Data **futura** (São Paulo) em livro físico: `Scheduled`, sem `ChooseDate`, sem e-mail à pessoa doadora e sem aviso de novo livro. **Sem data, hoje ou passada: fluxo de sempre.** Livro digital com data é recusado.

### Liberação (job `ReleaseScheduledBooks`, 7h de São Paulo)
- Promove `Scheduled` com `ReleaseDate <= hoje` para `Available`; define `ChooseDate = hoje + SharebookSettings:DaysInShowcase` (padrão 7) e `ApprovedAt = agora` (marca a publicação: o digest das 8h usa esse campo); manda o e-mail à pessoa doadora e o aviso de novo livro.
- Roda **antes** do digest de novos livros (`NewBookGetInterestedUsers`, 8h).
- Depois de liberar, envia o aviso aos interessados (`BookReleasedNotifyTemplate`, fila de baixa prioridade). Só pega avisos pendentes de livros já `Available`: falha de SMTP é retomada na execução seguinte e ninguém recebe duas vezes. O job roda essa etapa mesmo sem liberação no dia.
- A precisão é de dia, não de hora: o livro abre quando o job roda (7h). Decisão do Raffa: "não há pressa pra quem esperou até 60 dias".

### Solicitação
- `BookUserService.InsertAsync` recusa livro `Scheduled` no servidor ("ainda não foi liberado"), inclusive via API direta.

### "Quero ser avisado" (`/api/BookReleaseInterest`)
- `GET /{id}/Count` (aberto) e `GET|POST|DELETE /{id}` (exigem login). A tela hoje usa só o `GET` e o `POST` (o total público e o cancelar saíram da PDP, mas os endpoints ficam). Inscrever e cancelar são idempotentes; só vale para livro `Scheduled` e para quem não desativou e-mails (mensagem clara se desativou).
- O visitante clica no mesmo botão e vai ao login; o aviso não reserva nem dá prioridade (dito no toast e no e-mail). O admin vê "Avisos pedidos" por livro: é o feedback de demanda do Raffa.
- LGPD: anonimizar a conta cancela livros `Scheduled` da pessoa e remove seus pedidos de aviso.

### Frontend (versão final, depois de várias rodadas de feedback do Raffa)
- **Home:** livros `Scheduled` vêm depois dos disponíveis, no mesmo shelf, por data crescente. Badge "Em breve · N dias" (amanhã, hoje) acima do "Livro físico" no card e ao lado dele na PDP.
- **PDP "Em breve":** (1) uma **faixa compacta** no azul-claro do aviso do livro digital (`alert-info`), com o número de dias em destaque, "DIAS" e "Será lançado em 1º de novembro"; (2) **um botão âmbar com sino, "Quero ser avisado"**, junto de "Comprar na Amazon" e "Compartilhar". Sem seção extra, sem texto corrido, sem total público de avisos.
- **O botão é o mesmo para todos.** Visitante vai ao login e, ao voltar (`?avisar=1`), o pedido é concluído sozinho. Logado: o sino balança durante o envio, toast "Combinado! Avisaremos por e-mail em 1º de novembro. Nesse dia, lembre-se de solicitar o livro." e o botão vira o selo verde "Aviso ativado! Você será avisado em 1º de novembro." (mesmo padrão do "Você já solicitou"). **Não há cancelar na tela**: as saídas são o link de descadastro do e-mail e a configuração de e-mails da conta. O endpoint `DELETE /api/BookReleaseInterest/{id}` existe e não é usado pela tela.
- **Listagens:** categoria, tag e busca pública também mostram os livros `Scheduled` (com o badge). Ordem das três: **físicos disponíveis → físicos "Em breve" (liberação mais próxima primeiro) → digitais**; dentro de cada grupo vale o critério de cada tela (data de cadastro; relevância na busca, com título exato sempre em primeiro). A regra vive em `BookCatalogOrder` (backend); a busca tem a mesma expressão escrita à mão em `BookRepository.FullTextSearch`, manter igual. Contagens de categoria e tag incluem os agendados. Recomendações seguem só com disponíveis (decisão do Raffa).
- **Admin:** filtro "Em breve (N)", data de liberação e "Avisos pedidos" por livro, e campo opcional "Data de liberação" ao aprovar (sem data = fluxo de sempre).
- **Utilitário `release-date`:** dia de hoje em São Paulo, dias restantes, data por extenso e badge; não passa por `Date`, para não deslocar o dia por fuso.

## Decisões e motivos (para não se perder)
- **Status novo em vez de `Available + data`.** Primeiro desenho foi `ReleaseAtUtc` com o estado derivado do relógio; a auditoria achou 7 caminhos públicos que vazavam prévia como disponível, e o risco era regressão em toda query nova. O Raffa escolheu clareza de modelo ("`Status == Available` volta a significar disponível"). Custo aceito: precisa de job para promover e os pontos que enumeram status precisam conhecer o valor novo (já tratados: LGPD, admin, home).
- **Data sem hora + job diário.** O Raffa não precisa de precisão de hora. Simplificou o modelo e o countdown (em dias).
- **Total de interessados só no admin.** Chegou a ser mostrado na PDP como prova social; o Raffa desanimou (gasta espaço, pouco valor) e saiu. Sem lembrete na véspera nesta temporada: "começar simples, um aviso no dia".
- **Deslogado precisa entrar** (nada de só e-mail): evita lista de e-mails sem consentimento e abuso. Primeiro com instrução na tela; no fim, o mesmo botão para todos que leva ao login e conclui o pedido na volta.
- **Aprovação não mudou.** Quem não manda data não vê nada diferente.
- **Aviso simples na PDP.** A primeira PDP teve dois blocos e depois um cartão azul-escuro; o Raffa achou poluído e depois gritante. Ficou: faixa de contagem discreta + um botão. Aprendizado: o hype está na data e no botão, não em texto; a ressalva "não reserva nem dá prioridade" mora no toast do momento do pedido e no e-mail.
- **Prévia vem antes do digital nas listagens** (a prévia é a vitrine da campanha e o físico é o diferencial), mas depois dos físicos disponíveis (esses têm ação imediata e prazo). A regra de tipo-primeiro vale em toda categoria, não só nas que têm prévia.
- **Merge:** preferência do Raffa é **merge commit, nunca squash** ("o git precisa contar uma história pelos seus commits"). O backend (#613) foi mergeado por squash por engano da sessão (`fe28ff2`, um commit só); o frontend (#574) foi com merge commit. A `master` não foi reescrita. Regra registrada no `AGENTS.md`.

## Fora do MVP / limites conhecidos
- **Reagendar ou cancelar um lançamento não tem tela.** Hoje só se agenda na aprovação. Para corrigir uma data errada: cancelar a doação pelo fluxo atual e cadastrar de novo, ou ajustar no banco com o Raffa. Candidato natural a próximo item.
- Quem pediu aviso **e** tem interesse na categoria pode receber dois e-mails no mesmo dia (aviso das 7h e digest das 8h). Sem decisão de mudar.
- Sem lembrete na véspera, reservas, fila prioritária, push/WhatsApp.
- **Achado fora de escopo (2026-10-18):** o `EmailTemplate` apaga qualquer `{...}` de uma linha só, inclusive CSS em linha única; cerca de 20 templates antigos têm esse formato e, pelo código, devem sair sem estilo. O Raffa disse que nunca teve problema e mandou ignorar; **investigar só se aparecer**. O template novo usa CSS em várias linhas (há teste que protege isso).

## Como cadastrar um lançamento (referência)
Seguir `playbooks/importers/physical-book-importer/PLAYBOOK.md` e acrescentar **`--release-date YYYY-MM-DD`** (data do dia da abertura, fuso de São Paulo) ao `create ... --approve` ou ao `approve --id ...`. A flag só vale com `--approve` e em livro físico. Conferir `status: Scheduled` e `releaseDate` no retorno e abrir a PDP. Cadastrar a temporada inteira de uma vez (decisão de produto: sem títulos secretos). Não existe tela nem comando para reagendar.

| Liberação (`--release-date`) | Título |
| --- | --- |
| 2026-11-01 | Harry Potter e a Pedra Filosofal |
| 2026-11-15 | A Menina que Roubava Livros |
| 2026-11-29 | A Paciente Silenciosa |
| 2026-12-13 | É Assim que Acaba |
| 2026-12-27 | O Hobbit |

## Lições técnicas (valem para próximas features)
- **Projeções manuais esquecem campo novo.** `FullSearch` e a consulta da PDP por slug montam `new Book { ... }` campo a campo; `ReleaseDate` ficou de fora e só apareceu em produção. Ao expor campo em DTO, procurar `new Book {`.
- **A API usa Newtonsoft** (`.AddNewtonsoftJson()`): `DateOnly` trafega como `"yyyy-MM-dd"` e há teste que protege isso.
- **O `EmailTemplate` apaga qualquer `{...}` de uma linha só**, inclusive CSS em linha única. Cerca de 20 templates antigos têm CSS assim e, pelo código, devem sair sem estilo; o Raffa disse que nunca teve problema e **mandou investigar só se aparecer**. O template novo (`BookReleasedNotifyTemplate`) usa CSS em várias linhas e há teste que protege isso.
- **Status novo exige varrer quem enumera status** (LGPD, admin, home, contagens); por isso o `Scheduled` foi tratado nesses pontos.
- **Merge com histórico preservado**: PRs sempre com merge commit (regra no `AGENTS.md` e no playbook do habitat). O #613 foi mergeado por squash por engano.

## Métricas e critérios de aceite
- Visualizações de PDP em prévia; interessados únicos (total de avisos pedidos por livro); conversão de visualização para aviso.
- Entrega do aviso (e-mails enviados no job) e retorno à PDP; conversão de aviso para solicitação efetiva.
- Solicitações por livro, tempo até a primeira solicitação e doações concluídas; comparar com lançamentos sem prévia quando viável.
- Aceite técnico (todos cumpridos antes do merge): ordenação correta na home; pedido de `Scheduled` recusado no servidor; livro libera na data; aviso único por interessado; fluxo atual de doações preservado; build e testes verdes (no fim: backend 250 testes, frontend 131). **Não verificado de ponta a ponta com e-mail real** na data do fechamento do item; o Raffa validou o fluxo em produção.

## Dependências e limites
**Não confundir com [Lista de Desejos](../todo/lista-de-desejos.md)**: nela o leitor pede um livro que deseja; aqui o Sharebook anuncia um exemplar futuro e o leitor pede somente um aviso. A Lista de Desejos está em execução pelo **Josué**; não modificar nem assumir esse trabalho sem autorização explícita.
