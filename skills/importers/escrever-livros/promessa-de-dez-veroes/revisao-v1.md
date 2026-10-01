# Revisão editorial — Promessa de Dez Verões

Revisão feita em 2026-10-01 pela sessão Claude Code web, a pedido do Raffa, sobre o rascunho
dele de 2026-10-01. Etapa 1 do fluxo da skill `escrever-livros`: *"resolver repetição, tom e
progressão antes da etapa visual; PDF não corrige texto frouxo."*

- Rascunho original, **intocado**: `rascunho-original-raffa.md`
- Texto revisado: `chapters/01.md` a `05.md`
- Manuscrito consolidado: gerado por `build_manuscript.py`, **nunca editar à mão**

**20 trechos alterados, +12 palavras.** A contagem não é de memória: saiu de um diff
palavra a palavra entre o rascunho e a revisão, justamente para garantir que nenhuma frase
se perdeu por descuido. Reproduza com o script no fim deste arquivo.

---

## 1. Erros de língua (3) — não são opinião

| Onde | Fonte | Revisão | Por quê |
|---|---|---|---|
| Cap. 1 | "se não **vir**..." | "se não **vier**..." | Futuro do subjuntivo de *vir* é *vier*. E estava na fala que carrega o ultimato do Lucas, o pior lugar possível para um deslize. |
| Cap. 1 | "a voz dele tinha engrossado, **ressonando** no meu peito" | "**ressoando**" | *Ressonar* em português é **roncar**. O que se queria é *ressoar*. |
| Cap. 2 | "ansiedade desgovernada **que** começava a vazar" | "desgovernada**,** que começava" | Oração explicativa pede vírgula; sem ela, lê-se como restritiva (existiria outra ansiedade, governada). |

## 2. Continuidade (1) — a mais importante

**Cap. 2, a balsa.** O rascunho dizia:

> "A balsa para Ilhabela estava suspensa. Seguimos para a antiga casa da família dele na
> Feiticeira."

A **Praia da Feiticeira é em Ilhabela**. Se a balsa estava suspensa, os dois não chegam lá —
e o capítulo 4 abre com "os sete dias em Ilhabela", confirmando que estão na ilha. Era
contradição factual, não estilo.

Consertei pelo caminho de menor intervenção, que também é o melhor dramaticamente:

> "**Pegamos a última balsa para Ilhabela antes de a travessia ser suspensa.**"

Isso preserva Ilhabela, preserva a Feiticeira, e **ganha** o isolamento que a sinopse promete:
eles entram e a travessia fecha atrás deles. A alternativa seria mudar a casa para o
continente, o que custaria o nome "Feiticeira" — um presente que o texto não devia devolver.

## 3. Lógica de cena (1)

**Cap. 1, o atraso.** "Faltavam vinte minutos para a meia-noite" e, na porta, ela diz "Você
está atrasado", ele responde "Trinta minutos, para ser exato". Trinta minutos em relação a
quê? O guardanapo não marca hora, só o dia — e ele mesmo argumenta isso duas linhas depois.
A precisão dele ficava sem âncora.

- "— Você está **dez anos** atrasado"
- "— **Dez anos e trinta** minutos, para ser exato"

A piada de precisão dele continua inteira, agora apoiada em algo, e a primeira fala dela
depois de dez anos passa a dizer o que ela sente em vez de marcar relógio.

## 4. Mundo interno: um nome por coisa (4)

O rascunho dava **três nomes ao mesmo feitiço** — "encanto de contenção" (sinopse), "selo"
(cap. 1), "encanto de negação" (cap. 4) — e dois à mesma instituição, "clã" e "Ordem".

| Onde | Fonte | Revisão | Por quê |
|---|---|---|---|
| Cap. 4 | "o encanto de **negação**" | "o **selo de contenção**" | Um nome só, o da sinopse. |
| Cap. 1 | "Renunciei ao **clã**" | "Renunciei à **magia**" | Resolve a tensão com o epílogo, em que ela "se liberta das obrigações da Ordem" e ainda recebe mensagens "da minha família na Ordem" — se tivesse renunciado ao clã dez anos antes, não haveria obrigação a romper. Ela escondeu e selou; não saiu. É o que a sinopse já dizia. |
| Cap. 3 | "ativava um **glifo mágico**" | "acendia uma **runa**" | "Glifo" aparecia uma única vez num livro que fala em runa sete vezes. |
| Cap. 3 | "os dentes roçando **a pele** onde as runas douradas **de bruxa**..." | "roçando **o lugar** onde as runas douradas..." | "Pele" duas vezes na mesma frase, e "runas de bruxa" é redundante — ela é a bruxa. |

**O "clã" sobrevive de propósito** na última fala do Lucas no cap. 4 ("nosso próprio clã"):
ali a palavra é o oposto da Ordem, e o eco com o que ela renunciou é bom.

## 5. Vocabulário e fluência (4)

| Onde | Fonte | Revisão | Por quê |
|---|---|---|---|
| Cap. 3 | "O **sweater** voou" | "O **cardigan** voou" | Ela veste um cardigan no cap. 1. Era a única palavra inglesa crua do livro, e descrevia a peça errada. |
| Cap. 4 | "**Reescrevemos** poções" | "**Refizemos** poções" | Reescreve-se receita, refaz-se poção. |
| Cap. 4 | "na minha **nuca rúnica**" | "na minha nuca, **onde as runas tinham voltado a acender**" | "Nuca rúnica" lê como adjetivo de catálogo; e desdobrar aqui paga, porque é o último toque antes da escolha dela. |
| Cap. 1 | "acabar **da forma exata como** eu **tinha** planejado: uma taça de **vinho** Pinot Noir **semi-cheia**" | "acabar **exatamente como** eu **havia** planejado: uma taça de Pinot Noir **pela metade**" | Quatro arestas na frase de abertura do livro, que é onde o leitor decide se continua. "Vinho Pinot Noir" é redundante; "semi-cheia" é etiqueta de embalagem, e o ponto é o copo largado. |

---

## O que eu NÃO mudei, e precisa da sua decisão

### 1. A sinopse promete uma coisa que o texto não entrega

A sinopse do rascunho diz: *"Entre **cartas antigas e encantamentos que revelam** o verdadeiro
motivo do afastamento..."*. No texto, o motivo é revelado por **fala do Lucas** no cap. 2, e as
cartas aparecem só no cap. 4, já queimadas, fora de cena.

**Ajustei a sinopse**, não o texto — a revelação por diálogo funciona e é mais econômica. A
sinopse no `build_manuscript.py` agora diz "entre poções refeitas e cartas antigas que queimam
junto com o passado", e também passa a nomear Ilhabela.

Se você preferir o contrário — fazer as cartas revelarem o motivo, e o Lucas confirmar —, é
reescrita de cena e eu não faço sem você pedir. Aviso também que **a sinopse de publicação tem
regra própria** (`voice-glossary`, exatamente 3 parágrafos) e eu não li essa skill nesta
sessão: trate a minha como sinopse de trabalho, não como texto de catálogo.

### 2. O antagonista nunca aparece

O pai da Catarina e a Ordem são a força que separou os dois, revelada no cap. 2 — e **nunca
mais voltam**. No epílogo ela "se libertou das obrigações da Ordem" fora de cena, e o Gustavo
fica "horrorizado" também fora de cena.

Para um mini-livro isso é escolha legítima: o foco é o reencontro, não o conflito externo.
Mas é o maior buraco estrutural do texto, e era o que eu desenvolveria se você algum dia
quisesse expandir — uma cena de confronto com o pai valeria mais que qualquer outra adição.
**Não toquei**, porque você pediu revisão e não expansão.

### 3. Escala

2.031 palavras contra ~20 mil do `bruxa-por-acaso`, o projeto de referência da linha. Você
chamou de mini-livro, então presumo que é de propósito — mas isso muda o que o PDF vira
(poucas páginas em A5 4:5) e provavelmente a expectativa de catálogo. Decisão sua, só
registrando.

### 4. Catálogo

O capítulo 3 é cena de sexo explícita, entre adultos e consensual — gênero legítimo, nada a
ajustar no texto. Mas o cadastro precisa da **classificação adulta**, e a categoria dos
Originals de bruxa é **Bruxas & Magia** por decisão sua, registrada na skill.

---

## Como auditar esta revisão

```bash
cd skills/importers/escrever-livros/promessa-de-dez-veroes
python3 - <<'PY'
import re, glob, difflib
o = open("rascunho-original-raffa.md", encoding="utf-8").read()
o = o[o.index("## Capítulo 1"):].replace("**FIM**", "").strip()
r = "\n\n".join(open(f, encoding="utf-8").read().strip() for f in sorted(glob.glob("chapters/*.md")))
n = lambda t: re.sub(r"\s+", " ", re.sub(r"^## .*$", "", t, flags=re.M).replace("---", " ")).strip()
a, b = n(o).split(), n(r).split()
for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
    if tag != "equal":
        print(f"[{tag}] - {' '.join(a[i1:i2])!r}  + {' '.join(b[j1:j2])!r}")
PY
```

Tem de imprimir exatamente os 20 trechos descritos aqui. Se imprimir mais, alguém editou
capítulo sem atualizar este relatório.
