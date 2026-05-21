# Checklist de Design & UI - Sharebook

Este guia serve para auditar o frontend do Sharebook (Angular 13, Bootstrap 4, Angular Material).

## 🕵️ Critérios de Auditoria

### 1. Responsividade (Bootstrap 4)
- **Grid**: Use classes `col-12`, `col-md-x`, `col-lg-x` para layouts fluidos.
- **Margens/Paddings**: Use as classes utilitárias do Bootstrap (`mt-3`, `mb-2`, `p-2`) em vez de estilos inline quando possível.
- **Quebras**: Verifique se elementos não transbordam em dispositivos móveis.

### 2. Consistência Visual
- **Botões**: Use `mat-flat-button` do Angular Material como padrão para CTAs primários.
- **Cores**: Siga o tema do projeto (`primary`, `accent`, `warn`).
- **Sentence Case**: Títulos e labels de botões devem estar em *sentence case* (ex: "Entrar para solicitar" e não "Entrar Para Solicitar").

### 3. Acessibilidade (A11y)
- **Contraste**: Garanta que o texto seja legível contra o fundo.
- **Alt Text**: Imagens de livros devem ter um `alt` significativo.
- **Foco**: Elementos interativos devem ser navegáveis via teclado.

### 4. Microcopy & Tom
- **Feedback**: Mensagens de sucesso devem usar `ngx-toastr` e tom positivo.
- **Erro**: Nunca mostre código técnico de erro para o usuário. Use mensagens que orientem a ação.
- **Estados Vazios**: Quando não houver livros em uma categoria, convide o usuário para a vitrine principal.

## 🚀 Workflow de Revisão
1. **Inspecione o Código**: Busque padrões de strings ou classes inconsistentes com `grep_search`.
2. **Avalie o Contexto**: A mudança respeita o tom acolhedor e simples?
3. **Corrija Cirurgicamente**: Aplique `replace` apenas onde necessário, mantendo as convenções do projeto.
