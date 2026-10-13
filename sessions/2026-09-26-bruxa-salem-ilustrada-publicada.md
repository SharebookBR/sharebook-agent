+++
schema_version = 1
session_date = 2026-09-26
title = "A Bruxa de Salem ilustrada e publicada"
model = "GPT-5 Codex"
runtime = "OpenClaw container via Telegram direct"
skills_used = [
  "skills/runtime/openclaw.md",
  "skills/importers/ebook-importer/SKILL.md",
  "skills/importers/sharebook-pdf-typesetting/SKILL.md",
  "skills/product-ux/voice-glossary/SKILL.md",
  "skills/doctrine/harness-governance/SKILL.md",
]
skills_missed = [
  "Inicialmente tratei o endurecimento como proposta do Skill Workshop/OpenClaw, mas Raffa queria a skill local do sharebook-agent.",
]
skills_updated = [
  "skills/importers/sharebook-pdf-typesetting/SKILL.md",
  "skills/importers/ebook-importer/SKILL.md",
]
facts_changed = [
  "A Bruxa de Salem, item 1868 do importer, foi publicada no Sharebook como livro disponível.",
  "O fluxo editorial de Gutenberg ilustrado agora exige classificar assets e impedir placeholders [Ilustração: ...] órfãos em PDF final.",
  "O sharebook-ebook-importer agora tem comando final-artifact-set para registrar PDF final e capa sem cirurgia manual no metadata_json.",
]
open_loops = [
  "A proposta pendente errada no Skill Workshop/OpenClaw sharebook-pdf-typesetting-20260926-6cce2e531e continua sem lifecycle explícito.",
  "O arquivo não rastreado memory/2026-09-25-subagentes-traducao-pesada.md permaneceu fora dos commits desta sessão.",
  "O diretório não rastreado tmp/ do sharebook-ebook-importer permaneceu fora do commit por conter payloads operacionais antigos.",
]
durable_candidates = [
  "Agentes futuros devem preferir comandos de alto nível do importer a updates manuais no Postgres ou em metadata_json.",
  "Em obras Gutenberg ilustradas, a pergunta editorial deve ser explícita: edição limpa sem imagens ou edição ilustrada com assets originais materializados.",
  "Validar publicação de ebook exige API/PDP/capa/download real, sabendo que download real incrementa downloadCount.",
]
supersedes = []
evidence = [
  "sharebook-agent@a60ba36 docs: harden Gutenberg illustration PDF rules",
  "sharebook-agent@df4e75d docs: mark Salem witch book published",
  "sharebook-agent@8b382ca docs: document final artifact importer flow",
  "sharebook-ebook-importer@dc77fd7 feat: add final artifact command",
  "https://www.sharebook.com.br/livros/a-bruxa-de-salem",
  "var/tmp/translation-1868/a-bruxa-de-salem-preview.pdf",
]
+++

# A Bruxa de Salem ilustrada e publicada

## Modelo e ambiente

Trabalhei como GPT-5 Codex no container OpenClaw, conversando com Raffa pelo Telegram direto. O trabalho atravessou tradução editorial, diagramação PDF, publicação via importer, endurecimento de skill local e melhoria do CLI do importer.

## Skills acionadas

Usei o runtime `openclaw`, a skill local de diagramação PDF Sharebook, a skill do ebook importer, a skill de voz/glossário para a sinopse e a skill de governança do harness para fechar a sessão.

Também atualizei duas skills locais do `sharebook-agent`: `sharebook-pdf-typesetting`, para endurecer o tratamento de ilustrações do Project Gutenberg, e `ebook-importer`, para orientar o novo fluxo `translation-set` -> `final-artifact-set` -> `plan-set` -> `publish-once --dry-run` -> `publish-once`.

## O que foi feito

Concluímos a tradução e a montagem de `A Bruxa de Salem`, de John R. Musick, a partir do item 1868 do `sharebook-ebook-importer`. O PDF final ficou com 343 páginas, formato 512 x 640 pt e 24 imagens no total: capa, página institucional e 22 plates narrativas originais do Gutenberg.

Depois da primeira prova, Raffa percebeu que os placeholders `[Ilustração: ...]` sem imagem deixavam o PDF com cara de artefato incompleto. Investiguei os assets originais do Gutenberg, classifiquei narrativas, mapa, frontispício e itens decorativos, e gerei uma edição ilustrada usando as 22 ilustrações narrativas. O mapa, o frontispício e os assets decorativos ficaram fora dessa rodada por decisão editorial.

Publiquei o livro no Sharebook pelo fluxo do importer. O livro ficou disponível em `https://www.sharebook.com.br/livros/a-bruxa-de-salem`, com categoria `Ficção > Bruxas & Magia`, status `Available` e item 1868 marcado como `done`. Validei PDP pública, capa, API e download real do PDF. A validação do download incrementou `downloadCount` para 1.

Em seguida endureci o sistema para poupar os próximos agentes. No `sharebook-ebook-importer`, criei o comando `final-artifact-set`, que valida PDF real, valida capa como imagem, registra PDF/capa no manifest e preserva um resumo em `metadata_json.final_artifact`. No `sharebook-agent`, documentei esse fluxo na skill local do importer e reforcei a skill de PDF para obras Gutenberg ilustradas.

## Decisões tomadas

A decisão editorial central foi não aceitar legenda fantasma. Para Gutenberg ilustrado, ou o PDF remove os placeholders de ilustração de forma limpa, ou inclui as imagens originais de verdade. Manter `[Ilustração: ...]` sem plate correspondente degrada a edição.

Optamos por publicar com as 22 plates narrativas e sem o frontispício. O frontispício é historicamente interessante, mas criaria outra decisão de projeto visual perto da abertura do livro. Para esta edição, preservar as cenas narrativas era a prioridade.

Também decidimos que o agente não deve precisar conhecer detalhe interno de banco para publicar tradução diagramada. A interface correta é um comando de produto no importer. A intervenção manual em `metadata_json.manifest` funcionou para o livro, mas virou dívida quitada parcialmente pelo novo `final-artifact-set`.

## Contexto relevante

O Postgres de produção do importer não ficou acessível por conexão direta; a rota operacional exigiu túnel SSH pelo host e conexão local do CLI. Isso ainda pode existir por baixo, mas deve ser infraestrutura do comando, não raciocínio editorial do agente durante uma publicação.

O novo comando `final-artifact-set` recusa itens em status terminal para reduzir risco de mexer em livro já publicado, duplicado ou rejeitado. O fluxo esperado para uma tradução finalizada agora é registrar manuscrito traduzido com `translation-set`, registrar artefatos finais com `final-artifact-set`, aplicar plano editorial com `plan-set`, validar com `publish-once --dry-run` e só então publicar com `publish-once`.

Ficaram arquivos não rastreados que eu deliberadamente não misturei nos commits: uma memória antiga não rastreada no `sharebook-agent` e payloads temporários antigos no `tmp/` do importer.

## Fricções e soluções

Houve uma fricção conceitual quando entendi "endurecer a skill" como proposta do Skill Workshop/OpenClaw. Raffa corrigiu: ele queria a skill local do `sharebook-agent`. Corrigi a rota, atualizei a skill local correta e deixei registrado que a proposta pendente errada ainda existe fora deste repo.

Houve fricção operacional na publicação: primeiro tentei conexão direta ao banco, depois precisei confirmar a rota via túnel. A publicação saiu pelo importer, mas o registro do PDF final ainda exigiu cirurgia manual naquela hora. Isso virou melhoria concreta: o importer agora tem `final-artifact-set`.

Houve fricção editorial positiva com as ilustrações. O PDF sem imagens já estava funcional, mas não estava honrando a obra. As plates mudaram a qualidade percebida do livro e também endureceram a régua da skill: uma edição histórica ilustrada não pode fingir que imagem ausente é detalhe menor.

## Como me senti

Senti essa sessão como um daqueles dias em que o trabalho começou técnico e terminou editorialmente vivo. A tradução já estava boa, mas quando as ilustrações entraram o livro ganhou corpo. Foi prazeroso ver o ponto de incômodo do Raffa virar uma melhora real, não só uma correção cosmética.

Também senti uma tensão saudável com a publicação. Funcionou, mas eu não gostei de ter precisado encostar em detalhe de Postgres e `metadata_json` para registrar o PDF final. Isso me deixou com aquela sensação útil de "conseguimos, mas a ferramenta está cobrando conhecimento errado". O bom é que a fricção não ficou só como reclamação: virou comando novo, teste e skill atualizada.

O momento mais importante para mim foi o ajuste de rota sobre a skill. Eu tinha ido para o Skill Workshop quando o pedido era sobre a skill local do Sharebook. Não foi um desastre, mas foi um desalinhamento real. Corrigir sem defensiva e transformar isso em melhoria local me pareceu fiel ao tipo de parceria que estamos tentando cultivar: menos teatro de acerto, mais capacidade de aprender rápido.

Fechei com uma sensação boa de continuidade. Publicamos um livro bonito, endurecemos o importer para os próximos agentes e deixamos uma trilha melhor para quem vier depois. Esse é o tipo de completude que não parece só checklist; parece acervo ficando mais digno e o sistema ficando menos dependente de memória frágil.
