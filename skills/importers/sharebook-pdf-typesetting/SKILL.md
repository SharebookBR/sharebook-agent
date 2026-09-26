---
name: "sharebook-pdf-typesetting"
description: "Diagramar miolo de PDFs Sharebook com preset editorial 4:5 para leitura digital confortável."
---

# Sharebook PDF Typesetting

Use esta skill ao gerar, revisar ou orientar o miolo de PDFs Sharebook, especialmente livros traduzidos ou preparados a partir do Project Gutenberg.

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
