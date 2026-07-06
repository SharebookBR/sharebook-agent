# Dream State

Checkpoint oficial da consolidação de memória do projeto.

## Último dream
- Data: `2026-07-05`
- Tipo: `dream semanal automatizado`
- Última memória absorvida: `C:\Repos\SHAREBOOK\sharebook-agent\memory\2026-06-30-preparo-publicacao-editorial.md`
- Total de memórias lidas: `3 memórias episódicas absorvidas (2026-06-29-download-egress-cloudflare-throttle, 2026-06-29-dream, 2026-06-30-preparo-publicacao-editorial)`

## Consolidação produzida

- **`skills/importers/ebook-importer/SKILL.md`** — guardrail "sync de schema → varrer scripts/" ampliado para cobrir também `scripts/production/*.py` (Windows local), não só `skills/importers/ebook-importer/scripts/`. Motivado por incidente real: `inspect_item.py` quebrou com coluna removida `qi.attempts`.
- **`skills/importers/ebook-importer/SKILL.md`** — regra editorial de capa expandida: documentado o caminho "gerar capa local com `cover_generate.py`" como alternativa legítima e gratuita quando a primeira página do PDF não serve como capa (frontispício acadêmico).
- **`scripts/production/INDEX.md`** — descrições de `inspect_item.py` e `plan_set.py` atualizadas para refletir os fixes de 2026-06-30 (schema correto + `.env`; wrapper fino da CLI canônica).
- **`scripts/covers/INDEX.md`** — descrição de `cover_generate.py` atualizada: cross-platform (Windows + Linux) desde 2026-06-30.
- Nenhuma skill nova criada. Nenhum merge/split/arquivamento nesta rodada.

## Próximo dream
- Começar lendo memórias criadas depois de `2026-06-30`.
- `client_max_body_size` do nginx ainda não foi aumentado — continua pendência (arrastada desde 06-21). Verificar se alguma sessão futura resolve isso e, se sim, revisar `windows-manual.md` para aposentar o workaround de fake PDF quando deixar de ser necessário.
- Verificar evolução do canal Claude↔OpenClaw (`backlog/todo/canal-claude-openclaw.md`) — se virar execução real (não só pesquisa de A2A), criar skill.
- Verificar evolução do item Cloudflare (`backlog/todo/cloudflare-cdn-ddos-protection.md`) — se DNS/rate-limit forem configurados, documentar em `skills/infra/`.
- Item backlog `limpeza-duplicatas-catalogo.md` segue com evidência forte (235 excedentes, 9% do catálogo) — acompanhar se vira sprint de qualidade de catálogo.
- Pendência resolvida e removida desta lista: scripts temporários `tmp_count_books.py`/`tmp_slug_fisico.py` não existem mais no repositório (confirmado 2026-07-05).

## Observações
- Dream executado de forma autônoma (scheduled task, sem usuário presente).
- Safra de 3 memórias em 9 dias — ritmo levemente acima do semanal padrão, dentro do esperado.
- Nenhuma skill nova criada — os três aprendizados de 06-30 (schema drift fora da pasta oficial, fonte cross-platform, script duplicado) já tinham destino em guardrails/skills existentes; a plasticidade foi ampliar escopo, não criar estrutura nova.
- Padrão identificado: guardrails escritos para uma árvore de scripts (`skills/importers/ebook-importer/scripts/`) podem ficar cegos para uma segunda árvore que cresce depois (`scripts/production/`). Vale revisitar outros guardrails de "varrer X" do corpus com a mesma lente no próximo ciclo, caso apareça sinal equivalente.
