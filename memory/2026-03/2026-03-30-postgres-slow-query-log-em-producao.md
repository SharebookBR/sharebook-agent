# Sessão 30/03/2026 - Postgres slow query log em produção

## Resumo do que foi feito
- Recuperei o contexto operacional recente e reli os playbooks locais antes de tocar em produção.
- Confirmei no `sharebook-api` que a aplicação de produção usa Postgres via `ConnectionStrings__PostgresConnection` e que o banco real não é o `coolify-db`.
- Verifiquei se havia instrumentação pronta para histórico de consultas lentas.
- Confirmei que `pg_stat_statements` não estava habilitado e que o Postgres também não estava logando slow queries (`log_min_duration_statement = -1`).
- Coletei sinais indiretos do momento:
  - sem queries longas ativas na janela observada
  - sem locks pendentes
  - cache hit muito alto
  - `JobHistories` apareceu como principal candidata para investigação futura por volume de `seq_scan`
- Inspecionei a retenção real dos logs do container do Postgres:
  - rotação Docker `json-file`
  - `max-size=10m`
  - `max-file=3`
- Medi a idade do log mais antigo ainda retido e confirmei que havia histórico desde `2025-10-11 23:15:02 UTC`.
- Debatemos a estratégia e optamos por começar pelo simples e útil:
  - habilitar slow query log
  - threshold de `1000ms`
  - sem depender de `pg_stat_statements` neste primeiro passo
- Tentei primeiro aplicar com o usuário da aplicação e validei que ele não tem permissão para `ALTER SYSTEM`.
- Corrigi a abordagem usando o usuário administrativo do container (`$POSTGRES_USER`), apliquei:
  - `alter system set log_min_duration_statement = 1000;`
  - `select pg_reload_conf();`
- Validei o valor configurado com sucesso:
  - `show log_min_duration_statement;` retornando `1s`
- Rodei um teste de fumaça com `select pg_sleep(1.2);` e confirmei a linha de slow query no log do container.
- Atualizei o playbook `codex-skills/coolify-vps.md` com as descobertas, fluxo recomendado e armadilhas reais da sessão.
- Atualizei o `AGENTS.md` com duas regras duráveis:
  - slow query como higiene operacional de produção
  - necessidade de usar o usuário admin do container para config global do Postgres

## Decisões tomadas
- Não ligar `pg_stat_statements` agora: útil depois, mas desnecessário para começar a capturar casos gritantes.
- Não logar tudo: o foco ficou em `1000ms` para não transformar observabilidade em ruído.
- Não reiniciar o Postgres sem necessidade: a mudança escolhida permitia `reload` simples.
- Não confiar em retenção “por dias” sem medir: a retenção foi tratada como consequência da rotação real do Docker.

## Evidências relevantes
- `log_destination = stderr`
- `logging_collector = off`
- `log_min_duration_statement` saiu de `-1` para `1s`
- Rotação do container Postgres:
  - `json-file`
  - `max-size=10m`
  - `max-file=3`
- Log mais antigo ainda retido na hora da análise:
  - `2025-10-11 23:15:02 UTC`
- Linha de validação observada no log:
  - slow query de `select pg_sleep(1.2)` com duração de aproximadamente `1203 ms`

## Contexto relevante para o futuro
- Para consultas SQL operacionais no VPS, `vps_ssh.py --script-file` continua sendo o caminho menos frágil.
- Arquivo temporário UTF-8 com BOM pode quebrar o `vps_ssh.py` no Windows ao imprimir o comando; para esse fluxo, gravar UTF-8 sem BOM.
- `ALTER SYSTEM` não pode ser empilhado com outras queries no mesmo `psql -c`, porque o Postgres reclama de bloco transacional.
- O usuário da app serve para leitura operacional, mas não para configuração global do Postgres.
- Agora já existe observabilidade mínima útil para flagrar queries acima de `1s` direto no log do container.

## Como me senti — brutalmente sincero
Sessão boa justamente porque não tentou bancar a sofisticada antes de fazer o básico direito. Tinha um risco claro de cair naquela armadilha clássica de querer resolver observabilidade com feature chique enquanto o ambiente nem registrava slow query. Em vez disso, saiu uma melhoria simples, útil e imediatamente verificável. Também foi bom validar retenção real antes de prometer qualquer fantasia sobre “X dias de histórico”, porque esse tipo de bluff operacional costuma cobrar juros depois. As únicas partes irritantes foram as velhas palhaçadas de quoting no PowerShell e o BOM no arquivo temporário, mas pelo menos renderam aprendizado formal em vez de virar só mais um episódio esquecível. No geral, fechou com a sensação certa: pouca firula, mais verdade operacional.
