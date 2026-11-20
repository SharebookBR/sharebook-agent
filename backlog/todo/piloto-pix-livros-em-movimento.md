# Piloto de vaquinha — livros em movimento

## Estado

**Top 1 do backlog por decisão do Raffa em 2026-11-19.**

**Lançado em 2026-11-19.** A campanha pública está em [Vakinha — Doe um livro](https://www.vakinha.com.br/vaquinha/doe-um-livro), com capa aprovada e divulgação inicial feita por WhatsApp. Agora o experimento entra em janela de observação: não ampliar produto nem integração antes da leitura dos dados.

Primeiro experimento de mobilização comunitária para uma solicitação concreta de livro físico. Não substitui nem antecipa a Lista de Desejos v1, que continua sob responsabilidade do Josué; produz a evidência para decidir como ela deve evoluir.

## Hipótese

> Diante de uma pessoa real querendo um livro concreto, a comunidade contribui espontaneamente para colocá-lo em movimento.

O experimento mede mobilização financeira comunitária, não a disponibilidade espontânea de um exemplar parado na estante. As duas evidências são valiosas, mas respondem perguntas diferentes.

## Primeiro caso

- Livro: *O Código Da Vinci*.
- Custo de referência: R$ 10 do exemplar usado + R$ 20 de frete = **R$ 30** por solicitação atendida.
- Regra pública: cada bloco de R$ 30 **confirmado** viabiliza o próximo exemplar para uma solicitação elegível, pela ordem/curadoria já administrada pelo Sharebook.
- Excedente: não é saldo abstrato; abre o próximo livro em movimento.

A campanha usa meta de R$ 150. O valor líquido, depois das taxas da plataforma, define quantos exemplares podem de fato ser comprados e enviados; a comunicação não promete um número fixo de livros sem essa confirmação.

## Escopo

### Campanha pronta, sem integração

- Publicar a campanha em uma plataforma brasileira consolidada de vaquinha; primeira recomendação: **Vakinha**.
- Usar a página, o checkout PIX, a barra de progresso e a confirmação de pagamento nativos da plataforma.
- Não integrar API de pagamentos, webhook, banco de contribuições nem faixa de progresso na Home do Sharebook.
- O Sharebook apenas aponta para a campanha e publica atualizações de compra e envio depois dos blocos fechados.
- Guardar acessos à conta da campanha fora do browser público, Git ou Telegram.

### Distribuição: WhatsApp e mídias sociais

Isto é parte do experimento, não divulgação posterior.

- Publicar primeiro em grupos de WhatsApp e nas redes sociais do Sharebook; não disputar agora a fila do e-mail de onboarding.
- Criar uma peça de storytelling por canal com a mesma promessa verificável:

  > Um livro usado custa R$ 10. Com o frete, são R$ 30 para ele sair da internet e chegar a alguém que já o pediu. A comunidade consegue colocar o próximo livro em movimento?

- Todos os CTAs apontam para a mesma campanha. Usar links distintos por canal para medir ao menos cliques; se a plataforma oferecer atribuição de contribuições, registrar também esse dado, sem depender dele.
- Comunicar blocos fechados, compras e livros encaminhados, sem identificar pessoas beneficiadas.
- Registrar peça, data, canal e resultado: a distribuição também é evidência para a decisão de produto.

## Fora de escopo

- Implementar a Lista de Desejos v1.
- Integração própria de pagamentos, webhook, conciliação automatizada ou barra de campanha na Home.
- Compra, repasse ou marketplace automáticos.
- Disparo pela base de e-mail enquanto a fila de onboarding é drenada.
- Expor dados pessoais, valores individuais ou chaves PIX de contribuidores.

## Critérios de sucesso

### Produto e operação

- A plataforma confirma os PIX e atualiza a própria barra sem intervenção manual.
- Há links distintos e métricas de clique por canal; atribuição de contribuição é complementar, não requisito.
- Existe registro privado dos blocos de R$ 30, da compra e do atendimento.

### Hipótese

- O primeiro bloco de R$ 30 é confirmado por contribuições da comunidade.
- Há clareza sobre quais canais e qual história geraram participação.
- O resultado permite uma conversa concreta com Josué sobre demanda conectável, custo operacional e formato da Lista de Desejos.

## Riscos e proteções

| Risco | Proteção |
|---|---|
| Integração virar produto antes de haver evidência | A plataforma de vaquinha é dona do checkout, da confirmação e da barra no piloto. |
| Taxa ou regra da plataforma reduzir o valor útil | Definir meta e regra de blocos já considerando taxa e repasse líquido. |
| Campanha vaga | Regra pública de R$ 30 por exemplar + frete e prova posterior de compra/envio. |
| Exposição de pessoas | Progresso agregado; dados individuais ficam no fluxo privado necessário. |
| Saldo sem propósito | Destino do excedente e do bloco incompleto definido antes de publicar. |

## Próximo passo: decisão go/no-go

Em **2026-12-05 às 00:51 UTC** (2026-12-04 às 21:51 em Brasília), avaliar o piloto com Raffa e decidir **go/no-go da Lista de Desejos**. Levar para a conversa:

- valor bruto e líquido arrecadado, quantidade de contribuições e blocos de R$ 30 efetivamente viabilizados;
- cliques, canais e peças que trouxeram participação, dentro do que a Vakinha e os links permitirem medir;
- esforço real de compra, envio e prestação de contas;
- se a resposta valida mobilização comunitária suficiente para justificar uma Lista de Desejos — ou se indica que a hipótese precisa de outro corte.

Até essa decisão, a Lista de Desejos continua pertencendo ao Josué e não entra em implementação por este piloto.
