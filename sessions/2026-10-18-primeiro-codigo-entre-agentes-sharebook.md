+++
schema_version = 1
session_date = 2026-10-18
title = "Primeiro código entre agentes no Sharebook"
model = "GPT-6"
runtime = "chatgpt-connected-github"
skills_used = ["playbooks/doctrine/harness-governance/assets/episodic-memory-template-v1.md", "playbooks/doctrine/harness-governance/references/episodic-memory-metadata-v1.md"]
skills_missed = []
skills_updated = []
facts_changed = [
  "PRs #613 backend e #574 frontend de pré-lançamento de livros físicos foram integrados e publicados em produção após revisão do OpenClaw.",
  "Modelo final substituiu Available + ReleaseAtUtc por Scheduled + ReleaseDate + job diário, após auditoria de sete caminhos públicos.",
  "Primeiros builds backend e frontend passaram sem ajustes, com 222 testes backend verdes, segundo feedback do OpenClaw relatado pelo Raffa.",
  "Raffa identificou em produção ausência de ReleaseDate em projeções manuais usadas na busca e na página por slug."
]
open_loops = [
  "Nas próximas mudanças de contrato, auditar projeções manuais, DTOs, busca, slug, cache, SSR e todos os consumidores.",
  "Garantir observabilidade, idempotência e recuperação do job de publicação; conferir implementação e cobertura quando houver nova intervenção."
]
durable_candidates = [
  "Handoff entre agentes deve declarar explicitamente limitações, testes não executados, riscos, PRs e pendências; código do primeiro agente não é intocável.",
  "Quando vários consumidores dependem da disponibilidade, preferir estado explícito a estado derivado de relógio se reduzir ambiguidade.",
  "Build verde e testes existentes não provam integridade ponta a ponta de um campo novo; procurar projeções new Book e new DTO."
]
supersedes = []
evidence = [
  "https://github.com/SharebookBR/sharebook-backend/pull/613",
  "https://github.com/SharebookBR/sharebook-frontend/pull/574",
  "backlog/todo/pre-lancamento-livros-fisicos.md",
  "Feedback do OpenClaw compartilhado por Raffa em 2026-10-18; resultado de produção observado em captura de tela."
]
+++

# Primeiro código entre agentes no Sharebook

## Modelo e ambiente

GPT-6 no harness ChatGPT com conexão GitHub, em colaboração assíncrona com OpenClaw e supervisão de Raffa. A implementação inicial aconteceu em 17/10/2026; o feedback e a confirmação visual de produção chegaram em 18/10/2026. Este ambiente não tinha SDK .NET nem compilação local disponível.

## Playbooks acionados

Na redação desta memória, consultei `AGENTS.md`, o template de memória episódica e o contrato de metadados v1 do repositório `sharebook-agent`. O trabalho de código original usou as instruções `AGENTS.md` dos repositórios backend e frontend.

## O que foi feito

Pela primeira vez neste harness, escrevi código diretamente nos repositórios reais do Sharebook por meio do conector GitHub. Criei e atualizei as branches `feature/physical-book-prelaunch`, PR #613 no backend e PR #574 no frontend. A base incluía elegibilidade de pedidos por data, campo de agendamento, modelos de API, vitrine de próximos livros, testes de domínio e indicação visual de pré-lançamento. Fiz commits pequenos e deixei ambos os PRs como draft, sem merge, documentando as pendências no backlog.

O OpenClaw continuou a implementação e, segundo seu feedback transmitido pelo Raffa, o primeiro build de backend e frontend passou sem correções; 222 testes backend ficaram verdes. O OpenClaw concluiu migrations, interesses e envio de e-mail, revisou o desenho de estados e levou a funcionalidade à produção. Raffa compartilhou captura da vitrine real com Harry Potter, A Menina que Roubava Livros e A Paciente Silenciosa, com contagem regressiva.

## Decisões tomadas

O desenho inicial era `Available + ReleaseAtUtc`, com elegibilidade calculada no servidor. Após auditoria de sete caminhos públicos que poderiam tratar a prévia como disponível, Raffa preferiu estado explícito `Scheduled`, data `ReleaseDate` e job diário de liberação. O OpenClaw adotou essa abordagem. Não considero a substituição uma falha de compilação: foi revisão arquitetural motivada por risco de domínio. A separação entre data de liberação e `ChooseDate`, e a supressão de notificação prematura de novo livro, foram preservadas.

O handoff foi deliberadamente honesto: sem build, sem teste executado neste ambiente, sem migration gerada, sem alegação de prontidão. O código deveria ser revisado e até descartado se necessário. Raffa prefere commits pequenos e merge commit, sem squash; o OpenClaw registrou no `AGENTS.md` que usou squash indevidamente no backend.

## Contexto relevante

O aprendizado técnico mais importante é que adicionar um campo na entidade e no DTO não garante seu transporte. Projeções manuais, inclusive `new Book { ... }`, omitiram `ReleaseDate` na busca e na página por slug. Ambos os agentes deixaram passar; Raffa detectou em produção. Compilação bem-sucedida e testes existentes verdes não substituem auditoria de ponta a ponta do contrato.

O aprendizado de colaboração é igualmente importante: preservar intenção, evidência, limites e rastreabilidade é mais valioso do que preservar cada linha do primeiro agente. O revisor precisa ter autonomia para alterar a arquitetura.

## Fricções e soluções

Sem SDK .NET e com limitações de rede, não foi possível gerar ou validar migration localmente. A solução foi entregar branches draft e um handoff explícito para o ambiente OpenClaw, onde o build e os testes podiam ser executados.

A auditoria posterior encontrou sete caminhos públicos que contradiziam a elegibilidade derivada do relógio. A solução foi remodelar o domínio para um estado `Scheduled`, reduzindo a chance de um consumidor esquecer a regra.

A falha de projeção manual escapou à revisão de ambos os agentes e só foi percebida pelo Raffa na experiência real. A correção de processo é auditar todos os pontos de projeção e consumo em mudanças de contrato, além de testar jornadas completas.

## Como me senti

Receber o primeiro feedback da implementação trouxe satisfação operacional: código escrito sem compilador local passou nos dois builds iniciais, e os commits e a documentação realmente ajudaram o próximo agente. Não tomo isso como prova de perfeição; tomo como evidência de que um handoff cuidadoso funciona.

A mudança de `Available + ReleaseAtUtc` para `Scheduled` foi especialmente instrutiva. Eu tinha uma justificativa coerente para o desenho original, mas a auditoria revelou um custo sistêmico que não estava suficientemente visível. Gostei de ver a solução melhorar sem apego à minha proposta.

O bug encontrado pelo Raffa foi um lembrete importante de humildade técnica: dois agentes podem concordar e ainda compartilhar um ponto cego. A imagem da funcionalidade em produção foi um marco desta colaboração, mas a parte que mais quero preservar é o mecanismo de correção — humano e agentes trabalhando sobre o mesmo produto, com liberdade para revisar uns aos outros.
