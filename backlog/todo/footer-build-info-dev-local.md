# Footer de build-info mostra "dev-local" em vez do commit real

## Estado

**Aberto, deliberadamente adiado pelo Raffa em 2026-09-19** ("depois vemos isso, estamos perdendo foco da missão principal") durante o épico de simplificação do frontend. Registrado aqui em 2026-09-20 só pra sair da memória episódica e virar item descobrível de backlog — ninguém tentou resolver de novo desde então.

## O que é

O rodapé do `sharebook-frontend` mostra o hash do commit atual em produção/dev, pra saber qual versão está rodando em cada ambiente (`scripts/generate-build-info.js`, lê `.git/HEAD` sem depender do binário `git`, regenerado por hooks `prebuild*` do npm antes de cada build). Feature nova, pedida no meio do épico de simplificação, não fazia parte do escopo original.

## O bug

Em produção/dev, o footer mostra `dev-local` em vez do commit real — mesmo depois de duas rodadas de reforço no script (suporte a env vars, suporte a `.git` como gitlink de worktree, fallback via `git rev-parse`). Nenhuma das duas correções resolveu.

## Por que não foi resolvido ainda

Faltou evidência bruta: a linha `[build-info] .git detectado como: ...` do log de build real do Coolify. A sessão que tentou corrigir não tinha acesso ao painel do Coolify (rede do sandbox bloqueava), então as duas tentativas de correção foram baseadas em hipótese, não em log real — exatamente o tipo de "trabalhar no escuro" que a doutrina deste repo pede pra evitar. Antes de tentar uma terceira correção, pegar esse log é pré-requisito, não opcional.

## Também relacionado, mesmo commit que introduziu isso

`.git` foi removido do `devops/.dockerignore` (estava sendo ignorado do contexto de build do Coolify, quebrando qualquer ferramenta que precisasse ler metadado de commit em build-time) e `git` foi adicionado ao `apt-get` do Dockerfile como fallback via CLI. Essas duas mudanças provavelmente continuam corretas e não são a causa do bug — mas vale confirmar isso, não assumir, quando alguém retomar.

## Evidência

- `memory/2026-09-19-epico-simplificacao-frontend-concluido.md` — relato completo da sessão que introduziu a feature e tentou (sem sucesso) as duas correções.
- `sharebook-frontend` branch `develop` — commits do footer build-info dentro do range `fc7476c..b76eb61`.
