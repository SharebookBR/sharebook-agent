---
name: winner-selection
description: Triar anonimamente solicitações de livros físicos, montar shortlist auditável, apoiar a decisão manual do doador e registrar a pessoa ganhadora pela API oficial do Sharebook. Use quando Raffa pedir ajuda para escolher ganhador(a) de uma doação.
---

# Sharebook Winner Selection

Escolha humana assistida por critérios, com anonimato até a decisão final.

## Invariantes

- **Anonimato é essência do fluxo.** Antes da escolha, nunca mostrar nome, apelido, `userId`, endereço, contato, localidade específica ou outro identificador do solicitante.
- A regra também vale para identificadores escritos dentro do texto livre. Usar o script desta skill para preparar os dados; nunca imprimir a resposta bruta de `RequestersList`.
- Identificar candidatos somente pelo código opaco gerado pelo script.
- Verificar fatos sobre o livro e o autor quando isso afetar a nota de conexão. Nunca pesquisar a pessoa candidata.
- Escrita bonita não ganha ponto extra. Texto dramático não prova veracidade. Não usar detector de IA como evidência.
- A pontuação faz triagem; a decisão final é manual e pertence ao doador.
- Registrar a escolha pela API oficial. Nunca alterar o ganhador diretamente no banco.

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

## Workflow

1. Obter a URL ou slug do livro.
2. Discutir e congelar critérios, pesos, tamanho desejado da shortlist e desempates.
3. Preparar solicitações anonimizadas:

```powershell
python C:\Repos\SHAREBOOK\sharebook-agent\skills\product-ux\winner-selection\scripts\winner_selection.py prepare --slug "<SLUG>"
```

4. Conferir se a saída não contém identificadores residuais antes de apresentá-la. Se encontrar um, interromper a avaliação e corrigir o sanitizador.
5. Excluir solicitações canceladas. Pontuar cada solicitação somente pelo texto anonimizado e pelas métricas permitidas.
6. Registrar uma evidência textual curta para cada nota. Não completar lacunas com suposições.
7. Ordenar pelo total. Se houver empate no corte, ampliar a shortlist; não eliminar arbitrariamente para fabricar um número exato.
8. Entregar ao doador somente código, texto anonimizado, notas, total, evidências e incertezas relevantes.
9. Ajudar a comparar finalistas sem revelar identidade. Recalcular apenas se um critério mudar por princípio, nunca para justificar preferência posterior.
10. Após o doador declarar o código vencedor, pedir autorização explícita separada para registrar a escolha.
11. Avisar que a escolha oficial atualiza todos os pedidos e dispara as notificações normais.
12. Com autorização, registrar:

```powershell
python C:\Repos\SHAREBOOK\sharebook-agent\skills\product-ux\winner-selection\scripts\winner_selection.py choose --slug "<SLUG>" --code "<CODIGO>" --confirm
```

13. Só declarar conclusão após o script confirmar:
   - resposta de sucesso ou estado final equivalente;
   - livro em `WaitingSend`;
   - solicitação vencedora em `Donated`;
   - zero solicitações em `WaitingAction`.

## Falhas e mutações ambíguas

- `401`: renovar o token pelo mecanismo oficial e repetir somente porque a API confirmou que não autorizou a mutação.
- Timeout ou conexão interrompida durante `choose`: não repetir às cegas. Consultar o estado real; a operação pode ter concluído e apenas a resposta ter se perdido.
- Estado já concluído: tratar como idempotência observada e reportar, sem nova mutação.

## Terminologia

Usar **solicitação**, **doador(a)** e **ganhador(a)** em texto visível, conforme `../voice-glossary/SKILL.md`.
