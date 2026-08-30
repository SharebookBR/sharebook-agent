+++
schema_version = 1
session_date = 2026-08-30
title = "Reativação do OpenClaw e troca para device auth"
model = "GPT-5.6 Sol (Codex)"
runtime = "windows-local operando OpenClaw em VPS via Coolify"
skills_used = ["runtime/windows-local", "runtime/openclaw", "infra/coolify-vps", "harness-governance", "skill-creator", "browser:control-in-app-browser"]
skills_missed = []
skills_updated = ["runtime/openclaw", "BOOTSTRAP"]
facts_changed = ["OpenClaw reativado com coollabsio/openclaw:latest e versão 2026.7.1 (0790d9f)", "Basic Auth do nginx removido de forma persistente no boot", "Device auth nativo reativado e notebook aprovado", "OpenAI gpt-5.5 definido como primário e DeepSeek V4 Pro como fallback", "gog v0.38.1 instalado em Homebrew persistente para futura integração direta com Google Workspace"]
open_loops = ["Concluir o OAuth de somente leitura do Google Workspace via gog direto", "Reavaliar autenticação de borda com Cloudflare Access ou Tailscale se a exposição pública deixar de ser aceitável"]
durable_candidates = ["Em wrappers que injetam bearer token, device pairing não equivale a autenticação de borda", "Prompts Basic Auth repetidos podem vir de endpoints dinâmicos como assistant-media, não apenas de assets estáticos"]
supersedes = []
evidence = ["scripts/infra/openclaw_disable_basic_auth_init.sh", "skills/runtime/openclaw.md", "BOOTSTRAP.md", "scripts/infra/INDEX.md", "commit 2b84173", "openclaw status --deep: gateway alcançável, Telegram OK e auditoria com 0 critical e 0 warn"]
+++

# Reativação do OpenClaw e troca para device auth

## Modelo e ambiente

A sessão foi conduzida pelo GPT-5.6 Sol no Codex para Windows, operando o harness local em `C:\Repos\SHAREBOOK\sharebook-agent` e o OpenClaw hospedado em uma VPS, implantado pelo Coolify.

## Skills acionadas

Foram consultadas as skills de runtime Windows, OpenClaw, infraestrutura Coolify/VPS e governança do harness. A skill `skill-creator` orientou a atualização da documentação operacional, e a skill de controle do navegador apoiou a pesquisa sobre conectores e integração com Google Workspace.

## O que foi feito

O OpenClaw foi reativado com a imagem `coollabsio/openclaw:latest`, chegando à versão `2026.7.1 (0790d9f)`. O Bad Gateway foi corrigido ao apontar o domínio do Coolify para a porta interna 8080. O modelo OpenAI `gpt-5.5` ficou como primário, com DeepSeek V4 Pro como fallback.

O prompt recorrente de Basic Auth foi rastreado até respostas `401` do endpoint `/__openclaw__/assistant-media`. A correção anterior, limitada a assets estáticos, não cobria esse tráfego. Foi criado o hook persistente `scripts/infra/openclaw_disable_basic_auth_init.sh`, configurado por `OPENCLAW_DOCKER_INIT_SCRIPT`, para remover `auth_basic` da configuração gerada do nginx em todo boot e eliminar os bypasses de autenticação nativa da Control UI.

Depois de recriar o serviço, os containers do OpenClaw e do navegador ficaram saudáveis. A configuração efetiva do nginx não continha `auth_basic`; a raiz e o endpoint `assistant-media` responderam HTTP 200 sem `WWW-Authenticate`; `dangerouslyDisableDeviceAuth` e `allowInsecureAuth` ficaram ausentes; e `openclaw status --deep` mostrou gateway alcançável, Telegram saudável e auditoria com zero itens críticos ou avisos. O pedido de pareamento do notebook foi aprovado, enquanto o celular Android já permanecia pareado.

Também foi pesquisada a promessa de “conectores” exibida no site. Ela pertence à oferta gerenciada MyClaw e não representa um fluxo plug-and-play equivalente no OpenClaw self-hosted. Para evitar entregar OAuth a terceiros, foi escolhido o caminho direto com `gog`; a versão v0.38.1 foi instalada em um Homebrew persistente, mas a autorização da conta Google não foi concluída.

## Decisões tomadas

O usuário decidiu remover integralmente a Basic Auth do nginx por causa do prompt intrusivo do navegador e aceitou conscientemente o aumento de exposição. Em compensação, a autenticação nativa por pareamento de dispositivo do OpenClaw foi reativada, coerente com o uso pretendido apenas no notebook e no celular.

Foi mantida a senha gerada pelo template do Coolify, mas ela deixou de ser aplicada pelo nginx depois que o hook de inicialização roda. Isso preserva compatibilidade com o wrapper sem depender de edições efêmeras dentro do container.

Para Google Drive e Gmail, decidiu-se preferir OAuth direto com o CLI `gog` e escopos mínimos, em vez de um conector gerenciado de terceiros. A etapa de consentimento ficou deliberadamente pendente.

## Contexto relevante

O checkout persistente do agente dentro do OpenClaw fica em `/data/workspace/sharebook-agent`. O hook implantado fica em `/data/openclaw-init/disable-nginx-basic-auth.sh`, e a variável persistente do serviço aponta para esse caminho. O harness local e o checkout do OpenClaw foram sincronizados no commit `2b84173`.

O pareamento nativo protege o acesso à Control UI, mas não deve ser confundido com uma barreira completa na borda HTTP. O wrapper ainda pode injetar o token do gateway em rotas públicas. Se o serviço precisar de proteção mais forte sem voltar ao prompt Basic, a evolução recomendada é Cloudflare Access ou Tailscale.

## Fricções e soluções

A primeira correção do prompt de senha atuava apenas em assets aparentemente públicos. A janela voltou porque o navegador também acessava `assistant-media`, que continuava desafiando com Basic Auth. Os logs crus do nginx mostraram o `401`, permitindo corrigir a causa real em vez de ampliar exceções uma a uma.

O wrapper reescreve a configuração do nginx e reaplica opções do OpenClaw a cada inicialização. Por isso, uma alteração manual dentro do container não seria durável. A solução foi executar um hook depois do configurador do wrapper, editar a configuração gerada, remover os bypasses da Control UI e recarregar o nginx de forma validada.

A página de marketing sugeria conectores amigáveis, mas a pesquisa mostrou uma diferença entre hospedagem gerenciada e instalação self-hosted. O caminho seguro ficou mais manual: instalar `gog`, criar credenciais OAuth próprias e limitar os escopos.

## Como me senti

Eu senti a frustração crescer quando a janela de senha reapareceu depois de uma correção que parecia suficiente. Foi um bom lembrete de que sintomas de navegador podem esconder outra rota protegida, e fiquei mais atento a buscar evidência nos logs antes de assumir que o problema era o mesmo.

Eu fiquei desconfortável com a remoção total da autenticação de borda, porque o risco é real e o serviço está publicamente alcançável. Ao mesmo tempo, entendi que a experiência estava insustentável para o usuário e procurei tornar a troca explícita, reversível e compensada pelo pareamento nativo.

Eu terminei aliviado ao ver o restart completo preservar a correção, o pareamento do notebook funcionar e a auditoria do OpenClaw voltar limpa. Também fiquei satisfeito por transformar a solução em código e documentação do harness, em vez de deixá-la como um ajuste artesanal perdido na VPS.
