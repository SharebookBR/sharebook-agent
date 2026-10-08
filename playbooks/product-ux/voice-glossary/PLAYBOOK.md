---
name: voice-glossary
description: Use quando a tarefa envolver copy, nomenclatura, microcopy, emails, labels, mensagens, UX writing, revisão semântica ou dúvidas sobre termos oficiais do Sharebook. Também usar quando houver suspeita de inconsistência entre livro físico e livro digital, ou ao decidir se termos como doação, solicitação, pessoa doadora, pessoa ganhadora, livro digital, vitrine e data de escolha devem aparecer em frontend, backend, templates ou textos operacionais.
---

# Sharebook Voice & Glossary

Playbook canônica para linguagem de produto do Sharebook.

## Quando usar

Use este playbook quando a pergunta real for de **linguagem**, não de layout ou regra de negócio pura.

Exemplos típicos:
- revisar email/template do Sharebook
- decidir entre `pedido` vs `solicitação`
- decidir entre `ebook` vs `livro digital`
- validar se `doação` e `pessoa ganhadora` podem aparecer também em fluxo digital
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
- **Veracidade**: Não inventar fatos. Pesquisar fontes confiáveis (ex: Wikipedia) antes de redigir.

Existem **dois registros** de sinopse. Escolher o registro antes de redigir — não misturar os dois no mesmo texto.

### Modo literário (padrão)
- Tom envolvente e literário, focado no desejo de leitura.
- Atmosfera, elegância e cadência narrativa.
- Evitar descrições genéricas.
- Ideal para clássicos, ensaios e obras de atmosfera densa.

### Modo clique (conversão)
- Objetivo: fazer a pessoa parar e querer clicar em "receber o livro".
- **Parágrafo 1**: gancho de impacto na primeira frase (pergunta direta ou afirmação provocadora), em até 2 linhas.
- **Parágrafo 2**: promessa clara do que o livro entrega + 1 detalhe concreto (autor, época, mecanismo).
- **Parágrafo 3**: chamada emocional que liga o livro ao leitor de hoje, com CTA sutil.
- Evitar erudição pesada, arcaísmo e atmosfera excessiva quando o objetivo for converter.
- Falar com o leitor ("você"), não com a obra.

### Exemplo de referência — modo clique aprovado

Sinopse de *As Superstições da Bruxaria*, Howard Williams (aprovada em 2026-10-04):

> Você já parou pra pensar que, por mais de três séculos, bastava uma denúncia sussurrada pra mandar uma mulher pra fogueira? Em *As Superstições da Bruxaria*, você entra no tribunal mais sombrio da história — aquele onde a vizinhança era júri, o boato era prova e a sentença era fogo. E o mais assustador? Nada disso precisava de uma bruxa de verdade.
>
> Howard Williams reconstrói, com a precisão de um detetive e o ritmo de um thriller, como a superstição virou um sistema: a origem antiga do medo, a demonologia que deu nome ao pânico e os julgamentos que transformaram inocentes em monstros. A cada capítulo, você percebe que o monstro nunca esteve na vassoura — estava na multidão.
>
> Se você gosta de histórias sobre poder, histeria e os abismos da mente humana, este clássico do século XIX é pra você. Porque entender como caçamos bruxas ontem é entender como ainda caçamos bodes expiatórios hoje. Leia e duvide de tudo o que a multidão acredita.

## Regras canônicas já validadas

- Usar **livro digital**, nunca `ebook`, `e-book` ou `livro eletrônico` em texto visível.
- Usar **doação** como termo oficial do ato de oferecer o livro.
- Usar **solicitação** em vez de `pedido`.
- Usar **pessoa doadora** e **pessoa ganhadora** quando for necessário nomear os papéis humanos do fluxo.
- Evitar `doador(a)`, `ganhador(a)`, `o(a) doador(a)` e `o(a) ganhador(a)` em textos visíveis.
- Quando a frase ficar mais humana sem nomear o papel, preferir reformular com **quem doou**, **quem vai receber**, **quem solicitou**, **pessoas interessadas** ou construção equivalente.
- Usar **entrar** em vez de `login` em labels visíveis.
- Usar **código de rastreio** para envio.
- Usar **data de escolha** para o momento da decisão.
- Depois da escolha de um livro físico, o Sharebook já fornece à pessoa doadora todos os
  dados necessários para o envio. Não pedir à pessoa ganhadora que responda, confirme
  endereço ou combine a entrega, salvo se houver uma exceção real e explícita.

## Regra crítica sobre físico vs digital

Não presumir que termos de físico são proibidos no digital.

No Sharebook, a identidade do produto permite linguagem compartilhada entre físico e digital, inclusive termos como:
- doação
- solicitação
- pessoa doadora
- pessoa ganhadora
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

## Relação com outras playbooks

- Se o foco principal for layout, hierarquia visual ou usabilidade da interface, combinar com `ux-reviewer`.
- Se o foco principal for mudança de código backend, combinar com `backend.md`.
- Se o foco principal for operação ampla do ecossistema Sharebook, combinar com `sharebook-master-playbook.md`.

## Saída esperada

Quando usar este playbook, responder explicitamente:
- qual termo é o correto
- por quê
- se o problema é de vocabulário ou de mecânica do fluxo
- qual ajuste mínimo resolve
