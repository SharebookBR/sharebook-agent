+++
schema_version = 1
session_date = 2026-11-15
title = "Dream semanal — governança do pool Postgres e indexação dos scripts"
model = "codex"
runtime = "openclaw-cron-scheduler"
skills_used = ["DREAM.md", "playbooks/doctrine/harness-governance/PLAYBOOK.md"]
skills_missed = []
skills_updated = ["playbooks/_shared/PLAYBOOK.md"]
facts_changed = ["O Harness Doctor abriu com 3 achados nos artefatos do pg_pool_test e fechou limpo após indexação explícita.", "O pool 80 permaneceu aplicado; o pool 90 produziu 117 HTTP 500 e 31 timeouts no reteste misto c=200, mas a repetição externa continua necessária."]
open_loops = ["A scheduled task weekly-dream ainda descreve caminhos memory/ e skills/; os reais são sessions/ e playbooks/. Atualizar o SKILL.md da task é decisão do Raffa (arquivo fora do repo).", "Restaurar autenticação do provedor de embeddings do memory_search do OpenClaw (401 invalid_jwt, 2026-11-12).", "Repetir o cenário de pool válido a partir de origem externa, sem o gerador disputar CPU com a VPS.", "Rastrear por que Timeout=5 no Npgsql virou erros/respostas finais de aproximadamente 19 a 26 s no caso do pool 90.", "Propagar cancelamento do SSR até EF Core/Npgsql nos endpoints públicos de livro.", "Pré-processamento de páginas e recomendações: direção decidida, forma a discutir com o Raffa.", "Loops editoriais herdados do dream de 2026-11-08 e demais decisões de produto/infra dependentes do Raffa."]
durable_candidates = ["Não chamar o melhor ponto de um benchmark de ótimo quando o cenário não representa o incidente que se quer evitar.", "Para uma única réplica, jobs da API compartilham o mesmo pool PostgresConnection; não devem ser contados como consumidores externos adicionais.", "Timeout de aquisição de conexão não é, por si só, um SLA de resposta ao usuário: validar a cadeia inteira de retries, cancelamento e serialização de erro."]
supersedes = ["A conclusão provisória de que pool 60 venceu 80 como configuração ideal."]
evidence = ["git fetch origin && git pull --ff-only origin master", "python3 playbooks/doctrine/harness-governance/scripts/dream_report.py --repo-root . --json /tmp/sharebook-dream-report-2026-11-15.json", "python3 playbooks/doctrine/harness-governance/scripts/harness_doctor.py --root . --json (abertura: 3 achados; fechamento: limpo)", "python3 -m unittest discover -s playbooks/doctrine/harness-governance/scripts -p 'test_*.py' -v (32 OK)", "git diff --check", "git show ab318bd", "backlog/evidence/pg-pool-2026-11-15/", "backlog/todo/investigar-pool-conexoes-e-limite-postgres.md"]
+++

# Dream semanal — governança do pool Postgres e indexação dos scripts

## Processo

O repositório foi sincronizado com `git fetch origin && git pull --ff-only origin master` antes de confiar no checkpoint. O checkpoint oficial é `sessions/_dream-state.md`; a task externa ainda usa os caminhos legados `memory/` e `skills/`, um `open_loop` preservado por depender de decisão do Raffa fora deste repositório. Nenhum mecanismo nativo de Dream do OpenClaw foi executado ou configurado.

A safra delimitada pelo `dream_report.py` contém três memórias não absorvidas: `2026-11-14-dream.md`, `2026-11-14-iris-restore-drill-e-teste-de-carga-externo.md` e `2026-11-15-pool-conexoes-reteste-80-90.md`.

## Doctor: triagem e correção

O Doctor abriu com três achados, todos no diretório recém-criado `playbooks/_shared/scripts/infra/pg_pool_test/` pelo commit `ab318bd`:

| Achado | Classificação | Ação |
|---|---|---|
| `README.md` não mencionado em `playbooks/_shared/PLAYBOOK.md` | artefato deliberado, dívida de indexação no mesmo commit | listado explicitamente como documentação de janela, backup e limites |
| `pg_pool_monitor.py` não mencionado no `PLAYBOOK.md` | artefato deliberado, dívida de indexação no mesmo commit | listado como monitor de métricas por segundo |
| `pg_pool_probe.mjs` não mencionado no `PLAYBOOK.md` | artefato deliberado, dívida de indexação no mesmo commit | listado como rampa HTTP |

A pasta e o fluxo já estavam indexados em `playbooks/_shared/scripts/infra/INDEX.md` e referenciados pelo backlog; o detector exige, adicionalmente, que cada artefato fique observável no `PLAYBOOK.md` dono. A correção foi documental e segura: não houve deleção, mudança de comportamento dos scripts ou alteração de configuração de produção.

## Consolidação

Os fatos da safra já estavam promovidos nos destinos corretos: `arquitetura-sharebook.md` registra pool 80, Postgres 100, o resultado ruim do pool 90 e a necessidade de repetição externa; `coolify-vps.md` registra as limitações de origem e banda dos testes; `backend.md` já contém a regra geral de margem entre pool e `max_connections`. Não criei playbook, split, merge, arquivamento ou alteração no `SOUL.md`: as três heurísticas novas do reteste ainda têm uma ocorrência e ficam como candidatos para validação por uso recorrente.

O pool 80 continua aplicado. A conclusão anterior de que 60 seria ótimo foi supersedida pelo reteste válido c=200 por 15 s: pool 80 completou 549/549 HTTP 200; pool 90 teve 117 HTTP 500 e 31 timeouts. A interpretação permanece provisória porque o gerador estava na própria VPS. Os loops sobre origem externa, cadeia de timeout/cancelamento e propagação do cancelamento SSR foram preservados, sem inferir uma decisão humana.

## Validação

- Doctor final: limpo (`finding_count: 0`).
- Suíte da governança: 32 testes aprovados.
- `git diff --check`: limpo.

## Reflexão

Este ciclo foi pequeno, mas útil: os scripts não eram lixo nem estavam realmente invisíveis — a família e o índice já os apontavam —, porém a regra de indexação por artefato ainda não estava satisfeita. Tornar essa intenção explícita reduziu a chance de o próximo Dream confundir uma ferramenta operacional recém-nascida com entulho. O limite mais importante foi não transformar um único reteste em regra universal: o corpus ganhou precisão, mas não ganhou uma playbook nova por impulso.
