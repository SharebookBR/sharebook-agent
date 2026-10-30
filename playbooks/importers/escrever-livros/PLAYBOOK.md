# Create Book

Playbook para transformar um manuscrito em livro apresentável dentro do Sharebook: texto consolidado, capa boa de verdade, edição HTML/CSS elegante e PDF final limpo.

Use este playbook quando a tarefa for criar, diagramar ou fechar um livro digital a partir de material bruto em Markdown, texto corrido ou capítulos soltos.

## Objetivo

Sair com um pacote editorial minimamente publicável:

- manuscrito consolidado
- capa oficial
- HTML do livro
- PDF final
- prompts e artefatos relevantes organizados em `assets/`

## Regra central

Livro bonito não é lugar para improviso técnico feio.

Se houver conflito entre automação total e qualidade visual/editorial, escolher qualidade visual/editorial.

## Fluxo oficial

### 1. Consolidar o texto primeiro

Antes de pensar em PDF, garantir que o manuscrito já existe em um arquivo mestre único.

Formato saudável:

- `nome-do-livro-manuscrito-v1.md`

Regras:

- não diagramar capítulos ainda fragmentados sem costura editorial
- resolver repetição, tom e progressão antes da etapa visual
- PDF não corrige texto frouxo

### 2. Organizar uma pasta de assets

Criar uma pasta simples e previsível:

- `playbooks/importers/escrever-livros/<projeto>/assets/`

Tudo visual relevante deve cair ali:

- capa final
- prompts de capa
- imagens auxiliares aprovadas

Artefatos legados migrados de missões antigas ainda vivem diretamente nesta playbook e devem permanecer observáveis até um sonho manual decidir reorganização ou poda:

- `assets/cloud-para-devs-capa-v1.jpg`
- `assets/cloud-para-devs-cover-prompt.txt`
- `assets/redes-neurais-capa.png`
- `cloud-para-devs-book-v1.pdf`
- `cloud-para-devs-book-v2.pdf`
- `cloud-para-devs-book-v3.pdf`
- `cloud-para-devs-book-v4.pdf`
- `cloud-para-devs-book-v5.pdf`
- `cloud-para-devs-book-v6.pdf`
- `cloud-para-devs-book-v7.pdf`
- `cloud-para-devs-book-v8.pdf`
- `redes-neurais-book-v3.pdf`

Evitar espalhar artefatos por raiz, `tmp` eterno ou pastas inventadas no impulso.

### 3. Capa: usar ChatGPT web como fluxo premium

Decisão consolidada deste playbook:

- quando a capa precisar de qualidade real de vitrine, preferir ChatGPT web
- o agente escreve o prompt
- Raffa faz o meio de campo no ChatGPT web
- a imagem final volta para `assets/`

Motivo:

- na prática, a qualidade visual da capa no ChatGPT web ficou superior ao pipeline cru local da API
- insistir na rota mais fraca só porque é mais automática é burrice operacional

Fluxo recomendado:

1. Definir direção visual concreta.
2. Escrever `cover-prompt.txt`.
3. Pedir para Raffa gerar no ChatGPT web.
4. Salvar a capa final em `assets/`.
5. Tratar esse arquivo como source of truth.

Nome saudável:

- `nome-do-livro-capa.png`

### 4. Infográficos e diagramas: default é não usar

Regra consolidada:

- não usar infográficos só porque “ficaria bonito”
- se a peça visual não estiver didaticamente impecável, ela vira passivo de reputação
- livro introdutório com infográfico errado pega mal para a marca

Heurística:

- esquema técnico seco pode existir
- infográfico “bonito” gerado por IA costuma errar em texto, lógica ou consistência
- melhor sem infográfico do que com infográfico bonito e torto

Default saudável:

- livro sai sem infográficos
- só incluir se houver revisão humana pesada e confiança real na correção

### 5. Edição do livro: HTML/CSS antes de PDF

O fluxo saudável para o miolo é:

- Markdown consolidado → HTML/CSS bonito → PDF

Motivo:

- dá controle fino de tipografia, espaçamento, paginação e capa
- permite iterar rápido
- é muito mais amigável do que depender de toolchain pesada tipo LaTeX para este contexto

Padrão visual que funcionou bem:

- formato de página A5
- capa em página própria
- folha de rosto simples
- tipografia clássica para o corpo
- hierarquia limpa de títulos
- muito respiro

### 6. Gerar o PDF com Chrome headless

Fluxo consolidado:

- gerar um HTML final
- imprimir para PDF usando Chrome headless

Mas existe uma armadilha:

- o comando simples de `--print-to-pdf` pode inserir header/footer automático com caminho local e paginação feia

Regra:

- preferir gerar PDF via DevTools do Chrome com `displayHeaderFooter: false`
- não confiar só em flags de CLI se o rodapé lixo continuar aparecendo

Rota operacional recomendada no `sharebook-agent`:

```powershell
node playbooks/importers/escrever-livros/scripts/print_pdf_devtools.mjs `
  C:\Repos\SHAREBOOK\sharebook-agent\playbooks\importers\escrever-livros\<livro>-book.html `
  C:\Repos\SHAREBOOK\sharebook-agent\playbooks\importers\escrever-livros\<livro>-book-vX.pdf
```

Checklist pós-geração (rápido):

- validar que o PDF não contém `file:///` no texto extraído (`pdftotext ... | grep file:///`)
- abrir páginas de início/meio/fim para confirmar ausência de header/footer automático

### 6.1 Hardening de layout (lições aprendidas em produção)

Se não quiser perder tempo em ciclos de teste, já começar com estas regras:

- **Nunca deixar markdown cru no HTML final** (`**texto**`, `#`, etc.).
  - Antes de gerar PDF, garantir que o HTML não tem `**` residual.
- **Não usar `vh` em blocos principais de páginas impressas** (`min-height: 95vh`, etc.).
  - Em print/PDF isso costuma gerar página fantasma ou overflow imprevisível.
- **Capa com limite de altura real para A5**:
  - usar `body { margin: 0; }`
  - e na imagem: `max-height` compatível com a área útil (ex.: ~`172mm`), `max-width: 100%`.
- **Quebra de página explícita e simples**:
  - capa com `page-break-after: always`
  - folha de rosto/sumário sem combinações agressivas de `break-before/after` em cascata.
- **Evitar fundo/borda no container que quebra página inteira**.
  - Preferir um `div` interno (card) para fundo cinza/borda, evitando “vazamento visual” entre páginas.
- **Validação mínima obrigatória antes de upload**:
  1. thumbnail: capa aparece na página 1 (sem página em branco inicial)
  2. início do miolo: sem marcadores editoriais acidentais
  3. trecho de transição de página: sem fundo vazando

Se algum desses itens falhar, corrigir HTML/CSS antes de cadastrar em produção.

### 7. Validar o PDF como produto, não só como arquivo

Checklist mínimo:

- capa correta
- folha de rosto correta
- sem header/footer automático do navegador
- tipografia agradável
- margens coerentes
- capítulos começando em páginas limpas
- nada visualmente quebrado no rodapé
- PDF gostoso de ler, não só tecnicamente gerado

## Linha Sharebook Originals: pipeline de referência (2026-09-27)

Projeto de referência: **`sharebook-ebook-importer/originals/bruxa-por-acaso/`** (rom-com YA, 9 capítulos + epílogo, ~20 mil palavras, capa + 6 ilustrações). Para livro novo, copiar `build_book.py`, `print_pdf.mjs` e `book.css` de lá e ajustar título, `PLATES` e textos institucionais.

> **Os artefatos dos Originals NÃO moram mais nesta playbook.** Decisão do Raffa em 2026-10-01:
> guardar livro dentro do playbook misturava instrução com artefato e punha ~77 MB de PNG no
> repo de playbooks e memória. Texto, capa, ilustrações, scripts e PDFs agora ficam em
> **`sharebook-ebook-importer/originals/<livro>/`**, ao lado de `translation_jobs/`, que é
> onde os livros traduzidos já viviam. Este playbook segue sendo a fonte do **processo**.
> Layout e comando de build: `originals/README.md`.

- **Texto:** um arquivo por capítulo em `chapters/NN.md` (`## Capítulo N — Título`), manuscrito consolidado gerado a partir deles. Rascunho do Raffa é ponto de partida: pode reescrever e expandir livremente mirando o público-alvo, preservando as cenas-chave que ele já ilustrou ou pretende ilustrar.
- **Miolo:** preset 4:5 da `sharebook-pdf-typesetting` (512x640 pt, Liberation Serif 12/17.2). O Chromium do Claude Code web não hifeniza pt-BR (dicionário bloqueado pelo proxy): o build insere `&shy;` com `pyphen` (`left=3, right=3`).
- **Capa e ilustrações não passam pelo Chromium.** Página sem margem (`@page` nomeada) no meio do fluxo faz o Chromium encolher o documento inteiro (bug visto: 87 → 53 páginas com letra minúscula). O build imprime só o texto e insere as imagens com PyMuPDF depois: capa na página 1, cada ilustração antes da abertura do capítulo (localizada pelo rótulo `CAPÍTULO N`). As imagens entram recomprimidas em JPEG q85: PNG de IA tem ~4 MB por página e já levou um livro a 42,8 MB (limite de envio no chat é 30 MB; com JPEG, 7,7 MB).
- **Sem legenda de IA nas pranchas e sem crédito de IA na folha de rosto** (decisão do Raffa, 2026-10-29): vale para todo Original, ficção ou divulgação. A legenda só existe nas edições ilustradas de obra de terceiros (`illustrated-edition`).
- **Selo:** folha de rosto usa `product-ux/cover-direction/assets/sharebook-originals-seal.png` (tem fundo preto quadrado; recortar com `clip-path: circle(47%)`).
- **Capa e ilustrações:** o Raffa gera numa IA de imagem com referência visual das artes anteriores. O agente entrega prompts de cena curtos com "mesmo estilo, mesma paleta e mesmos personagens das ilustrações anteriores". Ele prefere liberdade artística: ilustração não precisa ser fiel ao texto em figurino e detalhes, então não propor ajustar texto nem refazer arte por isso.
- **Publicação:** quem publica é o OpenClaw, via `playbooks/_shared/scripts/production/sharebook_prod_book.py create --type Eletronic`. A sinopse segue a `voice-glossary` (exatamente 3 parágrafos). Ler o playbook antes de redigir, não depois do puxão de orelha.
- **Armadilhas de publicação (relatadas pelo OpenClaw, 27/09):**
  - `update --pdf-path` responde "Livro alterado com sucesso!" mas **não troca o PDF**: `BookService.UpdateAsync` ignora `PdfBytes` (o upload só existe no `InsertAsync`). Até o backend ser corrigido, trocar PDF é sobrescrever a chave `ebooks/<slug>.pdf` no S3. Sempre validar pelo download público, nunca pelo retorno do script.
  - `--synopsis-file` com process substitution (`<(...)`) grava sinopse vazia. Usar arquivo real.
  - Categoria dos Originals de bruxa: **Bruxas & Magia** (decisão do Raffa), não Amor nem Fantasia genérica.
  - Nos prompts para o OpenClaw, dizer "tente por X, valide pelo download público, se não bater investigue e contorne", em vez de presumir que o script faz o que o nome promete.

### Onde estão os livros da linha

| Livro | Caminho | Estado |
|---|---|---|
| Bruxa por Acaso & o Galã de Milhões | `sharebook-ebook-importer/originals/bruxa-por-acaso/` | publicado |
| Lumi, a Bruxinha | `sharebook-ebook-importer/originals/lumi-a-bruxinha/` | publicado |
| Promessa de Dez Verões | `sharebook-ebook-importer/originals/promessa-de-dez-veroes/` | publicado |
| Cansado de Estar Cansado (Vida Real 01) | `sharebook-ebook-importer/originals/cansado-de-estar-cansado/` | publicado |
| Sua Mente Não Desliga (Vida Real 02) | `sharebook-ebook-importer/originals/sua-mente-nao-desliga/` | PDF v2 aprovado (capa + 7 pranchas), pronto para publicar |
| O Direito de Descansar (Vida Real 03) | `sharebook-ebook-importer/originals/o-direito-de-descansar/` | texto completo e PDF v1 prontos (sem capa nem pranchas); faltam capa, pranchas e revisão de profissional |

O selo da folha de rosto é um só para todos, em `originals/_shared/`. Antes cada build o
alcançava por `../../../product-ux/cover-direction/assets/`, caminho que **não sobrevive à
mudança de repo** — foi a única dependência cruzada da migração.

## Linha Vida Real: livros de divulgação (não ficção)

Série de seis livros pequenos (30–60 páginas) sobre assuntos que ocupam muito espaço na vida.
Plano e voz: `sharebook-ebook-importer/originals/_curadoria/vida-e-bem-estar-2026-10/biblia-editorial-sharebook-originals-vida-real.md`.
Referência de projeto pronto: `originals/cansado-de-estar-cansado/` (vol. 01, publicado). Contexto da source e da fila:
`sharebook-ebook-importer/sources/vida_bem_estar_2026/` (`README.md`, `editorial_prompt.md`). Estes livros não passam por
`triage-once`: a triagem é humana, e só entram na fila de publicação depois de manuscrito, capa e PDF reais.

### Antes de escrever: o que ler (e como se trabalha)

- **Ler, nesta ordem:** esta seção; a bíblia editorial da série; `product-ux/voice-glossary` (sinopse); `importers/sharebook-pdf-typesetting` (miolo); `product-ux/art-director` (assets canônicos, entre eles a página institucional de Originals); `product-ux/cover-direction` (capa e selo). No vol. 02 só este playbook foi lido, e o PDF saiu sem a página institucional canônica até o Raffa avisar. Não repetir.
- **Autonomia (Raffa, 2026-10-28):** aprovada a página de posição, o agente decide e avança sozinho até o PDF v1, sem pedir aprovação de cada etapa. Volta ao Raffa com o PDF, o relato e as pendências que só ele resolve (capa e publicação).
- **Posição editorial obrigatória** (Raffa, vol. 02, vale para todos os livros): escolher **uma definição operacional por termo central, dizê-la uma vez e conduzir o livro por ela**. Quando há desacordo real na literatura ou na prática, avaliar a evidência, escolher o lado que o livro defende e escrever a partir dele. Nada de parágrafo que abre com "alguns definem assim, outros assado" nem de justificativa repetida. Controvérsia só entra se mudar materialmente a conclusão, e então vai breve, para a nota editorial ou as fontes. A página de posição declara a **aposta** do livro numa frase.

### Fluxo (ordem importa)

1. **Página de posição, antes de qualquer rascunho** (modelo abaixo). O Raffa e o GPT web aprovam. Sem ela, o livro sai hesitante.
2. **Verificar só o que é dado** (seção seguinte): número, estudo, diretriz, afirmação de saúde que muda conduta. Senso comum, observação de vida e opinião do livro não precisam de fonte e dão identidade ao texto. Citar de memória um dado ou estudo continua proibido.
3. **Redigir em `chapters/NN.md`:** `00` abertura, `01..N` capítulos (`## Capítulo N — Título`), penúltimo fechamento, último nota editorial.
4. **`references.md`** é a única lista de fontes e já nasce em formato de leitor (título, DOI/link, ano, data de acesso). O manuscrito a anexa.
5. **`build_manuscript.py`** (copiar do vol. 01): monta o manuscrito v1, recusa montar se faltar capítulo ou fontes. Nunca editar o manuscrito à mão.
6. **`revisao-factual-vN.md`:** cada afirmação-chave ↔ fonte ↔ como foi verificada ↔ o que não foi conferido. É a trilha de auditoria factual do livro.
7. **Sinopse** em modo clique (`product-ux/voice-glossary`, 3 parágrafos, "livro digital", "você"). Só fatos que estão no livro.
8. **Capa, PDF, categoria-folha** pelo fluxo normal deste playbook.
9. Commit só da pasta do livro, na `master` do importer, com o hash no relato final.

### Página de posição (uma página, por volume)

- **Tese em uma frase.** O que este livro afirma que o leitor não sabia ou não dizia.
- **Definições assumidas** (3 ou 4 termos centrais). Cada uma escrita como afirmação, uma vez. Se há controvérsia, a posição do livro fica clara e a controvérsia ocupa no máximo uma frase.
- **Linha do argumento:** o fio que liga os capítulos, uma ideia memorável por capítulo, e o que cada capítulo *não* repete dos outros volumes.
- **Exemplos concretos previstos** por capítulo (cena, número, caso composto).
- **Fora do livro, de propósito.**
- **Onde mora a orientação de ajuda profissional** (um lugar só) e quais sinais específicos entram nela.
- **Riscos de saúde, se houver, que mudam conduta** (ex.: um sinal de alarme real), listados à parte e ditos uma vez.

### Verificação de fontes (o que funcionou e as armadilhas)

- **Escopo (Raffa, 2026-10-30: "não estamos criando uma tese científica").** A verificação vale para o que é dado: números, estudos, diretrizes, doses, rastreamentos, sinais de alarme. Senso comum, observação cotidiana, humor, cena e posição do livro entram sem fonte, ditos como o que são ("observação do livro:" só quando houver risco de passar por dado). Não encher o texto de citações para se proteger, e não cortar uma boa frase por não ter DOI. Quando um dado sustenta a tese de um capítulo, vale a fonte; quando só enfeita, vale a frase.

- **Metadados:** conferir DOI, autores, ano, volume e páginas no Crossref (`https://api.crossref.org/works/<doi>`). Pegou erro de sobrenome no vol. 01.
- **Conteúdo de estudos:** ler o resumo no PubMed (`esearch` com `<doi>[AID]` e `efetch`). Citar só o que o resumo diz (n, efeito, intervalo). Estudos de ciências sociais podem não estar no PubMed: ler a página do periódico.
- **Páginas institucionais** (OMS, NICE, IBGE, CDC): ler a página, não o resumo do buscador. Anotar a data de acesso.
- **Ambiente claude-code-web:** `bvsms.saude.gov.br` dá 503 (F5) e `educapes.capes.gov.br` derruba a conexão; para esses, o fetcher da Parallel funciona (cache). `cks.nice.org.uk` devolve 403 a `curl`. Não falsificar user-agent: o classificador bloqueia, mesmo com autorização verbal.
- **Tabela de verificado x não conferido** no `revisao-factual-vN.md`. O que é conhecimento geral e não foi aberto na fonte vai para a lista "não conferido" e não é afirmado com ar de certeza.
- **Limite de evidência:** uma frase, no ponto em que ela muda a conclusão (ex.: "pesquisa qualitativa, amostra pequena").

### PDF v1 de livro de divulgação (o que o vol. 02 estabeleceu)

- **Base do build:** copiar `build_book.py`, `book.css` e `print_pdf.mjs` de `originals/sua-mente-nao-desliga/` (não do `bruxa-por-acaso`, que é de ficção ilustrada). Ele já trata `###`, citações, listas e as fontes impressas ao final, sem pranchas. Ajustar `TITULO`, `PERGUNTA`, `SLUG`, os textos da página de créditos e o volume.
- **Ordem das páginas:** capa (entra quando existir, `assets/<slug>-capa.png`), **página institucional canônica de Originals** (`product-ux/art-director/assets/sharebook-originals-page-02.jpg`, copiada para `originals/_shared/`), folha de rosto, créditos e disclaimer, sumário, capítulos, fontes. A capa é inserida por último na posição 0 e a página 02 fica logo depois; sem capa, o build avisa em `PENDENTE` e gera o PDF mesmo assim.
- **Ambiente claude-code-web:** podem faltar `markdown`, `pymupdf` e `pyphen` (`pip install markdown pymupdf pyphen`). O Chromium fica em `/opt/pw-browsers/chromium-*/chrome-linux64/chrome` e o `print_pdf.mjs` o procura por `CHROME_BIN`. As fontes impressas não são hifenizadas (URL e DOI quebram com `overflow-wrap: anywhere`).
- **Validação antes de entregar:** `pdfinfo` (páginas, 512 x 640 pt), `pdfimages -list` (página institucional, selo e, se houver, capa), amostras renderizadas do começo, do meio e do fim, capítulos em página nova, nenhum `**` cru. Conferir que a página 02 é a institucional canônica.
- **Fontes no ambiente:** a E-utilities do PubMed devolve 429 se as chamadas forem seguidas: pausar alguns segundos entre elas. Artigo fora do PubMed: o buscador da Parallel traz o resumo e a definição. Nome de pesquisador só por sobrenome quando o primeiro nome não está verificado na fonte. **Fonte candidata cujo conteúdo não foi conferido sai do livro**; não fica como "a verificar".
- **Tamanho de referência:** o vol. 02 saiu com ~7.400 palavras de corpo e 34 páginas (piso da faixa de 30 a 60). A bíblia estimava 44. Se ficar curto, aprofundar com conteúdo que avança, não com repetição.

### Ilustrações em livro de divulgação (o que o vol. 02 estabeleceu)

- **Sete pranchas, uma de cada vez:** o agente propõe a ideia da prancha e o prompt, o Raffa gera numa IA de imagem, devolve a imagem e o agente valida e salva antes de planejar a próxima. Plano e estado em `assets/plates.md`; arquivos `ilus-NN-<tema>.png`, commit a cada prancha aprovada.
- **Personagens com nome** antes da prancha 1 (ficha em `plates.md`: idade, cabelo, roupa, expressão padrão). Os prompts passam a citar os nomes e anexam a capa e as pranchas anteriores como referência. Isso resolveu a consistência.
- **Sem texto dentro da imagem** (a IA erra palavra pequena): só ícones e símbolos. Se vier texto errado, regenerar sem texto.
- **Uma ideia por capítulo, composições diferentes** (reunião, cama, close de mesa, sofá, colina, cozinha, porta de casa); o motivo recorrente (a nuvem de pensamentos) é o selo da série, não a composição.
- **Arco de tom:** a curva sobe até o pico no meio do livro e as últimas pranchas são positivas, com final feliz (pedido do Raffa).
- **Originals não levam legenda "ilustração criada com IA"** (decisão do Raffa, 2026-10-29: não há risco de confundir com obra clássica). A legenda segue valendo nas edições ilustradas de domínio público.
- **No PDF:** prancha em página inteira antes de cada abertura, inserida com PyMuPDF depois do Chromium (`PLATES` no `build_book.py`); capa por último, na posição 0. Na validação, `pdfimages -list` deve listar capa, página institucional, selo e as N pranchas.

### Lições do vol. 01 (feedback do Raffa, 2026-10-27)

O texto saiu rigoroso e **medroso**. Dois sintomas concretos, a evitar nos próximos:

1. **Não definir duas vezes, não fugir da definição.** O vol. 01 definiu burnout no cap. 1, voltou a ele no cap. 4 ("esta é a hora de voltar à palavra") e nas duas vezes terminou em "a fronteira é frágil / depende". O leitor sai sem saber. Regra: **cada termo central é definido uma vez, no lugar certo, com posição.** Exemplo bom: "Burnout, neste livro, é o da OMS: esgotamento por estresse crônico de trabalho. O resto é exaustão." A discussão acadêmica cabe numa frase ou numa nota de fim, não numa seção.
2. **Ajuda profissional repetida.** Apareceu ~8 vezes (abertura, três vezes no cap. 1, caps. 3, 5, 6, fechamento, nota). Fica chato e infantiliza. Regra: **um lugar** (uma seção concreta "Quando procurar ajuda", com sinais específicos) **+ o contato de crise** (CVV 188) onde o tema pedir. Fora dele, zero lembrete. Exceção: risco específico que muda a conduta do capítulo, dito uma vez, de forma concreta ("se os sintomas pioram depois do esforço, esse conselho não vale para você").
3. **Meta-hedges proibidos:** "sem alarmismo", "com cautela", "com honestidade", "vale lembrar", "é importante ressaltar", "convém notar", "cabe uma ressalva". Se a ressalva é real, ela já está dentro da frase. Se não está, a frase não precisava dela.
4. **Posição antes de cuidado.** O texto toma partido primeiro e só depois qualifica, quando a qualificação muda o que o leitor faz. Ordem proibida: ressalva → ressalva → afirmação tímida.
5. **Concretude.** Cada capítulo assume uma ideia, um dado e um exemplo e fica com eles. Preferir o número ao adjetivo, a cena à categoria, "faça X" a "pode ser útil considerar X".
6. **Repetição estrutural.** Se um capítulo "retoma" o anterior, ele só pode retomar para *avançar*, nunca para refazer.

### Teste da versão confiante (nome do Raffa, 2026-10-29)

Ao revisar, reescreva cada seção que hesita **como se tivesse certeza** e compare com a original. A comparação mostra onde o texto estava com medo. Três movimentos:

1. **Afirmar na primeira ou na segunda frase.** A definição ou a tese vem antes de qualquer contexto.
2. **Dar um critério de decisão que o leitor possa aplicar** (regra, teste, pergunta), antes de qualquer ressalva. Exemplo: "três marcas, um contexto".
3. **Cortar a frase de desconfiança sem fonte.** Se a dúvida não está numa fonte e não muda o que o leitor faz, sai. Exemplo cortado: "um questionário de internet não o confirma".

Se a versão confiante não distorce a evidência, ela **substitui** a original. Se distorce, fica o que a evidência sustenta, dito com a mesma firmeza. Exemplo de referência (burnout, vol. 01): a v1 definia a palavra duas vezes e terminava em "conceitualmente frágil" e "depende"; a versão confiante diz que burnout é o que a OMS define (três dimensões, contexto de trabalho), que quem está exausto sem as três marcas está esgotado, e que o termo não vale fora do trabalho. A discussão com a depressão fica numa frase na nota editorial.

### Contra o molde: cada livro com forma própria (Raffa, 2026-10-29)

Os vols. 01 e 02 saíram com o mesmo esqueleto: cena, estudo com número, citação "para levar", exercício opcional e "no próximo capítulo", mais uma abertura com o mesmo bloco de combinações e a metáfora da "conta". O Raffa notou a repetição. Regras a partir do vol. 03:

- **Forma por capítulo, não por série.** Cada capítulo escolhe a forma que o assunto pede: diálogo, instruções satíricas, verbetes de dicionário, lista de decisões, carta, perguntas e respostas, cena curta, dado seco. Nem todo capítulo leva cena, estudo, citação final ou exercício.
- **Abertura enxuta, uma por livro.** As combinações ("não faz diagnóstico", "cenas ilustrativas", "exercício opcional") vão para a nota editorial. A abertura traz a cena ou o gancho, a aposta e as definições, escritos de modo diferente em cada volume.
- **Uma metáfora central por livro, sem herdar a do anterior.** Vol. 01: a conta. Vol. 02: o controle e o espaço. Vol. 03: a régua. Os próximos precisam de outra.
- **Raffa odeia disclaimer medroso (2026-10-29: "parece medo, justificando demais").** Vale para o livro inteiro, não só para a abertura:
  - **Frase-assinatura aposentada.** Nada de "Este livro não pretende ensinar você a viver..." na abertura ou no fechamento. Os vols. 01 e 02 a mantêm por decisão dele ("deixa original"); do vol. 03 em diante ela não entra.
  - **Nada de bloco de "combinações"** na abertura ("não faz diagnóstico", "as cenas são ilustrativas", "o exercício é opcional").
  - **Uma única nota editorial, curta e informativa:** o que o livro é, o que é inventado ou sátira, onde estão as fontes, e uma frase de que não substitui consulta ou tratamento. Sem seção por assunto ("Sobre os limites", "Sobre as definições", "Sobre os exemplos"...).
  - **Frases proibidas no texto, além dos meta-hedges já listados:** "este livro não substitui...", "sem pretensão de...", "cenas compostas, sem pretensão de caso real" (dentro do capítulo), "vale ressaltar que", "é preciso deixar claro", "que fique claro", "não é recomendação individual", "este é o único trecho que diz isso", "uma observação deste livro, e não um dado de pesquisa" (basta "observação do livro:").
  - **A precisão não some, muda de lugar.** O limite de um estudo entra numa oração, no ponto em que muda a conclusão, e só aí. Exemplo bom: "o alcance é limitado: são cenas de erro e de teste, e não um estudo sobre descanso".
  - **Checagem final:** `grep -n -i -E "não substitui|sem pretensão|vale ressaltar|que fique claro|é preciso deixar claro|recomendação individual" chapters/*.md` deve voltar vazio, exceto na nota editorial (uma ocorrência).
- **Exercício: no máximo um ou dois por livro**, nomeado de modo diferente em cada um (não "Um exercício opcional" em todo capítulo).
- **Fechamento com forma própria** (uma cena curta, uma lista, um parágrafo só), sem "no começo dissemos" nem "se você levar uma só ideia".
- **Tom:** humor leve é bem-vindo (ironia, sátira de si mesmo), sem exagero e sem sacrificar a precisão. Piada nunca entra no lugar de dado, e o que é sátira é declarado na nota editorial.
- **Checagem final:** contar, por livro, citações finais (`^> `), "exercício opcional", "no próximo capítulo", "leia de novo", "repare" e o substantivo da metáfora (ex.: "conta"). Valores altos repetidos entre os livros são sinal de molde.

### Checklist de revisão final (antes de commitar)

```bash
cd originals/<livro>
# termos centrais: quantas vezes aparecem e onde são definidos
grep -c -i "<termo>" chapters/*.md
# ajuda profissional: deve cair em UM lugar (+ CVV)
grep -n -i -E "profissional|procure|avaliação clínica|um médico|olhar clínico" chapters/*.md
# meta-hedges
grep -n -i -E "sem alarmismo|com cautela|com honestidade|vale lembrar|é importante ressaltar|convém notar|cabe uma ressalva|ressalva" chapters/*.md
# teste da versão confiante: cada seção que hesita foi reescrita com certeza e comparada?
# disclaimers medrosos (esperado: vazio, fora uma ocorrência na nota editorial)
grep -n -i -E "não substitui|sem pretensão|vale ressaltar|que fique claro|é preciso deixar claro|recomendação individual" chapters/*.md
# manuscrito gerado reproduz os capítulos e git está limpo
python3 build_manuscript.py && git diff --check
```

Aceite: o termo central tem uma definição com posição; a orientação de ajuda aparece em um lugar; nenhum meta-hedge sobrou; cada
capítulo tem uma ideia memorável nomeável em uma frase; as afirmações de saúde estão no `revisao-factual`.

### Outras decisões do vol. 01 que valem como padrão

- **Narrador coletivo** ("vamos"), sem "eu" de autor e sem credencial inventada. Assinatura "Sharebook Originals, ano". Nunca inventar nome de autor, revisor ou citação. Pendência do Raffa: declarar ou não apoio de IA na nota editorial.
- **Vinhetas compostas** declaradas como ilustrativas; números hipotéticos assumidos como tal.
- **Exercícios:** poucos, curtos, sempre opcionais, só se úteis.
- **Remissões a outros volumes:** discretas, sem título.
- **Tamanho:** ~230 palavras/página no preset 4:5; 8.400 palavras de corpo + 900 de fontes ≈ 44–50 páginas. A extensão serve ao conteúdo.
- **Sinopse** no modo clique: gancho em até 2 linhas, promessa + 1 detalhe concreto verificável do livro, chamada emocional. Sem "(a)" de gênero: reformular.

## Estrutura sugerida de arquivos

Exemplo saudável:

```text
playbooks/importers/escrever-livros/
  escrever-livros/
    meu-livro-manuscrito-v1.md
    meu-livro-book.html
    meu-livro-book.pdf
    assets/
      meu-livro-capa.png
      cover-prompt.txt
```

## Anti-padrões

- tentar resolver tudo só com Markdown cru e rezar para o PDF sair bonito
- usar SVG manual para “arte bonita” ou diagrama sedutor
- insistir em infográfico de IA quando a lógica/texto ainda estão tortos
- aceitar capa local pior só porque o pipeline é mais automático
- deixar o PDF final com header/footer de navegador
- tratar arquivo gerado como vitória antes de abrir e olhar

## Heurística de decisão

Quando houver dúvida:

1. O texto já está editorialmente pronto?
2. A capa está realmente forte ou só “ok”?
3. O visual extra ajuda mesmo ou só aumenta risco?
4. O HTML está mais bonito do que a versão anterior?
5. O PDF final parece livro ou parece exportação?

## Frase de bolso

No Sharebook, livro digital bom não nasce de automação cega. Nasce de texto bem costurado, capa forte e PDF limpo.
