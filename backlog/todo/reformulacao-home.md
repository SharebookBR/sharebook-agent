# Reformulação da Home do Sharebook

## Objetivo

Reformular a home com foco em descoberta de catálogo, especialmente no mobile.

A home deixa de ser lista de categorias e passa a funcionar como vitrine inteligente de leitura — respondendo à pergunta **"Qual livro eu vou ler agora?"**.

## Base entregue em 25/07/2026

- title, description e H1 reposicionados para livros gratuitos digitais e físicos;
- hero comunica dinamicamente o tamanho real do catálogo digital;
- assinatura "Doe. Ganhe. Leia." preservada como marca;
- prateleiras de novidades, livros físicos e categorias continuam SSR;
- rodapé ganhou coluna dinâmica de categorias antes de páginas institucionais;
- Home recebeu dados estruturados `Organization`, `WebSite` e `SearchAction`;
- sitemap e robots passaram a sustentar a descoberta de PDPs e categorias.

Essa entrega fecha a fundação de posicionamento e navegação. O backlog restante
abaixo é evolução de curadoria e personalização, não correção da Home atual.

---

## Inspiração

Modelo de descoberta da Netflix:
- facilitar a escolha;
- prateleiras temáticas;
- destacar novidades;
- valorizar curadoria;
- incentivar o usuário a voltar;
- reduzir esforço para encontrar algo relevante.

---

## Princípios

### 1. Mobile first
- scroll vertical entre seções;
- scroll horizontal dentro de cada seção;
- cards simples e visuais;
- poucos textos;
- decisão rápida.

### 2. Descoberta guiada
Seções com intenção clara, exemplos:
- Novidades digitais
- Tecnologia para devs
- Livros infantis em destaque
- Clássicos gratuitos
- Curtos para ler hoje
- Mais baixados
- Escolhidos pela curadoria
- Continue de onde parou

### 3. Curadoria como diferencial
O Sharebook não deve ser só repositório de PDFs. Curadoria aparece como valor de produto: livros melhores, capas melhores, boas sinopses.

Seções possíveis:
- Escolhidos pela curadoria Sharebook
- Livros que merecem sua atenção
- Capas premium
- Boas portas de entrada

### 4. Retenção
Feature futura importante:
- leitura online;
- persistência do progresso;
- seção "Continue de onde parou".

---

## Estrutura proposta da home mobile

### Header
- logo Sharebook;
- botão de busca;
- acesso à conta (se aplicável).

### Hero / Banner rotativo
- 3 a 5 livros em destaque;
- capa grande + título + CTA "Ler agora" ou "Ver livro".

### Seções de prateleira (lista vertical de rails horizontais)
Cada seção: título + scroll horizontal de cards.

Card mínimo:
- capa;
- título;
- autor.

### Seções sugeridas (ordenadas por impacto)
1. Novidades
2. Mais baixados
3. Escolhidos pela curadoria
4. Por categoria top (Tecnologia, Infantil, etc.)
5. Gratuitos e curtos
6. Continue de onde parou *(requer leitura online — feature futura)*

### Footer leve
- link para catálogo completo;
- link para busca.

---

## Notas de execução

- Antes de implementar qualquer componente Angular → ler `sharebook-agent/skills/engineering/frontend.md`.
- Dados das prateleiras virão de endpoints existentes ou novos no backend; alinhar antes de criar contratos.
- "Continue de onde parou" depende de feature de leitura online — não bloqueia o restante, mas não entregar a seção vazia.
