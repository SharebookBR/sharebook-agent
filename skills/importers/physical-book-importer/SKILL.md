---
name: physical-book-importer
description: Cadastra livros físicos no Sharebook usando foto da capa, pesquisa de contexto, frete explícito e API de produção. Use quando o usuário quiser importar ou cadastrar livros impressos, montar sinopses editoriais com base em fontes públicas confiáveis, aprovar os livros em produção e transformar atritos do fluxo em melhorias permanentes.
---

# Sharebook Physical Book Importer

Cadastrar livro físico é parecido com ebook, mas não igual. Esta skill existe para evitar os atalhos errados: não há PDF, a foto da capa pode ser a própria imagem do exemplar, duplicidade é aceitável e o frete precisa ser informado.

## Workflow

1. Ler a capa ou foto do exemplar e confirmar título, autor e editora legíveis.
2. Pesquisar contexto público confiável antes de escrever a sinopse. Priorizar páginas de editora, livraria, acervo ou resenha claramente atribuída.
3. Escrever sinopse de vitrine com no mínimo 3 parágrafos, sexy, tom envolvente e sem inventar fatos que a pesquisa não sustenta.
4. Em sessão manual de PowerShell, se houver vários cadastros seguidos, rodar `python C:\Repos\SHAREBOOK\sharebook-agent\scripts\production\sharebook_refresh_token.py` para renovar o token (o `sharebook_prod_login.ps1` está quebrado — módulo `sharebook_prod_auth` ausente).
5. Antes de cadastrar, consultar `GET /api/Category` e confirmar que a categoria escolhida é folha (`children` vazio). Em caso de homônimo, usar sempre `--category-id`.
6. Cadastrar com `C:\Repos\SHAREBOOK\sharebook-agent\scripts\production\sharebook_prod_book.py create --type Printed --freight-option ... --approve`, preferindo `--synopsis-file` em UTF-8.
7. Validar o retorno publicado com `find-many` ou pelo próprio payload do script.
8. Reflita sobre as fricções nessa sessão e fique a vontade pra melhorar essa skill ou scripts.

## Regras

- Duplicidade de livro físico é aceitável. Não bloquear cadastro só porque já existe exemplar parecido.
- Usar a própria foto da capa do livro como imagem, salvo orientação contrária do usuário.
- Livro físico exige `--freight-option`. Se o usuário disser que paga para todo o Brasil, usar `Country`.
- Não exigir PDF nem tentar forçar o fluxo de ebook em livro impresso.
- Gate de categoria obrigatório: não cadastrar físico em categoria-pai quando houver subcategorias; usar sempre categoria folha (`--category-id`), especialmente em árvores com homônimo (`Drama`, `Aventura` etc.).
- No estado atual do catálogo, tratar `Ficção`, `Tecnologia` e `Drama` como categorias-pai (proibidas como destino final).
- A sinopse final deve ter no mínimo 3 parágrafos e vender a leitura sem virar fanfic.
- Quando o contexto público for fraco, segurar a mão: apoiar-se no subtítulo, orelha, quarta capa ou dados objetivos visíveis, sem completar lacuna no chute.
- Em Windows, preferir `--synopsis-file` em UTF-8 para evitar texto quebrado na CLI.
- O cache permitido do token do Sharebook é o `.env`. Não registrar o valor em memória operacional, logs, skills ou documentação.
- Tratar a execução como treino. Se o fluxo pediu ajuste real no script de produção, incorporar a melhoria em vez de conviver com gambiarra.

## Scripts úteis

- `C:\Repos\SHAREBOOK\sharebook-agent\scripts\production\sharebook_prod_book.py`
  - Hoje opera livro físico e digital.
  - Para físico, usar `create --type Printed --freight-option ...`.
  - Para ebook, usar `create --type Eletronic --pdf-path ...`.
  - Aceita `--synopsis` ou `--synopsis-file`.
  - `find-many --pairs-file` é útil para validar vários cadastros com um único login.
- `C:\Repos\SHAREBOOK\sharebook-agent\scripts\production\sharebook_refresh_token.py`
  - Renova `SHAREBOOK_PROD_ACCESS_TOKEN`, salva no `.env` automaticamente.
  - **Usar este em vez do `sharebook_prod_login.ps1`** — o .ps1 está quebrado (módulo `sharebook_prod_auth` ausente desde 2026-06-11).
- `C:\Repos\SHAREBOOK\sharebook-agent\scripts\web\sharebook_prod_login.ps1`
  - ⚠️ QUEBRADO desde 2026-06-11: `ModuleNotFoundError: No module named 'sharebook_prod_auth'`. Não usar até corrigir.

## Execução sugerida

```powershell
python C:\Repos\SHAREBOOK\sharebook-agent\scripts\production\sharebook_refresh_token.py
```

```powershell
python C:\Repos\SHAREBOOK\sharebook-agent\scripts\production\sharebook_prod_book.py create `
  --type Printed `
  --title "Título do Livro" `
  --author "Nome do Autor" `
  --category-id "<ID_CATEGORIA_FOLHA>" `
  --freight-option Country `
  --synopsis-file "C:\Repos\SHAREBOOK\codex-temp\<slug>\synopsis.txt" `
  --image-path "C:\Users\raffa\Downloads\<foto-da-capa.jpeg>" `
  --approve
```

## Referências

- Ler [workflow.md](references/workflow.md) para o fluxo operacional mínimo e os atritos já conhecidos.
