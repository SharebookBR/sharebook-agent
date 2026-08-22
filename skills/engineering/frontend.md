# Frontend Sharebook

Skill operacional para desenvolvimento, manutenção e evolução do `sharebook-frontend` (Angular).

## Quando usar

- Criação ou modificação de componentes, serviços ou pipes no Angular.
- Ajustes de layout, temas (SCSS) ou responsividade.
- Mudança em fluxos de navegação ou integração com a API.
- Diagnóstico de falhas de build ou inconsistências entre ambiente local e produção.

## Design System — Paleta Oficial

**Obrigatório consultar antes de criar ou modificar qualquer elemento visual.**

| Papel | Cor | Uso |
|---|---|---|
| **Primary** | `#29abe2` (azul Sharebook) | Botões padrão, inputs focados, links de ação |
| **Accent** | `#ff4081` (rosa) | Destaque máximo — usar com parcimônia (ex: botão "Receber livro digital") |
| **Warn** | vermelho Material | Erros de formulário, ações destrutivas |

**Regras:**
- Nunca hardcode uma cor sem antes verificar se o papel `primary` ou `accent` já resolve.
- Nunca usar `mat.$indigo-palette` — foi substituído pela paleta `$sharebook-blue`.
- O botão "Doe um Livro" no header usa `#29abe2` via CSS direto — é a referência visual da primary.
- Accent é raro por design. Se tudo grita, nada grita.

**Fonte:** `src/custom-theme.scss` — paleta `$sharebook-blue`, tom 500.

---

## Princípios de UI/UX (Doutrina Sharebook)

- **Cartão > Tabela**: Para listas operacionais (ex: painel do importador), prefira cartões compactos e responsivos. Tabelas são hostis em dispositivos móveis.
- **Smart Sorting**: Automatize a ordenação baseada no status selecionado (ex: fila de espera -> id ASC; concluídos -> data DESC).
- **Busca por ID/Título**: No dashboard, digitar números deve buscar por `id` exato; texto busca por `title` (ILIKE).
- **Feedback de Sucesso**: Em fluxos de publicação ou criação, exibir a miniatura do ativo gerado (ex: capa do livro) no card de conclusão é o melhor feedback visual.
- **Toast de Ação**: Toda ação mutante bem-sucedida (salvar, publicar, atualizar) deve exibir um toast de confirmação via `ToastrService.success('...')`. Nunca fechar silenciosamente um modal ou formulário sem feedback. Para erros, usar `ToastrService.error()` ou exibir inline se o contexto for um formulário com campos. `ToastrService` já está configurado no `AppModule` — apenas injetar no construtor.
- **Inspetor de Metadados**: Nunca exiba JSON bruto para o usuário. Use flattening recursivo e listas zebradas para inspeção humana.

## SSR v2 (Angular Universal)

O Sharebook utiliza Angular 13 Universal + Express (ngExpressEngine) para SSR de SEO e performance. Siga estes padrões para evitar quebras no ambiente Node:

### Princípios gerais

- **Zero `if (isBrowser)` espalhado**: Use o `TransferStateInterceptor` para automatizar o compartilhamento de dados entre servidor e browser.
- **Abstração de Browser APIs**: Nunca use `window`, `localStorage` ou `document` diretamente. Use os serviços:
    - `PlatformService`: Para checar `isBrowser` de forma centralizada.
    - `BrowserStorageService`: Wrapper seguro para storage que não quebra no servidor.
- **Meta Tags**: Garanta que as meta tags de redes sociais (OpenGraph) sejam renderizadas no servidor para correta indexação.
- **Moment-timezone**: Cuidado com importações de `moment-timezone` no ambiente Node; prefira importações ES nativas quando possível.

### Cache integral da home — contrato de 30 minutos

A rota exata `/` usa microcache do HTML SSR completo em `server.ts`, com TTL de 30 minutos e armazenamento em escopo de módulo Node.js.

- `MISS`: uma única renderização Angular consulta as APIs e armazena o HTML final.
- `COALESCED`: acessos simultâneos durante o `MISS` aguardam a mesma Promise; nunca iniciar renders concorrentes para preencher o mesmo cache.
- `HIT`: enviar o HTML armazenado sem inicializar o Angular SSR. Isso precisa produzir zero chamadas a `/api/*` no servidor.
- O HTML cacheado deve preservar o `TransferState` da primeira renderização. Assim, um carregamento direto no navegador também hidrata sem repetir chamadas a `/api/*`.
- Capas em `/Images/*` continuam sendo assets carregados pelo navegador; não confundir esses GETs estáticos com chamadas de dados ou conexões ao Postgres.
- Não ampliar o cache para outras rotas sem decisão explícita. Páginas privadas, personalizadas e respostas diferentes de HTTP 200 não podem entrar no cache público.
- Deploy ou restart naturalmente esvazia o cache. Na expiração, o single-flight garante uma única atualização.

Validação mínima após mudança no fluxo: build SSR, rajada concorrente comprovando `1 MISS + N COALESCED`, acesso posterior `HIT` e navegador headless comprovando zero requests para `https://api.sharebook.com.br/api/*` durante a hidratação do `HIT`.

### SsrCacheService — escopo de módulo, não de classe

**Bug crítico corrigido em 2026-06-11**: O `SsrCacheService` original declarava `private store = new Map()` como propriedade de instância. Angular Universal cria novo contexto de injeção por request → o Map morria a cada requisição → o cache nunca funcionava.

**Fix**: Mover o `_store` para escopo de módulo (fora da classe):
```typescript
// FORA da classe — persiste enquanto o processo Node.js estiver vivo
const _store = new Map<string, { data: any; timestamp: number }>();

@Injectable({ providedIn: 'root' })
export class SsrCacheService {
  get(key: string) { return _store.get(key); }
  set(key: string, data: any) { _store.set(key, { data, timestamp: Date.now() }); }
  // ...
}
```

`providedIn: 'root'` **não é singleton entre requests no SSR** — a injeção de dependências do Angular é recriada por request. A única forma de persistir estado entre requests no mesmo processo Node.js é usar variável de módulo JavaScript.

### TransferState manual em cache hit

Quando um serviço retorna dados cacheados via `of(cached)`, ele **desvia do `HttpClient`** → o `TransferStateInterceptor` nunca roda → o `TransferState` fica vazio → o browser re-fetcha e re-renderiza (perdendo o benefício do SSR).

**Sintoma**: conteúdo aparece igual no HTML SSR, mas o browser faz requests duplicados e pode sobrescrever dados sorteados (ex: categorias do showcase trocando a cada F5).

**Fix**: no cache hit em ambiente servidor, popular o `TransferState` manualmente:
```typescript
import { isPlatformServer } from '@angular/common';
import { TransferState, makeStateKey } from '@angular/platform-browser';

// No método que retorna cache hit:
if (isPlatformServer(this.platformId)) {
  const key = makeStateKey('categories-showcase');
  this.transferState.set(key, cached);
}
return of(cached);
```

A chave deve ser a mesma que o `TransferStateInterceptor` usaria se o `HttpClient` tivesse sido acionado. Validar inspecionando o bloco `<script id="angular-state">` no HTML SSR de produção.

### RESPONSE injection — server.ts

O token `@Inject(RESPONSE)` (usado para setar HTTP status code no SSR) só funciona se `server.ts` passar `RESPONSE` nos providers do `res.render()`:

```typescript
// server.ts — dentro do res.render()
providers: [
  { provide: RESPONSE, useValue: res },
  // ... outros providers
]
```

Sem isso, **todos** os `@Optional() @Inject(RESPONSE)` do app são `null` — HTTP 404 nunca chega ao Googlebot (soft 404). O fix é mínimo e resolve para todos os componentes de uma vez.

### NotFoundPageComponent — 404 real, não redirect

**Não redirecionar para `/404`**. Isso causa soft 404 para crawlers (o URL original retorna 200 com redirect, não 404).

Padrão correto:
- Criar `NotFoundPageComponent`: fonte da verdade visual + `this.response?.status(404)` + SEO meta tags
- `NotFoundComponent` (rota `**`) vira wrapper de 1 linha que renderiza `<app-not-found-page>`
- `BookDetailComponent` e outros componentes que detectam recurso inexistente renderizam `<app-not-found-page>` **no URL original**, sem redirect
- O componente deve ser declarado no `AppModule`

### HomeService showcase — Union para subcategorias

A query de seleção de categorias para o showcase da home filtrava apenas `b.Category.ParentCategoryId == null` (categorias raiz). Categorias como Drama tinham quase todos os ebooks em subcategorias filhas → mostrava 1 livro.

**Fix**: Union entre ebooks com categoria raiz direta e ebooks com categoria filha de categoria raiz:
```typescript
// books query:
.where('b.Category.ParentCategoryId = :categoryId OR b.Category.Id = :categoryId', { categoryId })
```

## Chart.js atrás de `*ngIf`

Quando o `<canvas>` do gráfico vive atrás de `*ngIf="!loading && !error"`, montar o `Chart` em `ngAfterViewInit` corre uma corrida real contra a resposta HTTP: o elemento pode não existir ainda no DOM na primeira tentativa, e o gráfico simplesmente não aparece. Padrão que já se repetiu duas vezes (`analytics-dashboard`, depois `download-logs-dashboard`, 2026-07-24):

- Montar o gráfico em `ngAfterViewChecked` (não `ngAfterViewInit`), guardado por uma flag para não recriar a cada change detection.
- Toda troca de filtro que force o Angular a destruir/recriar o `<canvas>` (mesmo `*ngIf`) também destrói a instância anterior do `Chart.js` — chamar `chart.destroy()` antes de montar de novo dentro do método que recarrega os dados, senão sobra uma instância órfã presa a um canvas que não existe mais.

## Karma/Puppeteer — Chrome ausente no cache

`ChromeHeadless` via Puppeteer pode ter `executablePath()` apontando para um binário que existe só às vezes (baixado, mas some do cache temporário do Windows antes da execução) — o teste falha sem mensagem útil. Fix aplicado em `karma.conf.js`: verificar se o candidato do Puppeteer existe de fato no disco antes de usá-lo; se não existir, usar o Chrome/Edge já instalado no Windows como fallback automático, sem exigir configuração manual por máquina.

## Padrões de Layout

### Container
- Usar `class="container"` para páginas admin — cria margens laterais automáticas e dá respiro em monitores grandes.
- **Nunca** usar `container-fluid` em páginas admin — estica até a borda e fica ilegível em telas largas.
- Referência: importer dashboard usa `class="importer-dashboard container"`.

### Breadcrumb
Padrão obrigatório em todas as páginas admin:
```html
<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a routerLink="/panel">Painel</a></li>
    <li class="breadcrumb-item active" aria-current="page">Nome da Página</li>
  </ol>
</nav>
```
CSS obrigatório para remover o fundo cinza padrão do Bootstrap:
```css
.breadcrumb {
  background: none;
  padding: 0;
  margin: 0;
  font-size: 14px;
}
```
Sem esse CSS o breadcrumb fica com uma caixa cinza/azul que destoa do restante do app.

### Proteção de rota admin
```typescript
// app-routing.module.ts
{
  path: 'admin/minha-pagina',
  component: MinhaPaginaComponent,
  canActivate: [AuthGuardAdmin],
}
```
`AuthGuardAdmin` verifica `user.profile === 'Administrator'` via localStorage.

## Integração com o Backend

### apiEndpoint
O `environment.apiEndpoint` já inclui `/api`:
```
https://api.sharebook.com.br/api
```
Chamadas de serviço devem ser: `${this.config.apiEndpoint}/Controller/Action`  
**Nunca** adicionar `/api` ou `/v1/` na URL — resulta em `apiController` concatenado errado.

### TypeScript — limitações do lib target
O projeto tem `lib` configurado em ES2018 ou anterior. Evitar:
- `Object.fromEntries()` — usar `reduce` como alternativa:
  ```typescript
  array.reduce((acc, x) => { acc[x.key] = x.value; return acc; }, {} as Record<string, T>)
  ```

## Angular Material / CDK — Integração e Sobreposições

### z-index hierárquico

| Camada | z-index | Origem |
|---|---|---|
| Header Sharebook | 1040 | CSS hardcoded |
| CDK overlay (default) | 1000 | Angular Material |
| **Override correto** | **1100** | `custom-theme.scss` |

Fix global obrigatório em `src/custom-theme.scss`:
```scss
.cdk-overlay-container { z-index: 1100; }
```
Sem isso, modais, selects e tooltips ficam atrás do header.

### `::ng-deep` para componentes de terceiros

Usar `::ng-deep` quando o componente gera DOM dinamicamente sem atributo `_ngcontent` (ex: CodeMirror/EasyMDE, Chart.js overlays).

Caso real — CodeMirror no modal editorial:
```scss
::ng-deep .CodeMirror {
  overflow-x: hidden;
  word-wrap: break-word;
}
::ng-deep .CodeMirror-scroll { overflow-x: hidden !important; }
::ng-deep .CodeMirror pre.CodeMirror-line {
  white-space: pre-wrap;
  word-break: break-word;
}
```
`::ng-deep` está deprecated mas é o único caminho correto para content gerado dinamicamente. Isolar com um seletor pai (ex: `.editorial-prompt-dialog__body`) para não vazar para outros componentes.

## Regras Técnicas e Armadilhas

### Design de Modais (Mobile)
- Problema de modal cortado no mobile quase nunca é bug isolado do componente. Suspeitar primeiro de duas causas sistêmicas: `dialog.open(...)` com `minWidth`/larguras fixas incoerentes e override global agressivo em `src/custom-theme.scss` forçando Material dialog para `100vw` sem respeitar internals.
- **Não usar hacks de CSS local**: para consistência, preferir correção estrutural na camada global do Material dialog e depois alinhar a configuração de `dialog.open(...)` nos componentes.
- **Padrão Mobile**: todo modal no celular deve ter largura mobile-safe de forma consistente, sem mistura caótica de `minWidth` fixo por modal. Se precisar ocupar a tela, fazer isso com critério, sem quebrar título, body rolável e footer.
- **Modal com conteúdo expansivo**: usar `max-height: 80vh` + `flex: 1; min-height: 0; overflow-y: auto` no body + `flex-shrink: 0` no footer para garantir que o footer sempre apareça.
- Em legado de modais, endurecer também a estrutura interna: título, ações e scroll precisam ser mobile-safe antes de sair remendando CSS pontual de um componente por vez.

### Sincronia e Build
- **Build Real > Ambiente Local**: O comportamento no ambiente de produção (CI/CD) é a única verdade. Sempre valide se o build passa antes de considerar a tarefa concluída.
- **Branch Desatualizada**: Se encontrar um erro "misterioso" onde o código local não parece refletir a realidade da CI, a suspeita primária deve ser branch local defasada em relação à `master`.
- **Validar Sintaxe**: Em alterações de HTML/JS/SCSS, uma verificação rápida de sintaxe ou build local economiza rodadas de CI falhas.

## Comandos Úteis

```bash
# Rodar lint para garantir padrão de código
npm run lint

# Rodar testes unitários
npm test

# Build de produção local (para validar se não quebra na CI)
npm run build-prod
```

## Amazon Affiliate Button

Tag: `sharebook09-20`. Link dinâmico: `https://www.amazon.com.br/s?k=TITULO+AUTOR&tag=sharebook09-20`

Regras de hierarquia na PDP:
- Livro físico já doado → `mat-flat-button accent` (primário — único CTA da página)
- Ebook disponível ou físico disponível → `mat-stroked-button` (secundário, abaixo do CTA principal)

Sempre: `rel="noopener noreferrer sponsored"` (SEO correto para afiliado). GA event: `amazon_click` com `book_title` + `book_slug`.

Máximo um `mat-flat-button accent` por página — Amazon nunca compete com "Receber livro digital".

## Shelf arrows — visibilidade e estado inteligente

Para controles de scroll horizontal (carrosséis, prateleiras):

- **Usar SVG em vez de Unicode**: caracteres `‹` `›` variam entre fontes e plataformas. Substituir por `<polyline>` SVG com `stroke-width="2.5"`.
- **Estado disabled via HTML**: inicializar a seta esquerda com classe `.shelf-arrow--disabled` direto no HTML (sem `AfterViewInit`). Método `updateArrows(wrapper)` toggle a classe com base em `scrollLeft` vs `scrollWidth`.
- **Eventos**: chamar `updateArrows()` no evento `(scroll)` do track + `setTimeout(400)` após `scrollBy` programático.
- **CSS disabled**: `opacity: 0.22` no hover, `pointer-events: none`.

```html
<button class="shelf-arrow shelf-arrow--left shelf-arrow--disabled">
  <svg><!-- polyline chevron --></svg>
</button>
```

## Hover padrão em botões

```scss
&:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}
```

Aplicar a CTAs em PDPs e cards de ação. Não aplicar em botões inline de formulários ou links de texto.

---

## Referências
- [`sharebook-agent/skills/product-ux/ux-reviewer/SKILL.md`](../product-ux/ux-reviewer/SKILL.md) - Para auditoria crítica de fluxos.
- [`sharebook-agent/skills/product-ux/web-design-reviewer/SKILL.md`](../product-ux/web-design-reviewer/SKILL.md) - Para correção visual e layout.
