# Pré-lançamento de livros físicos — calendário editorial e avisos

## Prioridade e estado
**Top 1 do backlog.** Proposta aprovada pelo Raffa em 2026-10-17; **planejamento, ainda não implementado**. Primeira temporada planejada para novembro e dezembro de 2026, com cinco lançamentos a cada 14 dias. Títulos e datas escolhidos em 2026-10-17; sujeitos à validação de preço, disponibilidade e execução operacional. Horário de liberação ainda será definido.

## Calendário editorial aprovado — novembro e dezembro de 2026

**Decisão de produto:** publicar **o calendário inteiro desde o começo**, com título, capa, sinopse e countdown de cada livro. Sem títulos secretos, revelação gradual, `RevealAt` ou trabalho manual quinzenal de divulgação. A liberação para solicitações é automática na data/hora configurada. O hype vem da programação pública e da expectativa pela data.

| Liberação | Título | Autor | Papel na temporada | Teto-alvo de aquisição* |
| --- | --- | --- | --- | ---: |
| 01/11/2026 | Harry Potter e a Pedra Filosofal | J. K. Rowling | Grande estreia / nostalgia | R$ 35 |
| 15/11/2026 | A Menina que Roubava Livros | Markus Zusak | Emoção / afinidade com leitura | R$ 30 |
| 29/11/2026 | A Paciente Silenciosa | Alex Michaelides | Suspense / curiosidade | R$ 25 |
| 13/12/2026 | É Assim que Acaba | Colleen Hoover | Romance contemporâneo / público ampliado | R$ 35 |
| 27/12/2026 | O Hobbit | J. R. R. Tolkien | Grande final / fantasia | R$ 40 |

\* **Metas de compra, não cotações verificadas.** Valores incluem frete e devem ser confirmados antes de anunciar. Soma das metas: **R$ 165**; reserva proposta de **R$ 35**; orçamento total de referência **R$ 200**. Horários de liberação pendentes de decisão.

### Estratégia de aquisição e curadoria
- O Sharebook **compra o exemplar somente após a escolha do ganhador**, preferencialmente no sebo online com menor **preço total (livro + frete)** e entrega diretamente no endereço da pessoa. Não exige compra ou estoque antecipado.
- A condição de livro usado é natural ao Sharebook; **não adicionar avisos explicativos redundantes na campanha**. Evitar prometer uma edição específica sem garantia de fornecimento.
- Maximizar **desejo/hype por real gasto**: reconhecimento, vontade de receber, circulação de usados, disponibilidade, custo total e diversidade de públicos.
- Antes de confirmar qualquer título, conferir se **já está na vitrine atual ou participou de campanha recente**, para assegurar novidade. **O Código Da Vinci foi descartado por já estar na vitrine**, substituído por **A Paciente Silenciosa**.
- Conferir disponibilidade em mais de um sebo e preços com frete antes do anúncio; revalidar no momento da compra e prever alternativa em caso de esgotamento. Os valores acima não foram pesquisados/validados.
- Esta heurística de curadoria é candidata a uma **local skill** futura, após aprendizado com a primeira temporada.
- A execução pressupõe que a operação de doação patrocinada pelo Sharebook e envio direto ao ganhador seja compatível com o fluxo de doador/seleção existente; validar no discovery técnico antes de lançar.

## Objetivo e hipótese
Transformar a vitrine existente de livros físicos em uma experiência de antecipação e retorno: anunciar doações futuras, permitir que leitores optem por receber um aviso e abrir solicitações somente no momento anunciado. Hipótese: calendário quinzenal aumenta revisitas, interesse e participação em doações. Validar com métricas reais.

## Jornada do leitor (decisões de produto)
1. Livro físico é anunciado com data e hora futuras de liberação, capa, sinopse e PDP pública.
2. O livro aparece **na seção atual "Livros físicos" da home**, sem criar outra seção: **da esquerda para a direita, primeiro livros disponíveis na ordem atual; depois livros em prévia por data de liberação crescente**.
3. Card em prévia mostra estado inequívoco e countdown compacto; PDP é customizada, com countdown em destaque e CTA **"Quero ser avisado"**.
4. Leitor autenticado opta pelo aviso e pode desfazer o interesse. O interesse **não é solicitação, reserva, inscrição na seleção, preferência ou prioridade**.
5. No horário anunciado, o livro se torna solicitável no fluxo comum. Interessados recebem aviso por e-mail com link para PDP; o usuário **precisa solicitar separadamente** caso queira participar.
6. A seleção do ganhador, limites de solicitações, frete e demais regras da doação seguem o fluxo atual, sem vantagem para quem pediu aviso.

## Regras funcionais
- Exclusivo para livros **físicos**. E-books fora do escopo.
- Livros disponíveis sempre precedem livros em prévia na home; prévias ordenadas da mais próxima para a mais distante.
- Livro em prévia nunca pode ser solicitado, mesmo via API direta. Validar no servidor, não só ocultar botão.
- Um usuário pode ter no máximo um interesse ativo por livro; inscrição e cancelamento idempotentes.
- O countdown é informativo; a fonte de verdade para liberação é o relógio do servidor, com data/hora e fuso explicitados.
- No momento da liberação, o livro migra automaticamente para o grupo de disponíveis; evitar depender do envio de e-mail para habilitar solicitações.
- Se o horário mudar ou o livro for cancelado, UI e notificações devem refletir a alteração, sem promessas falsas.
- A janela para solicitar e a data de escolha do ganhador começam a contar a partir da liberação, não do anúncio (proposta a validar no detalhamento).
- A inscrição de aviso deve respeitar preferências de comunicação e permitir cancelamento; sem disparos duplicados.

## Desenho técnico inicial (hipóteses, não implementação prescrita)
**Referência: branches `master` do backend e frontend, inspecionadas em 2026-10-17.**

- Backend: `Book` já contém `Status`, `ApprovedAt`, `ChooseDate` e `MaxRequestsOverride`. `BookService.ApproveAsync` atualmente torna o livro `Available` imediatamente. **Não reutilizar `ChooseDate`**: é a data da escolha do ganhador, não de abertura das solicitações. Avaliar `ReleaseAt` (UTC) e estado de publicação separado do estado da doação; confirmar todos os filtros e transições antes de decidir por novo `BookStatus`.
- Persistência de avisos: avaliar entidade dedicada `BookReleaseInterest` (BookId, UserId, CreatedAt, NotifiedAt), índice único por par e endpoint autenticado para aderir/cancelar/consultar.
- Backend: garantir a restrição de `ReleaseAt` no serviço de solicitação (`BookUserService`) e nas consultas públicas; respeitar limites de solicitações e encerramento antecipado presentes na `master`.
- Home Angular: `HomeComponent` usa `getFeaturedPrintedBooks()`, `app-book-shelf` e `book-card`; ampliar DTO/consulta e apresentação sem criar seção paralela. Não prejudicar descoberta de livros já disponíveis.
- PDP Angular: `DetailsComponent` atualmente usa `available` e mostra indisponíveis como já doados. Criar terceiro estado visual explícito de prévia, sem cair na mensagem de "já foi doado"; SSR/SEO e acessibilidade devem ser testados.
- E-mail: reaproveitar infraestrutura transacional existente, com envio assíncrono, idempotência, retry e observabilidade; atraso/falha do e-mail não bloqueia a liberação.
- Admin: definir como cadastrar/agendar, editar, cancelar e liberar antecipadamente um lançamento; evitar operação manual frágil.
- Migrations EF Core, testes de domínio/API, testes Angular, regressão de fluxo normal e checagem de fuso/virada de horário são obrigatórios.

## Entrega em etapas
1. **Discovery técnico**: mapear queries de disponibilidade, `BookUserService`, enums, jobs, admin e templates de e-mail na `master`; confirmar modelagem e política de lançamento.
2. **Backend**: migração, agendamento, API de vitrine, inscrições/cancelamentos, bloqueio de solicitações antecipadas e testes.
3. **Frontend**: ordenação da home, card com countdown, PDP customizada e estado da inscrição; acessibilidade e SSR.
4. **Operação**: liberação pontual, avisos resilientes, logs e tratamento de reagendamento/cancelamento.
5. **Piloto editorial**: campanha quinzenal com poucos títulos, validar dados e ajustar antes de escalar.

## Métricas e critérios de aceite
- Visualizações de PDP em prévia; interessados únicos; conversão de visualização → aviso.
- Taxa de entrega/clique dos avisos; retorno à PDP; conversão de aviso → solicitação efetiva.
- Solicitações por livro, tempo até primeira solicitação e doações concluídas; comparar com lançamentos sem prévia quando viável.
- Critérios mínimos: ordenação correta; countdown consistente; inscrição sem reserva; API bloqueia pedidos antecipados; livro libera no horário; aviso único por interessado; fluxo atual de doações preservado; testes verdes.

## Fora do MVP
Reservas, fila prioritária, sorteio privilegiado, pagamentos, push/WhatsApp, campanhas automatizadas complexas e redesign completo da home.

## Dependências e limites
**Não confundir com [Lista de Desejos](lista-de-desejos.md)**: nela o leitor pede um livro que deseja; aqui o Sharebook anuncia um exemplar futuro e o leitor pede somente um aviso. Lista de Desejos está em execução pelo **Josué**; não modificar ou assumir esse trabalho sem autorização explícita.

## Handoff para OpenClaw — implementação em andamento (2026-10-17)

**PRs de trabalho (DRAFT, NÃO MERGEAR):**
- Backend: https://github.com/SharebookBR/sharebook-backend/pull/613 — branch `feature/physical-book-prelaunch`.
- Frontend: https://github.com/SharebookBR/sharebook-frontend/pull/574 — branch `feature/physical-book-prelaunch`.
- Ambas as branches partem de `master`. **Não usar `develop`**, que está desatualizada.

### Implementado parcialmente
- Backend: `Book.ReleaseAtUtc`, `BookReleasePolicy` e testes de domínio; bloqueio de pedidos antecipados em `BookUserService.InsertAsync`; agendamento opcional em aprovação; modelos API e DTO de vitrine; home inclui prévias após os livros disponíveis, ordenadas pela data de lançamento.
- Frontend: campos `releaseAtUtc` nos modelos, card físico com indicação "Em breve" e data.
- **Não houve build, teste ou execução de migration** neste ambiente; commits não foram validados.

### Trabalho pendente obrigatório
1. **Primeiro compilar e corrigir** backend/frontend das branches. Revisar cuidadosamente assinaturas, enum `BookType`, DI de `TimeProvider`, mapeamento AutoMapper, regras de autorização e comportamento de aprovação.
2. Gerar migration EF Core de `ReleaseAtUtc` (nullable, PostgreSQL `timestamp with time zone`) via `dotnet ef migrations add`, com snapshot e designer consistentes. **Não criar migration apenas em texto sem atualizar snapshot**. Validar SQL e aplicação em banco descartável; não executar em produção sem autorização.
3. Completar modelo de interesses em avisos (usuário/livro único, opt-in/cancelamento, autenticação, proteção contra duplicatas, endpoints, testes, política de privacidade), e e-mails assíncronos idempotentes, sem bloquear abertura. A fila de novo livro existente foi suprimida no agendamento, então **é obrigatório garantir envio no momento da liberação**.
4. Revisar todos os caminhos de solicitação e consultas públicas (inclusive busca, categorias, recomendações, sitemap e caches). O relógio do **servidor** é fonte de verdade; evitar vazamento de prévias como disponíveis.
5. Implementar PDP Angular com estado "Em breve", countdown acessível, CTA **"Quero ser avisado"**, cancelamento do interesse, atualização de estado na virada do horário, SSR/SEO e botão "Solicitar livro" apenas após liberação.
6. Conferir se os 15 livros disponíveis continuam na mesma ordem e se todos os lançamentos futuros aparecem **depois**, no mesmo shelf. Verificar mudanças de horário e status de cancelamento.
7. Validar `ChooseDate` relativa à liberação, transições por máximo de solicitações e fluxo de compra/envio direto ao ganhador. Evitar e-mails de aprovação prematuros que anunciem disponibilidade.
8. Testar integração, concorrência, timezone (Brasil x UTC), retries, idempotência, responsividade e acessibilidade. Registrar resultados e falhas reais.
9. **Não tocar na Lista de Desejos** desenvolvida pelo Josué; não inventar títulos, preços ou datas de horários além do calendário aprovado.

### Comandos de validação sugeridos
```bash
# backend, a partir da raiz do repositório
dotnet restore ./ShareBook/ShareBook.sln
dotnet build ./ShareBook/ShareBook.Api/ShareBook.Api.csproj --no-restore
dotnet test ./ShareBook/ShareBook.Test.Unit/ShareBook.Test.Unit.csproj --no-restore
# conferir comando ef adequado ao DbContext e projeto startup antes de executar:
dotnet ef migrations list --project ./ShareBook/ShareBook.Repository --startup-project ./ShareBook/ShareBook.Api

# frontend, a partir da raiz do repositório
unset NODE_ENV
npm ci --legacy-peer-deps --include=dev
npm test -- --watch=false
npm run build-dev
```

### Critério para publicação
Só promover os PRs à `master` **após** completar os fluxos, validar migration em banco de teste, build e testes verdes, revisar impacto no deploy e obter aprovação explícita do Raffa. Não publicar automaticamente em produção.

## Estimativa inicial
4,5–9 dias de desenvolvimento **muito preliminares**, sujeitos ao discovery completo e testes. Prioridade Top 1 definida pelo Raffa; estimativa não é compromisso de entrega.
