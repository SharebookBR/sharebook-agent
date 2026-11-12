# Observabilidade do onboarding por e-mail

## Estado

Prioridade 2 desde 2026-11-12, por decisão do Raffa.

## Objetivo

Medir o efeito real da jornada fixa de cinco e-mails de onboarding sem depender do GA4: etapas enfileiradas, aberturas rastreáveis e cliques nos CTAs, com uma tela administrativa de acompanhamento.

## V1

1. Criar no PostgreSQL um registro por etapa da jornada, vinculado a `OnboardingJourney`.
2. Registrar quando cada etapa foi enfileirada, a primeira abertura rastreável e o primeiro clique de cada CTA.
3. Inserir um pixel de imagem 1×1 nos templates, apontando para endpoint público com token opaco e assinado.
4. Trocar os CTAs dos templates por endpoint público de redirect: registrar clique, responder `302` para o destino real.
5. Criar painel **Onboarding** no admin, com recortes de 7, 30 e 90 dias, funil geral e tabela por etapa/coorte.

## Métricas do painel

- Jornadas iniciadas, concluídas, canceladas por bounce/descadastro e atrasadas.
- Por e-mail: enfileirados, aberturas rastreáveis, taxa de abertura, cliques, CTR e CTA clicado.
- Coortes por data de cadastro para comparar a evolução semanal do fluxo.

## Regras e limites

- PostgreSQL é a fonte de verdade. Não usar GA4 nesta V1.
- Não armazenar e-mail, nome, URL sensível, IP ou user-agent na telemetria nova; a jornada já referencia a pessoa de forma interna.
- Tokens devem ser opacos, assinados, de escopo mínimo e inválidos fora da etapa correspondente.
- Abertura deve aparecer como **abertura rastreável**, não como leitura humana: proxies e Apple Mail Privacy Protection a tornam um sinal imperfeito.
- Clique no redirect é o sinal forte da V1.
- Não medir ainda conversão posterior (download, pedido ou doação); isso é evolução futura, depois de termos o funil básico.

## Validação

- Testes unitários da emissão/validação de token, idempotência e registro de primeira abertura/clique.
- Teste de integração dos endpoints de pixel e redirect, incluindo `302` para o destino correto.
- Teste funcional de uma jornada de teste: os cinco templates carregam pixel e CTAs rastreáveis; o painel consolida os eventos sem dados pessoais.
