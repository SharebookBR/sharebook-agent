# Tornar a busca encontrável no mobile

**Status:** concluído em 29/08/2026.

## Problema resolvido

A busca existia e funcionava, mas sua entrada principal desaparecia abaixo de `768px`. Visitantes deslogados não tinham uma entrada visível em primeiro nível para buscar livros.

## Decisão de produto

O desenho foi discutido e aprovado antes da implementação:

- ícone de lupa persistente no canto direito do header mobile;
- toque expande o campo de busca logo abaixo do logo, sem abrir outra tela;
- navegação inferior permanece intacta;
- mesmo comportamento para visitantes logados e deslogados;
- rota, contrato, componente de busca e evento de analytics existentes são reutilizados.

## Implementação

- header mobile reorganizado em grade simétrica para manter o logo centralizado;
- alvo de toque da busca com `44 × 44px`;
- painel inline reutiliza `app-input-search`;
- foco entra automaticamente no campo ao abrir;
- `aria-label`, `aria-expanded` e `aria-controls` descrevem o estado;
- `Escape` fecha o painel e devolve o foco ao botão;
- submissão fecha o painel e mantém a rota `/buscar/:termo`;
- o evento GA4 `search` continua sendo emitido por `SearchResultsComponent` após a resposta da busca.

## Evidências

- frontend `fbfc87bae9f8b13a9103f9fcb1dbea13560a6ffb`;
- 6 testes direcionados aprovados para header e input de busca;
- suíte completa: 76 testes, 29 sucessos e as mesmas 47 falhas históricas já isoladas em `RegisterComponent` e `FormComponent`; nenhuma falha nova nos componentes alterados;
- `npm run build-prod` aprovado;
- projeto não possui target de lint configurado;
- inspeção local em `375px`, `767px`, `768px` e `1280px`;
- deploy Coolify `m33l0pvd4kpjmqbcgyut8ufs` concluído;
- container `sharebook-frontend` saudável na imagem do SHA exato;
- produção em `375px`: lupa visível, foco automático e busca por `C#` navegando para `/buscar/C%23`, com resultados do contrato atual.

## Critérios de aceite

- [x] desenho discutido e aprovado antes da implementação;
- [x] busca alcançável em primeiro nível abaixo de `768px`;
- [x] mesma capacidade para visitante logado e deslogado;
- [x] rota e contrato existentes reutilizados;
- [x] navegação por teclado, nome acessível e foco protegidos;
- [x] evento de analytics preservado;
- [x] testes de comportamento adicionados;
- [x] build e suíte direcionada aprovados.

## Dívida observada, fora do escopo

Em `768px` o Bootstrap já troca para o header desktop antigo, que fica apertado nesse limite. A mudança mobile não introduziu essa condição; uma revisão futura pode tratar o intervalo de tablet junto da navegação responsiva como um todo.
