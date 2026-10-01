# Capa e ilustrações — Promessa de Dez Verões

Geradas pelo Raffa em IA de imagem e entregues em 2026-10-01. Todas **1122×1402 px**,
proporção **4:5 exata**, que é o preset do miolo (512×640 pt). Nenhuma precisa de
reenquadramento.

PNG somam ~11 MB. O `build_book.py` recomprime em **JPEG q85** antes de inserir no PDF —
a skill registra um livro que foi de 42,8 MB para 7,7 MB com essa conversão, e o limite de
envio no chat é 30 MB.

## Mapa

| Arquivo | Onde entra | Por que esta cena |
|---|---|---|
| `promessa-de-dez-veroes-capa.png` | **capa**, página 1 | Varanda ao pôr do sol com o guardanapo luminoso nas mãos dela. Traz o selo Sharebook Originals embutido. |
| `ilus-01-porta-chuva.png` | antes do **Capítulo 1** | A porta do apartamento, a chuva, a cidade ao fundo, a mão dele no pescoço dela e as runas douradas acendendo — é o momento exato em que o selo do pulso quebra. |
| `ilus-02-casa-tempestade.png` | antes do **Capítulo 2** | A casa da praia à luz de velas, o raio na janela, o mar revolto, e a **runa de ancoragem acesa no antebraço dele** — o detalhe que o capítulo revela. |
| `ilus-03-aparador-runas.png` | antes do **Capítulo 3** | O aparador de madeira, as runas correndo pela pele dela. Casa com a cena como escrita. |
| `ilus-05-varanda-escolha.png` | antes do **Capítulo 4** | Ela de pé na varanda: celular aceso numa mão, aliança solta na palma aberta da outra, runas acesas no antebraço. Ele sentado atrás, esperando sem interromper. A assimetria das mãos conta o capítulo sozinha. |
| `ilus-04-varanda-grimorio.png` | antes do **Epílogo** | Varanda ensolarada, chá, o grimório novo aberto e o **guardanapo emoldurado** com a proteção mágica. Fecha o círculo visual da capa. |

## O Capítulo 4 ganhou ilustração (prompt em `ilus-05-prompt.txt`)

Eu tinha deixado sem, e o Raffa discordou — com razão. A cena escolhida **não é a cama**:
o capítulo é a manhã seguinte, mas pedir quarto ou casal seminu a uma IA restritiva é o
caminho curto para a recusa, e a varanda conta "A Escolha" melhor de qualquer forma.

O gerador acertou de primeira, inclusive dois detalhes que ninguém pediu: a **runa do
antebraço dele repete o desenho de roda da `ilus-02`**, e os props (grimório, xícara azul e
branca, lavanda, lanternas) são os mesmos da capa e da `ilus-04`.

**Recorte aplicado:** veio em 1072×1467 (0,731), fora do 4:5 das outras cinco. Cortados 100 px
do topo, que era folhagem decorativa, e 27 px da base — pouco embaixo de propósito, porque o
grimório e a xícara estão na borda inferior e são o que amarra esta imagem às outras duas de
varanda. Resultado: 1072×1340, proporção 0,800 exata.

**Para o cadastro:** esta é a imagem mais translúcida do conjunto, em plena luz do dia. Não
muda nada no texto nem no pipeline — a classificação adulta já é exigida pelo capítulo 3 —,
mas é a que mais provavelmente apareceria como miniatura de vitrine. Decisão do Raffa.

## Nota de pipeline

O `build_book.py` localiza o ponto de inserção pelo rótulo `CAPÍTULO N`. **O epílogo não tem
número**, então a inserção da `ilus-04` precisa de tratamento próprio quando o build for
copiado de `bruxa-por-acaso/` — conferir se lá o epílogo tinha prancha e como foi resolvido.
