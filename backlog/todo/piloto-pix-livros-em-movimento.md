# Piloto PIX — livros em movimento

## Estado

**Top 1 do backlog por decisão do Raffa em 2026-11-19.**

Primeiro experimento de mobilização comunitária para uma solicitação concreta de livro físico. Não substitui nem antecipa a Lista de Desejos v1, que continua sob responsabilidade do Josué; produz a evidência para decidir como ela deve evoluir.

## Hipótese

> Diante de uma pessoa real querendo um livro concreto, a comunidade contribui espontaneamente para colocá-lo em movimento.

O experimento mede mobilização financeira comunitária, não a disponibilidade espontânea de um exemplar parado na estante. As duas evidências são valiosas, mas respondem perguntas diferentes.

## Primeiro caso

- Livro: *O Código Da Vinci*.
- Custo de referência: R$ 10 do exemplar usado + R$ 20 de frete = **R$ 30** por solicitação atendida.
- Regra pública: cada bloco de R$ 30 **confirmado** viabiliza o próximo exemplar para uma solicitação elegível, pela ordem/curadoria já administrada pelo Sharebook.
- Excedente: não é saldo abstrato; abre o próximo livro em movimento.

Antes de publicar, definir explicitamente a conta titular, prazo, destino de um bloco incompleto, regra de compra/envio e política de estorno se a operação ficar impossível.

## Escopo

### PIX rastreável e automático

- Integrar provedor de pagamentos com PIX por API; primeira recomendação: Mercado Pago.
- Criar cobrança individual para R$ 1, R$ 5, R$ 10, R$ 30 ou valor livre, retornando QR Code e copia-e-cola.
- Receber o webhook de pagamento no backend.
- Verificar assinatura do webhook e consultar a API do provedor antes de registrar valor como confirmado.
- Processar eventos de modo idempotente: uma cobrança nunca pode somar duas vezes.
- Guardar credenciais somente como segredo de infraestrutura, nunca no browser, Git ou Telegram.

### Estado público na Home

- Inserir uma faixa discreta logo abaixo do hero; não pop-up e não vaquinha genérica.
- Mostrar o efeito, não um total solto:

  > **3 livros em movimento**  
  > R$ 12 de R$ 30 para o próximo  
  > Cada R$ 30 confirmados coloca um exemplar usado e seu frete no caminho de quem o solicitou.  
  > **[Colocar o próximo livro em movimento]**

- A barra usa exclusivamente pagamentos confirmados pelo provedor.
- Exibir progresso agregado, sem dados de contribuidores ou solicitantes.
- Atualizar após a confirmação sem intervenção manual.

### Distribuição: WhatsApp e mídias sociais

Isto é parte do experimento, não divulgação posterior.

- Publicar primeiro em grupos de WhatsApp e nas redes sociais do Sharebook; não disputar agora a fila do e-mail de onboarding.
- Criar uma peça de storytelling por canal com a mesma promessa verificável:

  > Um livro usado custa R$ 10. Com o frete, são R$ 30 para ele sair da internet e chegar a alguém que já o pediu. A comunidade consegue colocar o próximo livro em movimento?

- Todos os CTAs apontam para a mesma página/âncora, com parâmetros de origem para atribuir contribuições a WhatsApp, Instagram etc.
- Comunicar blocos fechados, compras e livros encaminhados, sem identificar pessoas beneficiadas.
- Registrar peça, data, canal e resultado: a distribuição também é evidência para a decisão de produto.

## Fora de escopo

- Implementar a Lista de Desejos v1.
- Compra, repasse ou marketplace automáticos.
- Disparo pela base de e-mail enquanto a fila de onboarding é drenada.
- Expor dados pessoais, valores individuais ou chaves PIX de contribuidores.

## Critérios de sucesso

### Produto e operação

- Um PIX confirmado chega à barra sem intervenção manual e sem contagem duplicada.
- A origem de cada contribuição pode ser atribuída pelo menos ao canal.
- Existe auditoria privada de contribuição, confirmação, bloco de R$ 30, compra e atendimento.

### Hipótese

- O primeiro bloco de R$ 30 é confirmado por contribuições da comunidade.
- Há clareza sobre quais canais e qual história geraram participação.
- O resultado permite uma conversa concreta com Josué sobre demanda conectável, custo operacional e formato da Lista de Desejos.

## Riscos e proteções

| Risco | Proteção |
|---|---|
| Soma errada ou pagamento forjado | Webhook assinado, consulta canônica ao provedor e idempotência por cobrança. |
| QR estático impede conciliação | Uma cobrança rastreável por contribuição. |
| Campanha vaga | Regra pública de R$ 30 por exemplar + frete e prova posterior de compra/envio. |
| Exposição de pessoas | Progresso agregado; dados individuais ficam no fluxo privado necessário. |
| Saldo sem propósito | Destino do excedente e do bloco incompleto definido antes de publicar. |

## Próximo passo bloqueante

Raffa escolhe e habilita a conta titular do provedor. Com uma conta Mercado Pago apta, implementar a integração mínima: API, webhook, estado da campanha, faixa na Home e checkout.
