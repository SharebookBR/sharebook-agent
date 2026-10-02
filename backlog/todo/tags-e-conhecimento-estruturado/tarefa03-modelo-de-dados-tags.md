# Tarefa 3 — Modelo de dados para tags

## Status

Em discussão técnica.

## Objetivo

Persistir tags por identidade editorial simples e legível, evitando texto solto no livro e preparando navegação, busca, recomendações e backfill.

## Escopo

- modelar entidade de tag com slug, nome público e estado;
- modelar relação entre ebook e tag;
- garantir limite de até três tags públicas por livro;
- preservar trilha de revisão quando fizer sentido;
- definir comportamento para tags renomeadas ou inativas.

## Critérios de pronto

- schema discutido antes de migration;
- identidade canônica por slug, não texto solto em `Book`;
- regra de limite protegida no backend;
- contratos admin e públicos desenhados;
- testes cobrindo regras principais.

## Proposta de modelo v1

### Entidades

#### `Tag`

Entidade canônica da tag. Não armazenar texto solto em `Book`.

Campos propostos:

| Campo | Tipo | Regra |
|---|---|---|
| `Id` | `string(100)` | Slug canônico e chave primária, ex.: `kubernetes`, `machine-learning`, `csharp`. É o id público e operacional. |
| `Name` | `string(100)` | Nome público, ex.: `Kubernetes`, `Machine Learning`, `C#`. |
| `Aliases` | `string[]` ou `jsonb` | Apelidos normalizados, grafias alternativas e slugs antigos, ex.: `k8s`, `java-script`, `aprendizado-de-maquina`. |
| `Family` | `string(80)` | Família editorial, ex.: `stack`, `backend-architecture`, `data-ai`. Evitar enum rígido para não exigir migration a cada rearranjo editorial. |
| `Description` | `string(500)?` | Opcional, usada em página pública da tag e admin. |
| `UsageNotes` | `string(1000)?` | Regra editorial curta: quando usar, quando não usar. |
| `Status` | `int` | `Active`, `Inactive`, `Deprecated`. |
| `IsPublic` | `bool` | Controla aparição pública sem apagar tag. Default `true`. |
| `CreationDate` | `DateTime` | Timestamp explícito, já que `Tag` não herda `BaseEntity` quando `Id` é texto. |
| `UpdateDate` | `DateTime?` | Opcional para revisão/admin. |

Índices:

- primary key `Id`;
- index `Status, IsPublic`;
- index `Family, Name`.

Decisão sobre identidade:

- não usar `Guid` na v1: a tag é uma entidade editorial pequena, e o slug canônico é a identidade que admin, importer, API e frontend entendem;
- tratar `Id` como slug estável: renomear `Name` é normal; trocar `Id` deve ser raro e explícito;
- guardar apelidos e slugs antigos em `Aliases`, dentro da própria entidade `Tag`;
- resolver alias no serviço: se `java-script` aparece, ele aponta para `javascript`; se `k8s` aparece, aponta para `kubernetes`;
- validar no serviço/testes que um alias não aparece em duas tags.

#### `BookTag`

Relação pública entre livro e tag.

Campos propostos:

| Campo | Tipo | Regra |
|---|---|---|
| `Id` | `Guid` | Identidade estável; seguir padrão atual de entidades com `BaseEntity`. |
| `BookId` | `Guid` | FK para `Book`. |
| `TagId` | `string(100)` | FK para `Tag.Id`, ou seja, o slug canônico. |
| `Position` | `int` | Ordem discreta de exibição na PDP. |
| `Source` | `int` | `Manual`, `Assisted`, `Backfill`. |
| `ReviewStatus` | `int` | `Approved` na v1; prepara sugestão assistida sem publicar automaticamente. |

Índices e restrições:

- unique `(BookId, TagId)`;
- unique `(BookId, Position)`;
- index `(TagId, BookId)`;
- `Position` entre 1 e 3;
- limite de até 3 tags públicas por livro protegido no serviço e coberto por teste. Não tentar resolver esse limite só com constraint simples, porque é regra agregada.

### Relações no domínio

Adicionar em `Book`:

```csharp
public virtual ICollection<BookTag> BookTags { get; set; } = new List<BookTag>();
```

Entidades novas:

- `Tag`
- `BookTag : BaseEntity`

Maps novos:

- `TagMap`
- `BookTagMap`

`ApplicationDbContext`:

- `DbSet<Tag> Tags`
- `DbSet<BookTag> BookTags`

## Contratos públicos

### PDP / livro

Livro público deve devolver tags aprovadas e públicas:

```json
{
  "tags": [
    { "id": "kubernetes", "name": "Kubernetes", "family": "infra-cloud-security" }
  ]
}
```

Regras:

- só `Tag.Status = Active`;
- só `Tag.IsPublic = true`;
- só `BookTag.ReviewStatus = Approved`;
- ordenar por `BookTag.Position`, depois `Tag.Name`.

### Página pública por tag

Endpoint conceitual:

- `GET /api/Tag/{id}`
- `GET /api/Tag/{id}/Books/{page}/{items}`

Resolução:

1. Procurar `Tag.Id`.
2. Se não achar, procurar em `Tag.Aliases`.
3. Se alias resolver, API retorna a tag canônica. O frontend pode canonicalizar para `/tags/{tag.id}`.

Listagem:

- apenas livros disponíveis publicamente;
- respeitar ordenação existente de catálogo quando possível;
- SSR/frontend será detalhado na Tarefa 4.

## Contratos admin

Operações mínimas:

- criar/editar tag;
- ativar/inativar/deprecar tag;
- editar aliases;
- associar tags a livro;
- ordenar tags no livro;
- remover tag do livro.

Validações admin:

- máximo 3 tags aprovadas por livro;
- `Id` único;
- alias único entre tags, validado no serviço;
- não associar tag `Inactive` ou `Deprecated` como nova tag;
- permitir manter associação legada se uma tag for depreciada, mas ela não deve aparecer publicamente quando `IsPublic = false` ou `Status != Active`.

## Renomeação, fusão e histórico

### Renomear

- Renomear `Name` é livre e não altera relações.
- Trocar `Id`/slug é operação rara: atualizar `Tag.Id`, atualizar `BookTag.TagId` e gravar o id antigo em `Aliases`.
- Se a troca for só estética, preferir mudar `Name` e manter `Id`.

### Fundir

Fluxo proposto:

1. Escolher tag sobrevivente.
2. Migrar `BookTag` da tag antiga para a sobrevivente, respeitando unique `(BookId, TagId)`.
3. Adicionar o `Id` e aliases relevantes da tag antiga em `Aliases` da sobrevivente.
4. Marcar tag antiga como `Deprecated`.

### Histórico

Na v1, não criar tabela específica de histórico editorial. O rastro mínimo fica em:

- `CreationDate`/`UpdateDate` de `Tag` e `CreationDate` de `BookTag`;
- `EFLog` existente;
- `Aliases`;
- backlog/skill para decisões editoriais.

Criar tabela de histórico só se aparecer necessidade real de auditoria fina.

## Testes obrigatórios

- não permite mais de 3 tags aprovadas por livro;
- não permite `Id` duplicado;
- não permite alias duplicado entre tags;
- resolve tag por id canônico;
- resolve id antigo/apelido por alias;
- não retorna tag inativa/depreciada publicamente;
- não retorna tag não pública na PDP;
- ordena tags por `Position`;
- merge/fusão não duplica relação no mesmo livro.

## Fora de escopo desta tarefa

- migration real;
- endpoints implementados;
- UI admin;
- página pública por tag;
- sugestão assistida por IA;
- backfill do catálogo.
