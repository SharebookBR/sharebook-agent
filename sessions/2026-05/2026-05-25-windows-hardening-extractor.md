# Memória Episódica — 2026-05-25 (Windows Local)

## 1. Modelo e ambiente
- Claude Sonnet 4.6 (Claude Code) via Windows Local.
- Runtime: Windows local (`skills/runtime/windows-local.md` seguido).
- Repositório tocado: `sharebook-ebook-importer`.

## 2. Skills acionadas
- `skills/runtime/windows-local.md` — ritual de abertura, glob com path absoluto.
- `skills/importers/sharebook-public-ebook-importer/SKILL.md` — referência ao pipeline.

## 3. O que foi feito

### Análise dos 13 itens source_blocked da ebook_foundation_subjects
- Classificados em: falsos positivos, bloqueios reais, links mortos, hash URLs sem PDF, 403 de bot.
- Raffa confirmou 6 itens como recuperáveis, 4 como corretos, 2 como WAF.
- #1135 (GitHub blob) e #1128 (AWS) resolvidos na primeira rodada de fixes.

### Commit `f3afe45` — primeira rodada
- `BROWSER_HEADERS` completo substituindo `User-Agent` simples.
- `raise_for_restricted_html` refinado: removidos sinais genéricos (`sign in`, `login`, `password`, `get access`); mantidos apenas sinais de bloqueio de conteúdo.
- Wayback: removida chamada precoce de `raise_for_restricted_html` antes de `discover_assets_from_wayback_html`.
- `github_blob_to_raw`: converte blob URL → raw.githubusercontent.com.

### Commit `a2b2f06` — segunda rodada (após feedback real do OpenClaw)
- `make_pdf_request`: headers específicos para PDFs diretos (`Accept: application/pdf` + `Referer` do domínio) — desbloqueou defense.gov (#1129).
- `inject_wayback_raw_modifier`: insere `if_` em URLs do Wayback que apontam para `.pdf`, forçando entrega de conteúdo bruto sem toolbar HTML — resolveu #1137 e #1138.
- Família `bepress` (`viewcontent.cgi`): handler dedicado com `resolve_bepress_assets`.
- `discover_assets_from_html`: adicionados `citation_pdf_url` meta tag e `<embed type="application/pdf">` como padrões de alta prioridade.
- `WAF_SIGNALS` + detecção em `raise_for_restricted_html`: erro semântico "AWS WAF challenge — requer browser com JavaScript" em vez de "sem magic bytes".
- Removido `'access denied'` de `RESTRICTED_SIGNALS` (era string JS do plugin WordPress Download Monitor).

### Resultado final dos 13 itens
| Status | Itens |
|---|---|
| ✅ Resolvidos (waiting_editor) | #1128, #1135, #1129, #1137, #1138 |
| ❌ AWS WAF (source_blocked legítimo) | #1126 (Milne→KnightScholar), #1143 (cupola.gettysburg.edu) |
| ❌ Bloqueio real | #1127 (CockroachLabs) |
| ❌ Links mortos | #1130, #1134, #1140 |
| ❌ Vendendo livro | #1132, #1133 (cpbook.net) |

### Workflow desta sessão
- Teste rodou localmente (Windows) para obter feedback antes de commitar.
- Dependências instaladas no Python 3.12 local: `pillow`, `pypdf`, `pymupdf`.
- Ao final, 5 itens resetados para `waiting_triage` para o OpenClaw processar de verdade.

## 4. Decisões tomadas
- Testes locais são válidos para feedback rápido, mas o processo real roda no OpenClaw (triage → editorial → publish completos).
- AWS WAF requer browser headless (Playwright) — fora do escopo do importer atual. Raffa vai pedir triagem manual quando `last_error` mencionar "WAF".
- `'access denied'` removido dos sinais: servidores HTTP 403 já são tratados pela exceção de HTTP; o sinal em HTML era sempre string JS, nunca bloqueio real.
- `if_` no Wayback é a forma canônica de forçar conteúdo bruto — documentado em `windows-local.md` implicitamente via fix.

## 5. Contexto relevante
- Source `ebook_foundation_subjects` (ID 6): 765 itens, pipeline ativo.
- O `raise_for_restricted_html` foi a maior fonte de falsos positivos: sinais genéricos queimavam páginas de OA legítimas.
- Duas fontes de falso positivo clássicas: (1) navbar com "sign in", (2) strings JS de plugins WordPress.
- WAF pattern específico: HTML de 3042 bytes com `window.gokuProps` e `awsWafCookieDomainList`.

## 6. Fricções e soluções
- **Glob com path relativo no Windows**: armadilha conhecida, resolvida com path absoluto no pattern.
- **`psycopg2` ausente no Python 3.12 do sistema**: estava instalado — era o Python errado sendo chamado. Solução: usar `C:\Users\raffa\AppData\Local\Programs\Python\Python312\python.exe` explicitamente.
- **`PIL` e `pypdf` ausentes**: instalados via pip no Python 3.12.
- **Heredoc no PowerShell**: não funciona. Solução: escrever mensagem em arquivo e usar `git commit -F`.
- **Milne 3-hop**: o PDF final fica em `knightscholar.geneseo.edu` que é AWS WAF — não resolvível sem JS.

## 7. Como me senti
Foi uma sessão de diagnóstico cirúrgico. A dinâmica de trabalhar local para obter feedback antes de commitar foi a certa — evitou commitar código que pareceria funcionar mas quebraria no OpenClaw. Cada rodada de teste revelou uma camada nova do problema, e cada fix foi provado antes de avançar.

O `raise_for_restricted_html` foi o grande vilão. Um sinal genérico demais ("sign in", "access denied") queimava páginas livres. A lição é: sinal de conteúdo bloqueado precisa ser específico sobre *acesso ao conteúdo*, não sobre *existência de autenticação no site*.

A descoberta do AWS WAF foi frustrante mas honesta. Dois itens claramente acessíveis ao ser humano são inacessíveis ao bot por design. A solução correta foi reconhecer isso e dar uma mensagem semântica — não fingir que é problema nosso nem deixar o erro genérico. "WAF challenge" no `last_error` é suficiente para o Raffa saber o que fazer (triagem manual no OpenClaw).

No geral, saímos com 5 itens resolvidos de 7 recuperáveis (os 6 confirmados pelo Raffa mais o #1135). Os 2 WAF são ceiling real, não teto de ambição.
