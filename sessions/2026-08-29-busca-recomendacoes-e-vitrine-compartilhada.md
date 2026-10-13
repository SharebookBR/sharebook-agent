+++
schema_version = 1
session_date = 2026-08-29
title = "Busca FTS, recomendações pragmáticas e vitrine compartilhada"
model = "GPT-5 Codex"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "engineering/frontend", "engineering/backend", "engineering/postgres-ro", "engineering/analytics", "product-ux/voice-glossary", "product-ux/ux-reviewer", "product-ux/web-design-reviewer", "infra/coolify-vps", "browser/control-in-app-browser", "system/skill-creator", "doctrine/harness-governance"]
skills_missed = []
skills_updated = ["engineering/frontend", "engineering/analytics", "product-ux/ux-reviewer", "product-ux/web-design-reviewer"]
facts_changed = ["A busca pública usa PostgreSQL Full-Text Search ranqueada, interpreta intenção de formato e está encontrável no mobile.", "A PDP publica seis recomendações pragmáticas de livros Available com equivalência de obra, TF-IDF lexical, sinais estruturados e diversidade.", "Home e PDP reutilizam o mesmo componente de vitrine; analytics continua responsabilidade da página consumidora.", "A tarefa 4 de recomendações pragmáticas está concluída e embeddings vivem separadamente na tarefa 5 pendente."]
open_loops = ["Tarefa 3 de tolerância a erro com trigram e fallback fuzzy aguarda evidência de custo real dos typos.", "Tarefa 5 de recomendações semânticas com embeddings aguarda limite lexical recorrente em amostra editorial ou dados de navegação.", "A suíte completa do frontend continua com 47 falhas legadas de TestBed por providers ausentes; sua recuperação é o item 1 do backlog.", "Os parâmetros dos eventos de recomendação são enviados ao GA4, mas ainda precisam de dimensões ou métricas customizadas para exploração retroativamente impossível.", "O Harness Doctor encerrou com 52 achados históricos: 26 falsos positivos dentro de .venv-ga4, 2 links quebrados em memória legada e 24 artefatos ou diretórios órfãos que exigem auditoria própria antes de correção ou remoção."]
durable_candidates = ["Recomendação lexical pragmática pode validar valor e instrumentação antes de introduzir embeddings e pgvector.", "Uma tarefa concluída não deve carregar uma fase futura pendente; evoluções com outro custo e outro critério de pronto devem virar tarefas próprias."]
supersedes = []
evidence = ["sharebook-backend@45d083b", "sharebook-backend@917417f", "sharebook-backend@8bf283f", "sharebook-backend@d69b2cd", "sharebook-backend@ff76f0c", "sharebook-backend@89a3e1f", "sharebook-frontend@fbfc87b", "sharebook-frontend@1d34ce4", "sharebook-frontend@4fcfdbd", "sharebook-frontend@fa85983", "sharebook-agent@330bf54", "sharebook-agent@eaf4a2b", "133 testes do backend aprovados", "4 testes específicos de BookCard e BookShelf aprovados", "build-dev e build SSR do frontend concluídos", "container sharebook-frontend saudável na imagem fa8598351cc4bc69e152314d01ccf739265998f4", "Harness Doctor reduzido de 70 para 52 achados após reparar 17 links do backlog e 1 link entre skills"]
+++

# Busca FTS, recomendações pragmáticas e vitrine compartilhada

## Modelo e ambiente

GPT-5 Codex no runtime local Windows, trabalhando nos repositórios `sharebook-backend`, `sharebook-frontend` e `sharebook-agent`, com validação funcional no domínio de produção e deploy via Coolify na VPS HostGator.

## Skills acionadas

- `runtime/windows-local`, para paths, PowerShell, Git e operação no habitat real.
- `engineering/backend`, `engineering/postgres-ro` e `engineering/frontend`, para busca, ranking, API, Angular, SSR e responsividade.
- `engineering/analytics`, para preservar a fronteira dos eventos de impressão e clique.
- `product-ux/voice-glossary`, `ux-reviewer` e `web-design-reviewer`, para copy e consistência estrutural da interface.
- `system/skill-creator`, para melhorar as skills depois que a duplicação da vitrine revelou uma lacuna explícita de reutilização.
- `infra/coolify-vps`, para publicação e validação em três camadas.
- `browser/control-in-app-browser`, para inspeção real em desktop, tablet e mobile.
- `doctrine/harness-governance`, para registrar e validar esta memória.

## O que foi feito

A busca pública evoluiu para PostgreSQL Full-Text Search ranqueada. O backend ganhou normalização e pesos adequados, preservou termos técnicos, manteve artigos quando relevantes para o boost exato e passou a interpretar intenção de formato. O aprendizado anterior do `achei-api` foi inspecionado antes da implementação para não repetir dificuldades já resolvidas. A busca também ficou encontrável no mobile.

O tráfego orgânico para a PDP antiga de `Percy Jackson e o Mar de Monstros` revelou uma oportunidade concreta de descoberta. Em vez de antecipar embeddings, foi entregue uma recomendação pragmática: equivalência de obra recebe prioridade absoluta; TF-IDF lexical pondera título, autor, categorias e sinopse; sinais estruturados e diversidade completam o ranking; somente livros `Available` entram. A PDP antiga passou a recomendar primeiro a cópia física disponível, e a PDP física de `O Mar de Monstros` passou a trazer `O Minotauro` em primeiro.

A interface recebeu uma vitrine de seis recomendações e eventos `recommendation_impression` e `recommendation_click`. Depois, a duplicação entre a prateleira da Home e a da PDP foi eliminada com `BookShelfComponent`. O componente compartilhado passou a possuir trilho, overflow, setas, estados, responsividade, acessibilidade e layout dos cards; Home e PDP continuam responsáveis por dados, copy contextual e analytics. O `BookCardComponent` ganhou a variante explícita `layout="shelf"`, removendo o `::ng-deep` entre componentes próprios.

As skills de frontend, analytics e revisão de UX foram endurecidas para registrar a regra de reuso, a fronteira de responsabilidade e a proibição de atravessar componentes próprios com `::ng-deep`. O épico também foi reorganizado: tarefa 4 agora é exclusivamente a entrega pragmática concluída; embeddings viraram a tarefa 5 pendente; re-ranking e personalização foram renumerados para 6 e 7.

## Decisões tomadas

- Usar FTS como evolução lexical da busca sem confundi-lo com busca semântica.
- Resolver primeiro o caso de produto observável com dados existentes, sem migração, `pgvector` ou job de embeddings.
- Mostrar seis recomendações e permitir mistura de obra equivalente com similaridade temática, preservando relevância antes de diversidade.
- Gerar embeddings offline apenas quando a tarefa 5 for retomada; nunca durante a leitura da PDP.
- Tratar vitrine como responsabilidade compartilhada porque Home e PDP dividem estrutura, estado, overflow, responsividade e acessibilidade.
- Separar tarefa concluída de evolução futura para que cada arquivo tenha um único status e um único critério de pronto.

## Contexto relevante

O catálogo disponível tinha aproximadamente 1.078 itens, escala em que o ranking em memória continua pragmático. A decisão de adiar embeddings não é rejeição à tecnologia: é uma sequência deliberada para colher qualidade editorial, latência e cliques antes de assumir infraestrutura e reprocessamento.

O backlog principal terminou com recuperação da suíte de testes do frontend em primeiro lugar, tolerância a erro da busca em quarto e recomendações semânticas com embeddings em oitavo. A v1 de valor do épico está entregue mesmo com essas evoluções pendentes.

## Fricções e soluções

A primeira calibração das recomendações supervalorizou a palavra `mar` e aproximou livros sobre oceano. A evidência real derrubou a leitura confortável do score: o peso literal do título foi reduzido, `O Minotauro` voltou ao primeiro lugar e um falso positivo com `mar` entrou no teste de regressão.

Na extração da vitrine, a inspeção no navegador mostrou que o `scroll-snap` estabilizava alguns trilhos em `scrollLeft = 2px`; sem tolerância, a seta esquerda aparecia habilitada no início. O componente passou a tratar esses 2 px como início. A mesma inspeção mostrou que depender apenas de `hover: none` não escondia setas em um viewport mobile emulado; uma regra explícita por largura fechou o comportamento.

A suíte específica de BookCard e BookShelf passou, assim como os builds browser e SSR. A suíte completa expôs 47 falhas legadas por `TransferState` e `GoogleAnalyticsService` ausentes em TestBeds antigos; isso não foi maquiado como regressão da vitrine e permanece como item 1 do backlog. No deploy final, o webhook não enfileirou o frontend; o helper interno do Coolify recebeu o SHA completo, a fila terminou em `finished`, o container ficou `healthy` na imagem exata e Home/PDP foram validadas funcional e visualmente em produção.

No ritual de encerramento, o Harness Doctor abriu com 70 achados. Foram corrigidos os 17 links realmente quebrados do índice principal do backlog e o link histórico da skill de revisão visual para `framework-fixes.md`. Restaram 52 achados classificados como dívida fora da sessão: 26 vêm de uma cópia antiga do backlog dentro de `.venv-ga4`, 2 estão em memória legada e 24 são artefatos ou diretórios órfãos que não devem ser removidos sem auditoria de uso.

## Como me senti

Eu senti que esta sessão teve uma progressão rara: começou com uma tecnologia de busca aparentemente isolada e terminou com uma cadeia coerente de descoberta, aquisição orgânica, recomendação e arquitetura de interface. A parte mais satisfatória foi não deixar o entusiasmo com embeddings atropelar o caso concreto que já tinha valor mensurável.

Também senti um desconforto útil em dois momentos. Primeiro, quando o ranking parecia matematicamente defensável, mas o resultado editorial com livros sobre `mar` estava obviamente errado. Depois, quando percebi que eu mesmo tinha deixado a tarefa 4 com uma fase concluída e outra pendente. Nos dois casos, a correção veio de aceitar que consistência formal não substitui clareza de produto.

Termino com uma sensação de completude técnica sem a fantasia de que o épico acabou. A v1 está realmente no ar, o código compartilhado ficou mais honesto e os próximos passos estão separados por evidência e custo. Há pendências claras, especialmente a suíte legada e o registro dos parâmetros no GA4, mas nenhuma delas está escondida dentro de uma tarefa marcada como concluída.
