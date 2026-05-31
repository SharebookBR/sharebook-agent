---
name: sharebook-cover-direction
description: Direção visual e prompt de capas do Sharebook com roleta cromática, papéis `background`/`primary`/`secondary`/`accent` e geração de prompt a partir da URL do livro. Use quando Raffa pedir "roda a roleta", quando precisar montar prompt de capa, revisar direção cromática ou evitar capa genérica/tech-clean.
---

# Sharebook Cover Direction

Usar direção visual, não improviso.

## Fonte da verdade

- `sharebook-agent/scripts/covers/cover_prompt_from_url.py`
- `sharebook-agent/scripts/covers/cover_roulette.py`
- `sharebook-agent/scripts/covers/INDEX.md`

Se a skill divergir dos scripts, os scripts mandam.

## Workflow canônico

Quando Raffa disser "roda a roleta" ou "roda a roleta de estilos", exigir URL do livro e rodar:

```bash
python3 /data/workspace/sharebook-agent/scripts/covers/cover_prompt_from_url.py "<URL_DO_LIVRO>"
```

O script já:
- lê título, autor e sinopse da página do livro
- sorteia direção cromática pela roleta
- devolve prompt pedindo 3 conceitos distintos antes de gerar imagem

Sem URL, não inventar roleta.

## Gramática cromática durável

A direção usa 4 papéis de cor padrão:
- `background`
- `primary`
- `secondary`
- `accent`

Regras:
- sortear explicitamente o `background`, senão a IA tende a cair no neutro por default
- `accent` é termo aceito e deve ser usado pouco
- 4 papéis funcionam melhor do que paleta solta
- a combinação de cores é sagrada; se quebrar a coerência da paleta-mãe, o modo `ruim_bom` vira só ruim

## Heurística de qualidade

- partir de paletas-mãe coerentes e só depois distribuir os 4 papéis
- evitar explicação extra quando os nomes dos papéis já bastam
- não deixar a IA cair no tech-clean genérico
- o próximo gargalo natural, depois da harmonia, é diversidade insuficiente de paletas e schemes

## Preferência operacional do habitat

Para capa de livro, priorizar geração no ChatGPT web quando o objetivo for qualidade final superior.

Esta skill organiza a direção e o prompt. Ela não obriga gerar a imagem localmente.
