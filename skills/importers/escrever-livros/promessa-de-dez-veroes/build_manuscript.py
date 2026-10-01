#!/usr/bin/env python3
"""Monta o manuscrito consolidado a partir de chapters/.

O manuscrito é SEMPRE gerado por este script e NUNCA editado à mão: se algo está errado
nele, o erro está num capítulo ou aqui. Convenção herdada do pipeline de tradução
(`translated.md` gerado, nunca editado), pelo mesmo motivo — manuscrito editado à mão
diverge silenciosamente dos capítulos e ninguém descobre até o PDF.

RECUSA montar se faltar capítulo: manuscrito incompleto que "monta sem erro" passa pelo
pipeline e vira PDF publicado com buraco.

Uso: python3 build_manuscript.py
"""
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
TITULO = "Promessa de Dez Verões"
SELO = "Sharebook Originals"
ESPERADOS = ["01.md", "02.md", "03.md", "04.md", "05.md"]

SINOPSE = """Catarina construiu uma vida milimetricamente planejada em São Paulo: rotina
impecável, controle financeiro e um noivado morno que prometia estabilidade. Ela aprendeu a
sufocar sua natureza bruxa, escondendo o grimório da família e selando seus poderes em um
selo de contenção. O que ela não esperava era que uma promessa de sangue feita dez anos
atrás, selada em um guardanapo em um bar de praia, voltasse para cobrar a conta.

No dia em que completa vinte e oito anos, Lucas aparece na porta de seu apartamento. O
garoto do passado deu lugar a um homem de olhar denso, ombros largos e uma energia tátil
capaz de quebrar qualquer selo místico. Ele não vem para pedir desculpas pelo silêncio de
uma década; vem para resgatar os sete dias que ela lhe prometeu antes de tentarem fechar
definitivamente as portas do passado e da magia.

Com um prazo de validade implacável e uma tempestade mágica isolando os dois numa casa de
praia em Ilhabela, o contrato entre a razão de Catarina e a obsessão de Lucas rui a cada
toque. Entre poções refeitas e cartas antigas que queimam junto com o passado, Catarina
precisa decidir se volta para a sua vida comum ou se liberta a bruxa que sempre esteve
adormecida dentro dela por um amor que nunca soube morrer."""


def main():
    cap_dir = os.path.join(AQUI, "chapters")
    faltando = [c for c in ESPERADOS if not os.path.exists(os.path.join(cap_dir, c))]
    if faltando:
        print(f"RECUSADO: capítulos faltando: {faltando}", file=sys.stderr)
        return 1

    partes = [f"# {TITULO}", "", f"*{SELO}*", "", "## Sinopse", "", SINOPSE, "", "---", ""]
    for c in ESPERADOS:
        corpo = open(os.path.join(cap_dir, c), encoding="utf-8").read().strip()
        partes += [corpo, "", "---", ""]

    texto = "\n".join(partes).rstrip()
    # O "**FIM**" vive em chapters/05.md, nao e costurado aqui: fonte unica, para o
    # manuscrito e o PDF nunca divergirem (o PDF v1 saiu sem FIM justamente por isso).
    texto = texto[: texto.rfind("---")].rstrip() + "\n"

    # Markdown cru não pode sobrar no caminho do PDF (anti-padrão da skill).
    if re.search(r"\*\*(?!FIM\*\*)", texto.replace("**FIM**", "")):
        print("AVISO: há `**` fora do FIM; confira antes de diagramar.", file=sys.stderr)

    dest = os.path.join(AQUI, "promessa-de-dez-veroes-manuscrito-v1.md")
    open(dest, "w", encoding="utf-8").write(texto)
    print(f"manuscrito: {len(texto.split()):,} palavras, {len(ESPERADOS)} arquivos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
