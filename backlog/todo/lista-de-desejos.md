# MVP — Lista de Desejos

## Objetivo

Permitir que leitores publiquem livros físicos que gostariam de receber, aumentando as chances de conexão entre doadores e leitores.

A Lista de Desejos vale apenas para livros físicos. E-books já estão disponíveis no acervo digital; desejar ebook não faz parte deste fluxo.

---

## V1 — fluxo conectivo, sem pagamento

1. Solicitante logado pede um livro físico, mesmo que o livro ainda não exista no Sharebook.
2. Pedido entra em revisão.
3. Admin humano ou agente revisa, aprova e normaliza o pedido.
4. Se o livro ainda não existir, o admin cria um `Book` novo como referência de catálogo/lista de desejos, sem deixá-lo `Available` para o fluxo comum de doação.
5. Pedido aprovado aparece na Lista de Desejos.
6. Doador logado navega pela lista e escolhe um pedido.
7. O doador declara que tem o livro e quer atender aquele pedido.
8. Sharebook apresenta doador e solicitante, como no fluxo atual de doação.
9. Doador e solicitante combinam a entrega.
10. Pedido atendido permanece como prova social agregada, sem expor dados pessoais.

Esta v1 existe para validar a pergunta central: demanda explícita gera doação?

---

## Dados do pedido

- Título do livro
- Autor (opcional)
- Pequena justificativa (opcional)
- Data da solicitação
- Status de revisão e atendimento
- Livro normalizado vinculado após aprovação

---

## Regras

- Máximo de 3 pedidos ativos por usuário
- Login obrigatório para criar pedido
- Pedido livre entra em revisão antes de aparecer publicamente
- Admin/agente pode aprovar, rejeitar, normalizar e vincular o pedido a um `Book`
- Um mesmo livro pode ter vários pedidos ativos
- Um pedido individual pode ser atendido apenas uma vez
- Livro atendido não sai da Lista de Desejos se ainda houver outros pedidos ativos para o mesmo livro
- Lista pública deve mostrar prova social agregada, como total de pessoas que desejam e total de pedidos já atendidos
- Contatos só são revelados após o match entre doador e solicitante
- A v1 não tem pagamento, compra pela Amazon nem intermediação financeira

---

## Benefícios

| Para leitores | Para doadores | Para o Sharebook |
|---|---|---|
| Não dependem do livro aparecer na vitrine | Descobrem quem realmente deseja um livro | Aumenta matches |
| Podem desejar livros que ainda não existem no Sharebook | Podem ajudar quando já têm o exemplar físico | Revela livros mais desejados |
| Acompanham pedidos aprovados | São conectados ao solicitante como no fluxo atual | Transforma histórico de doações em demanda futura |
| Veem que pedidos anteriores foram atendidos | Não precisam passar por pagamento na v1 | Cria base para uma v2 patrocinada |

---

## Escopo e restrições

- **MVP simples:** sem Karma, sem priorização, sem IA
- **Sem economia de pontos:** publicar pedido é gratuito no MVP
- **Sem pagamento na v1:** doador e solicitante são apresentados e combinam a entrega
- **Anonimato:** contatos só são revelados após o match (doador escolhe atender)
- **Apenas livros físicos:** e-books ficam fora da Lista de Desejos
- **Book continua sendo a fonte da verdade:** pedido aprovado deve apontar para um `Book`
- **Book criado para desejo não entra na vitrine comum:** não pode aparecer como doação `Available`
- **Stack:** mesma do Sharebook (Angular + .NET + PostgreSQL)

---

## Métrica de sucesso

- Nº de pedidos criados
- Nº de pedidos aprovados
- Nº de matches via lista de desejos
- % de pedidos atendidos
- Tempo médio entre pedido aprovado e match
- Nº de livros com múltiplos interessados
- Nº de pedidos atendidos exibidos como prova social

---

## Evoluções futuras (pós MVP)

- Pagamento para patrocinar a compra do livro
- Compra operacional pelo Sharebook usando link de associado Amazon
- Reembolso quando a compra não puder ser realizada
- Sistema de Karma/Pontos para publicar pedidos
- Priorização de pedidos (mais antigos, mais votados)
- Notificações para possíveis doadores
- Recomendações por IA
- Campanhas baseadas nos livros mais solicitados
