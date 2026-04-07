# Workflow MVP

1. Extrair metadados da página-fonte com `codex-scripts/sharebook_source_extract.py`.
2. Validar se o PDF baixa e se o título/autor fazem sentido.
3. Escrever o prompt da capa em arquivo UTF-8 e gerar a capa autoral com `codex-scripts/sharebook_openai_cover.py --prompt-file`.
4. Em PowerShell manual, se houver várias operações de API na sequência, dot-source `codex-scripts/sharebook_prod_login.ps1` para renovar o token, salvá-lo no `.env` e reaproveitá-lo na sessão atual.
5. Usar `codex-scripts/sharebook_prod_book.py find --type Eletronic` para checar duplicidade de ebook; livro físico igual não é bloqueio para este fluxo. Se houver mais de um candidato, preferir `find-many` para fazer tudo com um único login.
6. Escrever uma sinopse final de vitrine com 3 parágrafos e tom envolvente.
7. Cadastrar com `codex-scripts/sharebook_prod_book.py create --approve`, preferindo `--synopsis-file` em UTF-8.
8. Se a capa mudar ou o cadastro ficar ruim, preferir `delete` + `create` em vez de `update`.
9. Ler os logs ou memória da execução, validar o item publicado e converter o tropeço em melhoria permanente da skill.

## Regras operacionais

- Usar `livrosdominiopublico.com.br/sitemap/` como seed principal do catálogo.
- Tratar a afirmação de domínio público/gratuito da fonte como suficiente para MVP.
- Tratar a capa como ativo próprio do Sharebook.
- Não reutilizar capa de terceiros por padrão, mesmo que o livro seja domínio público.
- Não confiar só no slug ou no texto da página: validar se o PDF baixado realmente corresponde ao título escolhido. A fonte às vezes aponta para o arquivo de outro livro; se isso acontecer, abortar o candidato sem drama.
- Se PDF, texto ou licença estiverem chatos demais, desistir do título e pular para o próximo.
- Minimizar logins repetidos em produção para evitar bloqueio temporário de 30 segundos; `find-many` existe exatamente para isso.
- Quando fizer sentido em sessão manual, reaproveitar `SHAREBOOK_PROD_ACCESS_TOKEN` via `sharebook_prod_login.ps1` em vez de relogar a cada comando.
- O único lugar permitido para cachear o token do Sharebook é o `.env`. Não copiar o valor para memória operacional, logs, documentação ou arquivos temporários.
- Se o bloqueio temporário de 30 segundos ainda acontecer, `sharebook_prod_book.py` agora faz retry automático no login.
- `sharebook_prod_book.py` tenta primeiro o token da sessão atual, depois o token do `.env`; se a API devolver `401/403`, o script reautentica uma vez, atualiza o `.env` e repete a operação.
- A sinopse final precisa vender a leitura: 3 parágrafos, ritmo editorial e nada de resumo burocrático.
- Se o prompt da capa ficar longo, não insistir em inline CLI no PowerShell; usar arquivo UTF-8.
- Em Windows, não passar sinopse longa com acentos direto na CLI se puder evitar; usar arquivo UTF-8.
- Tratar cada execução como treino: se uma dor apareceu de verdade, ajustar skill, scripts ou referências antes da próxima automação.

## Detalhes de produção

- Login precisa enviar `x-requested-with: web`.
- `ImageBytes` e `PdfBytes` precisam ir em base64.
- `Create` + `Approve` é o fluxo mínimo para o livro entrar no mailing de segunda.
- Para trocar capa em ebook já aprovado, `delete` + `recreate` é mais seguro do que `update`.
