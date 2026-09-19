# Débitos técnicos backend (achados incidentais)

## Estado

- **Status:** identificado em 2026-09-19, durante a execução do épico [Simplificação e modernização do código (backend)](simplificacao-modernizacao-backend/index.md). Nenhum dos dois itens corrigido ainda.
- **Origem:** os dois foram encontrados no caminho, não procurados de propósito — um ao rodar a suíte de testes, outro ao validar a Tarefa 4 (aposentar `BookDownload`) contra Postgres real.
- **Valor:** médio — não bloqueiam produção hoje, mas cada um corrói confiança (teste que falha por motivo errado ensina a ignorar falha real; migration que só roda em produção afasta gente de testar migration em ambiente limpo).

## Item 1 — `HelperTests.ImageResize` é um teste "unitário" que faz chamada HTTP de verdade pra URL externa de terceiro

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

### Risco

Nenhum — é teste, não produção. Só precisa de uma imagem pequena de fixture versionada no repo.

### Como validar

- `dotnet test` passando sem rede (rodar com `--offline`/desconectado, ou simular via firewall local).
- Mesma asserção de tipo/comportamento de hoje.

## Item 2 — Migration `RenameEFLogs` depende de nome de índice hardcoded específico do banco de produção real

```csharp
migrationBuilder.RenameIndex(
    name: "idx_17657_IX_LogEntries_EntityName_EntityId",
    newName: "IX_EFLogs_EntityName_EntityId");
```

`idx_17657_...` é um nome com prefixo de OID do Postgres — típico de quando um índice foi criado sem nome explícito (ou importado/restaurado) e o Postgres autogerou um nome interno. Isso só existe no banco de produção real; qualquer banco criado do zero via `dotnet ef database update` (CI, ambiente novo, banco local de um dev que nunca teve o legado) tem o índice com o nome limpo de sempre (`IX_LogEntries_EntityName_EntityId`), e a migration falha com `relation "idx_17657_..." does not exist` — **confirmado na prática** durante a validação da Tarefa 4 (aposentar `BookDownload`): não foi possível rodar a cadeia completa de migrations do zero num Postgres limpo por causa disso, precisou simular manualmente esse passo pra continuar o teste.

### Abordagem

Tornar a migration tolerante a ambos os nomes possíveis — ou (mais simples) reescrever pra usar SQL condicional (`DO $$ ... IF EXISTS ...`) que renomeia o índice/constraint só se existir com o nome antigo esperado, sem quebrar em banco limpo. Alternativa mais simples ainda: como essa migration já foi aplicada em produção há tempos, considerar just deixá-la como está historicamente e adicionar uma migration nova, tolerante, que normaliza o nome apenas se necessário — sem reescrever histórico já aplicado.

### Risco

Baixo — é mudança em migration de infraestrutura (nome de índice), não em dado. Cuidado real: não mexer na migration já aplicada em produção sem entender o que `dotnet ef database update` faz com histórico já registrado em `__EFMigrationsHistory` (não reaplica migration já marcada, então editar o arquivo já aplicado é seguro pra produção, mas resolve o problema só pra quem migra do zero dali pra frente).

### Como validar

- Rodar a cadeia completa de migrations do zero num Postgres limpo (`dotnet ef database update` numa base nova) sem erro — é o teste que falhou durante a Tarefa 4 e motivou este item.
- Confirmar que produção continua migrando normalmente (não deveria nem tentar reaplicar `RenameEFLogs`, já que está marcada como aplicada no histórico).

## Por que virou um item só

Os dois achados não têm relação direta entre si, mas compartilham a mesma natureza: **dívida descoberta de graça enquanto se fazia outra coisa**, de baixo risco e esforço pequeno, sem lugar óbvio nos épicos existentes. Agrupados aqui pra não se perderem soltos em notas de rodapé de outras tarefas.
