# Missão — Evolução da busca e recomendações do Sharebook

## Objetivo
Evoluir a descoberta de livros no Sharebook sem cair em overengineering.

A missão tem dois pilares distintos:
1. **melhorar a busca principal** para consultas digitadas
2. **criar recomendações inteligentes na PDP** para descoberta contextual

A ordem importa.
Primeiro consertamos a busca textual e a regra de disponibilidade.
Depois adicionamos recomendação vetorial na PDP.
Só então faz sentido pensar em score híbrido e personalização.

---

## Resumo executivo

### Agora
- corrigir a inconsistência de disponibilidade entre backend e frontend
- substituir busca por substring por **PostgreSQL Full-Text Search**
- adicionar **trigram / fuzzy matching** para tolerância a erro de digitação

### Em seguida
- habilitar **pgvector**
- gerar embeddings dos livros
- criar endpoint de recomendação por similaridade semântica na PDP

### Depois
- reordenar recomendações com sinal de popularidade
- personalizar por usuário quando o resto já estiver sólido

---

## Contexto atual
Hoje a busca é fraca.

Na prática, ela opera como uma busca literal por substring, algo próximo de `Contains`, sem inteligência real de relevância.
Isso gera vários problemas:
- resultado ruim para termos compostos
- pouca tolerância a erro de digitação
- baixa capacidade de descoberta
- ranking fraco
- desperdício de sinopse e categoria
- inconsistência de regra entre backend e frontend

Além disso, o catálogo está crescendo. Continuar com busca literal vai degradar a experiência cada vez mais.

---

## Capacidade de infraestrutura disponível
A VPS atual do Sharebook tem:
- **4 vCPU**
- **16 GB RAM**

Leitura operacional:
- aguenta **Full-Text Search** com índices tranquilos
- aguenta **pg_trgm** sem drama
- aguenta **pgvector** para recomendação de catálogo em escala moderada
- aguenta **jobs batch/offline** de geração de embedding
- não justifica pipeline em tempo real exagerado nem arquitetura de foguete

Princípio:
**aproveitar bem a máquina sem inventar circo.**

---

# Fase 1 — Arrumar a casa

## Problema atual
Existe uma inconsistência de disponibilidade na busca:
- parte da regra está no backend
- parte da regra está no frontend
- o comportamento final fica torto e difícil de manter

Hoje isso gera acoplamento desnecessário e risco de bug.

## Objetivo
Centralizar a regra de visibilidade no backend.

## Regra canônica desejada
- **público**: só pode receber livros `Available`
- **admin**: pode buscar tudo, conforme regra administrativa

## Ações
- revisar `FullSearchAsync` e métodos relacionados
- garantir que o filtro de disponibilidade pública seja aplicado no backend
- remover o filtro redundante no frontend público
- validar se a paginação continua coerente depois da mudança

## Resultado esperado
- regra única
- menos comportamento surpreendente
- base limpa para evolução de relevância

## Critério de pronto
- frontend público não faz mais filtro manual de disponibilidade
- backend já entrega exatamente o que o público pode ver
- admin mantém a capacidade de consultar escopo ampliado

---

# Fase 2 — Melhorar a busca principal com Full-Text Search

## Objetivo
Trocar a busca textual por substring por uma busca ranqueada, nativa do PostgreSQL, simples e eficiente.

## Justificativa
Antes de falar de embeddings, precisamos resolver a dor principal da caixa de busca.
Quem digita uma consulta normalmente quer:
- título
- autor
- categoria
- termos relacionados no texto editorial

Isso é problema de **busca textual**. Não precisa semântica pesada logo de cara.

## Escopo inicial da busca
Campos candidatos:
- `Title`
- `Author`
- `Category.Name`
- `Synopsis` (com cuidado)

## Estratégia de relevância
Montar um documento textual com pesos diferentes.

Sugestão inicial:
- `Title` = peso **A**
- `Author` = peso **B**
- `Category.Name` = peso **C**
- `Synopsis` = peso **D**

### Observação crítica sobre a sinopse
A sinopse deve entrar com peso baixo.
Se entrar forte demais, polui o ranking com termos genéricos e linguagem editorial vaga.
Exemplos de ruído:
- “história envolvente”
- “personagens marcantes”
- “obra transformadora”
- “jornada”

A sinopse deve enriquecer, não mandar no ranking.

## Entregáveis técnicos
- coluna calculada ou materializada para `tsvector`
- ponderação por campo usando `setweight`
- índice GIN apropriado
- query com `ts_rank` ou `ts_rank_cd`
- ordenação por relevância
- compatibilidade com a paginação atual

## Decisão sugerida de implementação
Começar com algo simples e explícito.
Evitar magia escondida.

Possível documento de busca:
- título
- autor
- categoria
- sinopse resumida ou limpa

## Resultado esperado
A busca deixa de ser “contém esse texto” e passa a ser “quão relevante este livro é para esta consulta”.

## Critério de pronto
- melhora perceptível para termos compostos
- ranking mais razoável nos primeiros resultados
- sem regressão séria de performance
- paginação preservada

---

# Fase 2.5 — Tolerância a erro com trigram e fallback fuzzy

## Objetivo
Resolver uma dor real que o FTS sozinho não cobre bem: typo e pequenas variações de escrita.

## Justificativa
Usuário real digita errado.
Exemplos:
- “machdo de assis”
- “javascipt”
- “doker”
- “policarpo quaresm”

Se a busca morrer nesses casos, a experiência continua fraca.

## Estratégia
Adicionar extensão e índice para busca fuzzy:
- `pg_trgm`
- similaridade por trigram
- fallback quando o FTS não trouxer resultado bom o bastante

## Possível comportamento
1. tenta FTS normal
2. se não houver resultado suficiente, aplica fuzzy match
3. mistura os resultados com score controlado

## Uso recomendado
Aplicar fuzzy principalmente em:
- `Title`
- `Author`

Categoria e sinopse devem ter uso muito mais conservador no fuzzy para evitar ruído.

## Resultado esperado
- tolerância a erros de digitação
- melhor recall
- sensação de busca mais inteligente sem custo alto

## Critério de pronto
- consultas com erro pequeno ainda retornam livros relevantes
- custo de query permanece aceitável com índice correto

---

# Fase 3 — Recomendações na PDP com embeddings + pgvector

## Objetivo
Na página de um livro, mostrar livros semanticamente parecidos.

Não é para substituir a busca principal.
É para melhorar a **descoberta contextual**.

## Justificativa
A PDP tem um comportamento diferente da caixa de busca.
Na busca, o usuário está expressando intenção por texto.
Na PDP, o usuário já sinalizou interesse num livro específico.

A pergunta muda de:
- “o que corresponde a esse termo?”

para:
- “o que se parece com este livro?”

Aí sim embeddings fazem sentido cedo.

## Pré-condições
Não começar esta fase sem:
- busca textual melhorada
- regra de disponibilidade resolvida
- catálogo minimamente limpo
- sinopses com qualidade razoável

Se o metadado estiver ruim, a recomendação vetorial nasce ruim.

## Fonte do embedding
Construir embedding a partir de algo como:
- título
- autor
- sinopse
- categoria

Sugestão prática:
criar um texto canônico por livro, algo como:
- título
- autor
- categoria folha
- sinopse limpa

## Armazenamento
- habilitar extensão `pgvector`
- adicionar coluna de embedding na tabela ou tabela auxiliar
- indexar conforme volume justificar

## Estratégia operacional
Gerar embedding **offline**, não na leitura da PDP.

Eventos válidos para regenerar embedding:
- criação do livro
- alteração de título
- alteração de autor
- alteração de categoria
- alteração de sinopse

Nunca recalcular embedding por acesso do usuário.

## Fluxo da recomendação
1. usuário abre livro X
2. backend pega embedding do livro X
3. busca vetores mais próximos entre livros `Available`
4. remove o próprio livro X
5. retorna top N

## Saída inicial
- 3 ou 6 recomendações
- simples
- sem personalização
- sem overfit em categoria exata

## Risco importante
Embeddings parecem mágicos em demo, mas podem produzir semelhança ruim se:
- sinopses forem fracas
- categorias estiverem tortas
- catálogo tiver muito ruído repetitivo

Mitigação:
- testar com amostras reais
- revisar qualitativamente recomendações antes de considerar “pronto”

## Critério de pronto
- PDP exibe livros parecidos com boa coerência editorial na maioria dos casos
- latência aceitável
- custo sob controle

---

# Fase 4 — Re-ranking com popularidade

## Objetivo
Evitar que a recomendação vetorial entregue apenas livros parecidos, mas irrelevantes para produto.

## Justificativa
Similaridade pura pode favorecer itens obscuros, pouco clicados ou pouco atraentes.
Um toque de popularidade melhora confiança e apelo.

## Sinais candidatos
- visualizações da PDP
- downloads
- solicitações
- avaliações
- nota média
- recência, se fizer sentido

## Estratégia
Não misturar tudo cedo.
Começar simples:
1. buscar top 20 por similaridade
2. reordenar com score de popularidade
3. devolver top final

## Exemplo conceitual
`score_final = score_similaridade + peso_popularidade`

Sem obsessão matemática no início.
Produto primeiro.

## Critério de pronto
- recomendação continua coerente
- livros com tração real ganham algum destaque
- sem destruir relevância semântica

---

# Fase 5 — Personalização por usuário

## Objetivo
Evoluir da recomendação contextual da PDP para recomendação adaptada ao gosto do usuário.

## Sinais candidatos do usuário
- livros baixados
- livros favoritados
- livros avaliados positivamente
- categorias preferidas
- autores recorrentes
- histórico de navegação, se existir e fizer sentido

## Estratégia inicial
Montar um perfil vetorial simples do usuário, por exemplo:
- média ponderada dos embeddings dos livros com interação positiva

## Uso na prática
Na PDP do livro X, combinar:
- proximidade com o livro atual
- proximidade com o gosto do usuário
- popularidade

## Princípio
Esta fase só entra quando:
- a recomendação da PDP já estiver boa
- os sinais do usuário tiverem qualidade suficiente
- a operação estiver estável

## Critério de pronto
- usuários diferentes passam a receber recomendações diferentes para o mesmo livro
- sem perder coerência contextual com a PDP atual

---

# Decisões de arquitetura

## Busca principal ≠ recomendação PDP
Essas duas coisas são irmãs, não gêmeas.

### Busca principal
Tecnologia principal:
- PostgreSQL Full-Text Search
- suporte de `pg_trgm`

Uso:
- caixa de busca
- listagens
- descoberta direta por intenção textual

### Recomendação na PDP
Tecnologia principal:
- embeddings
- `pgvector`

Uso:
- livros parecidos
- descoberta contextual
- expansão de navegação no catálogo

Misturar responsabilidades cedo demais é erro.

---

# O que não fazer agora

- não transformar a busca principal inteira em busca semântica
- não recalcular embeddings em tempo real
- não personalizar antes de validar recomendação simples
- não subir pipeline sofisticado sem medir valor
- não deixar a sinopse dominar ranking textual
- não usar fuzzy em tudo sem controle, senão vira ruído

---

# Riscos

## Risco 1 — Overengineering
Querer resolver busca, recomendação, popularidade e personalização tudo de uma vez.

### Mitigação
Executar por fases e medir valor por etapa.

## Risco 2 — Relevância ruim no FTS
Peso mal calibrado pode trazer resultados estranhos.

### Mitigação
Testar com consultas reais e ajustar pesos.

## Risco 3 — Recomendação vetorial ruim
Metadados editoriais fracos geram embeddings fracos.

### Mitigação
Validar catálogo e sinopses antes de confiar cegamente na semântica.

## Risco 4 — Custo operacional bobo
Gerar embedding demais, reindexar à toa, query sem índice.

### Mitigação
Processamento offline, índices certos e atualização por evento relevante.

## Risco 5 — Licença e conteúdo de terceiros
Mesmo quando um livro é publicamente acessível, enriquecer, transformar ou redistribuir pode ter implicações diferentes dependendo da licença.

### Mitigação
Evitar investir pipeline pesado em acervo juridicamente duvidoso. Priorizar obras com base editorial e jurídica limpa.

---

# Métricas de sucesso

## Busca principal
- melhor qualidade percebida
- mais aderência dos primeiros resultados
- menos buscas frustradas
- menor taxa de “busca sem resultado”

## Recomendação na PDP
- mais cliques em livros recomendados
- mais navegação entre PDPs
- aumento de downloads / leituras iniciadas

## Evolução futura
- maior profundidade de navegação
- melhor descoberta de catálogo
- maior retenção

---

# Ordem recomendada de implementação

## Sprint 1
### Corrigir regra de disponibilidade
- centralizar regra no backend
- remover filtro redundante no frontend
- validar paginação e comportamento público/admin

## Sprint 2
### Implementar Full-Text Search
- estruturar documento textual
- definir pesos
- indexar
- ordenar por relevância
- validar qualidade dos resultados

## Sprint 3
### Adicionar trigram / fuzzy
- habilitar `pg_trgm`
- criar índices
- implementar fallback ou score híbrido controlado
- validar tolerância a typo

## Sprint 4
### Implementar recomendação vetorial simples na PDP
- habilitar `pgvector`
- adicionar campo/tabela de embedding
- gerar embeddings dos livros existentes
- criar endpoint de recomendação por livro
- renderizar recomendações na PDP

## Sprint 5
### Melhorar recomendação com popularidade
- definir sinal de popularidade inicial
- combinar com similaridade
- revisar ordenação final

## Sprint 6
### Personalização
- definir sinais do usuário
- montar perfil vetorial simples
- combinar com contexto da PDP

---

# Checklist de decisão por fase

## Antes da Fase 2
- a regra de disponibilidade está 100% canônica no backend?

## Antes da Fase 3
- o FTS está bom o bastante?
- o fuzzy já resolveu typo relevante?
- as sinopses têm qualidade mínima?
- o catálogo está limpo o bastante para embeddings?

## Antes da Fase 5
- a recomendação simples já gera valor?
- temos sinais reais de usuário?
- faz sentido operacional agora?

---

# Definição de pronto desta missão
A missão será considerada bem-sucedida quando existir:
1. busca pública consistente e centralizada no backend
2. busca textual relevante com FTS
3. tolerância mínima a erro com trigram
4. recomendação semântica funcional na PDP
5. base pronta para score híbrido e personalização futura

---

# Resumo final
A estratégia correta não é jogar IA em tudo.

A estratégia correta é:
1. **consertar a regra**
2. **fazer busca textual de verdade**
3. **adicionar tolerância a erro**
4. **usar vetorial onde ele realmente brilha: recomendações na PDP**
5. **evoluir com popularidade e personalização depois**

Sem cocada.
Sem NASA.
Com ganho real de produto.
