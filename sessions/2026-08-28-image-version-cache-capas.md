+++
schema_version = 1
session_date = 2026-08-28
title = "Versionamento de URLs de capas"
model = "GPT-5 Codex"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "engineering/backend", "infra/coolify-vps", "doctrine/harness-governance"]
skills_missed = []
skills_updated = []
facts_changed = ["Book passou a persistir ImageVersion com valor inicial 1", "Trocar a capa incrementa ImageVersion; editar apenas texto preserva a versão", "URLs públicas da capa original e do thumbnail passaram a carregar ?v=N", "A migration inicializou os 2.734 livros existentes com ImageVersion 1", "O endpoint público por slug passou também a projetar imageSlug corretamente"]
open_loops = ["Avaliar futuramente se o microcache SSR de até 30 minutos da Home também deve ser invalidado imediatamente após troca de capa"]
durable_candidates = ["Ativos mutáveis servidos com cache longo devem manter cache agressivo e trocar a chave pública por uma versão persistida quando o conteúdo mudar"]
supersedes = ["memory/2026-08-27-backlog-estrategia-catalogo.md#open-loop-versionar-url-da-capa-ou-thumbnail"]
evidence = ["sharebook-backend@79cc0ccd32378ab12a3349225a9bb8f2d8b7d040", "migration 20260828103104_AddBookImageVersion", "dotnet test unit: 115 aprovados, 0 falhas", "dotnet test integration: 23 aprovados, 0 falhas", "dotnet build Release: 0 erros", "dotnet ef migrations has-pending-model-changes: nenhuma mudança pendente", "Coolify deployment sz5rtfagx1hsbt8bkvyha4wx: finished", "container sharebook-api no SHA exato e healthy", "produção: /api/book/Slug/learning-modern-3d-graphics-programming retornou imageVersion 1 e URLs ?v=1", "produção: 2.734 Books agrupados em ImageVersion 1", "thumbnail público ?v=1: HTTP 200 e Cache-Control public,max-age=86400"]
+++

# Versionamento de URLs de capas

## Modelo e ambiente

Trabalhei como GPT-5 Codex no runtime Windows local, principalmente no backend e na produção do Sharebook. A sessão continuou a investigação anterior sobre thumbnails e tratou o problema remanescente de cache após a troca de uma capa.

## Skills acionadas

Usei a skill de runtime Windows para operar no habitat correto, a skill de backend para seguir o contrato de persistência e validação, e o playbook do Coolify para publicar e provar o SHA exato em produção. No fechamento, usei `harness-governance` para criar e validar esta memória episódica.

## O que foi feito

Implementei `ImageVersion` como propriedade persistida de `Book`, inicializada em 1 e configurada com default 1 no PostgreSQL. A migration `20260828103104_AddBookImageVersion` adicionou a coluna sem exigir backfill manual; em produção, os 2.734 livros existentes ficaram na versão 1.

O fluxo de atualização agora incrementa a versão apenas quando há uma nova capa. Alterações textuais não mudam o valor. Os contratos públicos e administrativos receberam `ImageVersion`, e o serviço de upload passou a acrescentar `?v=N` às URLs da imagem original e do thumbnail. Home, busca, detalhe do livro e dashboard do importer foram ajustados para usar a mesma regra. A projeção pública de busca também passou a carregar `ImageSlug`, corrigindo a inconsistência observada durante o incidente anterior.

Adicionei testes para a composição exata da URL, preservação da versão em edição textual, incremento na troca da capa e URLs versionadas na Home. A suíte terminou com 115 testes unitários e 23 de integração aprovados. O build Release teve zero erros e o Entity Framework confirmou que o modelo não possuía mudanças pendentes após a migration.

O commit `79cc0ccd32378ab12a3349225a9bb8f2d8b7d040` foi enviado ao GitHub e enfileirado no Coolify. O deploy `sz5rtfagx1hsbt8bkvyha4wx` terminou como `finished`; o container subiu com a imagem do SHA exato e ficou saudável. A API pública devolveu `imageVersion: 1`, `imageSlug` preenchido e URLs terminadas em `?v=1`. O thumbnail continuou com cache público de 24 horas e respondeu HTTP 200, confirmando que a invalidação acontece pela troca da chave da URL, sem sacrificar o cache do ativo.

## Decisões tomadas

Escolhemos versionamento de URL em vez de tentar purgar caches intermediários. O conteúdo continua imutável do ponto de vista de cada URL individual, enquanto uma troca de capa cria uma nova identidade pública por meio do parâmetro `v`. Isso funciona no navegador, em proxies e em futuras CDNs sem acoplamento a um fornecedor específico.

A versão pertence ao livro e não ao nome físico do arquivo. Assim, mesmo quando a extensão e o slug permanecem iguais, uma nova capa produz uma URL diferente. O incremento fica restrito à atualização real da imagem para evitar churn de cache em edições de título, autor ou descrição.

Não foi necessária mudança no frontend. Ele já consome as URLs devolvidas pela API; mudar a composição no backend resolveu todos os consumidores sem duplicar regra de versionamento no cliente.

## Contexto relevante

O cache estático de 24 horas continua deliberadamente ativo. A correção não apaga o objeto antigo do cache: ela torna a versão anterior inalcançável pelo fluxo normal porque a API passa a anunciar uma nova URL.

A Home renderizada no servidor ainda possui um microcache próprio de até 30 minutos. A API oferece a nova versão imediatamente, mas uma página SSR já armazenada pode manter a URL anterior durante essa janela. Isso não invalida a solução do ativo e ficou registrado como avaliação futura separada.

## Fricções e soluções

O scaffold da migration exigiu alternar temporariamente a configuração de design-time para PostgreSQL com uma conexão fictícia. O arquivo de configuração foi restaurado logo depois, e o status do Git confirmou que nenhuma configuração temporária permaneceu no commit.

Um teste de URL falhou inicialmente porque a fixture usava um caminho absoluto temporário para `ImagePath`, fazendo esse caminho aparecer na URL esperada. A produção usa `wwwroot/Images`; corrigi a fixture para representar o contrato real e a suíte passou integralmente. A falha revelou um erro no arranjo do teste, não no código de produção.

O webhook não iniciou o deploy logo após o push. Segui o playbook do Coolify, enfileirei explicitamente o SHA completo, acompanhei a fila até `finished` e só declarei a entrega depois de validar container, logs, banco, endpoint público e header do thumbnail.

Durante uma checagem em PowerShell, usei sem perceber `$home` como variável; como nomes são case-insensitive, isso tentou sobrescrever a variável protegida `$HOME`. O comando falhou sem alterar estado. Refiz a inspeção com um nome específico, `$catalogPayload`, e obtive a evidência esperada. É uma lembrança concreta para não usar nomes genéricos reservados nem mesmo em comandos descartáveis.

## Como me senti

Eu me senti satisfeito porque a solução fechou a sequência inteira do incidente anterior. Primeiro garantimos que o thumbnail não fosse apagado durante a troca de extensão; agora garantimos que um thumbnail corretamente substituído seja realmente percebido pelo usuário. As duas falhas pareciam uma só na superfície, mas exigiam correções independentes.

Também senti confiança na escolha técnica. Purgar cache costuma virar uma coleção de integrações frágeis e comportamentos diferentes por camada. A versão persistida deixa a regra simples: conteúdo novo, identidade nova. É uma solução pequena, visível no payload e fácil de provar.

O quase-erro com `$HOME` foi incômodo justamente porque havia uma regra explícita para evitá-lo. Não causou dano, mas reforçou que disciplina operacional também vale em comandos de leitura e scripts efêmeros. Fiquei aliviado por a falha ter sido imediata e transparente, e por ter corrigido o comando sem esconder a fricção da memória.

Termino com sensação de completude. O código, a migration, os testes, o deploy e a evidência pública contam a mesma história. Restou apenas uma nuance honesta, o microcache SSR da Home, registrada como escolha futura em vez de ser misturada artificialmente à entrega concluída.
