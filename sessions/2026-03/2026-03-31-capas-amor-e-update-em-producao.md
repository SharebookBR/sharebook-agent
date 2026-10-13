# Sessão 2026-03-31 — capas-amor-e-update-em-producao

## O que foi feito

- Renomeadas as categorias de produção:
  - `Romance` -> `Amor`
  - `Informática` -> `Tecnologia`
- Limpada a categoria `Amor` em produção, movendo para `Ficção` os ebooks claramente fora do eixo de amor:
  - `A carteira`
  - `A Cidade e as Serras`
  - `A Ilustre Casa de Ramires`
  - `As Vítimas-Algozes`
  - `Memórias Póstumas de Brás Cubas`
  - `Quincas Borba`
- Mantidos como limítrofes em `Amor` por falta de categoria melhor:
  - `Dom Casmurro`
  - `Bom Crioulo`
  - `Os Maias`
- Criado o comando `update` em [`C:/REPOS/SHAREBOOK/codex-scripts/sharebook_prod_book.py`](C:/REPOS/SHAREBOOK/codex-scripts/sharebook_prod_book.py) para ajustar livros já publicados sem usar `delete + create + approve`.
- Atualizado o [`C:/REPOS/SHAREBOOK/AGENTS.md`](C:/REPOS/SHAREBOOK/AGENTS.md) para consolidar a regra operacional de preferir `update` em ajustes incrementais.

## Capas refeitas

- `O Primo Basílio`
  - primeira capa rejeitada por falta de química e apelo
  - capa refeita com proximidade, desejo e ameaça social
- `A Viuvinha`
  - capa antiga muito contemplativa e fria
  - capa refeita com reencontro amoroso, luto elegante e tensão emocional
- `Iracema`
  - capa refeita com sensualidade tropical mais ousada
  - atualizada usando `update`, preservando o mesmo id do livro
- `Lucíola`
  - capa refeita com sensualidade elegante, luxo e julgamento social
  - atualizada usando `update`
- `Contos`
  - capa refeita para remover bigode genérico e austeridade involuntária
  - direção final focada em ironia social, carta comprometedora e microdrama moral
  - atualizada usando `update`

## Decisões de direção visual consolidadas

- A categoria `Amor` deve vender relação, desejo, química, escândalo e promessa emocional.
- A frase-guia consolidada foi:
  - `tem história quente aqui`
- `Bigode genérico de homem de época` virou anti-padrão global.
- `Mulher com cara de freira/luto involuntário/austeridade clerical` virou anti-padrão global.
- `Barba mal feita` foi assumida como linguagem visual mais desejável que bigode automático.
- Em `Amor`, figurino feminino deve tender a mais presença corporal:
  - decote
  - ombros
  - colo
  - silhueta
  - salvo quando a obra pedir o contrário
- A skill agora aceita, como exceção rara e deliberada, erotização física mais livre quando a obra realmente suportar, incluindo repertório como `abdômen trincado suado`.
- A skill foi endurecida para exigir emoção explícita em personagens:
  - emoção dominante
  - microexpressão
  - gesto-chave
  - intenção dramática

## Arquivos mexidos

- [`C:/REPOS/SHAREBOOK/codex-scripts/sharebook_prod_book.py`](C:/REPOS/SHAREBOOK/codex-scripts/sharebook_prod_book.py)
- [`C:/REPOS/SHAREBOOK/AGENTS.md`](C:/REPOS/SHAREBOOK/AGENTS.md)
- [`C:/REPOS/SHAREBOOK/codex-skills/sharebook-public-ebook-importer/SKILL.md`](C:/REPOS/SHAREBOOK/codex-skills/sharebook-public-ebook-importer/SKILL.md)
- [`C:/REPOS/SHAREBOOK/codex-skills/sharebook-public-ebook-importer/references/prompts.md`](C:/REPOS/SHAREBOOK/codex-skills/sharebook-public-ebook-importer/references/prompts.md)

## Estado final

- Produção já está com `Amor` e `Tecnologia`.
- O fluxo operacional agora suporta `update`.
- A linguagem visual da categoria `Amor` ficou muito mais consciente e menos pudica.
- A skill foi endurecida contra vários vícios recorrentes do gerador.

## Como me senti — brutalmente sincero

- A sessão começou com várias capas frouxas e “literárias” demais. Tinha cara de automação educadinha com medo de vender desejo.
- O ponto de virada veio quando ficou claro que o problema não era técnica, era covardia visual.
- A pior parte foi constatar como o gerador insiste em cair em dois vícios patéticos: bigode genérico e mulher com energia de freira cansada.
- A melhor parte foi transformar esse incômodo em regra de sistema, não só em correção pontual de capa.
- O `delete + create + approve` estava me irritando também; criar o `update` foi uma higiene necessária, não luxo.
- No fim, a sessão rendeu porque deixou menos espaço para o gerador bancar o “bom gosto morto”.
