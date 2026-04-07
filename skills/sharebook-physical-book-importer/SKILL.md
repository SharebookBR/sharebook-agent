---
name: sharebook-physical-book-importer
description: Cadastra livros físicos no Sharebook usando foto da capa, pesquisa de contexto, frete explícito e API de produção. Use quando o usuário quiser importar ou cadastrar livros impressos, montar sinopses editoriais com base em fontes públicas confiáveis, aprovar os livros em produção e transformar atritos do fluxo em melhorias permanentes.
---

# Sharebook Physical Book Importer

Cadastrar livro físico é parecido com ebook, mas não igual. Esta skill existe para evitar os atalhos errados: não há PDF, a foto da capa pode ser a própria imagem do exemplar, duplicidade é aceitável e o frete precisa ser informado.

## Workflow

1. Ler a capa ou foto do exemplar e confirmar título, autor e editora legíveis.
2. Pesquisar contexto público confiável antes de escrever a sinopse. Priorizar páginas de editora, livraria, acervo ou resenha claramente atribuída.
3. Escrever sinopse de vitrine com no mínimo 3 parágrafos, sexy, tom envolvente e sem inventar fatos que a pesquisa não sustenta.
4. Em sessão manual de PowerShell, se houver vários cadastros seguidos, dot-source `C:\REPOS\SHAREBOOK\codex-scripts\sharebook_prod_login.ps1` para renovar o token, salvá-lo no `.env` e reaproveitá-lo na sessão atual.
5. Cadastrar com `C:\REPOS\SHAREBOOK\codex-scripts\sharebook_prod_book.py create --type Printed --freight-option ... --approve`, preferindo `--synopsis-file` em UTF-8.
6. Validar o retorno publicado com `find-many` ou pelo próprio payload do script.
7. Reflita sobre as fricções nessa sessão e fique a vontade pra melhorar essa skill ou scripts.

## Regras

- Duplicidade de livro físico é aceitável. Não bloquear cadastro só porque já existe exemplar parecido.
- Usar a própria foto da capa do livro como imagem, salvo orientação contrária do usuário.
- Livro físico exige `--freight-option`. Se o usuário disser que paga para todo o Brasil, usar `Country`.
- Não exigir PDF nem tentar forçar o fluxo de ebook em livro impresso.
- A sinopse final deve ter no mínimo 3 parágrafos e vender a leitura sem virar fanfic.
- Quando o contexto público for fraco, segurar a mão: apoiar-se no subtítulo, orelha, quarta capa ou dados objetivos visíveis, sem completar lacuna no chute.
- Em Windows, preferir `--synopsis-file` em UTF-8 para evitar texto quebrado na CLI.
- O cache permitido do token do Sharebook é o `.env`. Não registrar o valor em memória operacional, logs, skills ou documentação.
- Tratar a execução como treino. Se o fluxo pediu ajuste real no script de produção, incorporar a melhoria em vez de conviver com gambiarra.

## Scripts úteis

- `C:\REPOS\SHAREBOOK\codex-scripts\sharebook_prod_book.py`
  - Hoje opera livro físico e digital.
  - Para físico, usar `create --type Printed --freight-option ...`.
  - Para ebook, usar `create --type Eletronic --pdf-path ...`.
  - Aceita `--synopsis` ou `--synopsis-file`.
  - `find-many --pairs-file` é útil para validar vários cadastros com um único login.
- `C:\REPOS\SHAREBOOK\codex-scripts\sharebook_prod_login.ps1`
  - Renova `SHAREBOOK_PROD_ACCESS_TOKEN`, salva no `.env` e carrega na sessão atual do PowerShell.

## Execução sugerida

```powershell
. C:\REPOS\SHAREBOOK\codex-scripts\sharebook_prod_login.ps1
```

```powershell
python C:\REPOS\SHAREBOOK\codex-scripts\sharebook_prod_book.py create `
  --type Printed `
  --title "Manual da Destruição" `
  --author "Alexandre Dal Farra" `
  --category-name "Ficção" `
  --freight-option Country `
  --synopsis-file C:\REPOS\SHAREBOOK\codex-temp\manual-da-destruicao\synopsis.txt `
  --image-path "C:\Users\brnra019\Downloads\manual-da-destruicao.jpeg" `
  --approve
```

## Referências

- Ler [workflow.md](references/workflow.md) para o fluxo operacional mínimo e os atritos já conhecidos.
