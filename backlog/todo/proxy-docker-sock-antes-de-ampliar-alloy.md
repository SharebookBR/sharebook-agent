# Proxy do docker.sock antes de ampliar o Alloy

## Escopo

Interpor proxy de socket Docker que exponha ao Alloy somente descoberta e logs
em leitura; validar ACL efetiva e só depois coletar outros containers/Postgres.

## Valor

O bind `docker.sock:ro` não torna a API Docker read-only. O proxy reduz a
superfície de um coletor comprometido.

## Risco

ACL incompleta corta logs; permissiva mantém o risco. Não alterar o frontend
estabilizado sem plano de reversão.

## Validação

Alloy continua entregando `ssr_access` sem perda/duplicata; chamadas necessárias
funcionam e ações de escrita são negadas pelo proxy.

## Relações

- Concluído: `backlog/done/protecao-sobrecarga-ssr.md`.
- Observabilidade: `observabilidade-sharebook-epico.md`.
