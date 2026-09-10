# Vitrine Bruxas & Magia — Sharebook

## Contexto

Criar uma nova vitrine temática **Bruxas & Magia** na home do Sharebook, aproveitando o interesse atual pelo tema.

A vitrine deve começar pequena e curada, com aproximadamente 15 obras, priorizando livros interessantes e populares em vez de simplesmente quantidade.

## Objetivo

Disponibilizar uma seleção de obras sobre:

- Bruxas e bruxaria
- Magia e ocultismo
- Salem e julgamentos de bruxas
- Folclore
- Ficção fantástica
- Horror relacionado ao tema

O conteúdo precisa estar disponível em português, já que esse é um requisito para o público-alvo da vitrine.

## Estratégia de Catálogo

### Origem principal

Usar preferencialmente o **Project Gutenberg** como fonte única dos livros.

Motivos:

- Grande catálogo de domínio público
- EPUB e texto estruturado disponíveis
- Metadados relativamente padronizados
- IDs estáveis
- Facilita enormemente a automação
- Categorias específicas de `Witchcraft` e `Witches -- Fiction`

Evitar múltiplas fontes nesta primeira versão.

## Curadoria Inicial

Selecionar aproximadamente 15 das melhores obras disponíveis, considerando:

1. Popularidade / downloads
2. Apelo para leitores comuns
3. Relação direta com bruxas e magia
4. Potencial de título e capa
5. Diversidade da vitrine
6. Qualidade da obra
7. Disponibilidade no Gutenberg
8. Elegibilidade jurídica no Brasil

Não selecionar simplesmente os 15 livros mais baixados.

A vitrine deve equilibrar:

- Ficção
- Horror
- Fantasia
- Salem
- História da bruxaria
- Magia e ocultismo

## Candidatos Iniciais

1. **The Witch of Salem** — John R. Musick
2. **The Lancashire Witches** — W. H. Ainsworth
3. **The Witch-Cult in Western Europe** — Margaret Murray
4. **Salem Witchcraft** — Charles W. Upham
5. **Letters on Demonology and Witchcraft** — Walter Scott
6. **The Superstitions of Witchcraft** — Howard Williams
7. **A History of Witchcraft in England** — Wallace Notestein
8. **Black Magic** — Marjorie Bowen
9. **Brood of the Witch-Queen** — Sax Rohmer
10. **Living Alone** — Stella Benson
11. **Dulcibel: A Tale of Old Salem** — Henry Peterson
12. **A Mirror for Witches** — Esther Forbes
13. **With Force and Arms** — Howard R. Garis
14. **The Discovery of Witches** — Matthew Hopkins
15. **Mary Schweidler, the Amber Witch** — Wilhelm Meinhold

Esta é uma lista de candidatos, não uma lista automaticamente aprovada para publicação.

## Regra Jurídica

O fato de uma obra estar em domínio público no Project Gutenberg não significa automaticamente que esteja em domínio público no Brasil.

Antes da tradução ou publicação, o pipeline deve validar a situação jurídica da obra no Brasil.

Regra:

- Obra original elegível no Brasil: pode seguir no pipeline.
- Obra não elegível ou situação jurídica incerta: rejeitar ou enviar para revisão manual.

Também é necessário separar os direitos da obra original dos direitos de uma tradução existente.

Não reutilizar traduções comerciais protegidas.

## Tradução

Português é requisito da vitrine.

Quando a obra original for elegível, mas não houver tradução reutilizável, produzir uma nova tradução PT-BR pelo pipeline agêntico do Sharebook.

Isso evita depender de traduções comerciais existentes.

A tradução deve buscar:

- Fidelidade ao original
- Português brasileiro natural
- Consistência de nomes e termos
- Preservação do estilo e período da obra sem tornar o texto artificialmente arcaico
- Ausência de trechos omitidos
- Ausência de conteúdo inventado pelo modelo

## Pipeline Agêntico

```text
Project Gutenberg
 ↓
Descoberta / Curadoria
 ↓
Validação jurídica BR
 ↓
Download do original
 ↓
Extração e normalização
 ↓
Tradução PT-BR
 ↓
Revisão agêntica
 ↓
QA / Judge
 ↓
Sinopse + metadados
 ↓
Geração do EPUB
 ↓
Capa
 ↓
Publicação no Sharebook
 ↓
Vitrine Bruxas & Magia
```

## QA da Tradução

A revisão deve verificar pelo menos:

- Fidelidade semântica
- Trechos ausentes
- Alucinações
- Nomes próprios
- Terminologia recorrente
- Diálogos
- Formatação
- Divisão de capítulos
- Consistência entre capítulos
- Fluidez do PT-BR

Para livros grandes, processar em partes mantendo um contexto editorial compartilhado, contendo personagens, nomes, lugares, decisões de tradução e glossário.

## Rastreabilidade

Guardar junto ao livro:

- `source`: Project Gutenberg
- `sourceId`: `<id>`
- `originalLanguage`: `en`
- `originalTitle`: `<title>`
- `translationLanguage`: `pt-BR`
- `translationType`: `Sharebook AI Translation`
- `translationPipelineVersion`: `<version>`
- `sourceRevision`: `<revision/hash>`

A versão do pipeline é importante para permitir que traduções antigas sejam reavaliadas ou regeneradas futuramente conforme os modelos e processos melhorarem.

## Princípio Arquitetural

O original deve permanecer como fonte imutável.

Os artefatos derivados — tradução, sinopse, metadados enriquecidos e EPUB — podem ser regenerados.

```text
ORIGINAL
 │
 ├── tradução v1
 ├── tradução v2
 ├── sinopse
 ├── metadados
 └── EPUB
```

## MVP

O objetivo inicial não é traduzir centenas de livros.

O MVP é:

> 15 livros muito bons, juridicamente seguros, bem traduzidos, bem apresentados e reunidos em uma excelente vitrine.

Isso permite validar:

- Interesse dos usuários
- Cliques na vitrine
- Downloads
- Qualidade percebida das traduções
- Custo do pipeline
- Tempo de processamento por livro
- Problemas recorrentes de QA

Somente depois dos resultados, considerar expansão do catálogo.

## Próximos Passos

1. Validar juridicamente os 15 candidatos no Brasil.
2. Confirmar o ID e os arquivos disponíveis no Project Gutenberg.
3. Ranqueá-los por popularidade e potencial para o Sharebook.
4. Substituir candidatos juridicamente problemáticos.
5. Fechar a lista definitiva de 15.
6. Implementar/ajustar o pipeline de tradução.
7. Processar 1 livro como golden case.
8. Revisar manualmente o resultado do golden case.
9. Ajustar prompts, agentes e critérios do Judge.
10. Processar os outros 14.
11. Criar capas e sinopses.
12. Publicar a vitrine.
13. Medir resultado.

## Critério de Sucesso Inicial

Antes de escala, responder três perguntas:

1. Conseguimos produzir uma tradução que dá prazer de ler?
2. Conseguimos fazer isso com custo e esforço operacional aceitáveis?
3. Os usuários realmente querem baixar esses livros?

Se as três respostas forem positivas, o mesmo pipeline pode posteriormente ser aplicado a outros nichos de obras em domínio público que ainda possuem pouca ou nenhuma oferta em português.
