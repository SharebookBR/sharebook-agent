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
| `ilus-04-varanda-grimorio.png` | antes do **Epílogo** | Varanda ensolarada, chá, o grimório novo aberto e o **guardanapo emoldurado** com a proteção mágica. Fecha o círculo visual da capa. |

## O Capítulo 4 fica sem ilustração

Não é lacuna: o projeto de referência `bruxa-por-acaso` tem 6 ilustrações para 9 capítulos
mais epílogo. O capítulo 4 é o da escolha, quase todo diálogo na cama, e vem logo depois da
ilustração mais forte do conjunto — abrir sem imagem dá respiro antes do epílogo.

Se o Raffa quiser uma quinta, a cena óbvia é o celular na mesa de cabeceira com as mensagens
da Ordem e a aliança ao lado: é o objeto que carrega a decisão.

## Nota de pipeline

O `build_book.py` localiza o ponto de inserção pelo rótulo `CAPÍTULO N`. **O epílogo não tem
número**, então a inserção da `ilus-04` precisa de tratamento próprio quando o build for
copiado de `bruxa-por-acaso/` — conferir se lá o epílogo tinha prancha e como foi resolvido.
