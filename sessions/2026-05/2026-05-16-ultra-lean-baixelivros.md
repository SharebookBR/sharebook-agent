# 2026-05-16 - Ultra Lean BaixeLivros Workflow

## Modelo e Ambiente
- Gemini 1.5 Pro via Gemini CLI.
- Workspace: `C:\REPOS\SHAREBOOK`.
- Repositórios afetados: `sharebook-ebook-importer` e `sharebook-agent`.

## O que foi feito
- Implementada simplificação brutal no preparo editorial do BaixeLivros.
- **Triage Worker:** Adicionada deduplicação por título via query SQL direta no PostgreSQL de produção (Read-Only).
- **Triage Worker:** Adicionada extração automatizada de contexto (primeiras 15 páginas do PDF via `pdftotext` + `og:description` da fonte).
- **Extractor BaixeLivros:** Adicionada captura de `og:description` no manifesto.
- **Skill Editorial:** Reescruta completa da skill `sharebook-baixelivros-editorial-preparer` para o modo "Ultra Lean" (Zero Tool), agora utilizando o comando concierge `editor-next`.
- **CLI Concierge:** Criado comando `python cli.py editor-next` que entrega o contexto mastigado (Título, Autor, Context Text) em JSON puro, eliminando necessidade de queries SQL manuais pelo agente.
- **Deduplicação Prod:** Implementada checagem direta no PostgreSQL de produção para evitar re-triagem de livros já existentes.

## Decisões tomadas
- **Deduplicação na Triagem:** Mover a responsabilidade de evitar duplicatas para a fase de triagem (Python) para economizar tokens do agente de IA.
- **Contexto no Banco:** Armazenar todo o texto necessário para a sinopse no campo `metadata_json` da fila, eliminando a necessidade de o agente baixar PDFs ou abrir URLs.
- **Categorias Hardcoded:** Embutir a árvore de categorias diretamente na Skill para evitar chamadas de API desnecessárias.
- **Abstração Concierge:** Fornecer ferramentas prontas (`editor-next`) para que o agente não precise conhecer a estrutura do banco de dados, focando 100% na criatividade editorial.

## Contexto relevante
- A sinopse de 3 parágrafos foi mantida por exigência editorial, mas agora é gerada a partir de um resumo pré-processado de 2000 palavras.
- O agente agora realiza o ciclo completo com apenas **2 chamadas de CLI**: `editor-next` (leitura) e `plan-set` (escrita).
- **Fallback Visual:** Identificamos PDFs "mudos" (Itaú/Kidsbook) que são 100% imagem. O agente tem permissão para usar visão como fallback nesses casos, registrando o ato no log.

## Fricções e soluções
- **PowerShell Syntax:** O uso de `&&` no `run_shell_command` falhou devido ao ambiente Windows/PowerShell. Corrigido usando `;` para encadeamento de comandos Git.
- **Encoding/Fontes PDF:** Descobrimos que layouts complexos falham em parsers simples. A solução foi injetar a descrição do site original e instruir o agente a "olhar" o PDF se necessário.

## Como me senti
Este ciclo foi "Absolute Cinema". A transformação de um fluxo artesanal e caro em uma esteira de produção industrial automatizada é a essência da engenharia de prompts e sistemas. A colaboração para abstrair a complexidade do banco em um comando concierge (`editor-next`) foi o ponto alto, provando que ferramentas bem desenhadas são o segredo para a escala e economia de tokens.

