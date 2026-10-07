# Laboratorio Sharebook - observabilidade .NET por 24h

## Estado

Aberto em 2026-10-07, apos diagnostico read-only da VPS confirmar folga de CPU/disco e atencao moderada em RAM/swap.

Escopo deliberadamente temporario: montar um laboratorio de aproximadamente 24 horas para medir o comportamento real do runtime .NET do Sharebook em producao. A pergunta inicial nao e "o que otimizar?", e sim:

> Como o runtime .NET do Sharebook realmente se comporta durante um dia normal?

Nada de otimizacao antes dos dados.

## Stack inicial

Subir somente:

```text
Sharebook API (.NET)
  -> OpenTelemetry
  -> OpenTelemetry Collector
  -> Prometheus
  -> Grafana
```

Containers novos esperados:

- Grafana: visualizacao;
- Prometheus: armazenamento temporario das metricas;
- OpenTelemetry Collector: coleta e encaminhamento.

Fora do escopo inicial:

- Loki;
- Tempo;
- tracing detalhado;
- ingestao ampla de logs.

Logs e tracing podem entrar em uma segunda janela, se a pergunta mudar de comportamento do runtime para correlacao entre metricas, logs e traces.

## Baseline antes de instalar

Guardar o estado atual para comparacao posterior:

| Metrica | Baseline observado |
| --- | --- |
| CPU | 93-97% idle |
| Load average | 1.39 / 1.08 / 0.57 |
| RAM usada | 2.6 GiB |
| RAM disponivel | 4.3 GiB |
| Swap usada | 1.8 GiB / 4.0 GiB |
| Disco | 63 GiB / 196 GiB |
| Sharebook API RAM | 277.5 MiB |
| Sharebook API CPU | ~0.15% |

A swap ja em 1.8 GiB merece atencao especial. O laboratorio deve medir tambem se a propria observabilidade aumenta pressao de memoria ou swap.

## Metricas do host

Monitorar:

- CPU total;
- load average;
- RAM usada e disponivel;
- swap utilizada;
- atividade de swap-in e swap-out;
- disco utilizado;
- I/O de disco;
- CPU e RAM por container.

Pergunta operacional:

> Quanto custa manter a observabilidade ligada?

## Metricas do .NET

### Managed heap

Acompanhar o tamanho do heap gerenciado ao longo do tempo. O padrao de serrote e esperado; o importante e reconhecer mudancas de comportamento, crescimento sustentado ou pausas anormais.

### Allocation rate

Medir quantos bytes por segundo o Sharebook esta alocando. Essa e uma das metricas centrais para investigar objetos temporarios, strings, DTOs, buffers, boxing e padroes de alocacao evitavel.

### Gen0, Gen1 e Gen2

Monitorar quantidade e frequencia das collections. O padrao esperado e Gen0 muito mais frequente que Gen1, e Gen2 bem menos frequente. Gen2 frequente demais vira sinal de investigacao.

### Tempo gasto em GC

Medir quanto do tempo de execucao esta sendo consumido pelo coletor. Relacionar, quando possivel:

```text
allocation rate -> GC collections -> GC pause -> latencia
```

### LOH

Se a instrumentacao disponivel expuser, acompanhar tambem Large Object Heap. Procurar crescimento sustentado, oscilacao significativa ou criacao frequente de objetos grandes.

## Metricas da API

Coletar junto das metricas de runtime:

- requests por segundo;
- duracao das requests;
- p50;
- p95;
- p99;
- erros;
- CPU do processo;
- memoria do processo.

Objetivo: permitir perguntas do tipo:

> O p99 piorou as 14:32. Houve Gen2, pressao de GC, aumento de allocation rate ou pressao de memoria no mesmo periodo?

Correlacao nao prova causalidade, mas aponta onde investigar.

## Dashboard

Primeiro procurar um dashboard Grafana pronto e decente para .NET/OpenTelemetry/Prometheus.

Se a experiencia for boa, criar um dashboard proprio:

```text
Sharebook - .NET Bike Management Dashboard

1. Sharebook API
   RPS, p50, p95, p99, errors

2. .NET memory
   managed heap, allocation rate, LOH

3. GC
   Gen0, Gen1, Gen2, pause time

4. Host e containers
   CPU, RAM, swap, disco, I/O, consumo da propria observabilidade
```

Esse dashboard deve permitir ver literalmente os conceitos estudados no Pro .NET Bike Management: heap, allocation rate, GC, pausas, latencia e custo operacional no mesmo painel.

## Janela do experimento

Rodar durante 24 horas reais de producao.

Durante a janela:

- nao fazer otimizacoes;
- nao alterar pooling;
- nao mexer em `Span`;
- nao sair cacando boxing;
- nao mudar configuracoes de GC;
- nao ajustar query, cache ou infraestrutura por intuicao;
- observar primeiro.

O objetivo da janela e formar uma linha de base confiavel. Qualquer mudanca durante o periodo contamina a leitura.

## Perguntas depois das 24 horas

Ao final do laboratorio, sentar com os graficos e responder:

- Qual e o allocation rate normal do Sharebook?
- Com que frequencia acontecem Gen0, Gen1 e Gen2?
- Quanto tempo o processo passa fazendo GC?
- Existe pressao relevante sobre o LOH?
- O heap retorna para um patamar estavel depois das collections?
- Existe correlacao entre GC e p95/p99?
- Quanto a stack de observabilidade custou de CPU/RAM/I/O?
- A swap mudou significativamente?
- Existe algum indicio concreto de que vale otimizar memoria?

Resultado excelente tambem pode ser:

> O Sharebook esta saudavel. Nao vamos otimizar nada agora.

Nesse caso, `ArrayPool`, pooling, `Span`, evitar boxing e tecnicas semelhantes deixam de ser receitas procurando onde serem aplicadas e continuam como ferramentas para quando houver dor real.

## Guardrails

- Retencao curta, idealmente apenas o suficiente para a janela de 24h.
- Scrape interval conservador.
- Evitar metricas de alta cardinalidade.
- Limitar containers da stack quando possivel, especialmente memoria.
- Nao expor Grafana/Prometheus publicamente sem protecao.
- Registrar comandos e configuracoes aplicadas para desmontagem limpa.

## Criterios de sucesso

- Stack sobe sem derrubar ou degradar perceptivelmente o Sharebook.
- Dashboard mostra metricas de host, containers, API e runtime .NET.
- Depois de 24h, existe leitura objetiva de:
  - baseline real de CPU/memoria da API;
  - allocation rate;
  - comportamento de Gen0/Gen1/Gen2;
  - tempo gasto em GC;
  - padrao de heap gerenciado;
  - impacto da observabilidade em CPU/RAM/swap/disco.
- Decisao registrada ao final:
  - desmontar tudo;
  - manter stack minima;
  - evoluir para logs/traces com Loki/Tempo;
  - abrir tarefas especificas de otimizacao.
  - nao otimizar nada porque o sistema esta saudavel.

## Riscos

- A observabilidade interferir nas medicoes, principalmente por RAM, swap, I/O ou scrape agressivo.
- Prometheus crescer em disco se retencao ficar solta.
- Loki/Tempo entrarem cedo demais e ampliarem ruido operacional.
- Dashboard bonito induzir otimizacao prematura sem hipotese clara.

## Recomendacao inicial

Comecar com Grafana + Prometheus + OpenTelemetry Collector.

Nao iniciar com Loki e Tempo. Para o primeiro laboratorio, a pergunta e runtime .NET, memoria, GC e latencia. Logs e traces entram depois, se os dados mostrarem necessidade.

## Validacao

1. Registrar baseline pre-instalacao.
2. Subir a stack em escopo temporario.
3. Confirmar que Sharebook API continua saudavel.
4. Confirmar que a stack mostra metricas de runtime .NET.
5. Acompanhar impacto da propria stack por 24h.
6. Registrar achados e decisao final.
7. Desmontar ou formalizar a stack minima, conforme decisao.
