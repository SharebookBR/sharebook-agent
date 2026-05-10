---
name: sharebook-voice-glossary
description: Use quando a tarefa envolver copy, nomenclatura, microcopy, emails, labels, mensagens, UX writing, revisão semântica ou dúvidas sobre termos oficiais do Sharebook. Também usar quando houver suspeita de inconsistência entre livro físico e livro digital, ou ao decidir se termos como doação, solicitação, doador(a), ganhador(a), livro digital, vitrine e data de escolha devem aparecer em frontend, backend, templates ou textos operacionais.
---

# Sharebook Voice & Glossary

Skill canônica para linguagem de produto do Sharebook.

## Quando usar

Use esta skill quando a pergunta real for de **linguagem**, não de layout ou regra de negócio pura.

Exemplos típicos:
- revisar email/template do Sharebook
- decidir entre `pedido` vs `solicitação`
- decidir entre `ebook` vs `livro digital`
- validar se `doação` e `ganhador(a)` podem aparecer também em fluxo digital
- revisar CTA, label, título de tela, estado vazio ou mensagem de erro
- auditar inconsistência semântica entre backend, frontend e operação
- responder dúvida sobre voz oficial do Sharebook

## Fonte da verdade

A fonte primária atual é:
- `references/ux-writing-guide.md`

Leia esse arquivo antes de decidir terminologia quando houver dúvida real.

## Regras de Sinopse

Ao escrever sinopses para o catálogo:
- **Tamanho**: Exatamente 3 parágrafos.
- **Tom**: Envolvente e literário, focado no desejo de leitura, evitando descrições genéricas.
- **Veracidade**: Não inventar fatos. Pesquisar fontes confiáveis (ex: Wikipedia) antes de redigir.

## Regras canônicas já validadas

- Usar **livro digital**, nunca `ebook`, `e-book` ou `livro eletrônico` em texto visível.
- Usar **doação** como termo oficial do ato de oferecer o livro.
- Usar **solicitação** em vez de `pedido`.
- Usar **doador(a)** e **ganhador(a)** como papéis oficiais do fluxo.
- Usar **entrar** em vez de `login` em labels visíveis.
- Usar **código de rastreio** para envio.
- Usar **data de escolha** para o momento da decisão.

## Regra crítica sobre físico vs digital

Não presumir que termos de físico são proibidos no digital.

No Sharebook, a identidade do produto permite linguagem compartilhada entre físico e digital, inclusive termos como:
- doação
- solicitação
- doador(a)
- ganhador(a)
- vitrine

O que deve ser evitado não é o vocabulário compartilhado, e sim a **mecânica falsa**.

Exemplos do que corrigir:
- sugerir logística para livro digital quando ela não existe
- sugerir espera por decisão manual quando o fluxo digital for imediato
- induzir comportamento operacional de livro físico em etapa digital sem motivo real

Resumo de bolso:
- **termo institucional compartilhado** pode
- **promessa operacional errada** não pode

## Heurística prática

Ao revisar um texto, validar nesta ordem:
1. Usa o termo oficial do glossário?
2. Está coerente com a identidade do Sharebook?
3. Está coerente com a mecânica real daquele fluxo?
4. Está claro para alguém novo?
5. Diz o próximo passo quando necessário?

## Relação com outras skills

- Se o foco principal for layout, hierarquia visual ou usabilidade da interface, combinar com `sharebook-ux-reviewer`.
- Se o foco principal for mudança de código backend, combinar com `backend.md`.
- Se o foco principal for operação ampla do ecossistema Sharebook, combinar com `sharebook-master-playbook.md`.

## Saída esperada

Quando usar esta skill, responder explicitamente:
- qual termo é o correto
- por quê
- se o problema é de vocabulário ou de mecânica do fluxo
- qual ajuste mínimo resolve
