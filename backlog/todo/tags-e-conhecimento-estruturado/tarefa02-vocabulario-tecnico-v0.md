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

### Stack, ferramenta ou tecnologia

| Tag canônica | Aliases / grafias aceitas | Notas |
|---|---|---|
| `Python` | `python`, `py` | `Pygame` não vira alias; é biblioteca/tópico fino demais. |
| `R` | `linguagem R`, `R language` | Exige curadoria humana; busca textual por "R" gera falso positivo demais. |
| `Docker` | `docker`, `containers`, `contêineres` | `Contêineres` pode ajudar copy/vitrine, mas a tag pública inicial fica `Docker`. |
| `Kubernetes` | `kubernetes`, `k8s` | Palavra de alto valor para o público, mesmo com baixa contagem. |

### Área, problema ou domínio

| Tag canônica | Aliases / grafias aceitas | Notas |
|---|---|---|
| `Arquitetura` | `arquitetura de software`, `design de software`, `software architecture` | Usar quando a promessa é decisão estrutural de sistema, não só organização de código. |
| `Arquitetura de Computadores` | `computer architecture`, `organização de computadores` | Para hardware, memória, CPU, hierarquia e topologias. |
| `Computação de Alto Desempenho` | `HPC`, `high performance computing` | Para performance científica, paralelismo e gargalos de execução. |
| `Desenvolvimento de Jogos` | `game dev`, `game development`, `programação de jogos` | Cobre Pygame, Unity patterns e livros de jogos quando a intenção principal é construir jogos. |
| `DevOps` | `devops`, `operações`, `infra` | Usar quando o livro conecta desenvolvimento, deploy, automação, observabilidade ou operação. |
| `Estatística` | `statistics`, `statistical learning` | Pode conviver com `Machine Learning` quando estatística é parte central da promessa. |
| `Machine Learning` | `ML`, `aprendizado de máquina` | Manter em inglês pela força de busca do público técnico. |
| `Métodos Numéricos` | `numerical methods`, `análise numérica` | Para algoritmos numéricos, solvers, álgebra numérica, simulação e cálculo científico. |
| `Microsserviços` | `microservices`, `micro-services` | Para arquitetura, comunicação, migração e operação de serviços distribuídos pequenos. |

### Uso editorial

| Tag canônica | Aliases / grafias aceitas | Notas |
|---|---|---|
| `Prático` | `hands-on`, `guia prático`, `projetos` | Usar quando a estrutura do livro é aplicada: projetos, checklist, laboratório ou passo a passo. |

### Candidatas fora da v0

Estas tags têm sinal no catálogo, mas ainda não foram testadas nos 5 livros do ciclo manual:

- `Sistemas Operacionais`
- `Criptografia`
- `Segurança`
- `Computação Gráfica`
- `Controle de Versão`
- `Git`
- `Computação Quântica`
- `Matemática Discreta`
- `Teoria da Computação`
- `Estruturas de Dados`
- `Bancos de Dados`
- `Referência`

Elas podem entrar quando aparecerem em uma rodada editorial concreta. `Segurança` deve ser avaliada com cuidado para não misturar criptografia, hardening, pentest e governança como se fossem a mesma intenção.

## Regras de governança

### Criação de tag

- Tag existe para descoberta pública, não para espelhar toda categoria ou todo capítulo.
- Tag pode nascer com baixa contagem, até com 1 livro, quando a palavra tiver alto valor para o público (`Kubernetes`, `Docker`, `Python`).
- Não há mínimo de livros para a tag existir nem para a navegação pública por tag. Catálogo pequeno é aceitável se a intenção for forte e houver chance real de crescimento.
- Tag nova precisa ter nome canônico, aliases, exemplo positivo e pelo menos um contraexemplo.
- IA pode sugerir apenas dentro do vocabulário permitido; criação de tag nova é decisão editorial.

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

- Raffa aprova decisões de vocabulário v0 e mudanças de regra.
- Agente pode propor tags com racional, exemplos e rejeições, mas não promover vocabulário novo sozinho.
- Ao final desta fase, as regras aprovadas devem virar skill local de tagging editorial quando isso for explicitamente solicitado.

## Exemplos do ciclo manual

| Livro | Tags aprovadas | Aprendizado |
|---|---|---|
| `Making Games with Python & Pygame` | `Python`, `Desenvolvimento de Jogos`, `Prático` | Biblioteca específica (`Pygame`) não precisa virar tag se a intenção pública melhor é jogos em Python. |
| `Kubernetes for Full-Stack Developers` | `Kubernetes`, `Docker`, `DevOps` | Tags de stack podem ser mais úteis que categoria; `Cloud Native` ficou vago demais. |
| `An Introduction to Statistical Learning` | `Machine Learning`, `Estatística`, `R` | `Data Science` era mais genérico que a intenção real. |
| `Microservices AntiPatterns and Pitfalls` | `Microsserviços`, `Arquitetura`, `Prático` | Livro de arquitetura pode precisar de uso editorial quando funciona como checklist/revisão de design. |
| `The Art of High Performance Computing - Volume 1` | `Computação de Alto Desempenho`, `Arquitetura de Computadores`, `Métodos Numéricos` | Livro ambíguo em `Tecnologia > Geral` pode ficar descobrível com tags sem depender de recategorizar tudo. |

## Decisões explícitas

- `Nível` fica fora das tags visíveis na v1. Será campo separado ou metadado próprio nas tarefas 3 e 7.
- `Acadêmico` sai do vocabulário: é alegação editorial fraca para clique.
- `Boas Práticas` sai do vocabulário: vira etiqueta genérica fácil de abusar.
- `Prático` fica porque comunica uma forma de uso clara quando o livro é projeto, laboratório, checklist ou guia operacional.
