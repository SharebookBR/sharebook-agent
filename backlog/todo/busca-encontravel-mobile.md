# Tornar a busca encontrável no mobile

## Problema

A busca existe e funciona, mas sua entrada principal desaparece abaixo de `768px`.

Na experiência mobile atual:

- o header público mostra apenas o logo;
- visitantes deslogados recebem na navegação inferior `Vitrine`, `Pedidos`, `Doe`, `Doações` e `Entrar`;
- a busca fica dentro da folha `Mais`, que só aparece para usuário logado;
- portanto, quem chega deslogado pelo mobile não encontra uma entrada visível para buscar livros.

Esconder a busca contradiz a prioridade de melhorar sua relevância: busca melhor que ninguém encontra é decoração de arquitetura.

## Decisão obrigatória antes da implementação

**Discutir o desenho com Raffa antes de escrever código.**

A discussão deve decidir:

- onde a busca aparece no primeiro nível da navegação mobile;
- se a interação abre um campo, uma tela dedicada ou outro padrão;
- como preservar espaço para doação, conta e navegação principal;
- como o comportamento se mantém consistente para usuários logados e deslogados.

Nenhuma das alternativas acima está escolhida por este backlog.

## Objetivo

Dar à busca uma entrada óbvia, acessível e rápida no mobile, sem depender de login nem de conhecimento prévio do menu.

## Critérios de aceite

- desenho discutido e aprovado antes da implementação;
- busca visível ou alcançável em primeiro nível abaixo de `768px`;
- mesma capacidade para visitante logado e deslogado;
- fluxo reutiliza a rota e o contrato de busca existentes;
- navegação por teclado, nome acessível e foco funcionam corretamente;
- evento de analytics continua registrando o termo pesquisado;
- testes protegem o comportamento relevante, sem se limitar a conferir detalhes cosméticos;
- build e suíte útil do frontend passam no pipeline.

## Fora de escopo

- implementar FTS ou fuzzy search;
- redesenhar toda a navegação mobile;
- introduzir recomendações vetoriais;
- escolher a solução visual sem a discussão prévia.
