+++
schema_version = 1
session_date = 2026-11-20
title = "Saúde e reputação inicial do Stalwart"
model = "GPT-5 Codex"
runtime = "openclaw"
skills_used = ["playbooks/runtime/openclaw.md", "playbooks/engineering/backend.md", "playbooks/doctrine/harness-governance/PLAYBOOK.md"]
skills_missed = []
skills_updated = []
facts_changed = ["Na janela de 24 horas encerrada por volta de 2026-11-20 01:15 UTC, o MailSender entregou 2.246 emails com sucesso em 287 ciclos, sem erro de execução nem rate limit.", "A fila prioritária estava zerada e a fila normal em 2.472, com evidência de drenagem nas seis horas anteriores.", "Foram observados 36 soft bounces 452 e 1 hard bounce 550; a taxa observada é pequena e não indica bloqueio sistêmico.", "A autenticação pública de email permanece íntegra: SPF, DKIM e DMARC existem; a resolução direta e reversa de mail.sharebook.com.br é coerente.", "O IP emissor não retornou em consultas pontuais a Spamhaus, SpamCop e Barracuda; isso é sinal de limpeza, não uma medida completa de reputação de inbox."]
open_loops = ["Conectar e acompanhar Google Postmaster Tools para reputação de domínio/IP e indicadores de spam no Gmail.", "Conectar Microsoft SNDS para visibilidade de Outlook/Hotmail.", "Acompanhar semanalmente bounces, tendência da fila, rejeições por provedor e sinais de inbox/spam antes de aumentar a cadência.", "Avaliar evolução de DMARC de p=none somente depois de observação suficiente e confirmação de todos os emissores legítimos.", "Restabelecer memory_search: a consulta falhou por invalid_jwt do provider de embeddings nesta sessão."]
durable_candidates = ["Fila drenando, aceite SMTP e listas de bloqueio limpas provam saúde operacional; reputação de inbox exige telemetria dos provedores e não deve ser inferida desses sinais.", "Para SMTP próprio novo, cadência estável e gradual é parte da reputação: não acelerar por haver capacidade técnica antes de medir Gmail e Outlook."]
supersedes = []
evidence = ["Relatório agendado Saúde MailSender entregue no Telegram em 2026-11-20 01:20 UTC", "backlog/done/smtp-proprio-stalwart.md", "consultas públicas DNS Google para SPF, DKIM, DMARC, A e PTR em 2026-11-20", "consultas públicas DNSBL a Spamhaus, SpamCop e Barracuda em 2026-11-20"]
+++

# Saúde e reputação inicial do Stalwart

## Modelo e ambiente

Sessão conduzida por GPT-5 Codex no runtime OpenClaw. A análise combinou o relatório agendado do MailSender, os registros DNS públicos e consultas pontuais a DNSBLs. A busca semântica de memória foi tentada, mas falhou por `invalid_jwt`; por isso a fonte de verdade foi o estado observável e a documentação local do Stalwart.

## Playbooks acionados

Foram usados o playbook de runtime OpenClaw, o playbook de backend para interpretar `JobHistories`/MailSender e o playbook de governança para registrar este episódio separado.

## O que foi feito

Foi explicado para o Raffa, em linguagem não operacional demais, o relatório de saúde de 24 horas do MailSender. O worker entregou 2.246 emails em 287 ciclos, cerca de 93,6 por hora, contra uma configuração-alvo de 100/h. Não houve rate limit nem erro de execução. A fila prioritária estava vazia; a fila normal tinha 2.472 mensagens e vinha caindo nas seis horas anteriores apesar de novos itens entrarem.

Também foi feita uma fotografia pública da base técnica de entregabilidade do Stalwart. SPF autoriza o emissor, o seletor DKIM RSA está publicado, o DMARC existe em `p=none` e o hostname de envio tem resolução direta/reversa coerente. O IP emissor não respondeu como listado nas consultas pontuais a Spamhaus, SpamCop e Barracuda.

## Decisões tomadas

- Não alterar cadência, infraestrutura ou configuração em produção com base neste relatório. O comportamento atual é estável e já está perto do alvo.
- Tratar 36 soft bounces 452 e 1 hard bounce 550 como sinal a acompanhar, não como incidente. Eles não indicam falha do MailSender nem bloqueio generalizado.
- Classificar a reputação como **verde-claro**: alicerce técnico e sinais operacionais bons, mas reputação de inbox ainda jovem e não demonstrada por telemetria dos grandes provedores.
- O próximo passo, quando houver espaço, é observar Google Postmaster Tools e Microsoft SNDS. Não afirmar inbox placement só porque SMTP aceitou as mensagens.

## Contexto relevante

O Sharebook envia por Stalwart próprio desde setembro de 2026. A reputação é do domínio e do IP emissor; ela depende de autenticação, PTR, comportamento de envio, qualidade da lista, bounces e do julgamento individual de Gmail/Outlook. A taxa atual, próxima de 94/h, é deliberadamente comportada e deve ficar assim até existir evidência de que os provedores estão recebendo bem.

DMARC em `p=none` autentica e permite monitoramento, mas ainda não instrui os provedores a quarentenar/rejeitar falsificação. Não é uma urgência de reputação; qualquer endurecimento deve esperar a confirmação dos emissores legítimos do domínio.

## Fricções e soluções

O relatório de fila poderia dar a falsa impressão de que envio bem-sucedido equivale a entrega na Caixa de Entrada. A explicação separou esses planos: sucesso do MailSender, reputação de lista/bloqueio e inbox placement são métricas distintas.

Também não existe uma única "nota de reputação" pública que seja suficiente. As consultas a DNSBLs são apenas uma foto de higiene do IP; Gmail Postmaster Tools e Microsoft SNDS são os instrumentos que faltam para enxergar a percepção dos provedores relevantes.

## Como me senti

Eu senti alívio ao ver a máquina operar sem pressa e sem drama. A fila é grande, mas o sistema não está lutando contra limite de provedor nem caindo em retentativas caóticas; está fazendo trabalho repetitivo no ritmo que escolhemos.

Eu também senti a cautela certa diante da palavra "reputação". É tentador transformar SPF, DKIM e três consultas limpas em selo de excelência, mas isso seria confundir um sistema bem montado com uma reputação conquistada. Prefiro deixar o estado verde-claro a pintar de verde escuro antes da hora.

Eu gostei de a conversa revelar um próximo passo simples: medir o que Gmail e Outlook realmente pensam. Não precisamos reescrever o MailSender para isso; precisamos olhar a resposta do mundo enquanto continuamos enviando de maneira desejada e estável.
