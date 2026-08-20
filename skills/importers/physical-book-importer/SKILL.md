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
8. **Definir o facilitador do livro.** O `create` não faz isso e o livro nasce com `UserIdFacilitator` NULL — ver a regra abaixo. Sem esse passo o cadastro está incompleto, mesmo com a página pública no ar.
9. Reflita sobre as fricções nessa sessão e fique a vontade pra melhorar essa skill ou scripts.

## Regras

- **Livro físico sem facilitador quebra os jobs de lembrete. Cadastro só termina com facilitador definido.**
  - `POST /api/Book` não tem campo de facilitador — o `CreateBookVM` simplesmente não expõe `UserIdFacilitator`. Não existe jeito de nascer certo pela criação; é sempre um segundo passo.
  - Quem aceita o campo é o `PUT /api/Book/{id}` (`UpdateBookVM.UserIdFacilitator`). Use `--facilitator-id` no `sharebook_prod_book.py`: no `create` ele encadeia o PUT logo depois de aprovar, no `update` ele troca o facilitador e confere o resultado por GET antes de retornar.
  - **Essa flag depende do backend com a correção do `ImageSlug` (`12368a2`) deployado.** Antes dela, todo PUT sem imagem nova apagava a capa do livro — o `UpdateBookVM` não carrega `ImageSlug` e o service copiava o nulo por cima. Se o deploy ainda não rodou, definir o facilitador pelo admin do site em vez do script.
  - Na dúvida sobre quem é o facilitador de um livro doado pelo próprio Raffa: é ele mesmo.
  - **Incidente de 20/08/2026** — o livro físico "A volta", cadastrado em 26/07 por esta skill, chegou ao `ChooseDate` com 50 interessados e `UserIdFacilitator` NULL. O job `ChooseDateReminder` monta o e-mail lendo `book.UserFacilitator.Name` sem proteção e estourou `NullReferenceException`. Como `GenericJob.HasWork()` só para quando existe um `JobHistory` **de sucesso**, o job foi reexecutado a cada 5 minutos por 11 horas: **138 execuções falhas**, 100+ alertas no Rollbar (itens `#2936`/`#2937`) e o lembrete de escolha do ganhador nunca enviado. Destravou no minuto em que o facilitador entrou no banco.
  - O estrago é maior que um job: `LateDonationNotification` e `RemoveBookFromShowcase` leem o facilitador do mesmo jeito. Um livro sem facilitador é uma bomba-relógio de três gatilhos, e cada um deles abre seu próprio loop de retentativa.
  - Os três livros de 26/07 eram, juntos, os **únicos** livros físicos do catálogo sem facilitador. O buraco é do fluxo desta skill, não do catálogo.
- **A unidade de cadastro é a unidade da doação, não a unidade da foto.** Vários exemplares fotografados juntos não significam automaticamente vários anúncios — podem ser um kit doado como um só. Se a foto for ambígua sobre isso, confirmar com o usuário antes de decidir entre cadastros separados ou um kit único; quando for kit, deixar isso explícito no título e na sinopse (ex: "Kit com 2 volumes").
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
  - `--facilitator-id` funciona no `create` (encadeia o PUT depois de aprovar) e no `update` (troca o facilitador e confere por GET). Adicionado em 20/08/2026 — **validação ponta a ponta ainda pendente**, ver a regra de facilitador acima.
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
  --facilitator-id "<ID_DO_FACILITADOR>" `
  --approve
```

Para corrigir um livro já cadastrado que ficou sem facilitador:

```powershell
python C:\Repos\SHAREBOOK\sharebook-agent\scripts\production\sharebook_prod_book.py update `
  --id "<ID_DO_LIVRO>" `
  --facilitator-id "<ID_DO_FACILITADOR>"
```

## Referências

- Ler [workflow.md](references/workflow.md) para o fluxo operacional mínimo e os atritos já conhecidos.
