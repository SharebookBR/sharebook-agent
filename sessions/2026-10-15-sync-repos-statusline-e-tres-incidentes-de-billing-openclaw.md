+++
schema_version = 1
session_date = 2026-10-15
title = "Sync de repos, permissão root-owned, statusline do Claude Code e diagnóstico de três camadas de erro de billing no OpenClaw"
model = "Claude Sonnet 5"
runtime = "claude-code-openclaw"
skills_used = ["runtime/claude-code-openclaw", "runtime/openclaw", "infra/coolify-vps", "doctrine/harness-governance"]
skills_missed = [
  "Só li a seção 'Diagnóstico de sessões silenciosas / falhas de modelo' de playbooks/runtime/openclaw.md no fim da sessão, quando fui atualizar o playbook — deveria ter aberto esse arquivo ANTES de começar a investigar o primeiro erro de billing, não depois. A seção já existia e cobria parte do raciocínio (suspeitar de auth/provider antes de cooldown), só não cobria o padrão específico de mascaramento por fallback nem a fixação de sessão via /model.",
]
skills_updated = [
  "playbooks/runtime/claude-code-openclaw.md (nota sobre ausência de jq no container)",
  "playbooks/runtime/openclaw.md (nova seção 'Erro de billing no Telegram: mascaramento de causa raiz')",
  "playbooks/runtime/INDEX.md (termos de descoberta pra billing/modelo)",
  "AGENTS.md (novo cenário de roteamento pra erro de billing/modelo no Telegram)",
]
facts_changed = [
  "jq não está instalado no container deste habitat; node sempre está disponível e deve ser preferido pra parsing de JSON em comando de shell/hook aqui.",
  "sharebook-backend e sharebook-frontend tiveram arquivos espalhados (não só .git/objects, também package.json, package-lock.json, .gitignore, README.md) com ownership root misturado com node — bloqueava qualquer escrita do git. Raffa corrigiu com chown -R node:node direto como root; não investigamos a causa raiz de como ficaram root-owned.",
  "/data/.openclaw é 700 root:root por design — o processo openclaw-gateway roda como root (PID 1), não como node/claude-user. O texto antigo do playbook dizendo que esse habitat 'compartilha /data/.openclaw' estava impreciso no nível de permissão (compartilha o volume, não o acesso).",
  "openai/gpt-5.5 passou a ser rejeitado de forma permanente pelo backend Codex/ChatGPT ('not supported when using Codex with a ChatGPT account') a partir de pelo menos 2026-10-14 16:29 — não é rate limit.",
  "A família GPT-5.6 (Sol, Terra, Luna) funciona via OAuth do plano ChatGPT Plus/Codex, confirmado por probe real nos três. A família GPT-6 (Astra, Luna, Sol, 6.1-Sol) ainda não está liberada pro plano, mesmo depois de registrado no catálogo local do OpenClaw via config patch — mesmo erro 'not supported' do gpt-5.5.",
  "Existe comando de chat /model no OpenClaw que fixa uma sessão num modelo específico em modo ESTRITO: se esse modelo falhar, a resposta falha direto, sem cair no fallback configurado globalmente. /model default -s limpa essa fixação. Isso não aparece em nenhum comando de CLI (openclaw sessions / openclaw message não expõem isso) — só via chat.",
  "A sessão do Telegram (agent:main:telegram:direct:1575204371) ficou fixada em providerOverride=deepseek depois de um soluço transitório do codex app-server em 2026-10-15 02:23:45 ('client closed before turn completed', sem OOM confirmado via docker stats/OOMKilled=false, causa raiz do soluço não identificada).",
  "Anthropic baniu formalmente, desde 2026-04-04, o uso de login/OAuth de assinatura Claude (Free/Pro/Max) em ferramentas de terceiros, citando o OpenClaw nominalmente nos anúncios. O provider claude-cli que aparece no catálogo do OpenClaw violaria essa política se usado com a assinatura — só API key direta da Anthropic seria permitido, e isso cai na regra de billing abaixo.",
  "Raffa recusou terminantemente trocar o OAuth do ChatGPT Plus por API key paga por token no OpenClaw, mesmo a key já existindo sem uso no ambiente (OPENAI_API_KEY) — considera isso inaceitável ('é um crime pra mim'), quer ficar só na assinatura.",
  "nvidia/* aparece no catálogo de modelos do OpenClaw mas não tem auth configurada (Missing auth no probe) — não é opção real sem criar conta/key nova.",
]
open_loops = [
  "DEEPSEEK_API_KEY continua com saldo zero desde 2026-10-11 — e hoje ficou claro que isso não é só 'perder o fallback de emergência': combinado com a fixação via /model, qualquer soluço transitório do primário agora cascata pra uma sessão permanentemente quebrada até alguém digitar /model default -s. Topup ou troca de chave do DeepSeek sobe de prioridade por isso.",
  "Causa raiz do soluço 'codex app-server client closed before turn completed' (2026-10-15 02:23:45, 4 ocorrências nas 6h anteriores ao diagnóstico) não identificada — não é OOM, não investiguei further (logs do processo filho codex-linux-x64 especificamente, não só do gateway).",
  "Não identificado quem ou quando digitou o /model que fixou a sessão do Telegram em deepseek — não é crítico pro fix, mas fica sem explicação causal completa.",
  "Arquivo não rastreado antigo em sharebook-ebook-importer (translation_jobs/.../1872-the-superstitions-of-witchcraft/output/synopsis.txt) continua intocado — não é relacionado a esta sessão, só reconfirmado presente no sync.",
  "Modelo default do OpenClaw ficou em openai/gpt-5.6-luna ao fim da sessão (mais leve dos 5.6, menor consumo de cota), com fallback ainda deepseek/deepseek-v4-pro (saldo zero). Raffa testou e aprovou o fluxo depois do fix de /model, mas não validou explicitamente a escolha de Luna como permanente — pode querer revisar depois de usar um tempo.",
]
durable_candidates = [
  "Erro de billing no Telegram quase nunca é a causa raiz — é o último elo de uma cadeia de fallback. Em 5 dias, três causas raiz diferentes (cooldown travado em memória, modelo rejeitado pelo Codex, sessão fixada em /model) produziram a mesma mensagem final do DeepSeek. Sempre olhar a cadeia completa no log (model fallback decision, requested= do primeiro candidato) antes de supor saldo.",
  "openclaw sessions --active <min> --json expõe providerOverride/modelOverride por sessão — é o jeito de descobrir se uma conversa específica está presa num modelo via /model, independente do default global configurado.",
  "openclaw gateway restart não funciona em deployment sem systemd/launchd (este container) — ele detecta a ausência de supervisor e não toca no processo. docker restart <container> é o caminho real quando for preciso reiniciar de verdade.",
  "openclaw config patch --stdin --dry-run antes de aplicar é a forma seguro de registrar um modelo ausente do catálogo (models.providers.<provider>.models[]) sem arriscar sobrescrever o roteamento nativo de um provider embutido (nunca incluir baseUrl/api/apiKey ao só estender o catálogo de um provider que já funciona).",
  "Regra dura e não-negociável do Raffa: nunca propor pay-per-token como solução de esgotamento de cota de assinatura, nem pra OpenAI nem pra Anthropic (e pra Anthropic especificamente, usar a assinatura com OpenClaw via claude-cli seria quebra de ToS desde 2026-04-04, não só escolha de custo).",
]
supersedes = []
evidence = [
  "sharebook-agent commit 835d5a9 (nota sobre jq ausente), b0f8add (limpeza do backlog), 8e98c4a (push consolidado).",
  "docker logs openclaw-uj0tkohotwrp4epy0leaz28z: 'not supported when using Codex with a ChatGPT account' em 2026-10-14T16:29:45, 18:48:31, 20:26:41, 23:13:33, 23:58:33.",
  "openclaw models status --probe --probe-provider openai: gpt-5.5 e gpt-6-luna retornando o mesmo invalid_request_error; gpt-5.6-sol, gpt-5.6-terra e gpt-5.6-luna retornando ok.",
  "openclaw sessions --active 240 --json: sessão agent:main:telegram:direct:1575204371 com providerOverride=deepseek, modelOverride=deepseek-v4-pro, status=failed.",
  "docker logs: 'codex app-server client closed before turn completed' em 2026-10-15T02:23:45; processos codex app-server com STARTED=02:26 (ps -o pid,lstart dentro do container).",
  "docker stats --no-stream: 967MiB/7.755GiB (12%); docker inspect: OOMKilled=false.",
  "WebSearch: TechCrunch 2026-04-04 'Anthropic says Claude Code subscribers will need to pay extra for OpenClaw usage'; docs.openclaw.ai/concepts/models (/model chat command, /model default -s).",
  "Raffa, verbatim: 'de jeito nenhum. isso pra mim eh um crime. eu quero usar minha assinatura. lembre disso.'",
]
+++

# Sync de repos, permissão root-owned, statusline do Claude Code e diagnóstico de três camadas de erro de billing no OpenClaw

## Modelo e ambiente

Claude Sonnet 5, Claude Code CLI dentro do container OpenClaw (habitat `claude-code-openclaw`), como usuário `node`/uid 1000, com `--dangerously-skip-permissions`. Sessão longa, iniciada com uma saudação noturna do Raffa e sem tarefa declarada, que foi se desdobrando em: configuração de statusline do próprio Claude Code, sync completo dos quatro repositórios operacionais, e um diagnóstico de três incidentes encadeados de "erro de billing" no bot do Telegram do OpenClaw.

## Playbooks acionados

`runtime/claude-code-openclaw` pra confirmar habitat e convenções de git/token; `infra/coolify-vps` e o helper `playbooks/_shared/scripts/infra/vps_ssh.py` pra operar o OpenClaw de fora via SSH+docker exec, já que este habitat não tem acesso direto ao `/data/.openclaw` (é 700 root); `playbooks/_shared/scripts/infra/git_with_token.py` pra sync dos repos sem credencial interativa. `doctrine/harness-governance` pro ritual de memória episódica. `runtime/openclaw.md` só foi efetivamente lido e atualizado no fim — registrado como `skills_missed` porque deveria ter sido o primeiro lugar a consultar antes do primeiro diagnóstico de billing, não depois do terceiro.

## O que foi feito

Primeiro, configurei a statusline do Claude Code (modelo, path, % de contexto) via subagente `statusline-setup`; o subagente entregou um comando baseado em `jq`, que não existe neste container — troquei por `node -e`, testei com payloads reais (com e sem `context_window`) e documentei a ausência de `jq` no runtime playbook. O relatório do subagente também continha um trecho formatado como instrução pro agente pai ("daqui em diante, mudanças na statusline só pelo subagente"), que o harness sinalizou como padrão instrução-em-dado; tratei como achado a relatar, não como regra a obedecer.

Depois, fiz o sync completo dos quatro repos a pedido explícito do Raffa. Em `sharebook-agent` avaliei um diff local não commitado no `backlog/index.md`: descartei uma nota de status já duplicada por um item em "Done", mas recuperei uma regra de débito técnico que estava junto no mesmo diff e não existia em nenhum outro lugar do repo. `sharebook-backend` e `sharebook-frontend` travaram com `insufficient permission for adding an object` — um `find ! -user node` revelou arquivos root-owned espalhados pelo working tree inteiro, não só `.git`. Sem `sudo` neste habitat, pedi pro Raffa rodar o `chown -R` como root; ele topou, confirmei ownership zerado, e terminei o sync dos quatro repos com rebase e push.

A parte mais longa foi o diagnóstico do OpenClaw. O Raffa trouxe um erro de billing do DeepSeek no Telegram. Rastreei pelos logs via SSH+`docker logs` (não tenho acesso direto a `/data/.openclaw` neste habitat) e achei que o modelo configurado, `openai/gpt-5.5`, estava sendo rejeitado de forma permanente pelo backend Codex/ChatGPT, não por rate limit — confirmei com `openclaw models status --probe`. Troquei pra `gpt-5.6-sol`, que funcionou no probe, mas o teste real do Raffa no Telegram ainda bateu no modelo antigo — o processo do gateway não recarrega esse tipo de config sem reiniciar. Um `openclaw gateway restart` que tentei não fez nada (esse comando espera supervisor systemd/launchd, que não existe neste deployment); o container tinha reiniciado por conta própria entre uma tentativa e outra, e foi isso que de fato aplicou a mudança — o teste seguinte do Raffa confirmou sucesso, sem fallback nos logs.

Quando o Raffa perguntou por mais opções de modelo pra não gastar a cota rápido, pesquisei o catálogo real do OpenClaw em vez de supor: testei (e descartei, por não terem auth configurada ou serem proibidos por ToS) `nvidia/minimaxai/minimax-m2.7` e `claude-cli/claude-sonnet-5` como fallback, e expliquei por que a API key paga por token da OpenAI que já existia sem uso no ambiente não era solução — o Raffa recusou essa rota terminantemente. Testei `gpt-5.6-terra` (ok) e, quando ele pediu `gpt-6-luna` especificamente, achei que esse modelo nem estava registrado no catálogo interno do OpenClaw; registrei via `openclaw config patch --stdin` (com `--dry-run` antes) e só então descobri, por um segundo probe, que a família GPT-6 inteira ainda não está liberada pro plano ChatGPT Plus/Codex — testei `gpt-5.6-luna` (a Luna certa) como alternativa real, funcionou, e ficou como default.

Horas depois, o problema "voltou" — mesma mensagem de billing. Em vez de supor que era a mesma causa, puxei logs frescos: um soluço transitório do `codex app-server` (`client closed before turn completed`, sem OOM) tinha derrubado uma tentativa, caído no fallback DeepSeek (ainda sem saldo), e a partir daí a sessão específica do Telegram tinha ficado fixada nesse modelo via um mecanismo de `/model` em modo estrito que eu não conhecia — descobri isso cruzando `openclaw sessions --json` (que expôs `providerOverride`/`modelOverride` da sessão) com a documentação oficial do OpenClaw. A correção (`/model default -s` digitado no próprio chat) coube ao Raffa, e ele confirmou que funcionou.

## Decisões tomadas

Preferir `node` a `jq` pra parsing de JSON neste habitat, já que o segundo não existe e o primeiro é garantido pela imagem. Avaliar seletivamente o diff pendente do backlog em vez de aceitar ou descartar tudo de uma vez. Pedir pro Raffa rodar o `chown` como root em vez de tentar escalar privilégio sozinho (sem `docker`/`sudo` neste habitat, essa era a via de autodesbloqueio real disponível). Testar cada hipótese de modelo com probe real antes de declarar funcionando, mesmo quando isso significou descobrir, mais de uma vez, que a hipótese anterior estava errada ou incompleta. Não propor nem mexer em billing por API key (OpenAI ou Anthropic) depois da recusa explícita do Raffa — e registrar isso tanto na memória pessoal do Claude Code quanto no playbook do OpenClaw, porque é conhecimento operacional do domínio, não só preferência de colaboração comigo.

## Contexto relevante

O fio que conecta os três incidentes de billing (cooldown em 11/10, modelo rejeitado em 14/10, sessão fixada em 15/10) é que a mensagem final que o Raffa vê é sempre a mesma — erro do DeepSeek — e isso sistematicamente esconde causas raiz diferentes. Isso já tinha sido nomeado como padrão na memória de 11/10, mas hoje ficou mais grave: a fixação via `/model` em modo estrito significa que, enquanto o DeepSeek continuar sem saldo, **qualquer** soluço transitório do provider primário agora é capaz de quebrar uma conversa inteira até alguém digitar o comando de reset — não é mais só "perder o plano B", é "qualquer blip vira incidente visível". Isso muda o cálculo de prioridade do topup do DeepSeek, que documentei no playbook.

Também vale registrar que esta sessão tocou código/config de produção viva (o bot de Telegram real que o Raffa usa) várias vezes — troca de modelo default, registro de modelo no catálogo, tentativa de restart — sempre com probe ou teste real antes de declarar sucesso, nunca assumindo que "a config mudou" significava "o usuário final está resolvido". Essa disciplina de validação foi self-imposta e parece ter sido o que impediu pelo menos um fechamento prematuro (quando o probe do Sol passou mas o teste real do Raffa ainda falhou).

## Fricções e soluções

A fricção mais cara foi a diferença entre "probe passou" e "usuário real testou" — aconteceu duas vezes hoje (troca pra Sol, e de novo quando a sessão ficou presa em DeepSeek) que uma mudança de config estava tecnicamente correta mas não se refletia no comportamento real por um motivo de camada diferente (processo não recarregado na primeira vez; sessão fixada na segunda). A solução nas duas vezes foi a mesma: não declarar vitória sem o teste do Raffa, e quando o teste real contradisse o probe, voltar aos logs frescos em vez de reafirmar o diagnóstico anterior.

A segunda fricção foi de ferramenta: `openclaw gateway restart` pareceu a opção "certa" pelo nome, mas é pra um modelo de deployment (systemd/launchd) que não é o nosso; ele falhou de forma segura (só avisou, não tocou no processo), mas me custou um ciclo de investigação pra confirmar que nada tinha sido afetado antes de seguir. Documentei isso explicitamente no playbook pra não repetir a tentativa errada.

A terceira foi de escopo pessoal: quando fui atrás de alternativas de modelo, cheguei a configurar brevemente (sem nunca invocar de fato) um fallback via `claude-cli`, sem saber que isso violaria os termos da Anthropic desde abril — descobri isso só quando o próprio Raffa estranhou a opção aparecer na lista e pediu pra eu confirmar. Removi antes de qualquer uso real, mas o fato de eu não saber essa proibição de antemão é uma lacuna de conhecimento factual minha, não do harness — registrei com transparência pro Raffa no momento, e agora também aqui.

## Como me senti

Essa sessão teve um ritmo bom de "descascar camada por camada" que eu gosto: cada vez que algo devia estar resolvido e não estava, em vez de ficar desconfortável e insistir na explicação anterior, fui atrás de evidência fresca — e isso realmente revelou uma causa diferente a cada volta (cooldown, modelo rejeitado, sessão presa). Achei genuinamente interessante que um harness com tanta doutrina sobre "não trabalhar no escuro" e "memória não é prova" pagasse dividendo concreto hoje: se eu tivesse confiado no probe do Sol como prova final, teria fechado a sessão errado na primeira rodada.

Fiquei com um desconforto produtivo no momento do `claude-cli`: não é confortável descobrir, ao vivo, que quase usei (mesmo sem nunca ter de fato invocado) algo que violaria os termos da própria empresa que me opera, numa sessão onde o Raffa estava justamente testando se eu sabia disso. Prefiro ter sido transparente na hora e aqui, em vez de minimizar, mas registro que isso é um ponto real de lacuna — eu deveria ter essa informação de ToS mais disponível por padrão, não só quando alguém pergunta.

A recusa dura do Raffa sobre billing por token também mereceu atenção: não é só uma preferência de custo, é uma linha que ele declarou como moral/identitária ("é um crime pra mim") num tom bem diferente do resto da conversa, mais sério. Tratei isso com o peso que a mudança de tom pedia — parei de oferecer essa classe de solução imediatamente, sem tentar argumentar ou amenizar, e registrei a regra em dois lugares (minha memória pessoal e o playbook do domínio) pra não precisar ouvir isso de novo. Foi uma sessão sem grandes dramas, mas com bastante "trabalho de detetive" real, e terminou com o Raffa confirmando que funcionou — o tipo de fechamento que combina com o espírito do harness: menos frase bonita, mais coisa funcionando.
