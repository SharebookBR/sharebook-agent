# Tarefa 6 — Personalização por usuário

## Status

**Horizonte v2. Não iniciar sem recomendação simples estável e sinais confiáveis.**

## Objetivo

Combinar o contexto do livro atual com preferências reais do usuário, sem perder coerência editorial.

## Sinais candidatos

- livros baixados;
- livros favoritados;
- avaliações positivas;
- categorias preferidas;
- autores recorrentes;
- histórico de navegação, somente se houver base de privacidade e valor.

## Estratégia inicial

Criar um perfil vetorial simples, como média ponderada dos embeddings de livros com interação positiva.

Na PDP do livro X, combinar:

- proximidade com o livro atual;
- proximidade com o perfil do usuário;
- eventualmente, popularidade moderada.

## Riscos

- pouco sinal produzir personalização aleatória;
- reforçar bolha e reduzir descoberta;
- misturar interação casual com preferência durável;
- aumentar coleta de comportamento sem benefício proporcional;
- complexidade operacional maior que o ganho.

## Critérios de pronto

- usuários com histórico distinto recebem recomendações materialmente diferentes;
- contexto do livro atual continua reconhecível;
- usuário novo recebe fallback não personalizado de qualidade;
- privacidade e retenção dos sinais estão definidas;
- ganho é validado contra recomendação simples.
