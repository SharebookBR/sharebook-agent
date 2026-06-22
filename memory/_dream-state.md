# Dream State

Checkpoint oficial da consolidação de memória do projeto.

## Último dream
- Data: `2026-06-21`
- Tipo: `dream semanal automatizado`
- Última memória absorvida: `C:\Repos\SHAREBOOK\sharebook-agent\memory\2026-06-17-preparo-editorial-e-publicacao-windows.md`
- Total de memórias lidas: `13 memórias episódicas absorvidas (2026-06-02 a 2026-06-17)`

## Consolidação produzida

- **Windows Manual**: `windows-manual.md` expandida com Python 3.12 vs 3.14, compressão de capa (SSLEOFError), materialização de assets em `C:\data\workspace\...`, `publish-once --source + --limit`, boto3, sequência de diagnóstico de SSLEOFError, 4 novas armadilhas na tabela.
- **Triagem por Subagentes**: `SKILL.md` do ebook-importer com guardrail de critério duplo (PDF acessível + licença aberta) para instruções de subagentes — raiz do gap em 06-08.
- **SSR Frontend**: `frontend.md` com seção "SSR — Bugs Arquiteturais Pagos": SsrCacheService (variável de módulo), RESPONSE token no server.ts, TransferState manual no cache hit, NotFoundPageComponent como 404 real.
- **Python no Windows**: `windows-local.md` expandida com armadilha Python 3.14 sobrescrevendo PATH, Python 3.12 como ambiente canônico, `publish-once --id` nas armadilhas recorrentes.

## Próximo dream
- Começar lendo memórias criadas depois de `2026-06-17`.
- Verificar se scripts temporários `tmp_count_books.py`, `tmp_slug_fisico.py` (criados em 06-03) ainda existem — candidatos a limpeza.
- Verificar se `client_max_body_size` no nginx foi aumentado (elimina workaround de capa comprimida + fake PDF no Windows).
- Verificar evolução do canal Claude↔OpenClaw no backlog — se virou trabalho real, criar skill.
- Verificar se o cron do Dream estava funcionando — a última execução foi 06-01 e a janela 06-10 a 06-16 ficou sem memórias (sessões não registradas ou pausa real?).
- Checar se `publish-once --id` foi adicionado ao CLI ou continua sem suporte.

## Observações
- Dream executado de forma autônoma (scheduled task, sem usuário presente).
- Nenhuma skill nova criada — todos os aprendizados absorvidos em skills existentes por coesão de domínio.
- Safra maior que o ideal (3 semanas em vez de 1) — verificar regularidade do cron.
- Canal A2A Claude↔OpenClaw está no backlog como roadmap, não como procedimento operacional. Não merece skill ainda.
