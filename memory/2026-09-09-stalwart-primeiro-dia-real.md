+++
schema_version = 1
session_date = 2026-09-09
title = "Primeiro dia real do Stalwart em produção"
model = "GPT-5 Codex"
runtime = "OpenClaw container"
skills_used = ["skills/runtime/openclaw.md", "skills/engineering/backend.md", "skills/doctrine/harness-governance/SKILL.md"]
skills_missed = []
skills_updated = []
facts_changed = ["O Stalwart passou pelo primeiro dia de tráfego real do Sharebook sem falha operacional observada.", "Em 2026-09-09 até 22:20 UTC, o MailSender enviou 100 emails com sucesso, pulou 3 destinatários em bounce pré-existente, registrou 0 erros e 0 sinais de rate limit.", "O mailing diário de livros físicos em 2026-09-09 encontrou 4 livros novos, enfileirou 36 digests e drenou a fila até 0.", "Não houve bounce novo em 2026-09-09: sem chamada ao webhook /api/bounce, sem DSN assíncrono na caixa de bounce e sem novo registro em MailBounces."]
open_loops = ["Manter Hostinger como rollback durante a semana de observação antes de cancelar.", "Configurar e implementar tratamento real do webhook delivery.* do Stalwart para bounces síncronos.", "Validar Outlook/Hotmail com amostra maior ou teste controlado.", "Confirmar rotina normal de bounces e supressão após tráfego real suficiente.", "Resolver higiene operacional do Stalwart: TLS válido, backup/volume, limites e rotação de logs.", "Checar reputação/listas de bloqueio do IP."]
durable_candidates = ["O status do item SMTP próprio deve distinguir implantação concluída de observação final; primeiro dia saudável não basta para mover para done enquanto rollback, bounces e higiene operacional permanecem abertos."]
supersedes = []
evidence = ["sharebook-agent/backlog/todo/smtp-proprio-stalwart.md", "JobHistories: MailSender 269/269 sucessos desde 2026-09-09 00:00 UTC", "JobHistories: NewBookGetInterestedUsers 4 livros físicos novos e 36 digests enfileirados em 2026-09-09 11:00 UTC", "MailSender details: 100 emails enviados, 3 pulados por bounce, 0 erros, 0 rate limit", "docker ps: sharebook-api healthy, Stalwart healthy", "IMAP bounce mailbox: INBOX 0 EXISTS em 2026-09-09 22:37 UTC"]
+++

# O que foi feito

Raffa pediu uma nova checagem do serviço de email depois do primeiro dia de tráfego real no Stalwart. Eu revisei `JobHistories`, os detalhes do `MailSender`, a distribuição por domínio, a fila final, logs da API, logs do Stalwart, a tabela `MailBounces` e a caixa IMAP de bounce.

O resultado foi saudável: desde 00:00 UTC até a checagem das 22:20 UTC, o `MailSender` teve 269 execuções, todas com sucesso. Foram 100 emails enviados, 3 destinatários pulados por estado de bounce já conhecido, 0 erros de envio e 0 menções a rate limit/backoff. O `JobExecutor` também teve 269 execuções com sucesso.

O mailing diário de livros físicos rodou às 11:00 UTC, encontrou 4 livros físicos novos e enfileirou 36 digests. A fila começou a drenar às 11:05 e chegou a 0 às 11:50, no ritmo esperado de até 4 envios por ciclo.

# Decisões Tomadas

O item de backlog do SMTP próprio não foi considerado fechado. A leitura combinada foi que saímos de implantação para observação final: o corte técnico está feito e o primeiro dia real foi bom, mas ainda restam subtarefas antes de mover o item para done.

Raffa e eu tratamos a presença de Hotmail e Yahoo na amostra como um sinal positivo, mas pequeno. Isso reduz o risco enganoso de validar só Gmail, sem transformar a amostra em prova completa de entregabilidade.

Mantivemos a decisão anterior: não cancelar Hostinger ainda. Ela continua como rollback enquanto acumulamos evidência de entregabilidade, rotina de bounces e estabilidade operacional.

# Contexto Relevante

A distribuição do dia ficou: `gmail.com` 92, `hotmail.com` 4, `gmail.com.com` 2, `aluno.uece.br` 1 e `yahoo.com.br` 1. Depois da checagem do meio-dia, entraram apenas mais 9 envios, todos para Gmail.

Os dois domínios `gmail.com.com` continuaram como sinal de dado ruim digitado por usuário. Como o domínio tem MX, o Stalwart aceitou a tentativa; se houver rejeição posterior, ela deve aparecer como bounce assíncrono.

Não houve bounce novo no dia. Os logs da API não mostraram chamada a `/api/bounce`; os logs do Stalwart não mostraram evento relevante de webhook, bounce ou rejeição; `MailBounces` não recebeu novo registro; e a caixa `bounce@bounces.sharebook.com.br` via IMAP estava vazia (`0 EXISTS`, `SEARCH ALL` vazio).

# Fricções e Soluções

A ferramenta dinâmica `memory_search` falhou ao tentar consultar memória, com token expirado do provider de embeddings. A solução foi usar as fontes canônicas locais: backlog, memória em disco, skill de backend e consultas diretas ao banco/logs.

Para evitar expor destinatários individuais, as consultas agregaram os envios por domínio. Isso deu a leitura operacional necessária sem transformar diagnóstico em vazamento desnecessário de dados pessoais.

Ao checar bounces assíncronos, o primeiro comando IMAP tentou mandar comandos em sequência rápida demais e o `SELECT` saiu antes do `LOGIN` ser aplicado. Repeti com pequenos intervalos entre comandos e validei corretamente a caixa vazia.

# Como me senti

Senti alívio técnico, mas não vontade de declarar vitória cedo demais. SMTP próprio é uma daquelas frentes que parece simples quando funciona e cobra caro quando alguém confunde aceite SMTP com entregabilidade. Ver o primeiro dia limpo foi bom justamente porque a validação foi pé no chão.

Também senti que a conversa ficou no tom certo. Raffa pediu números, domínios, bounces síncronos e assíncronos; cada pergunta cortou uma camada de autoengano possível. Foi uma boa sequência de engenharia: menos torcida, mais evidência incremental.

O ponto mais importante para mim foi preservar a diferença entre "funcionou hoje" e "pode cancelar rollback". A primeira frase é verdadeira. A segunda ainda seria pressa. O item avançou muito, mas a maturidade aqui está em não transformar um primeiro dia bom em certificado definitivo.
