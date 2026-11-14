# Investigar pool de conexões e limite real do Postgres

## Escopo

Descobrir, com dados, qual configuração do pool de conexões da API e qual limite do Postgres fazem sentido para esta VPS (4 vCPU, 7,8 GiB de RAM), em vez de manter números herdados.

Hoje o pool está em `Maximum Pool Size=80`, com `max_connections=100` no Postgres, `Connection Idle Lifetime=300`, `Timeout=5` e `Command Timeout=15`. **O 80 provavelmente nunca foi calibrado: é um valor herdado/estimado** (o playbook de backend só registra a regra de deixar margem sobre o `max_connections`). `Minimum Pool Size` não está definido (padrão 0).

A decisão sai de medição. Perguntas a responder:

1. Em que número de conexões simultâneas o Postgres desta máquina para de ganhar vazão e começa a perder (a "curva do joelho")?
2. Um pool menor (com fila) entrega mais vazão e menos erros que um de 80 em 4 vCPU?
3. Manter conexões prontas (`Minimum Pool Size`) evita o custo de abrir muitas de uma vez numa rajada? No teste de 2026-11-13 houve `NpgsqlException` ao **abrir** conexão novas com o Postgres quase ocioso (no máximo 2 conexões).
4. **Hipótese a verificar, não medida:** quando o SSR desiste aos 4 s, a API continua a consulta até o `Command Timeout` (os 500 do teste tiveram ~20 s). Se for verdade, a conexão fica presa sem necessidade. Verificar se o cancelamento do cliente chega até o EF/Npgsql (por exemplo, via `RequestAborted`/`CancellationToken`) e quanto isso importa.
5. O `Timeout=5` e o `Command Timeout=15` atuais continuam adequados depois de medir?

**Não decidido:** qual será a solução (ajustar pool, pool mínimo, PgBouncer, cancelamento, outra). Isto é investigação; a decisão vem depois com os números.

## Teste de estresse do Postgres

Raffa autorizou em 2026-11-14 um teste de estresse para achar o limite do Postgres, **fora do horário comercial e sem se preocupar com derrubar o site** ("não se faz omelete sem quebrar ovos"). Mesmo com essa liberdade, registrar antes de começar:

- **Janela:** madrugada, longe de jobs agendados da API (conferir `JobHistories`) e de backups; avisar o time (e-mails do Rollbar).
- **Origem da carga:** de fora da VPS, ou com a limitação registrada.
- **Backup:** confirmar que existe backup recente e restaurável **antes** de levar o banco ao limite. O restore drill ainda não tem evidência de execução (`restore-drill-backups.md`); um banco levado ao limite pode ser reiniciado pelo kernel (OOM). Recomenda-se resolver ou ao menos mitigar isso antes do teste.
- **Método:** rampa de conexões e de consultas reais (as do `Slug` e do `Recommendations`, não só `SELECT 1`), repetida com diferentes tamanhos de pool, medindo vazão, latência p50/p95/p99, conexões ativas, CPU, memória, swap e I/O do host em série de 1 s.
- **Parada:** só por segurança dos dados ou ordem do Raffa; derrubar o site é aceito. Ainda assim, registrar o que cedeu primeiro (API, Postgres, host) e como o sistema se recuperou sozinho ou não.
- **Reversão:** voltar às configurações de antes do teste, registradas antes de começar.

## Valor

Evita dois erros opostos: um pool grande demais, que sob rajada disputa CPU e abre conexões demais num banco de 4 vCPU, e um pequeno demais, que enfileira sem necessidade. Também fecha a dúvida deixada pelo incidente de 2026-11-12: o gargalo foi o pool do banco ou o servidor inteiro?

## Risco

Alto no teste: pode derrubar API e banco, reiniciar containers e, no pior caso, exigir restauração. Mitigação: janela de madrugada, backup confirmado, reversão registrada. Risco de baixa confiança dos números se a origem for a própria VPS.

## Validação

- Curva de vazão e latência por tamanho de pool e por número de conexões, com as séries brutas guardadas.
- Recomendação escrita de `Maximum Pool Size`, `Minimum Pool Size`, `Timeout` e `Command Timeout`, com o dado que a sustenta.
- Resposta explícita à hipótese do cancelamento da consulta (confirmada, refutada ou não verificável).
- Depois de aplicar qualquer mudança: repetir o teste de `teste-carga-ssr-origem-externa.md` e comparar com o V2 (zero 500, recusas rápidas, humanos atendidos).

## Relações

- Origem: `backlog/done/protecao-sobrecarga-ssr.md` (incidente de 2026-11-12, testes de 2026-11-13, V2).
- Depende de série de CPU, memória e conexões para correlação: `observabilidade-sharebook-epico.md` (M7).
- `restore-drill-backups.md` (pré-requisito de segurança).
- `teste-carga-ssr-origem-externa.md` (inclui a investigação de memória e swap; teste vizinho, pode compartilhar a mesma janela).
- `Backend`: `playbooks/engineering/backend.md`, seção "Connection pool do Npgsql vs. `max_connections` do Postgres".
