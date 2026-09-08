# Missão — SMTP próprio com Stalwart

## Objetivo

Avaliar e, se a entregabilidade for comprovada, migrar o envio transacional do Sharebook da Hostinger para um SMTP próprio baseado em Stalwart no Coolify, reduzindo custo recorrente sem perder bounces, supressão ou capacidade de rollback.

## Contexto atual

- Até o corte de 2026-09-08, produção usava `smtp.hostinger.com:465` com SSL no plano Business Starter. Após o deploy `da77b34`, produção envia pelo Stalwart; Hostinger fica apenas como rollback temporário.
- A Hostinger permite 1.000 mensagens por caixa em uma janela móvel de 24 horas.
- `EmailSettings__MaxEmailsPerHour=50`, mas o `MailSender` roda a cada 5 minutos e usa divisão inteira (`50 / 12`), resultando nominalmente em 4 envios por ciclo, 48 por hora ou 1.152 por dia.
- O backoff self-healing atual deve ser preservado: ao receber `Ratelimit`, o worker espera progressivamente 5, 10, 15, 20 e 25 minutos.
- A VPS atual tem recursos suficientes, as portas de e-mail estão livres e a saída TCP 25 foi validada.
- Em 2026-09-06, `mail.sharebook.com.br` passou a resolver para `129.121.36.220` e o PTR de `129.121.36.220` passou a apontar para `mail.sharebook.com.br`.
- Em 2026-09-06, o recurso `stalwart-mail` foi criado no Coolify com imagem `stalwartlabs/stalwart:v0.16.13`, volumes persistentes gerenciados pelo Coolify e somente a porta pública `25:25` no compose parseado. Submissão SMTP, IMAP e admin sem publicação direta no host.
- Em 2026-09-07 o serviço subiu, saiu do bootstrap (config RocksDB em `/etc/stalwart/config.json`), ficou `healthy` e foi configurado via API: hostname `mail.sharebook.com.br`, domínio principal `sharebook.com.br`, domínio/conta de bounce (`bounce@bounces.sharebook.com.br`), DKIM RSA+Ed25519 gerados, listeners enxugados (POP3 e Sieve fechados) e anti-open-relay validado.
- Em 2026-09-08, DNS de autenticação foi publicado e validado publicamente: SPF raiz, DMARC `p=none`, MX/SPF de `bounces.sharebook.com.br` e quatro DKIM (`v1-rsa-20260906` / `v1-ed25519-20260906` para domínio raiz e bounce). A resolução direta/reversa também bate (`mail.sharebook.com.br` ↔ `129.121.36.220`).
- Em 2026-09-08, validação interna confirmou API e Stalwart na rede Docker `coolify`, SMTP 25/465 e IMAP 993 abertos da API para o Stalwart, autenticação SMTP em 465 funcionando e anti-open-relay ainda ativo. TLS do Stalwart ainda apresenta certificado autoassinado (`CN = rcgen self signed cert`), mas deixou de ser bloqueio para o uso interno API → Stalwart; permanece melhoria de higiene operacional.
- Em 2026-09-08, envio real controlado para `raffacabofrio@gmail.com` via submissão SMTP interna (`465`, TLS autoassinado aceito no cliente de teste) chegou na Inbox do Gmail. Gmail validou SPF `pass`, DKIM RSA `pass` e DMARC `pass`; a assinatura Ed25519 apareceu como `neutral (no key)`, então o RSA é a prova de DKIM efetiva no Gmail neste teste. O app password temporário criado para o teste foi removido em seguida.
- Em 2026-09-08, o `sharebook-agent` ganhou script operacional de envio (`scripts/infra/sharebook_agent_send_email.py`) usando Stalwart, credencial no `.env` e túnel SSH pela VPS quando necessário. Commit `56ac3fa`.
- Em 2026-09-08, a caixa `bounce@bounces.sharebook.com.br` foi validada por IMAP no Stalwart (`INBOX`) e recebeu um DSN real gerado por envio proposital para destinatário inexistente do Gmail.
- Em 2026-09-08, envio real com `Return-Path: bounce@bounces.sharebook.com.br` e `From: admin@sharebook.com.br` caiu na Inbox do Gmail com SPF `pass`, DKIM RSA `pass` para `bounces.sharebook.com.br` e DMARC `pass` por alinhamento relaxado. O script do agente passou a usar esse Return-Path por padrão.
- Em 2026-09-08, o backend foi deployado no commit `da77b34` com `EmailSettings` desacoplado (`Smtp*` / `Imap*`), variáveis Coolify apontando para Stalwart e teste real via `POST /api/Operations/EmailTest`. O Gmail recebeu na Inbox com `Return-Path: bounce@bounces.sharebook.com.br`, SPF `pass`, DKIM RSA `pass` e DMARC `pass`.
- Decisão operacional em 2026-09-08: **não cancelar a Hostinger ainda**. O corte técnico para Stalwart está feito, mas a Hostinger deve permanecer como rollback durante aquecimento/observação, teste em Outlook/Hotmail e validação de rotina dos bounces.
- Plano de observação aceito em 2026-09-08: aguardar **uma semana** antes de reavaliar cancelamento da Hostinger. Raffaello vai doar livros físicos nessa semana, gerando volumetria real para analisar logs, fila, entregabilidade e bounces do novo SMTP.
- O backend reutiliza `EmailSettings.HostName`, credenciais e SSL tanto para SMTP quanto para ler bounces por IMAP. Trocar apenas o host SMTP quebraria o processamento atual de bounces.
- Em 2026-09-07 foi criado `ShareBook/ShareBook.Api/Controllers/BounceController.cs` — `POST /api/bounce` → `200 OK` (placeholder). Commit `94c152d`, deploy `finished`, container healthy. Serve para o webhook de bounce síncrono do Stalwart.
- Distinção chave (2026-09-07): bounce **síncrono** (rejeição `5xx` no momento da entrega) é capturado por webhook; bounce **assíncrono** (DSN devolvido depois que o MX aceitou `250`) chega como e-mail de entrada no `Return-Path` (`bounce@bounces.sharebook.com.br`) e precisa ser lido por IMAP/JMAP. O webhook sozinho **não** pega tudo.
- Decisão de bounce (2026-09-07): seguir com **Opção A** para bounces assíncronos — migrar a leitura IMAP da Hostinger para a caixa `bounce@bounces.sharebook.com.br` no Stalwart e reutilizar o parser atual. Usar webhook `delivery.*` do Stalwart apenas para bounces síncronos. Não implementar webhook+JMAP para DSNs assíncronos agora; fica como otimização futura se o polling virar dor real.

## Status atual (2026-09-08)

**Feito:**
- Stalwart up e `healthy` no Coolify, fora do bootstrap (RocksDB).
- Hostname `mail.sharebook.com.br`, domínio `sharebook.com.br`, conta `bounce@bounces.sharebook.com.br`.
- DKIM RSA 2048 + Ed25519 gerados e publicados no DNS (seletores `v1-rsa-20260906` / `v1-ed25519-20260906`).
- Listeners enxugados: 25 (público), 465 (submissão), 993 (IMAP), 443/8080 (admin). POP3 e Sieve fechados.
- Anti-open-relay comprovado (`550 Relay not allowed`).
- Autenticação SMTP interna em 465 comprovada pela rede Docker `coolify`.
- Envio real para Gmail comprovado: mensagem aceita e entregue na Inbox, SPF/DKIM RSA/DMARC passando.
- Return-Path de bounce comprovado: Gmail aceitou mensagem real com `smtp.mailfrom=bounce@bounces.sharebook.com.br` e DMARC alinhado.
- IMAP da caixa de bounce no Stalwart comprovado: login OK, `INBOX` acessível e DSN real recebido.
- Endpoint de bounce `POST /api/bounce` criado, commitado e no ar (200 OK).
- Backend de produção já envia pelo Stalwart com Return-Path de bounce (`da77b34`, deploy `mlmevr5swovwyuhbdvy2l6zg`).

**Pendente (próximos passos, em ordem):**
1. Configurar webhook `delivery.*` do Stalwart para `POST /api/bounce` e implementar o tratamento real dos eventos síncronos.
2. Envio real controlado para ferramenta de diagnóstico e Outlook. Gmail já foi validado.
3. Aquecimento + observação com Hostinger como rollback.
4. Emitir/configurar certificado TLS válido para `mail.sharebook.com.br` no Stalwart como melhoria posterior.

**Hostinger:**
- [ ] Manter ativa como rollback imediato durante a observação inicial do Stalwart.
- [ ] Reavaliar cancelamento depois de uma semana de observação com doações físicas, Gmail + Outlook/Hotmail saudáveis, bounces processados em rotina e fila sem anomalia.
- [ ] Antes de cancelar, confirmar se a Hostinger não guarda outro serviço ainda usado pelo Sharebook (caixa humana, DNS, domínio, hospedagem ou credencial operacional esquecida).

## Direção recomendada

- Usar Stalwart em um único container no Coolify.
- Começar somente com envio transacional; sem webmail, POP3, calendários ou colaboração.
- Desabilitar os listeners e serviços que não participarem do fluxo SMTP; publicar somente o estritamente necessário.
- Manter o limitador do Sharebook inicialmente no ritmo atual e aumentar apenas com evidência de entregabilidade.
- Não publicar a porta de submissão para a internet se somente os containers do Sharebook precisarem usá-la; conectar pela rede interna do Coolify com autenticação obrigatória.
- Manter a Hostinger como rollback durante o período de aquecimento e validação.

## Alternativa avaliada — Mailcow

**Decisão em 2026-08-30: não incluir Mailcow como opção de execução para este caso.**

Mailcow é uma suíte completa de groupware, não um SMTP transacional enxuto. A própria documentação descreve uma composição com Postfix, Dovecot, Rspamd, webmail, ActiveSync, antivírus, antispam, indexação, MariaDB, Redis e outros serviços. A configuração padrão exige no mínimo 6 GiB de RAM mais 1 GiB de swap e 20 GiB de disco antes das mensagens. Mesmo desabilitando ClamAV e busca full-text, continuaria sendo uma topologia multi-container com superfície de operação muito maior que a necessidade do Sharebook.

Ele passa a fazer sentido se o objetivo mudar para hospedar caixas postais, IMAP, webmail, calendário e administração de usuários. Para **somente receber submissões autenticadas do backend, enfileirar e entregar e-mail transacional**, Mailcow acrescenta componentes, atualizações e backups sem remover os problemas realmente difíceis: PTR, SPF/DKIM/DMARC, reputação do IP, aquecimento, bounces e supressão.

Stalwart permanece a opção preferida porque entrega SMTP e fila em uma única imagem/container, permite remover listeners não usados e tem footprint ocioso documentado em torno de 100 MB. Isso simplifica o software, mas não transforma SMTP próprio em operação “zero cuidado”.

Fontes oficiais: [requisitos e componentes do Mailcow](https://docs.mailcow.email/getstarted/prerequisite-system/), [instalação e topologia Docker Compose](https://docs.mailcow.email/getstarted/install/), [ciclo próprio de atualização](https://docs.mailcow.email/maintenance/update/), [imagem Docker e listeners do Stalwart](https://stalw.art/docs/install/platform/docker/), [requisitos do Stalwart](https://stalw.art/docs/install/requirements/) e [desativação de portas não usadas](https://stalw.art/docs/install/security/).

## Alternativa viável — Postal

**Decisão em 2026-08-30: incluir Postal como desafiante do Stalwart, não como opção preferida.**

Postal é alinhado ao caso de uso: foi criado como alternativa self-hosted a SendGrid, Mailgun e Postmark para aplicações. Aceita envio por SMTP ou API e já oferece DKIM, inspeção de fila e histórico, webhooks de entrega e falha, detecção de bounces e lista de supressão. Essa camada integrada pode eliminar o acoplamento atual do Sharebook com uma caixa IMAP e reduzir código próprio de bounces.

O custo está na infraestrutura. A documentação recomenda servidor dedicado e no mínimo 4 GiB de RAM, 2 CPUs e 25 GiB de disco. Postal exige MariaDB, executa vários containers e precisa de proxy web; upgrades reiniciam os componentes e não são zero-downtime. É mais plataforma do que daemon SMTP e, no volume atual, provavelmente entrega mais operação do que valor.

Postal só deve superar Stalwart se um spike curto provar que bounces, supressão e webhooks integrados compensam objetivamente a topologia mais pesada. Se a prioridade continuar sendo **o menor número de peças**, Stalwart permanece na frente.

Fontes oficiais: [visão e recursos do Postal](https://docs.postalserver.io/welcome/feature-list/), [webhooks e eventos de bounce](https://docs.postalserver.io/developer/webhooks/), [pré-requisitos](https://docs.postalserver.io/getting-started/prerequisites/), [instalação](https://docs.postalserver.io/getting-started/installation/) e [upgrades](https://docs.postalserver.io/getting-started/upgrading/).

## Alternativa avaliada — Postfix puro

**Decisão em 2026-08-30: não incluir Postfix puro como opção de execução.**

Postfix é um MTA sólido, pequeno e extremamente testado, com SMTP, fila, retries, TLS e DSNs. Mas é um bloco de construção, não uma solução transacional completa. A autenticação SASL depende de Cyrus SASL ou Dovecot; DKIM depende de um Milter externo como OpenDKIM ou Rspamd; bounces estruturados, webhooks, supressão, painel e observabilidade teriam de ser montados ou implementados pelo Sharebook.

Para este objetivo, Postfix oferece a menor instalação inicial e o maior projeto de integração. Seria racional se quiséssemos controle fino e aceitássemos operar nossa própria plataforma de entrega. Com simplicidade como critério principal, é falsa economia.

Fontes oficiais: [arquitetura e filas do Postfix](https://www.postfix.org/OVERVIEW.html), [autenticação SASL e dependências](https://www.postfix.org/SASL_README.html), [DKIM por Milter externo](https://www.postfix.org/MILTER_README.html) e [controle de relay](https://www.postfix.org/SMTPD_ACCESS_README.html).

## Plano de execução

### 1. Pré-flight de infraestrutura

- [x] Confirmar com a HostGator que o PTR do IP da VPS pode ser alterado para `mail.sharebook.com.br`.
- [ ] Validar reputação atual do IP em listas de bloqueio relevantes.
- [x] Confirmar que a porta TCP 25 de saída continua liberada.
- [ ] Definir limites de CPU, memória, disco e rotação de logs do container.

### 2. Deploy seguro do Stalwart

- [x] Criar o serviço pelo template do Coolify com tag de imagem fixada, não `latest`.
- [ ] Persistir configuração, fila e dados em volumes com backup remoto validado.
- [ ] Expor o painel administrativo somente por HTTPS via Traefik.
- [ ] Restringir SMTP de submissão à rede interna ou a origens explicitamente autorizadas.
- [x] Provar que o servidor não funciona como open relay. (2026-09-07: RCPT externo sem auth → `550 Relay not allowed`)

### 3. DNS e autenticação

- [x] Criar `A` para `mail.sharebook.com.br` apontando para a VPS.
- [x] Configurar PTR com correspondência direta e reversa.
- [x] Atualizar o SPF existente sem criar um segundo registro SPF.
- [x] Gerar e publicar DKIM de 2.048 bits.
- [x] Validar DNS público de SPF, DKIM, DMARC, MX de bounce e PTR.
- [x] Validar alinhamento SPF/DKIM/DMARC em mensagem real. (2026-09-08: Gmail Inbox, SPF pass, DKIM RSA pass, DMARC pass; Ed25519 neutral/no key)
- [ ] Configurar TLS válido para SMTP. (higiene posterior; não bloqueia API → Stalwart interno)

### 4. Bounces e supressão

- [x] Criar endpoint de webhook de bounce no backend (`POST /api/bounce` → 200 OK).
- [x] Decidir arquitetura de bounces: Opção A para assíncronos (IMAP no Stalwart) + webhook `delivery.*` para síncronos.
- [x] Migrar leitura IMAP de bounces da Hostinger para o Stalwart (`bounce@bounces.sharebook.com.br`). (2026-09-08: app password separada criada, IMAP `INBOX` validado, variáveis Coolify preparadas)
- [ ] Configurar webhook `delivery.*` do Stalwart para `POST /api/bounce`.
- [ ] Implementar tratamento real dos eventos síncronos no `BounceController` (hoje 200 OK).
- [x] Dividir `EmailSettings` em configurações independentes de SMTP e IMAP. (commit backend `da77b34`)
- [x] Garantir que bounces assíncronos continuem alimentando `MailBounces` e a lista de supressão. (2026-09-08: DSN real processado por `Operations/JobTest`; `MailBounces` recebeu `sharebook-bounce-test-1788869999@gmail.com`, erro `550`, hard bounce)
- [ ] Validar que destinatários em estado de bounce não voltam a receber tentativas.

### 5. Aquecimento e corte

- [ ] Testar SPF, DKIM, DMARC, TLS, PTR e conteúdo em ferramentas de diagnóstico.
- [ ] Fazer envios graduais para Gmail, Outlook e outros provedores relevantes. (Gmail inicial validado em 2026-09-08)
- [ ] Usar a semana de doações físicas como janela de tráfego real para analisar logs do `MailSender`, `JobHistories`, `MailBounces`, Inbox/spam e eventuais rejeições.
- [ ] Medir entrega em caixa de entrada, spam, rejeições temporárias e definitivas.
- [ ] Manter troca rápida de configuração para retornar à Hostinger durante o período de observação.
- [ ] Só cancelar o serviço anterior depois de bounces, filas, backups e entregabilidade permanecerem saudáveis.

## Critérios de aceite

- SPF, DKIM e DMARC passam e estão alinhados em mensagens reais.
- PTR e resolução direta apontam um para o outro.
- Nenhum teste externo consegue usar o servidor como relay não autenticado.
- Gmail e Outlook aceitam os envios sem degradação relevante para spam.
- A fila retenta falhas temporárias sem duplicar mensagens nem gerar tempestade de tentativas.
- O processamento de bounces e a lista de supressão continuam funcionando.
- Volumes e configuração têm backup remoto cujo conteúdo foi inspecionado.
- Existe rollback documentado e testado para o SMTP anterior.

## Fora de escopo

- Webmail e caixas postais para uso humano.
- Campanhas de marketing ou gestão de contatos.
- Substituir o rate limit do Sharebook antes de medir a reputação do novo emissor.

## Riscos principais

- IP novo ou com reputação ruim cair em spam mesmo com DNS correto.
- Configuração incorreta de SPF/DMARC afetar outros emissores do domínio.
- Open relay causar abuso e bloqueio imediato do IP.
- Cancelar a Hostinger antes de substituir corretamente o fluxo IMAP de bounces.
- Tratar aceite SMTP como prova de entrega em caixa de entrada.
