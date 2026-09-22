# Manutencao Autonoma de Producao - Rollbar + OpenClaw

> **Status: proposta de arquitetura operacional.**
> O objetivo e permitir autonomia real em producao sem trocar revisao humana obrigatoria por fe cega no agente. A confianca deve morar no harness: validacao automatica, observabilidade, reversibilidade e historico de tentativas.

## Objetivo

Criar um fluxo autonomo capaz de detectar incidentes em producao, investigar a causa, implementar uma correcao, validar, realizar deploy e acompanhar o resultado em producao.

O humano atua como supervisor por excecao, e nao como etapa obrigatoria do fluxo.

> "A confianca nao esta no agente. Esta no harness."

## Fluxo

```text
Rollbar detecta incidente
  |
OpenClaw recebe webhook
  |
Investiga erro e contexto
  |
Identifica provavel causa
  |
Implementa correcao
  |
Executa harness de validacao
  |
Valido?
  |-- nao -> aborta + notifica
  |
 sim
  |
Commit + deploy
  |
Observa producao
  |
Saudavel?
  |-- nao -> rollback -> notifica -> nova investigacao
  |
 sim
  |
encerra + notifica
```

## Deteccao

O Rollbar continua responsavel por detectar e agregar erros.

Inicialmente, disparar automacao para eventos relevantes:

- novo erro em producao;
- erro reativado;
- aumento anormal na taxa de ocorrencias.

Evitar enviar cada ocorrencia individual ao agente.

## Investigacao

O OpenClaw recebe o incidente e utiliza o contexto disponivel para investigar:

- mensagem e stack trace;
- aplicacao e componente afetado;
- codigo-fonte;
- commits e alteracoes recentes;
- deploy atual;
- incidentes relacionados;
- telemetria disponivel.

O agente deve registrar sua hipotese de causa antes de realizar alteracoes.

## Correcao autonoma

Quando houver confianca suficiente na causa identificada, o agente pode:

1. modificar o codigo;
2. adicionar ou alterar testes;
3. executar build;
4. executar testes automatizados;
5. executar validacoes do harness;
6. criar commit;
7. realizar deploy.

Nao existe aprovacao humana obrigatoria ou code review manual no fluxo normal.

## Harness

O harness e a principal camada de seguranca.

Uma alteracao somente pode chegar a producao quando passar pelas validacoes automaticas definidas para o projeto:

- build;
- testes unitarios;
- testes de integracao;
- testes de regressao;
- lint ou analise estatica;
- smoke tests;
- health checks;
- validacoes especificas do dominio.

O harness deve evoluir continuamente conforme novos modos de falha forem descobertos.

## Observacao pos-deploy

Deploy bem-sucedido nao significa incidente resolvido.

Apos cada correcao, iniciar uma janela de observacao utilizando metricas reais de producao. Observar pelo menos:

- ocorrencia do erro original;
- surgimento de novos erros;
- error rate global;
- disponibilidade;
- latencia;
- health checks;
- metricas especificas do componente alterado.

Comparar, quando possivel, os indicadores antes e depois do deploy.

## Rollback automatico

Caso as metricas indiquem regressao durante a janela de observacao:

```text
Deploy
  |
Regressao detectada
  |
Rollback automatico
  |
Producao estabilizada
  |
Resultado da tentativa e registrado
  |
OpenClaw recebe o novo contexto
  |
Nova investigacao
```

Uma tentativa que falhou nao deve ser simplesmente descartada. O agente deve saber:

- qual alteracao realizou;
- qual hipotese estava tentando validar;
- quais testes passaram;
- quais metricas pioraram;
- por que ocorreu rollback.

Esse historico passa a fazer parte da proxima investigacao.

## Reversibilidade

A autonomia deve considerar o impacto da operacao.

Operacoes reversiveis podem possuir alto grau de autonomia:

- alteracao de codigo;
- commit;
- deploy;
- configuracao versionada;
- rollback.

Operacoes potencialmente irreversiveis devem possuir protecoes adicionais no harness:

- migrations destrutivas;
- exclusao ou alteracao massiva de dados;
- storage;
- DNS;
- secrets;
- pagamentos;
- recursos externos.

A solucao preferencial e criar guardrails automaticos, nao introduzir aprovacao humana no fluxo normal.

## Notificacao

O responsavel recebe o resultado do processo, nao uma solicitacao de aprovacao.

Exemplo de resolucao:

```text
Incidente detectado

Erro:
NullReferenceException em /books

Causa:
Regressao introduzida no commit abc123.

Acao:
Correcao implementada e publicada.

Validacao:
- Build
- Testes
- Smoke tests 14/14
- Health checks
- Rollbar sem novas ocorrencias

Deploy:
def456

Status:
RESOLVIDO AUTOMATICAMENTE
```

Exemplo de regressao:

```text
Correcao rejeitada pelo harness

Deploy:
def456

Problema:
Error rate aumentou apos o deploy.

Acao:
Rollback automatico executado.

Producao:
Estavel.

Status:
NOVA INVESTIGACAO INICIADA
```

## MVP

Primeira versao:

```text
Rollbar -> Webhook -> OpenClaw -> Investigacao -> Patch -> Testes -> Deploy -> Observacao -> Rollback automatico -> Notificacao
```

Priorizar inicialmente incidentes:

- de producao;
- claramente associados ao codigo;
- reproduziveis;
- com correcoes reversiveis.

## Principio arquitetural

O objetivo nao e construir um agente que nunca erre.

O objetivo e construir um sistema no qual o agente possa agir autonomamente porque suas acoes sao validadas, observadas e reversiveis.

> "Agent autonomy + strong harness + production feedback + automatic rollback."

