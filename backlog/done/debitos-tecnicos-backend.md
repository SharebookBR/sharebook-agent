# Débitos técnicos backend (achados incidentais)

## Estado

- **Status:** concluído. Ambos os itens foram corrigidos em 2026-09-20. Identificados em 2026-09-19, durante a execução do épico [Simplificação e modernização do código (backend)](simplificacao-modernizacao-backend/index.md), e movidos para `done/` em 2026-09-22.
- **Origem:** os dois foram encontrados no caminho, não procurados de propósito — um ao rodar a suíte de testes, outro ao validar a Tarefa 4 (aposentar `BookDownload`) contra Postgres real.
- **Valor:** médio — não bloqueavam produção, mas cada um corroía confiança (teste que falha por motivo errado ensina a ignorar falha real; migration que só rodava em produção afastava gente de testar migration em ambiente limpo).
- **Motivo da correção**: o Raffa apontou que um achado incidental que é bug real de comportamento não deveria ficar arquivado como "fora de escopo" só porque não era da tarefa em curso — mesmo racional que motivou o fix do `Random15BooksAsync` (ver [`simplificacao-modernizacao-backend/index.md`](simplificacao-modernizacao-backend/index.md)).

## Item 1 — `HelperTests.ImageResize` é um teste "unitário" que faz chamada HTTP de verdade pra URL externa de terceiro

**Corrigido em 2026-09-20 — commit `2c9a841` direto em `develop`.**

```csharp
[Fact]
public async Task ImageResize()
{
    var imageurl = "https://images.sympla.com.br/62b34c1818c0f.png";
    var imageBytes = await imageurl.GetBytesAsync();
    var result = ImageHelper.ResizeImage(imageBytes, 50);
    Assert.Equal(typeof(byte[]), result.GetType());
}
```

**Não é só "flaky por causa do proxy da sandbox"** — é frágil por design: depende de rede disponível, de um domínio de terceiro (`images.sympla.com.br`, nem é do Sharebook) estar no ar, servindo aquele arquivo específico, indefinidamente. Quebra em qualquer CI com egress restrito, em qualquer ambiente offline, ou no dia em que a Sympla mover/apagar a imagem — e quando quebra, a mensagem de erro (exceção de rede) não deixa óbvio que o teste em si é que está mal desenhado, não o `ImageHelper.ResizeImage`.

### Abordagem

Substituir a chamada HTTP por um fixture local: embutir um PNG pequeno de teste (`ShareBook.Test.Unit/Fixtures/sample.png` ou similar, como `EmbeddedResource`/arquivo copiado no build) e ler os bytes direto do disco, sem rede. `ImageHelper.ResizeImage` recebe `byte[]`, então a troca é mecânica — não muda o que está sendo testado de verdade (a lógica de resize), só remove a dependência de rede.

### Execução real

Em vez de um arquivo fixture versionado, o PNG de teste é gerado **em memória** via `SixLabors.ImageSharp` (a mesma biblioteca que `ImageHelper.ResizeImage` já usa internamente) — zero I/O, zero arquivo binário novo no repositório. A asserção também foi fortalecida: antes só conferia o tipo do retorno (`byte[]`), agora confere as dimensões reais da imagem redimensionada (200x100 com scale 50% → 100x50), validando de fato o comportamento do resize, não só que ele não lançou exceção.

### Risco

Nenhum — é teste, não produção.

### Como validar

- ✅ `dotnet test` passando sem rede — confirmado rodando a suíte completa: **146/146 pela primeira vez nesta sessão** (antes desta correção, essa era a única falha conhecida e documentada em todo o épico).

## Item 2 — Migration `RenameEFLogs` depende de nome de índice hardcoded específico do banco de produção real

**Corrigido em 2026-09-20 — commit `722cf4e` direto em `develop`.**

```csharp
migrationBuilder.RenameIndex(
    name: "idx_17657_IX_LogEntries_EntityName_EntityId",
    newName: "IX_EFLogs_EntityName_EntityId");
```

`idx_17657_...` é um nome com prefixo de OID do Postgres — típico de quando um índice foi criado sem nome explícito (ou importado/restaurado) e o Postgres autogerou um nome interno. Isso só existe no banco de produção real; qualquer banco criado do zero via `dotnet ef database update` (CI, ambiente novo, banco local de um dev que nunca teve o legado) tem o índice com o nome limpo de sempre (`IX_LogEntries_EntityName_EntityId`), e a migration falhava com `relation "idx_17657_..." does not exist` — **confirmado na prática** durante a validação da Tarefa 4 (aposentar `BookDownload`): não foi possível rodar a cadeia completa de migrations do zero num Postgres limpo por causa disso, precisou simular manualmente esse passo pra continuar o teste.

### Abordagem

Tornar a migration tolerante a ambos os nomes possíveis — ou (mais simples) reescrever pra usar SQL condicional (`DO $$ ... IF EXISTS ...`) que renomeia o índice/constraint só se existir com o nome antigo esperado, sem quebrar em banco limpo.

### Execução real

Implementada exatamente a abordagem de SQL condicional: dois blocos `DO $$ ... IF EXISTS ... ELSIF EXISTS ... END $$;` (um pra índice, um pra constraint de PK) que verificam em `pg_indexes`/`pg_constraint` qual dos dois nomes (`idx_17657_...` de produção ou o nome-padrão `IX_LogEntries_EntityName_EntityId`/`PK_LogEntries` de um banco criado do zero) existe antes de renomear. A migration já aplicada em produção não é reexecutada (fica registrada em `__EFMigrationsHistory`), então editar o arquivo é seguro — resolve o problema só pra quem migra a partir de um banco limpo dali pra frente.

### Risco

Baixo — mudança em migration de infraestrutura (nome de índice), não em dado.

### Como validar

- ✅ Rodada a cadeia COMPLETA de migrations do zero num Postgres 16 local recém-instalado (`dotnet ef database update` numa base nova, sem nenhum histórico) — exatamente o teste que falhava antes. Resultado: todas as 13 migrations aplicadas com sucesso, incluindo `RenameEFLogs`. Schema final conferido via `psql \d "EFLogs"`: `PK_EFLogs` (chave primária) e `IX_EFLogs_EntityName_EntityId` (índice) com os nomes corretos.
- ✅ `dotnet build` limpo (0 warnings, 0 errors) e `dotnet test` 146/146.

## Por que virou um item só

Os dois achados não têm relação direta entre si, mas compartilhavam a mesma natureza: **dívida descoberta de graça enquanto se fazia outra coisa**, de baixo risco e esforço pequeno, sem lugar óbvio nos épicos existentes. Agrupados aqui pra não se perderem soltos em notas de rodapé de outras tarefas — e, no fim, os dois foram resolvidos juntos também, na mesma sessão em que o `Random15BooksAsync` deixou de ser "achado incidental" pra virar fix de verdade.
