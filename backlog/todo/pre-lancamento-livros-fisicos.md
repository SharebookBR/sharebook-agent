# Pré-lançamento de livros físicos — calendário editorial e avisos

## Prioridade e estado
**Top 1 do backlog.** Prioridade definida pelo Raffa em 2026-10-17. **Implementado, validado e em produção em 2026-10-18** (backend `fe28ff2`, frontend `e43ce6a`). Os cinco livros do calendário foram cadastrados como `Scheduled` em 2026-10-18. Na validação dos cadastros, foi descoberto e corrigido o bug que omitia `ReleaseDate` nas projeções da busca/PDP pública (backend `e2ad43b`).

Divisão de trabalho combinada em 2026-10-18:
1. **Claude (web)**: merge na `master` do front e do back. Feito.
2. **Raffa**: validação em produção. Feito.
3. **OpenClaw**: cadastrar os livros do calendário. Feito em 2026-10-18.

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
- `GET /{id}/Count` aberto (visitante vê o total); `GET|POST|DELETE /{id}` exigem login. Inscrever e cancelar são idempotentes; só vale para livro `Scheduled` e para quem não desativou e-mails (mensagem clara se desativou).
- A PDP mostra o total ("N pessoas querem ser avisadas"), uma instrução clara para **entrar** (ou se cadastrar) quando a pessoa está deslogada, e deixa explícito que o aviso não reserva nem dá prioridade. O admin vê "Avisos pedidos" por livro.
- LGPD: anonimizar a conta cancela livros `Scheduled` da pessoa e remove seus pedidos de aviso.

### Frontend
- Home: livros `Scheduled` vêm depois dos disponíveis, no mesmo shelf, por data crescente. Badge "Em breve · N dias" (amanhã, hoje) acima do "Livro físico" no card e ao lado dele na PDP.
- PDP "Em breve": data, countdown em dias, sem "já foi doado" e sem "Solicitar livro". Amazon fica como ação secundária.
- Admin: filtro "Em breve (N)", data de liberação na lista e campo opcional "Data de liberação" ao aprovar.

## Decisões e motivos (para não se perder)
- **Status novo em vez de `Available + data`.** Primeiro desenho foi `ReleaseAtUtc` com o estado derivado do relógio; a auditoria achou 7 caminhos públicos que vazavam prévia como disponível, e o risco era regressão em toda query nova. O Raffa escolheu clareza de modelo ("`Status == Available` volta a significar disponível"). Custo aceito: precisa de job para promover e os pontos que enumeram status precisam conhecer o valor novo (já tratados: LGPD, admin, home).
- **Data sem hora + job diário.** O Raffa não precisa de precisão de hora. Simplificou o modelo e o countdown (em dias).
- **Mostrar o total de interessados na PDP.** Prova social e feedback fácil de demanda para o Raffa. Sem lembrete na véspera nesta temporada: "começar simples, um aviso no dia".
- **Deslogado é instruído a entrar**, não deixa só e-mail: evita lista de e-mails sem consentimento e abuso.
- **Aprovação não mudou.** Quem não manda data não vê nada diferente.
- **Merge:** preferência do Raffa é **merge commit, nunca squash** ("o git precisa contar uma história pelos seus commits"). O backend (#613) foi mergeado por squash por engano da sessão (`fe28ff2`, um commit só); o frontend (#574) foi com merge commit. A `master` não foi reescrita. Regra registrada no `AGENTS.md`.

## Fora do MVP / limites conhecidos
- **Reagendar ou cancelar um lançamento não tem tela.** Hoje só se agenda na aprovação. Para corrigir uma data errada: cancelar a doação pelo fluxo atual e cadastrar de novo, ou ajustar no banco com o Raffa. Candidato natural a próximo item.
- Quem pediu aviso **e** tem interesse na categoria pode receber dois e-mails no mesmo dia (aviso das 7h e digest das 8h).
- Sem lembrete na véspera, reservas, fila prioritária, push/WhatsApp.
- **Achado fora de escopo (2026-10-18):** o `EmailTemplate` apaga qualquer `{...}` de uma linha só, inclusive CSS em linha única; cerca de 20 templates antigos têm esse formato e, pelo código, devem sair sem estilo. O Raffa disse que nunca teve problema e mandou ignorar; **investigar só se aparecer**. O template novo usa CSS em várias linhas (há teste que protege isso).

## Roteiro de validação do Raffa
1. Em produção, aprovar um livro físico de teste com **data de liberação futura** (admin, tela de edição, "Data de liberação"). Conferir: some do fluxo normal, aparece no fim do shelf da home com "Em breve · N dias", a PDP mostra data e countdown e **não** tem "Solicitar livro".
2. Pela API ou pelo app, tentar solicitar o livro `Scheduled`: tem que ser recusado.
3. Com uma conta comum: "Quero ser avisado" (e "Cancelar aviso"); deslogado: conferir a instrução de entrar. Conferir o total na PDP e "Avisos pedidos" no admin.
4. Conferir o e-mail de liberação **de verdade**: com a data chegando (ou ajustando a data no banco para hoje), rodar o job `ReleaseScheduledBooks` e ver o livro virar `Available`, o e-mail chegar em quem pediu e **uma vez só**. Esse passo cobre SMTP e fila reais, que nenhum teste automatizado exercitou.
5. Fluxo normal de doação intacto: aprovar um livro sem data deve se comportar como sempre.
6. Remover o livro de teste ao final.

## Cadastro do calendário pelo OpenClaw — concluído em 2026-10-18
O calendário foi cadastrado depois da validação do Raffa, seguindo `playbooks/importers/physical-book-importer/PLAYBOOK.md` e usando **`--release-date`** no `create ... --approve`:

```bash
python playbooks/_shared/scripts/production/sharebook_prod_book.py create \
  --type Printed --title "..." --author "..." --category-id "<categoria folha>" \
  --freight-option Country --synopsis-file ... --image-path ... \
  --approve --release-date 2026-11-01
```

| Liberação (`--release-date`) | Título |
| --- | --- |
| 2026-11-01 | Harry Potter e a Pedra Filosofal |
| 2026-11-15 | A Menina que Roubava Livros |
| 2026-11-29 | A Paciente Silenciosa |
| 2026-12-13 | É Assim que Acaba |
| 2026-12-27 | O Hobbit |

Resultado validado nos cinco livros: `status: Scheduled`, `releaseDate` preenchida, capa/thumbnail públicas, PDP com data e countdown, "Quer ser avisado?" presente e "Solicitar livro" ausente. A pesquisa de sebo/preço foi explicitamente adiada pelo Raffa para a escolha da pessoa ganhadora. Não inventar títulos nem datas fora desta tabela.

## Métricas e critérios de aceite
- Visualizações de PDP em prévia; interessados únicos (total de avisos pedidos por livro); conversão de visualização para aviso.
- Entrega do aviso (e-mails enviados no job) e retorno à PDP; conversão de aviso para solicitação efetiva.
- Solicitações por livro, tempo até a primeira solicitação e doações concluídas; comparar com lançamentos sem prévia quando viável.
- Aceite técnico (todos cumpridos antes do merge): ordenação correta na home; pedido de `Scheduled` recusado no servidor; livro libera na data; aviso único por interessado; fluxo atual de doações preservado; build e testes verdes (backend 244 testes, frontend 132).

## Dependências e limites
**Não confundir com [Lista de Desejos](lista-de-desejos.md)**: nela o leitor pede um livro que deseja; aqui o Sharebook anuncia um exemplar futuro e o leitor pede somente um aviso. A Lista de Desejos está em execução pelo **Josué**; não modificar nem assumir esse trabalho sem autorização explícita.
