# E-mails de descoberta: pré-lançamento e afinidade por categoria

## Estado: pendente de desenho de cadência

O pré-lançamento de ebook entrou no produto em 2026-11-25: um ebook pode ficar `Scheduled`, exibir data, receber pedidos de aviso e abrir automaticamente no dia definido.

Hoje os dois e-mails de descoberta têm janelas e públicos independentes:

- o digest diário das 8h divulga **livros físicos** `Available` aprovados nas últimas 24h;
- o mailing semanal de segunda-feira divulga **ebooks** `Available` aprovados nos últimos 7 dias;
- ambos definem o público apenas por `BookUsers`: a pessoa já solicitou um livro naquela categoria. Um download autenticado de ebook não conta como afinidade.

Isso deixa de fora justamente quem já demonstrou interesse real por leitura digital.

Falta decidir e implementar duas evoluções complementares:

- **Audiência por afinidade:** substituir a consulta de “pessoas que solicitaram” por uma única audiência por categoria, deduplicada, que una:
  - pessoas que já solicitaram livro físico da categoria (`BookUsers`);
  - pessoas autenticadas que já baixaram ebook da categoria (`BookDownloadEvents.UserId` não nulo).
  A mesma regra deve valer para ambos os digests: quem baixou Ficção pode receber novidades físicas ou digitais de Ficção; quem já solicitou físico continua elegível para as duas modalidades. Downloads anônimos não entram porque não há pessoa para associar. A regra respeita `AllowSendingEmail`/descadastro e não cria mais de um e-mail por pessoa em cada execução.

- **Pré-lançamento:** apresentar de forma honesta os títulos que ainda não podem ser baixados:

- **Mailing semanal de ebooks:** incluir uma seção curta de “Em breve”, com capa, data e CTA para pedir aviso, sem misturar esses títulos aos já disponíveis para leitura.
- **E-mail diário de novos livros:** manter o anúncio de físico no dia em que fica disponível e avaliar uma menção separada a lançamentos próximos; não anunciar ebook por esse job enquanto ele não estiver disponível.
- **Deduplicação:** quem pediu o aviso de um ebook pode receber o aviso de liberação e o digest diário no mesmo dia. Decidir se essa duplicidade é desejada, aceitável ou se uma das mensagens deve ser suprimida.

## Critérios de aceite

- Todo título agendado deixa explícito que ainda não está disponível para download.
- O CTA de pré-lançamento cria `BookReleaseInterest`; o CTA de lançamento abre a PDP para receber o livro digital.
- Os dois digests usam a audiência deduplicada por afinidade de categoria (solicitação física **ou** download autenticado).
- O digest diário só chama de novidade o livro físico que já está `Available`; o semanal só chama de novidade o ebook que já está `Available`.
- A regra de duplicidade fica explícita e coberta por teste.
