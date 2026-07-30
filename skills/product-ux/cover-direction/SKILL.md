---
name: cover-direction
description: Gerar, selecionar, publicar e validar capas diversas do Sharebook com roleta de paleta, famílias visuais e fluxo adaptado à capacidade do agente. Use quando Raffa pedir "roda a roleta", quando precisar criar ou trocar uma capa, revisar direção cromática, evitar repetição na prateleira ou fugir de capa genérica/tech-clean.
---

# Sharebook Cover Direction

Usar direção visual, não improviso.

## Fontes da verdade

- `sharebook-agent/scripts/covers/cover_prompt_from_url.py`
- `sharebook-agent/scripts/covers/cover_roulette.py`
- `sharebook-agent/scripts/covers/prepare_cover.py`
- `sharebook-agent/scripts/covers/INDEX.md`
- `sharebook-agent/scripts/production/sharebook_prod_book.py`

Os scripts mandam nos detalhes mecânicos; esta skill manda na escolha do caminho por capacidade.

## Workflow canônico

Exigir a URL do livro. Sem URL, não inventar roleta.

Antes de rodar, inspecionar as 8 capas recentes quando houver acesso ao catálogo. Se uma linguagem inteira estiver dominando a prateleira, excluir o macrogrupo; se a repetição for pontual, excluir somente a família:

```bash
python3 /data/workspace/sharebook-agent/scripts/covers/cover_prompt_from_url.py \
  "<URL_DO_LIVRO>" \
  --avoid-group "<MACROGRUPO_DOMINANTE>" \
  --avoid-style "<ESTILO_RECENTE>"
```

Sem evidência de repetição recente, omitir as exclusões. A roleta sempre sorteia famílias de macrogrupos distintos entre si.

### Agente com geração de imagem nativa

1. Usar a ferramenta nativa de geração de imagem; não usar `cover_generate.py`.
2. Tratar a saída de `cover_prompt_from_url.py` como briefing. Ela já contém 3 famílias visuais de macrogrupos distintos.
3. Ignorar no gerador a meta-instrução “não gere a imagem ainda” e fazer uma chamada de imagem por família.
4. Gerar **3 capas independentes**. Não misturar famílias, gerar triptych ou prancha.
5. Adaptar o conceito ao livro sem substituir meio, materialidade, iluminação, profundidade ou comportamento cromático sorteados.
6. Preservar literalmente título e autoria.
7. Inspecionar as três e escolher autonomamente a melhor por:
   - legibilidade em miniatura;
   - força conceitual e aderência à sinopse;
   - hierarquia de capa real;
   - fidelidade à paleta;
   - ausência de clichê visual e de estética tech-clean genérica;
   - diversidade em relação às capas recentes;
   - texto correto e ausência de artefatos impeditivos.
8. Se nenhuma passar nos requisitos duros, refazer apenas as candidatas defeituosas antes de publicar.
9. Salvar a escolhida no workspace e prepará-la para upload:

```bash
python3 scripts/covers/prepare_cover.py "<CAPA_NATIVA>" "<CAPA_FINAL.jpg>"
```

O utilitário preserva a proporção e mantém o arquivo abaixo de 800 KB.

10. Resolver o ID pelo livro real e atualizar **pela API**, nunca direto no banco:

```bash
python3 scripts/production/sharebook_prod_book.py update \
  --id "<BOOK_ID>" \
  --image-path "<CAPA_ESCOLHIDA>"
```

11. Validar o livro por GET e a PDP pública: título, capa nova, categoria e CTA devem permanecer íntegros.

O pedido “roda a roleta” com URL autoriza esse fluxo fechado quando o agente possui geração nativa.

### Agente sem geração de imagem nativa

Usar `generate_covers.py`/`cover_generate.py` para gerar múltiplas opções locais e escolher visualmente a melhor. Se o ambiente só puder produzir direção, devolver o prompt completo de `cover_prompt_from_url.py` para geração manual.

Não usar `sharebook_openai_cover.py` ou outra API cobrada sem confirmação explícita do Raffa.

## Gramática cromática durável

A direção usa 4 papéis de cor como âncoras:
- `background`
- `primary`
- `secondary`
- `accent`

Regras:
- sortear explicitamente o `background`, senão a IA tende a cair no neutro por default
- seguir o `palette_behavior` da família visual sorteada
- somente estilos de tinta spot, como serigrafia, devem ficar presos às 4 cores
- fotografia, pintura, neon, 3D e cenas podem derivar tons, luzes, sombras e cores ambientais
- a combinação de cores é sagrada; se quebrar a coerência da paleta-mãe, o modo `ruim_bom` vira só ruim

## Heurística de qualidade

- partir de paletas-mãe coerentes e só depois distribuir os 4 papéis
- não deixar a IA cair no tech-clean genérico
- não usar serigrafia, neon, fotografia ou qualquer outra família como default
- diversidade da prateleira > preferência recorrente do agente
- listar famílias e macrogrupos disponíveis com `cover_roulette.py --list-styles`

## Regra de capacidade

Detectar a capacidade real do agente antes de escolher o gerador. O caminho nativo é preferencial quando disponível; o gerador Python local permanece como fallback importante para outros modelos e habitats.
