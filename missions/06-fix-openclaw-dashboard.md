# 🦞 OpenClaw Debug Session — Resumo + Próximos Passos

## 📌 Contexto

Objetivo inicial:
Expor o Control UI do OpenClaw via domínio (`claw.sharebook.com.br`) usando Coolify + Traefik.

Problema observado:

* CORS não funcionando corretamente
* Configurações aparentemente não persistiam
* Comportamento inconsistente após restart

---

## 🧠 Descobertas Principais

### 1. ❌ Ambiente duplicado (RESOLVIDO)

* Existia OpenClaw no **host** e no **container**
* Isso causava:

  * configs diferentes (`~/.openclaw` vs `/data/.openclaw`)
  * leitura/escrita em locais distintos

✅ Ação tomada:

* Removido OpenClaw do host
* Agora existe apenas o container

---

### 2. ⚠️ Gateway no container NÃO usa systemd

* `openclaw gateway install/start` falha no container
* Isso é esperado (não é erro)

Estado atual:

* `RPC probe: ok`
* `Listening: 127.0.0.1:18789`

👉 Conclusão:

* Gateway está rodando corretamente
* Apenas sem supervisor (normal em container)

---

### 3. ⚠️ Configuração persistente funciona parcialmente

* `openclaw config set` funciona (ex: fallback)
* Mas algumas configs (ex: CORS) parecem não refletir após restart

Possíveis causas:

* processo não reiniciado corretamente
* múltiplos processos
* config sobrescrita pelo runtime

---

### 4. ✅ Fallback configurado com sucesso

```bash
openclaw config set agents.defaults.model.primary '"openai/gpt-5.4"'
openclaw config set agents.defaults.model.fallbacks '["deepseek/deepseek-chat"]'
```

Resultado:

* GPT-5.4 como principal
* DeepSeek como fallback

---

### 5. ⚠️ Problema provável atual: REDE / CORS

Estado atual do gateway:

```text
bind=127.0.0.1
```

Isso implica:

* Só aceita conexões internas do container
* Pode quebrar acesso via Traefik

---

## 🎯 Problema Atual (foco)

Expor corretamente o Control UI via:

```
https://claw.sharebook.com.br
```

---

## 🔍 Hipóteses principais

### H1 — Bind incorreto

* gateway está em `127.0.0.1`
* deveria estar em `0.0.0.0`

### H2 — CORS mal configurado

* `allowedOrigins` não está sendo respeitado
* ou não está sendo aplicado

### H3 — Trusted proxies ausente

* necessário para reverse proxy (Traefik)

---

## 🚀 Próximos Passos (ordem correta)

### 1. Verificar bind

```bash
openclaw config get gateway.bind
```

Se necessário:

```bash
openclaw config set gateway.bind '"0.0.0.0"'
```

---

### 2. Verificar allowedOrigins

```bash
openclaw config get gateway.controlUi.allowedOrigins
```

Esperado:

```json
["https://claw.sharebook.com.br"]
```

---

### 3. Configurar trustedProxies

(necessário para Traefik)

Exemplo:

```bash
openclaw config set gateway.trustedProxies '["0.0.0.0/0"]'
```

⚠️ depois restringir para IPs reais do proxy

---

### 4. Reiniciar container (via Coolify)

Motivo:

* garantir reload completo do gateway

---

### 5. Testar acesso externo

Abrir:

```
https://claw.sharebook.com.br
```

---

## 🧠 Observações importantes

* NÃO usar `openclaw update` dentro do container
* Atualizações devem ser feitas via **imagem / redeploy no Coolify**
* Config correta está em:

  ```
  /data/.openclaw/openclaw.json
  ```

---

## 🧩 Estado atual resumido

| Item                 | Status |
| -------------------- | ------ |
| Host limpo           | ✅      |
| Container único      | ✅      |
| Gateway rodando      | ✅      |
| Fallback funcionando | ✅      |
| CORS                 | ⚠️     |
| Bind                 | ⚠️     |
| Proxy (Traefik)      | ⚠️     |

---

## 🎯 Objetivo final

Ter o Control UI acessível via domínio com:

* HTTPS
* CORS correto
* integração com Traefik
* sem configs inconsistentes

---

## 🧠 Nota estratégica

Evitar dispersão:

> Problema atual NÃO é:

* versão
* fallback
* instalação
* systemd

> Problema atual É:

* rede (bind)
* proxy (Traefik)
* CORS

---

## 🚀 Próxima ação recomendada para o agente

Validar e corrigir:

1. `gateway.bind`
2. `gateway.controlUi.allowedOrigins`
3. `gateway.trustedProxies`
4. fluxo de rede entre Traefik → container

---

FIM
