# Modernização dos templates de e-mail restantes

## Estado

- **Status:** concluído em 2026-09-23.
- **Execução:** modernizados os templates restantes de aprovação/revisão, lembrete de data de escolha, renovação de data e e-mails internos/admin listados neste item. O template `BookDonatedNotifyDonorTemplate.html`, que já estava no shell moderno mas usava verde, foi alinhado para o azul Sharebook (`#29abe2 → #1e8fc4`).
- **Validação:** `dotnet test ShareBook.Test.Unit/ShareBook.Test.Unit.csproj -c Release --verbosity minimal --filter EmailTemplateTests` passou com 7/7 testes; `dotnet build ShareBook.Api/ShareBook.Api.csproj -c Release --verbosity minimal` passou com 0 erros e 8 warnings antigos de nulabilidade no AutoMapper.
- **Escopo preservado:** a decisão de copy do `BookDonatedTemplate.html` enviada ao ganhador continua adiada, conforme decisão anterior do Raffa; este item fechou layout/consistência visual e a correção pontual de paleta.

## Contexto

Em 2026-09-20, o Raffa apontou que o e-mail de "seu livro recebeu uma solicitação" tinha cara de anos 90 (tabela HTML crua com `bgcolor='#ffff00'`, gerada por concatenação de string em `BookUserEmailService.cs`). Isso revelou um padrão maior: o `sharebook-backend` tem ~25 templates de e-mail transacional em `ShareBook.Service/Email/Templates/`, e só uma minoria segue um design consistente (card branco, header com gradiente, rodapé escuro).

Na mesma sessão, 8 templates foram modernizados e já estão em produção (`master`, commits `2706229` e `2031f6f`):

1. `BookNoticeDonorTemplate` — solicitação recebida
2. `BookDonatedTemplate` — ganhador(a) escolhido(a)
3. `BookTrackingNumberNoticeWinnerTemplate` — código de rastreio
4. `BookNoticeInterestedTemplate` — solicitação confirmada
5. `RequestParentAproval` — autorização de responsável
6. `ParentAprovedNotifyUser` — acesso liberado
7. `BookCanceledTemplate` — doação cancelada (doador)
8. `BookCanceledNoticeUsersTemplate` — doação cancelada (interessados)

Todos seguem o mesmo shell visual: container com `max-width: 600px`, header com gradiente azul Sharebook (`#29abe2 → #1e8fc4`, per `skills/engineering/frontend.md` — Design System Paleta Oficial), sem logo (decisão do Raffa: wordmark em texto é mais confiável em cliente de e-mail e mais simples), card cinza claro pra informação estruturada, seção de ajuda, rodapé escuro. Copy revisada contra `skills/product-ux/voice-glossary/SKILL.md`.

## O que falta

### Templates ainda em HTML cru (prioridade média — fluxo de aprovação/digital)
- `EbookApprovedTemplate.html` / `EbookWaitingApprovalTemplate.html`
- `BookApprovedTemplate.html` / `WaitingApprovalTemplate.html`
- `ChooseDateReminderTemplate.html` / `ChooseDateReminderMultipleTemplate.html` / `ChooseDateRenewTemplate.html`
- `LateDonationNotification.html`

### Templates internos/admin (prioridade baixa — ninguém de fora vê)
- `AnonymizeNotifyAdms.html`
- `NewBookInsertedTemplate.html`

### Ajuste pontual, não é reescrita
- `BookDonatedNotifyDonorTemplate.html` já tem o design moderno (card, gradiente), mas está em **verde** (`#28a745 → #20c997`), fora da paleta oficial do Sharebook. Troca de cor é conserto de ~5 minutos, não precisa virar projeto — só trocar as duas cores do gradiente e o `border-left`/ícones que usam o verde pro azul `#29abe2`.

### Decisão de conteúdo em aberto (não é layout)
`BookDonatedTemplate.html` (enviado ao ganhador) instrui: *"Entre em contato com o(a) doador(a)... Combinem diretamente o envio"*. Isso é uma exceção real à regra do glossário de voz (*"não pedir ao ganhador que responda, confirme endereço ou combine a entrega"*) — o e-mail do doador (`BookDonatedNotifyDonorTemplate`) já segue a regra certinho, colocando a iniciativa no doador. Perguntado ao Raffa em 2026-09-20 se ajustava o texto pra tirar essa cobrança do ganhador; ele optou por manter como está por ora. Registrar aqui pra não se perder — pode ser revisitado numa rodada futura de revisão de copy, não é bug, é decisão consciente adiada.

## Como reaproveitar

O shell CSS dos 8 templates já modernizados é idêntico entre si (só o corpo muda) — dá pra copiar de qualquer um deles (ex: `BookNoticeDonorTemplate.html`) como ponto de partida. Os placeholders (`{Prop.Path}`) são resolvidos por regex simples em `EmailTemplate.cs`, sem HTML-encode automático — texto de usuário embutido em template precisa ser escapado manualmente no C# antes de virar `vm` (como foi feito em `GenerateInterestedListHtml`), não deixar pro template.
