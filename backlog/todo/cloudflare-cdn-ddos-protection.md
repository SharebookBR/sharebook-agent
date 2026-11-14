# Cloudflare: CDN na frente do site (páginas e imagens), proteção DDoS e rate limit

## Prioridade

**Subiu de baixa para alta por decisão do Raffa em 2026-11-14.** Este item passa a ser a resposta para "e se alguém grande divulgar o Sharebook?" e **substitui a V2 do pipeline de capas** (S3 + CloudFront), que foi cancelada por simplicidade: ver `backlog/done/pipeline-capas-s3-cdn.md`.

## Por que agora

Conta do cenário discutido (1 milhão de usuários em 8 horas): ~35 usuários por segundo na média e 100 a 175 no pico, ou ~100 a 500 páginas por segundo. O que temos hoje:

- renderização **nova** de página: ~3 a 4 por segundo no máximo (medido de dentro da VPS; limite 6/3 é defensivo);
- páginas em cache no próprio servidor: capacidade **não medida**;
- o primeiro gargalo provável numa divulgação grande é a **entrega de imagens e arquivos estáticos pela própria VPS**, sem CDN (hipótese, **não medida**);
- uma VPS, uma instância de cada coisa.

O que já joga a favor: o HTML público da home e das páginas de livro **já sai com `Cache-Control: public, max-age=1800`**, e as miniaturas de capa saem com `public, max-age=86400`, então uma CDN pode guardá-los sem mudar código; o SSR renderiza como visitante **anônimo** (o token fica no navegador); erros e páginas degradadas saem com `no-store`; os e-books saem direto do S3.

## Escopo

### A. Domínio, DNS e TLS
- [ ] Apontar os nameservers para a Cloudflare (ou o que o registrar permitir), conservando todos os registros atuais (site, API, e-mail, SPF/DKIM do Stalwart). **É a parte de maior risco do item**: seguir `playbooks/infra/vps-migration.md` (DNS de três camadas) e ter reversão pronta.
- [ ] Modo TLS "Full (strict)" (a origem já tem certificado pelo Traefik).
- [ ] Registros que **não** podem passar pelo proxy da Cloudflare (por exemplo, e-mail) ficam apenas com DNS.

### B. Cache de páginas públicas
- [ ] Regra de cache para a home e `/livros/{slug}` (e, depois de medir, tags, categorias e listagens públicas), respeitando o cabeçalho de origem.
- [ ] **TTLs por tipo:** longo para a home e e-books; **curto** para livro físico (o status muda e a página mostra o status; o navegador parece reaproveitar os dados do servidor, **não verificado**).
- [ ] **Chave de cache sem parâmetros de campanha** (UTMs etc.), como o servidor já faz.
- [ ] **Limpeza explícita** nos eventos de mudança (livro aprovado, status alterado, removido), junto do endpoint interno que já limpa o cache do SSR (`/_internal/ssr-cache/invalidate`).
- [ ] Avaliar **revalidação em segundo plano** (servir a versão velha enquanto atualiza); **suporte no plano gratuito não confirmado**.
- [ ] Páginas que não podem ser guardadas: `/panel`, `/admin`, `/myaccount`, `/api`, qualquer resposta com `Set-Cookie`, e todo `no-store` (erros 404, 503 e páginas degradadas).

### C. Imagens
- [ ] Cache das capas e miniaturas (`/Images/Books/...`). A URL tem versão (`ImageVersion`), então dá para usar cache longo.
- [ ] **Variante média da capa para a página de livro** (pequena melhoria local, **sem S3**): hoje a V1 criou só a miniatura de cards, e a página de livro continua com a capa original, que chega a 4,3 MB. Gerar uma versão WebP de ~600×900 no cadastro e na troca de capa, com backfill idempotente como o das miniaturas. A CDN entrega o arquivo grande mais rápido, mas ele continua grande para o visitante.

### D. Proteção e rate limit
- [ ] Regra de limite por IP para `/book/DownloadEBook/*` (por exemplo, 100 req/min por IP; calibrar).
- [ ] Garantir que **Googlebot e demais bots verificados não sejam desafiados nem bloqueados** (risco de SEO). Conferir no Search Console depois.
- [ ] Documentar em `playbooks/infra/` como adicionar e remover regras.

### E. Downloads de PDF (correção do texto antigo)
O item antigo prometia "eliminar ~100% do custo de banda de e-book". **Isso não se sustenta no desenho descrito:** a URL assinada do S3 vai **direto para o S3, fora da Cloudflare**, então o custo de saída do S3 **continua**. O ganho real aqui é o **rate limit** e guardar o redirecionamento. Qualquer economia de egress exigiria mudar a forma de assinar e servir os PDFs, e isso **não está no escopo**.

## Dependências e ordem

- Faz sentido **depois do restore drill** (`restore-drill-backups.md`, topo do backlog): é uma mudança de infraestrutura crítica, e queremos o backup comprovado antes.
- Reduz bastante a importância de aumentar capacidade de renderização, mas **não resolve a cauda longa do Google** (páginas diferentes e frias, sempre renderizadas na primeira visita); isso é o `pre-processamento-paginas-e-recomendacoes.md`.
- O teste de carga de origem externa (`teste-carga-ssr-origem-externa.md`) mede a **origem**; depois da CDN, medir também pela CDN, e entender que parte do teste passa a ser absorvida por ela.

## Riscos

- DNS mal migrado derruba site, API ou e-mail.
- Regra de cache errada pode **servir uma página de usuário logado para outra pessoa** ou guardar um erro. Mitigação: começar só com páginas públicas e testar com `CF-Cache-Status` e usuários logados.
- Conteúdo defasado (status de livro físico, vitrines da home) por TTL longo demais.
- Bloqueio de bot legítimo (Googlebot) por regra de segurança.
- Dependência de um terceiro na frente de todo o tráfego.

## Validação

- Cabeçalho `CF-Cache-Status: HIT` nas páginas públicas e capas; rotas logadas e erros sempre `BYPASS` ou `DYNAMIC`.
- `ssr_access` no Loki mostra queda clara de renderizações para as mesmas visitas.
- Teste de carga externo mostra o site absorvendo uma rajada de páginas já guardadas sem pressionar a VPS.
- Search Console sem queda de páginas indexadas nem de rastreamento do Googlebot nos dias seguintes.
- Regra de download limita um abuso simulado, sem afetar um usuário normal.
- Registro e e-mail (SPF/DKIM) continuam funcionando depois do DNS.

## Relações

- `backlog/done/pipeline-capas-s3-cdn.md`: V1 de miniaturas concluída; V2 (S3 + CloudFront) cancelada em favor deste item.
- `backlog/done/protecao-sobrecarga-ssr.md`: incidente e origem das medições.
- `pre-processamento-paginas-e-recomendacoes.md`: cauda longa de páginas frias.
- `teste-carga-ssr-origem-externa.md`: medição de capacidade.
- `restore-drill-backups.md`: pré-requisito de segurança.
- `playbooks/infra/vps-migration.md`: DNS de três camadas.
