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

O Sharebook utiliza SSR para SEO e performance. Siga estes padrões para evitar quebras no ambiente Node:

- **Zero `if (isBrowser)` espalhado**: Use o `TransferStateInterceptor` para automatizar o compartilhamento de dados entre servidor e browser.
- **Abstração de Browser APIs**: Nunca use `window`, `localStorage` ou `document` diretamente. Use os serviços:
    - `PlatformService`: Para checar `isBrowser` de forma centralizada.
    - `BrowserStorageService`: Wrapper seguro para storage que não quebra no servidor.
- **Meta Tags**: Garanta que as meta tags de redes sociais (OpenGraph) sejam renderizadas no servidor para correta indexação.
- **Moment-timezone**: Cuidado com importações de `moment-timezone` no ambiente Node; prefira importações ES nativas quando possível.

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
