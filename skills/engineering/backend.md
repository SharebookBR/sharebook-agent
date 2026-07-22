# Backend Sharebook

Skill operacional para mudanças de backend no `sharebook-backend`, com foco especial em EF Core, migrations, deploy e validação local.

## Quando usar

- Alteração de entidade, `DbContext`, mapping ou migration
- Endpoint novo ou mudança de contrato de API
- Diagnóstico de falha de deploy do backend
- Bugs de startup ligados a banco, provider ou migrations

## Onde estão os logs

- **`EFLogs`** (Postgres) — auditoria de mudança de entidade (quem alterou o quê). Retenção indefinida.
- **`Logs`** (Postgres) — eventos operacionais/segurança marcados explicitamente (hoje: rate limit de download). IP, `Outcome`, jsonb `Properties`. Retenção 15 dias (job `CleanupLogsTable`).
- **`docker logs sharebook-api`** — request log bruto (Serilog console). Não tem IP. Morre a cada deploy/restart (json-file).
- **Rollbar** — só exceções nível Error+.

Ver `2026-07-22-logs-estruturados-postgres-e-incidente-eflogs.md` na memória episódica para o histórico de como a tabela `Logs` nasceu.

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
- **Tabelas anteriores ao port SQL Server → Postgres têm index/constraint com prefixo `idx_17657_`** (nome físico real, não o nome de convenção do EF). A ferramenta de port renomeou constraint/index, mas manteve o nome da tabela limpo. Qualquer `RenameIndex`/`RENAME CONSTRAINT` manual em migration precisa confirmar o nome real via `pg_indexes`/`pg_constraint` em produção antes de escrever a migration — confiar na convenção (`IX_Tabela_Coluna`, `PK_Tabela`) derruba o container no startup (migration falha, transação reverte sozinha, mas o deploy fica em crash loop até corrigir). Incidente real em 2026-07-22 (rename `LogEntries` → `EFLogs`).

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

## Estrutura de projeto

```
ShareBook.Api/
  Controllers/      ← endpoints HTTP
  Configuration/    ← ServiceRepositoryCollectionExtensions.cs (registro de DI)
  Filters/          ← AuthorizationFilter, ValidateModelStateFilter
  Startup.cs        ← Configure<Settings>, JWTConfig, AddMemoryCache
ShareBook.Service/
  <Feature>/        ← IFeatureService.cs, FeatureService.cs, FeatureSettings.cs
ShareBook.Domain/   ← entidades, enums, validators
ShareBook.Repository/ ← repositórios, EF Core, migrations
```

## Padrão para novo endpoint admin

**1. Settings** (se precisar de configuração):
```csharp
// ShareBook.Service/<Feature>/<Feature>Settings.cs
namespace ShareBook.Service.<Feature>;
public class <Feature>Settings { public string MyKey { get; set; } }
```
```csharp
// Startup.cs
services.Configure<<Feature>Settings>(options => Configuration.GetSection("<Feature>").Bind(options));
```
Variável de ambiente no Coolify: `SECTION__Key` (duplo underscore = separador de seção).

**2. Service** — injetar `IOptions<Settings>` + `IMemoryCache` (já registrado no Startup):
```csharp
public class MyService(IOptions<MySettings> settings, IMemoryCache cache) : IMyService { }
```
Usar `AddSingleton` quando o serviço não tiver estado por request (ex: cache compartilhado).
Usar `AddScoped` para serviços que dependem de `DbContext` ou `IUnitOfWork`.

**3. Controller**:
```csharp
[Route("api/[controller]")]        // ← padrão do projeto. NÃO usar api/v1/
public class MyController : ControllerBase
{
    [HttpGet("action")]
    [Authorize("Bearer")]
    [AuthorizationFilter(Permissions.Permission.ApproveBook)] // admin only
    public async Task<IActionResult> Action() { ... }
}
```

**4. Registro em `ServiceRepositoryCollectionExtensions.cs`**:
```csharp
services.AddScoped<IMyService, MyService>();  // ou AddSingleton
```

## SMTP Rate Limit — Self-Healing Backoff

Padrão implementado para o `MailSender` em 2026-05-26.

**Problema**: Hostinger impõe rate limit global na conta SMTP. O Polly retry padrão tentava reenviar a mesma mensagem em loop, agravando o throttle.

**Solução**: interruptor global via `IMemoryCache` + backoff crescente.

```csharp
// Não retentar rate limit com Polly:
ShouldHandle = new PredicateBuilder().Handle<Exception>(ex =>
    ex is not SmtpCommandException smtp || !smtp.Message.Contains("Ratelimit"))

// Backoff global: constantes
const string RateLimitCacheKey = "smtp_rate_limit";
const int CycleMinutes = 5;
const int MaxBackoffCycles = 5; // 5, 10, 15, 20, 25 min

// No início de WorkAsync(): pular ciclo se em backoff
if (cache.TryGetValue(RateLimitCacheKey, out int cycles))
{
    Logger.LogInformation("SMTP em backoff. Ciclos: {cycles}. Pulando.", cycles);
    return; // IsSuccess=true, sem alarme no Rollbar
}

// Rate limit detectado — capturar ANTES do catch genérico:
catch (SmtpCommandException ex) when (ex.Message.Contains("Ratelimit"))
{
    int nextCycles = Math.Min((cache.TryGetValue(RateLimitCacheKey, out int c) ? c : 0) + 1, MaxBackoffCycles);
    cache.Set(RateLimitCacheKey, nextCycles, TimeSpan.FromMinutes(CycleMinutes * nextCycles));
    Logger.LogInformation("SMTP rate limit. Backoff por {min} min.", CycleMinutes * nextCycles);
}
```

**Regras**:
- **Sem nack**: ao tomar rate limit, não fazer nack da mensagem SQS — ela permanece na fila e será processada quando o backoff expirar. Ack (`DeleteMessageAsync`) só após envio bem-sucedido.
- **Sem alarme**: `LogInformation`, não `LogWarning`/`LogError`. Cenário self-healing não deve acionar Rollbar.
- **Queue depth**: logar profundidade da fila ao retomar o envio — visível em `/admin/jobs` sem precisar de frontend novo.
- O interruptor deve ser **global** (IMemoryCache), pois o rate limit é da conta inteira, não por mensagem.

## ImplicitUsings

Habilitado em todos os projetos desde 2026-06-01. Arquivos novos não precisam de `using System;`, `using System.Collections.Generic;`, `using System.Linq;`, `using System.Threading.Tasks;` etc.

## Comandos de validação úteis

```powershell
dotnet test C:\REPOS\SHAREBOOK\sharebook-backend\ShareBook\ShareBook.Test.Integration\ShareBook.Test.Integration.csproj -c Release --verbosity minimal
dotnet test C:\REPOS\SHAREBOOK\sharebook-backend\ShareBook\ShareBook.Test.Unit\ShareBook.Test.Unit.csproj -c Release --verbosity minimal
dotnet build C:\REPOS\SHAREBOOK\sharebook-backend\ShareBook\ShareBook.Api\ShareBook.Api.csproj
```

## Armadilhas conhecidas

### EF Core e Mapping
- **Propriedades Ignoradas**: Propriedades marcadas com `.Ignore()` no mapeamento (ex: `BookMap.cs`) NÃO são populadas pelo repositório genérico, mesmo que existam na entidade. Se precisar desses dados, use colunas persistidas (como `ImageSlug` em vez de `ImageUrl`).
- **Npgsql Resilience**: Ao ler colunas que podem ser `uuid`, `text` ou `varchar` no Postgres via Npgsql, prefira `reader.GetValue(i)?.ToString()` para evitar `InvalidCastException`.

### Arquitetura e Persistência
- **Bancos Isolados**: O banco do Importador e o banco da App são isolados na VPS. **NÃO tentar fazer JOIN SQL** entre eles. A composição de dados deve ser feita na camada de Serviço através de **Enriquecimento em Lote** (coletar IDs e fazer uma única consulta via repositório).

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
