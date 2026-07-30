# MVP — Lista de Desejos (Doação Reversa)

## Objetivo

Permitir que leitores publiquem livros que gostariam de receber, aumentando as chances de conexão entre doadores e leitores.

---

## Fluxo

1. Leitor cria um pedido
2. Pedido entra na Lista de Desejos
3. Doador navega pela lista
4. Doador escolhe um pedido para atender
5. Pedido é removido da lista
6. Contatos são liberados e a doação segue o fluxo atual

---

## Dados do pedido

- Título do livro
- Autor (opcional)
- Pequena justificativa (opcional)
- Data da solicitação

---

## Regras

- Máximo de 3 pedidos ativos por usuário
- Um pedido pode ser atendido apenas uma vez
- Ao ser atendido, sai automaticamente da lista
- Login obrigatório para criar pedido

---

## Benefícios

| Para leitores | Para doadores | Para o Sharebook |
|---|---|---|
| Não dependem do livro aparecer na vitrine | Descobrem quem realmente deseja um livro | Aumenta matches |
| Demonstram interesse por livros específicos | Escolhem qual pedido atender | Revela livros mais desejados |
| | | Nova forma de descoberta de doações |

---

## Escopo e restrições

- **MVP simples:** sem Karma, sem priorização, sem IA
- **Sem economia de pontos:** publicar pedido é gratuito no MVP
- **Anonimato:** contatos só são revelados após o match (doador escolhe atender)
- **Stack:** mesma do Sharebook (Angular + .NET + PostgreSQL)

---

## Métrica de sucesso

- Nº de pedidos criados
- Nº de matches via lista de desejos
- % de pedidos atendidos

---

## Evoluções futuras (pós MVP)

- Sistema de Karma/Pontos para publicar pedidos
- Priorização de pedidos (mais antigos, mais votados)
- Notificações para possíveis doadores
- Recomendações por IA
- Campanhas baseadas nos livros mais solicitados
