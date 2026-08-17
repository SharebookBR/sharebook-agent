# Dream State

Checkpoint oficial da consolidação de memória do projeto.

## Último dream
- Data: `2026-08-17`
- Tipo: `dream semanal automatizado`
- Última memória absorvida: `C:\Repos\SHAREBOOK\sharebook-agent\memory\2026-08-16-migracao-vps-e-openclaw-dormente.md`
- Total de memórias lidas: `3 memórias episódicas absorvidas (2026-08-03-quatro-preparos-editoriais-publicacao, 2026-08-13-quatro-preparos-editoriais-publicacao, 2026-08-16-migracao-vps-e-openclaw-dormente)`.

## Consolidação produzida

### Guardrail promovido
- `skills/importers/ebook-importer/SKILL.md`, seção "Regras editoriais" — adicionado passo 4 ao preflight editorial: buscar a obra no catálogo (busca semântica, não só título) antes de `plan-set`. Recorrência real: item `1358` (07-09) e `Think Bayes`/`1594` (08-13), ambos duplicatas pegas antes da mutação pela mesma prática ainda não escrita como regra.

### Reparo de roteamento
- `AGENTS.md`, "Cenários de Roteamento" — adicionada linha distinguindo "produção de PDFs/capas autorais" (`skills/importers/INDEX.md`, obra nova) de "gerar/trocar capa de livro existente" (`skills/product-ux/INDEX.md`, `cover-direction`). Gap identificado na autocrítica estrutural da própria sessão de 08-16, confirmado por leitura direta dos dois `INDEX.md` antes de editar.

### Reparo de link morto
- `backlog/todo/openai-codex-oauth-drain.md` — removida referência a `memory/2026-06-12-openai-drain-investigation.md`, confirmado via `git log --all` que esse arquivo nunca existiu no repo (não foi perdido, nunca foi escrito). Contexto da investigação preservado no próprio documento; texto agora deixa explícito para não recriar o arquivo por suposição.

### Decisão consciente de não agir
- **Feedback "silêncio operacional" (08-13)**: Raffa cobrou atualização por marco numa publicação longa. Primeira ocorrência clara desse feedback específico — sem recorrência anterior encontrada no corpus. Por doutrina (não promover por sessão isolada), não virou guardrail. Registrado em `2026-08-17-dream.md` para o próximo Dream cruzar; se repetir, promove para "Postura do Agente" em `AGENTS.md`.
- **Trap de quoting aninhado no `vps_ssh.py` (08-16)**: já documentado extensivamente em `skills/infra/coolify-vps.md` (regra de uma linha por comando, UTF-8 sem BOM, preferência por `--script-file`). Recorrência de erro já coberto, não lacuna de documentação. Sem ação.
- **BOOTSTRAP.md, seções "Memória semântica"/"Active Memory" marcadas dormentes por inferência**: pendente de confirmação explícita do Raffa, não é decisão do Dream autônomo.
- **Cron do importer (onde/se renasce), `client_max_body_size` do nginx, convenção de commit vs. proteção de branch do GitHub**: decisões de produto/infra fora do mandato de arquitetura de skills do Dream.

## Próximo dream
- Cruzar se o feedback de "silêncio operacional durante tarefa longa" (08-13) se repete. Se sim, promover a "Postura do Agente" em `AGENTS.md` — atualização por marco em tarefas longas, sem virar narração excessiva.
- A safra de 08-16 listou lacunas adicionais fora do escopo do brief daquela sessão que não são de arquitetura de skill (link `openai-codex-oauth-drain.md` já corrigido aqui; roteamento de capas já corrigido aqui). As restantes (BOOTSTRAP.md dormência por inferência, cron do importer, nginx, convenção de commit) seguem como pendência de produto/confirmação humana, não de Dream.
- Observar se o guardrail de duplicidade recém-formalizado em `ebook-importer/SKILL.md` reduz de fato a taxa de duplicata pega tarde, ou se ainda escapa alguma — sinal de que o preflight precisa de mais força (ex: script de checagem automática em vez de instrução em prosa).
- `limpeza-duplicatas-catalogo.md` (235 excedentes) segue sem novo caso de produção.
- Canal Claude↔OpenClaw (A2A) — sem objeto enquanto o OpenClaw estiver dormente; não é mais pendência ativa até reprovisionamento.

## Observações
- Dream executado de forma autônoma (scheduled task, sem usuário presente).
- Safra de 3 memórias, mas com uma sessão estrutural grande (08-16) que já fez a maior parte da plasticidade ao vivo, incluindo autocrítica explícita das próprias lacunas. O papel deste ciclo foi auditar essa lista e fechar os itens que eram de fato arquitetura de skill (2 de 6 itens listados), não recriar o trabalho nem tratar as pendências de produto/processo como se fossem do mandato do Dream.
- Padrão reconfirmado: quando uma sessão registra sua própria autocrítica estrutural com itens nomeados, o Dream deve tratar essa lista como backlog de auditoria prioritário — critério mais barato e mais confiável do que garimpar padrões em prosa solta.
- Disciplina aplicada deste ciclo: feedback de comunicação vívido e citável (08-13) foi conscientemente **não** promovido a guardrail por ser ocorrência única — evitando o anti-padrão "criar skill para migalha isolada" mesmo quando a migalha é memorável.
