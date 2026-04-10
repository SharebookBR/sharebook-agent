## 🗺️ Roadmap de Evolução
- **North star do produto**: tornar o Sharebook o melhor hub de livros gratuitos do Brasil, combinando escala em digitais, conexão emocional nos físicos e descoberta simples. Referência: `sharebook-agent/missions/maior site de livros do brasil/_plano.md`.
- **Painel de Jobs (v2)**: adicionar status calculado por job (`Saudável`, `Atrasado`, `Com erro`, `Inativo`) com base no intervalo esperado e na última execução registrada.
- **Painel de Jobs (histórico)**: permitir expandir cada job para ver as últimas execuções, com `CreationDate`, `TimeSpentSeconds`, `IsSuccess` e `Details`.
- **Painel de Jobs (diagnóstico)**: destacar melhor os jobs que só enfileiram trabalho (`NewBookGetInterestedUsers`, `NewEbookWeeklyDigest`) e o `MailSender`, deixando claro o fluxo “enfileirou” vs “consumiu fila”.
- **Painel de Jobs (backend)**: criar endpoint dedicado para histórico paginado por job, evitando carregar tudo em um único payload.
- **Painel de Jobs (frontend)**: manter a tela apenas como leitura no primeiro ciclo; qualquer ação manual de executar job ou editar configuração deve ser tratada separadamente e com mais cautela.
- **Dependências e segurança**: reduzir o passivo de vulnerabilidades do projeto, com foco inicial no `sharebook-frontend` e nas dependências legadas de email/runtime que estão aparecendo nos alertas do GitHub e no build.
- **Upgrade de toolchain Angular**: tratar separadamente a modernização do build do `sharebook-frontend` (`@angular-devkit/build-angular` e cadeia associada). Não aceitar PR automática com salto grande de major nesse tooling sem trilha dedicada de upgrade, validação de compatibilidade com Angular 13 e plano explícito de migração.
