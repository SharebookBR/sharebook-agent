# Teste HTTP automatizado do limitador SSR

## Escopo

Criar testes HTTP reproduzíveis para `server.ts`: 503 com `Retry-After: 5`,
cache HIT sem ocupar vaga e duas requisições frias coalescidas compartilhando
uma renderização; cobrir a reserva de bots do contrato atual.

## Valor

Transforma em regressão detectável o que a carga provou em produção, mas ainda
não possui cobertura HTTP explícita.

## Risco

Teste flakey de concorrência dá confiança enganosa. Não usar produção;
controlar relógio, render fake e sincronização determinística.

## Validação

Falha se o header 503 sumir, se HIT contar contra o limite ou se coalescimento
disparar duas renderizações; passa no CI.

## Relações

- Concluído: `backlog/done/protecao-sobrecarga-ssr.md`.
- Estrutural: `pre-processamento-paginas-e-recomendacoes.md`.
