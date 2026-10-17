# Pré-lançamento de livros físicos — calendário editorial e avisos

## Prioridade e estado
**Top 1 do backlog.** Proposta aprovada pelo Raffa em 2026-10-17; **planejamento, ainda não implementado**. Primeira campanha pretendida: último trimestre de 2026, com novos livros aproximadamente a cada 15 dias. Datas e títulos específicos ainda serão definidos.

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

## Estimativa inicial
4,5–9 dias de desenvolvimento **muito preliminares**, sujeitos ao discovery completo e testes. Prioridade Top 1 definida pelo Raffa; estimativa não é compromisso de entrega.
