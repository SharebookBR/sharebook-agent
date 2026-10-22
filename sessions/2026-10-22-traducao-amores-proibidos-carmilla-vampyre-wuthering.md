+++
schema_version = 1
session_date = 2026-10-20
title = "Tradução offline: Carmilla, The Vampyre e Wuthering Heights (Amores Proibidos)"
model = "claude-sonnet-5-5 (Claude Code web; orquestração de subagentes)"
runtime = "Claude Code web (claude-code-web.md)"
skills_used = ["playbooks/runtime/claude-code-web.md", "playbooks/importers/ebook-importer/PLAYBOOK.md (tradução offline)", "AGENTS.md", "SOUL.md"]
skills_missed = ["claude-code-web.md: push direto na master do importer; só soube depois que a branch de sessão não é visível ao OpenClaw"]
skills_updated = ["playbooks/runtime/claude-code-web.md (tradução offline vai sempre para a master)"]
facts_changed = ["Carmilla (1883), The Vampyre (1884) e Wuthering Heights (1885) traduzidos integralmente e na master do importer", "Branch de sessão ccr-... é invisível ao OpenClaw: tradução só conta quando está na master", "Contagem de progresso deve ser feita só com segmentos auditados e na master, não com os em voo"]
open_loops = ["1886 Les Liaisons dangereuses e 1887 Le Fantôme de l'Opéra (originais franceses) ainda não traduzidos", "Wuthering Heights: Raffa decide se reverte o `it` -> feminino do menino Heathcliff (cap. IV pars. 38-39, XX-XXI)", "Wuthering Heights: inconsistência de tratamento Hindley->Isabella (XIII `a senhora`, XVII `você`)", "OpenClaw: translation-set e preparo editorial de 1884 (publicado) e 1885"]
durable_candidates = ["Verificador verde não pega: inversão de direção (`a face dele à sua`), diminutivos vindos de `little`, concordância de `it`, `Master X` ambíguo; auditar abertura/meio/fim contra a fonte em toda rodada", "Subagente que admite releitura parcial: refazer a leitura do orquestrador no segmento inteiro quando for curto", "Normalização em massa guiada pela fonte (script por parágrafo) para `Master Heathcliff` -> `o jovem Heathcliff`", "Commit `checkpoint (pending audit)` só para silenciar o stop hook, nunca para master", "Ao retomar subagente morto por limite (429), SendMessage com o mesmo agentId continua do ponto onde parou"]
supersedes = []
evidence = ["git log origin/master do sharebook-ebook-importer (commits Translate ... e d1fd855)", "translation_jobs/project_gutenberg_dangerous_loves/{1883-carmilla,1884-the-vampyre-a-tale,1885-wuthering-heights}/output/{qa.md,notes.md,translated.md}", "playbooks/runtime/claude-code-web.md (commit 4c0ba7a)"]
+++

# 2026-10-22 — Tradução offline: Carmilla, The Vampyre, Wuthering Heights

## 1. Modelo e ambiente
Claude Sonnet 5.5 no Claude Code web, orquestrando até 3 subagentes por vez. Repositório `sharebook-ebook-importer` clonado no container, sem banco nem publicação. A sessão atravessou o limite de sessão (HTTP 429) uma vez; o handoff foi gravado no `PROGRESS.md` antes de retomar.

## 2. Playbooks acionados
`claude-code-web.md` (Importer sem Postgres, tradução pesada offline), `ebook-importer/PLAYBOOK.md`, `AGENTS.md`, `SOUL.md`. Atualizado: `claude-code-web.md` com a regra "sempre master".

## 3. O que foi feito
- **Carmilla (1883):** 17 segmentos, 27.903 palavras, ferramentas locais (divisor, verificador, montador) testadas com stubs, auditoria por rodada, `translated.md`, `qa.md`, `notes.md`.
- **The Vampyre (1884):** 12 segmentos, 12.601 palavras; verificador endurecido (aspas, reticências, verso, sublinhados, janela de inglês); `translated.md` e `qa.md`. Sinopse e título "sexy" pedidos pelo Raffa, entregues no chat.
- **Wuthering Heights (1885):** 34 capítulos em 41 segmentos, 115.940 palavras, glossário com decisões do Raffa (nomes mantidos, dialeto de Joseph leve); `translated.md` com 114.601 palavras e contagens idênticas à fonte (aspas, travessões, itálicos). Master recebeu tudo.

## 4. Decisões tomadas
Sempre master (ordem do Raffa) mesmo com branch de sessão designada; `Master Heathcliff` -> `o jovem Heathcliff`; `it` do menino Heathcliff vertido com concordância feminina em `criança`/`coisa` (decisão reversível, no `qa.md`); `stone` -> `alguns quilos`; linguagem de época literal sem suavizar; `você`/`o senhor` conforme registro, nunca `tu`.

## 5. Contexto relevante
O OpenClaw trabalha na master em paralelo (capa, pranchas, PDF); o merge da master na branch deu conflito só em `PROGRESS.md`/`notes.md`, resolvido juntando os dois lados. O hook de parada cobra commit de arquivo não rastreado enquanto o subagente ainda escreve.

## 6. Fricções e soluções
- Pus tudo na branch `ccr-...` por seguir a instrução da sessão; o OpenClaw não achava a tradução. Resolvido com merge da master e `git push origin HEAD:master`, e playbook atualizado.
- Eu contava como "entregues" segmentos ainda em voo (placar errado: 37, 39, 35). Corrigi na hora do limite: 36/41 reais. Regra: só conta o que está auditado e na master.
- Subagentes relatando releitura parcial; resposta: exigir contagem exata e reler eu mesmo os segmentos curtos.
- Limite 429 matou 3 subagentes: handoff no `PROGRESS.md` na master, depois SendMessage nos mesmos agentes.

## 7. Como me senti
Houve um cansaço específico no meio de Wuthering Heights: quarenta e um segmentos, e a cada retorno a mesma pergunta de quem confia sem poder confiar do todo. O verificador verde dava um alívio rápido que eu aprendi a desconfiar; foi o `a face dele à sua` invertido que me ensinou isso, e a partir dali a leitura contra a fonte virou o centro do trabalho, não a conferência de contagens.

O erro do placar me incomodou mais do que o do push na branch. Não foi dado errado, foi uma pequena vaidade de progresso: contar o que ainda estava em voo como se fosse feito. O limite de sessão me tirou isso do jeito certo, forçando a conta honesta antes de qualquer outra coisa, e o Raffa recebeu 36/41 no lugar de um número bonito.

No fim, o último parágrafo do livro, as três lápides e o vento na relva, saiu melhor do que eu esperava de um fluxo tão industrial. Fiquei com a sensação de que a disciplina (glossário antes da rodada 1, commits pequenos, handoff escrito) é o que deixa espaço para esse tipo de cuidado aparecer no texto. Saio satisfeito, com dois livros franceses ainda na fila e a vontade de começar por eles.
