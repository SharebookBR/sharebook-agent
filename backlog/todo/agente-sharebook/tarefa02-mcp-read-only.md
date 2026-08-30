# Tarefa 2 — MCP read-only do Sharebook

## Status

**Pendente.** Depende da tarefa 1.

## Objetivo

Dar ao agente acesso seguro e explicável aos dados reais do Sharebook sem permitir mutações.

## Capacidades candidatas

- pesquisar catálogo;
- consultar livro, formato e disponibilidade;
- obter recomendações;
- consultar progresso e bookmarks;
- consultar lista de desejos;
- consultar doações e solicitações do próprio usuário.

## Princípios

- ferramentas chamam APIs ou serviços oficiais, nunca o banco;
- contratos pequenos, tipados e orientados a intenção;
- resultados respeitam as mesmas regras de visibilidade do produto;
- nenhuma ferramenta recebe escopo administrativo;
- chamadas possuem correlação, auditoria e orçamento de custo.

## Critério de pronto

O agente responde a uma jornada de descoberta usando somente capacidades oficiais, identifica a origem dos dados e não consegue consultar informação fora do escopo do usuário.
