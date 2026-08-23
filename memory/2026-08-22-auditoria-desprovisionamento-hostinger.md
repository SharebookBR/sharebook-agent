+++
schema_version = 1
session_date = 2026-08-22
title = "Auditoria para desprovisionamento seguro da Hostinger"
model = "GPT-5 (Codex)"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "infra/coolify-vps", "chrome:control-chrome", "doctrine/harness-governance"]
skills_missed = []
skills_updated = []
facts_changed = ["A produção web e os bancos não dependem mais da VPS Hostinger; DNS e runtime apontam para a HostGator.", "O backend de produção ainda depende do Hostinger Email por smtp.hostinger.com e IMAP, usando o domínio pegasus-soft.com.br.", "Os backups externos de 22/08/2026 cobrem cinco bancos e o volume de imagens, mas não foi encontrada cópia externa do APP_KEY e do estado crítico do Coolify.", "Raffa informou ter seguido integralmente a recomendação de desativar apenas a renovação da VPS, preservar o e-mail Hostinger e proteger o estado crítico antes da expiração."]
open_loops = ["Após a expiração definitiva da VPS Hostinger, remover as credenciais VPS_SSH_* antigas e repontar defaults e documentação operacional que ainda usam esse prefixo como caixa padrão."]
durable_candidates = ["Toda saída definitiva de uma VPS deve auditar dependências de serviços do mesmo fornecedor, especialmente SMTP/IMAP, e a recuperabilidade dos backups de configuração além dos dados."]
supersedes = []
evidence = ["DNS público em 2026-08-22: sharebook.com.br, www e api em 129.121.36.220; NS b.sec.dns.br e c.sec.dns.br", "HostGator: onze containers ativos e saudáveis; home e API HTTP 200", "Container sharebook-api: EmailSettings__HostName=smtp.hostinger.com, SMTP 465, IMAP 993, serviço ativo", "DNS de pegasus-soft.com.br: MX mx1.hostinger.com e mx2.hostinger.com, SPF e DKIM Hostinger", "Coolify em 2026-08-22: backups success e s3_uploaded=true para coolify, sharebook, sharebook_importer, pegasus_core, simula_plus e volume de imagens de 1.162.204.881 bytes", "Inspeção de /data/coolify e agendamentos: nenhum backup externo de APP_KEY, SSH e proxy identificado", "Confirmação do Raffa: recomendações executadas integralmente"]
+++

# Auditoria para desprovisionamento seguro da Hostinger

## Modelo e ambiente

Sessão executada com GPT-5 no Codex, no runtime Windows local, com inspeções somente leitura dos repositórios, DNS público, produção na VPS HostGator, documentação oficial da Hostinger e tentativa de leitura do hPanel.

## Skills acionadas

Foram consultados o runtime Windows, o playbook de infraestrutura/Coolify, a skill de controle do navegador e, no encerramento, a governança do harness. Nenhuma skill precisou ser alterada.

## O que foi feito

Os quatro repositórios operacionais foram sincronizados e permaneceram limpos. Referências locais à Hostinger e à antiga VPS foram auditadas. O DNS público confirmou `sharebook.com.br`, `www` e `api` em `129.121.36.220`, com autoridade no Registro.br, enquanto home, healthcheck e Swagger responderam HTTP 200.

A VPS HostGator foi inspecionada por SSH. Os onze containers estavam ativos e saudáveis. Os backups de 22/08 registravam `success` e `s3_uploaded=true` para os bancos `coolify`, `sharebook`, `sharebook_importer`, `pegasus_core` e `simula_plus`; o volume de imagens também havia sido enviado, com aproximadamente 1,16 GB.

A auditoria encontrou uma dependência residual importante: o backend usa `smtp.hostinger.com`, SMTP 465 e IMAP 993, com o serviço ativo. O remetente pertence a `pegasus-soft.com.br`, cujo MX, SPF e DKIM apontam para Hostinger Email. Também não foi encontrada cópia externa do `APP_KEY`, das chaves SSH e das configurações de proxy do Coolify; os dumps de banco e o backup das imagens não cobrem sozinhos esse estado de recuperação.

O hPanel foi aberto apenas para leitura, mas exigiu autenticação e não havia sessão Chrome disponível para reutilizar. Por isso não foi possível provar pela interface se a assinatura de e-mail era comercialmente separada da VPS. A documentação oficial confirmou que desligar a renovação mantém o serviço ativo até o vencimento.

Raffa encerrou informando que seguiu integralmente as recomendações.

## Decisões tomadas

A recomendação foi desativar imediatamente a renovação automática somente da VPS, sem destruir a conta nem cancelar o Hostinger Email. A VPS antiga deveria permanecer disponível até a expiração em 28/08, preservando a janela de rollback sem nova cobrança.

Antes da destruição definitiva, o estado crítico de recuperação do Coolify deveria ser preservado com segurança, especialmente o `APP_KEY`. A dependência de e-mail deveria permanecer ativa e separada do cancelamento da VPS.

## Contexto relevante

A migração Hostinger para HostGator ocorreu em 17/08/2026. A VPS antiga `212.85.23.202` já estava desligada e mantida apenas como rollback. A produção atual vive em `129.121.36.220`.

Os backups externos atuais protegem os dados transacionais e as imagens, com lifecycle de sessenta dias no GCS. Recuperabilidade integral do Coolify exige mais do que esses dumps: o `APP_KEY` é necessário para decifrar variáveis e chaves armazenadas no banco da instância.

## Fricções e soluções

O quoting de SQL pelo PowerShell quebrou o parser do `vps_ssh.py`. A consulta foi refeita pelo fluxo canônico de `--script-file`, com arquivo temporário UTF-8, e o temporário foi removido após a inspeção.

A primeira seleção de navegador caiu no browser interno sem sessão autenticada; a tentativa de usar Chrome mostrou que ele não estava disponível. A incerteza comercial foi mantida explícita em vez de inferir a relação entre as assinaturas.

Uma consulta DNS inicial via `Resolve-DnsName` retornou SOA para tipos ausentes e poderia mascarar a leitura. A verificação foi repetida com `nslookup` e revelou os registros Hostinger do domínio de e-mail.

## Como me senti

Eu me senti aliviado ao encontrar a produção e os backups em ordem, porque isso confirmou que a migração técnica já estava madura o bastante para encerrar o custo da VPS antiga. A evidência era forte e coerente: DNS, containers, HTTP e uploads apontavam para a mesma conclusão.

Também senti cautela quando o SMTP apareceu. Era exatamente o tipo de dependência lateral que transforma um cancelamento aparentemente simples em incidente silencioso. Gostei de não ter arredondado “Hostinger” como se fosse uma coisa só; VPS, e-mail e conta têm fronteiras diferentes.

Por fim, senti uma satisfação tranquila com o encerramento. O Raffa seguiu a recomendação sem transformar a retirada da infraestrutura antiga numa aposta irreversível. Ficou a sensação de uma saída limpa: custo cortado, continuidade preservada e nenhum heroísmo desnecessário.
