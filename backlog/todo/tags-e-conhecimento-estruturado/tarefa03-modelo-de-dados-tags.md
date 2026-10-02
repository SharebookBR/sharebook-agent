# Tarefa 3 — Modelo de dados para tags

## Status

Em discussão técnica.

## Objetivo

Persistir tags por identidade estável, evitando texto duplicado e preparando navegação, busca, recomendações e backfill.

## Escopo

- modelar entidade de tag com slug, nome público e estado;
- modelar relação entre ebook e tag;
- garantir limite de até três tags públicas por livro;
- preservar trilha de revisão quando fizer sentido;
- definir comportamento para tags renomeadas ou inativas.

## Critérios de pronto

- schema discutido antes de migration;
- identidade estável, não texto solto;
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
| `Id` | `Guid` | Identidade estável, padrão `BaseEntity`. |
| `Name` | `string(100)` | Nome público, ex.: `Kubernetes`, `Machine Learning`, `C#`. |
| `Slug` | `string(100)` | Identificador público amigável e URL estável, único, ex.: `kubernetes`, `machine-learning`, `csharp`. |
| `Family` | `string(80)` | Família editorial, ex.: `stack`, `backend-architecture`, `data-ai`. Evitar enum rígido para não exigir migration a cada rearranjo editorial. |
| `Description` | `string(500)?` | Opcional, usada em página pública da tag e admin. |
| `UsageNotes` | `string(1000)?` | Regra editorial curta: quando usar, quando não usar. |
| `Status` | `int` | `Active`, `Inactive`, `Deprecated`. |
| `IsPublic` | `bool` | Controla aparição pública sem apagar tag. Default `true`. |

Índices:

- unique `Slug`;
- index `Status, IsPublic`;
- index `Family, Name`.

Decisão sobre identidade:

- manter `Id` como chave primária interna e FK para preservar segurança em renomes, fusões e relações;
- tratar `Slug` como identificador público da tag em rotas, contratos e exploração humana;
- não expor `Id` em contratos públicos quando o `Slug` resolver o caso de uso;
- aceitar `Slug` como chave operacional em comandos admin e importadores, convertendo para `Id` no serviço.

#### `TagAlias`

Aliases resolvem grafias, redirects e renames sem quebrar navegação.

Campos propostos:

| Campo | Tipo | Regra |
|---|---|---|
| `Id` | `Guid` | Identidade estável. |
| `TagId` | `Guid` | FK para `Tag`. |
| `Alias` | `string(100)` | Texto recebido: `k8s`, `Java Script`, `aprendizado de máquina`. |
| `AliasSlug` | `string(100)` | Forma normalizada para lookup/URL. |
| `Kind` | `int` | `SearchAlias` ou `SlugRedirect`. |

Índices:

- unique `AliasSlug`;
- index `TagId`.

Uso:

- `SearchAlias`: ajuda admin/importer a resolver sugestão para a tag canônica.
- `SlugRedirect`: preserva URL antiga quando `Slug` canônico mudar.

#### `BookTag`

Relação pública entre livro e tag.

Campos propostos:

| Campo | Tipo | Regra |
|---|---|---|
| `Id` | `Guid` | Identidade estável; seguir padrão atual de entidades com `BaseEntity`. |
| `BookId` | `Guid` | FK para `Book`. |
| `TagId` | `Guid` | FK para `Tag`. |
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

- `Tag : BaseEntity`
- `TagAlias : BaseEntity`
- `BookTag : BaseEntity`

Maps novos:

- `TagMap`
- `TagAliasMap`
- `BookTagMap`

`ApplicationDbContext`:

- `DbSet<Tag> Tags`
- `DbSet<TagAlias> TagAliases`
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

- `GET /api/Tag/{slug}`
- `GET /api/Tag/{slug}/Books/{page}/{items}`

Resolução:

1. Procurar `Tag.Slug`.
2. Se não achar, procurar `TagAlias.AliasSlug` com `Kind = SlugRedirect`.
3. Se alias resolver, API pode retornar tag canônica e frontend decide canonical/redirect.

Listagem:

- apenas livros disponíveis publicamente;
- respeitar ordenação existente de catálogo quando possível;
- SSR/frontend será detalhado na Tarefa 4.

## Contratos admin

Operações mínimas:

- criar/editar tag;
- ativar/inativar/deprecar tag;
- criar/remover alias;
- associar tags a livro;
- ordenar tags no livro;
- remover tag do livro.

Validações admin:

- máximo 3 tags aprovadas por livro;
- `Slug` único;
- `AliasSlug` único;
- não associar tag `Inactive` ou `Deprecated` como nova tag;
- permitir manter associação legada se uma tag for depreciada, mas ela não deve aparecer publicamente quando `IsPublic = false` ou `Status != Active`.

## Renomeação, fusão e histórico

### Renomear

- Preferir manter `Id` da tag.
- Se mudar `Slug`, gravar slug antigo como `TagAlias.Kind = SlugRedirect`.
- Renomear `Name` não exige alterar relações `BookTag`.

### Fundir

Fluxo proposto:

1. Escolher tag sobrevivente.
2. Migrar `BookTag` da tag antiga para a sobrevivente, respeitando unique `(BookId, TagId)`.
3. Transformar slug da tag antiga em alias/redirect da sobrevivente.
4. Marcar tag antiga como `Deprecated`.

### Histórico

Na v1, não criar tabela específica de histórico editorial. O rastro mínimo fica em:

- `CreationDate` das entidades;
- `EFLog` existente;
- aliases/redirects;
- backlog/skill para decisões editoriais.

Criar tabela de histórico só se aparecer necessidade real de auditoria fina.

## Testes obrigatórios

- não permite mais de 3 tags aprovadas por livro;
- não permite `Slug` duplicado;
- não permite `AliasSlug` duplicado;
- resolve tag por slug canônico;
- resolve slug antigo por alias redirect;
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
