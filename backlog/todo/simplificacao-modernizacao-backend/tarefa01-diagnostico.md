# Tarefa 1 — Diagnóstico de arquitetura e custo cognitivo (sharebook-backend)

## Status

**Diagnóstico entregue em 2026-09-19** — ver [`diagnostico.md`](diagnostico.md). Aguardando revisão do Raffa antes de fatiar as tarefas de execução (2, 3, 4...). Nenhuma refatoração foi feita ainda; a investigação foi só leitura de código real na branch `develop` pós-sync com `master` (commit `b27a6a6`).

Resumo dos achados principais (detalhe completo em `diagnostico.md`):
- `BookController` (823 linhas) e `BookService` (1101 linhas / 30 métodos públicos) concentram responsabilidades não relacionadas (CRUD, busca, admin/stats, sitemap, recomendação, e-book).
- `OperationsController` (313 linhas) é uma gaveta genérica que esconde todo o domínio do importer de ebooks atrás de um nome de infraestrutura.
- Camada dupla `RepositoryGeneric<T>` + `BaseService<T>` reimplementando, com indireção extra, o que `DbSet<T>`/`IQueryable<T>` do EF Core já resolve.
- 28 das 29 interfaces em `ShareBook.Service` têm exatamente 1 implementação — existem só para permitir mock em teste.
- `Thread.CurrentPrincipal?.Identity?.Name` repetido 20 vezes por falta de um acessor único de usuário autenticado.
- Pastas `AWSSQS/`/`AwsSqs/` duplicadas por casing; `BookDownload` (abril) e `BookDownloadEvent` (setembro) coexistindo como duas fontes paralelas do mesmo dado, achado durante o merge `develop`↔`master` desta sessão.
- `Nullable` (nullable reference types) nunca ligado em nenhum projeto de produção, apesar de todos rodarem .NET 10.
- Cobertura de teste: 11/27 services (41%) e 3/10 controllers — `BookController` e `AccountController`, os dois mais críticos, sem nenhuma cobertura direta ou de integração.

⚠️ Esta investigação foi feita só com leitura estática de código — não havia .NET SDK disponível no ambiente desta sessão para rodar build ou testes.

## Briefing original (Raffa, 2026-09-19)

# Diagnóstico para simplificação e modernização do backend Sharebook

O backend do Sharebook também carrega muitos anos de história.

Quero iniciar uma nova fase de simplificação e modernização, mas o objetivo principal **não é atualizar tecnologias ou aplicar patterns modernos**.

A prioridade é:

> **reduzir custo cognitivo e tornar o backend humano friendly e IA friendly.**

Quero um código que seja fácil de descobrir, navegar, entender e modificar — tanto por um desenvolvedor que nunca viu o projeto quanto por um agente de IA trabalhando com contexto limitado.

## Princípio central

Faça constantemente esta pergunta:

> Se estivéssemos construindo este backend hoje, conhecendo o domínio do Sharebook como conhecemos agora, ele teria esta forma?

Não assuma que pastas, projetos, layers, abstrações, interfaces, services, repositories, helpers, DTOs ou patterns existentes merecem continuar existindo apenas porque funcionam.

Tenha **desapego total ao passado, mas sem perder funcionalidades**.

Também não quero trocar arquitetura antiga por arquitetura sofisticada nova.

> **Não me entregue uma arquitetura mais bonita. Entregue uma arquitetura que precise de menos explicação.**

---

## IA friendly

Quero tratar "IA friendly" como requisito arquitetural explícito.

Um agente deveria conseguir entrar no repositório e descobrir rapidamente:

- onde mora uma regra de negócio;
- onde começa um caso de uso;
- quais arquivos participam dele;
- onde estão os contratos de entrada e saída;
- onde ocorre persistência;
- onde estão integrações externas;
- quais são as fronteiras entre os domínios;
- quais dependências uma mudança pode afetar;
- onde deve criar código novo para determinada funcionalidade.

Considere o contexto de uma IA como um recurso limitado.

Se para alterar uma regra simples o agente precisa abrir dezenas de arquivos espalhados pelo projeto apenas para reconstruir mentalmente a arquitetura, existe custo arquitetural real.

Faça esta pergunta durante o diagnóstico:

> **Quanto contexto um agente precisa carregar para alterar com segurança uma regra de negócio?**

Quero reduzir esse custo.

Mas não crie arquivos, comentários, documentação ou abstrações apenas para explicar o código para uma IA.

A melhor documentação arquitetural é uma estrutura que seja óbvia por si mesma.

---

## O que analisar

Faça uma investigação real do código antes de propor mudanças.

Analise especialmente:

- estrutura de solution/projects;
- organização de diretórios;
- organização por camada técnica versus domínio/capability/feature;
- localização das regras de negócio;
- tamanho e responsabilidade das classes;
- services grandes ou genéricos demais;
- controllers com responsabilidades excessivas;
- repositories e interfaces que apenas adicionam indireção;
- abstrações com uma única implementação;
- DTOs, models, entities e ViewModels redundantes;
- mapeamentos repetitivos;
- helpers e utils usados como gavetas genéricas;
- duplicação;
- código morto;
- código histórico mantido apenas por compatibilidade;
- nomes que dificultam descoberta;
- dependências circulares ou pouco claras;
- responsabilidades espalhadas por muitos projetos ou diretórios;
- quantidade de arquivos necessária para compreender um único fluxo;
- configuração e dependency injection excessivamente fragmentadas;
- tratamento de erros;
- logging;
- acesso a dados;
- integrações externas;
- autenticação e autorização;
- código assíncrono;
- nullability e tipagem;
- testes e testabilidade;
- dependências antigas;
- recursos modernos da versão atual do .NET que realmente possam simplificar o código.

Procure também classes que deveriam:

- deixar de existir;
- ser unidas;
- ser divididas;
- ser renomeadas;
- mudar de lugar;
- perder uma interface desnecessária;
- aproximar-se do domínio ao qual pertencem.

---

## Não parta de uma arquitetura pronta

Não assuma previamente que precisamos de:

- Clean Architecture;
- Hexagonal Architecture;
- Vertical Slice Architecture;
- DDD;
- CQRS;
- MediatR;
- Repository Pattern;
- Unit of Work;
- ou qualquer outra arquitetura/pattern.

Eles são ferramentas, não objetivos.

Se algum deles já existir, questione se está pagando o próprio custo cognitivo.

Se alguma dessas ideias simplificar concretamente o Sharebook, proponha.

Se aumentar quantidade de arquivos, indireções ou conceitos necessários para compreender uma operação sem benefício proporcional, não proponha.

Também não copie automaticamente a organização adotada no frontend.

O backend deve encontrar suas próprias fronteiras naturais.

---

## Exercício de descoberta

Escolha alguns fluxos reais e importantes do Sharebook e faça o caminho completo pelo código.

Por exemplo:

- encontrar um livro;
- cadastrar/publicar um livro;
- solicitar um livro;
- realizar uma doação;
- autenticar um usuário;
- alterar alguma informação de usuário.

Adapte os exemplos ao que realmente existir no código.

Para cada fluxo, responda:

1. onde ele começa;
2. quais arquivos precisam ser abertos para compreendê-lo;
3. por quantas camadas/abstrações ele passa;
4. onde está a regra de negócio;
5. onde estão persistência e integrações;
6. quais partes foram difíceis de descobrir;
7. quais indireções realmente agregam valor;
8. quais existem apenas por herança arquitetural.

Isso deve fornecer evidência concreta do custo cognitivo atual.

---

## Primeira entrega: diagnóstico, não implementação

**Não refatore nada ainda.**

Primeiro quero um diagnóstico baseado no código real.

Entregue:

1. **Mapa da arquitetura atual**
   - projects;
   - diretórios principais;
   - dependências;
   - principais domínios;
   - onde vivem regras, persistência e integrações.

2. **Principais fontes de custo cognitivo**
   - com exemplos concretos encontrados no código.

3. **Análise IA friendly**
   - onde um agente atualmente gastaria contexto desnecessariamente;
   - quantos lugares precisa visitar para compreender fluxos importantes;
   - onde a descoberta é ruim;
   - onde nomes ou estrutura ajudam ou atrapalham.

4. **O que você eliminaria**
   - arquivos;
   - abstrações;
   - interfaces;
   - layers;
   - duplicações;
   - código morto;
   - conceitos que não pagam mais seu custo.

5. **O que você uniria, dividiria, moveria ou renomearia**
   - sempre justificando pela redução de custo cognitivo.

6. **Arquitetura que escolheria hoje**
   - sem compromisso com a estrutura histórica;
   - explique por que ela é mais simples;
   - mostre uma árvore de diretórios concreta como exemplo.

7. **Comparação antes/depois**
   - especialmente usando os fluxos reais investigados.

   Quero conseguir enxergar algo como:

   Antes:
   "Para entender X preciso atravessar A → B → C → D → E."

   Depois:
   "X está concentrado aqui e depende explicitamente apenas de Y."

8. **Plano incremental de migração**
   - pequenas mudanças;
   - reversíveis;
   - testáveis;
   - sem perder funcionalidade;
   - sem big bang.

---

## Métrica principal

Não medir sucesso pela quantidade de APIs modernas adotadas nem pela quantidade de patterns aplicados.

O objetivo é conseguir abrir o backend depois da modernização e pensar:

> **"É óbvio onde cada coisa mora."**

E um agente conseguir receber uma tarefa de negócio, encontrar rapidamente o contexto necessário e fazer uma alteração segura sem precisar compreender o sistema inteiro.

Em outras palavras: **menos lugares para procurar, menos conceitos para carregar, menos arquivos para compreender e menos contexto desperdiçado.**

Modernização tecnológica é bem-vinda quando ajudar nisso. Simplificação vem primeiro.

## Como validar que a tarefa está concluída

O diagnóstico é aceito quando cobre as 8 entregas da seção "Primeira entrega" acima, com evidência real do código, não estimativa — mesmo padrão do diagnóstico que abriu o épico do frontend (`todo/simplificacao-modernizacao-frontend/index.md`, seção "Diagnóstico — números que sustentam as tarefas"). Entregue em `diagnostico.md`. Depois de revisado pelo Raffa, vira a base para fatiar as tarefas de execução (2, 3, 4...) deste épico, com prioridade e cadência de lote decididas então — igual ao frontend.
