# Pegasus — Engagement Engine

## Objetivo

A Pegasus é uma **Engagement Engine** event-driven e app-agnóstica. Não é biblioteca de gamificação — é uma camada de incentivo a comportamentos desejados, reutilizável entre aplicações.

---

## Restrições

- **Orçamento:** zero
- **Time:** colaboração esporádica de devs + agente (eu) ocasionalmente
- **Horizonte:** 1 ano

---

## Arquitetura

A Pegasus não conhece domínio de aplicação. Conhece apenas **eventos**:

```
App → POST /events { type, userId, payload } → Pegasus → pontos + histórico
```

Eventos exemplo:
- `UserRegistered`
- `BookDownloaded`
- `BookDonated`
- `ReviewSubmitted`

Cada app decide o que emitir. A Pegasus só processa, pontua e registra.

---

## Ano 1 — Escopo realista

### Pegasus (serviço)

| Entrega | Descrição |
|---|---|
| **Engine de eventos** | Endpoint REST para ingestão. App emite, Pegasus processa. |
| **Sistema de pontos** | Ledger simples: `user_id`, `point_type` (XP/Karma), `balance`. Transações imutáveis. |
| **Regras configuráveis** | JSON ou DB: "quando `BookDownloaded`, +10 XP". Sem UI — config via arquivo ou migration. |
| **Histórico de atividades** | Timeline por usuário: o que fez, quando, quantos pontos ganhou. |

### Sharebook (integração)

| Entrega | Descrição |
|---|---|
| Emitir eventos-chave | ~5 eventos: cadastro, download, doação, avaliação, indicação. |
| Perfil com pontos | Exibir XP/Karma no perfil do usuário. |
| Histórico simples | "Sua atividade" — lista cronológica dos eventos processados. |

---

## O que **não** cabe no Ano 1

- ❌ Níveis, barra de progresso, badges, títulos
- ❌ Missões diárias/semanais, streaks
- ❌ Leaderboards
- ❌ Loja de recompensas, economia (Karma/Coins)
- ❌ Lista de desejos com Karma (depende de economia madura)
- ❌ Feed social (já é outro módulo da Pegasus)
- ❌ Painel low-code de regras
- ❌ IA para personalização
- ❌ Campanhas sazonais, eventos temporários
- ❌ Avatares, molduras, notificações inteligentes

Tudo isso é **Ano 2+**, e só entra se os dados do Ano 1 justificarem.

---

## Stack sugerida

- **Serviço:** Node.js (já domina) ou Go (leve, binary único, barato de hospedar)
- **Banco:** PostgreSQL (já tem na VPS)
- **Comunicação:** REST (simples, sem mensageria)
- **Deploy:** Coolify (já tem)

Sem novos serviços pagos. Sem fila. Sem cache. A VPS atual aguenta.

---

## Métrica de sucesso do Ano 1

- Pegasus recebendo eventos de produção do Sharebook
- Usuário logado vê seus pontos e histórico
- Tempo até MVP funcional: ~3 meses com 1 dev part-time + agente

---

## Visão de longo prazo (pós Ano 1)

Se o motor de eventos + pontos estiver rodando e os dados mostrarem retenção real, aí evolui com:

- Níveis e badges (reconhecimento)
- Streaks e missões (retenção)
- Economia leve (gastar pontos em algo útil)
- Leaderboards (competição saudável)

Mas isso é conversa para quando o básico estiver no ar e validado.
