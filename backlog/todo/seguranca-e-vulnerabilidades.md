# Missão — Dependências e Segurança

## Objetivo
Reduzir o passivo de vulnerabilidades do projeto e modernizar a toolchain de desenvolvimento.

## Escopo Inicial
- **Vulnerabilidades**: Focar inicialmente no `sharebook-frontend` e nas dependências legadas de email/runtime detectadas pelo GitHub/Dependabot.
- **Upgrade de toolchain Angular**: Tratar a modernização do build do `sharebook-frontend` (`@angular-devkit/build-angular` e associados).
- **Regra de Ouro**: Não aceitar PR automática com salto grande de major sem plano explícito de migração e validação de compatibilidade com Angular 13.
