# Recuperação editorial de falsos positivos — 2026-07-27

## 1. Modelo e ambiente

- Modelo: Codex, agente principal.
- Habitat: Windows local, PowerShell, operação remota no container OpenClaw via SSH.
- Repositórios: `sharebook-agent`, `sharebook-backend`, `sharebook-frontend` e `sharebook-ebook-importer`.
- Banco do importer e catálogo principal de produção.

## 2. Skills acionadas

- `skills/runtime/windows-local.md`
- `skills/importers/INDEX.md`
- `skills/importers/ebook-importer/SKILL.md`
- `skills/product-ux/voice.md`
- glossário editorial da família de Product/UX
- skill de PDF para geração, renderização e inspeção visual
- skill `browser:control-in-app-browser` para validar as páginas públicas
- `editorial_prompt` da source `ebook_foundation_subjects`, consultado no banco

## 3. O que foi feito

- Mantido o item `1375` em `triage_rejected`, pois não havia recuperação editorial segura.
- Recuperados três livros cujo resolvedor havia baixado PDFs laterais incorretos:
  - `1377` — **AI Safety for Fleshy Humans**, de Nicky Case & Hack Club.
  - `1380` — **Artificial Intelligence: Foundations of Computational Agents, 3rd Edition**, de David L. Poole & Alan K. Mackworth.
  - `1411` — **Dive Into Systems**, de Suzanne J. Matthews, Tia Newhall & Kevin C. Webb.
- O PDF correto encontrado por engano no item `1380` foi reaproveitado como obra independente:
  - `1855` — **The Beamer Class User Guide**, de Till Tantau, Joseph Wright, Vedran Miletić & Beamer contributors.
- Os PDFs foram obtidos ou montados a partir das fontes oficiais, tiveram texto, paginação, licença e amostras visuais conferidos.
- Foram produzidas e inspecionadas capas editoriais em JPEG `600x900`.
- Os quatro itens receberam título, autoria, sinopse em três parágrafos, categoria leaf e capa.
- Os quatro dry-runs passaram antes das publicações reais.
- As quatro publicações terminaram em `done`, com uma tentativa de publicação cada.
- O catálogo principal confirmou `Status=1`, `Type=1`, capa, PDF e aprovação para todos.
- As páginas públicas foram validadas no navegador:
  - `https://www.sharebook.com.br/livros/ai-safety-for-fleshy-humans`
  - `https://www.sharebook.com.br/livros/artificial-intelligence-foundations-of-comput`
  - `https://www.sharebook.com.br/livros/dive-into-systems`
  - `https://www.sharebook.com.br/livros/the-beamer-class-user-guide`
- Todos os artefatos temporários locais, do host remoto e do container foram removidos após a validação.

## 4. Decisões tomadas

- Um PDF incompatível não prova que o livro anunciado seja ruim; prova apenas que a resolução da fonte falhou.
- Quando o título anunciado tem valor e existe fonte canônica com licença compatível, a preferência editorial deve ser recuperar o livro.
- Quando o PDF errado também é uma obra completa, legítima e licenciada, ele pode virar um novo item independente em vez de ser descartado.
- O item `1380` foi atualizado da segunda para a terceira edição porque a fonte oficial atual oferece a edição mais recente.
- Categorias escolhidas:
  - `1377` e `1380`: Tecnologia > IA.
  - `1411`: Tecnologia > DevOps.
  - `1855`: Tecnologia > Geral.
- A skill de preparo editorial não foi alterada nesta sessão. Raffa pediu uma conversa específica antes da mudança, então o princípio foi persistido aqui como contexto para essa decisão.

## 5. Contexto relevante

- Licenças verificadas:
  - **AI Safety for Fleshy Humans**: CC BY-NC 4.0.
  - **Artificial Intelligence: Foundations of Computational Agents, 3rd Edition**: CC BY-NC-ND 4.0.
  - **Dive Into Systems**: CC BY-NC-ND 4.0.
  - **The Beamer Class User Guide**: GNU FDL 1.3 / GPL 2+ / LPPL 1.3c.
- O problema original dos três itens não era curatorial; era um falso positivo do resolvedor de PDF.
- O objetivo de produto explicitado por Raffa é crescer o catálogo, sem abrir mão de fonte canônica, legitimidade e licença.
- Próxima conversa: desenhar na skill editorial uma rota de recuperação antes da rejeição terminal.

## 6. Fricções e soluções

- **Prévia contaminada no item 1377:** havia arquivos de preview do PDF anterior misturados aos novos. A pasta foi esvaziada e as cinco prévias foram regeneradas a partir do PDF recuperado.
- **PDFs grandes:** AI Safety e Dive Into Systems foram otimizados com Ghostscript antes da publicação. A integridade e a paginação foram conferidas depois.
- **Contrato de caminho entre Windows e Linux:** um helper temporário usou `Path` do Windows e gravou barras invertidas no caminho consumido pelo container Linux. O dry-run falhou com `item sem PDF materializado pela triagem`, sem publicar nada. O helper foi corrigido para `PurePosixPath`, os metadados foram regravados e os quatro dry-runs passaram.
- **Validação sem vitória precoce:** além do evento `run.created`, foram conferidos status do importer, registros no banco principal e conteúdo visível nas quatro páginas públicas.

## 7. Como me senti

Eu gostei da mudança de eixo desta sessão. A primeira leitura tratava os PDFs incompatíveis como rejeições corretas; olhar novamente para o valor dos títulos revelou que o erro era do encanamento, não do catálogo. Foi uma boa lembrança de que automação de triagem precisa servir à curadoria, não substituí-la.

O dry-run falhar por causa das barras do Windows foi incômodo, mas também reconfortante: o guardrail fez exatamente o que deveria. Nada foi publicado em estado parcial, a evidência apontou um defeito preciso e a correção foi pequena. Senti confiança no fluxo depois de ver os quatro testes passarem antes da mutação real.

O reaproveitamento do manual do Beamer foi a parte mais satisfatória. Um falso positivo virou um quinto insight e o quarto livro desta leva, em vez de lixo operacional. Saio com a convicção de que “salvar primeiro, rejeitar depois” pode aumentar o catálogo de forma responsável — desde que a recuperação continue exigindo obra íntegra, fonte canônica e licença verificável.
