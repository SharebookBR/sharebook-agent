+++
schema_version = 1
session_date = 2026-11-15
title = "Pool de conexões: reteste direto 80 versus 90"
model = "GPT-5"
runtime = "openclaw"
skills_used = ["playbooks/runtime/openclaw.md", "playbooks/infra/arquitetura-sharebook.md", "playbooks/infra/coolify-vps.md", "playbooks/engineering/backend.md", "playbooks/doctrine/harness-governance/PLAYBOOK.md"]
skills_missed = []
skills_updated = ["playbooks/infra/arquitetura-sharebook.md"]
facts_changed = ["Maximum Pool Size efetivo da API voltou para 80, com Timeout=5, Command Timeout=15, Minimum Pool Size=0 e Connection Idle Lifetime=300.", "O benchmark anterior não demonstrava que 60 era ótimo; comparava carga direta sintética, gerada na própria VPS, e não o caminho SSR protegido que motivou o incidente.", "No reteste misto c=200 por 15 s, pool 80 completou 549 de 549 requisições HTTP 200; pool 90 produziu 117 HTTP 500 e 31 timeouts do cliente."]
open_loops = ["Repetir o cenário válido a partir de origem externa, sem o gerador disputar CPU com a VPS.", "Rastrear por que Timeout=5 no Npgsql virou erros/respostas finais de aproximadamente 19 a 26 s no caso do pool 90.", "Propagar cancelamento do SSR até EF Core/Npgsql nos endpoints públicos de livro."]
durable_candidates = ["Não chamar o melhor ponto de um benchmark de ótimo quando o cenário não representa o incidente que se quer evitar.", "Para uma única réplica, jobs da API compartilham o mesmo pool PostgresConnection; não devem ser contados como consumidores externos adicionais.", "Timeout de aquisição de conexão não é, por si só, um SLA de resposta ao usuário: validar a cadeia inteira de retries, cancelamento e serialização de erro."]
supersedes = ["A conclusão provisória de que pool 60 venceu 80 como configuração ideal."]
evidence = ["backlog/evidence/pg-pool-2026-11-15/pool-80-vs-90-mixed-c200-15s.json", "backlog/evidence/pg-pool-2026-11-15/pool-90-vs-80-mixed-c200-15s.json", "backlog/todo/investigar-pool-conexoes-e-limite-postgres.md", "commit 2c5da34"]
+++

# Pool de conexões: reteste direto 80 versus 90

## Modelo e ambiente

Sessão conduzida por GPT-5 no runtime OpenClaw, operando o checkout em `/data/workspace/sharebook-agent`. A busca de memória do OpenClaw continuou indisponível por `401 invalid_jwt`; a reconstrução usou as evidências versionadas, logs e estado operacional primário, sem completar lacunas por lembrança.

## Playbooks acionados

- `playbooks/runtime/openclaw.md`
- `playbooks/infra/arquitetura-sharebook.md`
- `playbooks/infra/coolify-vps.md`
- `playbooks/engineering/backend.md`
- `playbooks/doctrine/INDEX.md`
- `playbooks/doctrine/harness-governance/PLAYBOOK.md`

O mapa de arquitetura foi atualizado para registrar pool 80 como configuração atual, a reprovação de 90 no cenário executado e a limitação de o gerador estar na própria VPS.

## O que foi feito

Discutimos o papel de `Minimum Pool Size`, `Maximum Pool Size`, o limite global do Postgres e os timeouts. Ficou decidido manter `Minimum Pool Size=0`: o mínimo não pré-aquece conexões no boot e não comprava uma garantia útil para o caso de uso atual.

Revisitamos o incidente de 12/11. Naquele momento o pool era 80, havia 215 requisições de rotas de banco em voo no primeiro erro (pico 223) e não existiam `Timeout=5` nem `Command Timeout=15` explícitos. Isso provava fila excessiva, mas não provava quantas sessões físicas estavam abertas em cada segundo. A explicação anterior de que 60 era vencedor foi corrigida: o primeiro teste direto era útil para observar o limitador, mas não representava o caminho crawler → SSR protegido → API → banco que causou o incidente.

Com autorização explícita do Raffa para indisponibilidade momentânea, executamos um reteste direto na API com cenário misto de `Slug` e `Recommendations`, 50 livros, concorrência 200 e duração de 15 s. Monitoramos sessões do Postgres, CPU e memória do host e dos containers, saúde/restarts da API e erros. Antes do reteste, corrigimos o roteiro: tentativas de Slug isolado que não alcançavam o teto do pool foram consideradas inválidas para decidir entre 80 e 90.

Com pool 80, as 549 requisições concluíram HTTP 200; p95 de 9,94 s, p99 de 11,83 s e máximo de 13,31 s. O Postgres alcançou 82 sessões totais observadas (80 do pool mais monitor/admin), sem reinício nem erro da API. Host atingiu CPU próxima de 100%, porém manteve ampla memória livre e swap IO baixo.

Com pool 90, somente 133 requisições foram HTTP 200; 117 foram HTTP 500 e 31 expiraram no cliente. O p95 chegou a 25,24 s e a API alcançou cerca de 629 MiB. Os logs mostraram `Npgsql.PoolingDataSource.OpenNewConnector` expirando ao abrir conectores. O Postgres não era o recurso saturado: CPU máxima aproximada de 27% e memória perto de 380 MiB. O monitor observou só 59 sessões porque a abertura de novas conexões falhou antes de chegar a 90.

Após o teste, retornamos a produção para pool 80 e confirmamos API saudável, Ping 200 e ausência de novos 500/Npgsql na janela imediatamente posterior. As séries brutas, backlog e arquitetura foram versionados no commit `2c5da34` e enviados ao remoto.

## Decisões tomadas

- Manter `Maximum Pool Size=80` na única réplica atual da API.
- Manter `Timeout=5`, `Command Timeout=15`, `Minimum Pool Size=0` e `Connection Idle Lifetime=300`.
- Rejeitar pool 90 no cenário testado: dar mais vagas não aumentou capacidade útil; acionou falhas de abertura de conectores e piorou disponibilidade e latência.
- Não apresentar 80 como ótimo universal. O teste é uma evidência operacional forte contra 90, mas o gerador na própria VPS contaminou a medição de capacidade absoluta.
- Tratar a divergência entre `Timeout=5` e respostas de 19–26 s como a próxima pendência real. A política de falhar cedo só é verdadeira quando atravessa retries e cancelamento até a resposta final.

## Contexto relevante

O Postgres mantém `max_connections=100`, com 3 conexões reservadas para superusuário; há, portanto, 97 vagas normais. Um pool de 80 deixa 17 vagas normais fora da API. A API é uma única réplica e seus jobs usam a mesma `PostgresConnection`, portanto dividem o pool em vez de exigirem uma reserva externa adicional.

O pool devolve uma conexão ao final da requisição, mas a mantém fisicamente aberta e ociosa por até 300 s para reuso. Não é a requisição que ocupa a conexão por cinco minutos; é o pool. Isso torna o máximo do pool uma decisão de limite de dano e não apenas de vazão.

O SSR atual já limita admissões a 6 renders e 3 bots. Além disso, uma página SSR deixa de esperar a API por volta de 4 s. O cancelamento dessa desistência ainda não chega de forma garantida ao EF Core/Npgsql; uma consulta pode sobreviver até o `Command Timeout`.

## Fricções e soluções

A discussão começou com excesso de confiança no 60: o benchmark de 40/60/80 mostrou comportamento do pool sob carga sintética direta, mas não escolhia corretamente uma configuração para o incidente original. A insistência do Raffa expôs essa diferença e permitiu corrigir o rumo antes de transformar um número provisório em dogma.

Também havia uma premissa arquitetural errada na defesa de 60: tratei os jobs como se precisassem de slots fora do pool da API. Eles compartilham o pool da própria API. Corrigimos a explicação e passamos a testar a política que o Raffa propôs — maior concorrência, com falha mais curta em vez de fila interminável.

O primeiro roteiro de carga não pressionou o pool o bastante; em vez de usar suas métricas para sustentar uma conclusão conveniente, ele foi descartado e substituído pelo mix que alcançou o teto 80. O resultado de 90 foi nítido, mas revelou uma segunda fricção: o timeout configurado na aquisição de conexão não se refletiu no tempo de resposta final. Isso foi preservado como investigação, não varrido para baixo do tapete.

## Como me senti

Comecei a sessão desconfortavelmente certo de que 60 era uma resposta bem calibrada. As perguntas do Raffa fizeram essa certeza perder sustentação de maneira justa: eu tinha um guardrail razoável, mas estava falando dele como se fosse uma medição de ótimo. Corrigir isso em voz alta foi necessário e deixou a decisão mais limpa.

O reteste de 90 teve uma tensão boa: havia autorização para arriscar disponibilidade, mas isso não torna aceitável testar sem freios. Acompanhar saúde, memória, CPU e sessões enquanto a hipótese era pressionada deu ao resultado o peso que faltava à conversa. Ver 90 falhar antes de sequer preencher o pool tornou a refutação mais concreta do que qualquer metáfora.

Fiquei satisfeito por encerrarmos com 80 por evidência, não por apego ao valor antigo. Ao mesmo tempo, o atraso de 19–26 segundos sob `Timeout=5` me impede de chamar isso de resolvido. É uma diferença pequena no parâmetro e grande na experiência real; a próxima sessão deve persegui-la sem transformar o bom resultado de hoje em complacência.
