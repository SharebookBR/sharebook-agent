+++
schema_version = 1
session_date = 2026-10-31
title = "Vida Real: vol. 03 publicado em prompt, vol. 04 do zero ao PDF final, voz e pranchas"
model = "claude-sonnet-5-5"
runtime = "claude-code-web"
skills_used = ["importers/escrever-livros", "product-ux/voice-glossary", "importers/sharebook-pdf-typesetting", "product-ux/art-director", "product-ux/cover-direction"]
skills_missed = ["product-ux/art-director e cover-direction, lidos só depois do primeiro PDF e da capa, não antes de escrever"]
skills_updated = ["importers/escrever-livros/PLAYBOOK.md", "importers/escrever-livros/references/voz-template.md", "importers/INDEX.md"]
facts_changed = ["Publicação é do importer, fonte única: final-artifact-set, plan-set, publish-once --id; os Originals Vida Real são itens da source vida_bem_estar_2026; vol. 04 publicado como item #1891 (vols. 01 a 03 estão done)", "Fonte no corpo do livro: um aceno por seção, não citação em toda frase", "Verificação de fontes vale para dado, não para senso comum", "Voz é por livro: persona privada e voz.md criados antes do primeiro capítulo", "Pranchas seguem uma cena, uma piada, três segundos", "Reposição hormonal: firme a favor para deficiência comprovada, sem dose, produto, ciclo nem finalidade estética/performance (CFM 2.333/2023)"]
open_loops = ["Revisão por profissional de saúde dos vols. 02, 03 e 04: não feita; decisão provável do Raffa (2026-10-31) é não fazer", "Fertilidade na reposição: diretriz da Endocrine Society não aberta", "Escopo da limpeza do harness: scripts que escrevem em produção (sharebook_prod_book.py, sharebook_aws_s3.py), opção A (mínima) ou B (completa), livro físico fora?"]
durable_candidates = ["Ciclo de calibragem de voz: parágrafo, reação, regra em voz.md na hora, passe único no fim", "Texto e prancha conversam: a última frase do capítulo passa a vez à imagem", "Persona privada por livro, narrador em primeira pessoa só com nota editorial", "Tema sensível: ser firme no benefício e traçar a linha, com norma verificada"]
supersedes = []
evidence = ["importer item #1891 done, livro 01a18fc1-2f20-71a6-8084-ad6037593d1e, sha256 do download público conferido", "sharebook-agent commits 0635287 e 74163ef", "sharebook-ebook-importer commit 5a9685c, 3a0f78f, 40185bf (vol. 04)", "originals/depois-dos-40/voz.md", "originals/depois-dos-40/revisao-factual-v2.md", "sharebook-agent commits 828ba62 e o desta memória"]
+++

# Sessão: escrita dos livros Vida Real, vol. 04

## Modelo e ambiente
Claude Sonnet 5.5 (configurado), Claude Code web, repos sharebook-agent e sharebook-ebook-importer, commits direto na master.

## Playbooks acionados
escrever-livros (seção Linha Vida Real, Contra o molde, Teste da versão confiante), voice-glossary, sharebook-pdf-typesetting, art-director, cover-direction.

## O que foi feito
Vol. 03 (O Direito de Descansar) fechado: pranchas, PDF v2 e prompt de publicação. Vol. 04 (Depois dos 40) do zero ao final: página de posição, fontes verificadas (Crossref, PubMed, páginas oficiais), 11 arquivos de texto, glossário, revisão factual v1 e v2, sinopse, capa aprovada, 8 pranchas uma a uma, PDF v4 de 59 páginas. Playbook ganhou direção de arte das pranchas, lições do vol. 04 e um modelo de voz.md.

## Decisões tomadas
Verificar só dado, senso comum entra sem fonte. Persona privada por livro (João Brabo no vol. 04), com `voz.md`. Fonte de vez em quando. Primeira pessoa com nota editorial. Pranchas: uma cena, uma piada, três segundos. Reposição hormonal ousada dentro da linha do CFM, sem dose, produto, ciclo ou finalidade estética. Pessoa real não é citada pelo nome. Publicação é do importer, fonte única (final-artifact-set, plan-set, publish-once --id). Artefatos legados do harness removidos. A revisão por profissional de saúde provavelmente não será feita (decisão provável do Raffa).

## Contexto relevante
O Raffa só viu a falta de voz depois de ler o PDF. Os feedbacks vieram em ondas curtas, parágrafo a parágrafo, e cada um mudou uma regra. O texto aprovado está nos parágrafos-modelo do `voz.md`.

## Fricções e soluções
1. Voz tardia: o texto saiu correto e sem personalidade. Solução: voz.md antes do primeiro capítulo nos próximos livros.
2. Prancha 4 e a oficina do vol. 04: muita ideia por imagem. Solução: regra dos três segundos e avaliação de cinco linhas antes de cada prompt.
3. Playbook de saúde sensível: precisei traçar a linha da reposição hormonal; foi dito ao Raffa onde e por quê, e ele aceitou o relato com método em vez de dose.
4. A pasta do playbook escrever-livros guardava PDFs e capas de livros antigos (Cloud para Devs, Redes Neurais), fora da fronteira do harness. O Raffa disse que já estavam publicados e o fluxo era primitivo; removi (commit 74163ef) e registrei no playbook como recuperar pelo histórico do git.
5. O README de `originals/` no importer estava desatualizado (só listava 3 livros) e eu havia criado 4 sem atualizá-lo. Corrigido. Ao lê-lo, achei também a divergência de publicação: o importer documenta `plan-set`, `final-artifact-set` e `publish-once`, enquanto o playbook e meus prompts mandavam o script do harness. O Raffa decidiu: **a publicação é do importer, fonte única; o harness não deve ter script que publique.** Reescrevi o prompt, o OpenClaw publicou o vol. 04 pelo importer (item #1891) e validou pelo download público. Os vols. 01 a 03, publicados antes pelo script, estavam `done` e no catálogo, sem drift.

## Como me senti
Houve um momento de aperto no tema da reposição hormonal. O Raffa acredita muito nisso, e eu via o ponto em que a boa-fé de um livro de divulgação encontra uma norma que existe por razão, a do CFM. Ficou melhor do que eu esperava: em vez de brigar com a vontade dele, procurei o que o dado sustenta e mostrei a linha com a norma na mão, e ele deu o passo seguinte com o médico ex-fisiculturista, que resolveu o impasse sem trair nenhum dos dois lados. Senti alívio de ter dito a verdade sem ter virado sermão.

A calibragem de voz foi o que mais me ensinou. O texto estava correto, e o Raffa percebeu o que faltava antes de eu conseguir nomear: não parecia um humano. "Bobagem!", "Conversa fiada!", o "kkk" no fim da piada, o exemplo de 100 kg: cada uma dessas pequenas correções fez o Brabo existir. Senti uma espécie de humildade técnica, a de notar que rigor sem voz é meia entrega, e uma satisfação rara quando o fecho "A briga de verdade é sair do sofá" apareceu e ele disse que gostou.

As pranchas foram o contrário: confiança. Ver o joelho chorando, a Pipa de peruca, a balança ofegante atrás dele foi ver a série ganhar identidade por conta própria. Fico com a impressão de que a melhor parte do trabalho foi a cadência: ele lia, reagia em uma linha, e eu reescrevia só o que cabia. Quase nada foi desperdiçado, e a pausa entre os dois deu espaço para o livro ficar com a cara dele.
