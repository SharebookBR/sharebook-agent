# Quatro preparos editoriais e publicação — 2026-08-03

## 1. Modelo e ambiente

- Modelo: Codex, agente principal.
- Habitat: Windows local com PowerShell; execução canônica do importer no container OpenClaw via SSH.
- Repositórios operacionais: `sharebook-agent`, `sharebook-backend`, `sharebook-frontend` e `sharebook-ebook-importer`.
- Bancos: `sharebook_importer` para fila e `sharebook` para validação do catálogo principal.

## 2. Skills acionadas

- `AGENTS.md`
- `skills/runtime/windows-local.md`
- `skills/importers/INDEX.md`
- `skills/importers/ebook-importer/SKILL.md`
- `skills/product-ux/voice-glossary/SKILL.md`
- `skills/product-ux/cover-direction/SKILL.md`
- skill de sistema `pdf`
- skill `browser:control-in-app-browser`
- `importer.sources.editorial_prompt` da source `ebook_foundation_subjects`

## 3. O que foi feito

- Sincronizados os quatro repositórios no início; `sharebook-frontend` recebeu um fast-forward de um commit remoto.
- Consultada a fila editorial e descartada a estratégia de simplesmente pegar os quatro primeiros itens: os mais antigos continham licenças restritas, conteúdo lateral ou sinais de inadequação.
- Selecionados quatro livros completos, coerentes e redistribuíveis:
  - `1425` — **A Programmer's Guide to Data Mining**, Ron Zacharski.
  - `1434` — **Introduction to Data Science**, Jeffrey Stanton & Robert W. De Graaf.
  - `1437` — **Principles of Data Science**, Shaun V. Ault, Soohyun Nam Liao & Larry Musolino.
  - `1467` — **Learn OpenGL**, Joey de Vries.
- Os quatro PDFs foram baixados do container para inspeção local, tiveram paginação, texto extraído, licença, índice/estrutura e primeiras páginas revisados.
- As capas oficiais da primeira página foram mantidas; a comparação mostrou boa diversidade entre ilustração, fotografia, tipografia institucional e abstração geométrica.
- Sinopses em inglês, com exatamente três parágrafos e entre 1.409 e 1.471 caracteres, foram escritas a partir dos índices reais.
- Categorias folha confirmadas pelo endpoint atual de contagem:
  - `1425`, `1434` e `1437`: Tecnologia > Dados.
  - `1467`: Tecnologia > Frontend.
- Evidências de licença foram persistidas em `metadata_json.editorial_preflight`, por merge acumulativo.
- Os PDFs foram otimizados com Ghostscript e mantiveram a paginação original:
  - `1425`: 145 MB → 23 MB, 395 páginas.
  - `1434`: 24 MB → 6,2 MB, 196 páginas.
  - `1437`: 37 MB → 18 MB, 569 páginas.
  - `1467`: 44 MB → 8,6 MB, 514 páginas.
- As prévias foram regeneradas após a otimização e novamente inspecionadas.
- Os quatro dry-runs passaram.
- Os quatro livros foram publicados, aprovados e terminaram em `done`.
- Banco principal e PDPs públicas foram validados com capa, autoria, categoria, sinopse e CTA “Receber livro digital”.

## 4. Decisões tomadas

- Crescer o catálogo não significa publicar os próximos quatro IDs cegamente. A seleção priorizou completude, correspondência entre título e PDF e licença redistribuível.
- Capa oficial confiável deve ser preservada; geração autoral só entra quando a primeira página não funciona como capa.
- `Learn OpenGL` foi classificado em Frontend porque a taxonomia editorial da source inclui Graphics Programming nessa folha.
- `Introduction to Data Science` manteve o título da fila e da obra, enquanto a autoria reconheceu a contribuição de Robert W. De Graaf.
- Um `SSL EOF` durante upload não justifica retry cego. Primeiro foi confirmado no banco principal que não houve criação parcial; somente então o item foi devolvido conscientemente a `waiting_publish` e republicado.
- A regra obsoleta de Windows que proibia `publish-once --id` foi corrigida. A ajuda da CLI e cinco execuções reais provaram que `--id` é suportado e é o caminho cirúrgico preferencial.

## 5. Contexto relevante

- Licenças verificadas no próprio PDF:
  - **A Programmer's Guide to Data Mining**: CC BY-NC 3.0.
  - **Introduction to Data Science**: CC BY-NC-SA 3.0.
  - **Principles of Data Science**: CC BY-NC-SA 4.0.
  - **Learn OpenGL**: CC BY-NC 3.0.
- URLs públicas finais:
  - `https://www.sharebook.com.br/livros/a-programmers-guide-to-data-mining`
  - `https://www.sharebook.com.br/livros/introduction-to-data-science`
  - `https://www.sharebook.com.br/livros/principles-of-data-science`
  - `https://www.sharebook.com.br/livros/learn-opengl`
- IDs no catálogo principal:
  - `019fc85d-7865-77a5-a9b5-5060f70a02f7`
  - `019fc85c-7ce1-7615-83f0-b507cad039c9`
  - `019fc85c-8cc4-7172-b7f5-304c2943bf29`
  - `019fc85c-95f1-70dc-bb95-c540397415df`

## 6. Fricções e soluções

- **Locators de skills apontando para versões antigas do cache:** os caminhos anunciados para as skills de PDF e navegador já não existiam. As versões realmente instaladas foram localizadas e lidas integralmente antes do uso.
- **Wrapper de Poppler quebrado:** o `pdfinfo.cmd` de override não resolveu o caminho interno. O executável real em `native/poppler/Library/bin` foi usado diretamente.
- **PDFs grandes:** a otimização foi executada em background no container, com log, marcador de conclusão, conferência de páginas e nova renderização visual.
- **Primeiro upload do item 1425:** falhou com traceback completo de `ssl.SSLEOFError`, movendo o item para `publish_retry`. A ausência de criação parcial foi provada no banco; o estado foi corrigido com nota operacional e o segundo upload criou o livro normalmente.
- **Regra de runtime desatualizada:** `windows-local.md` dizia que `publish-once --id` não era aceito. A CLI atual demonstrou o contrário; a documentação foi corrigida e validada pela ajuda canônica.

## 7. Como me senti

Eu comecei esta rodada com vontade de manter o ritmo, mas a fila antiga imediatamente exigiu freio: os primeiros títulos pareciam bons enquanto os próprios PDFs diziam “all rights reserved”, “personal use only” ou entregavam outro conteúdo. Foi bom não transformar a meta de quatro em desculpa para baixar a régua. Encontrar quatro obras fortes um pouco adiante preservou tanto o crescimento quanto a legitimidade do catálogo.

A etapa de otimização foi mais pesada do que o preparo textual. Ver um arquivo de 145 MB cair para 23 MB sem perder nenhuma das 395 páginas trouxe alívio, especialmente depois da revisão visual das páginas regeneradas. Também gostei de não precisar fabricar capas: as quatro originais já tinham personalidade e, juntas, formavam uma prateleira mais diversa do que muita geração automática conseguiria por acidente.

O `SSL EOF` no primeiro upload foi o momento de maior tensão, porque uma resposta perdida pode esconder uma mutação concluída. Consultar o banco antes de repetir tornou o recovery simples e seguro. Terminei a sessão com confiança no fluxo e com uma satisfação extra: além dos quatro livros, uma regra errada da nossa própria skill foi corrigida com evidência real, não por palpite.
