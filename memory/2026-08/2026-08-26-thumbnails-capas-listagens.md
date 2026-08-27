# Thumbnails locais para capas nas listagens

Data: 2026-08-26

## Decisao

Antecipamos o ganho de performance do pipeline de capas com uma V1 local, mantendo S3 + CDN como fase 2. A capa original continua em `Images/Books/<slug>.<ext>` e o card usa `Images/Books/Thumbs/<slug>.webp`.

A transformacao limita a imagem a 360 x 540, preserva a proporcao, nao amplia imagens pequenas, nao recorta, nao adiciona padding e aplica sharpen sutil depois do resize. O WebP usa qualidade 78.

Categorias passaram de 24 para 100 itens na primeira pagina. A busca continuou com 100 para preservar descoberta e superficie SSR/SEO.

## Rollout

- backend `1c92ebd4b555fbb5f072204ec7ae822b8f2036b4`;
- frontend `404e5d2691aff994c69fc935195357f66592ff81`;
- os dois deploys precisaram ser enfileirados manualmente no Coolify porque o webhook nao criou fila;
- fila concluida, containers nos SHAs esperados e saudaveis;
- contrato funcional validado em `/api/Home/categories-showcase` com `imageUrl` e `thumbnailUrl`;
- SSR da home e de categoria validado emitindo `/Images/Books/Thumbs/*.webp`;
- arquivo publico validado como `image/webp` e cache de 24 horas.

## Backfill

O comando `sharebook_prod_book.py backfill-thumbnails` percorre a API em lotes retomaveis de 50 por padrao.

Resultado:

- 2.902 arquivos examinados em 59 lotes;
- 2.811 thumbnails criados;
- 1.073.790.124 bytes de origem convertidos em 79.585.048 bytes;
- 91 arquivos reportados sem sobrescrita ambigua.

Os 91 casos sao pares ou trios legados com o mesmo nome-base e extensoes diferentes, alem de um PDF orfao na pasta de capas. Como a convencao remove a extensao no nome do thumbnail, duas origens como `x.jpg` e `x.png` convergem para `x.webp`. O backfill prefere reportar a colisao a escolher silenciosamente a capa errada. O frontend faz fallback automatico para a original.

No cruzamento com o banco, somente dois livros `Available` estavam em grupos que referenciavam extensoes diferentes; o risco visivel ficou restrito e protegido pelo fallback.

## Efeito medido

Validacao local da transformacao sobre 53 capas dinamicas: 42,75 MB para 1,59 MB, reducao de 96,3%.

Medicao apos o deploy sobre 47 capas unicas da home dinamica: 26,27 MiB nos originais contra 1,36 MiB efetivamente servidos, reducao de 94,8%.

`o-mar-de-monstros.webp` ficou com aproximadamente 72 KB, contra cerca de 1,18 MB da capa original.

## Proxima fase

S3 + CDN permanecem no backlog. A migracao futura deve manter a separacao entre `imageUrl` e `thumbnailUrl`, adotar chaves versionadas e nao remover os originais locais antes de uma janela de validacao e rollback.
