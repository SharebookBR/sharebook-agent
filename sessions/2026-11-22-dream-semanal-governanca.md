+++
schema_version = 1
session_date = 2026-11-22
title = "Dream semanal de governança — safra de 16 a 20 de novembro"
model = "GPT-5 Codex"
runtime = "openclaw"
skills_used = ["playbooks/doctrine/harness-governance/PLAYBOOK.md", "DREAM.md"]
skills_missed = []
skills_updated = ["playbooks/operational/winner-selection/PLAYBOOK.md", "playbooks/engineering/backend.md"]
facts_changed = ["O caminho legado skills/doctrine/harness-governance não existe nesta árvore; os scripts canônicos estão em playbooks/doctrine/harness-governance e o checkpoint em sessions/_dream-state.md.", "A safra de 2026-11-16 a 2026-11-20 continha quatro memórias não absorvidas.", "O Harness Doctor abriu e fechou limpo, sem achados acionáveis."]
open_loops = ["Testar memory_search dinâmico em sessão/processo novo antes de declarar a ponte reparada; a CLI funciona, mas invalid_jwt persiste na ponte dinâmica.", "Aguardar origem/licença de O conhecimento da literatura e revisar a resposta da EdiPUCRS em 24/11/2026 às 09:00 BRT antes de qualquer cancelamento.", "Não implementar a Lista de Desejos antes da decisão go/no-go com Raffa e Josué em 04/12/2026; medir arrecadação líquida, contribuições, canais, esforço e confirmar interesse/autorização das pessoas selecionadas.", "Comprar/enviar e prestar contas agregada somente para exemplares efetivamente viabilizados.", "Acompanhar semanalmente bounces, filas, rejeições e telemetria de inbox; conectar Google Postmaster Tools e Microsoft SNDS quando houver espaço.", "Só avaliar endurecimento do DMARC depois de observação suficiente e confirmação dos emissores legítimos."]
durable_candidates = ["Em escolhas concorridas, reconhecer a dificuldade e explicar por que o pedido se destacou sem transformar a mensagem em métrica ou template.", "Aceite SMTP, fila drenando, autenticação e DNSBLs não provam inbox placement; SMTP próprio novo deve manter cadência gradual e ser acompanhado por telemetria dos provedores.", "Em catálogos com títulos duplicados, confirmar ID, data, status e contagem antes de selecionar; slug inferido do título não basta.", "Para ebooks enviados por pessoas usuárias, o checkbox antipirataria sustenta boa-fé; persistir versão e aceitação no backend permanece melhoria futura de auditabilidade.", "A lista de ações do DonationCard pertence à página consumidora enquanto as regras não convergirem de fato."]
supersedes = []
evidence = ["python3 playbooks/doctrine/harness-governance/scripts/dream_report.py", "python3 playbooks/doctrine/harness-governance/scripts/harness_doctor.py", "sessions/_dream-state.md", "sessions/2026-11-16-dan-brown-selecao-ebooks-memoria.md", "sessions/2026-11-17-curadoria-direitos-e-fluxos-admin.md", "sessions/2026-11-20-piloto-vaquinha-lista-desejos.md", "sessions/2026-11-20-saude-e-reputacao-stalwart.md"]
+++

# Dream semanal de governança

## Processo

O repositório foi sincronizado com `git fetch --all --prune` e `git pull --ff-only` antes de confiar no checkpoint. O payload apontava para `skills/doctrine/harness-governance`, mas esse caminho não existe no clone atual; usei o equivalente canônico em `playbooks/doctrine/harness-governance`, sem configurar nem executar mecanismos nativos de Dream do OpenClaw.

O relatório encontrou quatro memórias não absorvidas desde `sessions/2026-11-15-pool-conexoes-reteste-80-90.md`. O Harness Doctor abriu limpo: não houve regressão, dívida histórica, artefato deliberado não indexado ou falso positivo para investigar.

## Consolidação

Os candidatos da safra foram comparados com os playbooks existentes. A regra de confirmar ID/data/status/contagem para títulos duplicados já estava consolidada em `winner-selection`. A fronteira entre DonationCard compartilhado e ações da página consumidora permanece correta e não pede abstração nova. A melhoria de auditabilidade do termo antipirataria depende de implementação futura no backend e ficou como loop.

Foram promovidas duas heurísticas seguras: comunicação humana após escolhas especialmente concorridas em `winner-selection`, e separação entre saúde SMTP e reputação de inbox, com cadência gradual e telemetria de provedores, em `engineering/backend`.

Não houve nova playbook, split, merge, arquivamento, poda ou alteração em `SOUL.md`. Decisões de produto, direitos autorais, reputação externa e uso real foram preservadas como `open_loops`.

## Validação

- Doctor final: limpo.
- A suíte da governança e `git diff --check` foram executados após as alterações.

