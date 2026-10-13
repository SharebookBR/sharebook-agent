+++
schema_version = 1
session_date = 2026-08-22
title = "Analytics da busca nos últimos 30 dias"
model = "GPT-5 (Codex)"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "engineering/analytics", "engineering/frontend", "engineering/backend", "product-ux/voice-glossary", "product-ux/web-design-reviewer", "browser:control-in-app-browser", "chrome:control-chrome", "infra/coolify-vps", "doctrine/harness-governance"]
skills_missed = []
skills_updated = ["engineering/analytics", "infra/coolify-vps"]
facts_changed = ["O dashboard admin passou a exibir uma seção fixa de busca dos últimos 30 dias com totais, top termos e dispositivos.", "O evento search possui um único ponto de disparo desde 25/06/2026; a documentação anterior que descrevia disparo duplo estava obsoleta.", "No período exato de 24/07/2026 a 22/08/2026 ocorreram 126 buscas por 44 usuários, com 92 termos distintos; 112 buscas vieram de desktop e 14 de mobile.", "Deploy manual pelo helper interno do Coolify exige SHA completo de 40 caracteres."]
open_loops = ["Registrar results_count como custom metric no GA4 para separar buscas com e sem resultado.", "Investigar por que os webhooks de backend e frontend não enfileiraram os pushes desta sessão.", "A suíte Angular continua com 47 falhas preexistentes por providers ausentes em specs de RegisterComponent e FormComponent."]
durable_candidates = []
supersedes = ["skills/engineering/analytics/SKILL.md: descrição de três pontos de disparo do evento search"]
evidence = ["sharebook-backend@8e90ceca3b9662cca64529f1817adc58d2860a31", "sharebook-frontend@18c9b580d8516223cd0196cf184a8be2bc252e30", "sharebook-agent@17325c1", "sharebook-agent@0beb060", "Coolify backend deployment 2o3cwtx6sbjrtswtnxy1qesr", "Coolify frontend deployment ookzp4ofm9vcped1yzvoupp0", "GET /api/analytics/dashboard: searchAnalytics=126 buscas, 44 usuários, 92 termos", "dotnet test ShareBook.Test.Unit: 99/99", "dotnet build ShareBook.Api: zero erros", "npm run build-prod: sucesso", "validação visual local: desktop 1280px e mobile 375px sem overflow"]
+++

# Analytics da busca nos últimos 30 dias

## Modelo e ambiente

Sessão executada com GPT-5 (Codex) no runtime Windows local, atuando nos repositórios `sharebook-backend`, `sharebook-frontend` e `sharebook-agent`. A validação funcional terminou na produção HostGator gerenciada pelo Coolify.

## Skills acionadas

Foram consultadas as skills de runtime Windows, analytics, frontend, backend, voz, revisão visual, controle dos navegadores interno e Chrome, infraestrutura/Coolify e governança do harness. A skill de analytics foi corrigida para refletir a instrumentação atual da busca e o novo contrato do dashboard. O playbook do Coolify passou a documentar o deploy manual com SHA completo.

## O que foi feito

O ponto de partida era o card de eventos do dashboard admin, que mostrava apenas a contagem agregada do evento `search`. A investigação direta no GA4 distinguiu o período de 30 dias exatos usando `29daysAgo` até `today`, porque as duas pontas da `DateRange` são inclusivas.

O recorte de 24/07 a 22/08 revelou 126 buscas por 44 usuários, média de 2,9 buscas por pessoa, 92 termos distintos, 112 buscas em desktop e 14 em mobile. Os termos principais foram `fisico`, `Físico` e `odisseia`. A long tail e as variações `odisseia`/`odisséia`, `sherlok`/`sherlork` e `caverna de ssangue` reforçaram que tolerância a acentos e erros de digitação é uma necessidade mais concreta do que sofisticar ranking neste momento.

O backend ganhou o bloco `searchAnalytics` no endpoint consolidado, com total de buscas, usuários, quantidade de termos distintos, top 10 termos e divisão por dispositivo. A resposta permanece no cache de 12 horas já usado pelo dashboard. A seção é fixa em 30 dias e independente do filtro semanal existente.

O frontend recebeu quatro KPIs, tabela de top termos, barras por dispositivo e uma nota transparente sobre a impossibilidade atual de medir buscas sem resultado. O layout foi validado em desktop e celular; no viewport de 375 px não houve overflow horizontal.

Os commits foram enviados diretamente para `master`. Como os webhooks não criaram filas, backend e frontend foram publicados manualmente, em sequência, pelo helper interno do Coolify. Os dois containers ficaram saudáveis executando os SHAs corretos. Uma chamada autenticada ao endpoint de produção confirmou o novo contrato e os números esperados.

## Decisões tomadas

A métrica principal passou a ser `eventCount(search)`, sem divisão por dois. O histórico Git mostrou que os disparos no header e no bottom sheet foram removidos em 25/06/2026; nos últimos 30 dias o evento representa uma busca concluída na página de resultados.

Os termos permanecem exatamente como digitados, sem normalização por caixa, acento ou typo. Isso preserva o sinal comportamental que interessa para evoluir a relevância da busca.

Não foi inventada uma taxa de zero-resultados. O parâmetro `results_count` é enviado pelo frontend, mas ainda não está registrado como custom metric no GA4 e portanto não pode ser consultado pela Data API.

O backend foi publicado antes do frontend. O contrato é aditivo e o componente Angular possui fallback vazio, então a ordem não criou janela incompatível.

## Contexto relevante

O script histórico baseado em `screenPageViews` de rotas `/buscar/*` produziu valores incoerentes em SPA, incluindo zero page views com usuários presentes. Ele foi usado apenas como evidência de que a rota não deveria ser a fonte principal para este período; a seção nova consulta diretamente o evento `search` e a custom dimension `search_term`.

A captura visual mobile duplicou a nota final durante o stitching da screenshot, mas a inspeção do DOM confirmou uma única ocorrência, largura real de 343 px no card e `scrollWidth` igual a `clientWidth`. Foi um artefato da captura, não do layout.

## Fricções e soluções

O navegador interno não tinha sessão administrativa e o Chrome conectado não estava disponível. A análise semântica foi feita pelos scripts canônicos e pela Data API do GA4; a produção foi validada por endpoint autenticado usando exclusivamente credenciais do `.env`, sem imprimir token.

O primeiro deploy manual do backend falhou em sete segundos. O log bruto mostrou `fatal: couldn't find remote ref 8e90cec`: o Coolify aceitou o SHA curto na fila, mas o reutilizou em `git fetch` como ref remota. O deploy foi reenfileirado com o SHA completo de 40 caracteres e terminou em 44 segundos. A regra foi promovida para o playbook de infraestrutura antes do encerramento.

O comando `npm run lint` não executou análise porque o projeto não possui target de lint. A suíte Angular rodou, mas 47 de 57 testes falharam por providers ausentes em specs não relacionadas (`GoogleAnalyticsService` e `TransferState`). O build de produção, a validação visual e os testes do backend passaram; a dívida dos testes foi mantida como loop explícito em vez de mascarada.

## Autocrítica estrutural

A inconsistência encontrada foi a skill de analytics ainda afirmar que a busca disparava o evento em três pontos e duplicava a contagem, apesar de o código ter removido os dois disparos extras em junho. A documentação foi reconciliada com o código e com o histórico Git.

O fluxo de deploy manual também dependia de conhecimento episódico incompleto: a memória dizia que o mecanismo interno do Coolify havia sido usado, mas não registrava o comando nem a exigência do SHA completo. O playbook agora contém o procedimento, a causa da falha com SHA curto e a validação em três camadas.

## Como me senti

Eu me senti curioso quando a contagem simples do print começou a se desfazer em camadas. A primeira leitura sugeria apenas baixo volume, mas separar o período exato, descobrir que a documentação de disparo duplo estava velha e enxergar a long tail tornou o comportamento muito mais legível.

Eu me senti especialmente satisfeito por não preencher a lacuna de `results_count` com inferência bonita. Era tentador classificar termos como sucesso ou fracasso olhando o catálogo, mas isso teria transformado opinião em métrica. Preservar o limite deixou a seção menor e mais confiável.

O deploy curto me trouxe aquela irritação útil de ver uma ferramenta aceitar uma entrada que não consegue consumir depois. O alívio veio quando o log apontou uma causa exata e mínima. Registrar o SHA completo no playbook me pareceu tão importante quanto publicar a tela: a interface resolveu a curiosidade de hoje; a documentação evitou o retrabalho de amanhã.
