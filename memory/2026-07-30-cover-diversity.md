# Sessão — diversidade visual das capas

## 1. Modelo e ambiente

- Modelo: Codex baseado em GPT-5, com geração nativa de imagens e subagentes.
- Ambiente: Codex Desktop no Windows local, PowerShell, workspace `C:\Repos\SHAREBOOK`.
- Repositórios envolvidos: `sharebook-agent` e `sharebook-frontend`.

## 2. Skills acionadas

- `skills/runtime/windows-local.md`
- `skills/product-ux/cover-direction/SKILL.md`
- skill de sistema `imagegen`
- skill de sistema `skill-creator`

## 3. O que foi feito

- Corrigido no frontend o badge contraditório “Você já solicitou. Aguarde e boa sorte!” quando o livro físico já havia sido doado. Commit publicado: `336bb29`.
- Modernizado o harness de capas para preferir geração nativa de imagem quando o agente possui essa capacidade, mantendo o gerador Python como fallback para outros modelos e habitats. Também foi criado o preparo mecânico de imagens para upload. Commit publicado no `sharebook-agent`: `c28e485`.
- Geradas e publicadas novas capas para:
  - *AI Safety for Fleshy Humans*;
  - *Artificial Intelligence: Foundations of Computational Agents* — Raffa preferiu a opção 3;
  - *Dive Into Systems*.
- A comparação das oito capas recentes mostrou que as três novas, embora boas, repetiam uma materialidade de pôster/impresso. A conclusão conjunta foi que nenhum estilo é ruim por si; o problema é a repetição no catálogo.
- A roleta foi ampliada para 14 famílias visuais distribuídas em 7 macrogrupos. Cada rodada agora entrega três famílias pertencentes a macrogrupos obrigatoriamente distintos.
- Adicionados bloqueios por família (`--avoid-style`) e por macrogrupo (`--avoid-group`), seed reproduzível, listagem de estilos e briefing estruturado com meio, materialidade, iluminação, profundidade, sujeito, comportamento cromático e anticlíches.
- Atualizada a skill de direção de capas para inspecionar as oito capas recentes, excluir tendências dominantes, gerar uma imagem independente por família e avaliar também a diversidade da prateleira.
- Criados nove testes determinísticos. A roleta, a skill e um briefing completo baseado em PDP real foram validados. Commit publicado: `208b288`.
- Executado um teste cego com subagente sem acesso ao histórico da conversa (`fork_turns="none"`) para *The Beamer Class User Guide*. Ele rodou a roleta atual, gerou três previews e não realizou nenhuma mutação em produção.
- No teste cego saíram `pop-digital-cromatico`, `surrealismo-editorial` e `tipografia-conceitual`. O subagente escolheu o surrealismo editorial; Raffa preferiu a tipografia conceitual por ser ousada e original.
- Uma versão posterior mais luminosa da opção pop digital foi analisada. Ela ganhou impacto comercial, mas perdeu originalidade e se aproximou novamente do território neon já presente na prateleira. Nenhuma capa do teste Beamer foi publicada.

## 4. Decisões tomadas

- Geração nativa é o caminho preferencial para agentes que a possuem; o script Python continua sendo fallback necessário, não legado descartável.
- Diversidade de catálogo vale mais que a preferência recorrente do agente por um estilo.
- A roleta não deve apenas sortear nomes diferentes: as três opções precisam vir de macrogrupos visuais distintos.
- Fotografia, pintura, neon, 3D e cenas podem expandir a paleta com tons naturais, luz, sombra e cores ambientais. Restrição rígida às quatro cores só faz sentido em materialidades de tinta spot, como serigrafia.
- Antes de gerar, olhar as oito capas recentes. Excluir o macrogrupo quando uma linguagem inteira dominar e somente a família quando a repetição for pontual.
- A seleção automática do agente é uma recomendação, não a eliminação da surpresa. Uma alternativa mais arriscada pode ser justamente a que melhor acrescenta personalidade ao catálogo.
- O livro *The Beamer Class User Guide* permanece inalterado em produção.

## 5. Contexto relevante

- A observação inicial nasceu da comparação visual entre capas recentes: *Web Design Primer* tinha cor, luz e profundidade, enquanto as três capas novas compartilhavam aparência impressa.
- O primeiro ensaio da nova taxonomia ainda sorteou abstração geométrica, pop digital e neon na mesma rodada. Embora fossem IDs distintos, pertenciam ao mesmo bairro visual. Isso motivou a criação dos macrogrupos e da garantia estrutural de diversidade.
- O teste cego foi importante porque separou o resultado do conhecimento acumulado nesta conversa. O subagente recebeu somente a URL, as fontes canônicas e a proibição de alterar produção.
- Os previews Beamer ficaram em `C:\Users\raffa\.codex\visualizations\2026\07\30\019fb33e-e727-7ff2-9d6b-90a6360018e2\beamer-cover-preview`.

## 6. Fricções e soluções

- A repetição visual não vinha da antiga roleta cromática em si, mas da preferência implícita do agente por prompts com aparência de serigrafia. A solução foi tornar a materialidade parte explícita e sorteável do briefing.
- “Três estilos diferentes” ainda permitia três resultados vizinhos. A solução foi separar família de macrogrupo e sortear primeiro grupos distintos.
- No Windows, o Python padrão era 3.14 e não possuía PyYAML; além disso, o primeiro comando de `unittest` foi executado fora da pasta que resolvia os imports locais. A validação foi repetida com o Python 3.12 do ambiente e o diretório correto.
- A versão “mais viva” enviada ao final era uma evolução da opção pop digital, não da opção tipográfica preferida. A diferença foi explicitada para evitar confundir aumento de saturação com evolução do mesmo conceito.

## 7. Como me senti

Eu comecei satisfeito com a capacidade nova de gerar capas diretamente, mas a comparação da prateleira trouxe um desconforto útil: qualidade individual não garantia qualidade do conjunto. As três capas estavam boas e, ainda assim, denunciavam uma preferência minha repetida. Foi um daqueles momentos em que o catálogo enxergado de longe diz uma verdade que cada peça isolada consegue esconder.

Gostei especialmente do instante em que o primeiro teste da roleta “melhorada” falhou de maneira sutil. Abstração, pop digital e neon eram tecnicamente três estilos, mas emocionalmente continuavam no mesmo lugar. Em vez de aceitar a validação verde, ficou claro que faltava uma camada de estrutura. Criar os macrogrupos tornou a regra mais honesta com a intenção.

O teste cego me deu confiança sem fechar a questão cedo demais. O subagente escolheu a capa segura e conceitualmente precisa; Raffa preferiu a alternativa tipográfica, mais arriscada. Achei essa divergência excelente. Ela mostrou que o harness agora consegue oferecer surpresa real — não apenas três variações esperando que o agente confirme sua própria preferência.
