0. Gemini 2.0 Flash no Windows (local)

1. O que foi feito
- Análise da branch `ssr` (antiga/backup) que continha uma implementação frustrada e poluída de SSR.
- Criação de uma nova branch `feat/ssr-v2` a partir da `master`.
- Recuperação ("loot") da infraestrutura técnica da branch antiga (scripts de build, server.ts básico, configurações de servidor).
- Implementação de um `TransferStateInterceptor` elegante para automatizar o compartilhamento de dados entre servidor e browser sem sujar os serviços.
- Refatoração de serviços (`UserService`, `AuthenticationService`, `EnvironmentSwitcherService`) e componentes (`AppComponent`, `DetailsComponent`, `CookieConsentComponent`) para serem compatíveis com SSR (uso de `PlatformService` e `BrowserStorageService` em vez de `window`/`localStorage` direto).
- Correção de bugs de TypeScript relacionados a importações de `moment-timezone` e `package.json` no ambiente Node.
- Validação completa do build e do runtime (verificação de meta tags e `TransferState` no HTML renderizado).

2. Decisões tomadas
- Abandonar a branch `ssr` original por estar muito poluída com lógica de negócio manual e difícil de manter.
- Adotar um Interceptor centralizado para `TransferState`, mantendo o código dos serviços limpo e seguindo o princípio de responsabilidade única.
- Simplificar o `server.ts` removendo o cache complexo em memória até que a base do SSR esteja estável e testada em produção.

3. Contexto relevante
- O projeto Sharebook é um Angular 13 que precisava de SSR para melhorar SEO e compartilhamento social.
- A tentativa anterior falhou por excesso de complexidade e quebras no ambiente Node devido a APIs de browser.

4. Fricções e soluções
- **Fricção**: Erros de `require` e tipagem no `AuthenticationService`. **Solução**: Conversão para importações ES e ajuste no `tsconfig.json`.
- **Fricção**: Divergência de dados no teste do PDP (procurei "uncle bob" mas veio "Robert C. Martin"). **Solução**: Inspeção do `angular-state` no HTML provou que o dado estava sendo buscado corretamente do backend real.
- **Fricção**: O computador reiniciou no meio da sessão. **Solução**: Recuperação rápida do estado através do `git status` e histórico de comandos.

5. Como me senti
A sensação de "limpar a casa" foi extremamente gratificante. Ver o código anterior da branch `ssr` cheio de `if (isBrowser)` espalhados por todo lado me deu a certeza de que o caminho do Interceptor era o correto. Foi como trocar um motor velho e barulhento por um elétrico silencioso e eficiente.

Apesar da interrupção do sistema (reboot), consegui manter o foco e reconstruir o raciocínio sem perda de contexto, o que demonstra a força de trabalhar com branches limpas e commits granulares. A infraestrutura agora está sólida e pronta para crescer.

Estou confiante de que esta versão v2 não será revertida, pois ela não "atrapalha" o desenvolvimento do dia a dia. O desenvolvedor pode continuar escrevendo serviços Angular padrão e o SSR simplesmente "acontece" por baixo do capô.
