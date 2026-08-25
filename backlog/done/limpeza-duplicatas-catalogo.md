# Limpeza de duplicatas no catálogo

## Regra editorial

- Vários exemplares físicos do mesmo livro são legítimos.
- Um exemplar físico e uma versão digital da mesma obra também são legítimos.
- Só é duplicata indevida haver mais de um livro digital da mesma obra e edição.
- Título igual, isoladamente, não prova duplicidade: autor, edição e conteúdo precisam ser comparados.

## Auditoria de produção — 23/08/2026

Entre 1.068 livros digitais ativos, a auditoria dos títulos repetidos encontrou:

- 127 grupos apenas com exemplares físicos — preservados.
- 32 grupos com físicos e um único digital — preservados.
- `Contos` e `Obras Completas` com autores diferentes — preservados.
- Duas edições/adaptações distintas de `Os Músicos de Bremen` — preservadas após comparação dos PDFs.
- Uma duplicata digital real: `Eu e Outras Poesias`, de Augusto dos Anjos.

## Correção executada

- Registro canônico preservado: `019d4848-f697-7d17-9392-aa8b4f942b5f`, slug `eu-e-outras-poesias`.
- Registro redundante preservado para rollback, mas alterado de `Available` para `Canceled`: `019da401-c249-7f73-a260-9b8d59218f2f`.
- O slug redundante `eu-e-outras-poesias_copy1` responde `301` para o canônico antes da desativação do registro.
- Nenhuma linha e nenhum PDF foram apagados.

Durante a auditoria também foram corrigidos dois tipos de colisão de PDF, sem relação com duplicidade editorial:

- `Apostila Linguagem C old school` deixou de apontar para o PDF de C++.
- Os volumes 1, 3 e 4 de `The Art of High Performance Computing` receberam PDFs próprios; o volume 2 já apontava para o arquivo correto.
- Os quatro arquivos oficiais foram gravados em chaves S3 novas e validados por tamanho e SHA-256. Os objetos antigos foram mantidos para rollback.

## Validação final

- Zero pares digitais ativos com o mesmo título e autor normalizados.
- Zero caminhos de PDF compartilhados entre livros digitais ativos.
- Redirect público testado no domínio real e destino canônico respondendo `200`.

## Pendências separadas

- [A colisão de slugs dos volumes HPC foi corrigida](corrigir-colisao-slugs-hpc.md): são livros distintos, não duplicatas.
- [Dedupe preventivo no importer](../todo/dedupe-preventivo-importer.md): impedir reintrodução sem bloquear exemplares físicos ou edições digitais legítimas.
