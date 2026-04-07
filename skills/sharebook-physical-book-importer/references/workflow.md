# Workflow MVP

1. Identificar título, autor e eventuais pistas visuais da categoria a partir da capa.
2. Pesquisar contexto público confiável para sustentar a sinopse.
3. Escolher a categoria menos torta entre as disponíveis no Sharebook.
4. Confirmar com o usuário o alcance do frete quando isso não estiver explícito. Em geral o Raffa paga o frete pro Brasil.
5. Em PowerShell manual, dot-source `C:\REPOS\SHAREBOOK\codex-scripts\sharebook_prod_login.ps1` se houver vários cadastros seguidos.
6. Escrever a sinopse em arquivo UTF-8.
7. Cadastrar com `sharebook_prod_book.py create --type Printed --freight-option ... --approve`.
8. Validar o cadastro final com o retorno do script ou `find-many`.
9. Converter toda dor recorrente em melhoria concreta da skill ou dos scripts.

## Fricções reais já validadas

- O fluxo antigo de `sharebook_prod_book.py` era enviesado para ebook; livro físico precisou de suporte explícito a `--type Printed` e `--freight-option`.
- Para livro físico, a API exige `FreightOption`; sem isso o cadastro falha na validação.
- Foto da capa sozinha nem sempre basta para escrever sinopse forte sem inventar. Pesquisa pública é parte do fluxo, não perfumaria.
- Se a pesquisa pública for fraca, usar formulações honestas e prudentes em vez de preencher lacunas com imaginação.
- Em Windows, texto longo com acento direto na CLI continua sendo uma má ideia. Usar `--synopsis-file`.
