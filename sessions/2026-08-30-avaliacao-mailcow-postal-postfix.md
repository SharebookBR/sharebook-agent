+++
schema_version = 1
session_date = 2026-08-30
title = "Avaliação de Mailcow, Postal e Postfix para SMTP próprio"
model = "GPT-5 Codex"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "doctrine/harness-governance"]
skills_missed = []
skills_updated = []
facts_changed = ["Mailcow foi descartado para o caso de SMTP transacional enxuto por ser uma suíte groupware multi-container com requisito padrão de 6 GiB de RAM mais swap.", "Postal foi incluído como desafiante do Stalwart por oferecer bounces, supressão e webhooks integrados, embora exija MariaDB, múltiplos containers e recursos maiores.", "Postfix puro foi descartado como opção de execução porque exige componentes externos e código operacional para SASL, DKIM, bounces, supressão e observabilidade.", "A ordem atual é Stalwart como preferência, Postal como alternativa condicionada a spike e Mailcow/Postfix fora da shortlist."]
open_loops = ["Executar um spike de Postal somente se a redução do acoplamento IMAP de bounces justificar a infraestrutura adicional."]
durable_candidates = ["Para infraestrutura de e-mail, simplicidade deve ser medida pelo fluxo completo — incluindo bounces e supressão — e não apenas pelo número de containers."]
supersedes = []
evidence = ["backlog/todo/smtp-proprio-stalwart.md", "commit 9b665d3", "commit d633344", "https://docs.mailcow.email/getstarted/prerequisite-system/", "https://docs.postalserver.io/welcome/feature-list/", "https://www.postfix.org/OVERVIEW.html"]
+++

# Avaliação de Mailcow, Postal e Postfix para SMTP próprio

## Modelo e ambiente

Sessão conduzida no Codex desktop com GPT-5 Codex, no runtime local Windows. Os quatro repositórios operacionais estavam limpos e alinhados com os remotos na abertura; o `sharebook-agent` foi atualizado e recebeu push após as alterações.

## Skills acionadas

`runtime/windows-local` foi usada para confirmar o habitat, paths, shell e ritual de sincronização. `doctrine/harness-governance` foi usada para criar esta memória no contrato TOML v1 e validar seus metadados.

## O que foi feito

Foi feita uma pesquisa breve em documentação oficial de Mailcow, Postal, Postfix e Stalwart, orientada pelo requisito real de subir SMTP próprio e enviar mensagens transacionais. O item de backlog do Stalwart foi atualizado em duas rodadas: primeiro registrando Mailcow como alternativa descartada; depois incluindo Postal como desafiante e Postfix puro como alternativa descartada.

## Decisões tomadas

Mailcow não entra na shortlist: seus recursos e sua topologia são de uma suíte de groupware completa, não de um emissor transacional enxuto.

Postal entra como segunda opção, condicionada a um spike. Seus recursos nativos de fila, entrega, bounces, supressão e webhooks podem reduzir código e acoplamento do Sharebook, mas a plataforma exige mais infraestrutura e manutenção.

Postfix puro não entra. Embora seja um MTA pequeno e robusto, a instalação mínima deslocaria a complexidade para componentes externos e código próprio, contrariando a prioridade de simplicidade.

Stalwart continua preferido pelo menor footprint e pela possibilidade de manter apenas SMTP e os listeners necessários. A escolha não elimina a operação de entregabilidade: PTR, DNS, reputação, aquecimento, retries e rollback continuam obrigatórios.

## Contexto relevante

O backend atual reutiliza configurações de SMTP e IMAP para ler bounces. Postal é interessante precisamente porque pode permitir trocar essa leitura por eventos/webhooks, mas isso ainda não foi provado no fluxo do Sharebook. O backlog deve permanecer como decisão de arquitetura, não como autorização para deploy imediato.

## Fricções e soluções

A documentação de Postal é mais orientada a plataforma do que a um container isolado, então a comparação exigiu separar simplicidade de instalação de simplicidade do fluxo completo. A solução foi tratar Postal como desafiante condicionado: ele só vence se eliminar trabalho real de bounces e supressão. As fontes foram mantidas no próprio item para tornar a decisão auditável.

## Como me senti

Eu senti que a pergunta finalmente encontrou o eixo certo. Mailcow e Postfix parecem extremos opostos — uma suíte enorme e um daemon mínimo — mas nenhum dos dois atende diretamente ao desejo de simplicidade quando olhamos o sistema inteiro.

Postal me deixou com uma ambivalência produtiva. Ele carrega mais peso operacional, mas oferece exatamente as peças que costumam virar dívida escondida. Gosto de deixá-lo na mesa sem fingir que isso já é uma decisão de deploy.

Termino a sessão com uma hierarquia limpa: Stalwart primeiro, Postal como hipótese testável, Mailcow e Postfix fora. A escolha ficou menor, mais honesta e mais fácil de revisar quando o custo da Hostinger realmente justificar a mudança.
