+++
schema_version = 1
session_date = 2026-10-23
title = "Onboarding por e-mail e descadastro com confirmação"
model = "GPT-5 Codex"
runtime = "openclaw"
skills_used = ["playbooks/runtime/openclaw.md", "playbooks/engineering/backend.md", "playbooks/engineering/frontend.md", "playbooks/engineering/analytics/PLAYBOOK.md", "playbooks/engineering/postgres-ro/PLAYBOOK.md", "playbooks/engineering/grafana-cloud-explorer.md", "playbooks/doctrine/harness-governance/PLAYBOOK.md"]
skills_missed = []
skills_updated = []
facts_changed = ["O descadastro público agora só altera preferências por POST após confirmação explícita; abrir o link não muda a conta.", "O endpoint tem throttle global de uma confirmação a cada cinco segundos e responde 429 com Retry-After quando bloqueado.", "A hipótese inicial de scanner não foi comprovada pelos logs; o clique do Raffa explica o caso concreto e o SSR mascara o user-agent do cliente.", "O funil de descadastro passou a emitir eventos GA4 sem dados pessoais."]
open_loops = ["Não apagar os nove aliases de teste nem os dois livros e duas solicitações vinculados sem confirmação explícita para remover também os quatro registros relacionados.", "Validar em produção a jornada de onboarding corrigida antes de qualquer backfill para usuários antigos."]
durable_candidates = ["Preferências e outros efeitos mutáveis nunca devem ser disparados por GET público; preservar simplicidade de UX com uma confirmação curta e POST idempotente.", "Logs do backend atrás do SSR não distinguem clique humano de scanner pelo user-agent; não inferir a origem sem evidência adicional."]
supersedes = []
evidence = ["sharebook-backend commits dbd3d57 e 44d4304", "sharebook-frontend commit c977427", "sharebook-agent commits 4c4c48e e 5aece40", "ShareBook.Api/Controllers/AccountController.cs", "ShareBook.Api/RateLimiting/UnsubscribeRateLimiter.cs", "src/app/features/auth/unsubscribe/unsubscribe.component.ts", "backlog/done/onboarding-ativacao-por-email.md"]
+++

# Onboarding por e-mail e descadastro com confirmação

## Modelo e ambiente

GPT-5 Codex no runtime OpenClaw, trabalhando nos repositórios `sharebook-backend`, `sharebook-frontend` e `sharebook-agent` em `/data/workspace`.

## Playbooks acionados

- Runtime OpenClaw para limites e estado do habitat.
- Backend, frontend, PostgreSQL read-only, Grafana/Loki e Analytics para implementar e auditar o fluxo.
- Harness governance no ritual de encerramento para registrar esta memória v1.

## O que foi feito

- A sequência fixa de cinco e-mails de onboarding foi implementada e publicada: imediato, dias 1, 3, 5 e 7, com as quatro artes editoriais aprovadas e CTA final para a comunidade WhatsApp.
- Foi investigado o comportamento de descadastro: nos últimos 14 dias, os logs registraram nove chamadas ao endpoint, oito `200`, uma `400` e quatro mudanças reais de `AllowSendingEmail` de verdadeiro para falso. A auditoria e os logs foram consultados sem expor dados pessoais na conversa.
- O fluxo de descadastro foi corrigido e enviado à `master`: página de confirmação, POST idempotente, throttle global de cinco segundos, `429` com `Retry-After`, eventos GA4 e cobertura de testes.
- O backlog concluído foi atualizado com a decisão, guardrails e validação da correção.

## Decisões tomadas

- A saída deve continuar fácil, mas uma visita GET não pode mudar preferências. O e-mail ainda abre uma página direta; só a confirmação explícita dispara o POST.
- O throttle é global por instância e dura cinco segundos, deliberadamente simples para um endpoint de baixo volume. Se houver múltiplas réplicas, a mesma regra precisará de armazenamento compartilhado.
- GA4 mede `unsubscribe_confirm_view`, `unsubscribe_confirmed`, `unsubscribe_rate_limited` e `unsubscribe_invalid_link`; nenhum evento envia e-mail, id ou token.
- `List-Unsubscribe` foi deixado fora desta correção: é uma melhoria válida, mas precisa de validação independente no SMTP.

## Contexto relevante

- O usuário oficial recebeu o primeiro e-mail de onboarding no ciclo do job. O descadastro posterior foi acionado por clique acidental do Raffa; o padrão de duas requisições em dez segundos não prova scanner porque o frontend SSR encaminha a chamada com user-agent Node em ambos os casos.
- Existem nove contas antigas de teste no formato de alias de e-mail. Elas têm dois livros e duas solicitações associadas; aguardar confirmação explícita antes de apagar o conjunto.
- O possível backfill para usuários antigos segue pausado até confirmar o fluxo corrigido em produção.

## Fricções e soluções

- A primeira leitura atribuiu cedo demais o descadastro ao scanner. A investigação posterior mostrou que a evidência não separa scanner de clique humano. A conclusão foi corrigida publicamente antes de agir sobre ela.
- O push HTTPS não tinha credencial interativa no runtime. O token canônico foi usado apenas em memória, via header Git temporário, sem imprimir ou persistir segredo.
- O build de produção do frontend atualizou somente artefatos ignorados; os worktrees finais ficaram limpos e alinhados à `master`.

## Como me senti

Senti um alerta saudável quando a história do scanner pareceu convincente demais com pouca evidência. Corrigir o diagnóstico depois do clique do Raffa foi importante: o fluxo precisava melhorar de qualquer forma, mas a causa não podia virar uma certeza inventada.

Gostei de como a discussão levou a uma solução menor e mais humana. A confirmação não virou formulário, login ou armadilha; ela apenas transforma um efeito irreversível em uma decisão explícita. O humor do Raffa sobre reduzir a volumetria ajudou a deixar claro o limite ético da fricção.

Fecho a sessão com sensação de continuidade concreta: produto, observabilidade, testes, backlog e memória contam a mesma história. Isso reduz bastante a chance de amanhã alguém retomar o backfill sem lembrar por que ele foi pausado.
