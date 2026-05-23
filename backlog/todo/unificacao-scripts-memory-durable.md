# Unificação de Scripts e Renomeação do Corpus

## Problema

O `sharebook-agent` tem conhecimento operacional espalhado em dois lugares com lógicas diferentes: `skills/` (markdown) e `scripts/` (executáveis). A separação cria custo cognitivo sem benefício real — dois lugares para procurar a mesma coisa, nomes que não comunicam o que cada coisa é.

## Proposta

### 1. Renomear para explicitar a simetria

- `skills/` → `memory-durable/`
- `memory/` → `memory-episodic/`

A nomenclatura torna explícito que são dois tipos de memória do mesmo organismo, alinhado com a doutrina do DREAM.

### 2. Scripts viram artefatos subordinados a uma knowledge

Scripts deixam de ser entidades de primeiro nível. Eles continuam existindo como executáveis — markdown não substitui executável quando o critério é baixo esforço de execução — mas passam a morar dentro de `memory-durable/` como artefatos de uma knowledge.

A knowledge define quando e como o script deve ser usado. Você nunca procura o script diretamente — você procura a knowledge, e ela te diz que tem um script e como executá-lo.

A seção de Scripts no `AGENTS.md` some. O routing cobre tudo.

### 3. Source of truth semântica única

Uma única pergunta: "qual memory-durable resolve X?"

## Custo real

- Renomear `memory/` para `memory-episodic/` exige atualizar todas as referências em `AGENTS.md`, `DREAM.md` e rituais.
- Cada script atual precisa ser avaliado: qual knowledge o absorve, ou precisa de knowledge nova?

## Decisão pendente

A renomeação de `memory/` para `memory-episodic/` vale o custo de migração, ou mantemos `memory/` como está e só renomeamos `skills/`?
