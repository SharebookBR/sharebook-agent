---
name: winner-selection
description: Triar anonimamente solicitações de livros físicos, montar shortlist auditável, apoiar a decisão manual da pessoa doadora e registrar a pessoa ganhadora pela API oficial do Sharebook. Use quando Raffa pedir ajuda para escolher uma pessoa ganhadora de uma doação.
---

# Sharebook Winner Selection

Escolha humana assistida por critérios, com anonimato até a decisão final. Este é um fluxo de operação de doações: conduz uma decisão já existente no produto, sem redefinir sua interface ou identidade.

## Invariantes

- **Anonimato é essência do fluxo.** Antes da escolha, nunca mostrar nome, apelido, `userId`, endereço, contato, localidade específica ou outro identificador do solicitante.
- A regra também vale para identificadores escritos dentro do texto livre. Usar o script deste playbook para preparar os dados; nunca imprimir a resposta bruta de `RequestersList`.
- Na conversa com o doador, identificar cada candidato somente pelo apelido anônimo
  `RequesterNickName` já gerado pelo Sharebook (ex.: `Interessado 12`). Esse é o nome
  humano do fluxo; não substituir por código opaco na apresentação, shortlist ou decisão.
- O código opaco gerado pelo script é apenas um identificador técnico interno para
  registrar a escolha com segurança. Nunca exibi-lo ao doador quando houver apelido
  anônimo válido.
- Verificar fatos sobre o livro e o autor quando isso afetar a nota de conexão. Nunca pesquisar a pessoa candidata.
- Escrita bonita não ganha ponto extra. Texto dramático não prova veracidade. Não usar detector de IA como evidência.
- A pontuação faz triagem; a decisão final é manual e pertence ao doador.
- Registrar a escolha pela API oficial. Nunca alterar o ganhador diretamente no banco.
- **Autorização permanente do Raffa:** quando ele declarar um apelido anônimo como pessoa ganhadora, isso já autoriza o registro oficial. Não pedir uma segunda confirmação redundante; executar, validar o estado final e comunicar o resultado.

## Critérios padrão

Fechar os critérios com o doador antes de ler as solicitações. Defaults validados na primeira escolha assistida:

### Autenticidade e coerência — 0 a 3

- `0`: genérica, contraditória ou sem motivação identificável.
- `1`: plausível, mas com poucos elementos pessoais.
- `2`: motivação pessoal clara e coerente.
- `3`: motivação específica, coerente e espontânea, com detalhes relevantes.

Avaliar autenticidade **aparente**, sem investigar a vida do solicitante.

### Impacto do livro — 0 a 4

- `0`: não explica por que quer o livro.
- `1`: vontade genérica.
- `2`: razão pessoal concreta.
- `3`: importância relevante no momento atual.
- `4`: impacto excepcional, incluindo dificuldade de acesso ou finalidade muito significativa.

Não exigir exposição de pobreza, trauma ou intimidade. Avaliar o impacto explicado, não o sofrimento exibido.

### Conexão com a obra — 0 a 3

- `0`: nenhum interesse específico por aquela obra.
- `1`: menciona livro, autor ou sinopse sem explicar a conexão.
- `2`: conhece algum aspecto concreto da obra, dos temas ou do autor.
- `3`: estabelece conexão pessoal significativa com algo específico e verificável.

Não exigir leitura prévia nem conhecimento acadêmico.

### Reciprocidade demonstrada — 0 ou 1

- `0`: ainda não realizou doação no Sharebook.
- `1`: já realizou pelo menos uma doação.

O critério é binário. Quantidade doada não aumenta a nota, para não transformar poder aquisitivo em vantagem moral.

### Livros já recebidos

Não descontar pontos. Usar somente como desempate entre candidatos com a mesma pontuação, favorecendo quem recebeu menos livros.

### Qualidade mínima para shortlist

Extensão não é mérito: texto bonito ou longo não soma pontos. Mas a solicitação precisa sustentar a escolha com motivação pessoal minimamente desenvolvida e conexão específica com a obra. Uma linha que só declara interesse, cita a sinopse ou promete repassar o livro não entra na shortlist.

Brevidade não desclassifica por si só, desde que traga evidência suficiente para uma escolha humana. Não usar contagem de palavras nem transformar essa porta de entrada em prêmio para verborragia.

## Workflow

1. Obter a URL ou slug do livro.
2. Discutir e congelar critérios, pesos, tamanho desejado da shortlist e desempates.
3. Preparar solicitações anonimizadas:

```powershell
python C:\Repos\SHAREBOOK\sharebook-agent\playbooks\operational\winner-selection\scripts\winner_selection.py prepare --slug "<SLUG>"
```

4. Conferir se a saída não contém identificadores residuais antes de apresentá-la. Se encontrar um, interromper a avaliação e corrigir o sanitizador.
5. Excluir solicitações canceladas. Pontuar cada solicitação somente pelo texto anonimizado e pelas métricas permitidas.
6. Registrar uma evidência textual curta para cada nota. Não completar lacunas com suposições.
7. Ordenar pelo total. Se houver empate no corte, ampliar a shortlist; não eliminar arbitrariamente para fabricar um número exato.
8. Entregar ao doador somente apelido anônimo do Sharebook, texto anonimizado, notas,
   total, evidências e incertezas relevantes. Manter o `selectionCode` fora da conversa.
9. Ajudar a comparar finalistas sem revelar identidade. Recalcular apenas se um critério mudar por princípio, nunca para justificar preferência posterior.
10. Após o Raffa declarar o apelido anônimo vencedor, tratar a declaração como autorização para registrar. Para qualquer outra pessoa doadora, pedir autorização explícita antes da mutação.
11. Avisar que a escolha oficial atualiza todos os pedidos e dispara as notificações normais.
12. Com autorização, localizar internamente o `selectionCode` correspondente ao
    apelido na saída preparada e registrar sem expor o código na conversa:

```powershell
python C:\Repos\SHAREBOOK\sharebook-agent\playbooks\operational\winner-selection\scripts\winner_selection.py choose --slug "<SLUG>" --code "<CODIGO>" --confirm
```

13. Só declarar conclusão após o script confirmar:
   - resposta de sucesso ou estado final equivalente;
   - livro em `WaitingSend`;
   - solicitação vencedora em `Donated`;
   - zero solicitações em `WaitingAction`.
14. Após o registro confirmado, fornecer ao Raffa um texto curto, amigável e comemorativo, em primeira pessoa, para ele notificar a pessoa ganhadora.

## Falhas e mutações ambíguas

- `401`: renovar o token pelo mecanismo oficial e repetir somente porque a API confirmou que não autorizou a mutação.
- Timeout ou conexão interrompida durante `choose`: não repetir às cegas. Consultar o estado real; a operação pode ter concluído e apenas a resposta ter se perdido.
- Estado já concluído: tratar como idempotência observada e reportar, sem nova mutação.

## Terminologia

Usar **solicitação**, **pessoa doadora** e **pessoa ganhadora** em texto visível, conforme `../../product-ux/voice-glossary/PLAYBOOK.md`.
