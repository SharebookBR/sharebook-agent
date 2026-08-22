---
name: harness-governance
description: "Auditar e evoluir o harness de conhecimento do Sharebook-agent: validar links, índices, artefatos e metadados de memória; preparar evidência para ciclos de Dream. Use em Dream, revisão de memória, plasticidade, governança cognitiva ou saúde estrutural do corpus. Não use em tarefas comuns de produto."
---

# Harness Governance

Use esta skill para observar e reparar a arquitetura cognitiva. As ferramentas produzem evidência; não promovem, apagam nem reescrevem conhecimento sozinhas.

## Escolher o fluxo

- **Criar memória episódica:** partir de [`assets/episodic-memory-template-v1.md`](assets/episodic-memory-template-v1.md) e seguir o contrato em [`references/episodic-memory-metadata-v1.md`](references/episodic-memory-metadata-v1.md).
- **Validar memória:** executar [`scripts/episodic_memory_metadata.py`](scripts/episodic_memory_metadata.py) nos arquivos novos. Memórias legadas sem frontmatter continuam válidas.
- **Preparar um Dream:** executar [`scripts/dream_report.py`](scripts/dream_report.py) e [`scripts/harness_doctor.py`](scripts/harness_doctor.py) na abertura. O primeiro delimita a safra e agrega uso, misses, fatos, loops e candidatos; o segundo fornece a fotografia estrutural que também deve ser investigada durante o ciclo.
- **Auditar o harness:** executar [`scripts/harness_doctor.py`](scripts/harness_doctor.py). Exit code `1` significa achados, não falha da ferramenta.

## Comandos canônicos

Na raiz de `sharebook-agent`:

```powershell
C:\Users\raffa\AppData\Local\Programs\Python\Python312\python.exe skills/doctrine/harness-governance/scripts/episodic_memory_metadata.py memory/2026-08-20-exemplo.md
C:\Users\raffa\AppData\Local\Programs\Python\Python312\python.exe skills/doctrine/harness-governance/scripts/dream_report.py --repo-root .
C:\Users\raffa\AppData\Local\Programs\Python\Python312\python.exe skills/doctrine/harness-governance/scripts/harness_doctor.py --root .
```

Os dois relatórios também oferecem saída JSON (`--json`) para automação.

## Protocolo do Doctor durante o Dream

O Dream deve tratar cada achado do Doctor como evidência que exige investigação, não como ruído de rodapé:

1. Rodar o Doctor na abertura e preservar a lista de achados da safra.
2. Para cada achado, examinar o arquivo, o alvo esperado, as referências, o histórico Git e o rastro de uso disponível.
3. Classificar o achado como `regressão`, `dívida histórica`, `artefato deliberado` ou `falso positivo`.
4. Corrigir a causa quando for seguro. Dúvida sobre deleção ou uso real exige sonho manual; não autoriza apagar nem ignorar.
5. Em falso positivo, corrigir o detector e adicionar teste que prove o comportamento correto.
6. Rodar o Doctor novamente no fechamento e confrontar a saída com a fotografia de abertura.

Nenhum achado acionável pode atravessar o checkpoint sem resolução ou `open_loop` explícito contendo evidência, motivo do bloqueio e decisão necessária. Uma contagem genérica de achados não satisfaz essa exigência.

## Guardrails

- A prosa continua sendo a memória; metadados são sinais observáveis, não substitutos da experiência.
- O schema v1 é estrito. Evolução do contrato exige nova `schema_version`.
- Não retroajustar memórias legadas só para melhorar métricas.
- Não promover uma ocorrência isolada porque apareceu no relatório.
- Não apagar achados do Doctor sem verificar uso real e aplicar o mandato do `DREAM.md`.
- Dívida preexistente não é sinônimo de achado tolerável; investigar sua causa e seu uso antes de decidir.
- Depois de mudança estrutural, rodar Doctor e testes; comparar a saída final com a fotografia de abertura.

## Testes

- [`scripts/test_episodic_memory_metadata.py`](scripts/test_episodic_memory_metadata.py)
- [`scripts/test_dream_report.py`](scripts/test_dream_report.py)
- [`scripts/test_harness_doctor.py`](scripts/test_harness_doctor.py)

```powershell
C:\Users\raffa\AppData\Local\Programs\Python\Python312\python.exe -m unittest discover -s skills/doctrine/harness-governance/scripts -p "test_*.py" -v
```
