# Tarefa 5 — Sugestão assistida no importer

## Status

**Fechada para avanço** — resolvida por regra mecânica determinística (não IA), durante a implementação incremental.

## Decisão de produto

A ideia original era IA sugerir tags no importer, com revisão humana. Ao alinhar o desenho, o Raffa pediu para **deixar o processo mecânico, sem depender de IA e sem POST/PUT extra**.

A regra determinística que já tínhamos validado no backfill (título + sinopse → vocabulário fechado) foi portada para dentro do backend e enganchada no ponto único de criação de livro. Nada de IA, nada de chamada externa, nada de rascunho para revisar — tags entram `Approved` e visíveis na criação.

## Resultado

- `BookTagRuleEngine` (C#) — motor regex determinístico (~110 regras), mesma normalização do backfill (C++→cplusplus, C#→csharp, .NET→dotnet, acentos removidos).
- `TagService.ApplyMechanicalTagsAsync` — resolve candidatos contra tags ativas/públicas, até 3, grava `BookTag` com `Source = Mechanical` e `ReviewStatus = Approved`.
- Hook no `BookService.InsertAsync` — best-effort (try/catch), nunca bloqueia o cadastro.
- Vale para **todo livro** (físico e digital), sem filtro de tipo: tag correta num livro físico é ganho, não ruído. Regra exige título casar, então não acende para romance/filosofia.
- `BookTagSource.Mechanical` ("Mecânica") — separa o que o robô pôs do que um humano pôs.
- Commit `65e2dc3 feat(tags): atribui tags mecanicas na criacao do livro` (sharebook-backend, master).

## Critérios de pronto originais → como foram atendidos

- "IA só sugere tags existentes" → o motor resolve contra o vocabulário fechado no banco (tags ativas + públicas), nunca cria tag.
- "sugestões ficam revisáveis" → **reconsiderado**: tags mecânicas entram `Approved` direto; correções manuais continuam possíveis via curadoria (`SetBookTagsAsync`).
- "rejeições são possíveis e registráveis" → coberto pela curadoria manual existente (a tag mecânica é um `BookTag` normal, removível/ajustável).
- "prompts seguem o playbook local de tagging editorial" → **não se aplica** (sem prompt, sem IA).
- "falha de sugestão não bloqueia importação" → atendido por try/catch no hook.

## Nota

Se aparecer ruído em produção, o portão B (motor gera `Pending`/rascunho e humano aprova) pode ser ligado depois — é uma mudança pequena no `ApplyMechanicalTagsAsync`. Por ora, A foi a escolha aprovada.
