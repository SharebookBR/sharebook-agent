# Onboarding e ativação por e-mail

Concluído em 2026-10-23.

## Decisão de produto

A sequência é fixa. Não observa se a pessoa solicitou, baixou ou doou um livro para trocar o conteúdo. Cinco mensagens contam uma história coerente e chegam uma única vez: boas-vindas, catálogo, impacto da doação, escolha anônima e comunidade.

| Quando | Tema | CTA |
|---|---|---|
| Imediato | Bem-vindo ao Sharebook | Explorar a vitrine |
| Dia 1 | Seu próximo livro pode estar aqui | Explorar o catálogo |
| Dia 3 | Todo livro importa. Muito. | Doar um livro |
| Dia 5 | Não é sorteio. É escolha. | Explorar a vitrine |
| Dia 7 | A biblioteca continua na conversa | Entrar na comunidade |

O quinto e-mail convida voluntariamente para a comunidade WhatsApp. Nunca adiciona contatos automaticamente e não trata o grupo como suporte obrigatório.

## Implementação

- `OnboardingJourney` persiste etapa, próximo horário, enfileiramento, conclusão/cancelamento e motivo.
- A jornada começa para cada cadastro elegível, inclusive depois da aprovação parental; `descadastrar`, conta inelegível ou bounce cancelam as etapas restantes.
- `OnboardingEmailSender` executa a cada cinco minutos, entrega pela fila de baixa prioridade já existente e avança apenas após enfileirar a mensagem. Reexecuções não duplicam etapa.
- O job vem antes do `MailSender`, para a mensagem imediata poder ser enviada no mesmo ciclo do executor.
- Os cinco templates responsivos usam as artes editoriais aprovadas, CTAs reais e link de descadastro.
- A migration `AddOnboardingJourneys` cria a tabela e os índices da jornada.

## Validação

- Testes unitários cobrem templates, substituição de links, criação/cancelamento idempotente da jornada e a agenda fixa completa até o dia 7.
- A implementação respeita o limite de envio SMTP existente e usa o tratamento de bounce já consolidado.

## Fora do escopo deliberado

- Personalização por comportamento, IA, newsletter recorrente e automação de WhatsApp.
- Métricas de abertura/clique: dependem de instrumento de tracking próprio e não foram inventadas nesta entrega.
