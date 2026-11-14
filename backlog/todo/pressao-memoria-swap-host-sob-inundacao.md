# Investigar pressão de memória e swap do host sob inundação SSR

## Escopo

Identificar consumidores de RAM/CPU e a origem do swap I/O sob rajada SSR;
avaliar OpenClaw, browser e processos residentes e decidir se devem sair da
VPS de produção.

## Valor

No V2, apesar de zero 500, houve 10 s de swap I/O acima do limiar; a última
amostra marcou 1.091,1 KiB/s de swap-in e 5.541,1 KiB/s de swap-out. Precisamos
atribuir essa pressão antes de chamar o limite de estável.

## Risco

Profiling e nova carga competem com o site. Exigir origem externa, guardrails,
janela autorizada e retenção segura das amostras.

## Validação

Série por processo/cgroup e host atribui a pressão; nova rajada não tem 10 s
consecutivos acima de 1 MiB/s de swap I/O nem crescimento superior a 300 MiB,
ou há correção documentada e revalidação.

## Relações

- Concluído: `backlog/done/protecao-sobrecarga-ssr.md`.
- Repetição: `teste-carga-ssr-origem-externa.md`.
