# Recuperar a suíte de testes do frontend

## Problema

Em 26/08/2026, a execução completa de `npm test` no `sharebook-frontend` terminou com 69 testes executados, 22 sucessos e 47 falhas.

Isso não equivale a 47 defeitos de produto. Muitas falhas são cascatas de setup, principalmente `No provider for TransferState` em specs que instanciam o `BookService`; há também expectativas antigas de UI, como configuração de modal divergente do comportamento atual.

## Escopo

- Identificar as poucas causas-raiz que derrubam vários testes.
- Corrigir providers e setups compartilhados dos specs.
- Atualizar expectativas comprovadamente obsoletas.
- Investigar separadamente qualquer falha funcional real que permanecer depois da recuperação da infraestrutura de testes.
- Não desabilitar, pular ou enfraquecer testes apenas para obter verde.
- Remover sem apego testes que não protegem regra, contrato, regressão ou comportamento relevante.
- Colocar `npm test` no pipeline automatizado como gate obrigatório antes de deploy.

## Regra de valor

Teste não é patrimônio só porque já existe. Deve permanecer quando protege pelo menos um destes pontos:

- regra de negócio;
- contrato entre componentes ou com a API;
- regressão real que já ocorreu ou tem risco plausível;
- comportamento complexo, condicional ou difícil de validar manualmente;
- requisito de acessibilidade ou navegação importante para o usuário.

Testes tautológicos, frágeis por detalhe cosmético ou que apenas confirmam que o mock devolveu o que o próprio teste configurou podem ser removidos sem substituição. Cobertura numérica não compensa uma suíte barulhenta. O objetivo é confiança para entregar, não um museu de specs.

Quando um teste falhar, a pergunta é primeiro **“qual valor ele protege?”**. Se a resposta for nenhum, remover é manutenção — não perda de qualidade.

## Pipeline

A recuperação só produz valor durável quando a suíte roda sozinha. O pipeline deve:

- instalar as dependências de forma reproduzível;
- executar `npm test` em modo headless;
- falhar antes do deploy quando um teste relevante falhar;
- manter o build de produção/SSR como gate separado;
- não permitir bypass silencioso por `fdescribe`, `fit`, `xdescribe`, `xit` ou configuração equivalente.

## Critério de pronto

- `npm test` termina com exit code zero.
- Todos os testes unitários mantidos por seu valor passam.
- `npm run build:ssr` continua passando.
- Testes sem valor foram removidos deliberadamente, sem apego a contagem ou cobertura cosmética.
- Nenhum teste relevante foi silenciado para maquiar falha.
- O pipeline executa a suíte automaticamente e bloqueia regressões antes do deploy.

## Evidência inicial

- Comando: `npm test`.
- Resultado em 26/08/2026: `TOTAL: 47 FAILED, 22 SUCCESS`.
- Falha dominante observada: `NullInjectorError: No provider for TransferState!`.
- Falha distinta observada: spec de `RequestedsComponent` ainda espera `minWidth: 450`, enquanto o componente usa configuração responsiva.
