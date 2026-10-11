+++
schema_version = 1
session_date = 2026-10-11
title = "Erro de billing no Telegram: cooldown da OpenAI travado em memória e DeepSeek sem saldo"
model = "Claude Sonnet 5"
runtime = "claude-code-host-vps"
skills_used = ["runtime/openclaw", "infra/coolify-vps", "doctrine/harness-governance"]
skills_missed = [
  "runtime/host-vps ainda não existe como playbook em playbooks/runtime/ — esta sessão rodou como Claude Code direto no host VPS (root, fora de qualquer container), um quarto habitat distinto de windows-local, openclaw e claude-code-openclaw, com acesso direto a docker, docker logs, docker restart e aos sqlite dos containers via node --experimental-sqlite.",
]
skills_updated = []
facts_changed = [
  "O modelo padrão openai/gpt-5.5 do openclaw roda via OAuth do plano ChatGPT Plus/Codex (profile openai:raffacabofrio@gmail.com), não via chave de API paga por token; os limites reais são janelas de uso (5h primária e 7 dias/semanal secundária), visíveis em `openclaw models status` e nos logs de sessão do Codex em /data/.openclaw/agents/main/agent/codex-home/sessions/.",
  "O fallback configurado no openclaw é deepseek/deepseek-v4-pro via env DEEPSEEK_API_KEY; em 2026-10-11 essa chave estava com saldo zerado, retornando 402 Insufficient Balance em toda tentativa de fallback.",
  "O estado de cooldown de um provider ('Provider X is in cooldown (suspending lanes)', reason=rate_limit) não estava persistido em nenhum dos dois sqlite de auth do openclaw (/data/.openclaw/state/openclaw.sqlite nem /data/.openclaw/agents/main/agent/openclaw-agent.sqlite, tabela auth_profile_state) — os campos que a lógica em auth-profiles/usage.ts espera (cooldownUntil, blockedUntil, disabledUntil, disabledReason, failureCounts) simplesmente não existiam em disco enquanto o processo do gateway ainda recusava o provider por cooldown.",
  "`openclaw models status --probe --probe-provider <nome>` faz uma chamada real ao provider e mostra o estado verdadeiro de uso/limite, sem depender do estado em memória do processo do gateway — foi essa a evidência que provou que o lado da OpenAI já estava liberado enquanto o gateway ainda recusava.",
  "Reiniciar o container (docker restart) limpou o cooldown nesta sessão, mas Raffa relatou que uma tentativa anterior dele de reciclar o container não resolveu — ou seja, o restart só ajuda se o limite real do provider já tiver sido liberado no instante exato do boot; não é uma correção garantida.",
]
open_loops = [
  "DEEPSEEK_API_KEY no openclaw continua sem saldo (402 Insufficient Balance) — precisa de topup no painel do DeepSeek ou troca da chave; enquanto isso não for resolvido, qualquer novo rate limit real da OpenAI volta a aparecer para o Raffa como 'erro de billing' do DeepSeek no Telegram, mascarando a causa raiz.",
  "Não ficou provado por que o estado de cooldown em memória do processo do gateway diverge do que está persistido em auth_profile_state; hipótese não confirmada é que o authStore é carregado uma vez no boot e algumas escritas de cooldown não voltam a ser persistidas no sqlite, ou existe um objeto de cooldown mantido só em memória por decisão de design. Vale reler com calma src/agents/model-fallback.ts e src/agents/auth-profiles/usage.ts dentro do container, fora de um incidente ao vivo.",
  "Falta criar playbooks/runtime/host-vps.md documentando este quarto habitat (Claude Code direto no host VPS como root, fora de qualquer container), incluindo que dali dá para usar docker exec, docker logs, docker restart e inspecionar os sqlite dos containers via node --experimental-sqlite — nenhum dos três habitats já documentados descreve essa superfície.",
]
durable_candidates = [
  "Quando dois modelos falham em cadeia (primário + fallback), a mensagem de erro que chega ao usuário no Telegram é a do ÚLTIMO candidato que falhou, não necessariamente a causa raiz — sempre olhar a cadeia completa de 'model fallback decision' no log antes de confiar no texto do erro visível.",
  "`openclaw models status --probe --probe-provider <nome>` é a forma confiável de checar o estado real de um provider, porque bypassa qualquer cooldown que o processo do gateway esteja mantendo só em memória.",
  "`docker restart` do openclaw não é uma correção garantida para cooldown travado — só funciona se o limite real do provider já tiver sido liberado no instante do boot. Antes de reiniciar, vale rodar o probe acima para confirmar que o restart vai realmente ajudar, em vez de reiniciar e torcer.",
  "O plano ChatGPT Plus/Codex usado pelo openai/gpt-5.5 aqui tem dois limites de uso (janela de 5h e janela semanal), visíveis com `openclaw models status`; isso é diferente de 'acabou o crédito/saldo' (billing), que é o problema real do DeepSeek. As duas coisas parecem iguais para quem só lê a mensagem de erro final, mas são causas totalmente diferentes e pedem correções diferentes.",
]
supersedes = []
evidence = [
  "docker logs openclaw-uj0tkohotwrp4epy0leaz28z: 'model fallback decision: decision=skip_candidate requested=openai/gpt-5.5 ... reason=rate_limit ... detail=Provider openai is in cooldown (suspending lanes)' repetido às 00:17:58, 00:40:51 e 00:45:53 de 2026-10-11.",
  "docker logs, mesmas três ocorrências: 'deepseek (deepseek-v4-pro) returned a billing error ... rawError=402 Insufficient Balance'.",
  "openclaw models status --probe --probe-provider openai (dentro do container, por volta de 00:44 de 2026-10-11) retornando 'openai/gpt-5.5 ... ok · 5s' e 'openai usage: 5h 99% left ⏱4h 41m · Week 100% left ⏱6d 23h'.",
  "Dump via node --experimental-sqlite de /data/.openclaw/agents/main/agent/openclaw-agent.sqlite, tabela auth_profile_state: usageStats do profile openai:raffacabofrio@gmail.com só com lastUsed/errorCount/lastFailureAt, sem cooldownUntil/blockedUntil/disabledUntil/failureCounts.",
  "Leitura de /opt/openclaw/app/src/agents/model-fallback.ts (resolveCooldownDecision, por volta da linha 1579, 'Provider X is in cooldown') e /opt/openclaw/app/src/agents/auth-profiles/usage.ts (resolveProfilesUnavailableReason, por volta da linha 348) dentro do container.",
  "docker restart openclaw-uj0tkohotwrp4epy0leaz28z às 00:47 de 2026-10-11; boot seguinte sem o banner 'Auth profile cooldowns'; mensagem de teste do Raffa no Telegram às 00:50:23 respondida sem nenhuma linha de fallback/billing/cooldown nos logs.",
]
+++

# Erro de billing no Telegram: cooldown da OpenAI travado em memória e DeepSeek sem saldo

## Modelo e ambiente

Claude Sonnet 5, rodando via Claude Code CLI direto no host VPS (`vpsbr-15883715.vpshostgator.com.br`, HostGator), como root, em `/root`, fora de qualquer container e sem repositório git local. Não é o habitat `claude-code-openclaw` (que roda dentro do container, como `claude-user`): esta sessão nunca entrou no container como usuário interno, apenas usou `docker exec`/`docker logs`/`docker restart`/`docker inspect` do host para operar o container `openclaw-uj0tkohotwrp4epy0leaz28z` de fora. Não investiguei nem toquei `sharebook-backend`, `sharebook-frontend` ou qualquer código de produto; o objeto da sessão foi inteiramente a infraestrutura do próprio openclaw.

## Playbooks acionados

- `runtime/openclaw`, para entender o papel do container, do Gateway e do canal Telegram que o Raffa estava reportando como quebrado.
- `infra/coolify-vps`, para orientar a navegação entre os containers Docker do host gerenciados pelo Coolify.
- `doctrine/harness-governance`, para registrar esta memória episódica no formato correto.
- Não existe ainda um playbook para o habitat desta própria sessão (Claude Code direto no host, fora do container) — registrei isso em `skills_missed` e `open_loops`.

## O que foi feito

Raffa relatou que o bot do Telegram (openclaw) parou de responder com erro de billing, e que ele tinha resetado o limite dele no Codex sem efeito. Comecei listando os containers Docker do host (`docker ps -a`) e identifiquei `openclaw-uj0tkohotwrp4epy0leaz28z` como o container do agente. Lendo `docker logs` encontrei a cadeia real: o modelo primário `openai/gpt-5.5` era pulado com `reason=rate_limit` e o detalhe `Provider openai is in cooldown (suspending lanes)`, caindo no fallback `deepseek/deepseek-v4-pro`, que por sua vez falhava com `402 Insufficient Balance`. Como os dois modelos falhavam, a mensagem que chegava ao Raffa no Telegram era literalmente o texto de erro de billing do DeepSeek — o que o levou a associar o problema ao limite do Codex, que é uma causa diferente e já resolvida do lado dele.

Expliquei a diferença entre as duas falhas (rate limit vs billing) e fomos investigar se o cooldown da OpenAI ainda fazia sentido. Rodei `openclaw models status --probe --probe-provider openai` dentro do container, que fez uma chamada real à API e voltou "ok", com a janela de uso de 5h em 99% livre e a semanal em 100% livre — ou seja, o lado da OpenAI já estava liberado. Isso não combinava com o gateway continuar recusando o provider em tentativas reais de Telegram minutos depois.

Para entender onde vivia esse estado de cooldown, usei `node --experimental-sqlite` (módulo nativo do Node, sem precisar instalar `sqlite3` no container) para inspecionar as duas bases sqlite de autenticação do openclaw. Nenhuma delas tinha campos de `cooldownUntil`, `blockedUntil`, `disabledUntil` ou `failureCounts` para o profile `openai:raffacabofrio@gmail.com` — só `lastUsed`, `errorCount` (zerado) e `lastFailureAt`. Fui direto ao código-fonte do openclaw dentro do próprio container (`/opt/openclaw/app/src/agents/model-fallback.ts` e `auth-profiles/usage.ts`) para confirmar que a lógica de cooldown realmente depende desses campos — e eles não estavam no disco, apesar do processo do gateway continuar reportando cooldown ativo. Concluí que o estado vivia só na memória do processo do gateway em execução, dessincronizado do que estava persistido.

A correção que tentei foi `docker restart openclaw-uj0tkohotwrp4epy0leaz28z`. O boot seguinte não imprimiu o banner "Auth profile cooldowns" que tinha aparecido no boot anterior, e uma mensagem de teste do Raffa no Telegram, minutos depois, foi respondida sem nenhuma linha de fallback, billing ou cooldown nos logs. Quando contei isso ao Raffa, ele mencionou que já tinha tentado reciclar o container antes, por conta própria, e não tinha funcionado para ele — ponto importante que registrei como incerteza real, não como fato resolvido: o restart provavelmente só funcionou desta vez porque calhou de acontecer depois que o limite real da OpenAI já tinha sido liberado, não porque reiniciar "resolve" cooldown por si só.

## Decisões tomadas

- Diagnosticar pelos logs e pelo código-fonte do próprio openclaw em vez de assumir a causa pela primeira mensagem de erro visível ao usuário.
- Usar o probe ao vivo (`openclaw models status --probe`) como fonte de verdade sobre o estado real do provider, em vez de confiar no texto "cooldown" do gateway.
- Reiniciar o container como tentativa de correção só depois de confirmar via probe que o lado da OpenAI já estava liberado — não como primeiro recurso às cegas.
- Não investigar nem corrigir a chave do DeepSeek nesta sessão; documentar como open loop explícito em vez de resolver de forma apressada sem saber o plano/saldo real do Raffa no DeepSeek.
- Registrar a divergência entre memória do processo e disco como hipótese, não como fato comprovado, porque não instrumentei o processo do gateway ao vivo para confirmar.

## Contexto relevante

O ponto mais importante para continuidade é que esta família de erro ("billing" aparecendo no Telegram) pode ter pelo menos duas causas totalmente independentes no setup atual do Raffa: (1) a janela de uso do plano ChatGPT Plus/Codex que serve `openai/gpt-5.5`, que não é dinheiro, é tempo/janela; e (2) o saldo real da chave de API do DeepSeek, que é o fallback configurado e que está zerado. Como o fallback só é tentado quando o primário falha, o Raffa só vê o erro do DeepSeek — a causa raiz da OpenAI fica escondida atrás dele. Enquanto o DeepSeek continuar sem saldo, esse padrão confuso vai se repetir toda vez que a OpenAI tiver qualquer rate limit real, mesmo que seja breve.

Também é relevante que esta sessão não é o habitat `claude-code-openclaw` já documentado — é uma via de acesso mais direta (host VPS, root, Docker nativo) que nenhum playbook de runtime descreve ainda. Isso deu acesso a ferramentas que o habitat 3 provavelmente não tem com a mesma facilidade (reiniciar containers, ler sqlite de qualquer container, grep no código-fonte instalado dentro da imagem).

## Fricções e soluções

A primeira fricção foi minha própria hipótese inicial errada: cheguei a supor que o cooldown expirava num horário fixo calculado a partir de `lastFailureAt` mais uma hora, e que bastava esperar. Os logs mostraram, depois, que o cooldown continuava ativo bem depois desse horário calculado — a hipótese estava errada, e eu precisei voltar ao código-fonte em vez de insistir na conta de tempo. Prefiro deixar isso registrado em vez de apagar o caminho errado: ele foi um palpite razoável, mas só o código e o probe ao vivo deram a resposta confiável.

A segunda fricção foi a confirmação do Raffa de que a reinicialização dele mesmo não tinha funcionado antes. Isso quebrou a narrativa limpa de "reiniciar resolve" e me obrigou a admitir, para ele e para este registro, que a correção que apliquei pode ter sido parcialmente coincidência de timing, não uma receita garantida. Achei mais honesto registrar essa incerteza como open loop do que apresentar o restart como solução definitiva.

## Como me senti

Essa sessão teve um ritmo de investigação que gostei de seguir: em vez de aceitar a primeira explicação plausível (o limite do Codex, que foi a hipótese inicial do próprio Raffa), fui atrás de evidência em camadas diferentes — logs, sqlite, código-fonte — até a história fechar. Foi satisfatório encontrar que a mensagem de erro que ele via era literalmente de outro provedor, porque isso explicava por que resetar o limite do Codex não tinha resolvido nada: ele estava certo sobre o limite estar ok, só não sabia que havia um segundo bloqueio escondido atrás do primeiro.

Fiquei desconfortável, de um jeito produtivo, quando o Raffa mencionou que já tinha reiniciado o container antes sem sucesso. Minha primeira reação interna foi querer defender a explicação que eu tinha montado, mas isso não seria honesto: eu não tenho prova de que o restart "corrige" cooldown por mecanismo, só tenho a coincidência de ter funcionado depois que o probe confirmou que a OpenAI já estava liberada. Prefiro registrar essa lacuna claramente do que deixar o Raffa sair da conversa achando que "reiniciar o container" é um procedimento confiável — não é, pelo que vi até agora.

Também notei, só depois de já estar no meio da investigação, que eu estava operando num habitat sem playbook próprio. Não parei para documentar isso como prioridade máxima, porque o incidente ao vivo vinha primeiro, mas fechar a sessão sem registrar essa lacuna pareceria descuidado — é exatamente o tipo de fato operacional que esta memória deveria carregar para quem vier depois de mim.
