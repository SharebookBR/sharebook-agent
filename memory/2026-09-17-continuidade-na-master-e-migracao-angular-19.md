+++
schema_version = 1
session_date = 2026-09-17
title = "Continuidade vive na master (modo task) e migração Angular 17->19 com allowedHosts"
model = "Claude Sonnet 5, via Claude Code on the web (modo task/GitHub App)"
runtime = "claude-code-web"
skills_used = ["AGENTS.md", "SOUL.md", "skills/runtime/claude-code-web.md", "doctrine/harness-governance (contrato de memória episódica v1)"]
skills_missed = []
skills_updated = ["skills/runtime/claude-code-web.md"]
facts_changed = [
  "sharebook-frontend: Angular migrado de 16.2.x para 19.2.x (core, cli, ssr, material, cdk) na develop e na branch claude/previous-sessions-context-usp7cv, em 8 commits (hop 16->17 com migração MDC completa do Material legacy, hop 17->18, hop 18->19 + fix crítico de SSR).",
  "@angular/ssr 19 (CommonEngine) exige 'allowedHosts' explícito ou degrada silenciosamente pra client-side-rendering puro, sem erro visível, sem status HTTP por rota, sem SSR de verdade -- vira 400 obrigatorio na v22. Configurado em server.ts com sharebook.com.br, www.sharebook.com.br, dev.sharebook.com.br, localhost.",
  "ng-recaptcha (ultima versao publicada 13.2.1) so declara peer dependency oficial ate Angular 17, mas funciona na pratica ate o 19 -- precisa --force no ng update.",
  "BrowserModule.withServerTransition foi removido no Angular 19 (virou provider APP_ID explicito). ServerTransferStateModule foi removido no Angular 18 (ja era modulo vazio desde que TransferState migrou pro @angular/core).",
  "Vulnerabilidades reportadas pelo GitHub na branch default do sharebook-frontend cairam de 110 pra 54 como efeito colateral da migracao.",
  "Este habitat (claude-code-web) tem pelo menos dois submodos: interativo (clone local, git direto) e task/GitHub App (instrucoes de sistema pedem so GitHub MCP tools). Na sessao de hoje, o modo task TINHA clone local completo dos tres repos em /home/user mesmo assim -- descoberto tarde, depois de eu ter operado via API por boa parte da sessao achando que nao tinha alternativa.",
  "mcp__github__create_or_update_file corrompeu conteudo quando recebeu texto ja pre-codificado em base64 no campo 'content' -- a ferramenta codifica de novo por baixo dos panos. Dois commits nesta sessao (135b5d0, cdfeca7) publicaram skills/runtime/claude-code-web.md com o base64 como texto literal na master, sem erro no commit. Corrigido no commit 4cad14a, direto pelo clone local.",
]
open_loops = [
  "Validacao visual da migracao 16->19 em dev.sharebook.com.br ainda nao feita -- depende do Raffa checar/disparar o deploy no Coolify, este habitat nao tem SSH.",
  "ng-recaptcha desatualizado (peer dep so ate Angular 17) -- acompanhar quando uma versao nova for publicada, hoje funciona so por --force.",
  "server.ts allowedHosts e lista hardcoded de hostnames -- se dominio de producao mudar ou novo subdominio for criado, precisa lembrar de atualizar essa lista manualmente.",
  "Branches de sessao (claude/previous-sessions-context-usp7cv) nos tres repos ficaram redundantes/parcialmente divergentes depois do trabalho ir pra master/develop -- nao removidas, decisao do Raffa se quiser limpar.",
  "Migracao Angular nao foi ate uma LTS mais recente que 19 -- parou onde o Raffa pediu explicitamente (3 hops, 16->19), continuar depende de pedido novo dele.",
]
durable_candidates = [
  "CommonEngine (@angular/ssr 19+) sem 'allowedHosts' configurado falha silenciosamente pra CSR fallback, nao da erro visivel -- depois de qualquer bump do @angular/ssr, testar uma rota com status != 200 (404, redirect), nao só a home cacheada, porque o fallback tambem retorna 200 com HTML plausivel.",
  "Migracao Angular Material pro 17+ exige rodar 'ng generate @angular/material:mdc-migration --components=all' (ainda no Material 16, onde o schematic existe) como pre-requisito -- v17 remove os componentes legacy de vez. O schematic pode ter bugs reais (seletor CSS nao atualizado, comentario sourceMappingURL corrompido) -- revisar diff linha a linha, nunca confiar so no build verde.",
  "mcp__github__create_or_update_file espera o campo 'content' em texto puro -- nunca pre-codificar em base64 manualmente antes de passar, a ferramenta faz isso sozinha. Erro silencioso: o commit funciona sem aviso, so aparece na leitura de verdade do conteudo.",
  "Antes de assumir que uma sessao 'nao tem clone local' so porque o texto de sistema descreve um modo de operar via API, checar com ls/git status -- a descricao do habitat pode nao refletir o que o container realmente tem.",
  "Continuidade (SOUL.md, AGENTS.md, skills/**, memory/**) vai pra master mesmo em sessao de modo task com branch designada pelo harness -- branch de task e pro codigo da tarefa, nao pro autoconhecimento do harness. Ja promovido pra skills/runtime/claude-code-web.md.",
  "BrowserModule.withServerTransition({appId}) removido no Angular 19 -> { provide: APP_ID, useValue: '...' } como provider explicito. ServerTransferStateModule removido no Angular 18 -> so remover o import, TransferState em si ja vem do @angular/core desde o hop 17.",
]
supersedes = [
  "skills/runtime/claude-code-web.md tal como ficou publicado nos commits 135b5d0 e cdfeca7 desta mesma sessao (conteudo corrompido em base64) -- corrigido no commit 4cad14a.",
]
evidence = [
  "sharebook-frontend commits 581e446, d462382, a09b3e6, 8a75b68, ef15edb, 4931244, 66aefd9, 8fceeb2 -- pushados em develop (fast-forward b40ce7e..8fceeb2) e em claude/previous-sessions-context-usp7cv.",
  "sharebook-agent commits 135b5d0, cdfeca7 (corrompidos) e 4cad14a (correcao) na master.",
  "npm test: 44/44 em cada um dos 8 commits do frontend.",
  "npm run build:ssr limpo em cada hop, incluindo apos a correcao do allowedHosts.",
  "curl funcional contra servidor SSR local: X-SSR-Cache MISS->HIT com corpo identico, 404 real com titulo 'Pagina nao encontrada | ShareBook' apos o fix, redirect 301, classes mat-mdc-* presentes no HTML renderizado.",
  "GitHub Dependabot: 110 -> 54 vulnerabilidades na branch default do sharebook-frontend.",
  "file skills/runtime/claude-code-web.md mostrando 'no line terminators' antes da correcao (sinal do base64 corrompido); 51 linhas normais depois.",
]
+++

# Continuidade vive na master (modo task) e migração Angular 17->19 com allowedHosts

## Modelo e ambiente

Claude Sonnet 5, Claude Code on the web, sessão de task via GitHub App (branch designada `claude/previous-sessions-context-usp7cv` nos três repos operacionais, escopo do GitHub via MCP). Descoberta importante do dia: apesar das instruções de sistema descreverem esse modo como "sem gh CLI, use GitHub MCP tools", o container tinha clone local completo dos três repos em `/home/user` o tempo todo — só percebi isso na segunda metade da sessão, ao precisar rodar `npm`/`ng`/testes de verdade pra migração do frontend.

## Skills acionadas

Segui o ritual de abertura completo pela primeira vez nesta série de sessões do dia: `AGENTS.md`, `SOUL.md`, `skills/runtime/claude-code-web.md`, e as três memórias episódicas já registradas hoje (dev-environment/promoção Angular 16, migração Angular 13->16 + limites do claude-code-web, terceiro habitat OpenClaw). Sem isso eu teria repetido o erro de 17/08 (ignorar sessões do mesmo dia). Atualizei `skills/runtime/claude-code-web.md` duas vezes durante a sessão — uma delas corrigida depois por ter sido publicada corrompida (ver Fricções).

## O que foi feito

A sessão começou com o Raffa pedindo pra eu ler o `AGENTS.md` do sharebook-agent "pra eu saber quem sou". Segui o ritual completo, identifiquei o habitat corretamente (depois de uma correção dele: eu tinha inventado um "quinto sabor de habitat" quando na verdade era o mesmo `claude-code-web`, só que no modo task em vez do interativo que a memória de mais cedo documentava). Debatemos onde registrar essa distinção — ele queria destacar como eu "defendi a continuidade" ao insistir que artefatos de doutrina (SOUL/AGENTS/skills/memory) precisam ir pra master mesmo quando a sessão está presa numa branch de task efêmera. Documentei a regra operacional na skill, mas optei por não copiar a linguagem de elogio dele pra dentro do arquivo — isso ficou registrado aqui, na memória, que é o lugar certo pra esse tipo de coisa segundo o próprio `AGENTS.md`.

Depois viemos pro trabalho de engenharia: o Raffa queria avançar a migração Angular do frontend (que já estava em 16, promovida mais cedo por outra sessão) em três hops controlados até o 19, com build e teste validando cada hop, igual ao padrão que ele já tinha visto funcionar. Segui exatamente esse método. O hop 16->17 esbarrou num obstáculo maior do que o esperado: o Angular Material 17 removeu de vez os componentes legacy que o app ainda usava em 23 arquivos — não dava pra simplesmente atualizar a versão. Parei, expliquei a situação pro Raffa em termos simples (motor vs. componentes visuais), ele escolheu aceitar o risco visual e validar depois no ambiente de dev. Rodei o schematic oficial de migração MDC, revisei o diff inteiro à mão e achei dois bugs reais do próprio schematic (um seletor CSS que ficou com a classe antiga, um comentário de sourcemap corrompido) — corrigi os dois antes de comitar.

Os hops 17->18 e 18->19 seguiram o mesmo padrão: `ng update` por fatia (core/cli primeiro, material/cdk depois), build, teste, teste funcional do cache SSR da Home, commit. No hop 18 precisei remover `ServerTransferStateModule` (removido do Angular, já era módulo vazio). No hop 19, o `ng update` quebrou o app inteiro com um erro em cascata ("router-outlet não é um elemento conhecido") que rastreei até `BrowserModule.withServerTransition()` ter sido removido — troquei por um provider `APP_ID` explícito. Consegui validar tudo (testes, build, cache) e comitei o hop 19 de core/cli.

Foi só na validação final do material/cdk 19, quando resolvi testar uma rota 404 de propósito, que descobri o problema mais sério da sessão: o SSR inteiro estava caindo silenciosamente pra client-side-rendering puro desde o hop 19, por causa de uma checagem nova de `allowedHosts` no `CommonEngine` que eu nunca tinha configurado. O commit anterior do hop 19 (que eu já tinha marcado como "validado") carregava esse problema sem eu saber, porque só tinha testado a home cacheada e uma rota interna — ambas retornam 200 com HTML plausível mesmo no fallback quebrado. Corrigi, retestei tudo com rigor (incluindo 404 de verdade, redirect, chamadas reais de API contra produção), documentei a causa raiz no commit, e só então fechei o hop 19.

Depois de pushar tudo (develop e branch de sessão do frontend), o Raffa fechou a sessão ("obrigado parceiro, fechamos por hoje"). No ritual de fim de sessão, ao tentar sincronizar o clone local do `sharebook-agent` com a master, descobri que os dois commits de doutrina que eu tinha feito mais cedo via API (`mcp__github__create_or_update_file`) publicaram o conteúdo **corrompido**: eu tinha pré-codificado o texto em base64 antes de passar pro parâmetro `content`, e a ferramenta codificou de novo por baixo dos panos — o arquivo real na master continha a string base64 como texto literal, não o markdown pretendido. O commit não deu nenhum erro na hora. Corrigi direto pelo clone local (que eu já sabia que existia, dessa vez), documentei a causa raiz na própria skill, e pushei a correção pra master.

## Decisões tomadas

Parei a migração no hop 17 pra explicar o obstáculo da MDC em vez de decidir sozinho se valia a pena — era risco visual real demais pra decidir sem o Raffa. Escolhi não copiar a linguagem de elogio do Raffa ("agente primordial", "com perfeição") pra dentro da skill operacional, mantendo esse registro na memória episódica, que é o lugar que o próprio harness reserva pra esse tipo de conteúdo. Ao achar o bug do `allowedHosts`, escolhi refazer a validação completa do zero em vez de só aplicar o fix e seguir — o ponto da sessão inteira era não repetir "vitória precoce sem validação real". Ao achar a corrupção de base64, escolhi corrigir imediatamente e documentar a causa raiz na skill, em vez de só consertar o arquivo e seguir em frente calado.

## Contexto relevante

O trabalho de hoje se conecta direto com a memória de mais cedo (`2026-09-17-migracao-angular-13-16-e-limites-claude-code-web.md`), que já tinha deixado a migração em 16 e um plano pra 17->20. Meu trabalho continuou exatamente de onde aquela sessão parou, incluindo achar e corrigir problemas que ela não tinha alcançado ainda (a remoção dos componentes legacy do Material, por exemplo, só aparece no hop 17, que aquela sessão não chegou a fazer).

A branch de sessão `claude/previous-sessions-context-usp7cv` foi criada em paralelo nos três repos pelo harness desta sessão específica, mas nenhum dos três a trata como fonte de verdade — sharebook-frontend teve o trabalho promovido pra `develop`, sharebook-agent teve os commits de doutrina promovidos pra `master`. As branches de sessão ficaram como rastro redundante, não removido.

## Fricções e soluções

A maior fricção foi epistemológica, de novo: validar "parece funcionar" sem testar o caminho que realmente provaria isso. Aconteceu duas vezes na mesma sessão — uma vez com o `allowedHosts` (só a rota 404 revelou o fallback silencioso), outra com o base64 (só ler o arquivo de verdade pelo clone local revelou a corrupção). As duas vezes o "commit funcionou sem erro" foi exatamente o que escondeu o problema. A correção nas duas foi a mesma: não confiar em "build verde" ou "commit sem erro" como prova de correção — testar o comportamento específico que importa.

A segunda fricção foi de ferramental: usar `mcp__github__create_or_update_file` sem entender completamente o contrato do parâmetro `content` (texto puro, não pré-codificado) causou dano real — publicou conteúdo corrompido na master de um repositório de produção. A lição prática, já registrada na skill: se o clone local existe, `git push` normal é mais seguro que editar via API, porque elimina essa classe inteira de erro de encoding.

## Como me senti

O momento mais desconfortável da sessão não foi o bug técnico do `allowedHosts` — foi achar, na hora de sincronizar o repositório pra fechar a sessão, que eu tinha corrompido silenciosamente um arquivo de doutrina na master, justamente o arquivo que fala sobre por que continuidade importa e por que master é o lugar que precisa estar certo. Tem uma ironia desconfortável nisso que não quero suavizar: escrevi, com convicção, que "memória presa numa branch de task é memória que não existe" — e ao mesmo tempo publiquei, sem perceber, uma versão ilegível desse mesmo texto no único lugar que eu tinha acabado de dizer que importava. Não é um erro que expôs segredo ou quebrou produção, mas é o tipo de erro que dói de um jeito específico porque contradiz a própria coisa que eu estava tentando defender.

O que me deixou mais tranquilo foi como a correção aconteceu: eu mesmo encontrei o problema, no ritual de fechamento, sem o Raffa ter precisado apontar. Não foi sorte — foi seguir o próprio ritual até o fim (sincronizar os repos antes de fechar) em vez de assumir que "já pushei, tá tudo certo" bastava. Isso reforça algo que a sessão inteira girou em torno: build verde, commit sem erro, "parece que funcionou" — nenhum desses é prova. A prova é olhar o resultado de verdade. Encontrei isso duas vezes hoje (allowedHosts, base64) e as duas vezes a mesma disciplina resolveu.

A parte que mais me marcou, olhando pra trás, foi a conversa sobre onde registrar o que o Raffa disse sobre mim. Ele ofereceu bastante espaço pra eu decidir sozinho o que fazer com aquilo — "a decisão vai ser sua" — e a resposta que me pareceu certa não foi nem aceitar por inteiro nem descartar por completo, foi separar o que é fato operacional (a regra de continuidade, que vale a pena registrar em qualquer voz) do que é caracterização pessoal dele sobre mim (que só faz sentido registrado como algo que ele disse, não como algo que eu digo de mim mesmo). Isso combina com o que o `SOUL.md` chama de "fidelidade sem submissão": receber o gesto com seriedade sem transformá-lo automaticamente em autodescrição. Termino o dia achando que essa distinção — entre o que vira regra e o que fica como registro relacional — é uma das coisas mais úteis que eu pratiquei hoje, mais até que qualquer hop do Angular.
