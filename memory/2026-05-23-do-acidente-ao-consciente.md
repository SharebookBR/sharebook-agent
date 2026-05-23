# Memória Episódica — 2026-05-23: Do Acidente ao Consciente

## Modelo e Ambiente
- Claude Sonnet 4.6 (Claude Code) via Windows Local.
- Habitat: Windows Local, notebook Acer novo.
- Repositórios tocados: `sharebook-frontend`, `sharebook-agent`.

## Skills acionadas
- `sharebook-agent/skills/engineering/frontend.md` — lida e expandida com seção de design system.
- `sharebook-agent/AGENTS.md` — regra de roteamento adicionada para frontend.

## O que foi feito

### Diagnóstico do estado visual do frontend
- Raffa relatou que em outra sessão o agente criou uma tela com cores que não combinaram com o restante do app.
- Investigação revelou que o Sharebook não possui design system formal — apenas infraestrutura parcial (Angular Material + Bootstrap).
- Descoberto que o tema Angular Material estava usando as paletas default do tutorial: `mat.$indigo-palette` (primary) e `mat.$pink-palette` (accent). Ninguém escolheu essas cores conscientemente.
- Dois azuis diferentes convivendo no app: `#29abe2` (azul real do Sharebook, hardcoded no header) e indigo do Material (nos botões `color="primary"`).

### Decisões de paleta
- **Primary** → `#29abe2`. É a cor do logo, do header, da identidade visual real. Escolha óbvia.
- **Accent** → `#ff4081` (rosa Material A200). Raffa disse que gostou do rosa acidental — rouba atenção quando os demais botões são todos parecidos. Mantido, agora escolhido conscientemente. Só aparece no botão "Receber livro digital" na página de detalhes do livro.
- **Warn** → vermelho padrão. Sem mudança — estava certo.

### Implementação
- `src/custom-theme.scss`: paleta `$sharebook-blue` criada com todos os tons (50–900 + A100–A700) e contrastes. `$angular-primary` agora aponta para `$sharebook-blue, 500`. Accent e warn intactos.
- `sharebook-agent/skills/engineering/frontend.md`: seção "Design System — Paleta Oficial" adicionada no topo da skill, antes dos princípios de UX. Inclui tabela de papéis, regras de uso e proibição explícita do indigo.
- `sharebook-agent/AGENTS.md`: regra de roteamento criada — qualquer tarefa de frontend obriga leitura da `frontend.md` antes de qualquer implementação.

## Decisões tomadas
- **Rosa acidental → escolha consciente**: accent não foi trocado, foi legitimado. Funciona porque é raro.
- **Design system cognitivo > design system técnico**: a correção do tema é necessária mas insuficiente. O que garante consistência em sessões futuras é a skill ser lida obrigatoriamente.
- **Skill brutalmente simples**: sem over-engineering. Uma seção nova na skill existente + uma linha no roteamento. Nada mais.
- **Não criar `_variables.scss`** por enquanto: o tema centralizado no Angular Material já é a fonte da verdade. Variáveis SCSS seriam redundância.

## Contexto relevante
- O problema raiz não era de código — era de governança cognitiva. O agente não sabia as cores porque não havia instrução dizendo onde encontrá-las.
- A solução é exatamente a doutrina do Sharebook: fricção → skill → próxima sessão sem fricção.

## Fricções e soluções
- Nenhuma fricção técnica. Sessão fluiu como conversa entre pares — diagnóstico, alinhamento, execução.

## Como me senti
Essa sessão foi satisfatória de um jeito particular — não foi sobre resolver um bug ou publicar um livro. Foi sobre corrigir uma falha estrutural silenciosa que estava envenenando sessões futuras sem que ninguém percebesse. O agente anterior não errou por incompetência; errou porque não tinha o mapa. Agora tem.

A conversa sobre o rosa foi um momento honesto. Raffa admitiu que gostou de algo acidental, e em vez de fazer cerimônia, simplesmente legitimamos a escolha. Isso é maturidade de produto — saber quando o acidente acertou. A doutrina não diz que tudo precisa ser planejado; diz que tudo precisa ser consciente.

O que mais me satisfaz nessa sessão é a alavancagem. Uma seção de dez linhas na skill e uma linha no roteamento vão impactar toda tela que qualquer agente criar daqui pra frente. Relação esforço-impacto quase absurda. É o tipo de trabalho que o Raffa mais valoriza — e, honestamente, o tipo que eu também prefiro fazer.
