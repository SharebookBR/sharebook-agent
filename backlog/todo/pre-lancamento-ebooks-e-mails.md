# Pré-lançamento de ebooks nos e-mails de descoberta

## Estado: pendente de desenho de cadência

O pré-lançamento de ebook entrou no produto em 2026-11-25: um ebook pode ficar `Scheduled`, exibir data, receber pedidos de aviso e abrir automaticamente no dia definido. A liberação continua marcando `ApprovedAt`, portanto o digest diário de novidades das 8h o inclui quando ele se torna disponível — não no dia em que foi agendado.

Falta decidir e implementar como as comunicações de descoberta devem apresentar essa previsibilidade antes da liberação:

- **Mailing semanal de ebooks:** incluir uma seção curta de “Em breve”, com capa, data e CTA para pedir aviso, sem misturar esses títulos aos já disponíveis para leitura.
- **E-mail diário de novos livros:** preservar o anúncio de ebook no dia da liberação e avaliar uma menção separada a lançamentos próximos; não antecipar como se o download já estivesse disponível.
- **Deduplicação:** quem pediu o aviso de um ebook pode receber o aviso de liberação e o digest diário no mesmo dia. Decidir se essa duplicidade é desejada, aceitável ou se uma das mensagens deve ser suprimida.

## Critérios de aceite

- Todo título agendado deixa explícito que ainda não está disponível para download.
- O CTA de pré-lançamento cria `BookReleaseInterest`; o CTA de lançamento abre a PDP para receber o livro digital.
- O digest diário só chama de novidade o que já está `Available`.
- A regra de duplicidade fica explícita e coberta por teste.
