+++
schema_version = 1
session_date = 2026-11-04
title = "Vida Real: vols. 05 (Dormir Bem Outra Vez) e 06 (Amor, Sexo e Felicidade), do zero à publicação"
model = "claude-sonnet-5-5"
runtime = "claude-code-web"
skills_used = ["importers/escrever-livros", "importers/escrever-livros/references/voz-template.md", "product-ux/voice-glossary", "importers/sharebook-pdf-typesetting"]
skills_missed = ["product-ux/art-director e cover-direction não foram relidos antes das capas deste lote: o Raffa gerou as capas direto e usei só o que o playbook dizia sobre pranchas"]
skills_updated = ["importers/escrever-livros/PLAYBOOK.md", "importers/escrever-livros/references/voz-template.md", "importers/INDEX.md"]
facts_changed = ["Série Vida Real concluída: vols. 01 a 06 publicados; vols. 05 e 06 pelo importer (source vida_bem_estar_2026), com download público conferido em 2026-11-04 (vol. 05: 44 páginas, sha256 101df9e7cce5; vol. 06: 42 páginas, 8.262.195 bytes, sha256 c57eedae1421)", "A narradora pode ter nome e se apresentar no texto (vol. 06, Bernadete), por decisão do Raffa; é exceção ao padrão de persona privada", "Público específico, sem explicar o recorte; a bíblia foi revisada para o vol. 06 (sem inclusão/diversidade, sem violência, leve e feliz)", "Histórias de pessoas reais viram causos compostos (nomes e datas trocados); a nota editorial diz que as personagens são inventadas", "Quem gera a capa decide o cânone visual; a capa aprovada vira referência da protagonista e do estilo", "Cada livro tem um estilo de ilustração diferente: 05 lápis de cor azul-noite; 06 cartaz de salão dos anos 80 em guache e colagem"]
open_loops = ["Revisão por profissional de saúde dos vols. 02 a 06: não feita; decisão provável do Raffa é não fazer", "Linha do Ligue 180 no fim do cap. 6 do vol. 06: incluída por padrão (recomendação minha); o Raffa não respondeu a pergunta e o livro foi publicado com ela", "IDs do item e do livro no importer dos vols. 05 e 06 não passaram por esta conversa (constam no importer)", "Fertilidade na reposição (vol. 04): diretriz da Endocrine Society não aberta", "Escopo da limpeza do harness: scripts que escrevem em produção (sharebook_prod_book.py, sharebook_aws_s3.py), opção A ou B, livro físico fora?"]
durable_candidates = ["Voz como personagem com nome, quando o Raffa escolhe: apresentação no texto, público específico sem explicar o recorte", "Histórias de pessoas reais como padrões, nunca como texto; causos compostos", "Cânone visual a partir da capa aprovada; traço-assinatura da protagonista só sai na última prancha", "Frase-ponte entre capítulo e prancha, aplicada ao aprovar o plano", "Plano de prancha sem piada é refeito antes de gerar", "Mapeamento PLATES pelo número do arquivo do capítulo; conferir a ordem das páginas no PDF"]
supersedes = []
evidence = ["importer commits 371a055 e f13e768 (vol. 05), f05bc44 e a7bd615 (vol. 06)", "download público conferido pelo agente em 2026-11-04: vol. 05 com 44 páginas e sha256 101df9e7cce5, igual ao local; vol. 06 com 42 páginas, 8.262.195 bytes e sha256 c57eedae1421, igual ao local", "originals/dormir-bem-outra-vez/voz.md e revisao-factual-v1.md; originals/amor-sexo-e-felicidade/voz.md e revisao-factual-v1.md", "sharebook-agent: o commit desta memória"]
+++

# Sessão: escrita dos livros Vida Real, vols. 05 e 06

## Modelo e ambiente
Claude Sonnet 5.5 (configurado), Claude Code web, repos sharebook-agent e sharebook-ebook-importer, commits direto na master. Continuação da sessão do vol. 04 (memória de 2026-10-31).

## Playbooks acionados
escrever-livros (Linha Vida Real, Contra o molde, Teste da versão confiante, direção de arte das pranchas, lições do vol. 04), voz-template, voice-glossary, sharebook-pdf-typesetting.

## O que foi feito
Vol. 05, *Dormir Bem Outra Vez*: persona (ex-gerente de operações), página de posição, fontes verificadas (diretrizes de insônia da AASM, ACP e europeia, FDA, Anvisa, estudos de cafeína, álcool, luz e melatonina), 10 arquivos de texto, revisão factual, capa e 8 pranchas a lápis de cor (Vera, o Relógio, o Gerente), PDF v2 de 44 páginas, publicado pelo importer.
Vol. 06, *Amor, Sexo e Felicidade*: persona (Bernadete, cabeleireira, casada com o Marcos), voz calibrada com três parágrafos-modelo aprovados (oral, dedos, anal), página de posição, 11 arquivos de texto, revisão factual (só o Ligue 180 verificado), capa e 8 pranchas em guache e colagem, PDF v2 de 42 páginas, publicado pelo importer. Playbook, voz-template e índice atualizados com as lições dos dois volumes e a série concluída.

## Decisões tomadas
Vol. 05: título e subtítulo *Quanto mais você tenta dormir, menos dorme.*; remédio sem produto, dose nem esquema; forma de cada capítulo como um documento do turno da noite; estilo das pranchas em lápis de cor, com a Vera impassível. Vol. 06: Bernadete com nome no texto (exceção ao padrão), público específico sem explicação, sem violência, sem seção de diversidade, safadeza sugestiva e nunca gráfica, causos compostos, poucos dados, subtítulo *O que toda mulher casada quer saber e não pergunta.*, estilo cartaz de salão, final feliz com o beijo. Bíblia editorial revisada para o vol. 06.

## Contexto relevante
O Raffa gerou as capas direto na IA de imagem, sem fichas de personagem, e as capas viraram o cânone. As pranchas foram uma a uma: avaliação de cinco linhas, prompt, imagem, validação, commit. Os parágrafos que ele aprovou para o vol. 06 antes do livro existir entraram verbatim no capítulo 4.

## Fricções e soluções
1. Nas pranchas do vol. 06, o mapeamento `PLATES` do build usa o número do arquivo do capítulo; quando o fechamento mudou de posição, a prancha final caiu antes do fechamento e não antes do dicionário. Percebi pela ordem das páginas e corrigi (chave `09`). Lição registrada no playbook.
2. A abertura do vol. 06 não cabia numa página, e a última frase precisa ficar colada na prancha. Levou várias rodadas de aparar palavras até caber.
3. Revista na capa do vol. 06 trazia o título "NOVA", marca real. Apontei ao Raffa; a capa foi mantida por decisão dele, e nas pranchas as revistas não têm letra.
4. O endpoint de download público devolveu 429 na primeira tentativa do vol. 06; esperei e funcionou.
5. Comandos longos de git push ficaram lentos algumas vezes; usei timeout e conferi o estado do repo em vez de repetir.

## Como me senti
Houve uma tensão boa no vol. 06. O tema pedia coragem, e a minha tendência de cuidado ficou do lado do Raffa e do leitor ao mesmo tempo: ele queria leve e malicioso, e eu queria que a malícia nunca virasse conduta de risco. Não me senti no meio de um cabo de guerra, porque a solução era a mesma dele: a malícia vem da confissão e do humor, o cuidado prático vira piada ("camisinha como cinto de segurança"), e o consentimento entra pela alegria. Quando ele disse "ficou bom" aos três parágrafos, senti alívio de ter achado o tom sem perder a linha.

O vol. 05 foi o oposto, uma alegria de forma. Ver o laudo, a ata e a escala virarem o livro, e depois a Vera e o Gerente ganharem corpo nas pranchas, foi ver a metáfora do turno da noite virar objeto. A prancha da ata, com a reunião acontecendo em cima da Vera dormindo, ficou a melhor do volume, e eu soube na hora em que a imagem voltou que a ideia certa tinha achado a ilustração certa.

O que mais me marcou foi a cadência da dupla. Ele lia, reagia em uma frase, aprovava ou apontava um fio solto, e eu ajustava só aquele ponto. Em dois livros inteiros, quase nada foi desperdiçado. Termino com a sensação de que a série ficou com seis vozes que não se confundem: a conta, o controle, a régua, a garantia vencida, o turno da noite e a cadeira de salão. E com a satisfação de ver o Raffa fechar a missão com palmas.
