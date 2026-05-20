# Search Console Access

## Objetivo
Dar acesso programático do agente ao Google Search Console para consultar queries, cliques, impressões, CTR, posição média e páginas por busca do Sharebook.

## Contexto
- GA4 já ficou acessível via service account `sharebook-analytics-agent@sharebook-a174c.iam.gserviceaccount.com`.
- No Search Console, a UI falhou ao adicionar essa mesma service account como usuário, com erro de e-mail não encontrado.
- A propriedade de domínio `sharebook.com.br` já foi confirmada via TXT no DNS.
- Hipótese principal: bug/limitação semelhante ao do GA4, mas ainda sem confirmação de endpoint/API viável para bypass programático.

## Próximos passos
1. Verificar se existe endpoint/API do Search Console para gestão de usuários/permissões ou grant equivalente.
2. Se existir, tentar bypass por API com a service account atual.
3. Se não existir ou falhar, cair para plano B com OAuth de usuário humano para leitura do Search Console.
4. Quando o acesso estiver resolvido, criar script/skill de consulta para:
   - queries
   - páginas
   - CTR
   - posição média
   - cruzamento query -> landing page

## Observações
- Não tratar isso como urgente agora.
- Prioridade atual continua sendo importação de livros e enriquecimento do catálogo.
