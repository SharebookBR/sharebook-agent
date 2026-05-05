# Etapa 07 - SEO técnico com SSR no frontend

## Objetivo
Melhorar indexação orgânica e qualidade do HTML entregue nas páginas públicas do Sharebook, começando pelas rotas com maior retorno de SEO.

A tese é simples:
- metadata client-side ajuda, mas não basta
- a página de livro é o ativo SEO mais valioso
- SSR deve entrar de forma seletiva, não como dogma aplicado ao app inteiro

---

## Diagnóstico resumido

### Estado atual
- Frontend em Angular 13 SPA puro
- Deploy estático via Nginx
- SEO atual já cobre:
  - `title`
  - `meta description`
  - `og:*`
  - `twitter:*`
  - `canonical`
  - `JSON-LD` em parte das páginas

### Limitação central
O conteúdo crítico nasce depois do boot da SPA. Para crawler, isso é pior do que HTML inicial já renderizado.

### Rotas públicas com maior ganho esperado
1. `/livros/:slug`
2. `/categorias/:slug`
3. `/categorias/:parentSlug/:slug`
4. `/livros-digitais/novidades`
5. `/`
6. `/buscar/:criteria` (baixa prioridade, possível no futuro)

---

## Achados técnicos da auditoria

### Bloqueadores de prontidão para SSR
- `AppConfigModule` depende de `EnvironmentSwitcherService`, que depende de `localStorage`
- `JwtInterceptor` acessa `localStorage` diretamente
- `AuthenticationService` e `UserService` assumem browser
- `ErrorInterceptor` usa `location.reload()`
- múltiplos componentes usam `window`, `document`, `navigator` sem guarda de plataforma
- deploy atual é estático, incompatível com SSR real

### Código browser-only espalhado
Pontos que precisam de blindagem:
- `window.scrollTo`
- `window.open`
- `window.location.pathname`
- `document.createElement`
- `navigator.clipboard`
- `localStorage`
- `canvas-confetti`
- Google Analytics via `ga(...)`
- cookie consent

### Conclusão técnica
SSR é viável, mas a base atual não está SSR-ready. Primeiro precisa de uma faxina cirúrgica para separar browser-only do que precisa renderizar no servidor.

---

## Estratégia recomendada

### Princípio
Adotar **SSR incremental nas páginas públicas de alto valor**, sem tentar renderizar tudo no servidor.

### O que NÃO fazer primeiro
- Reescrever o frontend inteiro
- Migrar de framework antes de provar retorno
- SSR global em rotas privadas e administrativas
- Priorizar busca antes de página de livro

---

## Arquitetura alvo
- Angular com SSR habilitado
- runtime Node para render server-side
- Nginx como reverse proxy
- cache para páginas públicas
- área autenticada continua funcional, mas não orienta a arquitetura de SEO

---

## Plano de implementação

## Fase 1 - Preparação da base
Objetivo: tornar o app seguro para SSR.

### Backlog
1. Criar camada de abstração para browser APIs
   - `PlatformService` ou equivalente
   - `BrowserStorageService`
   - helpers com `isPlatformBrowser`

2. Refatorar `AppConfigModule`
   - remover dependência estrutural de `localStorage`
   - usar config SSR-safe por environment/runtime

3. Blindar providers globais
   - `JwtInterceptor`
   - `ErrorInterceptor`
   - `AuthenticationService`
   - `UserService`
   - guards

4. Blindar comportamentos browser-only
   - analytics
   - cookie consent
   - confetti
   - clipboard
   - `window.open`
   - scroll manual
   - leitura de pathname no search input

### Critério de pronto
- bootstrap principal não depende estruturalmente de browser globals
- rotas públicas conseguem inicializar em ambiente server
- providers globais não quebram o render

---

## Fase 2 - Prova de conceito com página de livro
Objetivo: provar valor na rota com maior retorno.

### Escopo
- habilitar SSR
- renderizar `/livros/:slug`

### Requisitos
O HTML inicial da página de livro deve sair do servidor já contendo:
- `<title>` correto
- `meta description`
- `canonical`
- `og:*`
- `twitter:*`
- JSON-LD
- título, autor, categoria e sinopse no corpo HTML

### Observações
- a rota pública deve funcionar bem sem depender de estado autenticado
- preferir degradar recursos de usuário a quebrar render

### Critério de sucesso
Um `curl` na URL de livro deve retornar HTML útil, não apenas shell vazia da SPA.

---

## Fase 3 - Deploy SSR de produção
Objetivo: tornar a solução operacional.

### Backlog
1. Novo Dockerfile com runtime Node
2. Nginx como reverse proxy
3. cache de assets e estratégia para páginas públicas
4. healthcheck e logging mínimo
5. fallback controlado para erro de API/render

### Critério de sucesso
- produção estável
- páginas públicas renderizadas no servidor
- área autenticada sem regressão grave

---

## Fase 4 - Expansão seletiva
Ordem recomendada:
1. `/categorias/:slug`
2. `/categorias/:parentSlug/:slug`
3. `/livros-digitais/novidades`
4. `/`
5. `/buscar/:criteria` apenas se houver motivo forte

---

## Prioridades

### P0 - bloqueadores
- config SSR-safe
- storage/browser abstraction
- guards/interceptors SSR-safe
- blindagem de browser-only

### P1 - POC
- Angular Universal
- SSR em `/livros/:slug`
- validação do HTML inicial

### P2 - produção
- Dockerfile SSR
- Nginx proxy
- cache
- healthcheck/logs

### P3 - expansão
- categorias
- novidades
- home
- busca, se fizer sentido

---

## Riscos

### 1. Complexidade de auth contaminar o SSR
Mitigação: tratar página pública como primeira classe e degradar dependências de usuário.

### 2. Deploy ficar mais frágil
Mitigação: assumir desde o início que SSR muda o runtime e exige operação própria.

### 3. Angular 13 morder
Mitigação: provar valor cedo na rota de livro antes de ampliar escopo.

### 4. API lenta degradar SEO
Mitigação: cache e fallback controlado.

---

## Definição de sucesso
O projeto só conta como sucesso se:
1. a página de livro entregar HTML útil sem JS
2. metadata correta vier no source inicial
3. deploy SSR ficar estável
4. fluxo autenticado não implodir

Sem isso, é só maquiagem técnica cara.
