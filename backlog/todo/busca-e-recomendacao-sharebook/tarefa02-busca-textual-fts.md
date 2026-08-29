# Tarefa 2 — Busca textual com Full-Text Search

## Status

**Concluída em 2026-08-29.**

Produção está no backend `d69b2cd13fdea726d6ae30031070fcc83ce0282d`, com container saudável e migration aplicada.

## Resultado entregue

A busca pública deixou de usar substring e data de criação como critério principal. Ela agora usa Full-Text Search nativo do PostgreSQL, com:

- título com peso A;
- autor com peso B;
- categoria-folha e categoria-pai com peso C;
- sinopse com peso D;
- boost explícito de título exato e prefixo;
- `ts_rank_cd` para relevância lexical;
- data de criação apenas como desempate;
- normalização de caixa, acentos, pontuação e espaços;
- prefixo por token, no formato `token:* & token:*`;
- filtro público canônico por `Available` e escopo ampliado preservado no admin;
- interpretação estruturada de formato: `fisico/impresso` e `ebook/digital/eletronico`;
- canonização de termos técnicos como `C#`, `C++`, `F#` e `.NET`.

## O que foi reaproveitado do Achei

A implementação de FTS do `achei-api` foi auditada antes da publicação. O histórico mostrou que a primeira versão com `plainto_tsquery` não atendia busca parcial e foi substituída por tokens prefixados com `to_tsquery`.

O ShareBook incorporou os aprendizados duráveis:

1. normalizar o termo antes do banco;
2. montar `token:*` para busca parcial;
3. enviar o `tsquery` como parâmetro;
4. isolar o caminho PostgreSQL dos providers usados em testes;
5. testar a SQL traduzida, não apenas a lógica em memória.

Não foi copiada a coluna persistida `SearchText`. No Achei ela exigiu backfill; no ShareBook, manter título, autor, categorias e sinopse sincronizados criaria mais pontos de drift. Com o catálogo atual, o documento calculado em consulta entregou latência aceitável sem GIN nem backfill.

## Decisões arquiteturais

- **Configuração textual:** `simple`, porque o catálogo é bilíngue e previsibilidade vale mais que stemming específico de português nesta etapa.
- **Acentos:** extensão PostgreSQL `unaccent`, instalada por migration e confirmada no banco `sharebook`.
- **Documento:** calculado durante a consulta.
- **Índice GIN:** não adotado agora. Reavaliar somente com evidência de latência ou crescimento do catálogo.
- **Busca parcial:** todos os tokens relevantes são combinados com `AND` e recebem `:*`.
- **Palavras de uma letra:** ficam fora do `tsquery`, mas permanecem no boost de título exato. Isso evita buscas amplas por `a` ou `c` sem quebrar “A Divina Comédia”.
- **Formato:** tratado como filtro estruturado. `ebook python`, por exemplo, aplica `Eletronic` e só então ranqueia `python`.
- **Fuzzy e aliases:** continuam fora desta tarefa. `sherlok`, `caverna de ssangue` e `acotar` pertencem à Tarefa 3 ou à curadoria de aliases.

## Régua de relevância executada

Foram executadas 40 consultas na API pública antes e depois da publicação. A expectativa editorial e o resultado final ficaram assim:

| # | Consulta | Classe | Resultado final |
|---:|---|---|---|
| 1 | `fisico` | GA4 / formato | Único impresso `Available` no topo. |
| 2 | `Físico` | caixa e acento | Mesmo resultado de `fisico`. |
| 3 | `odisseia` | GA4 / sem acento | `Odisséia` no topo. |
| 4 | `odisséia` | GA4 / com acento | Mesmo resultado de `odisseia`. |
| 5 | `sherlock` | título indisponível | Zero público; todas as cópias estão fora de `Available`. |
| 6 | `sherlok` | typo | Zero esperado; caso da Tarefa 3. |
| 7 | `sherlork` | typo | Zero esperado; caso da Tarefa 3. |
| 8 | `caverna de ssangue` | typo composto | Zero esperado; caso da Tarefa 3. |
| 9 | `Corte de espinhos e rosas` | título indisponível | Zero público; cópia existente está fora de `Available`. |
| 10 | `stranger things` | termo ausente | Zero. |
| 11 | `o morro dos ventos` | título indisponível | Zero público; cópia existente está fora de `Available`. |
| 12 | `acotar` | alias editorial | Zero esperado; alias ainda não cadastrado. |
| 13 | `percy jackson` | títulos indisponíveis | Zero público; quatro cópias estão fora de `Available`. |
| 14 | `meu pé de laranja lima` | termo ausente | Zero. |
| 15 | `culpa das estrelas` | termo ausente | Zero. |
| 16 | `python` | técnico amplo | `Python para Matemáticos` no topo; 28 resultados. |
| 17 | `java` | técnico amplo | `Java Básico e Orientação a Objeto` no topo; 13 resultados. |
| 18 | `quantum algorithms` | inglês composto | `Quantum Algorithms` no topo. |
| 19 | `Orgulho e preconceito` | título exato | Título exato no topo. |
| 20 | `a divina comédia` | título exato com artigo | `A Divina Comédia` acima do guia e de menções na sinopse. |
| 21 | `1984` | título exato | `1984` no topo. |
| 22 | `A arte da guerra` | título exato | `A Arte da Guerra` no topo. |
| 23 | `Clean Code` | título indisponível | Zero público; cópia existente está fora de `Available`. |
| 24 | `machine learning` | inglês composto | Resultados diretamente relacionados; 33 resultados. |
| 25 | `neural networks` | inglês composto | `A Brief Introduction to Neural Networks` no topo. |
| 26 | `computational logic` | inglês composto | `A Computational Logic (1979)` no topo. |
| 27 | `Machado de Assis` | autor | Obras do autor no topo; 33 resultados. |
| 28 | `Jane Austen` | autor | `Orgulho e preconceito` no topo. |
| 29 | `George Orwell` | autor | `A Revolucao dos Bichos` e `1984` no topo. |
| 30 | `Edgar Allan Poe` | autor | `A Carta Roubada` no topo. |
| 31 | `tecnologia` | categoria-pai | Conteúdo tecnológico no topo; 314 resultados. |
| 32 | `literatura brasileira` | categoria / composto | `História da Literatura Brasileira` no topo. |
| 33 | `ficção` | categoria | Obras de ficção no topo; 49 resultados. |
| 34 | `aventura` | categoria | Obras de aventura no topo; 185 resultados. |
| 35 | `data warehouse` | sinopse / composto | Resultado relacionado a banco de dados; uma opção pública. |
| 36 | `20 mil léguas submarinas` | título indisponível | Zero público; cópia existente está fora de `Available`. |
| 37 | `carta roubada` | título exato | `A Carta Roubada` no topo. |
| 38 | `cartomante` | título exato | `A Cartomante` no topo. |
| 39 | `C#` | termo técnico | `C# para Iniciantes` no topo; três resultados relevantes. |
| 40 | `termo inexistente xyz` | inexistente | Zero. |

## Comparação com o as-is

Os ganhos mais claros foram:

- `odisseia`: de zero para `Odisséia` no topo;
- `a divina comédia`: o título exato passou à frente do guia que apenas contém o termo;
- categoria-pai e sinopse passaram a contribuir com pesos menores;
- autor passou a ser ranqueado por relevância, não por data;
- `C#` deixou de virar uma consulta ruidosa por uma única letra;
- `fisico` deixou de retornar e-books que mencionavam “físico” na sinopse.

A comparação bruta de contagens foi afetada positivamente pela Tarefa 1: a API antiga ainda vazava livros indisponíveis. Os zeros finais de títulos conhecidos foram auditados diretamente no banco e representam a regra pública correta.

## Performance em produção

Na passagem final dos 40 casos, medidos pelo endpoint público completo:

- p50: **340 ms**;
- p95: **398 ms**;
- mínimo: **91 ms**;
- máximo: **432 ms**;
- erros: **0**.

Esses números incluem rede, API, duas consultas de paginação (`Count` e itens) e serialização. São aceitáveis na escala atual. Um `tsvector` persistido com GIN só deve entrar se a telemetria mostrar degradação real.

## Validação técnica

- `dotnet test ShareBook.Test.Unit`: **129/129**;
- `dotnet test ShareBook.Test.Integration`: **23/23**;
- `dotnet build ShareBook.Api -c Release`: sucesso, zero erros;
- SQL gerada validada com `to_tsvector`, `to_tsquery`, `setweight`, `unaccent` e `ts_rank_cd`;
- extensão `unaccent` confirmada no PostgreSQL de produção;
- deploy final `hgtmkhykpu73i7h4vo79s5rd`: `finished`;
- container `sharebook-api`: saudável no SHA final.

## Observabilidade e continuidade

O frontend já preserva `search_term` e envia `results_count` no evento de busca. A consolidação de clique e posição clicada continua como melhoria transversal de analytics; não altera o motor lexical entregue nesta tarefa.

O próximo passo funcional do épico é a [Tarefa 3 — Tolerância a erro com trigram e fallback fuzzy](tarefa03-tolerancia-a-erro.md).
