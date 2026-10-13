# Sessão — variedade radical de capas e endurecimento da skill visual

## Resumo do que foi feito

- Revisamos a vitrine de ebooks e identificamos grupos de capas boas isoladamente, mas homogêneas demais quando vistas lado a lado.
- Atualizamos a capa de `Confessions` para uma direção visual radicalmente diferente, abandonando a pose contemplativa sentada e indo para uma cena noturna mais dramática.
- Atualizamos `O Pastor Amoroso` duas vezes até chegar numa ruptura de linguagem de verdade:
  - primeiro uma versão impressionista mais íntima
  - depois uma versão em desenho a lápis monocromático, que finalmente quebrou a família visual com `O Guardador de Rebanhos`
- Atualizamos `A Viuvinha` para uma linguagem de `aquarela`
- Atualizamos `Cinco Minutos` para uma linguagem de `cartaz/cartum editorial`
- Subimos todas essas capas novas em produção via API, preservando o restante do payload dos livros.
- Endurecemos a skill [`C:/REPOS/SHAREBOOK/codex-skills/sharebook-public-ebook-importer/SKILL.md`](C:/REPOS/SHAREBOOK/codex-skills/sharebook-public-ebook-importer/SKILL.md)
- Endurecemos também a referência [`C:/REPOS/SHAREBOOK/codex-skills/sharebook-public-ebook-importer/references/prompts.md`](C:/REPOS/SHAREBOOK/codex-skills/sharebook-public-ebook-importer/references/prompts.md)

## Decisões tomadas

- “Variedade” não pode significar só trocar pose, cor ou figurino dentro da mesma pintura editorial.
- Se duas miniaturas ainda parecem parentes demais, a regra de variedade falhou.
- Quando a prateleira começar a homogenizar, é melhor fazer ruptura consciente de macrofamília do que microajuste cosmético.
- Macrofamílias úteis para ruptura real:
  - aquarela
  - lápis / desenho manual
  - cartum / cartaz gráfico
  - colagem
  - foto realista
  - gravura

## Heurística validada

- A capa precisa ser julgada não só sozinha, mas também no contexto da fileira.
- O problema muitas vezes não está na capa individual; está na repetição do vocabulário visual.
- Para corrigir repetição, “mexer 5%” quase nunca resolve.
- Em covers do Sharebook, `ruptura brutal` costuma funcionar melhor do que `refino tímido` quando o objetivo é diferenciação.

## Alterações operacionais

Na skill e nas referências de prompt ficou registrado que:

- não conta como variedade:
  - mesma pintura com paleta diferente
  - mesma pose com outro personagem
  - mesma composição com luz diferente
  - mesma miniatura emocional com acabamento novo
- conta como variedade real:
  - mudar materialidade
  - mudar lógica de composição
  - mudar a distância da cena
  - mudar a sensação tátil da imagem
- se a fileira de um autor estiver homogênea demais, devemos forçar ruptura em pelo menos um título

## Livros impactados

- `Confessions`
- `O Pastor Amoroso`
- `A Viuvinha`
- `Cinco Minutos`

## Como me senti — brutalmente sincero

Sessão boa e meio viciante. Teve aquele momento clássico em que a primeira melhora parecia suficiente, mas ainda era “a mesma coisa com maquiagem nova”. O salto real veio quando paramos de tentar variar dentro do conforto e começamos a trocar a linguagem inteira. Isso foi importante porque refinou nosso gosto visual de um jeito prático, não abstrato. Em resumo: menos medo de radicalizar, mais clareza sobre o que é diversidade visual de verdade.
