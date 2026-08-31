# Missão — Dependências e Segurança

## Objetivo
Reduzir o passivo de vulnerabilidades do projeto e modernizar a toolchain de desenvolvimento.

## Escopo Inicial
- **Vulnerabilidades**: Focar inicialmente no `sharebook-frontend` e nas dependências legadas de email/runtime detectadas pelo GitHub/Dependabot.
- **Upgrade de toolchain Angular**: Tratar a modernização do build do `sharebook-frontend` (`@angular-devkit/build-angular` e associados).
- **Regra de Ouro**: Não aceitar PR automática com salto grande de major sem plano explícito de migração e validação de compatibilidade com Angular 13.

## Status — 2026-08-31

Primeira fatia segura aplicada no `sharebook-frontend`, sem salto de major do Angular:

- removido `base64-img`, dependência direta sem uso no código que puxava cadeia crítica (`ajax-request`, `file-system`, `utils-extend`);
- atualizado `express` de `4.22.1` para `4.22.2`;
- adicionados `overrides` npm para transitivos corrigíveis sem migração de framework:
  - `minimatch@3.1.4`;
  - `postcss@8.5.23`;
  - `ws@8.21.0`.

Resultado do `npm audit --omit=dev`:

- antes: 23 advisories (`2 low`, `3 moderate`, `11 high`, `7 critical`);
- depois: 8 advisories (`2 low`, `4 high`, `2 critical`);
- advisories restantes ficam presos em Angular 13 / Angular Universal 13:
  - `@angular/common`;
  - `@angular/compiler`;
  - `@angular/core`;
  - `@angular/localize` / `@babel/core`;
  - `@angular/platform-server`;
  - `@nguniversal/common`;
  - `@nguniversal/express-engine`.

Validação da fatia:

- `npm test -- --watch=false`: `44 SUCCESS`;
- `npm run build:ssr`: passou com warnings legados de CommonJS/budget/CSS.

Próxima decisão: tratar o bloco Angular/Universal como migração planejada ou mitigação explícita de SSR, não como `npm audit fix --force`.
