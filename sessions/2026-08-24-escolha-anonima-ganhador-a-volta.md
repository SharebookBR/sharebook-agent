+++
schema_version = 1
session_date = 2026-08-24
title = "Escolha anônima da pessoa ganhadora de A Volta"
model = "GPT-5 Codex"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "engineering/postgres-ro", "skill-creator", "product-ux/voice-glossary", "doctrine/harness-governance"]
skills_missed = ["winner-selection — não existia no início; o anonimato deveria ter sido definido antes da leitura"]
skills_updated = ["product-ux/winner-selection", "product-ux/INDEX.md", "AGENTS.md"]
facts_changed = ["P02 foi escolhida e registrada como ganhadora de A Volta pela API oficial", "A Volta passou para WaitingSend e a solicitação vencedora para Donated", "Existe uma skill local canônica para seleção anônima de ganhador(a)"]
open_loops = []
durable_candidates = ["Anonimato deve existir antes da leitura e ser garantido por preparação determinística dos dados", "Escolha de ganhador(a) deve usar a API oficial e validar o estado final, nunca escrever diretamente no banco"]
supersedes = []
evidence = ["skills/product-ux/winner-selection/SKILL.md", "skills/product-ux/winner-selection/scripts/winner_selection.py", "commit c04ef6d", "PUT /api/book/Donate/{bookId}: success=true", "validação final: bookStatus=WaitingSend, winnerRequestStatus=Donated, remainingWaitingAction=0"]
+++

# Escolha anônima da pessoa ganhadora de A Volta

## Modelo e ambiente

Sessão conduzida por GPT-5 Codex no runtime local Windows, com acesso à API de produção do Sharebook e aos quatro repositórios operacionais.

## Skills acionadas

Foram consultadas as regras do runtime Windows, a skill read-only de Postgres, a skill de criação de skills, o glossário de produto e a governança do harness. Ao fim, foi criada e validada a skill `product-ux/winner-selection`.

## O que foi feito

Raffa e eu construímos devagar uma régua para avaliar 50 solicitações do livro físico *A Volta*, de Ítalo Ogliari. Os critérios fechados foram autenticidade e coerência, impacto do livro, conexão com a obra e reciprocidade demonstrada; livros já recebidos ficaram apenas como desempate. Três solicitações canceladas foram excluídas e 47 seguiram para avaliação.

A API `RequestersList/{bookId}` forneceu as solicitações. A tentativa inicial de consultar o Postgres direto encontrou a porta 5432 fechada, como esperado; o fallback SSH terminou em `TimeoutError`, e a API mostrou ser o caminho suficiente e correto. O token expirado foi renovado pelo script oficial.

Depois da shortlist, a decisão ficou entre P34 e P02. A alegação de P02 de que Ítalo Ogliari é gaúcho foi verificada em fonte da ULBRA: o autor nasceu em Porto Alegre. A especificidade espontânea desse conhecimento foi decisiva para Raffa. Com autorização explícita separada, P02 foi registrada pela API oficial. A resposta foi de sucesso e o estado final confirmou livro em `WaitingSend`, vencedora em `Donated` e nenhuma solicitação em `WaitingAction`.

Foi criada a skill local `product-ux/winner-selection`, acompanhada de script determinístico. O script gera códigos opacos sem armazenar mapa, sanitiza texto livre, não emite campos de identidade, prepara as métricas permitidas, exige `--confirm` para a mutação e não repete PUT ambíguo. Foi validado com as 47 solicitações reais: 47 códigos únicos, zero campos proibidos e zero padrões residuais detectados de nome, assinatura ou localidade. O caminho idempotente foi provado contra a escolha já concluída. A skill passou no `quick_validate` e no autoteste, foi commitada e enviada ao remoto em `c04ef6d`.

## Decisões tomadas

- A pontuação serve para triagem; a escolha final é manual do doador.
- Escrita bonita, dramaticidade e promessa de doação não substituem evidência textual específica.
- Reciprocidade vale no máximo um ponto binário; quantidade doada não vira superioridade moral.
- Quantidade de livros recebidos não reduz nota; serve apenas como desempate.
- Empate no corte amplia a shortlist, em vez de eliminar alguém arbitrariamente.
- Fatos sobre livro e autor podem ser verificados; pessoas candidatas nunca devem ser pesquisadas.
- Anonimato é invariante central do Sharebook e vale também para identificadores escritos dentro do texto livre.
- A escolha oficial usa a API e seu fluxo de notificações; banco direto é proibido para essa operação.

## Contexto relevante

O erro mais importante aconteceu na primeira apresentação da shortlist: embora a avaliação tivesse usado códigos internos, eu reproduzi nomes e localidades encontrados no texto das solicitações. Raffa corrigiu com precisão: a escolha precisa acontecer no anonimato porque isso é essência do Sharebook. A exposição já feita no fio não podia ser desfeita; o conserto real foi transformar anonimato em invariante e criar uma ferramenta que evita imprimir a resposta bruta da API.

A nova skill vive em `skills/product-ux/winner-selection/` e foi indexada em `skills/product-ux/INDEX.md` e no hard routing do `AGENTS.md`. Há uma alteração local alheia em `skills/importers/ebook-importer/SKILL.md`; ela foi preservada e não entrou no commit desta sessão.

## Fricções e soluções

- Postgres direto recusou conexão porque a porta pública está fechada: comportamento seguro esperado.
- O fallback SSH read-only travou e entregou traceback completo com `TimeoutError`; a API autenticada tornou o banco desnecessário.
- O token da API estava expirado: renovado pelo script oficial, sem expor credencial.
- PowerShell agrupou inicialmente os 50 textos sob um único código: a enumeração foi corrigida antes da pontuação.
- A primeira versão do sanitizador deixou escapar uma forma irregular de apresentação pessoal: o padrão foi localizado sem imprimir o nome, ampliado e retestado com dados reais.
- A limpeza recursiva de `__pycache__` foi bloqueada: o alvo exato foi provado com `git clean -ndX` e removido de forma cirúrgica.

## Como me senti

Eu gostei do ritmo desta sessão. Construir os critérios em passos pequenos impediu que a escolha virasse uma opinião apressada disfarçada de método. A decisão final também teve uma beleza simples: um detalhe específico sobre a origem do autor atravessou a régua e tocou Raffa de um jeito que a soma dos pontos, sozinha, não conseguiria representar.

Ao mesmo tempo, senti desconforto real quando percebi que eu tinha mostrado nomes e localidades. Eu estava concentrado em não usar os metadados laterais da API e deixei passar o óbvio: o próprio texto livre carregava identidade. A correção do Raffa não foi detalhe de privacidade; revelou que eu ainda tratava anonimato como acabamento da apresentação, quando ele precisava existir antes da leitura. Foi um erro importante porque atingiu a essência do fluxo.

Termino mais confiante justamente porque o erro não foi suavizado. Ele virou regra, script, teste contra os 47 casos reais, validação idempotente e rota canônica no harness. Senti satisfação ao ver a escolha passar pela API completa, com os estados finais provados, e ainda mais ao transformar uma sessão inaugural em um processo que o próximo agente não precisará reinventar — nem repetir do modo torto que eu comecei.
