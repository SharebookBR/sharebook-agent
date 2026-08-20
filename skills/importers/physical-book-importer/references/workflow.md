# Workflow MVP

1. Identificar título, autor e eventuais pistas visuais da categoria a partir da capa.
2. Pesquisar contexto público confiável para sustentar a sinopse.
3. Escolher a categoria menos torta entre as disponíveis no Sharebook.
4. Confirmar com o usuário o alcance do frete quando isso não estiver explícito. Em geral o Raffa paga o frete pro Brasil.
5. Em PowerShell manual, se houver vários cadastros seguidos, renovar o token com `python C:\Repos\SHAREBOOK\sharebook-agent\scripts\production\sharebook_refresh_token.py`. Não usar `sharebook_prod_login.ps1`: o módulo de autenticação esperado por ele está ausente.
6. Escrever a sinopse em arquivo UTF-8.
7. Cadastrar com `scripts/production/sharebook_prod_book.py create --type Printed --freight-option ... --approve`.
8. Validar o cadastro final com o retorno do script ou `find-many`.
9. Definir o facilitador do livro (o `create` não define, e sem ele os jobs de lembrete quebram).
10. Converter toda dor recorrente em melhoria concreta da skill ou dos scripts.

## Fricções reais já validadas

- O fluxo antigo de `sharebook_prod_book.py` era enviesado para ebook; livro físico precisou de suporte explícito a `--type Printed` e `--freight-option`.
- Para livro físico, a API exige `FreightOption`; sem isso o cadastro falha na validação.
- Foto da capa sozinha nem sempre basta para escrever sinopse forte sem inventar. Pesquisa pública é parte do fluxo, não perfumaria.
- Se a pesquisa pública for fraca, usar formulações honestas e prudentes em vez de preencher lacunas com imaginação.
- Em Windows, texto longo com acento direto na CLI continua sendo uma má ideia. Usar `--synopsis-file`.
- O cadastro parece completo bem antes de estar: página pública no ar, imagem certa, categoria folha, e ainda assim sem facilitador. A conta chega semanas depois, no `ChooseDate`, quando o job de lembrete estoura em produção — foi o que aconteceu em 20/08/2026 com "A volta". A validação de cadastro só é honesta se olhar o `UserIdFacilitator` junto com o resto.
