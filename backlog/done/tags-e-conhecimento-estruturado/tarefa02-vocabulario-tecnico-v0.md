# Tarefa 2 — Vocabulário técnico v0 e governança

## Status

Fechada para avanço.

## Objetivo

Transformar o aprendizado do ciclo manual em um vocabulário técnico controlado, pequeno o bastante para ser governável e útil o bastante para descoberta.

## Escopo

- definir tags canônicas iniciais;
- mapear aliases e grafias equivalentes, como `JS`, `JavaScript` e `Node.js`;
- decidir critérios para criar, fundir, renomear e aposentar tags;
- definir quem pode aprovar tag nova;
- documentar regras para a futura skill local de tagging editorial.

## Critérios de pronto

- vocabulário v0 documentado;
- aliases principais definidos;
- regra de criação e revisão clara;
- exemplos positivos e negativos vindos dos cinco livros;
- decisão sobre nível como tag, campo ou não-v1.

## Vocabulário v0

Status da revisão: aprovado por Raffa em 2026-10-02 após expansão orientada a devs e tech leads.

### Linguagens, plataformas e frameworks

| Tag canônica | Aliases / grafias aceitas | Notas |
|---|---|---|
| `C` | `linguagem C`, `C language` | Para material em C; cuidado com menção incidental em livros de SO/compiladores. |
| `C++` | `cpp`, `c plus plus` | Para C++ como linguagem ou ecossistema. |
| `C#` | `c sharp`, `c-sharp` | Linguagem de alto valor para o público dev; não fundir automaticamente com `.NET`. |
| `.NET` | `dotnet`, `ASP.NET`, `NET` | Plataforma/ecossistema; pode conviver com `C#` quando ambos forem relevantes. |
| `Go` | `Golang`, `Go Lang` | Alias exige curadoria para evitar falso positivo com verbo em inglês. |
| `Java` | `java` | Não confundir com `JavaScript`. |
| `JavaScript` | `JS`, `Java Script`, `Node.js`, `NodeJS` | `Node.js` entra como alias inicial; pode virar tag própria se o catálogo justificar. |
| `PHP` | `php` | Stack de alto valor para web/backend legado e atual. |
| `Python` | `python`, `py` | `Pygame` não vira alias; é biblioteca/tópico fino demais. |
| `R` | `linguagem R`, `R language` | Exige curadoria humana; busca textual por "R" gera falso positivo demais. |
| `Scala` | `scala` | Relevante em JVM, dados e programação funcional. |
| `Spring Boot` | `Spring`, `Spring Framework` | Framework de alto valor para backend Java; pode existir mesmo antes de grande massa no catálogo. |
| `TypeScript` | `TS`, `Type Script` | Alto valor para frontend/backend moderno, mesmo com baixa presença atual. |
| `SQL` | `sql` | Linguagem de consulta e sinal de banco relacional; pode conviver com `Bancos de Dados`. |

### Backend, arquitetura e engenharia de software

| Tag canônica | Aliases / grafias aceitas | Notas |
|---|---|---|
| `APIs` | `API`, `REST`, `GraphQL` | Para desenho, consumo e contrato de APIs; não basta mencionar endpoint. |
| `Arquitetura` | `arquitetura de software`, `software architecture` | Decisão estrutural de sistema, não só organização de código. |
| `Backend` | `back-end`, `server-side` | Tag transversal quando categoria não resolver a intenção. |
| `Clean Code` | `código limpo`, `code quality`, `qualidade de código` | Design de código, legibilidade, manutenção e simplicidade. |
| `Design Patterns` | `padrões de projeto`, `patterns` | Não usar como sinônimo genérico de arquitetura. |
| `Event-Driven` | `arquitetura orientada a eventos`, `event sourcing`, `stream processing` | Eventos, streaming, pub/sub, Kafka e padrões assíncronos. |
| `Microsserviços` | `microservices`, `micro-services` | Arquitetura, comunicação, migração e operação de serviços distribuídos pequenos. |
| `Sistemas Distribuídos` | `distributed systems` | Comunicação, consenso, replicação, particionamento e escala. |
| `Testes` | `testing`, `unit testing`, `testes automatizados` | Qualidade verificável, TDD, testes unitários/integrados e automação. |

### Infra, cloud, operação e segurança

| Tag canônica | Aliases / grafias aceitas | Notas |
|---|---|---|
| `AWS` | `Amazon Web Services`, `Amazon S3` | Provedor específico de alto valor; não fundir em `Cloud`. |
| `CI/CD` | `continuous integration`, `continuous delivery`, `pipeline` | Build, testes, deploy e automação de entrega. |
| `Cloud` | `computação em nuvem`, `cloud computing` | Fundamentos e estratégia de nuvem; preferir provedor específico quando for o foco. |
| `DevOps` | `devops`, `operações`, `infra` | Desenvolvimento, deploy, automação, observabilidade ou operação. |
| `Docker` | `docker`, `containers`, `contêineres` | `Contêineres` pode ajudar copy/vitrine, mas a tag pública inicial fica `Docker`. |
| `Git` | `controle de versão`, `version control` | `Controle de Versão` pode virar copy/alias; tag canônica inicial fica `Git`. |
| `Kubernetes` | `kubernetes`, `k8s` | Palavra de alto valor para o público, mesmo com baixa contagem. |
| `Linux` | `Unix`, `shell`, `linha de comando` | Sistema, administração, shell e fundamentos operacionais. |
| `Networking` | `redes`, `TCP/IP`, `IPv6` | Redes de computadores; cuidado com falso positivo em neural networks. |
| `Observabilidade` | `monitoramento`, `logging`, `metrics`, `tracing` | Prometheus, logs, tracing, métricas e diagnóstico operacional. |
| `Segurança` | `security`, `hardening`, `appsec` | Segurança aplicada; não misturar automaticamente com criptografia teórica. |
| `Criptografia` | `cryptography`, `crypto` | Primitivos, protocolos ou teoria criptográfica. |

### Dados, IA e busca

| Tag canônica | Aliases / grafias aceitas | Notas |
|---|---|---|
| `Bancos de Dados` | `databases`, `database`, `banco de dados` | Modelagem, projeto, sistemas de banco e teoria relacional. |
| `Data Science` | `ciência de dados`, `ciencia de dados` | Ciclo de dados; não usar para qualquer livro com estatística isolada. |
| `Deep Learning` | `redes neurais`, `neural networks` | Redes neurais como promessa central. |
| `Estatística` | `statistics`, `statistical learning` | Pode conviver com `Machine Learning` quando estatística é parte central da promessa. |
| `Information Retrieval` | `busca`, `search engines`, `recuperação de informação` | Motores de busca, indexação, ranking e avaliação de busca. |
| `Machine Learning` | `ML`, `aprendizado de máquina` | Manter em inglês pela força de busca do público técnico. |
| `Computer Vision` | `visão computacional`, `image processing` | Processamento de imagem, visão e aplicações visuais de IA. |

### Fundamentos de computação

| Tag canônica | Aliases / grafias aceitas | Notas |
|---|---|---|
| `Algoritmos` | `algorithms` | Análise, projeto e repertório algorítmico. |
| `Arquitetura de Computadores` | `computer architecture`, `organização de computadores` | Hardware, memória, CPU, hierarquia e topologias. |
| `Compiladores` | `compilers`, `compiler design` | Parsing, análise léxica/sintática, geração de código e runtime. |
| `Computação de Alto Desempenho` | `HPC`, `high performance computing` | Performance científica, paralelismo e gargalos de execução. |
| `Estruturas de Dados` | `data structures` | Listas, árvores, heaps, hashing, grafos como estrutura etc. |
| `Matemática Discreta` | `discrete mathematics`, `matematica discreta` | Ponte entre computação e matemática; não substitui categoria Matemática & Lógica. |
| `Métodos Numéricos` | `numerical methods`, `análise numérica` | Para algoritmos numéricos, solvers, álgebra numérica, simulação e cálculo científico. |
| `Sistemas Operacionais` | `operating systems`, `kernel` | Kernel, processos, memória, concorrência, sistemas de arquivos e chamadas de sistema. |
| `Teoria da Computação` | `theory of computation`, `autômatos`, `Turing` | Computabilidade, linguagens formais, autômatos e complexidade teórica. |

### Frontend, gráficos e jogos

| Tag canônica | Aliases / grafias aceitas | Notas |
|---|---|---|
| `Frontend` | `front-end`, `web frontend` | UI/web client, não qualquer coisa visual. |
| `HTML/CSS` | `HTML`, `CSS` | Tag combinada inicial para fundamentos de marcação/estilo. |
| `Web Design` | `design web`, `web design` | Composição, semântica, UX visual e construção de páginas. |
| `Computação Gráfica` | `computer graphics`, `OpenGL`, `rendering`, `ray tracing` | `OpenGL` pode virar tag própria se houver massa/valor. |
| `Desenvolvimento de Jogos` | `game dev`, `game development`, `programação de jogos` | Pygame, Unity patterns e livros de jogos quando a intenção principal é construir jogos. |

### Uso editorial

| Tag canônica | Aliases / grafias aceitas | Notas |
|---|---|---|
| `Prático` | `hands-on`, `guia prático`, `projetos` | Usar quando a estrutura do livro é aplicada: projetos, checklist, laboratório ou passo a passo. |

### Candidatas fora da v0

Estas tags ficam fora por enquanto: `Computação Quântica`, `UX`, `Mobile`, `Android`, `iOS`, `Terraform`, `SRE`, `NoSQL`, `PostgreSQL`, `React`, `Angular`, `Vue`, `Django`, `Laravel`, `Rails`.

Motivo: podem ser excelentes, mas ainda precisam de evidência de catálogo, demanda editorial ou livros concretos antes de entrarem na v0.

## Regras de governança

### Criação de tag

- Tag existe para descoberta pública, não para espelhar toda categoria ou todo capítulo.
- Tag pode nascer com baixa contagem, até com 1 livro, quando a palavra tiver alto valor para o público (`Kubernetes`, `Docker`, `Python`).
- Não há mínimo de livros para a tag existir nem para a navegação pública por tag. Catálogo pequeno é aceitável se a intenção for forte e houver chance real de crescimento.
- O conjunto deve priorizar intenção de devs e tech leads: stack, arquitetura, operação, dados/IA, fundamentos de computação e uso editorial claro.
- Enriquecer vocabulário não é liberar buzzword infinita. Tag precisa ajudar alguém a decidir clique, leitura, trilha ou comparação.
- Tag nova precisa ter nome canônico, aliases, exemplo positivo e pelo menos um contraexemplo.
- Agente tem autonomia para criar/promover tags novas quando elas seguirem estas regras e servirem claramente ao usuário.
- IA de sugestão automática para livros continua restrita ao vocabulário permitido; expansão do vocabulário é autonomia editorial do agente, com registro de racional.

### Aplicação em livros

- Usar no máximo 3 tags visíveis por livro.
- Não é obrigatório preencher 3 tags. Se 2 forem mais honestas, ficam 2.
- Não repetir a categoria como tag se ela não acrescentar intenção de busca.
- Preferir nome buscável pelo público a termo guarda-chuva abstrato: `Kubernetes` vence `Cloud Native`; `Python` vence `Programação`.
- Tagar pela promessa editorial do livro, não pela categoria atual. O ciclo manual mostrou categorias históricas ruidosas.

### Fusão, renomeação e aposentadoria

- Alias não é tag duplicada. `k8s` aponta para `Kubernetes`; `aprendizado de máquina` aponta para `Machine Learning`.
- Renomear tag exige preservar identidade estável quando houver schema, com slug antigo redirecionando ou virando alias.
- Fundir tags quando duas intenções forem indistinguíveis para navegação pública.
- Aposentar tag significa deixá-la inativa para novas aplicações, não apagar histórico.

### Aprovação

- Raffa delegou autonomia editorial ao agente para evoluir o vocabulário dentro das preferências já alinhadas: usuário em primeiro lugar, devs e tech leads como público prioritário, descoberta útil acima de taxonomia ornamental.
- Agente não precisa pedir aprovação tag por tag. Deve decidir, registrar racional, exemplos e rejeições, e deixar a mudança revisável.
- Pedir revisão de Raffa apenas para mudanças estruturais: nova família de tags, alteração de limite público, mudança em regra de governança, conflito conceitual forte ou dúvida editorial real.
- Ao final desta fase, as regras aprovadas devem virar skill local de tagging editorial quando isso for explicitamente solicitado.

## Exemplos do ciclo manual

| Livro | Tags aprovadas | Aprendizado |
|---|---|---|
| `Making Games with Python & Pygame` | `Python`, `Desenvolvimento de Jogos`, `Prático` | Biblioteca específica (`Pygame`) não precisa virar tag se a intenção pública melhor é jogos em Python. |
| `Kubernetes for Full-Stack Developers` | `Kubernetes`, `Docker`, `DevOps` | Tags de stack podem ser mais úteis que categoria; `Cloud Native` ficou vago demais. |
| `An Introduction to Statistical Learning` | `Machine Learning`, `Estatística`, `R` | `Data Science` era mais genérico que a intenção real. |
| `Microservices AntiPatterns and Pitfalls` | `Microsserviços`, `Arquitetura`, `Prático` | Livro de arquitetura pode precisar de uso editorial quando funciona como checklist/revisão de design. |
| `The Art of High Performance Computing - Volume 1` | `Computação de Alto Desempenho`, `Arquitetura de Computadores`, `Métodos Numéricos` | Livro ambíguo em `Tecnologia > Geral` pode ficar descobrível com tags sem depender de recategorizar tudo. |

## Correção editorial 2026-10-02

Raffa rejeitou o primeiro vocabulário v0 como pobre demais para um catálogo técnico. Ajuste incorporado:

- O vocabulário v0 passa a ser organizado por famílias: linguagens/frameworks, backend/arquitetura, infra/cloud/segurança, dados/IA, fundamentos de computação, frontend/gráficos/jogos e uso editorial.
- Entram tags de alto valor para devs e tech leads mesmo quando não apareceram nos 5 livros do ciclo manual.
- O vocabulário v0 não precisa nascer apenas dos 5 livros; ele deve combinar evidência do ciclo, sinais do catálogo e conhecimento editorial do público dev.
- Tags de stack de alto valor podem existir mesmo antes de grande massa no catálogo, porque amanhã o acervo cresce e a navegação por tags deve ser livre.

## Decisões explícitas

- `Nível` fica fora das tags visíveis na v1. Será campo separado ou metadado próprio nas tarefas 3 e 7.
- `Acadêmico` sai do vocabulário: é alegação editorial fraca para clique.
- `Boas Práticas` sai do vocabulário: vira etiqueta genérica fácil de abusar.
- `Prático` fica porque comunica uma forma de uso clara quando o livro é projeto, laboratório, checklist ou guia operacional.
