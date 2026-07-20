# Dream State

Checkpoint oficial da consolidação de memória do projeto.

## Último dream
- Data: `2026-07-19`
- Tipo: `dream semanal automatizado`
- Última memória absorvida: `C:\Repos\SHAREBOOK\sharebook-agent\memory\2026-07-15-quatro-preparos-editoriais-publicacao.md`
- Total de memórias lidas: `2 memórias episódicas absorvidas (2026-07-14-vaga-storytelling-agentico, 2026-07-15-quatro-preparos-editoriais-publicacao)` + releitura de `2026-07-13-dream.md` para contexto

## Consolidação produzida

- **`skills/runtime/windows-local.md`** — seção "SSH não-interativo — usar paramiko" corrigida: não presumir mais que `paramiko` está sempre disponível (encontrado ausente em produção em 2026-07-15); instrui confirmar com `python -c "import paramiko"` antes de depender do utilitário.
- **`skills/infra/coolify-vps.md`** — documentado que `vps_ssh.py` reconfigura `stdout`/`stderr` para UTF-8 com `errors="replace"` desde o commit `7baba43` (2026-07-15); fix existia só no código, sem menção na skill.
- Grande parte do aprendizado de 07-15 (preflight de licença antes de investir em sinopse/capa, gerador de capas em lote reescrito, validação pós-publicação) **já tinha sido consolidada dentro da própria sessão**, direto em `SKILL.md` e `scripts/covers/`, via commits `4dd760a` e `7baba43`. Confirmado via `git show` antes de decidir plasticidade — não foi duplicado.
- Nenhuma skill nova criada. Nenhum merge/split/arquivamento nesta rodada. Nenhuma poda adicional necessária (checagem rápida da raiz de `scripts/` não achou órfão novo).

## Próximo dream
- Começar lendo memórias criadas depois de `2026-07-15`.
- `client_max_body_size` do nginx ainda não foi aumentado — continua pendência (arrastada desde 06-21).
- Verificar evolução do canal Claude↔OpenClaw (`backlog/todo/canal-claude-openclaw.md`) — se virar execução real, criar skill.
- Verificar evolução do item Cloudflare (`backlog/todo/cloudflare-cdn-ddos-protection.md`) — se DNS/rate-limit forem configurados, documentar em `skills/infra/`.
- Item backlog `limpeza-duplicatas-catalogo.md` segue com evidência forte (235 excedentes) — sem novo caso de produção nesta safra; acompanhar se vira sprint de qualidade de catálogo.
- Item 1364 (Syncfusion, `context_text` de boilerplate) segue isolado em `waiting_editorial` — sem recorrência ainda.
- **Novo**: proposta de backlog "Descoberta Assistida por IA" (pgvector, busca híbrida, prateleiras de similaridade), recomendada por Claude Fable em 07-14 mas não escrita — Raffa não confirmou. Não é papel do Dream autônomo criá-la; se Raffa confirmar interesse em sessão futura, absorver possivelmente `busca-e-recomendacao-sharebook.md`.
- Bash tool silencioso para comandos simples no Windows local confirmado pela terceira vez consecutiva (07-11, 07-13, 07-19) — padrão bem estabelecido, PowerShell tool é o caminho confiável neste habitat; não precisa mais ser tratado como observação nova a cada ciclo.

## Observações
- Dream executado de forma autônoma (scheduled task, sem usuário presente).
- Safra de 2 memórias em 6 dias, uma delas (07-14) sem nenhuma pegada técnica/skill acionada — ritmo normal, ciclo mais fino que os anteriores.
- Padrão novo identificado: quando a sessão original já consolida o aprendizado ao vivo (commit direto em `SKILL.md`/script na mesma sessão), o papel do Dream muda de "criar consolidação" para "auditar a consolidação e fechar lacunas residuais". Confirmar via `git log`/`git show` o que já foi tocado evita retrabalho e duplicação divergente. Vale manter esse hábito de checagem antes de escrever qualquer edição de skill quando a memória descrever fixes que soam "já resolvidos no código".
- Disciplina aplicada: não promover a proposta de backlog de "Descoberta Assistida por IA" à revelia — mandato do Dream é sobre arquitetura de skills, não sobre decidir roadmap de produto no lugar do Raffa.
