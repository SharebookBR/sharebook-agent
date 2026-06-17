# 2026-06-17 — Preparo editorial e publicação no Windows local

## 1. Modelo e ambiente

- Modelo: Codex GPT-5 no Codex desktop.
- Runtime detectado: Windows local em `C:\Repos\SHAREBOOK`.
- Shell: PowerShell.
- Python efetivo para operação: `C:\Users\raffa\AppData\Local\Programs\Python\Python312\python.exe`.
- Observação: `python` no PATH apontava para Python 3.14 sem `psycopg2`, `dotenv` ou `boto3`; o Python 3.12 era o ambiente operacional correto.

## 2. Skills acionadas

- `AGENTS.md` do Sharebook.
- `sharebook-agent/skills/runtime/windows-local.md`.
- `sharebook-agent/skills/importers/INDEX.md`.
- `sharebook-agent/skills/importers/ebook-importer/SKILL.md`.

## 3. O que foi feito

- Rodada de roleta de capa para:
  - `Partial Evaluation and Automatic Program Generation`.
  - `Think OS: A Brief Introduction to Operating Systems`.
- Alinhado que preparo editorial deve começar com:
  - `cd /data/workspace/sharebook-ebook-importer && sh -c 'python3 cli.py editor-next'`
  - No Windows local, equivalente: executar `cli.py editor-next` no repo local com Python 3.12.
- Preparado editorialmente o item `1279`:
  - Título: `Don't Just Roll the Dice`.
  - Autor: Neil Davidson.
  - Categoria: `Tecnologia > Geral` (`019dcbfc-0a09-702e-a0ab-090acb5597b6`).
  - Status: `waiting_editorial` -> `waiting_publish`.
- Publicado o item `1279` via workaround:
  - Primeiro o worker normal falhou com `SSLEOFError` no POST da API.
  - Workaround final: `fake.pdf` + capa compactada + upload do PDF real direto no S3.
  - Livro criado/aprovado: `019ed640-263e-7a25-b727-424265b5fbe7`.
  - Slug: `dont-just-roll-the-dice`.
  - S3 key: `ebooks/dont-just-roll-the-dice.pdf`.
  - Importer status final: `done`.
- Preparado editorialmente o item `1280`:
  - Título: `How to Stand Out as a Software Engineer`.
  - Autor: Landry Monga.
  - Categoria: `Tecnologia > Geral` (`019dcbfc-0a09-702e-a0ab-090acb5597b6`).
  - Status: `waiting_editorial` -> `waiting_publish`.
- Publicado o item `1280` pelo worker normal:
  - Livro criado/aprovado: `019ed64c-f47b-70d0-9f03-b11965c946fd`.
  - Slug: `how-to-stand-out-as-a-software-engineer`.
  - S3 key: `ebooks/how-to-stand-out-as-a-software-engineer.pdf`.
  - Importer status final: `done`.

## 4. Decisões tomadas

- Para `ebook_foundation_subjects`, respeitar `editorial_prompt` como fonte da verdade:
  - sinopse em inglês;
  - 3 parágrafos;
  - ler o table of contents antes de escrever;
  - categoria sempre folha;
  - `Professional Development` -> `Tecnologia > Geral`.
- Para publicação local Windows, quando o worker normal falhar por transporte HTTPS durante upload:
  - checar duplicata no catálogo antes de retry;
  - reduzir capa quando o payload JSON estiver causando fechamento de conexão;
  - renovar token se o erro real virar `401`;
  - usar `fake.pdf` + S3 real como workaround operacional.
- Não insistir em retries cegos quando o erro se repete sem mudança de hipótese.

## 5. Contexto relevante

- `editor-next` pode retornar paths canônicos de OpenClaw (`/data/workspace/...`) mesmo quando executado no Windows local.
- No Windows, para o worker normal conseguir publicar, foi necessário espelhar assets em:
  - `C:\data\workspace\sharebook-ebook-importer\var\tmp\triage-<ID>\source.pdf`
  - `C:\data\workspace\sharebook-ebook-importer\var\tmp\triage-<ID>\preview-pages\page-01.png`
- Para o item `1279`, o POST com PDF real falhou; o POST com fake PDF também falhou enquanto a capa era PNG de 877 KB.
- Compactar a capa para JPEG de ~86 KB fez a API responder de verdade. O próximo bloqueio foi token expirado (`401`), resolvido com `sharebook_refresh_token.py`.
- `boto3` não estava instalado no Python 3.12; foi instalado com `pip install --user boto3` para permitir upload S3 no workaround.

## 6. Fricções e soluções

- Fricção: comecei um preparo editorial em livro já publicado por assumir o último contexto da conversa.
  - Solução: Raffa esclareceu que o primeiro passo correto é `editor-next`; fluxo corrigido imediatamente.
- Fricção: Python default era 3.14 sem dependências operacionais.
  - Solução: usar explicitamente Python 3.12.
- Fricção: `publish-once` não aceita `--id`, só `--source` e `--limit`.
  - Solução: operar por source com `--limit 1`, após garantir que o item desejado era o próximo elegível.
- Fricção: paths `/data/workspace` retornados pelo banco não existem naturalmente no Windows.
  - Solução: materializar/espelhar assets em `C:\data\workspace\...`.
- Fricção: `SSLEOFError` mascarava causas diferentes.
  - Solução: reduzir payload, renovar token, validar catálogo e importer após cada tentativa.

## 7. Como me senti

Comecei a sessão meio confiante demais no contexto imediato, e isso apareceu quando tratei o último livro da conversa como alvo do preparo editorial. Não foi catastrófico, mas foi um bom lembrete: quando existe comando canônico, especialmente no importer, contexto conversacional não vence protocolo operacional. A correção do Raffa foi precisa e ajudou a deixar o fluxo mais nítido.

A parte da publicação foi tecnicamente interessante porque o erro tinha cara de "PDF grande", mas o dado bruto desmontou essa hipótese. O payload estimado estava abaixo do limite, o fake PDF também falhou, e só depois de compactar a capa apareceu o `401` real. Foi uma daquelas situações em que o sistema parecia estar sendo caprichosamente opaco, mas a sequência de hipóteses pequenas foi abrindo a caixa.

Fiquei satisfeito com a segunda publicação porque ela mostrou o caminho mais limpo: preparo por `editor-next`, materialização dos assets, worker normal, validação no banco. Também ficou claro que o Windows local precisa de menos improviso e mais rotinas explícitas para espelhar `/data/workspace`. Essa é uma fricção pagável, mas se repetir muito deveria virar script ou hardening do worker.
