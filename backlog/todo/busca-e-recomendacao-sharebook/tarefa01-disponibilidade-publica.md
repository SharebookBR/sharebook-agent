# Tarefa 1 — Disponibilidade pública canônica

## Status

**Concluída em 2026-08-28.**

## Problema

A regra estava invertida:

- a busca pública consultava todos os status;
- o frontend removia indisponíveis depois de receber até 100 itens;
- a busca administrativa recebia somente livros `Available`.

Isso tornava `TotalItems`, paginação e ordenação pública incoerentes.

## Regra entregue

- público recebe exclusivamente livros `BookStatus.Available`;
- admin pode consultar todos os status;
- frontend público confia no contrato do backend e não refiltra o payload.

## Critérios de pronto

- [x] disponibilidade pública centralizada no backend;
- [x] escopo ampliado preservado no admin;
- [x] filtro compensatório removido do frontend;
- [x] contrato HTTP preservado;
- [x] testes explícitos para público e admin;
- [x] builds dos dois projetos validados.

## Evidências

- Backend: commit `742ed26` — `fix: corrigir visibilidade da busca pública`.
- Frontend: commit `c7e54b1` — `fix: remover filtro compensatório da busca`.
- Backend: 117 testes unitários e 23 testes de integração aprovados; build Release sem erros.
- Frontend: teste focado aprovado e build de produção concluído.
- A suíte completa do frontend manteve a dívida conhecida de 47 falhas legadas de DI; o teste novo não participa dessas falhas.
- Sem migration e sem mudança do contrato HTTP.

## Resultado

A busca agora parte de uma verdade única. As tarefas seguintes podem alterar relevância sem carregar uma regra de visibilidade quebrada.
