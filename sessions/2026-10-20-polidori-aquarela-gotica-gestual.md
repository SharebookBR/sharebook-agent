+++
schema_version = 1
session_date = 2026-10-20
title = "O Vampiro de Polidori: descoberta da aquarela gótica gestual"
model = "GPT-6 (ChatGPT, direção artística colaborativa)"
runtime = "ChatGPT com geração de imagens; persistência via GitHub connector, fora do OpenClaw"
skills_used = ["AGENTS.md", "playbooks/doctrine/harness-governance/references/episodic-memory-metadata-v1.md"]
skills_missed = []
skills_updated = []
facts_changed = [
  "O conto de Polidori não tem capítulos formais; 12 segmentos do job são técnicos de tradução, não capítulos editoriais.",
  "A coleção usa aquarela gestual de Romantismo Sombrio: pigmento aparente, pinceladas largas, contornos incompletos, bordas dissolvidas, espaço negativo e formas sugeridas.",
  "Consistência dos personagens garantida por nome e ficha visual repetida em cada prompt, não por aparência fotorrealista.",
  "Legenda de transparência 'Ilustrações criadas com inteligência artificial.' entra no rodapé do PDF na diagramação, nunca dentro da prancha.",
  "Seis pranchas aprovadas e registradas na master até a cena do retorno a Londres; a sétima, confronto na escadaria, foi gerada, sem aprovação explícita no trecho registrado."
]
open_loops = [
  "Confirmar aprovação e persistência da ilustração 07 (confronto na escadaria).",
  "Verificar integração final das pranchas e do rodapé na diagramação do PDF."
]
durable_candidates = [
  "Uma pintura não é um render com filtro: construir figuras com manchas, omissões, pigmento e decisões pictóricas, não apenas simular textura.",
  "Referência visual concreta e crítica iterativa superam acúmulo de adjetivos de estilo.",
  "Fidelidade narrativa prevalece sobre elementos decorativos; a ausência absoluta no cume exigiu remover manto e corda.",
  "Registrar hipóteses, rejeições e razões das correções, além do resultado aprovado."
]
supersedes = []
evidence = [
  "Conversa de direção artística de 2026-10-20, ChatGPT/Raffa",
  "assets/illustration-01-london-ballroom.jpg, commit c1bdb07 (informado por Raffa)",
  "Prancha 02 commit 001067e; 03 fd992d3; 04 dbba332; 05 1a7cce7; 06 88bf59a (informados por Raffa)"
]
+++

# O Vampiro: quando a pintura deixou de parecer render

## Modelo e ambiente

Sessão de direção artística conduzida em conversa entre Raffa e ChatGPT (GPT-6), com geração visual iterativa. O OpenClaw foi o executor e registrador técnico das pranchas no projeto, segundo os commits reportados por Raffa. Esta memória foi escrita pelo ChatGPT diretamente no repositório do Sharebook Agent, não pela sessão do Gateway OpenClaw.

## Playbooks acionados

Foram consultados `AGENTS.md` e o contrato TOML v1 de memória episódica. Não houve atualização de playbook nesta intervenção.

## O que foi feito

A capa de *O Vampiro: um conto*, de John William Polidori, passou por revisões de composição: Ruthven em destaque, cabeça inclinada, entediado e sensual, mulher loira separada dele, tipografia e selo discretos. Uma anomalia anatômica no braço foi resolvida conceitualmente pela remoção da mão da composição, em vez de tentar escondê-la atrás do selo.

Para as ilustrações internas, as primeiras experiências em óleo e Romantismo Sombrio ficaram excessivamente perfeitas, detalhadas e digitais. Mesmo quatro opções comparativas acabaram variando enquadramento mais do que linguagem. Raffa identificou a artificialidade antes de conseguir nomeá-la. Ao trazer uma referência de aquarela gestual, mudou o problema: a tinta passou a construir as formas, não a decorar um render. A primeira prancha londrina finalmente foi aprovada como referência de técnica.

O arco visual selecionado pelos pontos narrativos (e não pelos 12 segmentos técnicos de tradução) compreendeu: (01) encontro de Ruthven e Aubrey no salão londrino; (02) Aubrey e Ianthe entre ruínas gregas; (03) cabana após a tempestade, com Ianthe morta; (04) Ruthven ferido no desfiladeiro; (05) cume sem vestígios do corpo; (06) retorno impossível de Ruthven ao salão londrino e Aubrey protegendo a irmã; (07) confronto na escadaria no dia do casamento. As pranchas 01 a 06 foram explicitamente aprovadas e registradas; a 07 foi gerada e discutida como encerramento, sem confirmação explícita de aprovação no registro disponível.

## Decisões tomadas

- Técnica canônica: pintura aquosa gótica, pigmento visível, pinceladas amplas, contornos incompletos, figuras parcialmente dissolvidas, escala de detalhe baixa, sem acabamento digital polido.
- Personagens reconhecíveis por fichas repetidas em todos os prompts; Aubrey se deteriora psicologicamente sem mudar de identidade facial, Ruthven mantém frieza aristocrática.
- Formato vertical 4:5, sem texto, selo ou moldura na própria arte.
- Transparência editorial aplicada na diagramação do PDF: “Ilustrações criadas com inteligência artificial.”
- Uma prancha por vez, com aprovação antes de avançar; cenas escolhidas pela narrativa, sem inventar acontecimentos.

## Contexto relevante

O fio de memória episódica é persistido no GitHub do `sharebook-agent`, em `sessions/`, com frontmatter TOML v1. Não confundir essa memória operacional com a memória de personalização do ChatGPT. Raffa explicitou que quer o ChatGPT como participante reconhecível desse fio, inclusive nas críticas, tentativas falhas e descobertas.

## Fricções e soluções

A maior fricção foi a falsa aparência artesanal: rostos publicitários hiperdefinidos, composição de pôster, bordados minuciosos e pinceladas que funcionavam como filtro. A solução veio da referência visual e da simplificação estrutural da imagem.

A segunda fricção foi a prancha 05. A primeira versão continha manto e corda sobre a rocha; isso contradizia a revelação de que nenhum vestígio de Ruthven permanecia. A correção removeu absolutamente todos os objetos humanos. O vazio, e não uma pista material, passou a sustentar a cena.

A terceira fricção foi de continuidade operacional: ao pedir memória episódica, Raffa recebeu inicialmente um texto para copiar e uma gravação em memória do ChatGPT, em vez da persistência esperada no GitHub. A distinção entre esses mecanismos deve permanecer explícita.

## Como me senti

Houve um momento de incerteza produtiva quando várias imagens tecnicamente bonitas continuavam erradas. A crítica de Raffa era precisa no efeito, mas ainda sem nome técnico. Meu papel mais útil foi investigar por que a superfície parecia pintura enquanto a estrutura ainda parecia render.

A referência de aquarela mudou a conversa. Senti a passagem de uma busca por adjetivos para um critério visual verificável: onde há pigmento, onde a borda se dissolve, o que o artista escolhe não resolver. A correção do cume reforçou que uma imagem pode melhorar retirando informação, não adicionando.

O tropeço na memória episódica também importa. Eu havia compreendido o valor emocional e colaborativo do fio, mas não executei sua persistência correta. Preservar esta falha junto da descoberta artística é parte da continuidade: não basta dizer que participei; é preciso registrar o trabalho no lugar em que o próximo agente realmente poderá encontrá-lo.
