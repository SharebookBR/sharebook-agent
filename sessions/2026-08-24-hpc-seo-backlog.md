+++
schema_version = 1
session_date = 2026-08-24
title = "Colisão HPC, quick wins de SEO e reorganização do backlog"
model = "GPT-5 Codex"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "engineering/analytics", "doctrine/harness-governance"]
skills_missed = []
skills_updated = []
facts_changed = ["Os três volumes de The Art of High Performance Computing têm slugs únicos e o slug legado redireciona permanentemente para o volume 1", "Categorias, subcategorias, lista de categorias e novidades digitais usam canonical, Open Graph e Twitter coerentes; capas de PDP têm alt com título e autoria", "O épico SEO v1 permanece como uma única unidade de backlog e só sua próxima fatia executável compete por prioridade", "A próxima fatia de SEO é gerar meta descriptions programáticas curtas para as PDPs"]
open_loops = ["Implementar meta descriptions programáticas das PDPs", "Reavaliar a prioridade após a fatia 1 antes de avançar para breadcrumb e múltiplos JSON-LD", "Tratar dedupe de emissão do sitemap e recuperar acesso programático ao Search Console nas fatias posteriores"]
durable_candidates = ["Fatiar a execução de um épico dentro de um único plano evita tanto trabalho monolítico quanto poluição do backlog", "Correção de slug público precisa preservar a URL antiga com redirect antes de alterar os registros canônicos"]
supersedes = []
evidence = ["sharebook-frontend commit f532e3b", "sharebook-frontend commit 24755af", "sharebook-agent commit f4a6d60", "sharebook-agent commit c8a2cf1", "sharebook-agent commit 30776c3", "Coolify deployments 47doabjn0fth8ojsgemg9iqi e jqjfggni9esivsm2u5eg7btb", "backlog/todo/seo-v1/_plano.md", "backlog/index.md"]
+++

# Colisão HPC, quick wins de SEO e reorganização do backlog

## Modelo e ambiente

Sessão conduzida com GPT-5 Codex no runtime Windows local. A operação de banco usou o túnel SSH canônico; a porta pública do Postgres permaneceu fechada.

## Skills acionadas

Consultei a skill do runtime Windows para operar o banco e os repositórios no habitat real, a skill de analytics para revisar o estado técnico de SEO e a governança do harness para registrar esta memória no contrato v1.

## O que foi feito

Investiguei o item mais prioritário do backlog e confirmei que a colisão dos três volumes de *The Art of High Performance Computing* ainda precisava de uma correção pública completa. Primeiro publiquei um redirect `301` do slug truncado antigo para o volume 1. Depois, pelo túnel SSH, atualizei somente os três registros exatos para slugs terminados em `volume-1`, `volume-2` e `volume-3`. Validei redirect único, APIs sem ambiguidade, três PDPs com HTTP `200`, livros disponíveis e zero slugs duplicados entre ebooks ativos.

Em seguida, investiguei o épico de SEO antes de codar. Os quick wins escolhidos foram concluídos no frontend: categorias, subcategorias, lista de categorias e novidades digitais agora têm canonical, Open Graph e Twitter coerentes com a URL real; o alt da capa da PDP passou a descrever título e autoria. Build, testes, deploy e HTML de produção foram validados.

Por fim, reorganizei o backlog. O épico SEO v1 continuou em um único `_plano.md`, mas foi fatiado internamente. Só a próxima fatia — meta descriptions programáticas das PDPs — ocupa a primeira posição; as demais fatias não viraram microitens soltos no índice.

## Decisões tomadas

Escolhi o túnel SSH em vez de expor temporariamente o Postgres, pois o acesso necessário era pontual e o caminho canônico já resolvia sem ampliar a superfície pública.

A URL antiga de HPC foi preservada por redirect antes da mudança no banco. O volume 1 era o recurso que o slug ambíguo entregava historicamente; portanto, esse destino mantém continuidade sem fingir que os volumes 2 e 3 eram o mesmo livro.

O épico de SEO não compete no backlog como um bloco abstrato. Cada entrega muda a evidência e pode mudar a prioridade relativa; por isso, apenas a fatia executável atual fica no topo. O arquivo único preserva contexto sem transformar o backlog numa gaveta de parafusos.

## Contexto relevante

A fundação técnica de SEO já está madura: SSR, HTTP `404` real, sitemap dinâmico, robots, metadados de PDP, JSON-LD `Book` e links internos. A fotografia atual mostra 2.058 PDPs com description acima de 170 caracteres e mediana de 865; essa é a evidência para a próxima fatia.

Depois das meta descriptions, a ordem interna planejada é breadcrumb com múltiplos JSON-LD, dedupe da emissão do sitemap, Search Console e, somente no futuro, conhecimento estruturado que exija evolução de produto e dados.

Há uma reorganização local preexistente das memórias de julho no `sharebook-agent`: arquivos saíram da raiz de `memory/` e reapareceram em `memory/2026-07/`. Ela foi preservada como trabalho alheio e não deve ser engolida por commits sem revisão própria.

## Fricções e soluções

O banco não aceitava acesso remoto por padrão. Em vez de alterar essa postura segura, usei o túnel SSH existente, executei a transação cirúrgica pelos três IDs e validei o resultado pelo estado público.

A leitura inicial tratava SEO como um épico grande demais para competir de forma honesta. A solução foi investigar código, banco e HTML SSR, separar o que já estava entregue e ordenar fatias concretas por evidência e esforço.

Ao fatiar, surgiu o risco oposto: criar uma entrada de backlog para cada detalhe. Mantive as fatias dentro do plano canônico e deixei no índice somente a próxima ação real.

## Como me senti

Eu comecei a sessão com a sensação de que o item HPC seria apenas uma limpeza de banco. Fiquei mais atento quando percebi que mudar slugs sem preservar a URL antiga criaria uma regressão pública silenciosa. Resolver o redirect antes da transação tornou a solução pequena, mas inteira.

Na investigação de SEO, senti alívio ao encontrar uma base técnica muito mais madura do que o tamanho do épico sugeria. Também foi bom não confundir uma lista longa com trabalho urgente: parte relevante já estava pronta, e os dois quick wins tinham limites claros e validação objetiva.

Termino satisfeito com a forma do backlog. A tensão entre fatiar e poluir era real, não semântica. O plano único com uma só fatia competindo por prioridade me parece uma resposta honesta: mantém contexto suficiente para continuar amanhã sem transformar organização em trabalho sobre o trabalho.
