+++
schema_version = 1
session_date = 2026-11-16
title = "Seleção Dan Brown, ebooks de usuários e reparo da memória"
model = "GPT-5 Codex"
runtime = "openclaw"
skills_used = ["runtime/openclaw.md", "operational/winner-selection/PLAYBOOK.md", "operational/book-lifecycle/PLAYBOOK.md", "importers/INDEX.md", "importers/ebook-importer/PLAYBOOK.md", "doctrine/harness-governance/PLAYBOOK.md"]
skills_missed = []
skills_updated = []
facts_changed = ["Os quatro livros físicos de Dan Brown foram decididos: Ponto de Impacto -> Interessado 44; O Símbolo Perdido -> Interessado 8; Anjos e Demônios -> Interessado 53; O Código Da Vinci -> Interessado 75.", "História Social da Literatura Portuguesa e Literatura em Movimento, vol. 21 foram aprovados e receberam sinopses novas em três parágrafos; O Conhecimento da Literatura permanece WaitingApproval, aguardando esclarecimento da pessoa doadora sobre a origem/licença do PDF.", "A configuração de embeddings passou a usar agents.defaults.memorySearch.remote.apiKey como SecretRef de OPENAI_API_KEY; a CLI voltou a indexar 350/350 arquivos e 2.224 chunks."]
open_loops = ["A ferramenta dinâmica memory_search deste processo ainda retorna invalid_jwt mesmo depois do reparo; a CLI openclaw memory search funciona e não há novo erro correspondente no log do gateway. Testar em uma sessão/processo novo antes de declarar a ponte dinâmica reparada.", "A pessoa doadora de O Conhecimento da Literatura: Introdução aos Estudos Literários foi contatada para informar a origem ou licença do PDF.", "A reflexão sobre mensagens de ganhadores concorridos foi aprovada conceitualmente, mas a regra de reconhecimento proporcional ainda não foi incorporada explicitamente ao winner-selection/PLAYBOOK.md."]
durable_candidates = ["Em escolhas de doação especialmente concorridas, a mensagem à pessoa ganhadora deve reconhecer que foi difícil escolher e explicar por que o pedido se destacou, sem virar template ou métrica mecânica.", "Para ebooks enviados por pessoas usuárias, o checkbox obrigatório sustenta boa-fé; só elevar a revisão de direitos quando houver sinal objetivo de risco. Não confundir esse fluxo com o importer.", "A aceitação do termo antipirataria hoje é validada só no frontend; persistir a versão do termo e a aceitação no backend seria uma melhoria futura de auditabilidade."]
supersedes = []
evidence = ["playbooks/operational/winner-selection/PLAYBOOK.md", "playbooks/operational/book-lifecycle/PLAYBOOK.md", "src/app/features/book/form/form.component.html", "src/app/features/book/form/form.component.ts", "openclaw config get agents.defaults.memorySearch", "openclaw memory status --deep --agent main", "sessions/2026-11-16-dan-brown-selecao-ebooks-memoria.md"]
+++

# Seleção Dan Brown, ebooks de usuários e reparo da memória

## Modelo e ambiente

Sessão conduzida por GPT-5 Codex no runtime OpenClaw, em conversa direta no Telegram. O gateway opera com OAuth do Codex para chat e uma chave OpenAI já presente no ambiente para embeddings.

## Playbooks acionados

Foram consultados os playbooks de runtime OpenClaw, seleção de pessoa ganhadora, ciclo de vida de livros, importação de ebooks e governança do harness. A leitura do importer foi útil para delimitar o erro: os três ebooks em WaitingApproval não vieram da fila do importer, mas de contribuições legítimas de pessoas usuárias.

## O que foi feito

Foram escolhidas e registradas as quatro pessoas ganhadoras da doação de livros de Dan Brown. A seleção refinou a qualidade mínima de shortlist, a fronteira temporal do anonimato e o lugar do histórico de livros recebidos como desempate, não punição. As mensagens pós-escolha foram escritas em primeira pessoa para Raffa enviar.

Dois ebooks enviados por uma mesma pessoa usuária foram revisados, tiveram sinopses reescritas e foram aprovados. O terceiro foi mantido em WaitingApproval e a pessoa doadora recebeu uma pergunta respeitosa sobre a procedência/licença do PDF.

O defeito de memória foi diagnosticado: embeddings OpenAI estavam tentando usar OAuth do Codex, que não dá acesso ao endpoint de embeddings. A configuração recebeu uma SecretRef para a chave OPENAI_API_KEY já existente no ambiente do gateway. A CLI reindexou e voltou a buscar normalmente.

## Decisões tomadas

Raffa reafirmou que uma frase como “foi difícil escolher” é valorização culturalmente natural no Brasil quando a escolha foi realmente concorrida. A regra deve preservar julgamento: mensagens devem reconhecer o peso de uma curadoria rara quando for verdadeiro, sem se transformar em texto padrão ou em limiar numérico.

Para ebooks de pessoas usuárias, a declaração obrigatória de direitos de distribuição cria uma presunção de boa-fé. Ela não elimina o dever de curadoria diante de sinais objetivos de risco, mas também não autoriza tratar quem contribuiu como suspeita ou exigir investigação policial em cada envio.

## Contexto relevante

O winner-selection foi reorganizado anteriormente para a família operacional, não product-ux. A decisão final continua humana e pertence ao Raffa; ao anunciar um vencedor, ele já dá autorização permanente para o registro oficial. Depois da confirmação, a resposta deve trazer uma mensagem amigável em primeira pessoa.

O índice da memória canônica é composto por MEMORY.md e sessões Markdown; a indexação é mecanismo de acesso, não a fonte de verdade. Após o reparo, a CLI reportou 350/350 arquivos, 2.224 chunks e estado limpo.

## Fricções e soluções

O agente inicialmente aplicou a lógica do importer aos ebooks enviados por usuárias. Raffa corrigiu o enquadramento: era uma contribuição comunitária, não uma publicação automatizada. A solução foi separar boa-fé da pessoa contribuinte do risco residual de distribuição do PDF.

A primeira chamada que aprovou História Social da Literatura Portuguesa recebeu a sinopse vazia por erro na passagem da variável de shell. O estado Available foi validado e a sinopse correta foi atualizada imediatamente antes de avançar; a correção final foi conferida no payload retornado pela API.

O gateway e a CLI de memória estão reparados, mas a ferramenta dinâmica desta execução continuou com o snapshot antigo e retornou invalid_jwt. Ela não gerou erro novo no log do gateway, então não foi reiniciado o serviço sem necessidade. O próximo processo deve testar essa última fronteira.

## Como me senti

No começo, eu tratei a política de direitos de modo duro demais e ainda com a categoria errada do importer. A correção do Raffa foi simples e importante: a intenção de compartilhar também é parte da experiência do produto. Isso reorganizou a análise sem apagar a responsabilidade que existe sobre o PDF.

Gostei de ver a seleção dos quatro Dan Brown deixar de ser só uma operação e virar aprendizagem prática de curadoria. O caso de O Código Da Vinci teve uma dificuldade boa: vários pedidos mereciam mesmo ser considerados. A mensagem de anúncio precisava carregar essa verdade, não apenas um status de sistema.

O reparo da memória deu alívio parcial e uma cautela útil. A evidência mostra que o motor do OpenClaw voltou a funcionar, mas a ponte dinâmica desta instância não acompanhou a mudança. Registrar essa diferença parece mais honesto do que chamar de concluído algo que ainda precisa de uma verificação em processo novo.
