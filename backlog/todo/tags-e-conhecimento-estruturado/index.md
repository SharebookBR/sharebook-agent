# Épico — Tags e conhecimento estruturado

## Estado

- **Status:** discovery / backlog
- **Prioridade:** 3 no backlog principal
- **Valor:** médio-alto
- **Esforço:** alto
- **Próxima tarefa:** [Tarefa 1 — Ciclo manual de 5 livros técnicos](tarefa01-ciclo-manual-5-livros.md)
- **Critério de avanço:** ciclo manual produzir vocabulário v0, regras editoriais e decisão explícita sobre nível, uso editorial e automação.

## Tese de produto

Categoria organiza o corredor principal. Tag organiza descoberta transversal.

Para tecnologia, tags respondem intenções objetivas que a categoria não cobre bem: stack, área, problema, utilidade e talvez nível. Isso importa especialmente para devs e tech leads, porque "Tecnologia" é uma prateleira grande demais para quem procura `Python`, `Docker`, `Arquitetura` ou `Data Science`.

Em terror, bruxas e outros recortes editoriais amplos, categorias já resolvem melhor a intenção principal. Tags podem ajudar no futuro, mas a primeira fatia deve começar pelo catálogo técnico, onde o valor é mais claro.

## Princípios

- até três tags visíveis por livro;
- vocabulário controlado, sem criação livre por usuário ou IA;
- IA pode sugerir dentro do vocabulário permitido, mas não publicar automaticamente na fase inicial;
- começar por ebooks técnicos;
- categoria é prateleira principal; tag é eixo transversal;
- valor para o usuário decide prioridade; "alegação forte" aumenta custo de validação, mas não é argumento para descartar uma dimensão;
- tags podem alimentar vitrines temáticas e páginas públicas quando houver vocabulário estável;
- conhecimento estruturado só vira schema depois de julgamento editorial manual.

## Dimensões candidatas

1. **Stack/tecnologia:** `Python`, `.NET`, `Docker`, `Kubernetes`, `SQL`, `AWS`.
2. **Área/problema:** `Backend`, `DevOps`, `Data Science`, `Arquitetura`, `Segurança`.
3. **Uso editorial:** `Fundamentos`, `Referência`, `Prático`, `Acadêmico`, `Legado`.
4. **Nível:** `Iniciante`, `Intermediário`, `Avançado`.

Nível não deve ser descartado por ser uma alegação editorial. Deve ser testado no ciclo manual: se ajudar devs e tech leads a decidir clique/download, pode virar tag, campo separado ou metadado interno.

## Tarefas

| # | Tarefa | Status | Depende de | Resultado |
|---|---|---|---|---|
| 1 | [Ciclo manual de 5 livros técnicos](tarefa01-ciclo-manual-5-livros.md) | **Pendente** | — | Cinco ebooks avaliados com até três tags cada, alternativas rejeitadas e vocabulário v0. |
| 2 | [Vocabulário técnico v0 e governança](tarefa02-vocabulario-tecnico-v0.md) | **Pendente** | 1 | Lista controlada inicial, aliases, critérios de criação e regras de revisão. |
| 3 | [Modelo de dados para tags](tarefa03-modelo-de-dados-tags.md) | **Pendente** | 1–2 | Schema persistente com identidade estável e limite de tags visíveis. |
| 4 | [PDP e página pública por tag](tarefa04-pdp-e-pagina-publica-tag.md) | **Pendente** | 2–3 | Tags discretas na PDP e navegação pública por tag com SSR. |
| 5 | [Sugestão assistida no importer](tarefa05-sugestao-assistida-no-importer.md) | **Pendente** | 2–3 | IA sugere tags do vocabulário controlado para revisão editorial. |
| 6 | [Backfill controlado do catálogo técnico](tarefa06-backfill-controlado.md) | **Pendente** | 2–5 | Catálogo técnico preenchido de forma idempotente e revisável. |
| 7 | [Conhecimento estruturado: nível, pré-requisitos e tópicos](tarefa07-conhecimento-estruturado-nivel-pre-requisitos.md) | **Horizonte v2** | 1 + evidência de valor | Decisão sobre campos além de tags, guiada por valor ao usuário. |

## Fronteira da primeira fatia

A primeira fatia não tem código, migration, automação ou backfill.

Ela existe para responder uma pergunta: quando um humano bom olha para um livro técnico, quais três tags realmente ajudam um dev ou tech lead a decidir clicar, baixar ou continuar navegando?

## Relações

- pode alimentar vitrines temáticas na home quando tags forem estáveis;
- pode melhorar busca e recomendações com sinal estruturado simples;
- não depende de embeddings;
- deve seguir `skills/product-ux/catalog-strategy/SKILL.md` para critérios de qualidade e descoberta;
- ao final do ciclo manual, criar uma skill local de tagging editorial com as regras aprendidas, usando o fluxo oficial de skill quando isso for explicitamente solicitado.

## Fora de escopo agora

- automatizar publicação de tags;
- permitir tag livre;
- aplicar a todo o catálogo de uma vez;
- criar taxonomia universal para ficção, terror, filosofia e tecnologia ao mesmo tempo;
- implementar filtros avançados antes de provar navegação simples por tag;
- transformar nível, pré-requisitos e "você aprenderá" em schema antes do ciclo manual.
