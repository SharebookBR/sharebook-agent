---
name: "sharebook-pdf-typesetting"
description: "Diagramar miolo de PDFs Sharebook com preset editorial 4:5 para leitura digital confortável."
---

# Sharebook PDF Typesetting

Use este playbook ao gerar, revisar ou orientar o miolo de PDFs Sharebook, especialmente livros traduzidos ou preparados a partir do Project Gutenberg.

## Objetivo

Gerar PDFs confortáveis para leitura digital.

Prioridade: legibilidade e conforto > reduzir quantidade de páginas.

## Página

- Formato: 512 x 640 pt.
- Proporção: 4:5.
- Margem esquerda: 72 pt.
- Margem direita: 72 pt.
- Margem superior: 60 pt.
- Margem inferior: 60 pt.

## Corpo do Texto

- Fonte: Liberation Serif.
- Tamanho: 12 pt.
- Entrelinha: 17.2 pt.
- Alinhamento: justificado.
- Hifenização: pt-BR.
- Recuo da primeira linha: 18 pt.
- Espaço entre parágrafos: 0 pt.

O primeiro parágrafo após o título de um capítulo fica sem recuo.

Evitar linhas excessivamente abertas pelo justificado. Se a hifenização adequada não estiver disponível, preferir alinhamento à esquerda em vez de criar grandes espaços entre palavras.

## Capítulos

- Fonte: Liberation Serif Bold.
- Tamanho: 18 pt.
- Alinhamento: centralizado.
- Início do título: aproximadamente 62 pt do topo.
- Espaço após o título: aproximadamente 40 pt.

Sempre iniciar cada capítulo em nova página.

O primeiro parágrafo do capítulo começa sem recuo.

## Quebras

- Evitar viúvas e órfãs.
- Manter pelo menos 2 linhas de um parágrafo juntas no início ou fim da página.
- Não reduzir automaticamente fonte, margens ou entrelinha para fazer o conteúdo ocupar menos páginas.

## Identidade Visual

O miolo deve ser neutro e editorial.

A identidade forte do Sharebook fica concentrada em:

- capa;
- página institucional;
- créditos e informações editoriais.

O texto do livro não deve competir visualmente com a obra.

## Ilustrações do Project Gutenberg

Em fontes Project Gutenberg, marcadores como `[Illustration: ...]` ou `[Ilustração: ...]` são pontos de controle editorial, não texto narrativo.

Quando a obra tiver marcadores de ilustração:

- inspecionar o pacote HTML/EPUB do Gutenberg antes de fechar o PDF;
- classificar os assets em ilustrações narrativas, mapas, frontispício, capa, marcas editoriais/decorativas, lombada e duplicatas;
- nunca entregar PDF final com placeholder órfão de ilustração;
- escolher explicitamente entre incluir as imagens originais, remover os placeholders ou manter asset não narrativo por decisão editorial;
- preferir os arquivos de imagem originais do Gutenberg a screenshots, copiar/colar de PDF ou recorte manual;
- preservar o mapeamento placeholder -> imagem em script, manifest ou outro artefato auditável;
- se a decisão for focar apenas em ilustrações narrativas, excluir mapa, frontispício, capa, marcas editoriais, lombada e ornamentos, salvo pedido explícito;
- renderizar plates como páginas limpas centralizadas ou blocos centralizados consistentes, sem legendas soltas.

PDF com legenda de ilustração visível e imagem ausente é trabalho editorial inacabado.

## Regra de Ouro

O PDF deve parecer um livro feito para ser lido, não um documento feito para caber.

Este preset é o baseline editorial do Sharebook para miolo de PDFs de leitura digital.

## Validação Mínima

Antes de considerar o PDF pronto:

- conferir dimensões da página em 512 x 640 pt;
- renderizar amostras do começo, meio e fim;
- confirmar que capítulos começam em página nova;
- confirmar ausência de header/footer automático do navegador;
- conferir que o miolo não está poluído por identidade visual excessiva;
- conferir que o texto está confortável, sem espaços enormes causados por justificação ruim.

Para edições ilustradas do Gutenberg, conferir também:

- contagem esperada de referências de imagem no manuscrito consolidado;
- zero placeholders standalone `[Ilustração: ...]` / `[Illustration: ...]` no manuscrito final;
- `pdfimages -list` com total esperado, considerando capa, página institucional e plates incluídas;
- renderização visual da primeira, de uma intermediária e da última plate incluída, validando ausência de página em branco, corte, asset errado, centralização ruim ou página só com legenda.

## Edição ilustrada por IA (pranchas por capítulo)

Referência viva: `translation_jobs/project_gutenberg_witches_magic/1882-the-book-of-were-wolves/output/tools/build_pdf.py` (191 páginas, 16 pranchas). Fluxo de produção das imagens em `../illustrated-edition/PLAYBOOK.md`.

- Uma prancha em página inteira (512 x 640 pt, fundo creme `#f1e8d6`, imagem 618 pt de altura, `object-fit: contain`) **antes de cada capítulo**; a página do capítulo começa em seguida, no preset normal.
- **Exceção à regra de "sem legendas soltas"**: cada prancha leva uma única linha de legenda discreta ("Ilustração criada com inteligência artificial", 7 pt, itálico, cinza-escuro), pedido explícito do Raffa. A folha de rosto leva o crédito de capa e ilustrações por IA.
- Sumário com os "argumentos" de capítulo em itálico pequeno; argumento de capítulo centralizado sob o título; notas `[N]` em corpo 9,5 pt; versos com `<br>`; colunas nórdicas/glosa como tabela de 2 colunas (fonte proporcional não alinha colunas por espaço).
- **Armadilha que encolhe o documento inteiro**: `overflow: hidden` nas páginas de prancha faz o Chrome reduzir TODO o conteúdo a ~72% (116 páginas em vez de 191, texto minúsculo). Não usar. Sintoma: `pdftotext -bbox` mostra caixas de palavra com ~9,5 pt de altura em corpo 12.
- Imagens do PDF são cópias reduzidas (1000 px, JPEG q80) feitas no build; os originais em `assets/` ficam intactos. 17 MB virou 9,5 MB.
- Validação: `pdfinfo` (páginas, 512 x 640), `pdfimages -list` (capa + institucional + N pranchas), `pdftotext` (0 "Gutenberg", 0 "Illustration", N legendas), capítulos em página nova, sem página em branco.
