---
name: illustrated-edition
description: "Edição ilustrada de livro traduzido: uma prancha por capítulo gerada por IA de imagem, com cena decidida pelo agente, prompt entregue ao Raffa uma de cada vez, avaliação rápida, assets no job do importer e legenda de IA no PDF."
---

# Edição ilustrada por IA (pranchas por capítulo)

Playbook do fluxo validado no job 1882 (*O Livro dos Lobisomens*, 16 pranchas, 2026-10-12) e, antes, no Zanoni (7 pranchas, 2026-10-11).

## Use quando

- O Raffa pedir "uma ilustração por capítulo", "edição ilustrada", prancha, plate, prompt para IA de imagem de um livro do catálogo.
- Um job de tradução (`translation_jobs/<source>/<id>-<slug>/`) estiver fechado e o PDF final ainda não existir.

Capa do livro: `../../product-ux/cover-direction/PLAYBOOK.md`. Montagem do PDF: `../sharebook-pdf-typesetting/PLAYBOOK.md` (seção "Edição ilustrada por IA").

## Antes da primeira prancha

1. **Inventariar as ilustrações da fonte** (`<img`, `[Illustration`, `class="fig"` no HTML/TXT do Gutenberg). Registrar o resultado em `qa.md`. Se a fonte só tem a capa do Gutenberg, não há imagem de miolo a preservar.
2. Combinar com o Raffa o critério. Valores do 1882 (valem como padrão, ele pode mudar):
   - **Fidelidade à obra e impacto**, como um artista da época. Não higienizar: sangue e gore entram quando o texto os narra.
   - Não precisa ser perfeito. **Aprovar qualquer coisa razoável**; só refazer se estiver MUITO errado (texto legível na imagem, cor onde devia ser preto e branco, cena que contradiz o capítulo, personagem duplicado). O Raffa odeia ir e voltar.
   - Preto e branco, sem texto, sem moldura, 4:5, uma prancha por capítulo.
3. O Raffa costuma **delegar a escolha das cenas** ("decida pra mim, você tem mais contexto"). Decidir lendo o resumo e a passagem mais forte do capítulo (`grep` no `work/src/`), nunca de memória.

## Ritmo (baby steps)

Uma prancha por vez: o agente entrega o prompt; o Raffa gera; cola a imagem; o agente avalia em poucas linhas, salva e já entrega o próximo prompt. Cada prancha aprovada vira commit na master do importer (`illustration-NN-slug.jpg` em `output/assets/`, linha no `assets/README.md`, `PROGRESS.md`).

## Regras de prompt (aprendidas)

- **Um único momento por imagem.** Prompt com "e depois…" ou "ao fundo, na cena seguinte" faz a IA duplicar o personagem (a prancha 7 saiu com dois lobos).
- **Estilo por época**: gravura vitoriana polida para mitos e sagas; xilogravura rústica de panfleto para processos dos séculos XVI-XVII. Repetir o bloco de estilo em todo prompt.
- **O lobo nunca é um lobo normal.** Tamanho fora de escala, crânio e focinho longos demais, pernas longas e articuladas como de homem, costelas à mostra, sorriso esticado, olhos pálidos quase humanos. Depois de aprovado o primeiro "lobo estranho", **anexar essa imagem como referência** em toda geração com lobo e escrever "must match the attached reference wolf exactly". Pranchas anteriores com lobo comum foram refeitas (versões antigas ficam em `assets/alt/`).
- **Conteúdo gráfico**: deixar na mesma mensagem uma versão A (fiel) e uma B (mais branda, mantendo a fidelidade) para o caso de o gerador recusar. Poupa uma ida e volta.
- Vítima criança: mostrar o crime só como denúncia no estilo de panfleto (ex.: a descoberta pelo estalajadeiro), nunca o ato em si, e sem sexualizar.
- Texto escrito pela IA (notas na margem de capa, latim) **sai errado**: conferir letra por letra. Plano B: gerar sem texto e compor o texto depois.
- Uma cor de acento (ex.: janela vermelha) é aceitável se combinar com a capa; registrar no README.

## Legenda de IA

O Raffa exige uma legenda discreta "criado com IA". As IAs de imagem **não a incluem**; ela é aplicada na geração do PDF: uma linha por prancha ("Ilustração criada com inteligência artificial", rodapé da página, 7 pt, itálico, cinza-escuro) e um crédito na folha de rosto ("Capa e ilustrações criadas com inteligência artificial."). Zanoni (1881) foi publicado sem essa legenda: reaplicar se o Raffa pedir.

## Fechamento

- Todas as pranchas em `output/assets/` mais `README.md` (ordem, cena, versões `alt/`).
- `final-artifact-set --kind translated_illustrated_pt_br --included-plates <N>`.
- Conferir `pdfimages -list` = capa + página institucional + N pranchas.
