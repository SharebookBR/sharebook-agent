# Revisão de copy dos e-mails da leva 2

## Estado

**Concluído em 2026-09-26.** Os três primeiros foram aprovados um a um pelo Raffa; a partir do quarto ele delegou a revisão inteira ("pode avançar por conta própria até fechar todos"). Backend `master` validado com build + 159/159 testes unitários a cada push.

## Por que existe

A [modernização de 2026-09-23](../done/modernizacao-templates-email-restantes.md) (commit `afb176a` no backend) trocou só o visual: a copy antiga foi transplantada literalmente para o shell novo. O título "Modernização" e o status "concluído" levaram o Raffa (com razão) a esperar e-mails prontos, e em 2026-09-26 ele recebeu dois ainda frios, com o nome completo em caixa alta.

O problema do nome já foi resolvido de forma transversal no mesmo dia: `ToFirstName()` → `User.FirstName`/`ContactUs.FirstName`, aplicado em todas as saudações (backend `7d37062`).

## Critérios da revisão

- Ler `skills/product-ux/voice-glossary/SKILL.md` antes de escrever.
- Nada de "sua obra" para quem doa (doador raramente é autor).
- Cortar card "Detalhes do livro" quando título e autor já estão na frase.
- Evitar "não é preciso fazer (mais) nada": fecha a conversa em vez de gerar expectativa.
- Mecânica real do fluxo acima de frase bonita (sem prometer revisão/logística que não existe).
- Rodapé canônico "fale com a gente" é obrigatório (teste de contrato `VerifyCanonicalEmailFooters`).
- Build + `dotnet test` antes do push; atualizar `EmailTemplateTests` junto.

## Checklist

- [x] `EbookWaitingApprovalTemplate` — backend `7d37062`
- [x] `EbookApprovedTemplate` (+ assunto próprio "Seu livro digital está no ar!", CTA para a PDP) — backend `f590980`
- [x] `BookApprovedTemplate` (+ assunto "Seu livro está na vitrine!", CTA para a PDP) — backend `5481ced`
- [x] `WaitingApprovalTemplate` — livro físico em revisão (ganhou teste próprio) — backend `0cdfb3d`
- [x] `ChooseDateReminderTemplate` / `ChooseDateReminderMultipleTemplate` — mostra "N solicitações"; troca "entre em contato e confirme os dados" pelo que acontece de fato (dados do ganhador chegam por e-mail) — backend `7904ff0`
- [x] `ChooseDateRenewTemplate` — assunto "Seu livro ganhou mais 10 dias na vitrine" e a nova data de escolha, que não aparecia — backend `fed6149`
- [x] Doação atrasada — `LateDonationNotification.html` é relatório **só para admins** (fora do escopo); os e-mails para quem doa eram HTML cru montado dentro do job e viraram `LateDonationDonorSoft/HardTemplate` — backend `ce06c7b`
- Fora do escopo (admin/interno): `AnonymizeNotifyAdms`, `NewBookInsertedTemplate`.

## Achados

- **Ameaça falsa no "último aviso" de doação atrasada.** O texto dizia que a conta seria bloqueada, mas nenhum código bloqueia conta. O que existe é o job `CancelAbandonedDonations`: a doação é cancelada automaticamente (config `MaxLateDonationDaysAutoCancel`, hoje 10 dias de atraso) e quem fez solicitação é avisado. Um teste unitário **exigia** a frase do bloqueio; foi trocado por `DoesNotContain("bloquead")`.
- **E-mails fora de template escapam de revisão.** Os dois avisos de atraso eram HTML concatenado no C# e por isso passaram pelas duas levas sem ninguém ver. Varredura de `<p>`/`<br>` em `.cs` no fim da rodada: sobrou só o e-mail de teste de SMTP (admin) e fragmentos de lista dos digests.

## Para o Raffa decidir (não mexido)

- **Cadência dos avisos de atraso.** `LateDonationNotification` roda **diariamente**: quem não escolhe recebe o lembrete no dia da data de escolha, depois o aviso suave todo dia por 5 dias e o "último aviso" todo dia do 6º ao 10º (com cópia para admins), até o cancelamento automático. São até ~11 e-mails. Talvez valha espaçar (ex.: suave no 1º e 3º dia, último aviso só uma vez), mas é decisão de produto.
