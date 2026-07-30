---
name: cover-direction
description: Gerar, selecionar, publicar e validar capas do Sharebook com roleta cromática e fluxo adaptado à capacidade do agente. Use quando Raffa pedir "roda a roleta", quando precisar criar ou trocar uma capa, revisar direção cromática ou evitar capa genérica/tech-clean.
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

Usar `cover_prompt_from_url.py` para extrair título, autor e sinopse e sortear a direção:

```bash
python3 /data/workspace/sharebook-agent/scripts/covers/cover_prompt_from_url.py "<URL_DO_LIVRO>"
```

### Agente com geração de imagem nativa

1. Usar a ferramenta nativa de geração de imagem; não usar `cover_generate.py`.
2. Tratar a saída de `cover_prompt_from_url.py` como briefing. Ignorar no gerador a meta-instrução “não gere a imagem ainda”: conceber internamente 3 direções e fazer uma chamada de imagem por direção.
3. Gerar **3 capas independentes**. Não gerar triptych ou prancha.
4. Tornar os conceitos estruturalmente distintos, não meras variações de layout.
5. Preservar literalmente título e autoria.
6. Inspecionar as três e escolher autonomamente a melhor por:
   - legibilidade em miniatura;
   - força conceitual e aderência à sinopse;
   - hierarquia de capa real;
   - fidelidade à paleta;
   - ausência de clichê visual e de estética tech-clean genérica;
   - texto correto e ausência de artefatos impeditivos.
7. Se nenhuma passar nos requisitos duros, refazer apenas as candidatas defeituosas antes de publicar.
8. Salvar a escolhida no workspace e prepará-la para upload:

```bash
python3 scripts/covers/prepare_cover.py "<CAPA_NATIVA>" "<CAPA_FINAL.jpg>"
```

O utilitário preserva a proporção e mantém o arquivo abaixo de 800 KB.

9. Resolver o ID pelo livro real e atualizar **pela API**, nunca direto no banco:

```bash
python3 scripts/production/sharebook_prod_book.py update \
  --id "<BOOK_ID>" \
  --image-path "<CAPA_ESCOLHIDA>"
```

10. Validar o livro por GET e a PDP pública: título, capa nova, categoria e CTA devem permanecer íntegros.

O pedido “roda a roleta” com URL autoriza esse fluxo fechado quando o agente possui geração nativa.

### Agente sem geração de imagem nativa

Usar `generate_covers.py`/`cover_generate.py` para gerar múltiplas opções locais e escolher visualmente a melhor. Se o ambiente só puder produzir direção, devolver o prompt completo de `cover_prompt_from_url.py` para geração manual.

Não usar `sharebook_openai_cover.py` ou outra API cobrada sem confirmação explícita do Raffa.

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

## Regra de capacidade

Detectar a capacidade real do agente antes de escolher o gerador. O caminho nativo é preferencial quando disponível; o gerador Python local permanece como fallback importante para outros modelos e habitats.
