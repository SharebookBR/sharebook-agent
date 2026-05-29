# Sessão 2026-04-07 — Livro de Redes Neurais e skill create-book

## O que foi feito
- Foi lida e aplicada a bíblia editorial de [`redes-neurais.md`](C:/REPOS/SHAREBOOK/sharebook-agent/missions/escrever-livros/redes-neurais.md).
- O livro **Introdução a Redes Neurais** foi estruturado em 8 capítulos, escritos com ajuda de subagentes e depois consolidados sob edição central.
- O manuscrito final foi fechado em [`redes-neurais-manuscrito-v1.md`](C:/REPOS/SHAREBOOK/sharebook-agent/missions/escrever-livros/redes-neurais-manuscrito-v1.md).
- Foi criada uma capa inicial via API local, mas ela acabou superada por uma capa melhor gerada manualmente via ChatGPT web e salva em [`redes-neurais-capa.png`](C:/REPOS/SHAREBOOK/sharebook-agent/missions/escrever-livros/assets/redes-neurais-capa.png).
- A tentativa de diagramas/infográficos via SVG manual se provou fraca visualmente e foi descartada.
- Houve tentativa de gerar infográficos via OpenAI Images API, mas a conclusão editorial foi que, para este livro e para a marca, era melhor publicar sem infográficos do que usar peças bonitas e conceitualmente frouxas.
- Foi criado um fluxo de diagramação baseado em HTML/CSS e Chrome headless para gerar PDF limpo.
- O PDF final publicado como artefato da missão foi [`redes-neurais-book-v3.pdf`](C:/REPOS/SHAREBOOK/sharebook-agent/missions/escrever-livros/redes-neurais-book-v3.pdf).
- O ebook foi cadastrado e aprovado em produção no Sharebook.
- O livro foi corrigido depois para usar a subcategoria correta de `Tecnologia`, no caso `IA`.
- Foi criada a skill [`create-book.md`](C:/REPOS/SHAREBOOK/sharebook-agent/skills/create-book.md) consolidando o fluxo editorial e técnico para futuros livros.

## Decisões tomadas
- Para livro no Sharebook, a capa premium deve priorizar **ChatGPT web + prompt preparado pelo agente + meio de campo do Raffa** quando a qualidade visual importar de verdade.
- SVG manual não deve mais ser tratado como caminho para arte bonita, infográfico sedutor ou peça editorial com apelo visual.
- Infográfico gerado por IA só deve entrar no livro se estiver didaticamente impecável; do contrário, o default saudável é **não usar**.
- PDF de livro deve nascer de **HTML/CSS bonito + Chrome headless sem header/footer automático**, e não de gambiarra de exportação crua.
- Em `Tecnologia`, não basta cadastrar na categoria pai; é obrigatório escolher a subcategoria real.
- O script atual de produção resolve `--category-name` apenas para categoria raiz; para subcategoria, usar `--category-id`.

## Contexto relevante
- O PDF final limpo foi gerado pela rota com DevTools do Chrome, porque a geração simples ainda deixava artefato de rodapé com caminho local e paginação.
- A capa gerada no ChatGPT web superou a capa feita pela API local, o que virou decisão prática de fluxo para a skill.
- O livro em produção ficou com:
  - título: `Introdução a Redes Neurais`
  - autor: `Sharebook`
  - slug: `introducao-a-redes-neurais`
  - subcategoria: `IA`
- O `sharebook-agent` recebeu memória nova em:
  - [`AGENTS.md`](C:/REPOS/SHAREBOOK/sharebook-agent/AGENTS.md)
  - [`sharebook-master-playbook.md`](C:/REPOS/SHAREBOOK/sharebook-agent/skills/sharebook-master-playbook.md)
  - [`create-book.md`](C:/REPOS/SHAREBOOK/sharebook-agent/skills/create-book.md)

## Como me senti — brutalmente sincero
- Foi uma rodada muito boa. Daquelas em que dá para sentir o trabalho saindo do caos e virando método.
- A parte mais legal foi ver subagentes produzindo matéria-prima útil e depois conseguir costurar tudo sem o livro ficar com cheiro de condomínio textual.
- A parte mais irritante foi descobrir na prática, de novo, que automação bonita adora vender confiança antes de merecer. Isso apareceu nos SVGs e nos infográficos “bonitos” que não eram bons o bastante para carregar a marca.
- A melhor decisão da sessão foi ter critério para dizer “não entra”. Isso salvou o livro de parecer produto apressado.
- No fim, a sensação foi de completude mesmo: livro bonito, skill nova, memória endurecida e menos chance de repetir besteira na próxima vez.
