# Tarefa 2 — Limpeza mecânica: pastas duplicadas por casing + namespaces file-scoped

## Status

**Concluída em 2026-09-19** — PR aberto: https://github.com/SharebookBR/sharebook-backend/pull/611 (`chore/limpeza-mecanica-namespaces` → `develop`).

Achado extra durante a execução: o `.editorconfig` do repo tinha `csharp_style_namespace_declarations = block_scoped` explícito, na contramão do resto do arquivo (já pedia primary constructors, collection expressions, UTF8 string literals — tudo moderno). Não fazia sentido manter esse valor "porque já estava configurado assim" sem ninguém ter decidido isso de propósito (decisão do Raffa: "esse .editor é algo ultrapassado, melhor atualizar ele sem confiar muito nele"). Atualizado pra `file_scoped:warning` antes de rodar a conversão em massa, num commit separado.

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

## Execução real (2026-09-19)

- Commit 1 (`1ffaf46`): `git mv` unificando as pastas + correção do arquivo com espaço no nome. 4 arquivos, 0 inserções/deleções (rename puro).
- Commit 2 (`9151d92`): atualização do `.editorconfig` (decisão de estilo, isolada do rename mecânico).
- Commit 3 (`9eef825`): `dotnet format style --diagnostics IDE0161` aplicado no projeto inteiro. 271 arquivos, ~14 mil linhas (só sintático). `--verify-no-changes` confirmou zero namespace block-scoped remanescente.
- Build limpo e 145/146 testes passando em cada commit (mesma baseline da falha ambiental já conhecida).
