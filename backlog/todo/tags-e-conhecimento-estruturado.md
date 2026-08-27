# Tags e conhecimento estruturado

## Problema

Categoria organiza o corredor principal, mas não representa bem tecnologias, temas específicos, nível, idioma ou pré-requisitos. O importer já lê material suficiente para extrair parte desse conhecimento, porém hoje ele não é persistido nem usado para descoberta.

## Objetivo

Enriquecer livros digitais com metadados controlados que melhorem navegação, filtros, busca e futuras recomendações sem poluir a PDP.

## Fase 1 — tags visíveis

- vocabulário controlado, sem criação livre por usuário;
- até três tags visíveis por livro;
- sugestão automática por IA dentro do vocabulário permitido;
- decisão explícita sobre revisão/edição editorial antes de automatizar publicação;
- tags clicáveis na PDP;
- página ou filtro que permita navegar pelos livros da tag.

Exemplos iniciais para o domínio técnico: `.NET`, `Java`, `Node`, `Python`, `AWS`, `Azure`, `GCP`, `SQL`, `Docker` e `Kubernetes`. A taxonomia definitiva precisa ser discutida; esta lista não é schema aprovado.

## Fase 2 — conhecimento estruturado

Avaliar persistência de:

- tópicos principais;
- nível;
- idioma;
- pré-requisitos;
- itens para a seção `Você aprenderá`.

Esses campos podem alimentar filtros, preparo editorial, páginas por assunto e recomendações mesmo antes de todos aparecerem na interface.

## Decisões necessárias antes da implementação

- modelo de dados e relação entre tag, tópico e categoria;
- vocabulário inicial e governança de novas tags;
- se a IA apenas sugere ou pode persistir automaticamente;
- experiência de navegação e indexação SEO das páginas de tag;
- estratégia de backfill para o catálogo atual;
- limite entre conhecimento extraído e alegação editorial não comprovada pelo livro.

## Critérios de aceite da primeira fatia

- schema e vocabulário discutidos antes do código;
- tags persistidas por identidade estável, não texto duplicado;
- no máximo três tags visíveis na PDP;
- navegação por tag funciona em desktop, mobile e SSR;
- IA não cria tags fora da lista controlada;
- backfill é idempotente e retomável;
- testes protegem regras e contratos relevantes;
- pipeline, build SSR e validação em produção passam.

## Relações

- executar depois da busca textual FTS + fuzzy;
- conhecimento estruturado pode preparar recomendações vetoriais, mas não depende delas;
- seguir `skills/product-ux/catalog-strategy/SKILL.md` para critérios de qualidade e descoberta.
