# Backend Sharebook

Skill operacional para mudanças de backend no `sharebook-backend`, com foco especial em EF Core, migrations, deploy e validação local.

## Quando usar

- Alteração de entidade, `DbContext`, mapping ou migration
- Endpoint novo ou mudança de contrato de API
- Diagnóstico de falha de deploy do backend
- Bugs de startup ligados a banco, provider ou migrations

## Regras práticas

- Rodar `git` sempre em `C:\REPOS\SHAREBOOK\sharebook-backend`.
- Se a mudança tocar domínio persistido, assumir que migration, snapshot, seed e testes podem ser afetados.
- Antes de culpar a feature, separar falha de build, falha de teste, falha de migration e falha de startup. Misturar isso só produz histeria.

## Fluxo padrão para mudança persistida

1. Ler entidade, map e contrato exposto.
2. Conferir impacto em:
   - `ShareBook.Domain`
   - `ShareBook.Repository/Mapping`
   - `ShareBook.Repository/Migrations`
   - `ShareBook.Api/ViewModels`
   - `AutoMapper`
   - seeds e testes
3. Fazer a mudança mínima coerente.
4. Validar com `dotnet test` ou, no mínimo, `dotnet build`.
5. Se houver deploy via container, pensar no startup real: `Database.Migrate()`, seed e health check.

## Heurísticas de migration

- Se o EF gerar migration monstruosa mexendo em tudo, suspeitar primeiro de provider errado no design-time, não da sua alteração.
- Neste projeto, o design-time pode cair em `sqlserver` por default e gerar ruído falso. Conferir `ApplicationDbContextFactory` e `appsettings` antes de confiar cegamente no scaffold.
- Se a migration tiver sido criada no provider errado, remover e recomeçar. Não normalizar lixo.
- Se precisar fazer migration manual, patchar o snapshot com extremo cuidado e depois validar se o app sobe de verdade.
- `PendingModelChangesWarning` em runtime significa que modelo atual e snapshot versionado não batem. Isso pode derrubar a app no startup se o warning virar exceção.

## Lições da rodada de subcategoria

- Resolver `ApplicationDbContext` do root provider em teste de integração quebra com scoped service. Abrir `CreateScope()` no fixture.
- Controller herdado de `BaseCrudController` pode ficar com rota ambígua se você criar método novo com a mesma assinatura HTTP e deixar o herdado exposto.
- Mudança de contrato em categoria exige alinhar teste de integração. Não adianta deixar o teste esperando payload plano se a API agora devolve árvore.
- `POST /api/category` não aceita categoria filha sozinho se faltar mapping `CategoryVM -> Category`.
- Deploy “verde” não basta. Se a app cair no startup, o host público fica em `503` mesmo com build concluído.
- Quando a API quebra após deploy, olhar log de runtime mais recente antes de mexer no código de novo.
- `PendingModelChangesWarning` pode ser causado por snapshot stale, não só por entity nova sem migration.
- Migration manual sem `Designer.cs` é convite para drift silencioso na cadeia de migrations. Se criar migration na mão, materializar também o designer correspondente com o target model correto.
- Neste projeto, o `ApplicationDbContextModelSnapshot.cs` chegou a ficar atrás da própria migration `AddApprovedAtToBook`. Antes de culpar a migration nova, comparar o snapshot atual com o scaffold de probe.
- Para reproduzir erro real de startup local, às vezes é preciso destravar primeiro o bootstrap do ambiente `Development` com config mínima válida, como `TokenConfigurations:SecretJwtKey`.
- Se a API local ligada no banco certo subir e o host remoto continuar morto, usar a API local ou um utilitário temporário contra o mesmo Postgres ajuda a estabilizar o dado sem depender do deploy naquele minuto.

## Comandos de validação úteis

```powershell
dotnet test C:\REPOS\SHAREBOOK\sharebook-backend\ShareBook\ShareBook.Test.Integration\ShareBook.Test.Integration.csproj -c Release --verbosity minimal
dotnet test C:\REPOS\SHAREBOOK\sharebook-backend\ShareBook\ShareBook.Test.Unit\ShareBook.Test.Unit.csproj -c Release --verbosity minimal
dotnet build C:\REPOS\SHAREBOOK\sharebook-backend\ShareBook\ShareBook.Api\ShareBook.Api.csproj
```

## Armadilhas conhecidas

- Teste paralelo no Windows pode travar DLL em `obj\Release`. Se aparecer `CS2012`, rerodar de forma sequencial antes de entrar em paranoia.
- Probe com `dotnet ef migrations add` pode sujar `ApplicationDbContextModelSnapshot.cs`. Se foi só investigação, restaurar o arquivo antes de commitar.
- Hotfix que só “faz subir” pode ser válido em incidente, mas deve ser tratado como ponte, não como reconciliação definitiva de migration.

## Saída esperada

Ao terminar uma tarefa de backend persistido, deixar claro:

- quais arquivos estruturais mudaram
- se há migration real ou não
- se o startup foi considerado
- quais testes/builds passaram
- qual risco residual ficou
