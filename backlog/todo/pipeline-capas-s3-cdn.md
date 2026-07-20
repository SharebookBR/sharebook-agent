# Pipeline de capas: S3 + CDN + variantes otimizadas

## Problema

As capas dos livros ficam hoje no filesystem do backend, em `wwwroot/Images/Books`, e são entregues diretamente pelo Kestrel em `api.sharebook.com.br`.

Medição de produção em 2026-07-20:

- 48 referências de imagem renderizadas pela home;
- 38,5 MB transferidos para carregar essas capas;
- média de 821 KB por imagem;
- mediana de 273 KB;
- maior capa com 4,3 MB;
- cards exibidos em aproximadamente 170 × 230 px;
- imagens sem `Cache-Control`;
- componente de card sem `loading="lazy"`;
- endpoint `AvailableBooks` devolvendo 1.051 livros e aproximadamente 2 MB de JSON para a home aproveitar somente os livros físicos disponíveis.

Uma CDN isoladamente não resolve o desperdício: ela apenas entrega os mesmos arquivos excessivos mais rapidamente. A solução precisa combinar armazenamento de objetos, variantes adequadas ao contexto, cache e redução do volume solicitado pela home.

## Objetivo

Remover as capas do filesystem do backend e criar um pipeline de imagens que:

- armazene os arquivos no Amazon S3;
- entregue as imagens por CDN;
- gere variantes leves para home, busca e categorias;
- preserve uma versão de boa qualidade para a PDP;
- permita cache longo sem servir capa antiga;
- mantenha migração e rollback seguros.

## Arquitetura proposta

```text
Backend / importador
        |
        | normaliza e gera variantes
        v
Amazon S3 (bucket exclusivo de capas, privado)
        |
        | Origin Access Control
        v
Amazon CloudFront
        |
        v
img.sharebook.com.br
        |
        v
Frontend / e-mails / compartilhamentos
```

Papéis:

- **S3**: armazenamento dos objetos. Não é a CDN.
- **CloudFront**: CDN responsável por cache e entrega no edge.
- **Backend/importador**: recebe ou produz a capa, gera variantes e envia ao storage; não mantém arquivo local permanente.
- **Banco**: guarda somente a chave lógica/versionada da capa, nunca bytes ou URL acoplada ao provedor.

Usar bucket separado do bucket de PDFs de ebooks. Capas são ativos públicos; PDFs têm acesso privado e regras de download distintas. Misturar os dois aumenta o risco de erro de permissão, lifecycle e cache.

## Organização dos objetos

Estrutura de referência:

```text
covers/{bookId}/{version}/
├── source.jpg
├── display.webp
└── card.webp
```

Variantes iniciais:

- `source`: arquivo recebido, preservado para reprocessamento quando fizer sentido;
- `display`: capa para PDP, limitada aproximadamente a 600 × 900;
- `card`: miniatura para home/listagens, limitada aproximadamente a 320 × 480, sem recortar conteúdo da capa;
- WebP com qualidade inicial entre 75 e 80 para `display` e `card`, calibrada por medição visual e peso real.

Usar nomes ou diretórios versionados por hash/versão. Objetos publicados não devem ser sobrescritos na mesma URL. Isso permite:

```http
Cache-Control: public, max-age=31536000, immutable
```

Ao trocar uma capa, publicar nova versão e atualizar a chave do livro. Objetos antigos podem ser removidos depois por rotina segura ou lifecycle, sem invalidação urgente de CDN.

## Contrato e abstrações

- Criar uma abstração de storage de capas no backend; `BookService` não deve depender diretamente do SDK da AWS.
- Reaproveitar ImageSharp para normalização e geração de variantes.
- Reaproveitar a infraestrutura AWS já existente sem acoplar capas ao serviço específico de PDFs.
- Expor no contrato, no mínimo:
  - `imageUrl`: variante de exibição;
  - `thumbnailUrl`: variante de card.
- Preservar `ImageSlug` durante a transição ou evoluí-lo para uma chave lógica/versionada sem gravar hostname da CDN.
- Centralizar a montagem das URLs em configuração, usando `https://img.sharebook.com.br`.

## Integração com o backlog de Cloudflare

O item `cloudflare-cdn-ddos-protection.md` continua responsável pela proteção geral do domínio, mitigação L7 e estratégia de downloads de PDFs.

Esta iniciativa usa CloudFront especificamente como CDN do bucket privado de imagens, onde a integração S3 + Origin Access Control é direta. Não colocar Cloudflare e CloudFront em cascata para a mesma imagem.

O hostname `img.sharebook.com.br` deve isolar essa decisão. Se no futuro houver motivo econômico ou operacional para trocar a CDN, o contrato e as chaves persistidas não precisam mudar.

## Plano de execução

### Etapa 1 — Quick wins antes da migração

- [x] Criar endpoint compacto da home que retorne apenas os livros realmente exibidos.
- [x] Não usar `AvailableBooks` completo para obter os poucos livros físicos da home.
- [x] Adicionar `loading="lazy"` e `decoding="async"` às capas fora da primeira dobra.
- [x] Definir `width` e `height` para reduzir layout shift.
- [ ] Dar prioridade explícita somente à primeira capa relevante para LCP, se a medição confirmar benefício.
- [x] Configurar cache adequado para as imagens legadas enquanto a migração não termina.

Resultado validado em produção em 2026-07-20:

- contrato antigo removido, pois o frontend era seu único cliente;
- payload dos livros físicos da home: de 2.070.745 bytes para 803 bytes com os dados atuais, redução de 99,96%;
- frontend SSR saudável e emitindo 41 capas com `loading="lazy"` na home observada;
- cache legado de capas configurado por 24 horas; benefício secundário porque as prateleiras variam, mas reaproveitável entre home, busca, categorias e PDP;
- prioridade explícita da primeira capa mantida pendente: aplicar somente após confirmar que uma capa, e não o hero, é o elemento de LCP.

### Etapa 2 — Storage e geração de variantes

- [ ] Criar bucket exclusivo de capas com bloqueio de acesso público.
- [ ] Criar distribuição CloudFront com Origin Access Control.
- [ ] Configurar certificado e DNS de `img.sharebook.com.br`.
- [ ] Definir permissões mínimas de upload, leitura pela CDN e remoção.
- [ ] Implementar abstração de storage.
- [ ] Gerar `source`, `display` e `card` no create/update de livros.
- [ ] Integrar o mesmo pipeline ao ebook importer.
- [ ] Implementar rollback do upload quando persistência do livro falhar.
- [ ] Garantir limpeza segura de variantes ao excluir ou substituir uma capa.

### Etapa 3 — Contrato e frontend

- [ ] Adicionar `thumbnailUrl` aos DTOs de listagem.
- [ ] Usar `thumbnailUrl` na home, busca, categorias e dashboards.
- [ ] Usar `imageUrl`/`display` na PDP, Open Graph e contextos que exigem maior resolução.
- [ ] Manter fallback temporário para a URL legada.
- [ ] Evitar que e-mails dependam de URL assinada ou expiração.

### Etapa 4 — Backfill e corte

- [ ] Inventariar todas as capas existentes e detectar arquivos ausentes ou corrompidos.
- [ ] Criar script idempotente de migração e geração das variantes.
- [ ] Migrar em lotes com relatório de sucesso, falha, bytes de origem e bytes finais.
- [ ] Validar amostra visual de formatos e proporções diferentes.
- [ ] Confirmar que todos os livros ativos resolvem pela nova CDN.
- [ ] Trocar a URL padrão para `img.sharebook.com.br`.
- [ ] Monitorar erros 404/5xx e cache hit ratio.
- [ ] Remover arquivos da VPS somente depois da validação e de uma janela de segurança.

## Critérios de aceite

- Nenhuma nova capa fica armazenada permanentemente no container/backend.
- Bucket não permite leitura pública direta; leitura ocorre pela CDN.
- Home não usa capa principal onde existe miniatura.
- Capas fora da primeira dobra usam lazy loading.
- URLs de objetos publicados são imutáveis/versionadas.
- Trocar uma capa não exige invalidação manual para corrigir cache antigo.
- Migração é idempotente, observável e retomável.
- Nenhum livro ativo fica com imagem quebrada após o corte.
- Contrato persiste chave lógica, não hostname específico de AWS.
- Build e testes de backend/frontend passam antes dos commits.

## Metas iniciais de performance

Validar e ajustar com Lighthouse e dados reais, sem transformar estimativa em promessa:

- reduzir o conjunto atual de 38,5 MB de capas da home para menos de 3 MB se todas as prateleiras forem carregadas;
- manter miniaturas preferencialmente abaixo de 60 KB, aceitando exceções justificadas por qualidade;
- reduzir o payload usado pela home de aproximadamente 2 MB para um DTO compacto abaixo de 100 KB;
- eliminar transferência de capas pela VPS após o corte;
- medir LCP, bytes de imagem, quantidade de requests e cache hit ratio antes e depois.

## Fora de escopo inicial

- redimensionamento dinâmico por Lambda@Edge/CloudFront Functions;
- formatos adicionais além do necessário para o primeiro ganho;
- imagens assinadas: capas são conteúdo público;
- migração dos PDFs de ebooks para o mesmo fluxo;
- colocar duas CDNs em cascata.

## Riscos

- cache antigo ao sobrescrever a mesma chave;
- imagem quebrada por migração parcial;
- apagar arquivo legado antes de confirmar a cópia;
- importer e cadastro manual gerarem resultados diferentes;
- perda visual por compressão agressiva;
- acoplamento do domínio ao SDK/provedor;
- custos e complexidade desnecessários caso se implemente transformação dinâmica antes de haver demanda.
