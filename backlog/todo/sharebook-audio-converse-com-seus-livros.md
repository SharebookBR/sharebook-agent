# Sharebook Audio — Converse com seus livros

> **Status:** Discovery / Backlog
>
> **Valor potencial:** altíssimo
>
> **Esforço e risco:** muito altos
>
> **Restrição de produto:** a solução precisa ser lucrativa ou, no mínimo, economicamente sustentável.

## Visão

Transformar livros de conteúdo passivo em experiências interativas de aprendizado por áudio.

A proposta não é simplesmente gerar audiobooks ou resumos narrados. É permitir que a pessoa conheça, aprenda e interaja com um livro por áudio, mantendo contexto, progresso e continuidade.

```text
Livro original
12 horas de leitura

        ↓

Sharebook Audio
~45–90 minutos
```

O áudio condensado deve preservar:

- as principais ideias;
- a progressão conceitual;
- exemplos relevantes;
- o contexto necessário;
- as conclusões do autor.

O objetivo não é necessariamente substituir a leitura integral. É permitir que a pessoa conheça a obra profundamente o suficiente para aprender com ela e decidir se deseja explorar o original.

## Problema

Existem três sinais principais:

1. Muitas pessoas não têm tempo disponível para ler livros.
2. Existe tempo durante deslocamentos e outras atividades nas quais áudio é uma interface adequada.
3. O Sharebook possui livros técnicos e educacionais que despertam interesse mesmo quando o usuário não consegue dedicar horas à leitura tradicional.

## Hipótese central

Não construir apenas:

> Audiobooks resumidos por IA.

Explorar:

> Livros interativos que você pode ler, ouvir e conversar.

## A experiência diferenciadora

```text
🎧 usuário ouvindo
        ↓
⏸️ pausa
        ↓
💬 conversa com o agente
        ↓
🧠 explicação contextual
        ↓
▶️ continua exatamente de onde parou
```

O agente precisa conhecer mais do que o texto do livro:

```text
Livro
+
posição atual
+
conteúdo já consumido
+
dúvidas anteriores
+
conhecimento do usuário
```

Isso transforma um chatbot sobre documentos em um companheiro de leitura e aprendizado.

## MVP conceitual

Validar primeiro o loop principal:

```text
PLAY
 ↓
PAUSE
 ↓
ASK
 ↓
CONTEXTUAL ANSWER
 ↓
RESUME
```

Se esse loop for bom, existe produto. Evitar transformar a primeira versão em uma plataforma enorme antes dessa prova.

### Papel do agente no MVP

O agente mínimo é parte do MVP de `Converse com seu livro`. Ele precisa:

- compreender a pergunta;
- conhecer o livro e a posição atual;
- recuperar apenas o contexto relevante;
- respeitar o limite de spoilers;
- responder de forma adequada ao momento da leitura;
- devolver o controle ao player para a retomada.

O MVP **não depende** de um agente geral do Sharebook, WhatsApp, memória transversal sofisticada ou um MCP com todas as capacidades do produto. Construir essa plataforma antes de provar o loop principal criaria custo e abstração sem evidência de valor.

A evolução omnichannel, a memória transversal e as ações autenticadas pertencem ao épico separado [Agente Sharebook — companheiro de leitura e jornadas](agente-sharebook/index.md).

A relação entre os épicos é:

```text
Converse com seu livro
        ↓
prova o valor do agente
        ↓
Agente Sharebook amplia memória, ferramentas e canais
```

Uma prova de conceito do Audio pode simular identidade e sessão. Um MVP publicado deve consumir o contrato mínimo de identidade autenticada e contexto definido pelo épico do Agente Sharebook, sem depender das demais tarefas dele.

## Arquitetura conceitual

```text
                ┌──────────────────────┐
                │      Sharebook       │
                │ catálogo / usuário   │
                └──────────┬───────────┘
                           │
                    request audio
                           │
                ┌──────────▼───────────┐
                │  Audio Orchestrator  │
                │ estado + jobs + SLA  │
                └──────┬────────┬──────┘
                       │        │
              ingest   │        │ publish
                       │        │
          ┌────────────▼───┐  ┌▼──────────────┐
          │ Content Brain  │  │ Audio Pipeline │
          │ parse + RAG    │  │ script + TTS  │
          └──────┬─────────┘  └──────┬────────┘
                 │                   │
                 └─────────┬─────────┘
                           │
                    ┌──────▼──────┐
                    │ Session API │
                    │ player + AI │
                    └──────┬──────┘
                           │
            ┌──────────────▼──────────────┐
            │ Interactive Reading Agent  │
            │ RAG + position + memory    │
            └─────────────────────────────┘
```

O agente vive na interseção de três dimensões:

- **Book Knowledge:** o que este livro ensina?
- **Audio Timeline:** onde o usuário está?
- **User Learning Context:** o que esse usuário já sabe e como aprende, quando essa capacidade estiver disponível pelo Agente Sharebook?

### Content Brain

Cada livro deve ter uma representação semântica reutilizada pelo pipeline de áudio e pelo agente. Não depender apenas de chunks arbitrários.

Possíveis componentes:

- capítulos e seções;
- chunks semânticos;
- embeddings;
- conceitos, entidades e relações;
- pré-requisitos conceituais;
- opcionalmente, um knowledge graph.

Exemplo conceitual:

```json
{
  "bookId": "ddia",
  "chapter": 5,
  "section": "Replication Lag",
  "concepts": ["eventual consistency", "read-after-write"],
  "sourceRange": "...",
  "prerequisites": ["replication"],
  "introducedAfter": ["leader-follower replication"]
}
```

### Audio Timeline

Evitar gerar apenas um arquivo monolítico. Produzir segmentos semanticamente endereçáveis:

```text
Book
 └── Episode
      ├── Segment 001
      ├── Segment 002
      ├── Segment 003
      └── ...
```

Cada segmento pode relacionar `audioSegmentId`, livro, capítulo, conceitos, chunks-fonte, duração, transcrição e URL. Assim, posição do player, conceito e fonte original permanecem conectados.

### Session Context

Quando ocorre uma pergunta, o agente não deve receber apenas `question + vectorSearch(book)`. O contexto deve incluir usuário, livro, capítulo e segmento atuais, timestamp, transcrição corrente, conceitos já ouvidos, perguntas anteriores e memórias relevantes.

### Knowledge Boundary

O sistema deve saber até onde o usuário consumiu o livro:

```text
heardUntil = chapter 5 / segment 38
retrieval_scope <= heardUntil
```

Se a resposta depender de conteúdo futuro, o agente deve pedir permissão antes de antecipá-lo. Evitar spoilers intelectuais precisa ser uma propriedade arquitetural, não apenas uma instrução de prompt.

## Estado necessário para a experiência

O Sharebook Audio possui apenas o estado diretamente ligado à experiência do livro:

1. **Session Context:** contexto da conversa atual.
2. **Book Progress:** posição ouvida e limite de conhecimento alcançado.
3. **Book Context:** dúvidas, bookmarks e comentários necessários para retomar aquela obra.

Memória durável entre livros, preferências transversais de aprendizado, avaliação de candidatos a memória e controles de inspeção ou exclusão pertencem à [Tarefa 4 — Memória durável e controlável](agente-sharebook/tarefa04-memoria-duravel.md) do épico Agente Sharebook.

O Audio pode consumir essa memória quando ela existir, mas não deve criar um segundo sistema de memória.

## Pipeline de geração

Pipeline assíncrono, idempotente e retomável por estágio:

```text
REQUESTED
    ↓
INGESTING
    ↓
UNDERSTANDING
    ↓
SCRIPTING
    ↓
REVIEWING
    ↓
SYNTHESIZING
    ↓
PUBLISHING
    ↓
READY
```

Se o TTS falhar no segmento 47 de 63, reprocessar apenas esse segmento.

## Geração on-demand

Não é necessário processar todo o catálogo previamente.

```text
🎧 Ouvir este livro

Este livro ainda não possui uma versão em áudio.

[ Preparar para mim ]
```

Estratégia híbrida:

- **Hot catalog:** pré-processamento.
- **Long tail:** processamento sob demanda.

Ambos usam o mesmo pipeline; muda apenas quem dispara o processamento. Pedidos concorrentes para o mesmo livro devem compartilhar o mesmo job, por exemplo com `UNIQUE(bookId, audioProfile)`.

## Player + conversa

Separar reprodução e conversa. O cliente reproduz o áudio publicado em CDN e alterna para a interação de voz com o agente quando necessário.

```text
PLAYING
   ↓
PAUSED_FOR_CONVERSATION
   ↓
PLAYING
```

O backend não precisa misturar dinamicamente audiobook e conversa em um único stream.

## UX voice-first

Considerar desde o início situações nas quais a pessoa não pode ou não quer usar a tela:

```text
🎧 audiobook

"Sharebook, pausa."

💬 conversa por voz

"Entendi. Continua."

🎧 audiobook
```

Comandos futuros possíveis: explicar novamente, dar outro exemplo, comparar com outro conceito, marcar um trecho, testar entendimento, resumir a sessão, continuar e voltar.

## Research / benchmark obrigatório

Antes de desenhar definitivamente a experiência, usar por aproximadamente um mês:

1. NotebookLM — áudio interativo e conversa com fontes.
2. Spotify — experiência de áudio e funcionalidades conversacionais.
3. Audible — experiência madura de audiobook.
4. Blinkist — compressão de livros e aprendizado rápido.

Observar discovery, onboarding, escolha do livro, início e retomada da reprodução, capítulos, velocidade, bookmarks, interrupções, perguntas, conclusão, recomendações, retenção e experiência durante deslocamentos.

**Não desenhar a solução final antes dessa etapa.**

## Estratégia de catálogo

### V1 — Open Knowledge

Começar por obras que possam legalmente ser processadas e distribuídas dessa forma. Usar essa fase para validar produto, consumo, conclusão, interação, custo e qualidade do pipeline.

### V2 — Licensed Knowledge

Com dados reais, buscar acordos com autores e editoras para obras fechadas. O Sharebook pode funcionar também como canal de descoberta para as obras completas.

## Sustentabilidade econômica

A sustentabilidade econômica é uma restrição arquitetural e de produto, não uma preocupação posterior.

Custos marginais relevantes:

- LLM e inferência;
- TTS e STT;
- interação em tempo real;
- embeddings e retrieval;
- armazenamento, CDN e tráfego;
- processamento editorial;
- futuramente, royalties e licenciamento.

Princípio econômico:

```text
Receita por usuário
        >
custo variável por usuário
+
parcela dos custos fixos
```

O conteúdo processado é um ativo reutilizável: roteiro, QA e TTS podem ser pagos uma vez e amortizados por milhares de consumidores. A interação personalizada permanece como custo marginal por usuário.

Desde o MVP, explorar cache agressivo, geração única de áudio, processamento sob demanda, deduplicação de jobs, reuso de artefatos, escolha de modelos conforme complexidade, quotas de interação e monitoramento por usuário e por livro.

## Hipótese de monetização

Não definir preço antes de entender custo e valor percebido. Uma hipótese é preservar o Sharebook tradicional gratuito e, futuramente, oferecer uma camada premium com áudio, conversa, memória de aprendizado e jornada de conhecimento.

Preço deve ser consequência de unit economics e disposição a pagar, não uma premissa arbitrária.

## Métricas obrigatórias

### Unit economics

- custo de produção por livro;
- custo médio de TTS por minuto publicado;
- custo médio de interação por minuto;
- custo por usuário ativo e pagante;
- custo de livros nunca consumidos;
- percentual de produção reutilizada;
- margem bruta por usuário;
- receita média por usuário;
- LTV, churn e, quando aplicável, LTV/CAC.

Duas métricas centrais:

```text
cost_per_completed_book
```

```text
total product cost
        ÷
completed learning hours
        =
cost_per_learning_hour
```

### Produto

- minutos ouvidos e percentual concluído;
- sessões e retomadas por livro;
- livros iniciados e concluídos;
- perguntas por hora ouvida;
- sessões com conversa;
- momento e duração das perguntas;
- taxa de retorno ao áudio após a conversa.

A sequência `conversation → resume audio` é especialmente importante: indica se a interação ajuda o aprendizado em vez de apenas interrompê-lo.

## Critério de sucesso

Precisamos provar simultaneamente:

```text
DESEJABILIDADE
Usuários querem usar?
        +
QUALIDADE
Eles realmente aprendem?
        +
RETENÇÃO
Eles voltam?
        +
ECONOMIA
O uso é sustentável?
```

Crescimento sem sustentabilidade econômica não é considerado sucesso.

## Próximo passo quando priorizado

Executar o benchmark de aproximadamente um mês e produzir, ao final:

1. diário estruturado das experiências;
2. recorte jurídico seguro para o catálogo inicial;
3. protótipo do loop `PLAY → PAUSE → ASK → RESUME`;
4. orçamento preliminar por livro e por hora de aprendizado;
5. critérios objetivos de go/no-go para o MVP.
