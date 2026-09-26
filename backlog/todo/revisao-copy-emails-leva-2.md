# Revisão de copy dos e-mails da leva 2

## Estado

**Em execução desde 2026-09-26**, um e-mail por vez, com proposta aprovada pelo Raffa antes de aplicar.

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
- [ ] `BookApprovedTemplate` — livro físico aprovado
- [ ] `WaitingApprovalTemplate` — livro físico em revisão
- [ ] `ChooseDateReminderTemplate` / `ChooseDateReminderMultipleTemplate` — lembrete da data de escolha
- [ ] `ChooseDateRenewTemplate` — livro saiu da vitrine / renovação
- [ ] `LateDonationNotification` — doação atrasada
- Fora do escopo (admin/interno): `AnonymizeNotifyAdms`, `NewBookInsertedTemplate`.
