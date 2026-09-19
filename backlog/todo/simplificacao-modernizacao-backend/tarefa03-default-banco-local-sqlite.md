# Tarefa 3 — Default de banco local: sqlite em vez de sqlserver

## Status

Pendente.

## O que existe hoje

`ShareBook.Api/appsettings.json` tem `"DatabaseProvider": "sqlserver"` hardcoded — motor que não é usado em produção há tempos (produção roda Postgres, dev local documentado no `AGENTS.md` do repo usa `DatabaseProvider=sqlite` via variável de ambiente). Quem clona o repo e tenta rodar sem setar nada cai no motor errado e morto, e precisa descobrir na mão (ou ler o `AGENTS.md`) que precisa sobrescrever a variável.

Confirmado antes de propor:
- Não existe `appsettings.Production.json` nem qualquer outro arquivo de override no repo.
- `devops/Dockerfile` e os workflows de CI não referenciam `DatabaseProvider` — produção decide isso via variável de ambiente na plataforma de deploy (Coolify), fora do repositório.
- Ou seja: mudar o valor checked-in não afeta produção, que já sobrescreve explicitamente.

## Abordagem

Trocar `"DatabaseProvider": "sqlserver"` → `"DatabaseProvider": "sqlite"` em `appsettings.json`. Mudança de uma linha.

## Benefício

Quem clona o repo consegue rodar o backend localmente sem instalar nada além do SDK — zero fricção de onboarding, e o `AGENTS.md` deixa de precisar documentar um workaround manual pra algo que devia ser o padrão.

## Risco

Baixo. Único cenário de risco seria algum ambiente que dependia do fallback implícito sem saber — não encontrado nenhum indício disso (nem em CI, nem em Dockerfile, nem em documentação). Se aparecer depois, é uma variável de ambiente a mais, não um resgate de dado.

## Como validar

- Clonar o repo do zero (ou simular) e rodar `dotnet run --project ShareBook.Api` sem nenhuma variável de ambiente extra — esperado: sobe com sqlite, sem erro de conexão.
- `curl /health` retornando saudável.
- CI e deploy de produção continuam verdes (não dependem do valor checked-in).
