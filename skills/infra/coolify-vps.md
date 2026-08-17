# Coolify VPS Playbook

## Objetivo
- Guiar exploração operacional do VPS com Coolify sem depender de memória improvisada.
- Centralizar o passo a passo para diagnóstico de lentidão, saúde de containers e revisão de limites.

## Regra de Segredos
- Nunca registrar senhas, tokens, chaves, webhooks ou qualquer outro dado sensível neste arquivo.
- Credenciais devem ser lidas apenas do `.env`.
- Ao documentar comandos, referenciar apenas "ler do `.env`" sem repetir valores.
- No caso do VPS, o `.env` deve usar variáveis reais como `VPS_SSH_HOST`, `VPS_SSH_PORT`, `VPS_SSH_USER` e `VPS_SSH_PASSWORD`.

## Primeira Leitura
- Ler o `.env` para obter `VPS_SSH_HOST`, `VPS_SSH_PORT`, `VPS_SSH_USER` e `VPS_SSH_PASSWORD`.
- Assumir que o acesso é somente leitura até existir alinhamento explícito para alterar algo.
- Antes de mexer em tuning, coletar evidências.

## Estratégia de Acesso
- Este playbook assume sessões futuras em Windows com PowerShell.
- No Windows/PowerShell, `ssh` nativo pode existir sem helper para senha (`sshpass`, `plink`, módulos SSH do PowerShell).
- Se o acesso for por senha e não houver helper disponível, usar `python` com `paramiko`.
- O caminho preferido neste projeto é usar `scripts/infra/vps_ssh.py` em vez de reescrever bloco inline.
- Antes de improvisar, verificar o que existe no ambiente: `ssh`, `plink`, `sshpass`, módulo `Posh-SSH` e pacote `paramiko`.
- Se `paramiko` não estiver instalado, instalar localmente no usuário e seguir por script curto.
- Evitar gambiarras interativas frágeis para injetar senha no `ssh`.

 - Confirmar cedo se `paramiko` já está instalado com `python -c "import paramiko; print(paramiko.__version__)"`.

## Qual VPS é a produção

Desde **17/08/2026** a produção roda na **HostGator**: `129.121.36.220`, SSH na porta **22022**, credenciais no `.env` sob o prefixo `VPS_HOSTGATOR_SSH_*`.

A caixa antiga da Hostinger (`212.85.23.202`, prefixo `VPS_SSH_*`) ficou desligada como rollback até o cancelamento do plano. **Não presumir que `VPS_SSH_*` é produção** — esse prefixo ainda aponta para a máquina velha.

## Script Base para Windows
- Script reutilizável: `scripts/infra/vps_ssh.py`
- `--prefix` escolhe o conjunto de credenciais no `.env`. Padrão: `VPS_SSH` (caixa antiga).
- Exemplo de uso:

```powershell
# produção (HostGator)
python .\scripts\infra\vps_ssh.py --prefix VPS_HOSTGATOR_SSH --cmd "uptime"
python .\scripts\infra\vps_ssh.py --prefix VPS_HOSTGATOR_SSH --cmd "docker ps"

# caixa antiga (Hostinger), enquanto existir
python .\scripts\infra\vps_ssh.py --cmd "uptime"
```

- Para rodar vários comandos na mesma conexão:

```powershell
python .\scripts\infra\vps_ssh.py `
  --cmd "uptime" `
  --cmd "df -h" `
  --cmd "docker ps --format 'table {{.Names}}\t{{.Status}}'"
```

- O script lê o `.env` da raiz por padrão.
- O script espera as variáveis `VPS_SSH_HOST`, `VPS_SSH_PORT`, `VPS_SSH_USER` e `VPS_SSH_PASSWORD`.
- Para consultas maiores ou com SQL, preferir `--script-file` com arquivo temporário em `codex-temp/` em vez de insistir em quoting inline no PowerShell.
- `--script-file` do `vps_ssh.py` não executa um shell script multilinha; ele lê um comando remoto por linha. Heredoc, blocos SQL multilinha e scripts com várias linhas soltas vão quebrar feio.
- Para `psql` via `docker exec ... sh -lc`, preferir `sh -lc "psql ... -c \"SQL...\""` com aspas duplas por fora e SQL em uma linha. Esse padrão sobrevive melhor quando a query tem `interval`, datas, `timezone(...)` e identificadores com aspas.
- Limpar os arquivos temporários em `codex-temp/` ao final da investigação.
- `vps_ssh.py` já reconfigura `stdout`/`stderr` para UTF-8 com `errors="replace"` (fix 2026-07-15) — saída remota com emoji/acentuação não deve mais estourar `UnicodeEncodeError` no console CP1252 do Windows. Se aparecer mesmo assim, o script está desatualizado localmente (sync com o repo).

## Reconhecimento do ambiente Sharebook
- Confirmar cedo os containers com `docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'`.
- Não presumir que o banco da aplicação é o `coolify-db`; no ambiente atual ele é o Postgres do próprio Coolify.
- Descobrir o banco real da aplicação inspecionando as envs do `sharebook-api`, principalmente `DatabaseProvider` e `ConnectionStrings__PostgresConnection`.
- O `ConnectionStrings__DefaultConnection` pode continuar apontando para SQL Server legado. Não assumir que ele ainda é o banco ativo só porque está preenchido.

## Reconhecimento Inicial
- Identificar sistema operacional, uptime, disco e memória.
- Listar containers Docker ativos.
- Ler `crontab -l`.
- Verificar scripts operacionais customizados em `/usr/local/bin/`.

## Containers que merecem atenção
- `coolify`: aplicação web do painel. Primeiro suspeito em lentidão da interface.
- `coolify-proxy`: Traefik/proxy reverso. Observar, mas não culpar no escuro.
- `coolify-db`: Postgres do Coolify. Pode pesar em telas mais carregadas.
- `coolify-redis`, `coolify-realtime`, `coolify-sentinel`: suporte e observabilidade.

## Coleta para lentidão do painel
- Medir `docker stats --no-stream` dos containers do Coolify.
- Medir tempos de resposta locais com `curl` para o painel via `127.0.0.1:8000`.
- Correlacionar navegação real com CPU do `coolify`.
- Ler logs recentes de `coolify`, `coolify-proxy` e `coolify-db`.

## Higiene recorrente de banco
- Analisar slow queries em produção deve virar rotina, não só reação quando alguém já está reclamando.
- Sem observabilidade mínima, discussão de performance vira opinião com fantasia de diagnóstico.
- Se o Postgres ainda não estiver guardando slow queries, priorizar isso cedo no ciclo operacional.
- Para o estágio atual do Sharebook, `log_min_duration_statement = 1000` é um bom ponto de partida: pega casos gritantes sem transformar log em lixão.
- `pg_stat_statements` continua valioso para análise agregada, mas não é pré-requisito para começar a enxergar consultas ruins de verdade.

## Leitura segura do Postgres da aplicação
- Antes de consultar tabelas, confirmar `current_database()` e `current_user`.
- Se `pg_tables` ou `information_schema` voltarem vazios de forma suspeita, desconfiar primeiro do usuário usado no `psql`, não da base.
- No ambiente atual, para reconhecimento de schema funcionou melhor usar o usuário administrativo do container (`$POSTGRES_USER`) do que insistir no usuário da aplicação.
- Consultas iniciais úteis:
- `select schema_name from information_schema.schemata order by schema_name;`
- `select schemaname, tablename from pg_tables where schemaname not in ('pg_catalog','information_schema') order by schemaname, tablename;`
- Em leitura operacional, selecionar só as colunas necessárias e limitar linhas. Nada de `select *` preguiçoso.

## Slow query log no Postgres da app
- No ambiente atual, o Postgres da aplicação:
- usa `log_destination = stderr`
- está com `logging_collector = off`
- roda em container Docker com rotação `json-file`, `max-size=10m`, `max-file=3`
- Tradução prática: slow query log vai para o log do container; a retenção real depende do volume, não de uma política bonita por dias.
- Para habilitar captura dos casos gritantes sem restart, usar o usuário administrativo do container e aplicar:
- `alter system set log_min_duration_statement = 1000;`
- `select pg_reload_conf();`
- Validar com:
- `show log_min_duration_statement;`
- Teste de fumaça recomendado:
- rodar `select pg_sleep(1.2);`
- confirmar no `docker logs` uma linha com `duration: ... statement: select pg_sleep(1.2);`
- Não tentar fazer `ALTER SYSTEM` com o usuário da aplicação; no ambiente atual ele não tem permissão.
- Não empilhar `ALTER SYSTEM` com outras queries no mesmo `psql -c`; isso falha com `cannot run inside a transaction block`.
- Se a intenção for histórico de ocorrências reais, `log_min_duration_statement` resolve.
- Se a intenção mudar para ranking agregado das queries mais caras, aí sim complementar com `pg_stat_statements`.

## Fricções reais já validadas
- PowerShell + `docker exec` + `psql -c` + aspas simples vira armadilha rápido. Quando a consulta ficar minimamente complexa, migrar para `--script-file`.
- Mesmo usando `--script-file`, ainda vale a regra acima: cada linha precisa ser um comando fechado. Não tratar esse arquivo como `.sh`.
- Em query de Postgres com `interval '12 months'`, `date_trunc('month', ...)` e afins, evitar `sh -lc 'psql ... -c "..."'` se a SQL também tiver aspas simples. O shell remoto tende a fechar cedo e transformar diagnóstico simples em circo.
- `Set-Content -Encoding utf8` no Windows pode colocar BOM no arquivo temporário e quebrar o `vps_ssh.py` ao imprimir o comando. Para `--script-file`, gravar UTF-8 sem BOM.
- Container com nome aleatório do Coolify parece bagunça, mas é só o padrão dele. Descobrir dependências reais via `docker inspect`, não no chute.
- Para validar job semanal, cruzar três coisas: agenda no código, `JobHistories` e dados reais na janela consultada pelo job.
- `MailSender` saudável com fila vazia não prova nem reprova problema em job semanal. São sinais diferentes.

## Heurística validada
- Se a interface web do Coolify estiver lenta, o primeiro ajuste candidato é CPU do container `coolify`.
- `coolify-proxy` não deve ser alterado primeiro sem evidência.
- Só subir CPU do `coolify-db` se ainda houver lentidão depois de aliviar o `coolify`.
- Para desempenho de banco, começar por observabilidade simples e útil: slow query log com threshold conservador antes de inventar tuning no escuro.

## Limites operacionais conhecidos
- Existe script de boot/cron em `/usr/local/bin/limitar-coolify.sh`.
- Sempre conferir esse script antes de alterar CPU, porque qualquer mudança manual pode sumir no reboot.
- Se um limite for alterado ao vivo com `docker update`, persistir a mudança também no script.

## Fluxo recomendado para tuning
1. Coletar baseline com `docker stats`, `curl` e logs.
2. Pedir navegação real do usuário enquanto mede.
3. Identificar o container que satura primeiro.
4. Aplicar ajuste mínimo viável.
5. Validar novamente durante navegação real.
6. Persistir o ajuste no script operacional correspondente.

## DNS na VPS HostGator — três camadas independentes

Aprendido no corte de 2026-08-17, depois de um typo no IP publicado por alguns minutos.

Um erro de digitação no DNS (`29.` em vez de `129.`) sobrevive muito depois de corrigido, porque resolvedores públicos cacheiam o valor errado pelo TTL inteiro. No corte, o Google DNS segurou o IP inválido por quase uma hora enquanto o Cloudflare já servia o correto.

**A caixa tem três caminhos de resolução, e eles não conversam:**

1. **`/etc/resolv.conf`** — arquivo comum (não link), fixado pela HostGator em `8.8.8.8`. É o que `getent`, `curl` e praticamente todo processo do host usam de verdade.
2. **systemd-resolved** — está ativo, mas o `/etc/nsswitch.conf` é `hosts: files dns`, **sem o módulo `resolve`**. Então `resolvectl dns` e os drop-ins de `resolved.conf.d` não afetam a resolução real do host. Mexer só neles dá a ilusão de conserto.
3. **Docker** — containers ignoram o `resolv.conf` do host quando ele aponta para loopback; o que vale é `"dns"` no `/etc/docker/daemon.json`. Exige `systemctl restart docker`.

**Sintoma diagnóstico**: `resolvectl query X` responde certo e `getent hosts X` responde errado. Isso não é cache teimoso — é a camada 2 não estar no caminho. Ir direto na camada 1.

Configuração aplicada: Cloudflare primeiro nas camadas 1 e 3, com backups em `/root/resolv.conf.bak-pre-migracao` e `/root/daemon.json.bak-pre-migracao`. **O `resolv.conf` pode ser reescrito em reboot ou reprovisionamento** — reconferir depois de qualquer um dos dois.

**Efeito colateral não óbvio**: o frontend faz SSR chamando `api.sharebook.com.br` pelo nome público. Com DNS envenenado, cada render trava até o timeout, o healthcheck de 5s nunca passa, o container nunca fica `healthy` e o Traefik devolve **503**. O 503 parece falha de proxy e é falha de DNS. Antes de culpar Traefik ou healthcheck, rodar `docker exec <app> getent hosts <api>`.

## Backup agendado — "success" não prova backup

Descoberto em 2026-08-17, valendo desde pelo menos setembro de 2025.

O backup agendado do Postgres da aplicação estava com `databases_to_backup = postgres` — o banco de manutenção **vazio**, não os bancos reais. Rodava toda noite, subia para o bucket e gravava `success`. Todos os arquivos tinham exatamente **1055 bytes**. Durante cerca de um ano não existiu backup de dado real, e o painel afirmava o contrário.

**Regra: status `success` de backup não é evidência. Tamanho é.** Um dump do `sharebook` tem dezenas de MB; qualquer coisa na casa dos KB é banco vazio.

Conferir com:
```
docker exec coolify-db psql -U coolify -d coolify -At -F" | " -c "select id, enabled, frequency, databases_to_backup from scheduled_database_backups"
docker exec coolify-db psql -U coolify -d coolify -At -F" | " -c "select created_at, status, size, filename from scheduled_database_backup_executions order by id desc limit 5"
```

`databases_to_backup` é lista separada por vírgula. Valor correto neste ambiente:
`sharebook,sharebook_importer,pegasus_core,simula_plus`

Forçar uma execução real para validar:
```
docker exec coolify php artisan tinker --execute='$b = \App\Models\ScheduledDatabaseBackup::find(1); \App\Jobs\DatabaseBackupJob::dispatchSync($b); echo "OK";'
```

Ordens de grandeza esperadas hoje: `pegasus_core` ~76 MB, `sharebook` ~37 MB, `sharebook_importer` ~5 MB, `simula_plus` ~62 KB.

Vale generalizar a desconfiança: qualquer rotina que reporta sucesso sem nunca ter sido restaurada é candidata ao mesmo defeito.

## Backup das imagens (wwwroot) — backup de diretório

As capas dos livros vivem **só no disco da VPS**, em `/data/coolify/applications/sharebook-wwwroot/Images/Books` (~2.900 arquivos, 1,1 GB). O banco guarda apenas o nome do arquivo em `Books.ImageSlug`; a imagem é servida por `https://api.sharebook.com.br/Images/Books/<slug>`. **Não estão no S3 do Sharebook** — lá ficam os PDFs.

Até 2026-08-17 não existia backup nenhum delas. O `wwwrootbackup.zip` que morava dentro da própria pasta não era backup: era o pacote de *restore* usado para trazer as imagens na migração de setembro/2025 (confirmado no `.bash_history`). Nome de backup, função de veículo, e guardado no disco que deveria proteger.

Configurado via Coolify 4.3.x: **Persistent Storage → o mount → Configure Backup**. Grava em `scheduled_volume_backups` / `scheduled_volume_backup_executions`.

**Armadilha da interface**: marcar "Save to S3" sem que o combo de storage persista deixa `save_s3=false` e `s3_storage_id=null`. O job roda, gera o `.tar.gz` **no disco local**, e reporta `success`. Mesmo teatro do backup de banco. Conferir sempre no banco, não na tela:
```
docker exec coolify-db psql -U coolify -d coolify -At -F" | " -c "select save_s3, s3_storage_id, retention_amount_locally from scheduled_volume_backups"
docker exec coolify-db psql -U coolify -d coolify -At -F" | " -c "select id, status, size, s3_uploaded from scheduled_volume_backup_executions order by id desc limit 3"
```
`s3_uploaded = true` é o campo que importa; `status = success` não distingue local de remoto.

Disparar execução manual:
```
docker exec coolify php artisan tinker --execute='$b = \App\Models\ScheduledVolumeBackup::find(1); \App\Jobs\VolumeBackupJob::dispatchSync($b); echo "FIM";'
```

**Verificação final que vale (olhar dentro do bucket, não confiar em flag)** — script PHP montando um disk com a credencial que o Coolify já tem, executado por stdin (`php artisan tinker <arquivo>` cai no REPL interativo em vez de executar):
```
docker cp script.php coolify:/tmp/x.php && docker exec -i coolify sh -lc 'php artisan tinker < /tmp/x.php'
```
No script: `\App\Models\S3Storage::find(1)`, montar `config(['filesystems.disks.verif' => [...]])` e listar com `\Storage::disk('verif')->allFiles()`.

Tamanho esperado do tar.gz: ~1,16 GB. Qualquer coisa muito menor é backup vazio.

## Migração de instância Coolify entre VPS

Validado em 2026-08-17 (Hostinger → HostGator), Coolify 4.3.6 nos dois lados.

### Duas caixas ao mesmo tempo
- `vps_ssh.py` aceita `--prefix` (default `VPS_SSH`). Credenciais da caixa nova vivem em `VPS_HOSTGATOR_SSH_*` no `.env`.
- Para mover volume de dados, criar confiança SSH **direta entre as caixas** — nunca trafegar conteúdo pelo contexto do agente. `ssh-keygen` na origem, **append** da pública no `authorized_keys` do destino.
- **Nunca sobrescrever o `authorized_keys` de uma VPS HostGator.** Ela chega com ~11 chaves da plataforma; remover qualquer uma quebra o gerenciamento pelo painel deles. Só `>>`, nunca `>`.

### O que dumpar
- Dumpar **só o banco `coolify`** (`pg_dump -U coolify -d coolify --no-owner --no-acl`), **não `pg_dumpall`**. O dumpall arrasta roles com senha e conflita com a senha que a instalação nova gravou no volume do `coolify-db`.
- Com o dump de banco único, o único segredo que precisa atravessar é o `APP_KEY`.

### APP_KEY — a armadilha cara
O `APP_KEY` de `/data/coolify/source/.env` decifra env vars e chaves de deploy no banco. Trocar o arquivo **não basta**:

- `docker stop` + `docker start` **não relê `env_file`**. O container foi criado com a chave antiga e continua com ela na memória.
- É obrigatório recriar: `cd /data/coolify/source && docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --force-recreate coolify soketi`
- **Os nomes de serviço do compose não são os nomes dos containers.** Serviços: `redis`, `soketi`, `postgres`, `coolify`. O container `coolify-realtime` corresponde ao serviço `soketi`. Passar nome de container faz o compose abortar inteiro sem recriar nada — e o sintoma é idêntico ao de não ter feito nada.
- Trocar o `APP_KEY` no arquivo com `sed` é frágil: o valor é base64 e contém `/` e `+`. Preferir `grep -v '^APP_KEY=' .env > novo && cat chave-antiga >> novo`.

### Diagnóstico honesto de `DecryptException`
Não presumir chave errada. Comparar por hash, sem imprimir segredo:
```
docker exec coolify printenv APP_KEY | tr -d '\n' | sha256sum | cut -c1-16
grep '^APP_KEY=' /data/coolify/source/.env | cut -d= -f2- | tr -d '\n' | sha256sum | cut -c1-16
```
Hashes diferentes → problema é container, não chave.

Validar a decifragem sem vazar valor:
```
docker exec coolify php artisan tinker --execute='try { $v = \App\Models\EnvironmentVariable::first()->value; echo "OK len=" . strlen($v); } catch (\Throwable $e) { echo "FALHOU: " . get_class($e); }'
```

### Certificados
`/data/coolify/proxy/acme.json` guarda os certificados Let's Encrypt. **Certificado é vinculado a domínio, não a IP** — copiar o `acme.json` para a caixa nova faz o Traefik novo nascer com certificado válido, sem reemissão no corte e sem exposição a rate limit.

### O que mais copiar
`/data/coolify/ssh` (chaves de deploy), `/data/coolify/proxy`, `/data/coolify/databases` (nginx conf dos proxies de banco), `/data/coolify/services`. Pular `/data/coolify/backups` — é histórico, não estado.

## O que registrar depois
- Em `sharebook-agent/memory/`: diagnóstico, evidências, mudança aplicada e efeito percebido (memória episódica).
- Em `AGENTS.md`: apenas descobertas duráveis e heurísticas, nunca segredos.
