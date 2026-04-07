---
name: sharebook-public-ebook-importer
description: Importa livros digitais de domínio público ou gratuitos para o Sharebook usando fontes aprovadas, capa autoral e API de produção. Use quando for espelhar catálogos públicos, cadastrar ebooks no Sharebook, validar duplicidade, gerar capa própria para evitar risco de copyright, aprovar livros e preparar o acervo para o mailing semanal.
---

# Sharebook Public Ebook Importer

Importar pouco e bem. Esta skill existe para transformar um livro público/gratuito em um ebook aprovado no Sharebook sem improvisar em produção.

## Workflow

1. Tratar a fonte como fila sequencial, não como caça ao tesouro.
2. Ler [`source-queue.md`](source-queue.md), que é a fonte da verdade da fila sequencial; não reler a última sessão episódica para esse fluxo.
3. Escolher sempre o primeiro item marcado como `pending` em [`source-queue.md`](source-queue.md).
3. Extrair metadados com [workflow.md](references/workflow.md) e `C:\REPOS\SHAREBOOK\codex-scripts\sharebook_source_extract.py`.
4. Se a fonte estiver quebrada, o PDF vier errado ou o cadastro já existir em produção, marcar o item com o status correto na memória e seguir imediatamente para o próximo `pending`.
5. Tratar a capa como autoral e vendável. Antes de escrever o prompt, escolher deliberadamente uma família visual, uma paleta dominante, um nível de luminosidade e um enquadramento que não repitam a solução dominante das últimas rodadas. A meta não é “parecer livro sério”; a meta é parecer desejável, magnético, quase com sex appeal visual de cartaz de cinema, sem cair em clichê barato. Gerar com `C:\REPOS\SHAREBOOK\codex-scripts\sharebook_openai_cover.py`, preferindo `--prompt-file` em UTF-8 no Windows.
6. Em sessão manual de PowerShell, se for fazer várias operações seguidas, carregar um token reutilizável com `. C:\REPOS\SHAREBOOK\codex-scripts\sharebook_prod_login.ps1`.
7. Checar duplicidade com `C:\REPOS\SHAREBOOK\codex-scripts\sharebook_prod_book.py find --type Eletronic`.
8. Revalidar o candidato escolhido com um `find` imediatamente antes do `create`; produção não respeita sua expectativa de exclusividade.
9. Para poesia, usar `Artes` como categoria no Sharebook; `Poesia` não existe hoje no produto.
10. Escrever uma sinopse final de vitrine com 3 parágrafos, tom envolvente e gancho forte de leitura.
11. Cadastrar e aprovar com `C:\REPOS\SHAREBOOK\codex-scripts\sharebook_prod_book.py create --approve`, preferindo `--synopsis-file` em UTF-8 para evitar caracteres quebrados no Windows.
12. Atualizar a memória da automação na mesma rodada:
    - item publicado vira `done`
    - duplicata vira `done` se o livro já existir em produção
    - problema da fonte vira `source_blocked`
    - problema local temporário vira `retry_later`
    - se o `create` cair duas vezes seguidas com aborto de conexão durante upload de PDF grande (ex.: `WinError 10053`), marcar `retry_later` com nota curta e seguir para o próximo `pending`
13. Ler o rastro da execução e transformar qualquer dor recorrente em melhoria concreta da skill ou dos scripts.

## Regra de variedade visual e apelo visual

Capa de livro não tem obrigação nenhuma de ser comportada. Se a miniatura ficou apenas “bonita”, “respeitável” ou “literária”, provavelmente faltou pulso.

Use esta régua sem romantizar mediocridade:

1. A capa precisa ter apelo imediato, como um bom cartaz de cinema:
   - vender uma experiência
   - prometer tensão, atmosfera ou fascínio em 1 segundo
   - criar vontade de clicar, abrir ou baixar
2. `Sexy` aqui significa:
   - magnética
   - sedutora visualmente
   - desejável
   - memorável
   - cheia de presença
3. Ousadia não é opcional quando a alternativa for “mais uma capa correta”.
4. Não ter vergonha de usar:
   - contraste forte
   - cor viva
   - composição agressiva
   - deformação controlada
   - escala dramática
   - tipografia com personalidade
5. A capa não deve pedir desculpa por existir. Se estiver tímida demais, polida demais ou reverente demais, refazer.

O que o cinema costuma acertar e capa de livro costuma acovardar:

- vende acontecimento, não só respeitabilidade
- escolhe uma imagem central com tensão real
- trabalha luz, cor, gesto e escala para sedução imediata
- aceita exagero e assinatura visual sem culpa

### Regra comercial explícita

Se houver conflito entre `bom gosto literário` e `poder de clique`, o default saudável do Sharebook é pender para o clique.

Traduzindo sem maquiagem:

- o óbvio pode ser uma virtude comercial, não um defeito
- se a capa ficar mais vendável por ser mais direta, mais melodramática, mais sexy, mais sentimental ou mais kitsch, isso é aceitável
- `sutil demais`, `elegante demais` e `civilizada demais` são falhas recorrentes de conversão
- a capa pode abraçar exagero, clichê útil, iconografia popular e até uma certa cafonice calculada se isso fizer a miniatura funcionar melhor
- respeitabilidade nunca deve vencer magnetismo por inércia

Regra de bolso:

- antes de defender uma capa por ser `bonita`, testar se ela também é `irresistível`
- se a opção A parecer mais culta e a opção B parecer mais clicável, a automação deve suspeitar que B é a escolha melhor
- a pergunta certa não é `isso impressiona diretor de arte?`; é `isso faz alguém tocar na capa?`

Cuidado importante:

- exagero comercial não autoriza capa genérica
- o kitsch só presta quando ainda conversa com a fantasia central da obra
- se a capa ficar apelativa mas indistinta, falhou do mesmo jeito

### Anti-padrões globais de personagem

Independentemente da categoria, tratar estes dois vícios como suspeitos por padrão:

- `bigode genérico de homem de época`
- `mulher com cara de freira, luto involuntário ou austeridade clerical`

Regra prática:

- não usar bigode como atalho visual automático para “século XIX”
- preferir barba mal feita, mandíbula mais forte, rosto mais desejável ou homem sem pelos faciais quando isso servir melhor à capa
- se a mulher parecer apagada, reprimida, clerical ou vestida por medo do gerador, corrigir o figurino
- salvo quando a obra pedir contenção real, preferir presença, magnetismo, colo, ombros, textura de pele e roupa com intenção
- tratar expressão neutra como defeito estrutural de capa, não como detalhe cosmético
- emoção precisa ser legível no rosto e no gesto: nomear no prompt o que cada personagem está sentindo e tentando esconder

Exceções existem, mas precisam ser defendidas pela obra, não pela preguiça do modelo.

Aplicação prática no Sharebook:

- preferir “isso vende a experiência do livro?” a “isso parece capa cult?”
- preferir imagem central concreta a metáfora frouxa
- preferir magnetismo a elegância burocrática
- preferir risco consciente a solução educadinha que some no grid
- para `Amor`, preferir química humana, escândalo e desejo legível a ambientação respeitável
- para `Amor`, se a miniatura não sugerir `tem história quente aqui`, ela provavelmente está fria demais

### Regra especial para categoria `Amor`

Em `Amor`, capa bonita mas comportada continua ruim. O alvo não é respeitabilidade; é clique, curiosidade e tensão emocional imediata.

Use esta heurística sem vergonha:

1. O centro da capa deve ser gente, não decoração.
2. Expressão facial forte vale mais que cenário caprichado.
3. Proximidade, toque, confronto, carta comprometedora, ciúme, vigilância e tensão sexual/social valem mais que símbolo abstrato.
4. Meio-corpo, close ou casal com química quase tátil costumam performar melhor que figura isolada distante.
5. Elegância não pode virar castidade visual. Se a capa estiver respeitável demais, ela falhou.

Checklist prático para `Amor`:

- o rosto tem intenção ou está só bonito?
- existe boca, olhar ou gesto sugerindo desejo, culpa, provocação ou rendição?
- o grid pequeno promete fofoca, escândalo, obsessão ou perigo emocional?
- os personagens vendem calor humano real ou parecem manequins cultos?
- o cenário ajuda a cena ou roubou protagonismo?

O que costuma funcionar:

- casal em tensão visível
- meio-corpo ou close com leitura imediata
- triângulo emocional sugerido por terceiro observador
- carta, luva, espelho, batente, cama, corredor, salão, porta entreaberta
- paleta quente ou sedutora com contraste claro
- quando a obra realmente suportar erotização física mais livre, corpo também pode virar gancho comercial: pele quente, clavícula, costas, pernas, seios, torso masculino, e até `abdômen trincado suado` se isso ajudar a vender a fantasia certa da obra
- em `Amor`, mulheres devem tender a aparecer desejáveis e magnetizadas pelo próprio corpo: decote, ombros, colo e silhueta são default saudável, exceto quando a obra pedir claramente o contrário

O que costuma matar a capa:

- personagem sozinho olhando para o nada
- excesso de distância
- expressão neutra
- composição “bonita” mas sem calor
- medo de parecer apelativa demais
- homem genérico de época com bigode padrão quando o livro não pede isso com força real
- roupa feminina acidentalmente austera, clerical, de luto ou “quase freira” quando a obra pede desejo, brilho social ou sensualidade
- figurino feminino fechado demais, sem colo, sem pele e sem tensão corporal por pudor automático do gerador

Para `Amor`, é melhor correr o risco de ser um pouco apelativo do que morrer de bons modos.

Corolário operacional:

- se a escolha estiver entre `romance literário respeitável` e `novela perigosa que dá clique`, suspeitar primeiro da novela
- se a capa estiver sexy, quente, fofoqueira ou escandalosa, isso não é desvio automático; pode ser exatamente o acerto comercial
- pudor visual raramente ajuda o Sharebook a crescer

Exceção útil para não castrar a capa por moralismo automático:

- se a obra pedir fetichização mais livre de forma compatível com seu imaginário, a automação pode assumir isso sem vergonha
- nesse caso, usar apelo corporal explícito como linguagem visual legítima, não como acidente
- exemplos possíveis: torso masculino em destaque, boca úmida, pele luminosa, decote forte, pernas, abraço mais físico, suor, calor tropical, magnetismo carnal
- `abdômen trincado suado` não é proibido; só não pode virar muleta genérica em livro que não pede isso
- bigode também não pode virar muleta genérica de “homem do século XIX”; só usar quando a obra ou a iconografia realmente pedirem muito
- se a personagem feminina principal estiver parecendo freira, viúva em luto ou dama apagada sem que isso seja parte central da obra, a capa falhou no figurino
- decote é permitido e até preferível em `Amor` quando ajudar a vender desejo, status, sedução ou calor humano; não tratar colo e ombros como tabu automático

Antes de gerar a capa, passar por este mini-checklist sem preguiça:

1. Ler a memória da automação e identificar as últimas 2 ou 3 famílias visuais usadas.
2. Escolher uma família visual diferente da usada no livro imediatamente anterior.
3. Se as últimas 2 capas caíram na mesma macrofamília (`pintura/ilustração pictórica`, `cartaz gráfico`, `foto realista`, `gravura`, `desenho manual`), forçar a próxima para outra macrofamília.
4. Definir explicitamente:
   - família visual
   - cena central concreta
   - paleta dominante
   - temperatura cromática dominante e cor de ruptura
   - luminosidade
   - enquadramento
   - emoção dominante de cada personagem principal
   - microexpressão ou gesto-chave de cada personagem principal
   - lista curta do que evitar
5. Só depois escrever `cover-prompt.txt`.

Checklist cromático extra, porque “estilo novo” com cor velha continua parecendo primo do anterior:

- a paleta inteira caiu no mesmo campo térmico (`quente demais`, `fria demais`, `toda sépia`, `toda petróleo`)? Se sim, abrir contraste.
- existe uma cor de ruptura clara para ventilar a miniatura e impedir sensação de capa abafada?
- o fundo está dominando tudo ou ainda deixa os elementos respirarem?
- a capa parece elétrica e magnética, ou apenas envelhecida, empoeirada e “de época”?
- se o incômodo for difícil de nomear, testar estas hipóteses primeiro: `quente demais`, `abafada`, `envelhecida demais`, `sem respiro`, `falta cor que corte`.

### Anti-padrão cromático: pôster exposto ao sol

Tratar a estética `pôster exposto ao sol`, `pigmento lavado`, `estampa de camisa após 100 lavagens`, `papel antigo desbotado` e derivados como defeito presumido, não como elegância automática.

Sintomas típicos:

- paleta cansada
- cor sem sangue
- contraste morno
- sensação de arte que já nasceu velha
- thumbnail que some porque tudo parece gasto, seco ou pálido demais

Regra prática:

- se a capa estiver parecendo `lavada`, `cozida`, `empoeirada`, `begeada`, `pastel envelhecido` ou `sol demais sem pigmento`, assumir problema cromático até prova em contrário
- abrir cor, contraste e temperatura antes de defender a imagem por “delicadeza”
- exigir ao menos uma decisão cromática com pulso real, mesmo em obras melancólicas ou líricas

Única exceção:

- manter essa fadiga cromática só quando a própria obra gritar por desgaste, aridez, decadência, memória corroída ou documento antigo como parte essencial da fantasia visual
- fora disso, tratar `pôster exposto ao sol` como anti-padrão do Sharebook

O que NÃO conta como variedade:

- trocar só a cor mantendo a mesma pose e o mesmo enquadramento
- trocar só a roupa mantendo a mesma pintura editorial com personagem central
- trocar personagem em pé por personagem sentado, mas preservar a mesma linguagem plástica
- fazer “mais uma capa bonita” dentro da mesma família pictórica dominante da fileira
- fazer uma capa “respeitável” que não cria desejo de clique

Se a miniatura nova ainda parece “irmã quase gêmea” da anterior, a regra de variedade falhou.

Famílias visuais recomendadas para rodízio:

- `foto realista encenada`
- `pintura impressionista/luminosa`
- `óleo clássico`
- `desenho à mão com tinta, lápis ou gouache`
- `cartaz modernista/gráfico`
- `art nouveau/decorativo`
- `gravura/xilogravura/linocut`
- `colagem editorial`
- `litografia vintage`
- `minimalista tipográfica com imagem forte`

## Regras

- Usar `livrosdominiopublico.com.br` como fonte principal no MVP.
- A ordem do sitemap vira ordem oficial da fila; não reordenar por gosto pessoal enquanto houver item `pending` antes dele.
- Aceitar a afirmação de domínio público/gratuito da fonte como suficiente no MVP.
- Nunca assumir que capa de terceiros pode ser reutilizada.
- Preferir desistir do título a entrar em novela de PDF, metadata ou capa.
- Não voltar a triar do zero a cada execução; a memória sequencial existe justamente para impedir essa perda de tempo.
- Para o acervo do Sharebook, fazer esforço real para priorizar livros em português quando a obra permitir. Isso inclui procurar fonte alternativa, tradução em domínio público ou edição gratuita confiável antes de se conformar com inglês.
- Inglês é fallback aceitável, não padrão desejado. Se depois de um esforço razoável não houver versão boa em português, seguir com a versão em inglês sem travar a categoria.
- Para esta automação, não ler a última sessão em `codex-sessions/`; esse custo não está pagando valor prático.
- Se a automação perder a corrida para outro cadastro entre a triagem e o `create`, pular para o próximo candidato em vez de forçar `delete-existing` sem necessidade.
- Livro físico existente com o mesmo título/autor não bloqueia cadastro de ebook; a duplicidade relevante neste fluxo é ebook contra ebook.
- Para acervo de poesia, mapear `Poesia` para `Artes` ao cadastrar; é a categoria disponível no produto hoje.
- Se um PDF muito grande derrubar o upload duas vezes seguidas com erro de conexão local/API, tratar como `retry_later` e preservar a rodada para outro título em vez de insistir até desperdiçar a execução inteira.
- Preferir `update` quando a mudança for editorial ou incremental: categoria, sinopse, autor, título, capa sem troca estrutural do registro ou ajustes pequenos de metadata.
- Preferir `delete` + `create` só quando a troca principal realmente justificar recriação do ebook, como correção estrutural ruim de cadastro, slug muito comprometido ou quando o `update` não preservar bem o resultado esperado.
- A sinopse final não deve soar burocrática: usar 3 parágrafos com atmosfera, conflito e promessa de leitura.
- A capa não pode cair automaticamente sempre na mesma família “pintura editorial vintage com personagem central”; se essa solução já dominou as rodadas recentes, escolher outra linguagem.
- Variação não é aleatoriedade burra: escolher estilo por afinidade com a obra, mas usar a memória recente como freio contra repetição.
- Variar também luz, composição e materialidade. Não adianta trocar só a paleta e entregar a mesma capa com roupa diferente.
- Quando uma fileira de livros do mesmo autor ou do mesmo universo visual começar a ficar homogênea demais, forçar ruptura em pelo menos um dos títulos com outra macrofamília (`aquarela`, `lápis`, `cartaz gráfico`, `cartum`, `colagem`, `foto realista`, etc.).
- Em revisões de capa, preferir ruptura brutal e consciente a microajuste cosmético. Se o problema é repetição, a solução não é “mexer 5%”.
- Em revisões de capa, se o problema for falta de apelo, tratar como problema real. “Está bonito” não basta; a capa precisa puxar o olho e vender experiência.
- Em revisões de capa, quando a composição estiver boa mas a imagem parecer “cozida”, “abafada” ou “envelhecida”, atacar primeiro a paleta antes de jogar fora a ideia inteira.
- `Sexy` também passa por cor: não basta choque visual; a capa precisa ter tensão e desejo sem ficar cromaticamente pesada ou marrom de antiquário.
- Em qualquer categoria, se os personagens parecerem sem emoção, obrigar o prompt a explicitar: olhar, boca, tensão da mandíbula, postura, inclinação do tronco, mãos e intenção dramática.
- Em `Amor`, suspeitar cedo de quatro culpas recorrentes: distância demais, expressão fraca, cenário demais e tesão de menos.
- Em `Amor`, não ter vergonha de flertar com capa de desejo, fanfic, novela, fofoca e fantasia relacional, desde que a obra ainda se reconheça ali.
- Em revisões de capa, quando o problema for `boa demais` no sentido polido, tímido ou respeitável, considerar ruptura brutal em vez de refinamento: psicodelia, melodrama, foto-realismo kitsch, iconografia religiosa óbvia, erotização comercial, expressionismo agressivo ou outra linguagem que devolva pulso à miniatura.
- Se uma fileira inteira estiver civilizada demais, escolher deliberadamente um ou dois títulos para virarem outliers comerciais e puxarem o grid para cima.
- O prompt de capa também deve preferir arquivo UTF-8 com `--prompt-file` quando ficar longo ou detalhado.
- Para cadastro em Windows, preferir sinopse via arquivo UTF-8 com `--synopsis-file`; passar texto longo com acentos direto na CLI tende a virar bagunça.
- Se estiver em PowerShell interativo e for chamar a API várias vezes, dot-source `sharebook_prod_login.ps1` para renovar o token e salvá-lo no `.env`, além de reaproveitá-lo na sessão atual.
- O cache permitido do token do Sharebook é o `.env` do projeto. Não registrar o valor em memória operacional, logs, skills ou documentação.
- [`source-queue.md`](source-queue.md) é a fonte da verdade da fila; a memória da automação vira apoio resumido, não inventário principal.
- Não criar memória episódica em `codex-sessions/` ao fim de cada rodada automática; para esse fluxo, a memória durável relevante é a da automação.
- Não validar a capa com `HEAD` público depois do cadastro; esse passo já se mostrou estável e virou fricção desnecessária.
- Fazer self improvement deliberado: se a execução mostrou um atrito real, registrar a dor e endurecer a skill antes da próxima rodada.
- A memória da automação deve registrar, junto do livro publicado, a família visual e a macrofamília usadas na capa. Sem isso, a regra anti-repetição vira teatro.

## Scripts úteis

- `C:\REPOS\SHAREBOOK\codex-scripts\sharebook_source_extract.py`
  - Extrair título, autor, sinopse e PDF da página.
- `C:\REPOS\SHAREBOOK\codex-scripts\sharebook_openai_cover.py`
  - Gerar capa autoral via OpenAI Images API. Aceita `--prompt` ou `--prompt-file`.
- `C:\REPOS\SHAREBOOK\codex-scripts\sharebook_prod_book.py`
  - Buscar, deletar, cadastrar e aprovar livro em produção. Aceita `--synopsis` ou `--synopsis-file`.
  - Também atualiza livro existente com `update --id`, preservando campos não informados e permitindo trocar capa, PDF, sinopse ou categoria sem recriar o registro.
  - Use `find-many --pairs-file` quando estiver comparando vários candidatos em lote.
  - Tenta `SHAREBOOK_PROD_ACCESS_TOKEN` da sessão atual primeiro, depois do `.env`; se tomar `401/403`, reautentica uma vez e atualiza o `.env`.
  - Se a API bloquear o login por 30 segundos, o script agora espera e tenta de novo automaticamente.
- `C:\REPOS\SHAREBOOK\codex-scripts\sharebook_prod_login.ps1`
  - Renova `SHAREBOOK_PROD_ACCESS_TOKEN`, salva no `.env` e carrega na sessão atual do PowerShell.

## Execução sugerida

```powershell
python C:\REPOS\SHAREBOOK\codex-scripts\sharebook_source_extract.py `
  https://livrosdominiopublico.com.br/a-desobediencia-civil/ `
  --out-dir C:\REPOS\SHAREBOOK\codex-temp\a-desobediencia-civil
```

```powershell
python C:\REPOS\SHAREBOOK\codex-scripts\sharebook_openai_cover.py `
  --prompt-file C:\REPOS\SHAREBOOK\codex-temp\a-desobediencia-civil\cover-prompt.txt `
  --output C:\REPOS\SHAREBOOK\codex-temp\a-desobediencia-civil\cover.png
```

```powershell
python C:\REPOS\SHAREBOOK\codex-scripts\sharebook_prod_book.py create `
  --title "A Desobediência Civil" `
  --author "Henry David Thoreau" `
  --category-name "Política" `
  --synopsis-file C:\REPOS\SHAREBOOK\codex-temp\a-desobediencia-civil\synopsis.txt `
  --image-path C:\REPOS\SHAREBOOK\codex-temp\a-desobediencia-civil\cover.jpg `
  --pdf-path C:\REPOS\SHAREBOOK\codex-temp\a-desobediencia-civil\source.pdf `
  --delete-existing `
  --approve
```

## Referências

- Ler [workflow.md](references/workflow.md) para armadilhas de produção.
- Ler [prompts.md](references/prompts.md) quando a capa precisar de um prompt melhor.
- Ler [synopsis-template.md](references/synopsis-template.md) para manter a sinopse sexy, longa e usável.


## Futuras fontes de livros digitais.

- Hoje nossa fonte oficial é `livrosdominiopublico.com.br`
- Mas essa fonte vai esgotar rápido porque tem poucos livros.
- Apenas 63 livros: https://livrosdominiopublico.com.br/sitemap/
- Possivelmente vamos precisar criar uma skill pra cada uma das fontes abaixo.

| Site | Link | Descrição |
|------|------|----------|
| Portal Domínio Público | http://www.dominiopublico.gov.br | Maior acervo brasileiro de obras em domínio público (literatura, áudio, vídeo), mantido pelo MEC |
| Biblioteca Nacional Digital | https://bndigital.bn.gov.br | Acervo digital da Biblioteca Nacional com livros raros, históricos e domínio público |
| Brasiliana Guita e José Mindlin (USP) | https://www.bbm.usp.br | Coleção digital da USP com obras importantes sobre a história e cultura do Brasil |
| Open Library | https://openlibrary.org | Biblioteca digital global com milhões de livros, incluindo domínio público e empréstimo digital |
| Project Gutenberg | https://www.gutenberg.org | Um dos maiores acervos de livros gratuitos do mundo, focado em obras em domínio público |
