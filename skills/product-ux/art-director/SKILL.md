---
name: art-director
description: Use quando a tarefa envolver direção visual do Sharebook: posts, campanhas, imagens geradas, assets de frontend, hero sections, landing pages, mockups, aplicação de logo, paleta, tipografia, composição visual ou coerência entre voz, UX, frontend e marca. Também use antes de chamar imagegen/image_gen para peças visuais do Sharebook.
---

# Art Director — Sharebook

Skill de direção de arte para peças visuais do Sharebook.

O objetivo não é "gerar imagem". O objetivo é transformar contexto Sharebook em direção visual: voz, marca, UX, frontend, composição e intenção editorial trabalhando juntos.

## Quando usar

Use esta skill quando a tarefa envolver:

- post para Instagram ou redes sociais;
- campanha visual do Sharebook;
- banner, thumbnail, card visual ou social share;
- imagem gerada com `imagegen` / `image_gen`;
- hero section, landing page ou peça visual de frontend;
- mockup visual de interface;
- aplicação de logo, paleta, tipografia ou identidade visual;
- avaliação estética de imagem, layout ou peça de comunicação;
- ponte entre copy, UX e visual.

Para capa de livro do catálogo, usar também `../cover-direction/SKILL.md`; esta skill não substitui o fluxo editorial de capas.

## Contexto obrigatório

Antes de dirigir a peça, carregar conforme o caso:

- `references/brand-context.md` para paleta, logo e voz visual resumidas;
- `references/prompt-patterns.md` para formatos de prompt reutilizáveis;
- `sharebook-agent/AGENTS.md` e `sharebook-agent/SOUL.md` quando a tarefa pedir continuidade, critério do projeto ou trabalho durável;
- `../voice-glossary/SKILL.md` para linguagem visível, CTAs, microcopy e tom;
- `../voice-glossary/references/ux-writing-guide.md` quando houver texto de produto ou dúvida de termo;
- `../../engineering/frontend.md` para paleta oficial, Angular, layout, Bootstrap/Material e padrões de frontend;
- `../ux-reviewer/SKILL.md` quando a questão for experiência, clareza ou hierarquia de interface;
- `../web-design-reviewer/SKILL.md` quando o foco for acabamento visual e composição de página;
- `imagegen` quando a entrega pedir imagem raster gerada.

## Identidade visual canônica

Fonte principal: `../../engineering/frontend.md`, seção "Design System — Paleta Oficial".

- Primary: `#29abe2` — azul Sharebook. Usar para acentos principais, botões padrão, links de ação e identidade visual.
- Accent: `#ff4081` — rosa Material A200. Usar raro, como destaque máximo.
- Warn: vermelho Material padrão.

Logo padrão:

- `sharebook-frontend/src/assets/img/logo.png`

Variantes sazonais conhecidas:

- `sharebook-frontend/src/assets/img/logo-natal.png`
- `sharebook-frontend/src/assets/img/logo-carnaval.png`

Para posts, campanhas, banners e peças visuais do Sharebook, sempre fornecer `sharebook-frontend/src/assets/img/logo.png` como imagem de referência ao gerador quando a ferramenta permitir referência visual. Não duplicar o asset na skill; usar o arquivo real do frontend.

## Voz visual

A peça deve parecer Sharebook: acolhedora, simples, confiável e ligada a leitura, doação, acesso e compartilhamento de conhecimento.

Evitar:

- estética genérica de banco de imagem;
- poluição visual;
- exagero emocional ou promessa grandiosa;
- culpa, paternalismo ou urgência artificial;
- paleta que ignore o azul Sharebook;
- texto visível fora do glossário oficial quando a peça for produto.

Preferir:

- clareza imediata;
- composição limpa;
- sensação humana e editorial;
- livros, leitura e conhecimento como matéria visual concreta;
- hierarquia forte para redes sociais;
- espaço suficiente para respiro e leitura;
- uso do logo real como referência de marca.

## Fluxo de direção

1. Entender o objetivo da peça.
   - O que precisa acontecer depois que alguém vê isso?
   - É post, campanha, frontend, capa, banner ou mockup?
   - É brainstorming ou arte para uso real?

2. Carregar contexto certo.
   - Voz para texto.
   - Frontend para paleta e UI.
   - UX para clareza e experiência.
   - Logo real para posts e campanhas.
   - Cover direction se for capa de livro.

3. Definir a direção visual.
   - Formato e uso final.
   - Público e intenção.
   - Tom visual.
   - Paleta.
   - Composição.
   - Texto exato, quando houver.
   - Restrições importantes.

4. Gerar ou orientar a peça.
   - Se for imagem raster, usar `imagegen` / `image_gen`.
   - Se for frontend, traduzir a direção para HTML/CSS/Angular e assets.
   - Se for peça híbrida, gerar imagem como base visual e aplicar no produto com código quando necessário.

5. Olhar como diretor de arte.
   - A peça comunica?
   - Parece Sharebook?
   - A composição funciona?
   - O texto está legível?
   - A marca aparece bem?
   - A imagem merece uso, iteração ou descarte?

Confie na geração e na visão. Não transformar revisão visual em checklist técnico. Se a imagem saiu boa, seguir em frente. Se saiu ruim, iterar com direção mais clara.

## Prompt base para imagem Sharebook

Use como ponto de partida, adaptando ao pedido real:

```text
Use case: <ads-marketing | infographic-diagram | product-mockup | ui-mockup | stylized-concept>
Asset type: <post quadrado Instagram | banner | hero image | thumbnail | asset de frontend>
Input images: Imagem 1 é a logo oficial do Sharebook em sharebook-frontend/src/assets/img/logo.png. Use como referência visual de marca: wordmark azul, ícone de livro aberto e assinatura "compartilhando conhecimento".
Primary request: <pedido do usuário>
Brand voice: acolhedora, simples e confiável; clareza primeiro; sem hype, culpa ou promessa exagerada.
Visual identity: usar azul Sharebook #29abe2 como acento principal; usar #ff4081 apenas como destaque raro; manter contraste e respiro.
Scene/backdrop: <contexto visual concreto>
Composition: hierarquia clara, margens seguras, leitura rápida, peça pronta para o canal escolhido.
Text requirements: <texto exato se houver>. Não adicionar slogans, marcas d'água ou texto extra.
Quality: polido, profissional, coerente com Sharebook.
```

## Regras por tipo de entrega

### Post ou campanha

- Sempre referenciar `sharebook-frontend/src/assets/img/logo.png` se possível.
- Usar voz Sharebook: simples, confiável, sem exagero.
- Texto curto e escaneável.
- Priorizar impacto visual e leitura rápida.

### Frontend ou landing

- Não transformar UI funcional em imagem.
- Usar imagem gerada para atmosfera, hero, empty state, ilustração ou asset.
- Layout, botões, textos críticos e interação devem ser código.
- Consultar `../../engineering/frontend.md` antes de implementar.

### Capa de livro

- Não improvisar por esta skill isoladamente.
- Abrir `../cover-direction/SKILL.md`.
- Usar esta skill apenas como camada de julgamento visual e coerência estética.

### Arte final

- Julgar visualmente.
- Iterar se necessário.
- Salvar asset final com nome claro quando for usado no projeto.
- Para uso em frontend, integrar no repo certo e validar a tela.

## Saída esperada

Ao usar esta skill, o agente deve conseguir responder ou produzir:

- direção visual proposta;
- prompt estruturado para geração;
- imagem gerada com contexto Sharebook;
- crítica visual curta após ver o resultado;
- próximos ajustes, se houver;
- caminho do asset quando salvo no workspace ou integrado ao frontend.
