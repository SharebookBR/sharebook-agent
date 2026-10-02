# Tarefa 1 — Resultado do ciclo manual (rascunho para revisão)

> **Status:** rascunho de agente, aguardando julgamento editorial humano (Raffa/Josué). Nada aqui foi publicado ou aplicado ao catálogo.
> **Data:** 2026-10-02. **Fonte dos dados:** API pública (`Book/Slug/{slug}`, `Book/CategoryTree/...`). Sinopses e categorias lidas do catálogo em produção.
> **Limite do método:** o julgamento foi feito pelo agente a partir de título, autor, categoria e sinopse (as sinopses lidas estavam truncadas em ~400 caracteres, exceto a do HPC Vol. 1). Nenhum livro foi aberto. É uma proposta, não um veredito.

## Achado de contexto: a categoria técnica atual é ruidosa

Catálogo de Tecnologia no momento da leitura: **324 ebooks**. Amostra dos 100 primeiros: Geral 25, IA 20, Backend 20, DevOps 14, Dados 10, Frontend 8, Cloud 3.

Exemplos de descompasso entre categoria e conteúdo (todos dentro dessa amostra de 100):

| Categoria atual | Livros que moram nela | Problema |
|---|---|---|
| **DevOps** | Think OS, Little Book of Semaphores, Project Oberon, Joy of Cryptography, Gray Hat Hacking | Sistemas operacionais, criptografia e segurança ofensiva não são DevOps |
| **Frontend** | Learn OpenGL, Ray Tracing Gems, Virtual Reality, Making Games with Python & Pygame | Computação gráfica e games não são frontend web |
| **Backend** | Git internals, Emacs, GCC, Subversion, Open Data Structures | Ferramentas e estruturas de dados, não backend |
| **Geral** | Álgebra, Cálculo, Combinatória, CSP, Z, teoria da computação | Matemática e fundamentos acumulados num balde sem nome |
| **IA** | 5 livros de computação quântica, 2 de prompts (texto e imagem) | Quântica não é IA |

Leitura: a categoria parece funcionar como "onde coube", não como intenção de busca. Isso reforça a tese do épico (tag como eixo transversal) e sugere que parte do valor das tags é **compensar categorização histórica**, não só enriquecer descoberta. Hipótese a confirmar com os 324 livros.

## Registro por livro

### 1. Linguagem/framework — Making Games with Python & Pygame (Al Sweigart)
```text
Categoria atual: Tecnologia > Frontend
Tags escolhidas: Python · Desenvolvimento de Jogos · Prático
Alternativas rejeitadas: Pygame (fino demais, vira tag de 1 livro), Iniciante (nível, ver decisão abaixo), Frontend (a categoria atual induz ao erro)
Dimensões cobertas: stack (Python), área/problema (jogos), uso editorial (prático)
Valor esperado: dev Python que quer projeto concreto acha o livro; hoje ele está escondido em "Frontend"
Dúvidas editoriais: "Desenvolvimento de Jogos" cobre Pygame, OpenGL e Unity patterns? Ou separar de "Computação Gráfica"?
```

### 2. Infra/cloud/DevOps — Kubernetes for Full-Stack Developers
```text
Categoria atual: Tecnologia > Cloud
Tags escolhidas: Kubernetes · Docker · DevOps
Alternativas rejeitadas: Helm (específico demais), Cloud Native (vago), Prático (a sinopse é prática, mas todo livro de infra é)
Dimensões cobertas: stack (2), área (1)
Valor esperado: alto, pois Kubernetes/Docker são buscas diretas de dev/tech lead. Controle positivo: categoria e tags concordam
Dúvidas editoriais: Docker e Kubernetes como duas tags ou uma "Contêineres"? Busca real é pelo nome da ferramenta
```

### 3. Dados/IA/estatística — An Introduction to Statistical Learning (James, Witten, Hastie, Tibshirani)
```text
Categoria atual: Tecnologia > Dados
Tags escolhidas: Machine Learning · Estatística · R
Alternativas rejeitadas: Data Science (genérico, já é categoria "Dados"), Acadêmico (uso editorial; livro é didático mas usado na prática), Regressão (tópico, não eixo)
Dimensões cobertas: área (2), stack (1)
Valor esperado: alto, porque ML + estatística separa este livro de "IA" generativa e de deep learning
Dúvidas editoriais: a edição com Python (ISLP) é outro livro? Se existir, "R" vira diferencial real
```

### 4. Arquitetura/práticas — Microservices AntiPatterns and Pitfalls (Mark Richards)
```text
Categoria atual: Tecnologia > Backend
Tags escolhidas: Microsserviços · Arquitetura · Boas Práticas
Alternativas rejeitadas: Backend (é a categoria), Avançado (nível), Antipadrões (ótimo mas só 1 livro)
Dimensões cobertas: área (2), uso editorial (1)
Valor esperado: alto para tech lead; "Arquitetura" é exatamente a intenção citada no épico
Dúvidas editoriais: "Boas Práticas" é tag fraca? O livro é sobre o que NÃO fazer. Talvez "Referência" ou nenhuma terceira tag
```

### 5. Ambíguo — The Art of High Performance Computing, Vol. 1 (Victor Eijkhout)
```text
Categoria atual: Tecnologia > Geral
Tags escolhidas: Computação de Alto Desempenho · Arquitetura de Computadores · Métodos Numéricos
Alternativas rejeitadas: Redes Neurais (um capítulo de aplicação), Python/C (não ensina linguagem), Acadêmico (uso editorial, teste pendente)
Dimensões cobertas: área/problema (3), nenhuma de stack
Valor esperado: alto para quem busca HPC; hoje invisível em "Geral"
Dúvidas editoriais: série com 3 volumes: Vol. 2 (paralela) e Vol. 3 (programação científica). Tags idênticas nos 3 ou específicas?
```

## Vocabulário v0 proposto

**15 tags usadas nos 5 livros:**

- **Stack:** Python · R · Docker · Kubernetes
- **Área/problema:** Machine Learning · Estatística · Microsserviços · Arquitetura · DevOps · Computação de Alto Desempenho · Arquitetura de Computadores · Métodos Numéricos · Desenvolvimento de Jogos
- **Uso editorial:** Prático · Boas Práticas

**+9 sugeridas pelos descompassos de categoria (não testadas em nenhum livro):** Sistemas Operacionais · Criptografia · Segurança · Computação Gráfica · Controle de Versão (Git) · Computação Quântica · Matemática Discreta · Teoria da Computação · Estruturas de Dados.

## Decisões propostas

**Nível (Iniciante/Intermediário/Avançado): campo separado, fora das tags visíveis na v1.**
Evidência fraca: em 2 dos 5 livros (Pygame, Microservices) considerei uma tag de nível, e em ambos ela competiria com tags de área/stack por uma das 3 vagas. Nível responde "serve para mim?", não "o que é isso?". Proposta: metadado próprio, testado na PDP depois. Amostra pequena; reavaliar na tarefa 7.

**Uso editorial: manter só `Prático` e `Referência` como candidatas.** `Acadêmico` e `Boas Práticas` ficaram ambíguos. `Fundamentos` e `Legado` não foram testados.

**Limite de até 3 tags:** não há evidência suficiente para confirmar. O único sinal é que em um livro (Microservices) a terceira tag ficou duvidosa, o que sugere "até 3" em vez de "exatamente 3".

## Vitrines por tag (candidatas, a validar com os 324 livros)

- **Computação de Alto Desempenho:** os 3 volumes da série Eijkhout (Vols. 2 e 3 aparecem como recomendados do Vol. 1), possivelmente mais livros de Geral/DevOps sobre arquitetura e SO.
- **Machine Learning + Estatística:** ISLR, Think Stats, Bayesian Reasoning, Probabilistic Programming. Distingue ML clássico do deep learning.
- **Sistemas Operacionais:** Think OS, Operating Systems From 0 to 1, Project Oberon, Dive into Systems, Be File System. Hoje espalhados em DevOps.
- **Docker + Kubernetes:** poucos livros (3 em Cloud, nem todos sobre o tema), mas buscas de alta intenção.
- **Computação Quântica:** 5 livros hoje em "IA".

## Fricções e regras aprendidas (insumo da futura skill de tagging)

1. A categoria atual parece não ser evidência de conteúdo. Tagar pela sinopse, não pela categoria.
2. Tag que só serve para 1 livro é tópico, não tag (ex.: Pygame, Helm).
3. Nome da ferramenta (Docker, Kubernetes, Python) vence termo guarda-chuva (Cloud Native, Data Science) quando a busca real é pelo nome. Hipótese, sem dado de busca.
4. Séries devem ter tags consistentes entre volumes; decidir se há exceção por volume.
5. A API de listagem (`CategoryTree`) devolve `category` e `categoryInfo` nulos, só `categoryId`. Para o importer (tarefa 5) isso importa: resolver nome pelo ID da árvore.

## Pendências para fechar a Tarefa 1

- [ ] Revisão humana das 15 tags e das rejeições.
- [ ] Decisão do Raffa/Josué sobre nível (campo separado) e sobre `Acadêmico`.
- [ ] Ler as sinopses completas e validar vitrines contra a base completa (324 livros, só 100 lidos).
- [ ] Só depois: Tarefa 2 (vocabulário v0 e governança).
