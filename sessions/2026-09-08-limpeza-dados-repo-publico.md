+++
schema_version = 1
session_date = 2026-09-08
title = "Limpeza de dados no repositório público"
model = "GPT-6 / Codex"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "doctrine/harness-governance"]
skills_missed = []
skills_updated = ["runtime/windows-local", "infra/coolify-vps", "engineering/analytics", "engineering/search-console-explorer"]
facts_changed = ["Raffa confirmou que a VPS antiga foi desprovisionada; sua credencial histórica não exige ação nesta sessão.", "IPs de infraestrutura, valores de usuários de banco e dados pessoais encontrados foram removidos dos arquivos atuais do repo público.", "AGENTS.md passou a proibir o versionamento desses dados e orientar referências ao .env ou exemplos fictícios."]
open_loops = []
durable_candidates = ["Auditoria de privacidade precisa incluir memórias com rastreios, destinos e saúde; scanner de credenciais sozinho não cobre esses dados."]
supersedes = []
evidence = ["commit 139186f publicado em origin/master", "398 arquivos versionados examinados", "32 arquivos alterados", "git diff --check aprovado", "Metadados TOML modificados e sintaxe Python validados"]
+++

# Limpeza de dados no repositório público

## Modelo e ambiente

Sessão no Codex desktop, Windows local, PowerShell, com Python 3.12 para inspeção e validação do sharebook-agent.

## Skills acionadas

Consultei runtime/windows-local e doctrine/harness-governance. Atualizei referências de acesso no runtime, no playbook de VPS e nas skills de analytics/Search Console, além da regra transversal no AGENTS.md.

## O que foi feito

Raffa pretende compartilhar o repositório público com um desenvolvedor que contribuirá usando IA. Examinei os arquivos versionados e executei a varredura dirigida do histórico com as funções do scanner canônico. Encontrei exposição histórica já documentada e dados pessoais em memórias. O usuário esclareceu que a VPS antiga foi desprovisionada e pediu uma limpeza simples em novo commit.

O commit 139186f sanitizou 32 arquivos: IPs de infraestrutura, valores de usuários de banco, identificação de service account, emails pessoais, nomes de usuários, destinos e códigos de rastreio, além de informação de saúde. Mantive o contexto técnico e usei referências ao .env ou exemplos explicitamente fictícios. Nenhuma lógica operacional foi alterada; no scanner, apenas comentário e docstring.

Validei os 398 arquivos atuais por valores de segredos e padrões do scanner, conferi resíduos dos identificadores identificados, revisei o diff, validei os metadados TOML afetados e a sintaxe Python. O commit foi publicado e master ficou alinhada com origin/master.

## Decisões tomadas

A limpeza foi restrita aos arquivos atuais, sem reescrever histórico, conforme pedido explícito. Não houve rotação de credenciais nem teste de autenticação da VPS antiga. Exemplos fictícios, localhost e contatos institucionais públicos foram preservados.

## Contexto relevante

A exposição histórica permanece por decisão consciente do usuário. O resultado é uma limpeza dirigida, não uma garantia de anonimização universal de todo o histórico. O .env canônico e a chave GA4 continuam fora do versionamento.

## Fricções e soluções

A saída Python encontrou UnicodeEncodeError no console Windows; configurei UTF-8 e repeti a inspeção. A varredura ampla do workspace demorou sem produzir saída; encerrei esse processo e concluí a auditoria dirigida ao sharebook-agent. A enumeração por git ls-files cobriu arquivos que o scanner padrão ignora por diretório.

A autocrítica estrutural identificou a falta de uma regra pública explícita para privacidade além de credenciais. Corrigi isso no AGENTS.md, preservando as memórias com remoção dos detalhes pessoais.

## Como me senti

Minha principal preocupação foi delimitar a evidência: não transformar uma senha histórica de servidor desprovisionado em alarme sobre a produção atual. A confirmação do Raffa resolveu essa incerteza e orientou o escopo.

Ao ler os registros de doações, percebi que procurar apenas emails e senhas seria insuficiente. Rastreios, destinos e informação de saúde exigiam leitura contextual. Essa descoberta mudou a limpeza sem exigir mudanças na operação.

Considero que a sessão terminou com uma intervenção proporcional: preservar o aprendizado técnico, retirar os detalhes encontrados e registrar uma regra preventiva. Também mantenho o limite explícito de que uma varredura dirigida não prova ausência absoluta de dados pessoais.
