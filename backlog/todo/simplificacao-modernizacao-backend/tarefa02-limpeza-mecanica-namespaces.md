# Tarefa 2 — Limpeza mecânica: pastas duplicadas por casing + namespaces file-scoped

## Status

Pendente.

## O que existe hoje

- `ShareBook.Service/AWSSQS/` e `ShareBook.Service/AwsSqs/` coexistem como pastas irmãs, com arquivos de um mesmo namespace (`ShareBook.Service.AwsSqs`) fisicamente divididos entre as duas — achado do diagnóstico (`../diagnostico.md`, seção 2.6), provavelmente causado por dev em máquina Windows (case-insensitive) que criou pasta nova sem perceber a duplicata.
- 238 dos 302 arquivos `.cs` do projeto ainda usam namespace com chave (`namespace X { ... }`), só 64 usam a forma file-scoped (`namespace X;`), disponível desde C# 10 (2021).

## Abordagem

1. `git mv` de todo arquivo de `AWSSQS/` pra dentro de `AwsSqs/` (ou vice-versa — manter o nome já usado na maioria dos arquivos), sem tocar em lógica.
2. Rodar `dotnet format` (ou a regra equivalente de analyzer) pra converter namespace com chave em file-scoped em todo o projeto, numa tacada só — é transformação sintática pura, sem mudança de comportamento.

## Benefício

Some uma fonte de confusão de descoberta (pasta errada) e reduz uma indentação em todo arquivo do projeto — ganho de legibilidade generalizado, custo zero.

## Risco

Nenhum risco lógico — `dotnet build` detecta 100% qualquer referência quebrada. Único cuidado: diff grande (arquivo praticamente inteiro reformatado por causa da desindentação) pode dificultar review linha a linha; vale revisar por diff semântico (`git diff --ignore-space-change` não ajuda aqui, mas comentar no PR que é mudança 100% mecânica ajuda o revisor a não se assustar).

## Como validar

- `dotnet build ShareBook.sln` limpo.
- `dotnet test` sem regressão (baseline: 145/146 passando, 1 falha ambiental de proxy sem relação com o código).
- Revisão visual rápida de que nenhum arquivo de `AWSSQS/`/`AwsSqs/` ficou duplicado ou órfão.
