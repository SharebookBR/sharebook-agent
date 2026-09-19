# Tarefa 5 — Extrair o domínio do importer de `OperationsController` (backend + frontend)

## Status

Pendente. **Cross-repo**: precisa de mudança coordenada em `sharebook-backend` e `sharebook-frontend`, não só backend.

## O que existe hoje

`OperationsController.cs` (313 linhas) mistura health-check/diagnóstico real (`Ping`, `ForceException`, `JobExecutor`, `EmailTest`, `Jobs`) com **todo o domínio do importer de ebooks**: `ImporterDashboard`, `ImporterEditorialPrompt`, `ImporterTranslationPrompt`, `ImporterItems` (+ `AdminNotes`, `History`), `BookThumbnails/Backfill`.

**O cheiro atravessou a fronteira do sistema**: o frontend tem um `OperationsService` (`src/app/features/admin/services/operations.service.ts`) com 7 métodos, dos quais **6 são do importer** e só 1 (`getJobsDashboard`) é operação de verdade — o front já "sabe" que aquilo é tudo importer, só copiou a mesma mistura do backend.

## Abordagem

**Sem alias nem redirect de rota** — atualizar os dois lados juntos, não deixar rota velha "por garantia":

1. **Backend**: criar `ImporterController` em `/api/Importer/*`, mover os endpoints de importer de `OperationsController` pra lá. `OperationsController` fica só com `Ping`, `ForceException`, `JobExecutor`, `EmailTest`, `Jobs`, `BookThumbnails/Backfill` (este último é discutível se é "operação" ou "importer" — decidir no code review).
2. **Backend `Service/Importer/`**: mover a lógica de serviço correspondente (hoje majoritariamente em `ImporterDashboardService`, que já existe em `Service/Importer/`) pra perto do controller novo.
3. **Frontend**: extrair `ImporterService` de `OperationsService` — os 6 métodos de importer saem, `OperationsService` fica só com `getJobsDashboard`. Atualizar as URLs de `/Operations/Importer*` pra `/Importer/*`.
4. Atualizar os componentes do frontend que hoje injetam `OperationsService` pra pedir os métodos de importer em `ImporterService` (`importer-dashboard.component.ts` é o principal consumidor).

## Benefício

Descoberta melhora nos dois lados — quem procura "onde mexo no prompt editorial do importer" acha `ImporterController`/`ImporterService` pelo nome, sem precisar saber que isso mora dentro de "Operations".

## Risco

- Mecânico do lado do código (mover método + endpoint, sem mudar lógica), mas **risco real é de coordenação de deploy**: se o backend subir com as rotas novas antes do frontend apontar pra elas, o dashboard do importer quebra (404) até o frontend também subir. Área é só de admin (não é vitrine pública), então o impacto é aceitável, mas o deploy dos dois precisa ser tratado como uma unidade, não "cada repo quando terminar".
- Mitigação: subir backend e frontend na mesma janela, ou manter as duas rotas ativas por uma janela curta explícita (dias, não meses) só durante a virada — nunca como solução permanente.

## Como validar

- Backend: `dotnet build`/`dotnet test` limpos; smoke test manual dos endpoints novos.
- Frontend: `ng build`/`npm test` limpos; smoke test manual do dashboard do importer (listar itens, editar prompt editorial/tradução, ver histórico) apontando pro backend com as rotas novas.
- Confirmar que `OperationsController`/`OperationsService` continuam funcionando pro que sobrou (Jobs, health-check).
