# Épico — Agente Sharebook: companheiro de leitura e jornadas

## Estado

- **Status:** discovery / backlog
- **Prioridade:** 12 no backlog principal
- **Valor potencial:** altíssimo
- **Esforço e risco:** muito altos
- **Primeiro caso de uso especializado:** Sharebook Audio
- **Próxima tarefa:** [Tarefa 1 — Núcleo e identidade autenticada](tarefa01-nucleo-identidade-autenticada.md), quando o épico for priorizado

## Visão

Transformar o Sharebook de um conjunto de telas que o usuário navega em um companheiro que entende sua intenção, conhece sua jornada e o ajuda a descobrir, ler, aprender, doar e solicitar livros.

```text
Memória         → quem é o usuário e como ele aprende
RAG             → o que os livros dizem
MCP Sharebook   → o que o agente pode consultar e fazer
Canais          → onde a interação acontece
```

O agente deve ter um núcleo independente do canal:

```text
                    Agente Sharebook
       identidade + contexto + memória + capacidades
                            │
          ┌─────────────────┼──────────────────┐
          ▼                 ▼                  ▼
     Áudio interativo   Chat no app         WhatsApp
```

## Tese de produto

O catálogo é o conhecimento. O MCP dá mãos ao agente. A memória dá continuidade. Os canais dão presença.

O objetivo não é espalhar um chatbot genérico. Cada canal deve resolver jornadas adequadas à sua natureza, usando a mesma identidade e a mesma fonte de verdade.

## Tarefas

| # | Tarefa | Status | Depende de | Resultado |
|---|---|---|---|---|
| 1 | [Núcleo e identidade autenticada](tarefa01-nucleo-identidade-autenticada.md) | **Pendente** | — | Contexto seguro e independente de canal para um usuário autenticado. |
| 2 | [MCP read-only do Sharebook](tarefa02-mcp-read-only.md) | **Pendente** | 1 | Agente consulta catálogo e jornadas reais pelas capacidades oficiais. |
| 3 | [Chat no app](tarefa03-chat-no-app.md) | **Pendente** | 1–2 | Primeira interface conversacional geral dentro do ambiente autenticado. |
| 4 | [Memória durável e controlável](tarefa04-memoria-duravel.md) | **Pendente** | 1 + evidência de retorno | Continuidade útil sem acumulação indiscriminada ou memória invisível. |
| 5 | [Jornadas de leitura e aprendizado](tarefa05-jornadas-leitura-aprendizado.md) | **Pendente** | 2–4 | Objetivos viram percursos acompanháveis, não respostas isoladas. |
| 6 | [Ações via MCP com confirmação](tarefa06-acoes-mcp-confirmacao.md) | **Pendente** | 2 + confiança operacional | Agente executa mutações auditáveis sem retirar controle do usuário. |
| 7 | [Canal WhatsApp](tarefa07-canal-whatsapp.md) | **Horizonte v2** | 1–5 + jornada comprovada | Continuidade fora do app com identidade vinculada e custo controlado. |
| 8 | [Outros canais](tarefa08-outros-canais.md) | **Horizonte** | evidência específica | Novos canais entram por trabalho real, não por presença ornamental. |

## Fronteira com Sharebook Audio

São épicos irmãos:

- **Sharebook Audio** possui ingestão, Content Brain, roteiro, TTS, timeline, player, posição atual e limite de spoilers.
- **Agente Sharebook** possui identidade transversal, memória durável, capacidades MCP, jornadas e adaptadores de canal.

Uma prova de conceito do Audio pode simular identidade e sessão. Um MVP publicado do Audio depende apenas do contrato mínimo da tarefa 1, não da conclusão deste épico.

O Audio é o primeiro grande laboratório do agente, mas não é seu contêiner arquitetural.

## Princípios

- identidade e memória pertencem ao usuário, não ao canal;
- memória não concede permissão;
- MCP chama capacidades oficiais, nunca acessa banco diretamente;
- token e escopos sempre representam o usuário autenticado;
- leitura segura pode ser automática; mutação relevante exige confirmação;
- ações são auditáveis e idempotentes;
- o usuário pode inspecionar, corrigir e apagar suas memórias;
- nenhum canal ganha comportamento novo sem jornada e métrica próprias;
- autonomia cresce apenas depois de confiança observável.

## Métricas do épico

- conversas que terminam em uma ação ou descoberta útil;
- retorno do usuário à mesma jornada;
- livros descobertos, iniciados e concluídos com ajuda do agente;
- aceitação e rejeição de recomendações;
- correções e exclusões de memória;
- taxa de confirmação e cancelamento de ações propostas;
- custo por conversa útil e por jornada concluída;
- retenção incremental por usuário exposto ao agente.

## Fora de escopo agora

- assistente administrativo ou acesso privilegiado;
- agente autônomo que realiza mutações sem confirmação;
- memória integral de todas as conversas;
- MCP conectado diretamente ao banco;
- replicar a mesma UI conversacional em todos os canais;
- WhatsApp antes de existir jornada recorrente comprovada no app;
- construir toda a plataforma antes de validar uma fatia vertical.

## Critério para sair de discovery

Escolher uma jornada concreta, demonstrar que o agente a melhora em relação à navegação tradicional, estimar custo por conversa útil e provar que identidade, autorização e memória podem ser tratadas sem ambiguidade.
