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
- **Skill Editorial:** Reescruta completa da skill `sharebook-baixelivros-editorial-preparer` para o modo "Ultra Lean" (Zero Tool).

## Decisões tomadas
- **Deduplicação na Triagem:** Mover a responsabilidade de evitar duplicatas para a fase de triagem (Python) para economizar tokens do agente de IA.
- **Contexto no Banco:** Armazenar todo o texto necessário para a sinopse no campo `metadata_json` da fila, eliminando a necessidade de o agente baixar PDFs ou abrir URLs.
- **Categorias Hardcoded:** Embutir a árvore de categorias diretamente na Skill para evitar chamadas de API desnecessárias.

## Contexto relevante
- A sinopse de 3 parágrafos foi mantida por exigência editorial, mas agora é gerada a partir de um resumo pré-processado de 2000 palavras.
- O agente agora realiza apenas 2 operações de banco: uma leitura para obter o contexto e uma escrita para salvar o plano.

## Fricções e soluções
- **PowerShell Syntax:** O uso de `&&` no `run_shell_command` falhou devido ao ambiente Windows/PowerShell. Corrigido usando `;` para encadeamento de comandos Git.

## Como me senti
Este ciclo foi extremamente satisfatório por focar na eficiência técnica pura. A ideia de "mastigar" o contexto na triagem para que a IA atue apenas como um tomador de decisão é uma aplicação clássica de otimização de custo-benefício em sistemas de LLM.

Senti que a colaboração foi fluida, especialmente ao concordarmos em mover a responsabilidade de deduplicação para o código Python, o que é muito mais robusto e barato que tentar fazer via prompts complexos.

A sensação final é de uma arquitetura muito mais profissional e escalável, onde cada peça (triagem mecânica vs curadoria humana/IA) faz exatamente o que é melhor nela.
