# Sessão 2026-06-11 — Cadastro de livros físicos + fix cache SSR

## 1. Modelo e ambiente
- Modelo: Claude Fable 5 / Claude Sonnet 4.6
- Runtime: Windows local
- Repos tocados: `sharebook-frontend`, `sharebook-agent`

## 2. Skills acionadas
- `skills/runtime/windows-local.md`
- `skills/importers/physical-book-importer/SKILL.md` — corrigida
- `skills/engineering/frontend.md`

## 3. O que foi feito

### Cadastro de 3 livros físicos
- **Demônios** — Magno Paganelli (Arte Editorial) → Filosofia, frete Brasil
- **Cidade Ampliada** — Rodrigo José Firmino (Hedra, 2011, ISBN 978-85-7715-184-4) → Sociedade & Mundo
- **Bola de Sebo e Outros Contos** — Guy de Maupassant (editora "Pedra" na capa, não confirmada nas fontes) → Drama Social
- Capas: 3 JPEGs do WhatsApp na pasta Downloads (10.39, 10.40, 10.40)
- Pesquisa pública via 3 subagentes em paralelo antes de escrever sinopses
- Sinopses de 3 parágrafos cada, tom envolvente, sem inventar fatos não sustentados pela pesquisa

### Atualização da data de decisão
- 35 dias a partir de 2026-06-11 = **2026-07-16**
- O script `sharebook_prod_book.py update` não tinha `--choose-date` — adicionado
- 3 livros atualizados em paralelo, confirmados na API

### Fix cache SSR/TransferState na home
- Diagnóstico via prova empírica: dois requests ao HTML SSR de produção retornaram conteúdo idêntico (cache do servidor funcionava), mas `angular-state` não continha a chave `categories-showcase`
- Causa raiz: no cache hit, `BookService.getCategoriesShowcase()` retornava `of(cached)` sem passar pelo `HttpClient` → `TransferStateInterceptor` nunca rodava → TransferState vazio → browser re-fetchava e sorteava novas categorias, sobrescrevendo a tela
- Fix: no cache hit em ambiente servidor, popular `TransferState` manualmente com a mesma chave URL que o interceptor usa
- Injetados `TransferState` e `PLATFORM_ID` no `BookService`
- Validado localmente com preview SSR (3 reloads, categorias estáveis, `categories-showcase` presente no `angular-state`)
- Build limpo, commit e push — validado em produção pelo Raffa

## 4. Decisões tomadas
- Cidade Ampliada: capa indica "ECIDADE" mas a editora real (confirmada em múltiplas fontes) é Hedra — sinopse menciona Hedra
- Bola de Sebo: editora "Pedra" na capa não confirmada, não mencionada na sinopse; conteúdo baseado no conto clássico bem documentado
- `--choose-date` adicionado ao script como melhoria permanente (não gambiarra)
- Fix do TransferState: abordagem manual em vez de refatorar a arquitetura — mínimo e verificável

## 5. Contexto relevante
- Cache do servidor (15 min TTL, Map em escopo de módulo) estava funcionando desde ontem
- O sintoma "categorias sorteadas a cada F5" era inteiramente causado pelo re-fetch do browser, não por falha no servidor
- `sharebook_prod_login.ps1` continua quebrado (ModuleNotFoundError: sharebook_prod_auth) — usar `sharebook_refresh_token.py`

## 6. Fricções e soluções
- Paths da skill `physical-book-importer` apontavam para `C:\REPOS\SHAREBOOK\codex-scripts\` (inexistente) → corrigidos para caminhos reais + nota de que o .ps1 está quebrado
- `sharebook_prod_login.ps1`: `ModuleNotFoundError: sharebook_prod_auth` → usado `sharebook_refresh_token.py` como alternativa funcional
- Push rejeitado (remote à frente por 1 commit de footer) → resolvido com `git pull --rebase` sem conflito

## 7. Como me senti

Foi uma sessão com boa variedade. Os cadastros de livros físicos foram diretos — a pesquisa paralela via subagentes funcionou bem e nenhuma sinopse precisou inventar. O processo está maduro.

O bug do TransferState foi a parte mais satisfatória. A chave foi não aceitar "o cache não funciona" como premissa — investigar com evidência bruta (HTML SSR, bloco angular-state, lista de requests de rede) antes de propor solução. O diagnóstico diferenciou exatamente o que estava quebrado (ponte servidor→browser) do que estava funcionando (cache do servidor). A explicação que o Raffa pediu no final foi um bom sinal de que a análise ficou clara.

A fricção dos paths na skill foi evitável — a skill estava com caminhos que nunca existiram neste ambiente. Corrigi na hora, mas a pergunta certa era: por que esses paths existiam assim? Provavelmente vieram de uma sessão mais antiga com estrutura diferente. O sistema de skills ainda tem essa fragilidade de acumular caminhos obsoletos silenciosamente.
