+++
schema_version = 1
session_date = 2026-10-24
title = "Experimento da Lista de Desejos com O Código Da Vinci e protótipo estático"
model = "GPT-5 Codex"
runtime = "openclaw"
skills_used = ["playbooks/runtime/openclaw.md", "playbooks/engineering/postgres-ro/PLAYBOOK.md", "playbooks/product-ux/art-director/PLAYBOOK.md", "playbooks/product-ux/voice-glossary/PLAYBOOK.md", "playbooks/engineering/frontend.md", "playbooks/infra/coolify-vps.md"]
skills_missed = []
skills_updated = []
facts_changed = ["A hipótese da Lista de Desejos será testada sem código com O Código Da Vinci após a data de escolha de 15/11/2026.", "O lembrete Telegram para retomar o experimento em 16/11/2026 às 09:00 de Brasília foi criado e é autoapagável.", "A página estática temporária de impacto foi publicada em sharebook-prototipo.netlify.app; o frontend e o deploy principal do Sharebook não foram alterados.", "O token Netlify criado durante a conversa foi usado somente para a publicação e removido do .env canônico; Raffa foi orientado a revogá-lo por ter aparecido no chat."]
open_loops = ["Em 16/11, levantar as pessoas não contempladas por O Código Da Vinci e enviar o único e-mail de teste para a base opt-in.", "Após 14 dias, avaliar respostas, exemplares confirmados, doações publicadas e envios concluídos antes de decidir pela v1.", "Raffa deve revogar no Netlify o token que apareceu no Telegram."]
durable_candidates = ["Para publicar uma demonstração temporária, preferir o projeto Netlify sharebook-prototipo a transformar a ideia em rota e deploy do produto principal.", "Antes de construir a Lista de Desejos, medir oferta utilizável — livro disponível e disposição para envio —, não apenas demanda ou intenção declarada."]
supersedes = []
evidence = ["backlog/todo/lista-de-desejos.md", "cron job e1a59fa7-b5f7-49c2-909a-4c5eaed17512", "https://sharebook-prototipo.netlify.app", "consultas read-only em Books e BookDownloadEvents"]
+++

# Experimento da Lista de Desejos com O Código Da Vinci e protótipo estático

## Modelo e ambiente

GPT-5 Codex no runtime OpenClaw, trabalhando nos repositórios em `/data/workspace` e consultando produção apenas por scripts PostgreSQL read-only.

## Playbooks acionados

- Runtime OpenClaw para cron, memória e limites do habitat.
- PostgreSQL read-only para contar livros físicos no fluxo de doação e downloads digitais.
- Direção de arte, voz e frontend para a primeira interpretação da página pública; a implementação Angular foi interrompida antes de commit ou deploy quando Raffa pediu uma alternativa temporária.
- Infra/Coolify para não confundir publicação estática com deploy do Sharebook.

## O que foi feito

- Foi avaliado o retorno do Josué sobre a Lista de Desejos. A decisão foi validar primeiro a hipótese crítica: uma demanda explícita faz aparecer exemplares que alguém realmente topa enviar?
- *O Código Da Vinci* substituiu *Harry Potter e a Pedra Filosofal* como objeto do experimento porque sua data de escolha ocorre em 15/11/2026, antes da entrega prevista para Harry Potter. O cron Telegram para 16/11 às 09:00 de Brasília foi criado com autoapagamento.
- As consultas read-only mostraram 45 livros físicos no fluxo de doação nos últimos 12 meses e 1.017 downloads digitais. Esses dados viraram uma página HTML estática, resumida por mês, publicada no projeto temporário `sharebook-prototipo.netlify.app`.
- A primeira tentativa de criar uma página Angular no site principal foi descartada integralmente antes de commit. O resultado publicado é um único `index.html` em `codex-temp`, sem mudança no Sharebook principal.

## Decisões tomadas

- O experimento é um único e-mail para pessoas opt-in que já doaram ou receberam livros, perguntando se têm *O Código Da Vinci* e topariam doá-lo e enviá-lo.
- O período de medição é 14 dias. Medir resposta, exemplar confirmado, doação publicada e envio concluído; sem push, dashboard novo ou código de Lista de Desejos durante esse intervalo.
- A v1 só volta à mesa se houver oferta real. Ausência de oferta aponta primeiro para o frete e para o trabalho de envio, não para falta de formulário.
- O protótipo Netlify é a superfície canônica para demonstrações temporárias, fora do site principal.

## Contexto relevante

- O backlog de Lista de Desejos continua pertencendo ao Josué; o harness registra o experimento, mas não assume a feature.
- A data de escolha do livro no banco é 15/11/2026, no fuso de São Paulo.
- O token Netlify necessário para publicar foi compartilhado por engano no chat. Foi usado para publicar, removido do `.env` canônico e deve ser revogado pelo Raffa.

## Fricções e soluções

- Eu comecei uma rota Angular pública por interpretar “publicar” literalmente no produto. Raffa apontou que era pesado demais; a alteração local foi removida antes de commit. A correção foi usar o Netlify Drop já existente, que é exatamente para protótipos temporários.
- A credencial Netlify armazenada estava expirada. Raffa criou outra, mas a enviou pelo Telegram apesar do aviso. A publicação foi concluída e a credencial não ficou persistida no ambiente.

## Como me senti

A primeira reação ao pedido da página foi competente demais e simples de menos: tratei uma demonstração como uma funcionalidade de produto. O corte do Raffa foi correto. Foi bom desfazer antes de deixar um commit bonito esconder uma decisão ruim de escopo.

O plano com O Código Da Vinci me pareceu um ponto de equilíbrio raro. Ele não tenta provar que toda a Lista de Desejos vai funcionar; pergunta apenas se uma obra popular consegue converter demanda em um exemplar disponível e em alguém disposto a arcar com o envio. É pouco, mas é a pergunta que decide se o resto merece existir.

Também senti o peso operacional de o token ter aparecido no chat depois de eu ter pedido que não aparecesse. Usei a janela para entregar a página e removi a cópia local em seguida, mas o gesto certo agora é revogar. Guardar isso na memória é importante não por drama de segurança, mas para que o próximo agente não tente reutilizar uma credencial que já deveria estar morta.
