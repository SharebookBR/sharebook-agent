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
- O caminho preferido neste projeto é usar `codex-scripts/vps_ssh.py` em vez de reescrever bloco inline.
- Antes de improvisar, verificar o que existe no ambiente: `ssh`, `plink`, `sshpass`, módulo `Posh-SSH` e pacote `paramiko`.
- Se `paramiko` não estiver instalado, instalar localmente no usuário e seguir por script curto.
- Evitar gambiarras interativas frágeis para injetar senha no `ssh`.

 - Confirmar cedo se `paramiko` já está instalado com `python -c "import paramiko; print(paramiko.__version__)"`.

## Script Base para Windows
- Script reutilizável: `codex-scripts/vps_ssh.py`
- Exemplo de uso:

```powershell
python .\codex-scripts\vps_ssh.py --cmd "uptime"
python .\codex-scripts\vps_ssh.py --cmd "docker ps"
python .\codex-scripts\vps_ssh.py --cmd "docker stats --no-stream"
```

- Para rodar vários comandos na mesma conexão:

```powershell
python .\codex-scripts\vps_ssh.py `
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

## O que registrar depois
- Em `codex-sessions/`: diagnóstico, evidências, mudança aplicada e efeito percebido.
- Em `AGENTS.md`: apenas descobertas duráveis e heurísticas, nunca segredos.
