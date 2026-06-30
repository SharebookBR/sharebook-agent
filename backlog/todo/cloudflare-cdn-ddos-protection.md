# Cloudflare: CDN + Proteção DDoS + Egress Grátis

## Motivo da Decisão

1. **Proteção DDoS L7 grátis**: rate limiting automático no edge contra floods de aplicação (ex: abuso de download). No AWS equivalente seria WAF (~US$5+/mês).

2. **Egress grátis**: cada download de PDF hoje custa taxa AWS S3 egress (US$0,138/GB em sa-east-1). Cloudflare fornece CDN em edge com egress ilimitado grátis. Eliminaria~100% do custo de banda de ebook.

3. **Comparação AWS**: CloudFront + WAF + Shield + Route53 = pago em vários eixos + força rework de assinatura S3 (bucket OAC private + CloudFront signed URLs em vez de presigned S3). Cloudflare = grátis, plug-and-play.

4. **Escala atual**: hoje ~45 downloads/semana. Não justificaria complexidade AWS. Cloudflare é a defensiva correta antes de escalar.

## Escopo

- [ ] Adquirir domínio sharebook.com.br no Cloudflare (ou transferir se já tiver registrar próprio)
- [ ] Apontar nameservers do domínio para Cloudflare
- [ ] Configurar A record do domínio para VPS Coolify (IP públiso)
- [ ] Ativar "Full (strict)" SSL/TLS mode
- [ ] Criar rate-based rule para `/book/DownloadEBook/*` (ex: 100 req/min por IP)
- [ ] Ativar cache automático para resposta 302 do endpoint (não cachea o PDF em si, só o redirect)
- [ ] Testar: simular flood local, validar que Cloudflare bloqueia no edge
- [ ] Documentar em `skills/infra/INDEX.md` como adicionar/remover regras Cloudflare

## Dependências

- Acesso administrativo ao domínio (registrar ou transfer lock)
- Conhecimento de DNS e SSL/TLS do time de infra

## Notas

- Não precisa trocar S3 presigned por CloudFront signed; presigned URL seguirá direto pro S3 (fora do cache). O ganho é rate limiting + fallback de banda.
- Cloudflare page rules / workers podem adicionar lógica extra depois (ex: throttle por user_id em vez de IP).
