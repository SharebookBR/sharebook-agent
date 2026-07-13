# Dream State

Checkpoint oficial da consolidação de memória do projeto.

## Último dream
- Data: `2026-07-13`
- Tipo: `dream semanal automatizado`
- Última memória absorvida: `C:\Repos\SHAREBOOK\sharebook-agent\memory\2026-07-11-preparo-editorial-foundations-cs.md`
- Total de memórias lidas: `2 memórias episódicas absorvidas (2026-07-09-resgate-editorial-e-duplicata, 2026-07-11-preparo-editorial-foundations-cs)` + releitura de `2026-07-05-dream.md` para contexto

## Consolidação produzida

- **`skills/importers/ebook-importer/windows-manual.md`** — nova seção "Quando NÃO usar — publish remoto via SSH/docker exec": quando a triagem já rodou no OpenClaw, publicar direto no container via `vps_ssh.py`/`docker exec` em vez de default para o workaround de fake PDF + S3. Validado em produção (item 1367, 2026-07-11).
- **`skills/importers/ebook-importer/windows-manual.md`** — nova linha na tabela de armadilhas: `last_error` sobrevive à publicação manual de item resgatado; precisa limpeza explícita.
- **`skills/importers/ebook-importer/SKILL.md`** — handler de Google Drive adicionado a "Handlers por família" (`confirm=t` para evitar HTML interstitial em vez do PDF real).
- **`skills/runtime/windows-local.md`** — duas fricções novas: heredoc PowerShell corrompendo raw string Python (usar arquivo em vez de inline) e timeout de screenshot no Browser pane (usar `get_page_text` como fallback).
- **`backlog/todo/limpeza-duplicatas-catalogo.md`** — evidência de produção adicionada (item 1358): dedupe por título exato do importer não pega variantes editoriais óbvias.
- **Poda de conhecimento degradado** (fora do escopo direto das memórias absorvidas, achado ao verificar indexação real):
  - `skills/infra/coolify-vps.md` — 4 referências mortas a `codex-scripts/`/`codex-sessions/` corrigidas para `scripts/infra/`/`memory/`.
  - `skills/importers/physical-book-importer/references/workflow.md` — referência morta a `codex-scripts/sharebook_prod_login.ps1` corrigida para `scripts/web/`.
  - `scripts/sharebook_prod_book.py` (raiz, órfão, duplicata não indexada do canônico em `scripts/production/`) — removido via `git rm`.
  - `codex-temp/*.py`/`*.sql` (gitignorado, nunca commitado, continha senha de banco em texto plano) — removido.
- Nenhuma skill nova criada. Nenhum merge/split/arquivamento nesta rodada.

## Próximo dream
- Começar lendo memórias criadas depois de `2026-07-11`.
- `client_max_body_size` do nginx ainda não foi aumentado — continua pendência (arrastada desde 06-21). A nova seção "publish remoto via SSH/docker exec" reduz a frequência de uso do workaround por hábito, mas não resolve a causa raiz. Revisar `windows-manual.md` para aposentar o workaround quando o nginx for corrigido.
- Verificar evolução do canal Claude↔OpenClaw (`backlog/todo/canal-claude-openclaw.md`) — se virar execução real, criar skill.
- Verificar evolução do item Cloudflare (`backlog/todo/cloudflare-cdn-ddos-protection.md`) — se DNS/rate-limit forem configurados, documentar em `skills/infra/`.
- Item backlog `limpeza-duplicatas-catalogo.md` segue com evidência forte (235 excedentes + caso real de dedupe falho na entrada, item 1358) — acompanhar se vira sprint de qualidade de catálogo.
- Item 1364 (Syncfusion, `context_text` de boilerplate, source `ebook_foundation_subjects`) segue em `waiting_editorial` — observação isolada, não recorrência ainda; se repetir em outros itens da mesma source, investigar bug de extração/URL.
- Achado um script órfão (`scripts/sharebook_prod_book.py`) fora de qualquer família indexada, resíduo de reorganização passada. Não houve varredura exaustiva de toda a árvore `scripts/` neste ciclo — se aparecer padrão semelhante de novo, vale um passe dedicado dessa vez cobrindo a árvore inteira.

## Observações
- Dream executado de forma autônoma (scheduled task, sem usuário presente).
- Safra de 2 memórias em 6 dias — ritmo dentro do esperado.
- Nenhuma skill nova criada — os aprendizados de 07-09/07-11 já tinham destino em `windows-manual.md`, `SKILL.md` do importer e `windows-local.md`.
- Padrão identificado: a regra "o que não está indexado é lixo" (`DREAM.md`) funciona não só para prevenir criação de lixo novo, mas como detector de apodrecimento silencioso em documentação antiga — referências a paths de uma convenção de nomes anterior (`codex-scripts`, `codex-sessions`) sobreviveram sem gerar erro óbvio até serem checadas. Vale manter a checagem cruzada de paths citados em skill como parte de rotina do Dream, não só reagir ao que as memórias do período trazem.
- Achado incidental de segurança: credencial de banco em texto plano dentro de scratch gitignorado (`codex-temp/`), nunca commitado. Sem exposição real (`.gitignore` funcionou), mas reforça que "instrução de limpar ao final" sem enforcement é frágil — vale observar se o padrão se repete em outras sessões que usam `codex-temp/` como scratch.
