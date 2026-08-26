# Recuperar a suíte de testes do frontend

## Problema

Em 25/08/2026, a execução completa de `npm test` no `sharebook-frontend` terminou com 65 testes executados, 18 sucessos e 47 falhas.

Isso não equivale a 47 defeitos de produto. Muitas falhas são cascatas de setup, principalmente `No provider for TransferState` em specs que instanciam o `BookService`; há também expectativas antigas de UI, como configuração de modal divergente do comportamento atual.

## Escopo

- Identificar as poucas causas-raiz que derrubam vários testes.
- Corrigir providers e setups compartilhados dos specs.
- Atualizar expectativas comprovadamente obsoletas.
- Investigar separadamente qualquer falha funcional real que permanecer depois da recuperação da infraestrutura de testes.
- Não desabilitar, pular ou enfraquecer testes apenas para obter verde.

## Critério de pronto

- `npm test` termina com exit code zero.
- Todos os testes unitários do frontend passam.
- `npm run build:ssr` continua passando.
- Nenhum teste foi silenciado para maquiar falha.

## Evidência inicial

- Comando: `npm test`.
- Resultado em 25/08/2026: `TOTAL: 47 FAILED, 18 SUCCESS`.
- Falha dominante observada: `NullInjectorError: No provider for TransferState!`.
- Falha distinta observada: spec de `RequestedsComponent` ainda espera `minWidth: 450`, enquanto o componente usa configuração responsiva.

