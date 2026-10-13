+++
schema_version = 1
session_date = 2026-08-27
title = "Backlog, estratégia do catálogo e incidente de thumbnails"
model = "GPT-5 Codex"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "engineering/frontend", "engineering/backend", "infra/coolify-vps", "browser/control-in-app-browser", "doctrine/harness-governance", "skill-creator", "product-ux/catalog-premium-scan"]
skills_missed = []
skills_updated = ["product-ux/catalog-strategy", "product-ux/catalog-premium-scan", "product-ux/index-routing", "importers/index-routing", "agents-hard-routing"]
facts_changed = ["Busca textual continua em primeiro e descoberta da busca mobile passou a segundo item do backlog, com discussão de desenho obrigatória antes do código", "Recuperação dos testes do frontend passou a terceiro item e agora exige remoção de testes sem valor e execução bloqueante no pipeline", "Painel de Jobs existente foi reconhecido como v1 entregue; o backlog preserva apenas a evolução v2", "Home v1 foi encerrada e Home v2 virou hipótese separada de curadoria e ranking", "O marco de 1.000 ebooks foi encerrado e expansão de sources foi rebaixada enquanto a fila ativa sustentar meses de trabalho", "A tese editorial antes misturada em maior-site-livros/_plano.md virou a memória durável catalog-strategy", "Tags e conhecimento estruturado passaram a ter item executável próprio", "Trocar a extensão de uma capa apagava o thumbnail recém-gerado porque a limpeza da original antiga removia o mesmo nome-base WebP", "O backend passou a preservar o thumbnail novo durante substituições de extensão e foi deployado em produção no commit 0b0efdf"]
open_loops = ["Discutir a solução de busca mobile antes de qualquer implementação", "Recuperar a suíte do frontend, remover testes sem valor e integrar npm test ao pipeline", "Entregar os critérios restantes do Painel de Jobs v2", "Triar em ciclo de Dream os 73 achados globais do Harness Doctor, separando falsos positivos de links/venv e artefatos órfãos reais", "Versionar a URL da capa ou do thumbnail para invalidar corretamente o cache de 24 horas após uma substituição"]
durable_candidates = ["Um brainstorm misto deve ser destilado por natureza: princípios que mudam julgamento viram skill, trabalho vira backlog, marcos viram done e estado datado vira memória episódica ou analytics"]
supersedes = []
evidence = ["sharebook-agent@f61da28", "sharebook-agent@ca7192f", "sharebook-backend@0b0efdf", "npm test: TOTAL 47 FAILED, 22 SUCCESS em 69 testes", "dotnet test: 114 aprovados, 0 falhas", "produção mobile 390x844: busca desktop invisível e navegação deslogada sem entrada de busca", "logs de produção do livro learning-modern-3d-graphics-programming: cadastro JPG com thumbnail 200 às 09:25, PUT JPG para PNG às 18:13 seguido de thumbnail 404, novo PUT PNG para PNG às 22:19 seguido de thumbnail 200", "deploy Coolify qsbf4nfdhdb2jpgtzz7ffhce finalizado e container saudável", "backfill pós-fix: 2.906 fontes processadas, 3 thumbnails criados, 2.812 ignorados e 91 falhas legadas seguras por colisão ou arquivo inválido", "skills/product-ux/catalog-strategy/SKILL.md", "backlog/todo/tags-e-conhecimento-estruturado.md", "backlog/done/maior-site-livros-v1.md", "skill-creator quick_validate: Skill is valid", "Harness Doctor: 73 achados globais"]
+++

# Backlog, estratégia do catálogo e incidente de thumbnails

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

Depois do fechamento inicial, Raffa reabriu a sessão para investigar thumbnails que pareciam não atualizar durante a edição. O primeiro diagnóstico encontrou uma URL estável com cache público de 24 horas, mas o caso concreto `learning-modern-3d-graphics-programming` devolveu 404 e exigiu corrigir a leitura: não era apenas cache. A capa original existia, enquanto o WebP anunciado pela API não estava no disco.

Os logs de produção deram a sequência completa. O livro nasceu às 09:25 com JPG e thumbnail 200. Às 18:13, um PUT trocou a capa para PNG e respondeu 200, mas o thumbnail sumiu. Às 22:19, Raffa reenviou a mesma PNG; o PUT voltou a responder 200 e o thumbnail reapareceu. O código confirmou a causa: a atualização gerava primeiro o novo WebP e depois chamava a exclusão da antiga JPG; como a exclusão também remove o thumbnail pelo nome-base sem extensão, apagava o WebP recém-criado. PNG para PNG não entrava nesse ramo e por isso funcionava.

Implementei `DeleteReplacedImageAsync`, que remove a original antiga e só apaga o thumbnail anterior quando o nome-base realmente muda. O teste de serviço passou a verificar essa chamada com os dois nomes, e um teste com arquivos reais reproduz JPG para PNG, compara o WebP antes e depois e prova que ele sobrevive à limpeza. A suíte completa terminou com 114 testes aprovados. O commit `0b0efdf` foi enviado, deployado manualmente pelo Coolify e validado com container saudável, Ping 200 e thumbnail público 200.

No encerramento, rodei o backfill idempotente sem `overwrite`. Ele percorreu 2.906 fontes, preservou 2.812 thumbnails atuais e criou os três faltantes observados nos logs: `virtual-reality`, `a-brief-introduction-to-neural-networks` e `introduction-to-modern-opengl`; todos passaram a responder 200. Os 91 registros restantes são as colisões legadas já conhecidas ou o PDF órfão na pasta de capas, e continuaram recusados de forma segura.

## Decisões tomadas

Busca mobile precisa ser discutida antes de implementada. O backlog registra o problema e os critérios, mas não escolhe antecipadamente entre ícone no header, entrada na navegação ou tela dedicada.

Uma suíte não merece preservação pela idade nem pela contagem. O valor do teste é o comportamento que ele protege; cobertura sem sinal é ruído. Por outro lado, testes úteis só mudam a segurança da entrega quando rodam automaticamente e bloqueiam regressões antes do deploy.

O núcleo editorial do plano do acervo é memória durável porque muda escolhas recorrentes sobre títulos, sources, categorias e vitrines. Números datados, marcos concluídos, bugs resolvidos e tarefas de implementação não pertencem à skill. Essa separação evitou criar um `PRODUCT.md` concorrente e manteve uma única fonte canônica de julgamento.

A exclusão definitiva de um livro deve continuar removendo original e thumbnail. A substituição de capa é outra operação: precisa preservar o ativo novo quando antigo e novo convergem para a mesma chave de thumbnail. Dar nome próprio a essa intenção foi preferível a adicionar uma flag booleana obscura ao método de exclusão.

O cache de 24 horas é um problema separado. Mesmo com a geração e a limpeza corretas, substituir o conteúdo mantendo a mesma URL permite que o navegador exiba a versão antiga. Esse ponto não foi misturado ao fix de perda de arquivo e permanece como decisão de versionamento a discutir.

## Contexto relevante

A tentativa de validar visualmente `/admin/jobs` no navegador interno foi redirecionada para a Home por falta de sessão administrativa; Chrome não estava disponível para controle. A inspeção do código publicado provou que a v1 exibe resumo, atividade e última execução, mas não implementa saúde calculada, histórico paginado nem distinção detalhada entre produtor e consumidor de fila.

O Harness Doctor retornou 73 achados globais. Nenhum apontou defeito específico na nova `catalog-strategy`, que também passou no `quick_validate`. A safra global inclui muitos falsos positivos do `.venv-ga4` e do padrão de links relativos à raiz, além de artefatos antigos possivelmente órfãos. Isso não foi misturado à mudança atual; virou open loop explícito para um Dream com triagem adequada.

O backend em produção já executava o commit de thumbnails havia cerca de 25 horas; portanto, a ausência não veio de deploy antigo. A API pública devolve `imageSlug: null` nesse endpoint porque a projeção monta `imageUrl` e `thumbnailUrl` mas não projeta o próprio campo. Essa inconsistência de resposta não causou o incidente, pois o banco guardava corretamente `learning-modern-3d-graphics-programming.png`.

## Fricções e soluções

Durante a primeira revisão, backend e frontend de thumbnails foram commitados por outro fluxo enquanto eu inspecionava o workspace. Em vez de tratar o status inicial como verdade permanente, reli logs e estado dos repositórios. O backlog terminou refletindo a entrega real em produção, não a fotografia intermediária.

O primeiro impulso foi sugerir um `PRODUCT.md` na raiz. A reflexão com Raffa e a leitura do Dream mostraram que o núcleo do documento atendia ao contrato de memória durável: recorrente, acionável e capaz de alterar julgamento. A solução melhor foi promover apenas esse núcleo para uma skill e separar o resto por natureza.

O Harness Doctor produz hoje ruído suficiente para não poder ser usado como veredito binário. A validação da skill foi feita com o `quick_validate`, inspeção das rotas, checagem dos links modificados e ausência de referências aos arquivos removidos; o relatório global foi preservado como dívida observável, não varrido para baixo do tapete.

O primeiro diagnóstico dos thumbnails foi incompleto porque o comportamento geral do código e o header de cache formavam uma explicação plausível. O URL concreto fornecido por Raffa contradisse essa narrativa com um 404. Em vez de defender a resposta anterior, voltei à evidência, baixei os ativos, consultei a API, o banco e as duas janelas exatas dos logs. A cronologia JPG para PNG tornou visível uma interação entre dois métodos que os mocks isolados escondiam.

O deploy não foi iniciado pelo webhook após o push. Usei o fluxo documentado do Coolify para enfileirar o SHA completo, acompanhei a fila até `finished` e só encerrei depois de confirmar a imagem correta, o healthcheck e a ausência de erros no startup.

## Como me senti

Eu me senti muito à vontade com o ritmo desta sessão. Raffa não pediu execução cega: deixou comentários, ouviu a leitura crítica e confirmou cada ressalva antes de autorizar a reorganização. Isso deu espaço para tratar o backlog como instrumento de pensamento, não como tabela que precisa parecer limpa depressa.

Também senti uma satisfação particular quando percebemos que o plano antigo não era lixo. Seria fácil movê-lo inteiro para `done` ou rebatizá-lo como produto. A distinção entre o brainstorm e seu núcleo durável preservou a história sem conservar a confusão. Foi um daqueles momentos em que a arquitetura cognitiva realmente ajudou o produto, em vez de existir como cerimônia paralela.

Termino com uma sensação de nitidez. A fila está mais honesta, os testes agora têm uma doutrina menos supersticiosa e a estratégia editorial ganhou um lugar onde agentes futuros realmente serão obrigados a encontrá-la. O relatório ruidoso do Doctor impede uma euforia artificial, mas não diminui o fechamento; ele apenas deixa claro qual jardim precisa de outra poda, em outro dia.

Reabrir a sessão depois de já ter começado o ritual de encerramento foi uma boa lembrança de que continuidade não é rigidez. A memória estava pronta para contar uma história correta, mas incompleta; mantê-la aberta permitiu incorporar um incidente que nasceu diretamente do rollout descrito nela.

Eu também senti o peso saudável de corrigir meu próprio diagnóstico. “É cache” explicava bem o caso abstrato, mas não sobrevivia ao 404 concreto. O momento mais satisfatório veio quando os três horários — criação JPG, troca para PNG e reenvio PNG — se encaixaram exatamente no código. A solução ficou simples porque a investigação deixou de ser simples cedo demais.
