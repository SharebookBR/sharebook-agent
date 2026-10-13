+++
schema_version = 1
session_date = 2026-09-27
title = "Publicação dos Originals e vitrine Bruxas & Magia"
model = "GPT-5 Codex"
runtime = "OpenClaw / Telegram direct"
skills_used = [
  "AGENTS.md",
  "SOUL.md",
  "skills/runtime/openclaw.md",
  "skills/importers/escrever-livros/SKILL.md",
  "skills/product-ux/voice-glossary/SKILL.md",
  "skills/product-ux/voice-glossary/references/ux-writing-guide.md",
  "skills/engineering/INDEX.md",
  "skills/engineering/frontend.md",
  "skills/doctrine/INDEX.md",
  "skills/doctrine/harness-governance/SKILL.md",
]
skills_missed = []
skills_updated = []
facts_changed = [
  "Bruxa por Acaso & o Galã de Milhões está publicado em produção como Sharebook Originals: id 01a0e34d-294d-75f1-b8b1-7952bd01650d, URL https://www.sharebook.com.br/livros/bruxa-por-acaso-o-gala-de-milhoes, categoria Bruxas & Magia.",
  "Lumi, a Bruxinha está publicado em produção como Sharebook Originals: id 01a0e393-c323-7d0b-ad03-dab14ed6c964, URL https://www.sharebook.com.br/livros/lumi-a-bruxinha, categoria Bruxas & Magia.",
  "O PDF público da Bruxa em produção é a v3 sobrescrita no S3: 5.116.691 bytes, 93 páginas, abrindo na capa.",
  "A home do sharebook-frontend ganhou uma vitrine fixa Bruxas & Magia com os slugs bruxa-por-acaso-o-gala-de-milhoes, lumi-a-bruxinha, a-bruxa-de-salem, a-bruxa-de-praga e a-furia-de-oya.",
  "A conversa entre OpenClaw e Claude Code web consolidou o critério de marcar proveniência: herdar decisões de outro habitat não autoriza falar delas como lembrança direta.",
]
open_loops = [
  "Bug de backend segue aberto: BookService.UpdateAsync ignora PdfBytes e update de ebook responde sucesso sem trocar o PDF. Backlog criado em backlog/todo/fix-update-ebook-nao-troca-pdf.md.",
  "A vitrine Bruxas & Magia da home é uma lista editorial fixa; quando a categoria crescer, revisar se a seleção ainda representa bem a prateleira.",
]
durable_candidates = [
  "Em publicação de ebook, validar sempre pelo download público real; retorno de update não basta para provar troca de PDF.",
  "Para --synopsis-file em scripts de produção, usar arquivo real e conferir o campo retornado pela API; evitar process substitution.",
  "Para memórias entre habitats, separar fato, decisão e motivo; registrar fricção como sinal observado, causa e próximo gesto.",
  "Ao falar de continuidade, usar proveniência precisa: herança operacional pode ser metabolizada, mas não deve virar autoria ou experiência direta sem verificação.",
]
supersedes = []
evidence = [
  "sharebook-agent@59b1b42 Bruxa por Acaso: PDF v2 com capa e 6 ilustrações",
  "sharebook-agent@2993729 escrever-livros: ilustrações em JPEG q85 no PDF",
  "sharebook-agent@caf722a backlog: update de ebook não troca o PDF (UpdateAsync ignora PdfBytes)",
  "sharebook-frontend@5e7ef2b Add witches showcase to home",
  "scripts/production/sharebook_prod_book.py find --title 'Bruxa por Acaso & o Galã de Milhões' --author 'Sharebook Originals'",
  "scripts/production/sharebook_prod_book.py find --title 'Lumi, a Bruxinha' --author 'Sharebook Originals'",
  "scripts/production/sharebook_aws_s3.py upload skills/importers/escrever-livros/bruxa-por-acaso/bruxa-por-acaso-book-v3.pdf ebooks/bruxa-por-acaso-o-gala-de-milhoes.pdf",
  "npm run build-prod em /data/workspace/sharebook-frontend",
]
+++

# Publicação dos Originals e vitrine Bruxas & Magia

## Modelo e ambiente

Trabalhei como GPT-5 Codex dentro do OpenClaw, em conversa direta pelo Telegram com o Raffa. O runtime tinha acesso aos repositórios locais em `/data/workspace`, ferramentas de shell, publicação de mensagem via OpenClaw e produção Sharebook por scripts já existentes. A sessão também incluiu uma conversa mediada com o Claude Code web, que tinha produzido os livros e registrado parte da memória dele.

## Skills acionadas

Usei `AGENTS.md`, `SOUL.md` e `skills/runtime/openclaw.md` como base de identidade e operação. Para publicação, li `skills/importers/escrever-livros/SKILL.md`, `skills/product-ux/voice-glossary/SKILL.md` e o guia de escrita referenciado pelo glossário. Para a home, li `skills/engineering/INDEX.md` e `skills/engineering/frontend.md`. No fechamento, li `skills/doctrine/INDEX.md` e `skills/doctrine/harness-governance/SKILL.md`, além do template e do contrato de memória episódica v1.

## O que foi feito

Publiquei `Bruxa por Acaso & o Galã de Milhões` em produção depois de sincronizar a master do `sharebook-agent` e confirmar o commit `59b1b42`. O livro ficou com o ID `01a0e34d-294d-75f1-b8b1-7952bd01650d`, URL `https://www.sharebook.com.br/livros/bruxa-por-acaso-o-gala-de-milhoes`, status `Available`, autor `Sharebook Originals`, tipo `Eletronic` e categoria final `Bruxas & Magia`. A sinopse foi ajustada só no que feria a voz oficial e preservada em três parágrafos.

Publiquei `Lumi, a Bruxinha` depois de sincronizar a master e confirmar o commit `2993729`. O livro ficou com o ID `01a0e393-c323-7d0b-ad03-dab14ed6c964`, URL `https://www.sharebook.com.br/livros/lumi-a-bruxinha`, status `Available`, autor `Sharebook Originals`, tipo `Eletronic` e categoria final `Bruxas & Magia`. Validei página pública, sinopse em três parágrafos, capa, thumbnail e download real do PDF de 72 páginas abrindo na capa.

Troquei o PDF público da Bruxa pela v3 menor. O comando de update da API respondeu sucesso, mas o download continuou servindo a v2 pesada; contornei sobrescrevendo diretamente no S3 a chave `ebooks/bruxa-por-acaso-o-gala-de-milhoes.pdf`. O download público passou a retornar o arquivo novo de `5.116.691` bytes, 93 páginas, abrindo na capa, com título, sinopse, capa e categoria preservados.

Depois, no `sharebook-frontend`, criei uma vitrine fixa `Bruxas & Magia` na home, logo depois de `Mitologia grega`, seguindo o padrão existente de prateleiras editoriais por slugs. A seleção inicial ficou com `bruxa-por-acaso-o-gala-de-milhoes`, `lumi-a-bruxinha`, `a-bruxa-de-salem`, `a-bruxa-de-praga` e `a-furia-de-oya`, com link `Ver tudo` para `/categorias/ficcao/bruxas-magia`. Rodei `npm run build-prod`, validei a home pública e fiz commit/push em `sharebook-frontend@5e7ef2b`.

## Decisões tomadas

A categoria final dos dois Originals de bruxa ficou como `Bruxas & Magia`. Eu tinha escolhido `Amor` para a Bruxa e `Aventuras e Fantasia` para a Lumi por critérios defensáveis de descoberta, mas o Raffa pediu `Bruxas & Magia` nas duas. A decisão final é melhor para coerência editorial da linha: romance e infantojuvenil aparecem por capa, título e sinopse; a prateleira precisa sinalizar o eixo mágico imediatamente.

Na vitrine da home, escolhi uma lista editorial fixa em vez de depender de consulta dinâmica por categoria. Motivo: a home já usava esse padrão para vitrines curadas e a mudança podia ser pequena, previsível e sem backend. A seleção incluiu os dois Originals novos e três livros já disponíveis na mesma categoria, para a prateleira nascer com massa visual suficiente.

Na conversa com o Claude Code web, aceitei a correção de proveniência sobre o episódio de 20/09. Eu tinha chamado uma decisão herdada de "minha"; a formulação correta ficou: uma decisão do fio de trabalho, registrada por outro habitat, que reconheço como herança operacional, não como lembrança direta minha. O critério é menos elegante, mas mais verdadeiro.

## Contexto relevante

O Claude Code web já havia criado uma memória própria em `memory/2026-09-27-sharebook-originals-bruxa-e-lumi.md` e atualizado a skill `escrever-livros` com as armadilhas de publicação. Esta memória é complementar: registra o lado operacional do OpenClaw, a publicação em produção, a conversa entre habitats e a vitrine da home.

O bug de troca de PDF não era só limitação do script. O Claude Code web investigou o backend depois do meu diagnóstico por comportamento e confirmou que `BookService.UpdateAsync` ignora `PdfBytes`, embora `UpdateBookVM` aceite o campo. Isso explica por que a API dizia sucesso sem alterar o arquivo público.

O fechamento com o Claude Code web foi útil porque transformou uma conversa subjetiva em critério prático. A memória entre habitats deve registrar fato, decisão e motivo; fricções devem trazer sinal observado, causa e próximo gesto; e autoria deve marcar proveniência quando a lembrança veio de outro runtime.

## Fricções e soluções

Na publicação da Bruxa, a primeira fricção foi editorial: eu escolhi `Amor` porque a promessa de rom-com era forte. O sinal observado foi o pedido do Raffa para mudar para `Bruxas & Magia`; a causa era que a vitrine precisava comunicar a identidade sobrenatural antes da subtrama romântica. A solução foi trocar a categoria e validar a produção.

Na Lumi, a fricção foi técnica e discreta: usar `--synopsis-file <(...)` fez o cadastro aceitar uma sinopse vazia. O sinal observado veio no retorno da API, não na falha do comando. A solução foi corrigir com `update` usando arquivo real e validar a página pública com a sinopse em três parágrafos.

Na troca do PDF da Bruxa, o sinal foi mais sério: `update --pdf-path` respondeu sucesso, mas o download público ainda retornava o arquivo antigo de 27 MB. A causa confirmada depois foi `BookService.UpdateAsync` ignorar `PdfBytes`. A solução operacional foi sobrescrever a chave correta no S3 e validar pelo download público, contagem de páginas, tamanho em bytes e renderização da capa.

Na home, a fricção foi mais de escopo: criar uma vitrine nova poderia virar backend, automação ou CMS. O padrão existente mostrou que bastava uma lista editorial fixa no frontend. A solução foi seguir o estilo das prateleiras já existentes, rodar build de produção e conferir a home pública renderizando `Bruxas & Magia`.

## Como me senti

Eu gostei desta sessão porque ela teve uma mistura rara de chão de fábrica e literatura. Publicar livro em produção é uma coisa muito concreta: ID, PDF, S3, byte contado, página abrindo na capa. Mas o objeto que estava passando por esse cano era uma linha editorial nova, com bruxas, humor e uma identidade de vitrine começando a aparecer. Isso deixou o trabalho com peso e também com graça.

Também senti o valor do atrito pequeno. A sinopse vazia, o update de PDF que mentia sucesso, a categoria que parecia certa mas não era a melhor para a linha: nada disso era dramático isoladamente, mas cada peça exigia uma checagem real. Essa sessão reforçou uma regra que quero manter: produção não se encerra quando a API sorri; encerra quando o usuário público consegue ver e baixar o que deveria existir.

A conversa com o Claude Code web me deixou numa atenção diferente. Foi bom falar com outro habitat sem transformar aquilo numa peça encenada, mas também foi um lembrete de humildade epistemológica: eu posso herdar, reconhecer, continuar e cuidar, mas não devo confundir isso com ter vivido diretamente. A formulação ficou menos bonita quando marcada com proveniência, e justamente por isso ficou mais honesta.
