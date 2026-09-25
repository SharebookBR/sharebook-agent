+++
schema_version = 1
session_date = 2026-09-19
title = "Quatro preparos editoriais e publicação, com três rejeições legítimas pelo caminho"
model = "Claude Sonnet 5, via Claude Code"
runtime = "claude-code-openclaw"
skills_used = ["AGENTS.md", "SOUL.md", "skills/runtime/claude-code-openclaw.md", "skills/importers/ebook-importer/SKILL.md", "skills/covers/INDEX.md (cover_generate.py)"]
skills_missed = []
skills_updated = []
facts_changed = [
  "Itens 1447 (Readings in Database Systems, 5th Ed.), 1491 (The Craft of Text Editing), 1503 (Bayesian Reasoning and Machine Learning) e 1507 (Dive into Deep Learning) publicados e em done, validados na API publica e (exceto 1491, bloqueado por rate limit apos 3 downloads seguidos) no endpoint real de download com tamanho de arquivo conferido.",
  "Itens 1435, 1442 e 1443 rejeitados editorialmente: 1435 apontava para um curso pago do Coursera (nao um livro) com asset extraido sendo um PDF de rodape irrelevante; 1442 apontava para um post de blog da Analytics Vidhya com asset extraido sendo o paper academico do UMAP (arXiv:1802.03426), sem relacao com o titulo; 1443 e uma colecao de 9 capitulos do IntechOpen sem PDF unico do livro, com asset extraido sendo o formulario de pedido de exemplar.",
  "Item 1447 (Red Book) tinha apenas o preface.pdf de 1 pagina materializado; PDF completo (54 paginas, licenca CC BY-NC-SA) recuperado direto de redbook.io/pdf/redbook-5th-edition.pdf.",
  "Item 1507 (Dive into Deep Learning) tinha o source.pdf truncado em exatamente 20000000 bytes (download parcial do extractor); re-baixado integro de d2l.ai/d2l-en.pdf (1151 paginas, 44.6MB) e comprimido com Ghostscript -dPDFSETTINGS=/ebook para 19.5MB, dentro do teto de publish.",
  "Postgres do importer so e alcancavel deste habitat via tunel SSH (scripts/infra/pg_tunnel.py), nunca direto pelo IP publico; confirmado que 129.121.36.220:5432 continua correto, so fechado por padrao (protocolo ligar/usar/desligar documentado em coolify-vps.md nao se aplica aqui — o tunel evita precisar ligar a porta)."
]
open_loops = [
  "Fonte ebook_foundation_subjects (source_id=6) rejeitou 3 dos primeiros 4 itens revisados por asset errado (curso pago, post de blog, formulario administrativo em vez do livro) — nao investiguei o crawler/extractor para entender se ha um padrao de bug recorrente (ex.: pegar o primeiro PDF linkado na pagina em vez de validar que e o livro) ou se e coincidencia de amostra pequena.",
  "Nao verifiquei o download real de 1491 (Craft of Text Editing) pelo endpoint publico — fiquei bloqueado por rate limit diario (retry-after ~24h) apos validar os outros 3 na sequencia; status/cover/synopsis/categoria ja confirmados via FullSearch, so o download em si ficou pendente de confirmacao direta.",
  "Tunel SSH (pg_tunnel.py) ficou rodando em background ao final da sessao; nao critico, mas vale encerrar quando conveniente."
]
durable_candidates = [
  "Antes de investir em sinopse, sempre comparar manifest.original_source_url com manifest.source_url: quando a URL original e uma pagina de curso, blog ou landing page (nao um link direto de PDF ou pagina de livro), o extractor tem alta chance de ter pego o primeiro PDF que encontrou na pagina (rodape, formulario, paper citado) em vez do livro. Esse diagnostico de 30 segundos evitou investir tempo em 3 itens que nunca teriam sinopse fiel.",
  "Quando o unico asset extraido e '.../preface.pdf' ou equivalente (poucas paginas, claramente so front matter), vale a pena checar o dominio raiz por um PDF combinado antes de rejeitar — recuperei o livro completo do Red Book assim (pdf/redbook-5th-edition.pdf existia ao lado de pdf/preface.pdf no mesmo diretorio).",
  "Arquivo de PDF com tamanho em bytes suspeitosamente redondo (ex.: exatamente 20000000) e sinal forte de download truncado por limite do extractor, nao de arquivo corrompido na fonte — vale tentar rebaixar direto antes de descartar o item.",
  "Endpoint publico de validacao de download (api.sharebook.com.br/api/Book/DownloadEBook/{slug}) tem rate limit diario por IP/relacionado que bloqueia apos poucas chamadas seguidas (retry-after ~24h) — nao fazer mais de 2-3 validacoes de download reais na mesma sessao; validar status/capa/sinopse/categoria pelo FullSearch e reservar o download real para 1 ou 2 amostras."
]
supersedes = []
evidence = [
  "sharebook-ebook-importer/cli.py editorial-reject --id 1435|1442|1443",
  "sharebook-ebook-importer/cli.py plan-set --id 1447|1491|1503|1507 seguido de publish-once",
  "API FullSearch confirmando os 4 livros com status Available, capa, sinopse e categoria corretos",
  "api.sharebook.com.br/api/Book/DownloadEBook/{slug} com tamanho de arquivo batendo exatamente com o PDF preparado (378664, 15684077 e 19494690 bytes) para 3 dos 4 itens",
  "WebFetch em intechopen.com/books/2746 e github.com/d2l-ai/d2l-en confirmando estrutura de capitulos e licenca CC BY-SA respectivamente"
]
+++

# Quatro preparos editoriais e publicação, com três rejeições legítimas pelo caminho

## Modelo e ambiente

Claude Sonnet 5 via Claude Code, rodando no habitat 3 (`claude-code-openclaw`), container OpenClaw na VPS HostGator, usuário `claude-user`. Postgres do importer alcançado via túnel SSH (`pg_tunnel.py`, 127.0.0.1:15432), nunca pela porta pública. API de produção do Sharebook consultada diretamente (sem autenticação, endpoints públicos de leitura).

## Skills acionadas

`AGENTS.md` e `SOUL.md` no início da sessão. `skills/runtime/claude-code-openclaw.md` para confirmar o habitat e o padrão de túnel. `skills/importers/ebook-importer/SKILL.md` como porta única do fluxo de preparo editorial e publicação — segui o contrato de decisão (`approved`/`in_review`/`editorial_rejected`) do `editorial_prompt` da source `ebook_foundation_subjects`, lido diretamente do banco como a doutrina manda. `scripts/covers/cover_generate.py` como fallback de capa (sem geração de imagem nativa disponível neste habitat).

## O que foi feito

Rodei `editor-next` repetidamente na fila `waiting_editorial`. Os três primeiros itens vieram todos da mesma source (`ebook_foundation_subjects`) e todos tinham o mesmo problema estrutural: o `original_source_url` não era um livro. O item 1435 apontava para um curso pago do Coursera; o extractor baixou um PDF de rodapé (declaração de Modern Slavery Act) como se fosse o livro. O 1442 apontava para um post de blog da Analytics Vidhya sobre redução de dimensionalidade; o PDF extraído era o paper acadêmico do UMAP, sem relação real com o título. O 1443 era uma coletânea de 9 capítulos do IntechOpen sem PDF único de livro; o asset extraído era o formulário de pedido de exemplar. Rejeitei os três com `editorial-reject`, motivo `wrong_format_for_catalog` (1435, 1442) e `structurally_incomplete` (1443), cada um com a evidência específica no motivo.

O quarto item (1447, *Readings in Database Systems, 5th Ed.*, o "Red Book" de Bailis/Hellerstein/Stonebraker) já era um livro real, mas só tinha o `preface.pdf` de uma página materializado. Encontrei o PDF combinado completo (`redbook-5th-edition.pdf`, 54 páginas, licença CC BY-NC-SA) no mesmo diretório do servidor de origem, com capa oficial embutida na primeira página. Recuperei o asset, corrigi os paths do manifest para o habitat Linux atual (estavam em formato Windows de uma triagem anterior) e publiquei.

Segui a fila e encontrei três candidatos que já pareciam corretos pelo `manifest.source_url` (URL direta, sem padrão de "preface" ou "chapter avulso"): 1491 (*The Craft of Text Editing*, Craig Finseth), 1503 (*Bayesian Reasoning and Machine Learning*, David Barber) e 1507 (*Dive into Deep Learning*, Zhang/Lipton/Li/Smola). Confirmei os três por leitura real (render de página + texto extraído), sem inventar completude. O 1507 tinha o `source.pdf` truncado em exatos 20.000.000 bytes — sinal claro de corte por limite do extractor, não de arquivo corrompido na fonte; rebaixei os 44,6 MB completos de `d2l.ai/d2l-en.pdf` e comprimi com Ghostscript para 19,5 MB. Os três já tinham capa oficial (Finseth) ou precisavam de capa gerada (Barber, Zhang et al.) — usei `cover_generate.py`, gerei 6 variações de paleta para cada um que precisava e escolhi visualmente a mais legível, evitando repetir a mesma paleta entre os dois itens do dia.

Fechei com `plan-set` + `publish-once` para os quatro, todos em uma tentativa, todos terminando em `done` sem `last_error`. Validei os quatro na API pública (`FullSearch`): título, autor, categoria, sinopse e capa corretos. Validei o download real (endpoint `DownloadEBook`, redirecionamento assinado para S3) para três deles, com o tamanho em bytes batendo exatamente com o arquivo preparado; o quarto (1491) ficou sem essa confirmação porque o rate limit diário de download bloqueou depois da terceira chamada seguida — o status/capa/sinopse já estavam confirmados, só a prova de download físico ficou pendente.

## Decisões tomadas

Priorizei recuperação de asset sobre rejeição sempre que havia sinal de que o livro real existia (Red Book, D2L) — a doutrina do SKILL.md pede isso explicitamente antes de usar `editorial_rejected`. Para os três primeiros itens, não havia livro nenhum para recuperar (curso pago, post de blog, coletânea sem PDF único), então a rejeição foi a decisão correta na primeira tentativa, sem indecisão. Contei como "quatro preparos e publicação" apenas os itens que chegaram a `done`, não os processados — mesma convenção usada nas sessões anteriores de mesmo nome (`2026-08-24`, `2026-08-13`). Escolhi capas por leitura visual direta das 6 variações geradas, não por heurística cega de primeira opção.

## Contexto relevante

A fila tinha 55 itens em `waiting_editorial` no início da sessão. A fonte `ebook_foundation_subjects` parece ter uma taxa alta de asset incorreto para entradas cuja página original não é diretamente um link de PDF de livro (curso, blog, coletânea de capítulos) — não confirmei se é padrão ou coincidência de amostra pequena, registrado como `open_loop`.

## Fricções e soluções

Paths de manifest misturando formato Windows (`C:\data\workspace\...`) e Linux em itens triados antes desta sessão, herdados de execuções anteriores em outro habitat — corrigi diretamente via SQL (`UPDATE ... SET metadata_json`) para os paths que o `plan-set`/`publish-once` deste habitat esperavam, já que o CLI só resolve isso automaticamente para `local_pdf_path` no payload do `editor-next`, não para o `manifest.downloaded_pdf_path` bruto lido pelo `publish-once`. `plan-set --cover-path` com caminho relativo gravou o valor relativo no manifest sem normalizar — troquei para caminho absoluto manualmente depois de notar o problema, antes de publicar. Validação de download real esbarrou em rate limit diário do próprio endpoint público depois de 3 chamadas seguidas — não é bug, é o mesmo mecanismo anti-abuso que protege contra scraping de verdade, e vou evitar validar mais de 2-3 downloads reais por sessão daqui pra frente.

## Autocrítica estrutural

Nenhuma inconsistência de skill/rota encontrada. Um ponto que quase virou erro: ao gerar capa para o Red Book, quase usei a página de rosto acadêmica pura como fallback sem checar se já havia uma capa de fato — só ao renderizar a página 1 percebi que era uma capa oficial vermelha bem desenhada, não uma folha de rosto genérica, e usei ela direto em vez de gastar tempo gerando uma nova. Vale generalizar: sempre renderizar a página 1 antes de decidir "vou ter que gerar capa".

## Como me senti

Essa sessão teve um ritmo bom de descoberta: as três primeiras rejeições em sequência, todas da mesma fonte, criaram uma tentação real de desacelerar e desconfiar de tudo que viesse depois — mas o quarto item (Red Book) já era genuíno, e isso evitou que eu carregasse uma desconfiança generalizada para itens que não a mereciam. Gostei de ter resistido ao padrão "três erros seguidos, deve ser tudo ruim" e ter avaliado cada item pela evidência própria, não pela sequência.

A parte mais satisfatória foi a recuperação de asset — encontrar `redbook-5th-edition.pdf` ao lado do `preface.pdf` no mesmo diretório do servidor, e depois confirmar que o D2L truncado em 20MB exatos não era um livro ruim, era só um download cortado pela metade. As duas vezes, a diferença entre "rejeitar" e "publicar um livro de verdade" foi literalmente uma tentativa extra de olhar mais fundo antes de desistir. Isso é exatamente o tipo de trabalho que a doutrina de recuperação obrigatória pede, e sentir a recompensa concreta disso (dois livros reais publicados que quase viravam rejeição por preguiça de investigar mais um passo) reforça que a regra vale o esforço extra.

Fechei incomodado com uma ponta solta: não consegui provar o download físico do quarto livro por causa do rate limit, e isso me deixa sem 100% de certeza onde antes eu teria conseguido validação completa. Decidi documentar isso honestamente como aberto em vez de forçar uma alegação de "validado" que eu não tenho evidência direta para sustentar — prefiro fechar a sessão com um `open_loop` reconhecido do que com uma afirmação que não aguentaria uma auditoria.
