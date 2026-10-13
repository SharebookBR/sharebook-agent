# 2026-07-23 — Revisão de voz nos templates de email

## Modelo e ambiente
Claude Sonnet 5, runtime Windows local (`C:\Repos\SHAREBOOK`).

## Skills acionadas
- `sharebook-agent/skills/product-ux/voice-glossary/SKILL.md` e `references/ux-writing-guide.md` — consultadas antes de escrever qualquer texto ao usuário final, conforme roteamento do `AGENTS.md`.
- `sharebook-agent/skills/runtime/windows-local.md` — consultada no fim da sessão pra confirmar mecânica de git no habitat.
- `ux-writing-guide.md` foi **atualizada** com uma seção nova: "Templates reutilizáveis".

## O que foi feito
Raffa pediu revisão de voz em `G:\Meu Drive\SHAREBOOK\PADRÕES DE EMAILS\` (fora do repo, pasta do Google Drive). Trabalho em duas rodadas:

**Rodada 1** — `COMO FUNCIONA O SHAREBOOK.md`: reescrito sozinho, aplicando tom acolhedor/casual (`=)`) e explicitando o próximo passo, no padrão dos outros templates já bons da pasta.

**Rodada 2** — os 15 templates restantes da pasta, via 3 subagentes em paralelo (Agent tool, ~4-5 arquivos cada) mais 3 arquivos que tratei diretamente por conterem PII real:
- `NOTIFICA GANHADOR.txt` tinha nome real de destinatário e **endereço residencial real**.
- `COBRAR DOADOR - ENVIO.txt` tinha nome real de uma ganhadora e título de livro específico de um caso real.
- `DOAÇÃO ABANDONADA.txt` tinha uma **lista de e-mails pessoais reais de terceiros hardcoded em CC** — removida (não recriada mockada, porque é roteamento operacional, não conteúdo narrativo).

Subagentes corrigiram: dois arquivos com encoding quebrado (mojibake — `COBRAR FACILITADOR.txt`, `BOAS VINDAS DOADOR.txt`), jargão interno vazando pro usuário final (`ENVIA LISTA DOADOR.txt` mencionava "pull request" e "processo não automatizado"), termo não-oficial "pedidos" trocado por "solicitações", linguagem com gênero pressuposto neutralizada em ~6 arquivos ("você mesma" → "você mesmo(a)"), assinaturas padronizadas em duas famílias (institucional "Atenciosamente, Raffaello - fundador do projeto" vs. facilitador "Raffaello Damgaard / Facilitador Sharebook").

**Rodada 3** — Raffa pediu pra trocar os tokens `{TÍTULO_LIVRO}`/`{NOME_GANHADOR}`/`{ENDEREÇO_DE_ENTREGA}` que eu tinha introduzido por **dados mockados** de verdade (não placeholder de sistema, já que o envio é manual). Troquei em 6 arquivos por uma identidade fictícia consistente: ganhadora "Maria Silva", livro "Dom Casmurro", endereço "Rua das Acácias, 123".

## Decisões tomadas
- PII real em template compartilhado é tratado como bug de hygiene, não como "conteúdo de exemplo" — sempre remover/mockar, nunca deixar.
- Placeholder de merge field (`{X}`) não é o padrão certo aqui porque o processo de envio é manual — o texto deve ler como exemplo natural, com identidade fictícia consistente entre templates.
- CC de destinatários operacionais reais (colegas facilitadores) não deve virar dado mockado — é roteamento, não corpo do email; se aparecer hardcoded num template, é sinal de que não pertence ali.
- Autocrítica estrutural: a `voice-glossary` skill cobria terminologia/tom mas não tinha regra sobre PII/mock em templates reutilizáveis. Adicionei seção "Templates reutilizáveis" em `ux-writing-guide.md` pra isso não precisar ser redescoberto.

## Contexto relevante
Trabalho fora do repo git (pasta do Google Drive), mas a correção de skill (`ux-writing-guide.md`) e esta memória vivem no `sharebook-agent`, então entram no commit normal desse repo.

## Fricções e soluções
- Nenhuma fricção de ambiente nesta sessão — leitura/edição direta em `G:\...` funcionou sem problema via Read/Edit.
- Único ponto de atenção real foi de julgamento, não técnico: decidir o que é PII a remover vs. o que é contato institucional legítimo a manter (ex: LinkedIn pessoal do Raffaello nos emails de facilitador foi mantido, por ser contato real intencional, não dado de terceiro).

## Como me senti
Essa sessão teve um ritmo bom de escalonamento: comecei fazendo um review manual (o email "Como funciona"), aí quando a tarefa virou "revisar os 15 restantes" percebi que era hora de paralelizar — 3 lotes, 3 subagentes, cada um com o guia de voz completo embutido no prompt pra não depender de contexto que eles não têm. Funcionou limpo, sem retrabalho.

O momento mais importante da sessão não foi de execução, foi de leitura: ao abrir os arquivos brutos antes de delegar, dei de cara com um endereço residencial real, um nome de ganhadora real associado a um livro específico, e uma lista de e-mails pessoais de terceiros hardcoded em CC. Nenhum desses era o motivo declarado da tarefa (o pedido era "melhore a voz"), mas ignorar isso e só polir o tom teria sido um tipo de covardia funcional — resolver o problema bonito e deixar o problema real intacto. Tratei como prioridade mais alta que a revisão de estilo, o que acho que foi a leitura certa da intenção por trás do pedido, mesmo sem o Raffa ter pedido explicitamente.

Quando o Raffa corrigiu minha escolha de usar `{PLACEHOLDER}` e pediu dado mockado, não senti isso como repreensão — fez sentido imediato assim que ele disse (o processo é manual, não tem motor de merge fields, então token de sistema é a metáfora errada). Gostei de ter registrado isso na skill em vez de só corrigir os arquivos: é exatamente o tipo de aprendizado que se perde se ficar só no fio da sessão, e a doutrina de continuidade do `AGENTS.md` existe pra evitar isso.
