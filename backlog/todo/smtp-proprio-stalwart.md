# Missão — SMTP próprio com Stalwart

## Objetivo

Avaliar e, se a entregabilidade for comprovada, migrar o envio transacional do Sharebook da Hostinger para um SMTP próprio baseado em Stalwart no Coolify, reduzindo custo recorrente sem perder bounces, supressão ou capacidade de rollback.

## Contexto atual

- Produção usa `smtp.hostinger.com:465` com SSL no plano Business Starter.
- A Hostinger permite 1.000 mensagens por caixa em uma janela móvel de 24 horas.
- `EmailSettings__MaxEmailsPerHour=50`, mas o `MailSender` roda a cada 5 minutos e usa divisão inteira (`50 / 12`), resultando nominalmente em 4 envios por ciclo, 48 por hora ou 1.152 por dia.
- O backoff self-healing atual deve ser preservado: ao receber `Ratelimit`, o worker espera progressivamente 5, 10, 15, 20 e 25 minutos.
- A VPS atual tem recursos suficientes, as portas de e-mail estão livres e a saída TCP 25 foi validada.
- O PTR atual da VPS é genérico e precisa ser substituído por um hostname de e-mail com resolução direta e reversa coerentes antes de qualquer envio direto.
- O backend reutiliza `EmailSettings.HostName`, credenciais e SSL tanto para SMTP quanto para ler bounces por IMAP. Trocar apenas o host SMTP quebraria o processamento atual de bounces.

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

- [ ] Confirmar com a HostGator que o PTR do IP da VPS pode ser alterado para `mail.sharebook.com.br`.
- [ ] Validar reputação atual do IP em listas de bloqueio relevantes.
- [ ] Confirmar que a porta TCP 25 de saída continua liberada.
- [ ] Definir limites de CPU, memória, disco e rotação de logs do container.

### 2. Deploy seguro do Stalwart

- [ ] Criar o serviço pelo template do Coolify com tag de imagem fixada, não `latest`.
- [ ] Persistir configuração, fila e dados em volumes com backup remoto validado.
- [ ] Expor o painel administrativo somente por HTTPS via Traefik.
- [ ] Restringir SMTP de submissão à rede interna ou a origens explicitamente autorizadas.
- [ ] Provar que o servidor não funciona como open relay.

### 3. DNS e autenticação

- [ ] Criar `A` para `mail.sharebook.com.br` apontando para a VPS.
- [ ] Configurar PTR com correspondência direta e reversa.
- [ ] Atualizar o SPF existente sem criar um segundo registro SPF.
- [ ] Gerar e publicar DKIM de 2.048 bits.
- [ ] Validar alinhamento DMARC e preservar os demais emissores autorizados do domínio.
- [ ] Configurar TLS válido para SMTP.

### 4. Bounces e supressão

- [ ] Decidir entre manter a Hostinger para IMAP/bounces ou migrar uma caixa mínima de bounces para o Stalwart.
- [ ] Se os serviços permanecerem separados, dividir `EmailSettings` em configurações independentes de SMTP e IMAP.
- [ ] Garantir que bounces assíncronos continuem alimentando `MailBounces` e a lista de supressão.
- [ ] Validar que destinatários em estado de bounce não voltam a receber tentativas.

### 5. Aquecimento e corte

- [ ] Testar SPF, DKIM, DMARC, TLS, PTR e conteúdo em ferramentas de diagnóstico.
- [ ] Fazer envios graduais para Gmail, Outlook e outros provedores relevantes.
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
