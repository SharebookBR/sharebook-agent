# Tarefa 5 — Specs de caracterização dos services críticos

## O que existe hoje

Apenas 10/58 componentes (17%) e 2/19 services têm spec. Os services sem nenhum teste incluem os mais centrais da aplicação: `authentication.service.ts`, `book.service.ts`, `user.service.ts`, além de `category.service.ts`, `contact-us.service.ts`, `meetup.service.ts`, `platform.service.ts`, `browser-storage.service.ts`, `operations.service.ts`, `technologies.service.ts`, `confetti.service.ts`, `careers.service.ts`, `ssr-cache.service.ts`, `tools.service.ts`, `contributors.service.ts`, `google-analytics.service.ts`, `environment-switcher.service.ts`.

## Por que revisar

O princípio do épico é "usar os testes existentes como rede de segurança e identificar onde faltam antes de mexer em código de maior risco" — hoje não existe rede nenhuma pros três services que mais importam (autenticação, livro, usuário). Qualquer refactor "de aparência segura" neles (incluindo a Tarefa 1, reorganização de pastas, e a Tarefa 6, interceptors funcionais) corre sem prova de que não regrediu.

## Abordagem

Escrever **specs de caracterização** — o que o código faz hoje, não o que deveria fazer — pra `authentication.service.ts`, `book.service.ts` e `user.service.ts` antes de qualquer outra tarefa deste épico tocar neles. Não é reescrever o service, é travar o comportamento atual em teste antes de mexer na estrutura ao redor.

Os demais 14 services sem teste ficam de prioridade menor — cobrir oportunisticamente quando alguma outra tarefa do épico tocar neles (ex.: ao mover `category.service.ts` pra `features/category/` na Tarefa 1).

## Benefício esperado

Transforma "espero não ter quebrado" em "sei que não quebrei" para o código de maior risco do app (autenticação e fluxo de doação).

## Risco de não fazer

Alto — é precisamente onde um refactor de reorganização ou de interceptors pode introduzir regressão silenciosa em produção, sem qualquer sinal automático até alguém reportar em produção.

## Como validar

As specs em si são a validação — cobertura de comportamento real (login, refresh de token, fluxo de erro de autenticação; CRUD e transições de status de livro; leitura/atualização de perfil de usuário), rodando contra o comportamento atual antes de qualquer mudança estrutural.

## Status final — CONCLUÍDA em 2026-09-19

Commit `499e526` (branch `develop`, sharebook-frontend). Suíte Karma foi de 44 para 80 specs (78 executadas + 2 skip).

- `authentication.service.spec.ts` — login (via `response.success` e via `response.value.authenticated`, e falha), `logout`, `checkTokenValidity` (sem sessão, expirada, válida).
- `user.service.spec.ts` — pub/sub de usuário logado, leitura de `localStorage`, `register` (sucesso/falha), contrato HTTP de `getUserData`/`update`/`getProfile`, `whoAccessed` (extrai userId da sessão) e `unsubscribe`.
- `book.service.spec.ts` — CRUD básico, todas as transições de status (request, cancelRequest, approve, donate, cancelDonation, markAsDelivered, renewChooseDate), montagem condicional de query params de `getAdminBooks`, cache de `getCategoriesShowcase` (hit vs miss) e progresso de `createWithProgress`.

Decisão registrada: os ~20 métodos GET de puro repasse do `book.service` sem lógica condicional ficaram fora de propósito — não protegem regra de negócio, na linha do princípio já em `AGENTS.md` do sharebook-frontend ("poucos testes de alto sinal" em vez de cobertura por checklist). Os outros 14 services sem teste (categoria, contato, etc.) seguem de prioridade menor, cobertos oportunisticamente quando outra tarefa tocar neles.

Validação: `tsc --noEmit` limpo, suíte 78/80 verde (2 skip pré-existentes), `build:ssr` limpo.
