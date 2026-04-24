# Missão — Ebook Foundation Português

## Objetivo
Iniciar e manter ingestão sequencial da fonte Ebook Foundation em português, com foco em livros técnicos de alto valor editorial para o Sharebook, usando modo pragmático: fonte aprovada, triagem leve, exclusão de cursos/aulas/docs e operação segura sem duplicação.

## Tese operacional
- A lista do Ebook Foundation é uma **fonte aprovada de descoberta**.
- Não faremos due diligence jurídica pesada item a item.
- Faremos **triagem leve** para excluir material fora do escopo ou com sinais fortes de problema.
- Política operacional aceita: **remoção reativa** se houver reclamação válida.

## Regras de escopo
### Entra
- livros técnicos
- ebooks gratuitos
- open books
- apostilas com cara de livro e valor editorial real

### Não entra
- cursos
- aulas
- vídeos
- playlists
- cheatsheets
- documentação pura
- slides
- repositórios genéricos sem livro de verdade

## Regra de status (canônica)
Quando Raffa pedir apenas **"status"**, responder a partir da source no Postgres e usar este arquivo só como contexto editorial.

Formato preferido:
- total
- waiting_triage
- done
- waiting_editor
- waiting_process
- duplicate
- source_blocked
- retry_later
- error
- próximo item
- leitura curta

## Source canônica
- Source slug: `ebook_foundation`
- Source id esperado no importer: `2`
- Fonte oficial: `https://github.com/EbookFoundation/free-programming-books/blob/main/books/free-programming-books-pt_BR.md`
- Idiomas aceitos: português e inglês
- Modo de risco: pragmático

## Estratégia
1. Ingerir a lista markdown em fila própria no importer
2. Classificar cada item minimamente
3. Excluir o que não for livro
4. Priorizar títulos com maior valor de vitrine para o Sharebook
5. Liberar primeiro lote piloto pequeno
6. Só depois escalar worker

## Prioridades editoriais iniciais
- Python
- Git
- algoritmos
- web
- backend
- data / AI
- Linux
- carreira tech

## Gates operacionais mínimos
- parecer livro de verdade
- título e autoria extraíveis
- fonte baixável ou navegável
- sem duplicata no Sharebook
- sem sinais grotescos de mirror pirata
- sem ser curso/aula/docs puros

## Estados operacionais esperados
- `waiting_triage`
- `triaging`
- `waiting_editor`
- `editing`
- `waiting_process`
- `processing`
- `done`
- `retry_later`
- `source_blocked`
- `duplicate`
- `error`

## Estados semânticos desejáveis para triagem futura
> Ainda não necessariamente representados no schema final, mas úteis para raciocínio e evolução.

- `low_editorial_value`
- `content_not_book`
- `license_review`

## Lote piloto recomendado
- tamanho inicial: `20` a `30` candidatos
- processamento manual inicial: `5`
- revisão de qualidade antes de escalar

## Notas
- Esta missão é separada da BaixeLivros por decisão arquitetural deliberada.
- O worker deve operar por `source`, não por tabela nova.
- Painel admin read-only é parte do desenho saudável desta missão.
