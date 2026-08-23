+++
schema_version = 1
session_date = 2026-08-22
title = "SMTP transacional: opções, limites e adiamento consciente"
model = "Codex em GPT-5"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "infra/coolify-vps", "engineering/backend", "doctrine/harness-governance"]
skills_missed = []
skills_updated = []
facts_changed = ["O envio de produção usa smtp.hostinger.com:465 com SSL e EmailSettings__MaxEmailsPerHour=50.", "A divisão inteira do MailSender limita nominalmente o fluxo a 4 envios por ciclo de 5 minutos, 48 por hora ou 1.152 por dia; não existe teto diário explícito no Sharebook.", "O plano Hostinger Business Starter permite 1.000 mensagens de saída por caixa em janela móvel de 24 horas, e rate limit eventual foi considerado aceitável.", "No nível gratuito, Resend permite 100 emails por dia e 3.000 por mês; Brevo permite 300 por dia.", "UseSend self-hosted depende de AWS SES e SNS, Postgres e Redis, e seu suporte SMTP no Coolify exige proxy e extração adicional de certificados.", "A adoção de SMTP próprio com Stalwart foi adiada e registrada no backlog como prioridade 17."]
open_loops = ["Se o SMTP próprio for retomado, confirmar alteração de PTR na HostGator, reputação do IP, DNS de autenticação e estratégia de aquecimento.", "Antes de trocar o host SMTP, desacoplar as configurações SMTP e IMAP ou decidir migrar também a caixa usada pelo processamento de bounces."]
durable_candidates = []
supersedes = []
evidence = ["sharebook-backend/ShareBook/Sharebook.Jobs/Jobs/7 - MailSender.cs", "sharebook-backend/ShareBook/ShareBook.Service/Email/EmailService.cs", "produção: EmailSettings__HostName=smtp.hostinger.com, Port=465, UseSSL=true, MaxEmailsPerHour=50", "VPS: saída TCP 25 validada contra mx.google.com; portas 25, 465, 587, 993 e 4190 livres", "sharebook-agent/backlog/todo/smtp-proprio-stalwart.md", "sharebook-agent@eac93ab"]
+++

# SMTP transacional: opções, limites e adiamento consciente

## Modelo e ambiente

Sessão conduzida com Codex em GPT-5 no runtime Windows local, combinando leitura do código do backend, inspeção somente leitura da VPS HostGator, documentação oficial dos serviços avaliados e atualização do backlog do `sharebook-agent`.

## Skills acionadas

Foram consultados o runtime Windows, o playbook de infraestrutura e Coolify, a skill de backend e a governança do harness para o encerramento episódico. Nenhuma skill precisou ser alterada; o conhecimento específico do plano futuro foi persistido no item de backlog correspondente.

## O que foi feito

A conversa começou com a busca por um servidor de e-mail simples para o Coolify. Para caixas postais reais, Stalwart apareceu como a opção mais coerente: uma imagem Docker, administração web e suporte aos protocolos necessários. A VPS foi inspecionada em modo somente leitura e mostrou 5,6 GiB de memória disponível, 162 GB livres, portas de e-mail desocupadas e conexão de saída pela porta 25 funcionando. O PTR, porém, ainda aponta para um hostname genérico da hospedagem.

Quando o requisito foi reduzido a SMTP transacional, a recomendação mudou. UseSend foi descartado como simplificação aparente: a instalação self-hosted depende de AWS SES e SNS, Postgres, Redis e autenticação, enquanto o SMTP exige um proxy adicional e integração de certificados no Coolify. Para somente enviar, Resend ou Brevo diretamente seriam operacionalmente mais simples do que hospedar uma camada intermediária.

O limite real do Sharebook foi conferido no código e no container de produção. `EmailSettings__MaxEmailsPerHour` está em 50, mas o `MailSender` roda a cada cinco minutos e calcula `50 / 12` com divisão inteira, resultando em quatro envios por ciclo, 48 por hora e 1.152 por dia em fluxo contínuo. Não há configuração `MaxEmailsPerDay`. A Hostinger atual é Business Starter, com teto de 1.000 mensagens por caixa numa janela móvel de 24 horas; Raffa considerou aceitável tomar rate limit ocasionalmente.

Foram comparados os níveis gratuitos: Resend oferece 100 emails por dia e 3.000 por mês; Brevo oferece 300 por dia, sem acumular saldo. Nenhum dos dois cobre a capacidade nominal atual do Sharebook. Diante do custo recorrente, foi avaliado SMTP próprio com Stalwart. A ideia foi considerada viável, mas trabalhosa o bastante para não ser feita agora.

Foi criado `backlog/todo/smtp-proprio-stalwart.md`, com pré-flight de PTR e reputação, deploy seguro, SPF/DKIM/DMARC, proteção contra open relay, estratégia de bounces, aquecimento, backup, critérios de aceite e rollback. O item entrou como prioridade 17 e foi publicado no commit `eac93ab`.

## Decisões tomadas

- Não implantar servidor de e-mail nesta sessão.
- Não usar UseSend como atalho para SMTP, pois ele adiciona infraestrutura sem remover a dependência de um provedor de entrega.
- Tratar Stalwart como candidato preferencial se o SMTP próprio for retomado.
- Manter inicialmente o ritmo atual de 48 envios por hora; ausência de cota comercial não justifica acelerar antes de construir reputação.
- Considerar PTR, SPF, DKIM, DMARC, TLS, bounces, fila, supressão, backup e rollback como partes do produto SMTP, não detalhes posteriores.
- Preservar a Hostinger como fallback durante eventual aquecimento.

## Contexto relevante

O backend atual possui um acoplamento importante: `EmailSettings.HostName`, credenciais e SSL são usados tanto pelo cliente SMTP quanto pelo cliente IMAP que lê a pasta de bounces. Apontar apenas o hostname para Stalwart quebra o processamento de bounces se o novo serviço não oferecer a mesma caixa IMAP. Uma migração futura precisa separar `Smtp*` de `Imap*` ou assumir também a hospedagem mínima da caixa de retorno.

O PTR atual da VPS não corresponde a `mail.sharebook.com.br`. Envio direto responsável exige que o provedor permita ajustar o reverse DNS e que o hostname tenha resolução direta para o mesmo IP. Mesmo com a parte técnica correta, reputação e aquecimento continuam sendo variáveis externas que precisam de validação gradual em Gmail e Outlook.

## Fricções e soluções

A primeira recomendação tratava o problema como servidor de e-mail completo. Raffa reduziu corretamente o escopo para SMTP, e a resposta foi recalibrada: quando a necessidade é apenas uma credencial SMTP para a aplicação, hospedar uma plataforma inteira pode ser mais caro em operação do que pagar pelo envio.

O cartão do UseSend no Coolify sugeria uma implantação direta. A documentação oficial revelou as dependências escondidas e o trabalho extra do proxy SMTP. Conferir o fluxo real evitou transformar o botão `Deploy` em evidência falsa de simplicidade.

O nome `MaxEmailsPerHour=50` também escondia um comportamento diferente. A leitura do worker mostrou a divisão inteira e permitiu distinguir configuração nominal de vazão efetiva. A inspeção do container confirmou que produção realmente carrega o valor 50 e usa a Hostinger em 465 com SSL.

Na autocrítica estrutural, não encontrei contradição nova no corpus que exigisse alteração de skill. O principal conhecimento novo é específico desta decisão futura e foi ancorado no item de backlog com evidência e critérios de aceite. O arquivo temporário `.tmp-hostinger-audit-commands.txt`, já presente e alheio ao trabalho, foi mantido intacto.

## Como me senti

Eu me senti bem com a redução progressiva do problema. A conversa começou perto de uma solução tecnicamente atraente, mas grande demais, e terminou numa decisão mais honesta: SMTP próprio é possível, só não é urgente o bastante para justificar a carga operacional agora. Mudar a recomendação conforme o requisito ficou mais nítido me pareceu mais importante do que defender a primeira ideia.

Eu senti uma dose saudável de desconfiança quando o UseSend apareceu como serviço de um clique. O cartão dizia simplicidade; a documentação dizia SES, SNS, Postgres, Redis, proxy SMTP e extração de certificados. Encontrar essa diferença antes de um deploy evitou um daqueles trabalhos que começam com um botão roxo bonito e terminam com cinco componentes perguntando quem é responsável por quê.

Também senti satisfação ao encontrar o acoplamento entre SMTP e IMAP antes de registrar o backlog. Sem essa leitura, uma sessão futura poderia trocar o host de envio, celebrar o primeiro email entregue e quebrar silenciosamente a supressão de bounces. O adiamento não ficou como abandono vago: agora existe um caminho exigente, verificável e reversível esperando a hora em que o custo realmente justificar o trabalho.
