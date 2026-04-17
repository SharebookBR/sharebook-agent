# 📚 Refatoração da Categoria "Artes" → "Poesia & Artes"

## 🎯 Objetivo

Evoluir a categoria **Artes** para uma estrutura mais clara, navegável e alinhada com o conteúdo atual, sem quebrar a arquitetura existente.

---

## 🧭 Escopo

- Renomear categoria "Artes" → "Poesia & Artes"
- Criar subcategorias (auto-relacionamento)
- Reorganizar os 30 livros existentes
- Manter compatibilidade com API atual (`CategoryTree`)
- Não alterar outras categorias do sistema

---

## 🏗️ Estrutura final

### Categoria pai

- **Poesia & Artes**

---

### Subcategorias

1. Poesia Lírica
2. Poesia Reflexiva / Existencial
3. Poesia Moderna & Experimental
4. Poesia Dramática
5. Teatro & Dramaturgia
6. Épicos & Narrativas
7. Estética & Teoria

---

## 📊 Distribuição dos livros

### ✍️ Poesia Lírica (4)
- As Primaveras — Casimiro de Abreu
- Sonetos e Outros Poemas — Bocage
- O Guardador de Rebanhos — Alberto Caeiro
- O Pastor Amoroso — Alberto Caeiro

---

### 🧠 Poesia Reflexiva / Existencial (4)
- Eu — Augusto dos Anjos
- Eu e Outras Poesias — Augusto dos Anjos
- Mensagem — Fernando Pessoa
- Livro de Mágoas — Florbela Espanca

---

### 🧩 Poesia Moderna & Experimental (6)
- Cancioneiro — Fernando Pessoa
- O Eu Profundo e Outros Eus — Fernando Pessoa
- Poemas de Álvaro de Campos — Fernando Pessoa
- Poemas de Ricardo Reis — Fernando Pessoa
- Poesias Inéditas — Fernando Pessoa
- Broquéis — Cruz e Sousa

---

### 🎭 Poesia Dramática (2)
- O Navio Negreiro — Castro Alves
- A Mensageira das Violetas — Florbela Espanca

---

### 🎭 Teatro & Dramaturgia (5)
- Otelo — William Shakespeare
- Rei Lear — William Shakespeare
- Auto da Barca do Inferno — Gil Vicente
- Fausto — Johann Wolfgang von Goethe
- Primeiro Fausto — Fernando Pessoa

---

### 🌌 Épicos & Narrativas (7)
- A Divina Comédia — Dante Alighieri
- Inferno — Dante Alighieri
- Purgatório — Dante Alighieri
- Paraíso — Dante Alighieri
- Paraíso Perdido — John Milton
- A Caixa de Pandora — Hesíodo
- Faetonte (Filho de Apolo) — Ovídio

---

### 🧠 Estética & Teoria (2)
- Arte Poética — Aristóteles
- Grandeza — Orlando Fedeli

---

## 🔧 Etapas de implementação

### 1. Renomear categoria

- Atualizar nome:
 - `Artes` → `Poesia & Artes`
- Manter:
 - `Id`
 - slug atual (`/artes`) — evitar quebra

---

### 2. Criar subcategorias

- Inserir 7 registros em `Category`
- Definir:
 - `ParentCategoryId = ArtesId`
 - `Order` para exibição

#### Ordem recomendada:

1. Poesia Lírica
2. Poesia Reflexiva / Existencial
3. Poesia Moderna & Experimental
4. Poesia Dramática
5. Teatro & Dramaturgia
6. Épicos & Narrativas
7. Estética & Teoria

---

### 3. Reassociar livros

- Atualizar relacionamento:
 - `Book.CategoryId → SubcategoryId`

- Garantir:
 - Cada livro pertence a **uma subcategoria**
 - Total permanece 30

---

### 4. Validação

Checklist:

- [ ] Total de livros = 30
- [ ] Nenhuma subcategoria inconsistente
- [ ] API `/CategoryTree` funcionando
- [ ] Frontend renderiza corretamente
- [ ] Navegação intacta

---

## ⚠️ Cuidados

- Não alterar IDs existentes
- Não remover categoria pai
- Evitar migração destrutiva
- Garantir rollback simples

---

## 🚀 Melhorias futuras (fora do escopo atual)

- Permitir múltiplas categorias por livro (tags)
- Criar curadoria dinâmica por intenção
- Agrupar coleções (ex: Dante completo)
- Monitorar comportamento de navegação

---

## 🧠 Insight de produto

Essa mudança transforma:

- ❌ Lista genérica
- ✔ Estrutura com identidade e descoberta

---

## ✅ Resultado esperado

- Categoria clara
- Navegação intuitiva
- Escalabilidade para +1000 livros
- Base sólida para curadoria contínua

---

## 📌 Status inicial

- **Categoria atual:** Artes (ID `8c347027-8bcb-49a8-a755-df55eeb1affd`)
- **Livros na categoria:** 30 (confirmar via query)
- **Próxima ação:** validar lista de livros e IDs no banco de produção.

---

## 🗂️ Referências

- Skill `sharebook-category-organizer`
- Script `sharebook_prod_pg_rw_exec.py` (para execução controlada)
- API `CategoryTree` (GET `/api/Category/tree`)

---

*Missão cadastrada em 2026-04-17.*