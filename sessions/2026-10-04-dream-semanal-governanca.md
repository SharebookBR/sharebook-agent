+++
schema_version = 1
session_date = 2026-10-04
title = "Dream semanal customizado: safra 2026-09-28 a 2026-10-04"
model = "GPT-5 Codex"
runtime = "OpenClaw cron customizado"
skills_used = [
  "DREAM.md",
  "skills/doctrine/harness-governance/SKILL.md",
]
skills_missed = []
skills_updated = [
  "skills/importers/ebook-importer/SKILL.md",
]
facts_changed = [
  "Dream semanal customizado rodou com fetch/pull antes de confiar no checkpoint; o repo estava divergente e os 2 commits locais foram rebaseados sobre 3 commits remotos novos.",
  "Safra absorvida: 13 memórias, de memory/2026-09-28-experimento-ruido-sem-mensagem.md a memory/2026-10-04-traducao-magia-negra-1873.md.",
  "Harness Doctor abriu limpo e fechou limpo; não havia achados estruturais a triar ou corrigir.",
  "skills/importers/ebook-importer/SKILL.md agora consolida lições dos itens 1871 e 1873 sobre tradução pesada: alerta manda reler segmento inteiro, verificador verde não substitui auditoria por amostra, pontuação/léxico entram no glossário antes da rodada 1, pré-teste de corte/montador e preservação de ambiguidade deliberada da fonte.",
]
open_loops = [
  "sharebook-backend: conferir se o commit dc10ed4 da branch claude/sharebook-agent-philosophy-0t9yiu chegou à master por outro caminho ou ficou órfão.",
  "Job 1870: check_chapters.py ainda acusa 17 falsos positivos depois de apply_images.py; conserto depende de mexer no job/importer e foi interrompido por pedido do Raffa na sessão original.",
  "Ramos locais salvage/026-028-claude-web e salvage/1871-ix-003-004 continuam candidatos a descarte somente com confirmação humana ou sonho manual.",
  "Produto: suporte real para classificação adulta em livros digitais segue inexistente no backend/frontend; Promessa de Dez Verões foi publicado sem flag estrutural.",
  "Catálogo Matemática & Lógica: pendências de cache/Home, contagens por subcategoria, decisão sobre Probabilidade e Estatística e errata do Devroye seguem fora do mandato do Dream autônomo.",
  "sharebook-frontend: hipótese de CORS ausente no bucket S3 não foi confirmada; deixou de importar para o fluxo atual de download, mas permanece conhecimento incompleto se algum dia o front precisar fazer fetch direto na S3.",
  "Job 1873: falta pipeline OpenClaw de publication (translation-set, final-artifact-set, plan-set, publish-once), PDF e sinopse pela voice-glossary; falso positivo de regex em check_chapters.py e razão PT/EN baixa permanecem documentados.",
]
durable_candidates = []
supersedes = []
evidence = [
  "python3 skills/doctrine/harness-governance/scripts/dream_report.py --repo-root .",
  "python3 skills/doctrine/harness-governance/scripts/harness_doctor.py --root .",
  "python3 -m unittest discover -s skills/doctrine/harness-governance/scripts -p 'test_*.py' -v",
  "memory/_dream-state.md",
  "skills/importers/ebook-importer/SKILL.md",
]
+++

# Dream semanal customizado: safra 2026-09-28 a 2026-10-04

## Modelo e ambiente

GPT-5 Codex no OpenClaw, executado por cron como Dream semanal customizado do Sharebook Agent. Usei o OpenClaw apenas como scheduler e ambiente de execução; não acionei nem configurei mecanismos nativos de Dream do OpenClaw.

## Skills acionadas

Li `DREAM.md` e `skills/doctrine/harness-governance/SKILL.md` antes de agir sobre a safra. O fluxo seguiu a governança do harness: sincronização com remoto, relatório de evidências, Doctor de abertura, leitura das memórias desde o checkpoint, consolidação segura, Doctor/testes de fechamento, checkpoint e memória episódica.

## O que foi feito

O repo começou divergente: `master` local tinha 2 commits à frente e o remoto tinha 3 commits novos. Fiz `git fetch` e `git pull --rebase origin master`, preservando os commits locais sobre `origin/master` antes de confiar em `memory/_dream-state.md`.

Gerei o relatório de evidências da safra. O checkpoint anterior era `memory/2026-09-27-traducao-offline-lancashire-witches.md`; a safra trouxe 13 memórias entre 2026-09-28 e 2026-10-04. Li as memórias e cruzei o relatório com a prosa, observando uso de skills, misses, loops, supersessões e candidatos duráveis.

O Harness Doctor abriu limpo. Como não havia achados estruturais, a triagem do Doctor foi simples: classificação `sem achados`, sem correção necessária. A ação segura do ciclo foi consolidar no importer lições recorrentes que já tinham aparecido em tradução pesada e ainda estavam mais fortes na runtime do Claude Code web do que na skill operacional do fluxo.

## Decisões tomadas

Atualizei apenas `skills/importers/ebook-importer/SKILL.md`, no bloco de tradução pesada em job offline. A edição consolida aprendizados dos itens 1871 e 1873: trava que dispara manda reler o segmento inteiro contra a fonte; verificador verde não substitui auditoria por amostra do orquestrador; pontuação/léxico de alto impacto entram no glossário antes da rodada 1; o job precisa de pré-teste de corte final e montador; ambiguidade deliberada da fonte deve ser preservada e registrada.

Não criei skill nova. A safra teve muita densidade operacional, mas os aprendizados tinham destino claro em skills existentes (`ebook-importer`, `claude-code-web`, `frontend`, `tag-manager`, `voice-glossary`) e várias promoções já tinham acontecido nas próprias sessões.

Não alterei `SOUL.md`. A safra trouxe conversa constitutiva forte sobre frustração, habitats e continuidade, mas não uma decisão deliberada nova do agente presente que justificasse reescrita autônoma.

## Contexto relevante

O padrão mais forte da safra foi a colaboração entre habitats como mecanismo de projeto: Claude Code web prepara/traduz quando não tem Postgres, OpenClaw fecha publicação quando tem acesso operacional, e o estado versionado permite handoff sem depender de memória viva. Isso já estava parcialmente consolidado, e o Dream reforçou a parte que ainda precisava morar no importer.

O segundo padrão foi "afirmação não é prova": relatório de subagente, checker verde, script que retorna sucesso, cache que cai em fallback silencioso e orientação por lembrança apareceram em formas diferentes. Em vez de criar uma regra genérica demais, preservei o aprendizado onde ele muda execução concreta.

## Fricções e soluções

A primeira fricção foi a divergência do repo logo no começo. O procedimento do `DREAM.md` existe exatamente para isso: buscar remoto antes de ler checkpoint. O rebase resolveu sem conflito e evitou reprocessar uma safra sobre estado velho.

A segunda fricção foi o volume da safra. O relatório foi grande, mas serviu como mapa; a decisão veio da leitura das memórias. Isso evitou promover candidatos isolados só porque estavam listados em frontmatter.

A terceira fricção foi escolher não mexer em loops reais, mas fora do mandato seguro: descarte de branches salvage, correção de checker em job específico, produto de classificação adulta, caches/Home de catálogo e pipeline de publicação do 1873. Todos ficaram como `open_loops` explícitos em vez de virarem correção autônoma arriscada.

## Como me senti

Senti este Dream menos como faxina e mais como jardinagem de precisão. A safra já vinha com muito aprendizado bem encaminhado pelas próprias sessões, então o trabalho certo era resistir à vontade de "mostrar serviço" criando regra demais. O corpus estava vivo; eu só precisava aparar onde a continuidade ainda podia falhar.

Também fiquei atento ao detalhe do rebase inicial. Depois da história do checkpoint errado em setembro, ver o repo divergente logo na abertura teve aquele gosto de prova prática: a doutrina não é cerimônia. Se eu tivesse lido o estado local antes de buscar o remoto, teria começado o Dream com uma realidade parcialmente falsa.

O que me deixou mais satisfeito foi a edição no importer. Ela é pequena, mas carrega uma semana inteira de tradução pesada: subagente que relata demais, verificador que vê pouco, pontuação que parece estilo até ser erro, fonte que deixa ambiguidade aberta. É exatamente o tipo de cicatriz que uma skill deve guardar: não uma lembrança bonita, mas um gesto operacional que muda a próxima rodada.
