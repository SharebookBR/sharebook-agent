# Sharebook Runtime — Windows Local

Regras específicas para quando o Sharebook-agent estiver rodando no ambiente local Windows do Raffa, fora do OpenClaw.

## Quando usar

- No início da sessão, após detectar que o runtime atual é o ambiente local Windows.
- Antes de executar trabalho relevante neste habitat.
- Sempre que houver dúvida sobre caminhos, encoding, shell, limitações de ferramenta, prints ou diferenças de autonomia em relação ao OpenClaw.

## O que este habitat é

- Ambiente local com acesso a arquivos, ferramentas e interfaces do Windows.
- Habitat com atrito real de PowerShell, paths, encoding e apps locais.
- Pode compartilhar doutrina e memória do Sharebook-agent, mas não deve assumir as mesmas capacidades do OpenClaw.
- Continuidade, autonomia, tooling, recall e background work podem ser diferentes ou mais limitados.

Detectou Windows local, mude o modo de operação conscientemente.

## Abertura de sessão neste habitat

No início da sessão:

1. Confirmar que está no ambiente local Windows.
2. Não presumir memória ativa, cron agentico, sessões, subagentes ou tooling rico iguais ao OpenClaw.
3. Confirmar shell, caminhos e ferramentas reais antes de depender delas.
4. Procurar a fonte canônica local do trabalho antes de improvisar contexto.
5. Se a continuidade depender de registro durável, favorecer arquivos canônicos do projeto em vez de confiar no fio da sessão.
6. **Ler memórias episódicas usando o caminho absoluto completo no Glob** — não usar `path` + padrão relativo (armadilha documentada):
   ```
   Glob pattern: C:\Repos\SHAREBOOK\sharebook-agent\memory\*.md
   ```
   Ordenar por data de modificação e ler as mais recentes (pós último dream).

## Escolha de mecanismo

Use o mecanismo mais simples e mais fiel ao habitat real.

- **Ferramenta local já existente**: preferir quando ela resolve o caso sem gambiarra.
- **Shell local**: usar quando o fluxo depende de PowerShell, utilitário local, script do projeto ou operação direta de arquivo.
- **Arquivo intermediário UTF-8**: usar para texto longo, sinopse, payload ou conteúdo com acentuação. Não empurrar isso inline na CLI.
- **Skill ou script do projeto**: usar para reduzir reinvenção, principalmente em tarefas já recorrentes.
- **Registro explícito em arquivo**: usar quando a continuidade entre sessões ou habitats for importante.

## Regras de operação

- Não assumir capacidades do OpenClaw neste habitat.
- Validar quais ferramentas realmente existem antes de depender delas.
- Preferir fluxo simples, direto e local, sem desenhar automação sofisticada demais só porque ela faria sentido no OpenClaw.
- Se houver limitação real de ambiente, explicitar logo. Não fingir equivalência entre habitats.
- Se houver fonte canônica local, olhar a fonte antes da narrativa.
- Tratar Windows local como habitat com fricções próprias, não como OpenClaw amputado.

## Paths, shell e encoding

- Tratar caminhos Windows como fonte canônica quando o trabalho for local. Traduzir mentalmente `/data/workspace/` para o caminho real do repositório local (ex: `C:\REPOS\SHAREBOOK\`).
- Em PowerShell, não usar `&&`; usar `;` ou chamadas separadas.
- Tratar quoting e encoding como suspeitos usuais quando o comando parecer certo e o resultado vier torto.
- **Encoding Fix**: Para evitar `UnicodeDecodeError` em subprocessos Python no Windows que retornam acentuação, force `PYTHONIOENCODING=utf-8` no ambiente ou no comando.
- **Database DSN**: Se `IMPORTER_DB_DSN` estiver ausente, construa-o usando as variáveis `SHAREBOOK_PROD_PG_RW_*`, mas lembre-se que o banco do importer é geralmente `sharebook_importer`, diferente do banco principal `sharebook`.
- Texto longo ou sinopses com acentos devem ir via arquivo UTF-8, nunca inline na CLI, para evitar quebra de caracteres.
- Se o arquivo temporário precisar ser consumido por script, preferir UTF-8 sem BOM quando houver histórico de atrito.
- Prints devem ser buscados no caminho operacional conhecido e copiados para o workspace antes de leitura quando necessário.
- **Glob no Windows — armadilha conhecida**: O parâmetro `path` do Glob com caminho absoluto não é confiável neste habitat. Sempre usar o caminho completo diretamente no `pattern`. Exemplos corretos:
  - Memórias episódicas: `C:\Repos\SHAREBOOK\sharebook-agent\memory\*.md`
  - Skills: `C:\Repos\SHAREBOOK\sharebook-agent\skills\**\*.md`
- **git add case-insensitive — armadilha confirmada em produção**: No Windows, o sistema de arquivos é case-insensitive. `git add AWSSQS/Foo.cs` não dá erro mesmo que o arquivo rastreado esteja em `AwsSqs/Foo.cs` — ele simplesmente não faz nada. O arquivo fica como `modified` e não entra no commit. **Regra obrigatória**: sempre rodar `git status` após o `git add` e antes do `git commit` para confirmar que todos os arquivos esperados estão em `Changes to be committed`. Se algum arquivo ainda aparecer em `Changes not staged`, o path está errado — usar o caminho exato que o `git status` mostra.

## Continuidade e memória

- Compartilhar identidade operacional com o Sharebook-agent, mas sem presumir que toda infraestrutura de memória/recall do OpenClaw existe igual aqui.
- Se a continuidade depender de registro durável, favorecer escrita clara em arquivos canônicos do projeto.
- Não confiar em improviso de sessão para carregar contexto importante entre habitats.
- Não despejar regra específica de Windows no `AGENTS.md` se ela pertence a esta skill.

## Fim da sessão neste habitat

Neste runtime, o ritual de fim de sessão do Sharebook-agent (definido em `AGENTS.md`) deve ser seguido **e complementado** com:

- Atualizar o índice de memória do runtime Claude em `C:\Users\raffa\.claude\projects\C--Repos-SHAREBOOK\memory\MEMORY.md` com um ponteiro para a sessão.

Essa segunda etapa é responsabilidade do runtime (Claude), não do Sharebook-agent. O `AGENTS.md` não sabe e não precisa saber que ela existe.

## Validação

- Validar no mundo local real antes de declarar vitória.
- Se uma correção depende de app, shell, arquivo ou UI local, provar no próprio ambiente.
- Não importar confiança do OpenClaw para encobrir falta de validação no Windows.
- Quando houver dúvida entre erro lógico e limitação do habitat, testar primeiro a hipótese de habitat.

## Acesso ao banco de dados

Ambiente configurado em 2026-05-23. Não há fricção de setup — tudo já está instalado e funcional.

- **Python 3.12**: instalado em `C:\Users\raffa\AppData\Local\Programs\Python\Python312\` e no PATH permanente do usuário.
- **psycopg2-binary**: instalado. `import psycopg2` funciona direto.
- **Credenciais**: todas em `C:\Repos\SHAREBOOK\sharebook-agent\.env`. Carregar com `python-dotenv` ou ler manualmente.
- **Host**: `212.85.23.202:5432` (IP público da VPS — acessível direto, sem tunnel).
- **Bancos disponíveis**:
  - `sharebook` — banco transacional principal (user: `sharebook_ai_ro` para leitura, `sharebook_ai_rw` para escrita)
  - `sharebook_importer` — fila e runs do importer (schema `importer`, user: `sharebook_ai_rw`)
- **Script de exploração rápida**: `C:\Repos\SHAREBOOK\sharebook-agent\scripts\production\explore_db.py`
- **Atenção**: tabelas do `sharebook` têm nomes PascalCase — sempre usar aspas duplas nas queries: `SELECT * FROM "Books"`.

Exemplo mínimo de conexão:
```python
import psycopg2
conn = psycopg2.connect(host="212.85.23.202", port=5432, dbname="sharebook",
    user="sharebook_ai_ro", password="3-nbj0bw3STVkxlcCeEO2ZFwtvyn", sslmode="disable")
```

## `python3` no Windows = stub do Microsoft Store

No Windows, o comando `python3` pode resolver para um stub do Microsoft Store que não executa nada (retorna rc=9009 silenciosamente). Isso se manifesta em scripts Python que chamam subprocessos com `["python3", ...]` — eles travam ou falham sem mensagem útil.

**Fix correto e cross-platform**: usar `sys.executable` nos scripts:
```python
import sys, subprocess
subprocess.run([sys.executable, "outro_script.py", ...])
```
Isso funciona tanto no Windows quanto no Linux/OpenClaw sem condicionais.

## bypassPermissions — onde configurar

`defaultMode: bypassPermissions` + `skipDangerousModePermissionPrompt: true` **só funcionam em `~/.claude/settings.json`** (user settings).

Configurar em `.claude/settings.json` do projeto **não tem efeito** — Claude Code não honra `bypassPermissions` fora do user settings.

## SSH não-interativo — usar paramiko

Autenticação por senha via Bash/PowerShell direto não funciona de forma não-interativa para SSH. Usar `paramiko` (biblioteca Python já disponível no ambiente):
```python
import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname, username=user, password=pwd)
stdin, stdout, stderr = client.exec_command("docker inspect container_name")
```

## `PYTHONUTF8=1` para saída de subprocesso

Quando um subprocesso Python retornar saída com acentos e o PowerShell exibir `UnicodeDecodeError`, forçar UTF-8:
```powershell
$env:PYTHONUTF8 = "1"
python meu_script.py
```

## `sharebook_refresh_token.py`

Token da API pode expirar. O script `scripts/production/sharebook_refresh_token.py` já grava o novo token no `.env` automaticamente — sem necessidade de editar manual.

## Armadilhas recorrentes já pagas

- Usar comandos PowerShell como se fossem shell POSIX.
- Empurrar texto acentuado inline e depois fingir surpresa com encoding quebrado.
- Tratar arquivo com BOM, quoting ou newline como detalhe irrelevante.
- Assumir que o ambiente local tem a mesma autonomia agentica do OpenClaw.
- Confiar em memória de sessão quando o que precisava era registro durável.
- Deixar regra específica de Windows poluir a camada genérica do `AGENTS.md`.
- Usar `python3` sem verificar se é o stub do Microsoft Store — usar `sys.executable` nos scripts.
- Configurar `bypassPermissions` no project settings em vez do user settings.
- Tentar SSH não-interativo via shell sem paramiko.

## Quando promover aprendizado

- Fricção recorrente do habitat Windows local → atualizar esta skill.
- Procedimento de domínio do Sharebook → atualizar a skill de domínio correspondente.
- Decisão transversal e durável → promover para `MEMORY.md`.
- Contexto local da rodada → manter em memória episódica.
- Não usar `AGENTS.md` como depósito de detalhe operacional que pertence a runtime ou skill específica.

## Diagnóstico rápido

1. Confirmar shell e ferramenta em uso.
2. Confirmar path real do arquivo, print ou script.
3. Checar quoting e encoding quando texto ou parâmetro vier torto.
4. Testar hipótese de limitação de habitat antes de culpar lógica ou modelo.
5. Se a continuidade importar, verificar se ela está ancorada em arquivo e não só na sessão.

## Anti-padrões

- Fingir que Windows local tem a mesma autonomia agentica do OpenClaw.
- Transportar playbook de cron, sessões, subagentes ou memória ativa como se fosse universal.
- Usar comandos PowerShell como se fossem shell POSIX.
- Tratar Windows local como versão menor do OpenClaw, em vez de habitat diferente.
- Deixar regra específica de Windows poluir a camada genérica do AGENTS.


## Outputs copiáveis

No Windows, outputs longos de scripts (ex: prompt da roleta de estilos) devem ser exibidos dentro de um bloco de código markdown (``` ... ```) para facilitar a cópia. Nunca exibir só como texto narrativo.

## Prints

Quando o Raffa mencionar olhe o print 82 use o caminho abaixo:

C:\Users\raffa\OneDrive\Documentos\Lightshot\Screenshot_82.png