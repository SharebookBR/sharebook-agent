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
- **Inspetor de Metadados**: Nunca exiba JSON bruto para o usuário. Use flattening recursivo e listas zebradas para inspeção humana.

## SSR v2 (Angular Universal)

O Sharebook utiliza SSR para SEO e performance. Siga estes padrões para evitar quebras no ambiente Node:

- **Zero `if (isBrowser)` espalhado**: Use o `TransferStateInterceptor` para automatizar o compartilhamento de dados entre servidor e browser.
- **Abstração de Browser APIs**: Nunca use `window`, `localStorage` ou `document` diretamente. Use os serviços:
    - `PlatformService`: Para checar `isBrowser` de forma centralizada.
    - `BrowserStorageService`: Wrapper seguro para storage que não quebra no servidor.
- **Meta Tags**: Garanta que as meta tags de redes sociais (OpenGraph) sejam renderizadas no servidor para correta indexação.
- **Moment-timezone**: Cuidado com importações de `moment-timezone` no ambiente Node; prefira importações ES nativas quando possível.

## Regras Técnicas e Armadilhas

### Design de Modais (Mobile)
- **Não usar hacks de CSS local**: Para garantir consistência em todo o app, use o **Override Global** no arquivo `src/style/custom-theme.scss`.
- **Padrão Mobile**: Todo modal no celular deve ter 100% de largura (`width: 100% !important`) com padding reduzido de `15px` para maximizar a legibilidade.

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
npm run build -- --prod
```

## Referências
- [`sharebook-agent/skills/product-ux/sharebook-ux-reviewer/SKILL.md`](../product-ux/sharebook-ux-reviewer/SKILL.md) - Para auditoria crítica de fluxos.
- [`sharebook-agent/skills/product-ux/web-design-reviewer/SKILL.md`](../product-ux/web-design-reviewer/SKILL.md) - Para correção visual e layout.
