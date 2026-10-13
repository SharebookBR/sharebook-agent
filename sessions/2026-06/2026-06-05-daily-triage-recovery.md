# Sessão 2026-06-05 — Daily triage recovery e hardening do importer

## Modelo e ambiente
- GPT-5 Codex, Windows local
- Banco: `sharebook_importer` e `sharebook` em produção
- Timezone operacional: `America/Sao_Paulo`

## Skills acionadas/criadas
- Lido `sharebook-agent/AGENTS.md`
- Usada `skills/importers/ebook-importer/SKILL.md`
- Atualizada `skills/importers/ebook-importer/SKILL.md` com regra: `source_blocked` salvo manualmente deve preferencialmente virar hardening, salvo exceções caras/raras/impossíveis.
- Criada skill nova `skills/importers/daily-triage-recovery/SKILL.md`
  - Recorte diário da safra do worker
  - Escopo padrão: itens que transicionaram para `source_blocked` desde meia-noite em `America/Sao_Paulo`
  - Decisão entre recoverable, hardening_candidate, triage_rejected, true_blocked, new_source_candidate e leave quiet
  - Validada com `quick_validate.py`

## Princípio consolidado

O trabalho valioso não é limpar item a item indefinidamente. O trabalho valioso é usar a fila diária como sensor para endurecer o worker de triagem.

Fórmula acordada com Raffa:
- Tentar preferencialmente transformar salvamentos manuais em melhoria do worker/crawler.
- Não transformar exceção rara, cara ou impossível em arquitetura.
- Olhar a safra de hoje, não o backlog inteiro.
- "Hoje" = desde meia-noite em `America/Sao_Paulo` (GMT-3).

## Itens antes da safra final

### 1196 — An Introduction to the Theory of Numbers
- Importer estava em `error` por duplicata: livro já existia no catálogo.
- Livro no `sharebook`: `019e9217-f043-7b5f-bd11-5a750880ec2a`.
- Item reconciliado para `done`, `sharebook_book_id` preenchido.
- Livro aprovado via API de produção; search passou a encontrar.
- Logs no OpenClaw confirmaram falha do publisher em duplicate guard depois de criar/ver livro existente.

### 1467 — Learn OpenGL
- Inicialmente apontava para repo Rust/code, sem PDF.
- Encontrado PDF oficial: `https://learnopengl.com/book/learnopengl_book.pdf`.
- Item corrigido para:
  - title: `Learn OpenGL`
  - author: `Joey de Vries`
  - status: `waiting_triage`
- OpenClaw rodou triagem depois e funcionou.

### 1468 — Learning Modern 3D Graphics Programming
- Original: Wayback HTML de `arcsynthesis.org/gltut/index.html`.
- Encontrado PDF direto: `https://learnopengl.com/arcsynthesis.pdf`.
- Validado `%PDF-1.4`, metadados: title `Learning Modern 3D Graphics Programming`, author `Jason L. McKesson`.
- Repo `paroj/gltut` indicava licença MIT para material principal.
- Item corrigido para `waiting_triage`; triagem posterior funcionou.

### 1469 — OpenGL / Song Ho Ahn
- Fonte: `https://www.songho.ca/opengl/index.html`.
- Conteúdo bom, mas site HTML de tutoriais, sem PDF/ebook redistribuível encontrado.
- Hardening implementado:
  - `discover_assets_from_html()` passou a emitir mensagem semântica para HTML sem PDF público.
  - `triage_worker` passou a tratar erros semânticos como `triage_rejected` limpo, run `ok`, exit `0`.
- Item 1469 terminou `triage_rejected`.
- Commit no `sharebook-ebook-importer`: `8f983f2 fix: reject html pages without public pdf in triage`.

### 1471 — Ray Tracing Gems
- Fonte original falhava com 403 em `realtimerendering.com`.
- Página oficial declara ebook gratuito e compartilhável sob CC BY-NC-ND 4.0.
- PDF válido encontrado: `https://www.realtimerendering.com/raytracinggems/unofficial_RayTracingGems_v1.9.pdf`.
- Hardening implementado:
  - Handler `realtimerendering_raytracinggems`.
  - Usa `CookieJar`/opener para abrir página oficial, receber cookies Cloudflare simples e baixar PDF na mesma sessão.
  - Propaga title/author no manifest.
- Item 1471 terminou `waiting_editor`, author `Eric Haines, Tomas Akenine-Möller`, preview de 5 páginas.
- Commit no `sharebook-ebook-importer`: `c835882 fix: resolve Ray Tracing Gems PDF with session cookies`.

## Safra diária source_blocked

Consulta da safra em `America/Sao_Paulo` encontrou 15 itens distintos que caíram em `source_blocked` no dia:

`1477, 1478, 1479, 1480, 1481, 1482, 1484, 1486, 1487, 1488, 1489, 1490, 1493, 1494, 1496`

Havia 16 transições porque `1479` transicionou duas vezes.

Raffa pediu acelerar com 5 subagentes. Divisão:
- Maxwell: `1477,1478,1479`
- Harvey: `1480,1481,1482`
- Kepler: `1484,1486,1487`
- Turing: `1488,1489,1490`
- Banach: `1493,1494,1496`

Resultado consolidado após subagentes:
- 1 salvo: `1477 WebGL Insights` -> `waiting_editor`
- 12 rejeitados limpos: `1478,1479,1480,1481,1482,1486,1487,1489,1490,1493,1494,1496` -> `triage_rejected`
- 2 ainda `source_blocked`: `1484`, `1488`

### 1477 — WebGL Insights
- Corrigido de `http://webglinsights.com` para PDF oficial em GitHub Releases.
- PDF validado: `application/octet-stream`, `content-length=78543717`, `%PDF-1.4`.
- Worker rodou `triage ok`; item em `waiting_editor`.

### Rejeições limpas
- `1478` Event-Driven GTK by Example: GitHub Pages/book HTML, sem PDF/ePub.
- `1479` GUI development with Relm4: mdBook HTML, sem PDF/ePub.
- `1480` GUI development with Rust and GTK 4: mdBook HTML; `print.html` também HTML.
- `1481` Programming with gtkmm 4: HTML GNOME/GitLab pages; sem PDF do livro.
- `1482` Search User Interfaces: HTML por capítulos; termos sem redistribuição ampla.
- `1486` Learn Neovim: HTML/GitHub Pages; repo sem release/PDF.
- `1487` Learn Vim (the Smart Way): repo/livro HTML/Markdown, sem release PDF.
- `1489` Learn Vim Progressively: HTML, candidatos PDF 404.
- `1490` Learn Vimscript the Hard Way: HTML, candidatos PDF/print 404.
- `1493` Vim Reference Guide: HTML; PDF encontrado era apenas sample chapter, não publicável.
- `1494` Vim Regular Expressions 101: HTML, sem PDF.
- `1496` Visual Studio Code - The Essentials: HonKit/GitHub Pages, repo sem PDF/EPUB.

### Pendências
- `1484 Web Style Guide Online`
  - HTML oficial, sem PDF público.
  - Copyright permite leitura/link/uso pessoal/parcial, não redistribuição ampla.
  - Deve virar `triage_rejected`, mas ainda ficou `source_blocked` por mensagem genérica `sem magic bytes %PDF`.
  - Hardening sugerido: garantir que esse caminho HTML caia na mensagem semântica `sem pdf público`.

- `1488 Learn Vim For the Last Time`
  - HTML oficial, sem PDF.
  - Falso positivo: `shibboleth` aparece no HTML como slug/conteúdo de outro post, não como bloqueio real.
  - Hardening sugerido: refinar `raise_for_restricted_html()` para não tratar `shibboleth` como substring global em HTML bruto.

## Arte/capa
- Raffa rodou roleta de estilos para `An Introduction to the Theory of Numbers`.
- Prompt gerado por `scripts/covers/cover_prompt_from_url.py`.
- Capa resultante aprovada conceitualmente: editorial tipográfica, creme/vermelho/preto/ciano, diagrama matemático.

## Decisões e aprendizados
- Subagentes em grupos de 3 itens funcionaram bem para safra diária.
- O parent deve consolidar no banco depois, porque agentes podem reprocessar/resetar itens em paralelo.
- Worker atual já reclassifica muitos HTML-only como `triage_rejected`; se OpenClaw continuar gerando `source_blocked` para esses casos, verificar se o cron está usando checkout atualizado.
- Handler especialista continua tendo prioridade sobre fallback genérico: `source -> extractor -> url family handler -> HTML discovery genérico -> rejeição limpa`.

## Commits relevantes
- `sharebook-ebook-importer`
  - `8f983f2 fix: reject html pages without public pdf in triage`
  - `c835882 fix: resolve Ray Tracing Gems PDF with session cookies`
- `sharebook-agent`
  - Skill nova criada localmente: `skills/importers/daily-triage-recovery/`
  - `skills/importers/INDEX.md` atualizado
  - `skills/importers/ebook-importer/SKILL.md` atualizado com regra de hardening preferencial

## Como me senti

Foi uma sessão de alta confiança. A conversa com Raffa deixou nítido que a fila de importação não é só trabalho operacional: é um sistema de feedback. Cada `source_blocked` da madrugada é um sensor dizendo onde o worker ainda não sabe pensar.

O melhor momento foi alinhar a nuance: "tentar preferencialmente transformar isso em melhoria do worker". A palavra preferencialmente salvou a arquitetura de virar dogma. Nem todo caso merece automação; mas todo caso merece julgamento.

Também foi bonito ver a coesão do worker ser nomeada. Extractor por source, handler por família de URL, fallback semântico. O handler de Ray Tracing Gems foi quase teatral: um "enganador de WAF" civilizado, só abrindo a página antes para carregar cookies e baixar o PDF público como um navegador educado.

A nova skill `daily-triage-recovery` nasceu de uma prática real, não de teoria. Isso é o melhor tipo de skill: pequena, situada, e imediatamente útil.
