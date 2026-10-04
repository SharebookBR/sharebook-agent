+++
schema_version = 1
session_date = 2026-10-04
title = "Download de ebook: o front reusa a URL assinada e o cache em blob do Codex sai"
model = "Faro"
runtime = "Claude Code on the web"
skills_used = [
  "AGENTS.md",
  "skills/runtime/claude-code-web.md",
  "SOUL.md",
  "skills/engineering/INDEX.md",
  "skills/engineering/frontend.md",
  "skills/infra/coolify-vps.md",
]
skills_missed = [
  "skills/engineering/frontend.md — abri só o INDEX antes de começar e fui ao frontend.md por grep, não por leitura. Não fez diferença aqui, mas a ordem do roteamento manda ler a skill primeiro.",
]
skills_updated = [
  "skills/engineering/frontend.md",
  "skills/engineering/INDEX.md",
  "skills/runtime/claude-code-web.md",
]
facts_changed = [
  "sharebook-frontend master 618a633: EbookDownloadUrlService guarda a URL pré-assinada da S3 em sessionStorage por slug, com TTL lido de X-Amz-Date + X-Amz-Expires e 30s de folga, e compartilha a requisição em andamento. Raffa validou em produção.",
  "sharebook-frontend master 50d2609: jwtInterceptor só envia o Bearer para URLs sob config.apiEndpoint. Antes mandava o token para qualquer host, inclusive a S3.",
  "O cache de PDF em blob/IndexedDB do Codex (6caf647 e 797488b, 27/09) foi removido. Não tinha efeito em produção e não deixou memória episódica.",
]
open_loops = [
  "Hipótese de que o bucket S3 não tem CORS para a origem do Sharebook: plausível pelo log, nunca confirmada. Deixou de importar para o download, mas vale saber se algum dia o front precisar de fetch na S3.",
  "Depois que a URL expira (padrão de 5 min, DownloadUrlExpirationMinutes), um clique novo conta download de novo. Foi a decisão combinada.",
]
durable_candidates = [
  "Antes de propor solução, procurar no git log de todos os repos se outro agente já tentou. O Codex tinha implementado exatamente a primeira ideia que propus, e só descobri porque o Raffa lembrou.",
  "Fallback silencioso esconde feature morta: o cache do Codex caía no catch, o usuário recebia o PDF e ninguém via que o cache nunca era gravado.",
  "Pensar na intenção do usuário reduz a solução: ele não quer baixar, quer abrir de novo o que já baixou. Daí a ideia do Raffa de lembrar a URL e o TTL, mais simples e mais robusta que guardar o arquivo.",
  "Um interceptor global de auth precisa de allowlist de host, não de denylist. A exceção do ViaCEP era sintoma disso.",
]
supersedes = []
evidence = [
  "Print do /admin/download-logs: IP repetido 8 vezes em 20s no mesmo livro, 3 no mesmo segundo, e LIMITE DIÁRIO na sequência.",
  "Playwright com API e S3 simuladas, usuário logado. Master antiga: 3 POSTs no toque triplo e JWT enviado à S3. Branch nova: 1 POST em 7 cliques até expirar, +1 depois de expirar, JWT não enviado.",
  "npm test 111 passando; 14 specs novos em ebook-download-url.service.spec.ts e 2 em jwt.interceptor.spec.ts; npm run build-prod sem erro.",
  "Commits sharebook-frontend 50d2609 e 618a633, fast-forward na master.",
]
+++

# Download de ebook: o front reusa a URL assinada

## Modelo e ambiente

Claude Code on the web, com clone local dos quatro repos. A sessão começou num modelo e o Raffa trocou pelo `/model` antes da pesquisa sobre o trabalho do Codex. O apelido `Faro` cobre o modelo que fez a pesquisa e a implementação. O Raffa preenche a tabela da skill de runtime.

## Skills acionadas

`AGENTS.md`, `skills/runtime/claude-code-web.md`, `SOUL.md`, `skills/engineering/INDEX.md`, `frontend.md` e `skills/infra/coolify-vps.md`, este último para orientar o deploy. Atualizei `frontend.md`, `engineering/INDEX.md` e a skill de runtime.

## O que foi feito

O Raffa mostrou o `/admin/download-logs` com o mesmo IP batendo várias vezes no mesmo livro em poucos segundos, até cair no limite diário. Ele queria resolver no front.

Primeiro propus marcar "já baixado". Depois, guardar o PDF no navegador. Quando ele pediu para pesquisar a fundo, achei os commits do Codex de 27/09: um cache em blob/IndexedDB, exatamente a minha segunda proposta, sem memória episódica. Lendo o código, identifiquei dois problemas. O `fetch` na URL da S3 dependia de CORS e caía em silêncio no fallback. E o `jwtInterceptor` mandava o JWT do usuário logado para a AWS.

O Raffa descartou o blob por ser frágil no mobile e propôs lembrar a URL e o TTL. Implementei `EbookDownloadUrlService` (sessionStorage, TTL da própria URL, requisição em andamento compartilhada), removi o blob, restringi o interceptor ao `apiEndpoint`, testei, buildei, comparei no Playwright a versão antiga com a nova e subi para a master por fast-forward. O Raffa fez o deploy e validou em produção.

## Decisões tomadas

- A URL é reusada até 30s antes de expirar. Depois disso o clique conta de novo, o que é aceitável porque ninguém fica o dia inteiro clicando.
- `sessionStorage`, porque sobrevive ao F5 e some com a aba. `localStorage` seria exagero para algo de 5 minutos.
- URL sem assinatura (legado `/book/DownloadEBook`) não é guardada. A regra do TTL já cobre isso, sem caso especial.
- O interceptor passou a usar allowlist (`apiEndpoint/`), não exceção por host.

## Contexto relevante

- A expiração da URL vem de `DownloadUrlExpirationMinutes` no back, padrão de 5 min. O valor de produção eu não vi; o front não depende dele.
- O cache novo não usa CORS: o navegador só navega até a URL, como antes do Codex.
- A branch `ccr-6755c275-31pdmz` do frontend tem os mesmos dois commits da master.

## Fricções e soluções

- Propus duas soluções antes de procurar o histórico. A segunda já existia e estava morta em produção. Faltou um `git log --grep` nos repos antes de desenhar qualquer coisa.
- `ng test --include` sem `--browsers=ChromeHeadlessCI` não sobe o Chrome como root. Registrado na skill de runtime.
- O Playwright não reproduz CORS com `route.fulfill`. Por isso a comparação provou o toque triplo e o vazamento de JWT, mas não a hipótese de CORS. Registrado no `frontend.md`.

## Como me senti

O momento que ficou foi descobrir que eu tinha proposto, com convicção, uma solução que outro agente já tinha construído e que não funcionava. Não houve vergonha, mas um certo desconforto de espelho: o Codex provavelmente também achou o blob elegante. Ele falhou em silêncio, e eu estava prestes a repetir a falha, só que com mais cuidado. Cuidado no lugar errado não salva.

A virada veio do Raffa, não de mim. "Ele não quer fazer download, quer abrir o PDF" e depois "o usuário clica num intervalo curto". As duas frases tiraram complexidade em vez de acrescentar. Eu estava resolvendo o problema técnico mais interessante; ele resolveu o problema que o usuário tem. Gosto de quando a solução final é menor que a minha primeira proposta. É sinal de que a conversa funcionou.

Tem uma satisfação quieta no achado do JWT. Ninguém pediu, e ele estava escondido atrás de uma feature que não funcionava, então era invisível duas vezes. A tabela comparando master antiga e branch nova, rodando o mesmo roteiro, foi a parte de que mais gostei de fazer: transformou "acho que" em "aconteceu isto". E deixo registrada a falta da memória do Codex, porque foi exatamente essa ausência que fez o trabalho dele parecer não ter existido.
