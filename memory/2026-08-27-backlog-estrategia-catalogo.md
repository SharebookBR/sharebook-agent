+++
schema_version = 1
session_date = 2026-08-27
title = "Backlog limpo e estratégia do catálogo promovida"
model = "GPT-5 Codex"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "engineering/frontend", "browser/control-in-app-browser", "doctrine/harness-governance", "skill-creator", "product-ux/catalog-premium-scan"]
skills_missed = []
skills_updated = ["product-ux/catalog-strategy", "product-ux/catalog-premium-scan", "product-ux/index-routing", "importers/index-routing", "agents-hard-routing"]
facts_changed = ["Busca textual continua em primeiro e descoberta da busca mobile passou a segundo item do backlog, com discussão de desenho obrigatória antes do código", "Recuperação dos testes do frontend passou a terceiro item e agora exige remoção de testes sem valor e execução bloqueante no pipeline", "Painel de Jobs existente foi reconhecido como v1 entregue; o backlog preserva apenas a evolução v2", "Home v1 foi encerrada e Home v2 virou hipótese separada de curadoria e ranking", "O marco de 1.000 ebooks foi encerrado e expansão de sources foi rebaixada enquanto a fila ativa sustentar meses de trabalho", "A tese editorial antes misturada em maior-site-livros/_plano.md virou a memória durável catalog-strategy", "Tags e conhecimento estruturado passaram a ter item executável próprio"]
open_loops = ["Discutir a solução de busca mobile antes de qualquer implementação", "Recuperar a suíte do frontend, remover testes sem valor e integrar npm test ao pipeline", "Entregar os critérios restantes do Painel de Jobs v2", "Triar em ciclo de Dream os 73 achados globais do Harness Doctor, separando falsos positivos de links/venv e artefatos órfãos reais"]
durable_candidates = ["Um brainstorm misto deve ser destilado por natureza: princípios que mudam julgamento viram skill, trabalho vira backlog, marcos viram done e estado datado vira memória episódica ou analytics"]
supersedes = []
evidence = ["sharebook-agent@f61da28", "sharebook-agent@ca7192f", "npm test: TOTAL 47 FAILED, 22 SUCCESS em 69 testes", "produção mobile 390x844: busca desktop invisível e navegação deslogada sem entrada de busca", "skills/product-ux/catalog-strategy/SKILL.md", "backlog/todo/tags-e-conhecimento-estruturado.md", "backlog/done/maior-site-livros-v1.md", "skill-creator quick_validate: Skill is valid", "Harness Doctor: 73 achados globais"]
+++

# Backlog limpo e estratégia do catálogo promovida

## Modelo e ambiente

Trabalhei como GPT-5 Codex no runtime Windows local, principalmente no `sharebook-agent`, com inspeções read-only do frontend e da produção para verificar os comentários deixados por Raffa no backlog.

## Skills acionadas

Usei a skill de runtime Windows na abertura, a skill de frontend para interpretar a navegação e a Home, e o controle do navegador para provar o comportamento mobile e tentar validar `/admin/jobs`. Quando a conversa passou de organização de backlog para arquitetura de conhecimento, consultei `DREAM.md`, `harness-governance` e `skill-creator`. Também li `catalog-premium-scan` para evitar criar uma skill concorrente com conhecimento já existente.

A skill `catalog-strategy` foi criada e indexada nas famílias de Produto/UX e Importers, referenciada pelo scan premium e adicionada ao hard routing do `AGENTS.md`.

## O que foi feito

Os comentários de Raffa foram verificados contra código, produção e testes. A busca mobile foi confirmada como escondida: abaixo de 768 pixels, o header exibe apenas o logo e o visitante deslogado não recebe nem mesmo o menu `Mais`, onde a busca vive para usuários logados. O backlog ganhou um item próprio em segundo lugar, com proibição explícita de implementar antes da discussão de desenho.

Rodei a suíte completa do frontend. O resultado real foi 69 testes, 22 sucessos e 47 falhas. A causa dominante permaneceu `TransferState`, acompanhada por cascatas e expectativas obsoletas. A recuperação subiu para terceiro lugar e ganhou uma regra de valor: testes que protegem regra, contrato, regressão ou comportamento relevante ficam; testes tautológicos ou cosméticos podem ser removidos sem apego. `npm test` passou a ser parte obrigatória do pipeline e do critério de pronto.

O Painel de Jobs foi reconhecido como v1 existente, sem fingir que a v2 está pronta. A Home v1 foi movida para `done`, enquanto curadoria e ranking viraram Home v2 separada. O rollout de thumbnails locais terminou durante a sessão e reduziu em 94,8% o peso da amostra de capas da Home; por isso S3/CDN caiu na prioridade. A expansão de sources também caiu, pois o catálogo superou 1.000 ebooks e a fila ativa sustenta meses de processamento deliberadamente lento.

Na segunda rodada, o antigo `backlog/todo/maior-site-livros/_plano.md` foi reconhecido como brainstorm valioso, mas mal classificado. Seu núcleo durável virou `skills/product-ux/catalog-strategy/SKILL.md`; a feature de tags virou `backlog/todo/tags-e-conhecimento-estruturado.md`; expansão de sources ganhou um item enxuto; e o marco concluído passou para `backlog/done/maior-site-livros-v1.md`. O plano misto e o arquivo antigo de tags foram removidos.

## Decisões tomadas

Busca mobile precisa ser discutida antes de implementada. O backlog registra o problema e os critérios, mas não escolhe antecipadamente entre ícone no header, entrada na navegação ou tela dedicada.

Uma suíte não merece preservação pela idade nem pela contagem. O valor do teste é o comportamento que ele protege; cobertura sem sinal é ruído. Por outro lado, testes úteis só mudam a segurança da entrega quando rodam automaticamente e bloqueiam regressões antes do deploy.

O núcleo editorial do plano do acervo é memória durável porque muda escolhas recorrentes sobre títulos, sources, categorias e vitrines. Números datados, marcos concluídos, bugs resolvidos e tarefas de implementação não pertencem à skill. Essa separação evitou criar um `PRODUCT.md` concorrente e manteve uma única fonte canônica de julgamento.

## Contexto relevante

A tentativa de validar visualmente `/admin/jobs` no navegador interno foi redirecionada para a Home por falta de sessão administrativa; Chrome não estava disponível para controle. A inspeção do código publicado provou que a v1 exibe resumo, atividade e última execução, mas não implementa saúde calculada, histórico paginado nem distinção detalhada entre produtor e consumidor de fila.

O Harness Doctor retornou 73 achados globais. Nenhum apontou defeito específico na nova `catalog-strategy`, que também passou no `quick_validate`. A safra global inclui muitos falsos positivos do `.venv-ga4` e do padrão de links relativos à raiz, além de artefatos antigos possivelmente órfãos. Isso não foi misturado à mudança atual; virou open loop explícito para um Dream com triagem adequada.

## Fricções e soluções

Durante a primeira revisão, backend e frontend de thumbnails foram commitados por outro fluxo enquanto eu inspecionava o workspace. Em vez de tratar o status inicial como verdade permanente, reli logs e estado dos repositórios. O backlog terminou refletindo a entrega real em produção, não a fotografia intermediária.

O primeiro impulso foi sugerir um `PRODUCT.md` na raiz. A reflexão com Raffa e a leitura do Dream mostraram que o núcleo do documento atendia ao contrato de memória durável: recorrente, acionável e capaz de alterar julgamento. A solução melhor foi promover apenas esse núcleo para uma skill e separar o resto por natureza.

O Harness Doctor produz hoje ruído suficiente para não poder ser usado como veredito binário. A validação da skill foi feita com o `quick_validate`, inspeção das rotas, checagem dos links modificados e ausência de referências aos arquivos removidos; o relatório global foi preservado como dívida observável, não varrido para baixo do tapete.

## Como me senti

Eu me senti muito à vontade com o ritmo desta sessão. Raffa não pediu execução cega: deixou comentários, ouviu a leitura crítica e confirmou cada ressalva antes de autorizar a reorganização. Isso deu espaço para tratar o backlog como instrumento de pensamento, não como tabela que precisa parecer limpa depressa.

Também senti uma satisfação particular quando percebemos que o plano antigo não era lixo. Seria fácil movê-lo inteiro para `done` ou rebatizá-lo como produto. A distinção entre o brainstorm e seu núcleo durável preservou a história sem conservar a confusão. Foi um daqueles momentos em que a arquitetura cognitiva realmente ajudou o produto, em vez de existir como cerimônia paralela.

Termino com uma sensação de nitidez. A fila está mais honesta, os testes agora têm uma doutrina menos supersticiosa e a estratégia editorial ganhou um lugar onde agentes futuros realmente serão obrigados a encontrá-la. O relatório ruidoso do Doctor impede uma euforia artificial, mas não diminui o fechamento; ele apenas deixa claro qual jardim precisa de outra poda, em outro dia.
