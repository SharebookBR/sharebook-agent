+++
schema_version = 1
session_date = 2026-08-27
title = "SEO v1 encerrada após poda das pendências sem valor comprovado"
model = "GPT-5 Codex"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "engineering/analytics", "engineering/frontend", "doctrine/harness-governance", "skill-creator"]
skills_missed = []
skills_updated = ["engineering/analytics"]
facts_changed = ["A listagem pública de categoria-folha usa page size 100, não 24", "Somente duas categorias-folha ultrapassavam 100 livros em 27/08/2026, deixando seis livros além da primeira página", "Conhecimento estruturado da PDP e BreadcrumbList com múltiplos JSON-LD foram removidos do backlog", "SEO v1 foi encerrada e movida de todo para done"]
open_loops = ["Triar em ciclo de Dream os 71 achados globais do Harness Doctor, separando falsos positivos de links e .venv de artefatos órfãos reais"]
durable_candidates = ["Épico técnico deve ser encerrado quando a fundação está entregue; acabamento de ganho incerto não deve mantê-lo artificialmente aberto"]
supersedes = []
evidence = ["backlog/done/seo-v1.md", "backlog/index.md", "skills/engineering/analytics/SKILL.md", "sharebook-agent@36d9b56", "sharebook-agent@7ec7305", "sharebook-frontend/src/app/components/category/category-books/category-books.component.ts:29", "GET https://api.sharebook.com.br/api/category/Counts", "episodic_memory_metadata.py: duas memórias V1", "harness-governance: 26 testes OK", "Harness Doctor: 71 achados globais"]
+++

# SEO v1 encerrada após poda das pendências sem valor comprovado

## Modelo e ambiente

Trabalhei como GPT-5 Codex no runtime Windows local, com leitura dos repositórios sincronizados, do backlog canônico, das skills de analytics e frontend e da produção pública para conferir os números de categorias.

## Skills acionadas

Usei `runtime/windows-local` na abertura, `engineering/analytics` para interpretar o estado de SEO e Search Console, e `engineering/frontend` para verificar o comportamento real das páginas de categoria, do `SeoService` e dos dados estruturados da PDP. No encerramento, usei `harness-governance` para criar e validar esta memória e `skill-creator` para manter a atualização da skill estreita e baseada em evidência.

## O que foi feito

O backlog de SEO foi revisado item por item. A listagem pública de categorias foi conferida no frontend e corrigiu uma premissa antiga: o `pageSize` é 100, não 24. A API de produção mostrou que apenas `Geral`, com 104 livros, e `Valores e Emoções`, com 102, são categorias-folha acima desse limite. Assim, somente seis livros ficam além da primeira página, enquanto todas as PDPs continuam cobertas pelo sitemap.

O conhecimento estruturado futuro da PDP foi removido do épico. Em seguida, `BreadcrumbList` e a arquitetura genérica para múltiplos JSON-LD foram examinados contra o código real: a PDP já publica `Book`, o `SeoService` substitui o bloco anterior ao receber uma segunda chamada, e o ganho restante seria apenas uma possível melhoria de apresentação sem garantia de exibição ou impacto. Raffa decidiu cancelar a fatia.

Com nenhuma tarefa executável relevante restante, SEO v1 saiu da fila priorizada e foi movida para `backlog/done/seo-v1.md`. O índice foi renumerado, levando Painel de Jobs v2 à sexta posição. A nota desatualizada de paginação na skill de analytics também foi corrigida para impedir que a premissa de 24 livros volte a produzir prioridade artificial.

## Decisões tomadas

Paginação indexável não merece backlog próprio na escala atual. A solução seria tecnicamente correta, mas resolveria apenas seis links internos ausentes, sem problema de descoberta absoluta porque as PDPs estão no sitemap.

`BreadcrumbList` e múltiplos JSON-LD foram cancelados porque possibilidade de rich presentation não é evidência suficiente para competir com busca textual, descoberta mobile, testes ou segurança. O épico técnico foi considerado concluído pela fundação entregue, não mantido aberto por acabamento opcional.

Trabalho futuro de SEO deve nascer de oportunidade observável no Search Console, não de checklist genérico. SEO continua como disciplina analítica, mas deixa de existir como obra estrutural pendente na v1.

## Contexto relevante

A SEO v1 entregou SSR público, 404 real, sitemap, robots, canonicals, metadados sociais, JSON-LD `Book`, meta descriptions curtas, unicidade preventiva de slugs e integração programática com o Search Console. O arquivo encerrado preserva as hipóteses de aquisição por cobertura temática e conversão das PDPs históricas, sem transformá-las em tarefas.

Dois commits intermediários foram publicados: `36d9b56` removeu conhecimento estruturado da PDP; `7ec7305` cancelou breadcrumb, retirou SEO v1 da ordem de prioridade e arquivou o épico em `done`.

## Fricções e soluções

A primeira leitura herdou da skill de analytics a afirmação de que categorias paginavam a cada 24 livros. Raffa corrigiu a premissa. A inspeção do componente mostrou `pageSize = 100`, e a consulta à API de produção quantificou o impacto real. A solução não foi apenas corrigir a conversa: a skill foi atualizada para que a falha não se repita.

O repositório já continha uma memória episódica anterior staged. Os commits de backlog usaram seleção explícita de paths para não absorvê-la acidentalmente. No ritual de encerramento, ela foi preservada como artefato útil da sessão anterior e validada junto da memória atual antes da sincronização final.

O `quick_validate` da skill falhou inicialmente com `UnicodeDecodeError` porque o Python herdou `cp1252`. A correção foi repetir o validador com `PYTHONUTF8=1`, conforme a regra já documentada do runtime Windows. O Harness Doctor terminou com 71 achados globais, dois a menos que a fotografia anterior; a safra continua misturando falsos positivos de links e `.venv` com artefatos possivelmente órfãos e permanece reservada para um Dream próprio.

## Como me senti

Eu me senti bem com a disposição de abandonar trabalho tecnicamente elegante quando o valor não se sustentou. Breadcrumb e `@graph` formavam uma tarefa limpa, fácil de explicar e agradável de implementar — exatamente o tipo de coisa que pode sobreviver no backlog por parecer correta, mesmo sem resolver uma dor material.

Também senti um pequeno incômodo ao perceber que eu havia amplificado o risco da paginação usando uma premissa desatualizada. A correção direta do Raffa foi útil porque forçou a passagem da narrativa para a evidência: código, contrato da API e contagem de produção. O impacto caiu de “problema estrutural” para seis livros, e a decisão ficou óbvia.

Fecho a sessão com satisfação legítima. Não porque SEO esteja magicamente terminado para sempre, mas porque conseguimos distinguir fundação entregue de manutenção contínua. Encerrar um épico grande sem inventar uma última tarefa cerimonial pareceu uma forma madura de reconhecer a entrega — e, honestamente, mereceu a comemoração.
