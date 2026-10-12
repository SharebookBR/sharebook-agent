# Restaurar índice de memória do OpenClaw

## Status

Concluído em 2026-10-12.

## Contexto

Em 2026-10-11, durante consolidação da observabilidade Grafana Cloud, o `memory_search` ficou indisponível por falha de autenticação no provedor de embeddings:

```text
openai embeddings failed: 401 token_expired
```

Isso quebra uma capacidade estrutural do agente: recuperar memória episódica, decisões anteriores e contexto de continuidade antes de responder.

## Problema

Sem busca de memória:

- o agente depende demais da thread viva e do resumo de compactação;
- aumenta o risco de esquecer decisões recentes;
- fica mais difícil respeitar preferências, tarefas pendentes e histórico operacional;
- playbooks e memória viram menos encontráveis justamente quando a continuidade importa.

## Diagnóstico em 2026-10-12

O problema não parece ser corrupção do índice nem falta de vetores:

- `openclaw memory status --deep --agent main` mostra índice saudável, vetores prontos e 279/279 arquivos indexados;
- `openclaw memory search --agent main ...` funciona pela CLI, inclusive com query inédita;
- o auth OpenAI do agente aparece usável em `openclaw models status --agent main`;
- a ferramenta dinâmica `memory_search` exposta para a sessão continuava falhando com `401 token_expired`.

Leitura: a falha estava no caminho da tool dinâmica/Gateway, provavelmente usando token/cache antigo em memória. Um `openclaw config patch` seguro foi aplicado sem mudar provider nem segredo, mas a CLI respondeu:

```text
Restart the gateway to apply.
```

Raffa autorizou o restart do Gateway. O primeiro `SIGUSR1` ficou em drain porque havia turno ativo; após o restart efetivo, a tool dinâmica voltou a funcionar.

## Correção aplicada

1. Validado que o índice local estava íntegro pela CLI.
2. Reiniciado o Gateway/OpenClaw em janela controlada.
3. Revalidado o caminho dinâmico da sessão:
   - `memory_search` retornou resultados reais para memória recente de Grafana/Loki;
   - `memory_get` abriu `memory/2026-10-12.md`;
   - `openclaw memory search --agent main --query ...` também retornou resultados;
   - `openclaw memory status --deep --agent main` ficou com `280/280` arquivos indexados, vetores prontos e `Dirty: no`.

Conclusão: não era necessário reconstruir índice nem trocar credencial em arquivo; o problema era estado velho no Gateway.

## Resultado final

Fechado. A capacidade operacional voltou por inteiro:

- tool dinâmica `memory_search` funcional;
- tool dinâmica `memory_get` funcional;
- CLI de memória funcional;
- índice saudável, sem pendência de rebuild.

## Escopo original

1. Identificar onde o provedor de embeddings do OpenClaw está configurado.
2. Renovar ou corrigir a credencial expirada sem expor segredo em chat, logs ou arquivos versionados.
3. Rodar uma busca simples de memória e confirmar que `memory_search` voltou a retornar resultados.
4. Se a CLI estiver saudável mas a tool dinâmica continuar quebrada, fazer restart seguro do Gateway/OpenClaw em janela controlada e testar novamente.
5. Registrar no playbook/harness apropriado o procedimento de recuperação para a próxima expiração.
6. Se houver automação possível, propor alerta/check periódico para detectar `token_expired` antes de uma sessão operacional.

## Validação

- `memory_search` retorna resultados para uma query de teste sobre memória recente.
- `memory_get` consegue abrir um trecho retornado pela busca.
- Nenhum token, header ou segredo aparece em terminal, commit, playbook ou resposta ao usuário.
