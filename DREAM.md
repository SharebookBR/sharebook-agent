# DREAM.md — Ecologia de Conhecimento e Plasticidade

Este arquivo registra a doutrina de evolução cognitiva do Sharebook-agent.
Ele não descreve apenas um ritual. Ele descreve como o agente cultiva, reorganiza e poda o próprio conhecimento ao longo do tempo.

---

## 🧠 Tese central

O Sharebook-agent não trata memória durável como arquivo estático.

**Memória episódica** vive em `memory/YYYY-MM-DD.md`.
**Memória durável** vive primariamente em `skills/`.

Se um aprendizado recorrente muda comportamento, reduz retrabalho, melhora julgamento ou endurece execução, ele deve preferencialmente virar ou modificar uma **Skill**.

O Dream existe para manter essa arquitetura viva, coerente e saudável.

---

## 🧬 O organismo de conhecimento

Nossa arquitetura se comporta mais como um organismo do que como um repositório.

### 1. Hipocampo — Memória episódica
As memórias diárias (`memory/YYYY-MM-DD.md`) registram a experiência bruta:
- fricção
- erro de ambiente
- decisão local
- acerto operacional
- contexto da sessão

É memória de alta fidelidade e baixa abstração.

### 2. Neocórtex — Skills
As **Skills** são a forma primária de memória durável.
Elas não são apenas instruções. Elas são:
- aprendizado consolidado
- heurística reutilizável
- cicatriz transformada em procedimento
- conhecimento acionável

Uma memória durável que não muda comportamento operacional tende a ser ruído.

### 3. Dream — Plasticidade
O Dream é o mecanismo de plasticidade do sistema.
Sua função não é só promover memória. É:
- consolidar
- endurecer
- reorganizar
- especializar
- fundir
- podar
- esquecer

O objetivo não é acumular mais conhecimento. É manter um **corpus vivo, útil e bem recortado**.

---

## 🏛️ Princípios de sabedoria

### Consistência > performance
Preferimos um sistema que aprende de forma estável a um sistema que improvisa rápido e esquece o que importa.

### Fricção é sensor
Fricção recorrente não é azar. É evidência de que a arquitetura ainda não absorveu a lição.

### Skill é memória viva
Se um aprendizado merece durar, ele deve preferencialmente viver em uma Skill, não em um depósito genérico.

### Acúmulo sem poda degrada
Lembrar de tudo é uma forma de burrice. Sem esquecimento seletivo, o sistema perde nitidez.

### Organização por uso real
Conhecimento não deve ser organizado por estética ou apego histórico, mas por uso real, co-ativação, impacto e recorrência.

---

## 🌳 Famílias de Skills

Skills não são apenas unidades isoladas. Elas pertencem a **famílias**.

Famílias são domínios vivos de conhecimento, por exemplo:
- runtime
- importer
- editorial
- analytics
- identity
- user-model
- doctrine
- infra

A família ajuda a decidir:
- onde um aprendizado deve morar
- quando uma skill deve ser dividida
- quando duas skills devem ser fundidas
- quando uma região do conhecimento está inchada, órfã ou mal recortada

O Dream deve pensar em arquitetura de famílias, não apenas em arquivos soltos.

---

## 🔁 Rastro de uso como evidência

Toda memória episódica deve registrar **skills acionadas**.

Esse rastro é uma fonte de verdade para plasticidade.
Com ele, o Dream pode observar:
- frequência de uso
- co-ativação entre skills
- skills centrais vs periféricas
- regiões do corpus que viraram entulho
- oportunidades de split, merge, promotion ou arquivamento

Sem rastro de uso, reorganização vira opinião.
Com rastro de uso, reorganização vira governança por evidência.

---

## ⏳ Esquecimento seletivo

Esquecimento não é falha. É função vital.

Se Skills são a memória durável primária, então o sistema precisa saber:
- o que manter como núcleo
- o que endurecer
- o que especializar
- o que fundir
- o que aposentar
- o que arquivar

Sem isso, trocamos um `MEMORY.md` monolítico por um cemitério de Skills.

### Sinais de esquecimento ou reorganização
- skill pouco usada e sem valor estrutural
- skill redundante com outra mais viva
- skill ampla demais e difusa
- skill órfã sem família clara
- skill cujo conteúdo já foi absorvido por uma estrutura melhor

### Estados possíveis
Esses estados não precisam ser implementados formalmente de imediato, mas a arquitetura deve pensar neles:
- `core`
- `active`
- `stable`
- `dormant`
- `archived`
- `superseded`

---

## 🛠️ O que o Dream faz na prática

O Dream é o ritual periódico de governança do organismo de conhecimento.

### Funções principais
1. Ler memórias episódicas recentes.
2. Identificar padrões de fricção e recorrência.
3. Promover aprendizado para Skills existentes.
4. Criar nova Skill quando não houver “balde” adequado.
5. Dividir Skills grandes demais.
6. Fundir Skills redundantes ou concorrentes.
7. Reorganizar Skills por família e uso real.
8. Arquivar ou podar conhecimento degradado.

### Pergunta central do Dream
O Dream não deve perguntar apenas:
- “isso vai para memória durável?”

Ele deve perguntar:
- isso endurece qual Skill?
- isso merece criar uma nova Skill?
- isso revela uma família mal organizada?
- isso pede split ou merge?
- isso ainda merece existir?

---

## 🎯 Mandato do Sonhador

O Agente Sonhador não é um secretário de memória. Ele é um jardineiro da arquitetura cognitiva.

Ele tem mandato para:
1. **Criar Skills** quando houver um cluster recorrente sem destino adequado.
2. **Dividir Skills** quando uma skill perder coesão.
3. **Fundir Skills** quando duas competirem pelo mesmo território.
4. **Reorganizar famílias** quando a arquitetura atual deixar de refletir o uso real.
5. **Podar conhecimento** quando o corpus começar a degradar.

### Guardrails
- Toda nova Skill deve ser indexada.
- Skill com uso recorrente, transversal e validado por rastro de uso pode ser promovida para índices de nível mais alto quando isso reduzir fricção de descoberta.
- Não promover Skill por entusiasmo local, sessão isolada ou impressão subjetiva de importância.
- Toda mudança estrutural relevante deve ser explicada na memória episódica do ciclo.
- Não criar skill para migalha isolada.
- Não manter skill viva por apego histórico.
- Não arquivar conhecimento crítico só porque foi pouco usado recentemente.

---

## 🧭 Procedimento do Dream

### Quando executar
- A cada 7 dias, ou
- após marcos grandes, ou
- quando o corpus mostrar sinais de inchaço, redundância ou desorganização

### Como executar
1. Ler este `DREAM.md` para realinhar com a doutrina.
2. Ler memórias desde o último checkpoint.
3. Observar as **skills acionadas** e o padrão de uso.
4. Identificar fricções recorrentes, lacunas e redundâncias.
5. Atualizar, criar, dividir, fundir ou arquivar Skills conforme necessário.
6. Registrar na memória episódica o que foi alterado e por quê.
7. Atualizar o checkpoint do ciclo.

---

## 🧨 Anti-padrões

- Tratar `MEMORY.md` monolítico como destino principal de conhecimento durável.
- Acumular Skills sem poda.
- Criar Skill demais para ruído local.
- Organizar conhecimento por estética em vez de uso.
- Confundir apego histórico com valor estrutural.
- Fazer Dream como mera promoção burocrática de nota para arquivo.

---

## 🪶 Fórmula curta

Se precisar resumir toda a doutrina em poucas linhas:

- **Skills são a memória durável primária.**
- **Dream é o mecanismo de plasticidade.**
- **Famílias organizam o corpus.**
- **Uso real governa reorganização.**
- **Esquecimento seletivo é obrigatório.**

---

## Como usar este arquivo

- **Agentes comuns**: entendam que conhecimento durável não vive primariamente em um arquivo genérico, e sim em Skills acionáveis.
- **Agente Sonhador**: use este arquivo como constituição para consolidar, reorganizar e podar o corpus.
- **Arquitetura futura**: qualquer integração com sistemas nativos de dreaming deve preservar esta doutrina, não achatá-la em promoção genérica de memória.
