# OpenAI Codex — Dreno de Limites (OAuth por Agente)

> **Status: bloqueado — sem objeto desde 2026-08-16.**
> O agente `mini`, os cron jobs e os codex-homes investigados aqui viviam no container OpenClaw, desprovisionado junto com seu volume. Não há dreno acontecendo e não há como executar nenhuma das ações abaixo.
> Preservado intencionalmente: o diagnóstico (`usage: {}` vazio, 0 tool calls, tokens OAuth independentes por agente) volta a valer se o habitat for reprovisionado.

**Origem**: Investigação de 12/Jun/2026 (achados resumidos abaixo). O arquivo `memory/2026-06-12-openai-drain-investigation.md` citado nas versões anteriores deste documento nunca existiu no repo — link morto de origem, não arquivo perdido depois. Não recriar por suposição.
**Data**: 12/Jun/2026  
**Prioridade**: Suspensa (era Alta enquanto os cron jobs do mini existiam)

## Contexto
O agente `mini` (usado para cron jobs como `preparer-baixelivros`) está queimando limites OpenAI sem produzir output real. Sintoma: `usage: {}` vazio, 0 tool calls, completion em <5s. O agente `main` funciona normalmente no mesmo horário.

**Hipótese principal**: Tokens OAuth são por agente. O codex-home do mini tem token independente do main, e o token do mini expirou/corrompeu após upgrade do OpenClaw.

## Ações

### 1. Confirmar independência de tokens OAuth
```bash
diff /data/.openclaw/agents/main/agent/codex-home/.auth/ \
     /data/.openclaw/agents/mini/agent/codex-home/.auth/
```
**Objetivo**: Provar que os tokens são separados (explicaria a seletividade do problema).

### 2. Reautenticar OAuth do mini agente
```bash
openclaw models auth login --provider openai-codex --agent mini
```
**Objetivo**: Renovar o token do mini e verificar se resolve o `usage: {}`.

### 3. Teste controlado com modelo não-OpenAI
Reativar 1 run do `preparer-baixelivros` com modelo `deepseek/deepseek-v4-pro` e verificar se produz output real.
**Objetivo**: Isolar se o problema é específico do túnel OpenAI+OAuth ou se afeta qualquer modelo no mini.

### 4. Migrar cron jobs para deepseek (curto prazo)
Enquanto o OAuth da OpenAI não for revalidado, garantir que os cron jobs do mini usem modelos deepseek (`deepseek-chat` ou `deepseek-v4-pro`).
**Objetivo**: Retomar operação dos cron jobs sem depender da OpenAI.

### 5. Investigar sessão `f190bb6a`
A primeira sessão que falhou (09/Jun 14:00, MAIN, gpt-5.4). O que era? Heartbeat? Comando manual? Por que o main falhou ali mas funcionou 2h depois?
**Objetivo**: Entender se houve um evento gatilho (restart, upgrade) que causou a primeira falha.

### 6. Acompanhar bug reports
- GitHub OpenClaw #50452: OAuth expiry → falso "rate limit"
- GitHub OpenClaw #32828: Detecção agressiva de rate-limit
- OpenAI Community: múltiplos relatos de "credits draining while idle" com GPT-5.5
**Objetivo**: Saber se há fix upstream ou workaround documentado.

## Decisões pendentes
- Raffa quer reativar os cron jobs agora (com deepseek) ou esperar resolver o OAuth primeiro?
- Migrar definitivamente os cron jobs para deepseek (reduzir dependência da OpenAI) ou manter OpenAI como primário?

## Referências
- Achados registrados apenas neste documento (seção "Contexto" acima) — não há memória episódica correspondente no repo.
