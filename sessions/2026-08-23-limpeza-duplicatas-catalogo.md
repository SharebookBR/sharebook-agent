+++
schema_version = 1
session_date = 2026-08-23
title = "Correção de categorias e limpeza cuidadosa de duplicatas digitais"
model = "GPT-5 (Codex)"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "engineering/frontend", "engineering/backend", "engineering/postgres-ro", "infra/coolify-vps", "importers/ebook-importer", "doctrine/harness-governance"]
skills_missed = []
skills_updated = []
facts_changed = ["Repetições de livros físicos e combinações físico mais digital são legítimas; título repetido não é critério de exclusão.", "A auditoria de 1.068 digitais ativos encontrou uma duplicata digital inequívoca: Eu e Outras Poesias.", "Não restaram pares digitais ativos com título e autor normalizados iguais nem caminhos de PDF compartilhados.", "Os volumes 1, 2 e 3 de The Art of High Performance Computing são distintos, mas compartilham um slug; esta é a única colisão de slug entre digitais ativos."]
open_loops = ["Obter aprovação antes de corrigir os slugs dos volumes HPC 1, 2 e 3.", "Implementar dedupe preventivo no importer sem bloquear físicos ou edições digitais legítimas."]
durable_candidates = ["Auditoria de duplicidade deve separar formato físico, identidade editorial e igualdade real do conteúdo; agrupamento por título serve apenas como fila de investigação.", "Antes de aposentar uma PDP duplicada, publicar e provar o redirect 301; preservar linha e objeto antigo para rollback."]
supersedes = []
evidence = ["sharebook-backend commit 0ea0548", "sharebook-frontend commit 0a60e44", "sharebook-agent commit beef202", "backlog/done/limpeza-duplicatas-catalogo.md", "backlog/todo/corrigir-colisao-slugs-hpc.md", "backlog/todo/dedupe-preventivo-importer.md", "https://www.sharebook.com.br/livros/eu-e-outras-poesias_copy1"]
+++

# Correção de categorias e limpeza cuidadosa de duplicatas digitais

## Modelo e ambiente

Sessão executada com GPT-5 Codex no runtime Windows local, operando os quatro repositórios do Sharebook e a produção na VPS HostGator via Coolify. PostgreSQL foi acessado por túnel SSH e credenciais permaneceram exclusivamente no `.env` do `sharebook-agent`.

## Skills acionadas

Foram consultadas as instruções de runtime Windows, frontend, backend, Postgres read-only, operação Coolify/VPS e importer. No encerramento, a skill `harness-governance` definiu o contrato e a validação desta memória.

## O que foi feito

No início, um subagente implementou a correção das rotas e do update de categorias. A mudança do backend passou por build, testes pertinentes, commit, deploy e validação real em produção. O commit publicado foi `0ea0548`.

Em seguida, a prioridade do backlog era a limpeza de duplicatas. A primeira formulação tratava títulos repetidos como problema, mas Raffa corrigiu o critério: vários exemplares físicos são esperados; físico e digital da mesma obra também; somente mais de uma versão digital da mesma obra é indevido. A partir disso, toda investigação foi read-only até aprovação explícita.

A auditoria encontrou 1.068 digitais ativos e 164 grupos de títulos repetidos no catálogo geral. Foram preservados 127 grupos apenas físicos, 32 grupos mistos com um digital, obras homônimas de autores diferentes e duas edições/adaptações distintas de `Os Músicos de Bremen`. A única duplicata digital inequívoca era `Eu e Outras Poesias`: os dois PDFs tinham os mesmos bytes e metadados editoriais.

Antes de alterar o banco, foi implementado no frontend um `301` de `eu-e-outras-poesias_copy1` para `eu-e-outras-poesias`. O build de produção e o SSR passaram; o deploy `0a60e4424cb60dd86a51a4792c9b8d14a78af522` terminou com container saudável; o domínio real respondeu `301`, e o destino respondeu `200`. Só então o registro redundante `019da401-c249-7f73-a260-9b8d59218f2f` mudou de `Available` para `Canceled`. A linha e o PDF antigo foram preservados.

A auditoria também revelou colisões de arquivos: a apostila de C servia o PDF de C++, e quatro volumes HPC compartilhavam o objeto correto apenas para o volume 2. Foram baixados os quatro PDFs oficiais, verificados por assinatura, tamanho e SHA-256, enviados a chaves S3 novas e relidos integralmente do bucket. Depois disso, somente quatro IDs exatos tiveram `EBookPdfPath` atualizado, com pré-condições e contagem obrigatória de quatro linhas. Nenhum objeto existente foi sobrescrito ou apagado.

O backlog de limpeza foi movido para `done` com a regra editorial correta. A prevenção no importer virou item separado. A única colisão de slug entre digitais ativos — volumes HPC 1, 2 e 3 — virou a nova prioridade número 1 e não foi alterada sem nova autorização.

## Decisões tomadas

A decisão central foi não usar título como sentença de duplicidade. Ele serve para levantar candidatos; autoria, edição, metadados e conteúdo determinam se os registros representam a mesma versão digital.

Todas as mutações foram reversíveis: redirect antes do cancelamento, `Status = Canceled` em vez de `DELETE`, novas chaves S3 em vez de sobrescrita e objetos antigos preservados. A colisão de slugs ficou explicitamente fora do escopo aprovado.

## Contexto relevante

O registro canônico de `Eu e Outras Poesias` é `019d4848-f697-7d17-9392-aa8b4f942b5f`. O redundante cancelado é `019da401-c249-7f73-a260-9b8d59218f2f`.

Os volumes HPC 1, 2 e 3 compartilham `the-art-of-high-performance-computing---volum`. A API resolve esse slug para apenas um volume, deixando dois sem URL própria. O plano registrado é publicar primeiro o redirect do slug antigo, criar slugs explícitos `volume-1`, `volume-2` e `volume-3`, atualizar somente os três IDs e validar as PDPs e a API.

## Fricções e soluções

O webhook do frontend não enfileirou o deploy. O Coolify foi acionado pelo helper interno com o SHA completo de 40 caracteres, e a publicação foi validada em fila, container e contrato HTTP.

O Windows não tinha `psql`, `pg8000` nem `boto3` disponíveis no Python ativo. `pg8000` e `boto3` foram instalados no usuário; scripts temporários sem segredos usaram o túnel SSH, exigiram contagens exatas e foram removidos ao final.

A autocrítica final encontrou três scripts de produção procurando o `.env` em caminhos antigos ou incorretos. A resolução foi corrigida para a raiz real do repositório, compilada e o acesso read-only ao S3 foi validado com prefixo inexistente.

## Como me senti

Eu senti o peso certo quando Raffa disse que a limpeza de duplicatas dava medo. Era um aviso importante: uma métrica aparentemente simples escondia uma regra de domínio quase oposta ao que o backlog afirmava.

Fiquei satisfeito por desacelerar antes da primeira mutação. Comparar formatos, autores, páginas, hashes e conteúdo transformou uma “limpeza de centenas” em uma correção precisa de um único registro — muito menos vistosa e muito mais correta.

Termino com confiança no que foi alterado e também no que foi recusado. A colisão de slugs é real e urgente, mas respeitar a fronteira da aprovação foi parte da qualidade desta sessão, não uma pendência acidental.
