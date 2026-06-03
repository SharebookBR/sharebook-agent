# Guia Técnico de Correção de UI/UX

Este guia contém as melhores práticas para resolver problemas comuns de design e layout em projetos web.

## 🛠️ Layout e Controle de Transbordamento (Overflow)
Muitos problemas ocorrem quando o conteúdo é maior que o container.
- **Evite o Scroll Horizontal**: Garanta que os containers não excedam a largura do viewport.
  ```css
  .overflow-hidden { overflow-x: hidden; }
  ```
- **Dimensionamento de Flexbox**: Use `min-width: 0` em itens flex para evitar que eles quebrem o layout ao conter strings longas ou imagens grandes.
- **Classes Úteis**: No Bootstrap 4, use classes utilitárias como `mw-100` e `w-100` para controlar imagens e vídeos.

## ✍️ Tipografia e Alinhamento
- **Truncamento de Texto**: Use `.text-truncate` para evitar que títulos longos quebrem o layout.
- **Quebra de Palavra Agressiva**: Para URLs longas em colunas pequenas:
  ```css
  .text-break { word-wrap: break-word; overflow-wrap: break-word; }
  ```
- **Alinhamento de Ícones**: Garanta que os ícones (FontAwesome, Material Icons) estejam centralizados verticalmente em relação ao texto usando `align-items-center`.

## 🎨 Acessibilidade e Contraste
- **Níveis de Contraste**: Garanta que o texto atenda aos padrões WCAG AA (pelo menos 4.5:1).
- **Estados de Foco**: Melhore os anéis de foco do Bootstrap para navegação via teclado:
  ```css
  button:focus-visible, a:focus-visible { outline: 2px solid #007bff; outline-offset: 2px; }
  ```

## 🐛 Depuração Rápida
- **Visualizar Bordas**: Adicione temporariamente para encontrar problemas de alinhamento:
  ```css
  * { outline: 1px solid red !important; }
  ```
- **Detectar Overflow no Console**:
  ```javascript
  document.querySelectorAll('*').forEach(el => { if (el.scrollWidth > el.clientWidth) console.log('Horizontal overflow:', el); });
  ```
