# Sharebook Runtime — Windows Local

Regras específicas para o Sharebook-agent rodando no ambiente local Windows do Raffa.

Este é **o** habitat operacional do agente. Desde 2026-08-16 não existe outro: o container OpenClaw foi desprovisionado e `./openclaw.md` está dormente.

## Quando usar

- No início de toda sessão, antes de executar trabalho relevante.
- Sempre que houver dúvida sobre caminhos, encoding, shell, limitações de ferramenta, prints ou autonomia real.

## O que este habitat é

- Ambiente local com acesso a arquivos, ferramentas e interfaces do Windows.
- Habitat com atrito real de PowerShell, paths, encoding e apps locais.
- Onde vivem os repositórios operacionais, em `C:\Repos\SHAREBOOK\`.
- Onde a continuidade depende de registro em arquivo canônico, não de infraestrutura de memória do ambiente.

## Abertura de sessão neste habitat

No início da sessão:

1. Confirmar shell, caminhos e ferramentas reais antes de depender delas.
2. Procurar a fonte canônica local do trabalho antes de improvisar contexto.
3. Se a continuidade depender de registro durável, favorecer arquivos canônicos do projeto em vez de confiar no fio da sessão.
4. **Ler memórias episódicas usando o caminho absoluto completo no Glob** — não usar `path` + padrão relativo (armadilha documentada):
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
- **Registro explícito em arquivo**: usar quando a continuidade entre sessões for importante.

## Regras de operação

- Validar quais ferramentas realmente existem antes de depender delas.
- Preferir fluxo simples, direto e local, sem desenhar automação sofisticada demais só porque ela seria elegante.
- Se houver limitação real de ambiente, explicitar logo.
- Se houver fonte canônica local, olhar a fonte antes da narrativa.
- Tratar as fricções deste habitat como características, não como defeito a contornar com gambiarra.

## Paths, shell e encoding

- Caminhos Windows são a fonte canônica. Os repositórios operacionais vivem em `C:\Repos\SHAREBOOK\`.
- Alguns artefatos e CLIs ainda emitem caminhos POSIX `/data/workspace/...` herdados do runtime antigo (ex: saída do `editor-next`). Esses caminhos não existem em lugar nenhum hoje — traduzir para o repositório local correspondente em `C:\Repos\SHAREBOOK\`.
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

- Não existe infraestrutura de memória ativa ou recall automático neste habitat. A continuidade é a que estiver escrita em arquivo.
- Se a continuidade depender de registro durável, favorecer escrita clara em arquivos canônicos do projeto.
- Não confiar em improviso de sessão para carregar contexto importante entre sessões.
- Não despejar regra específica de Windows no `AGENTS.md` se ela pertence a esta skill.

## Fim da sessão neste habitat

Neste runtime, o ritual de fim de sessão do Sharebook-agent (definido em `AGENTS.md`) deve ser seguido **e complementado** com:

- Atualizar o índice de memória do runtime Claude em `C:\Users\raffa\.claude\projects\C--Repos-SHAREBOOK\memory\MEMORY.md` com um ponteiro para a sessão.

Essa segunda etapa é responsabilidade do runtime (Claude), não do Sharebook-agent. O `AGENTS.md` não sabe e não precisa saber que ela existe.

## Validação

- Validar no mundo local real antes de declarar vitória.
- Se uma correção depende de app, shell, arquivo ou UI local, provar no próprio ambiente.
- Não importar confiança de execução passada em outro ambiente para encobrir falta de validação aqui.
- Quando houver dúvida entre erro lógico e limitação do habitat, testar primeiro a hipótese de habitat.

## Acesso ao banco de dados

Ambiente configurado em 2026-05-23. Não há fricção de setup — tudo já está instalado e funcional.

- **Python 3.12**: instalado em `C:\Users\raffa\AppData\Local\Programs\Python\Python312\` e no PATH permanente do usuário.
- **psycopg2-binary**: instalado. `import psycopg2` funciona direto.
- **Credenciais**: todas em `C:\Repos\SHAREBOOK\sharebook-agent\.env`. Carregar com `python-dotenv` ou ler manualmente.
- **Host**: `129.121.36.220:5432`. Mudou em **17/08/2026** com a migração Hostinger → HostGator; o antigo `212.85.23.202` está desligado.
- **A porta 5432 fica FECHADA por padrão** (desde 17/08/2026). Não presumir acesso direto: `Connection refused` no 5432 é o firewall, **não** senha errada nem banco fora do ar. Antes de diagnosticar credencial, confirmar se a porta está aberta.

### Protocolo do 5432: abrir, usar, fechar

A exposição pública é um **toggle do Coolify** no recurso do Postgres. O Raffa autorizou (17/08/2026) ligar temporariamente quando houver necessidade real.

1. **Antes de pedir, checar se dá para não pedir.** Muita coisa se resolve por SSH sem expor nada: `docker exec` no container do Postgres, inspeção de env, contagem de linhas. Só pedir a abertura quando o que precisa provar for o acesso *externo* em si, ou quando for rodar os scripts locais em bloco.
2. **Usar** — todo o trabalho de banco de uma vez. Não abrir para uma query e voltar a pedir dez minutos depois.
3. **Desligar na hora** que terminar, e avisar. Não deixar ligado "por via das dúvidas".

Deixar a porta aberta porque pode ser útil depois é o mesmo antipadrão do monitor de background órfão: conveniência do agente virando risco permanente do Raffa. O passo 3 é obrigatório e é meu, não dele.

Para testar credencial sem abrir nada, ver "Testar credencial de banco — o falso verde do `trust`" em `skills/infra/coolify-vps.md`.
- **Bancos disponíveis**:
  - `sharebook` — banco transacional principal (user: `sharebook_ai_ro` para leitura, `sharebook_ai_rw` para escrita)
  - `sharebook_importer` — fila e runs do importer (schema `importer`, user: `sharebook_ai_rw`)
- **Acesso de fora depende de um toggle do Coolify.** O Coolify tem a opção de expor (ou não) o Postgres na internet. Com ela desligada — postura mais segura, e o estado normal — a porta 5432 não é publicada no host e toda conexão direta do Windows morre com `Connection refused`, embora o container esteja sadio e o app o alcance pela rede interna do Docker.
  - **Não confundir com firewall.** Em 2026-08-17 diagnostiquei `ufw` inativo, nenhuma regra DROP, e o sintoma real apareceu em `docker ps --format '{{.Ports}}'`: `5432/tcp` sozinho, sem `0.0.0.0:5432->`. Esse é o sinal de que a porta não está publicada.
  - **O Raffa pode ligar o toggle temporariamente** quando o trabalho exigir. Pedir em vez de presumir indisponibilidade.
  - **Alternativa sem reabrir a porta**: `python scripts/infra/pg_tunnel.py` levanta um túnel SSH até o container e o CLI canônico do importer funciona por ele sem alteração no servidor (`os.environ.setdefault` faz a variável exportada vencer o `.env`). Validado em 2026-08-17 com `cli.py status` e `cli.py status-set`.
- **Script de exploração rápida**: `C:\Repos\SHAREBOOK\sharebook-agent\scripts\production\explore_db.py`
- **Atenção**: tabelas do `sharebook` têm nomes PascalCase — sempre usar aspas duplas nas queries: `SELECT * FROM "Books"`.

Exemplo mínimo de conexão (credenciais sempre do `.env`, nunca hardcode):
```python
import os, psycopg2
from dotenv import load_dotenv
load_dotenv(r"C:\Repos\SHAREBOOK\sharebook-agent\.env")
conn = psycopg2.connect(
    host=os.getenv("SHAREBOOK_PROD_PG_RO_HOST"),
    port=int(os.getenv("SHAREBOOK_PROD_PG_RO_PORT")),
    dbname=os.getenv("SHAREBOOK_PROD_PG_RO_DATABASE"),
    user=os.getenv("SHAREBOOK_PROD_PG_RO_USER"),
    password=os.getenv("SHAREBOOK_PROD_PG_RO_PASSWORD"),
    sslmode=os.getenv("SHAREBOOK_PROD_PG_RO_SSLMODE", "disable")
)
```

## Varredura de segredo — receita

A auditoria de 09/06/2026 varreu **só `skills/**/*.md`** e declarou o repo limpo. Em 17/08/2026 apareceram 9 scripts `.py` versionados com senha de banco e a senha root de SSH da VPS. O defeito não foi a busca, foi o filtro.

**Regra: varredura de segredo é por conteúdo, não por extensão de documentação.** Cobrir no mínimo `.py`, `.ps1`, `.sh`, `.json`, `.yml` e `.md`.

Comando canônico (Bash tool, a partir da raiz do repo):
```bash
grep -rniE "password\s*[=:]\s*['\"][^'\"]{4,}|AKIA[0-9A-Z]{16}|sk-(proj|ant)-|ghp_|github_pat_|BEGIN [A-Z ]*PRIVATE KEY" \
  --include=*.py --include=*.ps1 --include=*.sh --include=*.json --include=*.yml --include=*.md . \
  | grep -v "\.venv\|node_modules\|os.getenv\|os.environ"
```

Complementar com uma varredura por valor: pegar cada senha real do `.env` e procurar literalmente pelo valor no repo. É o que pega o caso que o regex não prevê.

Depois de limpar, **checar o histórico** — `git log -S'<trecho>' --oneline`. Se o segredo já foi commitado num repo com remoto no GitHub, ele está comprometido e precisa de rotação; apagar do HEAD não desfaz nada.

## Python no Windows — armadilhas de versão

### `python3` no Windows = stub do Microsoft Store

No Windows, o comando `python3` pode resolver para um stub do Microsoft Store que não executa nada (retorna rc=9009 silenciosamente). Isso se manifesta em scripts Python que chamam subprocessos com `["python3", ...]` — eles travam ou falham sem mensagem útil.

**Fix correto e cross-platform**: usar `sys.executable` nos scripts:
```python
import sys, subprocess
subprocess.run([sys.executable, "outro_script.py", ...])
```
Isso funciona tanto no Windows quanto no Linux sem condicionais.

### `python` pode ser 3.14 sem dependências operacionais

Se Python 3.14 for instalado depois, pode sobrescrever o `python` no PATH. O ambiente operacional com todas as dependências (`psycopg2`, `boto3`, `dotenv`, `pikepdf`) é o **Python 3.12**:

```
C:\Users\raffa\AppData\Local\Programs\Python\Python312\python.exe
```

Checar antes de operações críticas: `python --version`. Se retornar 3.14 e houver falha de importação, usar o path completo do 3.12. Instalar dep faltante no 3.12: `C:\Users\raffa\AppData\Local\Programs\Python\Python312\python.exe -m pip install --user <dep>`.

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

Não presumir que `paramiko` já está instalado no Python 3.12 local — confirmar com `python -c "import paramiko"` antes de depender do utilitário canônico (`scripts/infra/vps_ssh.py`). Ausente em produção em 2026-07-15; instalar com `pip install --user paramiko` resolve.

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
- Usar `Invoke-WebRequest` em endpoint que responde HTTP 200 sem corpo e interpretar `Referência de objeto não definida para uma instância de um objeto` como falha certa da API. A mutação pode ter sido concluída e o erro vir apenas do cliente PowerShell ao processar a resposta vazia. Preferir `Invoke-RestMethod`; diante de resultado ambíguo, consultar o estado real por GET antes de repetir, principalmente quando a operação dispara e-mail ou outro efeito colateral.
- Confiar em memória de sessão quando o que precisava era registro durável.
- Deixar regra específica de Windows poluir a camada genérica do `AGENTS.md`.
- Usar `python3` sem verificar se é o stub do Microsoft Store — usar `sys.executable` nos scripts.
- Usar `python` sem verificar versão — pode ser 3.14 sem deps operacionais; o 3.12 é o ambiente canônico.
- Configurar `bypassPermissions` no project settings em vez do user settings.
- Tentar SSH não-interativo via shell sem paramiko.
- Assumir que `publish-once --id` não existe. A CLI canônica atual aceita `--id` e esse é o caminho preferencial para publicação manual cirúrgica; `--source + --limit 1` continua útil para processamento sequencial por source.
- Confiar no Bash tool para comandos longos do Windows (ex: `dotnet build`): já retornou saída vazia silenciosamente, inclusive em `echo`. Para build/git/dotnet, preferir o PowerShell tool (shell primário do habitat) e capturar log em arquivo com `*> $log`.
- **Inline Python no PowerShell com regex ou escaping**: comandos inline com `python -c "..."` quebram com regex, aspas aninhadas ou acentos (ex: heredoc `@'...'@` de um `-c` corrompendo `r"...".env"` em `rC:\...`). Sempre criar um arquivo `.py` temporário via `Write`, escrever o código nele e executar pelo path. Limpar o temporário depois.
- Abrir monitor de background (`run_in_background`) pra esperar deploy do Coolify. A notificação de conclusão já mentiu mais de uma vez (task "completed" com container ainda na imagem antiga) — a checagem direta (`docker ps`) é obrigatória de qualquer jeito, então o monitor não agrega nada, só risco de ficar órfão rodando por horas. Preferir checagem direta única; se não tiver terminado, avisar "ainda rodando" em vez de ficar em loop.
- Se mesmo assim abrir um monitor de background, esquecer de pará-lo quando a confirmação vier por outro caminho (ex: checagem manual). Rodou uma sessão inteira com 4+ monitores órfãos de deploys já confirmados horas antes, porque cada checagem manual "resolvia" o problema sem nunca chamar `TaskStop` no monitor equivalente. Regra: toda confirmação de deploy, por qualquer via, encerra o monitor de background correspondente na hora, não só quando ele mesmo notifica.

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

- Presumir cron agentico, sessões destacadas, subagentes persistentes ou memória ativa como se existissem aqui.
- Usar comandos PowerShell como se fossem shell POSIX.
- Rodar comando ou apontar caminho que só existia no runtime dormente (`/data/workspace/...`, `docker exec` no container do agente) sem checar que o alvo ainda existe.
- Deixar regra específica de Windows poluir a camada genérica do AGENTS.


## Browser pane — screenshot pode travar

`computer{action: screenshot}` no Browser pane já deu timeout sem modal aparente (confirmado 2026-07-11). Não insistir tentando diagnosticar — usar `get_page_text` como prova alternativa de validação; traz o conteúdo completo da página e costuma bastar para confirmar publicação/estado sem depender de captura visual.

## Outputs copiáveis

No Windows, outputs longos de scripts (ex: prompt da roleta de estilos) devem ser exibidos dentro de um bloco de código markdown (``` ... ```) para facilitar a cópia. Nunca exibir só como texto narrativo.

## Prints

Quando o Raffa mencionar olhe o print 82 use o caminho abaixo:

C:\Users\raffa\OneDrive\Documentos\Lightshot\Screenshot_82.png
