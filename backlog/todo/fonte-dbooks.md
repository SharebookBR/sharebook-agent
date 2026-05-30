# Nova Fonte: dBooks.org

## O que é
`https://www.dbooks.org` — agregador de livros técnicos gratuitos com estrutura navegável por subject.

## Por que vale
- Catálogo organizado por área: `/subject/computer-science/`, `/subject/science-and-mathematics/`, etc.
- API disponível em `/api/`
- RSS em `/rss.xml`
- Livros com download direto (PDF)
- Estrutura consistente de URL por livro: `/slug-do-livro/`

## Descoberta
Item `1328` da fila (`source_blocked`) apontava para a homepage — lixo como item individual, mas revelou a fonte como candidata.

## O que fazer
1. Explorar a API em `/api/` — verificar se expõe listagem paginada de livros
2. Verificar padrão de download (PDF direto ou redirect)
3. Criar extractor dedicado ou adicionar como nova `source` no importer
4. Priorizar subject `computer-science` para o corpus técnico do Sharebook

## Quem faz
Heartbeat do OpenClaw — expansão de fontes é domínio dele.
